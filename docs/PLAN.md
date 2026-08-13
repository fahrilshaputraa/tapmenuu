# TapMenu Finish — Implementation Plan

> Aligned via grill-with-docs. Domain language: `CONTEXT.md`. Decisions: `docs/adr/0001-*`, `0002-*`.

## Goal

Close the gaps between the current MVP and the PRD so the loop **scan QR → order → pay → live track → receipt** is complete, with role-based staff access and a real (config-gated) Midtrans gateway. All 8 agreed items, executed in priority batches, each verified before the next.

## Scope (agreed with user)

1. **Customer order-status tracking** — SSE live updates from the order-success page
2. **Role-based access** — `UserProfile` (role + restaurant); Owner/Admin full, Kasir order+payments, Dapur kitchen board
3. **Order status state machine** — align to PRD vocab `new/paid/processing/ready/completed/cancelled`, enforce transitions in service layer
4. **Revenue = paid orders only** — dashboard home consistent with reports
5. **Real payment gateway** — `midtrans.py` behind existing interface, activated by env keys, dummy remains default
6. **Dashboard all from DB** — already true; fix revenue inconsistency (item 4), no hardcoded metrics
7. **Customizable customer page** — extend `MenuAppearanceTheme`: banner, tagline/greeting, receipt footer, contact
8. **Print receipt (struk)** — HTML 80mm thermal print page, customer + admin

## Domain rules that MUST hold (from CONTEXT.md)

- **Order Status**: `new → paid → processing → ready → completed`; cancel from `new`, `processing` only
- **Payment Status**: `unpaid`, `paid`, `refunded` (on Order, mirrored on Payment)
- **OrderItem** is a price snapshot — never re-derived
- **MenuItem** visible only when `is_active` AND `is_available`
- **DiningTable** `qr_token` unique; table number unique per restaurant
- **Payment gateway**: `dummy` default; `midtrans` active when `MIDTRANS_SERVER_KEY` + `MIDTRANS_CLIENT_KEY` set

## Implementation batches

### Batch 1 — Core customer + staff loop (dependency-free, highest value)

**B1.1 Status vocabulary + state machine**
- `orders/models.py`: `Order.Status` → `new/paid/processing/ready/completed/cancelled`; `Order.PaymentStatus` stays `unpaid/paid/refunded`
- Migration: map old rows `pending→new`, `confirmed→paid` (or `processing`), `preparing→processing`
- `orders/services.py`: add `ORDER_STATUS_TRANSITIONS` map + `transition_order_status(order, new_status)` raising `OrderStatusTransitionError`
- `dashboard/forms.py`: `OrderStatusForm` validates via the service; `dashboard/views.py` `order_update_status` uses service
- Update templates + JS (`orders.html`, `orders-1.js`) status labels to new vocab
- Tests: model choices, migration mapping, transition allowed/denied matrix

**B1.2 Role-based access**
- `accounts/models.py`: `UserProfile` (OneToOne User, `role` choices owner/admin/kasir/dapur, `restaurant` FK)
- Migration; `accounts/admin.py` inline
- `dashboard/views.py`: `role_required(*roles)` decorator; keep `staff_required` for Owner/Admin
- Views gated: store/appearance/tables/menus/categories/employee → owner+admin; orders/order_detail/status → owner+admin+kasir; kitchen → all staff (dapur sees only kitchen)
- `seed_tapmenu.py`: assign roles to seeded users
- Tests: role matrix — kasir can't edit menu, dapur can't see payments, owner sees all

**B1.3 Customer order-status + SSE**
- `orders/views.py` (or `menus/views.py`): `customer_order_status(qr_token, order_id)` page (replaces/extends success page) with status timeline + receipt link
- SSE endpoint: `orders/<id>/stream/` — `StreamingHttpResponse(text/event-stream)`, DB-version polling loop (every ~2s), sends `status`/`payment_status` events on change; graceful `event: heartbeat`
- JS: `EventSource` client with reconnection; falls back to manual refresh
- Template: timeline (new → paid → processing → ready → completed), payment method + amount, print receipt button
- Tests: SSE returns `text/event-stream`; content-type; timeout closes cleanly

**B1.4 Receipt (struk) print**
- `orders/views.py`: `customer_receipt` (80mm thermal HTML) + `admin_receipt` (admin order detail)
- Template `receipt.html`: monochrome, dashed dividers, order code, table, items (qty × price), subtotal, discount, tax, total, payment method, paid amount, date, footer text from theme; `@media print`
- Buttons on order-status page + admin order detail → `window.print()`
- Tests: receipt renders order snapshot data; print stylesheet present

**B1.5 Dashboard kitchen board (Dapur)**
- `dashboard/views.py`: `kitchen(request)` — big cards of orders in `new/processing`, status advance buttons (processing→ready→completed), SSE new-order ticker
- `dashboard/urls.py`: `kitchen/`; sidebar link visible for dapur role
- Test: dapur sees kitchen; kasir sees orders page

### Batch 2 — Payments, metrics, theming

**B2.1 Midtrans gateway (config-gated)**
- `payments/gateways/midtrans.py`: `MidtransPaymentGateway` — `create_payment` → Snap transaction (QRIS/VA/EWALLET mapping), `verify_callback` → signature validation (SHA-512), status mapping (capture/paid → paid, expire/deny → expired/failed)
- `payments/services.py`: `get_payment_gateway()` — returns Midtrans when env keys present else Dummy
- `payments/views.py` `webhook`: route to `verify_callback` for `midtrans` provider; keep dummy behavior
- Settings: read `MIDTRANS_SERVER_KEY`, `MIDTRANS_CLIENT_KEY`, `MIDTRANS_IS_PRODUCTION` from env
- Tests: gateway selection logic (keys/no-keys), create_payment with mocked HTTP (requests-mock or unittest.mock), webhook signature valid/invalid
- Note: no sandbox keys today → unit-tested with mocks, active only when keys exist

**B2.2 Revenue consistency**
- `dashboard/views.py`: `dashboard_home` revenue = paid orders only (`Sum` filtered `payment_status=paid`); add `pending_payments` total card, clearly labeled
- `dashboard.html` template: show paid revenue + pending separately
- Tests: unpaid order not counted in revenue; pending card counts unpaid+refunded

**B2.3 Appearance theme extension (customizable customer page)**
- `restaurants/models.py`: `MenuAppearanceTheme` add `banner_image`, `tagline`, `greeting_message`, `receipt_footer_text`, `contact_phone`, `contact_instagram`
- Migration; `dashboard/forms.py` `MenuAppearanceThemeForm` new fields; `menu-appearance.html` UI
- `menus/views.py` customer_menu + customer_cart + customer_order_success + receipt templates render theme fields (banner, greeting, footer)
- Tests: theme fields render on customer pages; default values present

### Batch 3 — Verification & polish
- Full test suite green
- `ruff check .` + `ruff format .` clean; `djlint` clean
- Smoke: seed → QR menu → add to cart → checkout → dummy payment → SSE status → receipt print
- Smoke: login as owner/admin/kasir/dapur → role-gated visibility correct
- Smoke: revenue shows paid-only; pending card separate

## Verification commands (after each batch)
```bash
.venv/bin/python manage.py check
.venv/bin/python manage.py test
ruff check .
```
Smoke via `seed_tapmenu` + `runserver` (documented in TASKS 10.2/10.3).

## Notes / risks
- Status migration touches DB rows — keep mapping explicit and tested
- SSE: dev server `runserver` is single-threaded — stream blocks one worker; acceptable for dev (note in README); production would use gunicorn workers
- Midtrans live QRIS requires merchant MID from bank — sandbox/keys later; integration is code-complete and mock-tested now
