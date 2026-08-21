# AGENTS.md — TapMenu

> Instructions for AI agents (and humans acting as agents) working in this repository. Read this file before writing any code. Canonical docs: `CONTEXT.md`, `DESIGN.md`, `docs/PRD.md`, `docs/TASKS.md`.

---

## 1. What TapMenu Is

TapMenu is a Django monolith for Indonesian F&B (resto, cafe, UMKM kuliner). Two entry points:

- **Customer (no login)** — scans a `DiningTable.qr_token` → `GET /m/<qr_token>/` → browses Menu Category / MenuItem → Cart (session, bound to `qr_token`) → Order + OrderItem (price snapshot) → Payment via Payment gateway → Order Status + Receipt (struk).
- **Staff/Owner (login required)** — dashboard at `/dashboard/` → manages Menu Category / MenuItem, DiningTable & QR, orders, payments, Appearance theme, reports.

Root `/` is the **landing page** (`core/views.py:landing`, `core/templates/core/landing.html`), not the dashboard. Never redirect `/` to `/dashboard/`.

---

## 2. Read Order (Do This First)

Before any task, read in this order:

1. `CONTEXT.md` — ubiquitous language (do not rename these terms)
2. `DESIGN.md` — tokens, layout shells, component catalog, prototype → implementation delta
3. `docs/PRD.md` — MVP scope, entities, status machines
4. `docs/TASKS.md` — phased implementation plan; use it as the task checklist
5. `pyproject.toml` — lint rules (ruff + djlint)

If you skip (1) or (2), you will drift naming and styling.

---

## 3. Ubiquitous Language (Enforced)

Use these terms exactly. Search-and-replace violations before committing. Canonical definitions in `CONTEXT.md:1-80`.

| Use | Avoid | Notes |
|---|---|---|
| **Customer** | user, guest, client | Diner at a table, no login |
| **DiningTable** | Table | Model `restaurants.DiningTable`; `qr_token` unique; `(restaurant, number)` unique |
| **Menu Category** | Section, group | Ordered by `sort_order` |
| **MenuItem** | Product, dish | Price = integer Rupiah; visible only when `is_active` and `is_available` |
| **Cart** | Basket | Session-scoped, bound to `qr_token`; line = `menu_item_id + quantity + note + variant_option_ids` |
| **Order** | Transaction, ticket | `code` e.g. `ORD-20260808-AB12CD34` unique per restaurant |
| **Order Item** | Line item | Snapshot `item_name`, `item_price`, `quantity`, `subtotal`; never re-derive from MenuItem |
| **Order Status** | — | `new → paid → processing → ready → completed`; cancellable from `new`/`processing` → `cancelled` |
| **Payment Status** | — | On Order: `unpaid/paid/refunded`; on Payment: `pending/paid/failed/expired/refunded` (see §3.1) |
| **Order code** | — | Human-readable ID per order |
| **Payment** | Charge | One order → many payments, first `paid` marks order paid |
| **Payment method** | Payment type | `cash`, `qris`, `bank_transfer`, `ewallet` |
| **Payment gateway** | Payment provider | Adapter `create_payment` / `verify_callback`; `dummy` default, `midtrans` when keys exist |
| **Receipt (struk)** | Invoice, bill | 80mm thermal printable |
| **Staff role** | User type | `owner`, `admin`, `kasir`, `dapur` |
| **UserProfile** | Account | `OneToOne(User)` with `role` + `restaurant` |
| **Appearance theme** | Theme, skin | Colors, font, layout/header/button style, banner, tagline, receipt footer |

### 3.1 Status Vocabulary Conflict

`docs/PRD.md:9-10` defines Payment Status as `pending/paid/failed/expired/refunded`; `CONTEXT.md:42` narrows the Order-level payment status to `unpaid/paid/refunded`. Treat PRD as gateway-level and CONTEXT as order-level; do not mix. When changing order state, update both `Order.status` and `Order.payment_status`/`Payment.status` consistently.

---

## 4. Project Map

```
tapmenu/
├── core/               # settings, urls, global templates/static, landing
│   ├── templates/layouts/base.html:1-19          # public shell
│   ├── templates/layouts/dashboard.html:1-34     # dashboard shell (sidebar + header + main)
│   ├── templates/core/partials/dashboard_sidebar.html
│   ├── static/core/css/main.css / js/main.js
│   └── static/core/{css,js}/pages/*              # per-page built assets
├── accounts/           # User, UserProfile (role), auth, register
├── restaurants/        # Restaurant, DiningTable (qr_token), Appearance theme
├── menus/              # Category (sort_order), MenuItem (price int), variants
├── orders/             # Order, OrderItem (snapshot), Cart (orders/cart.py), services (orders/services.py)
├── payments/           # Payment, gateways/base.py + dummy.py + midtrans.py, services
├── dashboard/          # Owner/Admin/Kasir/Dapur dashboards, reports
├── design/             # STATIC PROTOTYPES — never edit, copy-convert to templates
├── docs/               # PRD.md, TASKS.md
├── DESIGN.md           # design system (tokens, shells, components)
└── manage.py
```

URL roots: `/` landing, `/m/<qr_token>/` customer menu, `/dashboard/` staff, `/accounts/` auth + `allauth` Google, `/onboarding/` 3-step setup.

Installed apps in `core/settings.py:INSTALLED_APPS` — `accounts`, `restaurants`, `menus`, `orders`, `payments`, `dashboard` + `allauth`.

---

## 5. Architecture Rules

1. **Django monolith, modular apps** — keep domain logic in its app; no cross-app model import cycles. Shared template base is `core/templates`.
2. **Models first, then services, then views/templates** — per `docs/TASKS.md` principle. Every important flow has a service layer (`orders/services.py:create_order_from_cart`, `payments/services.py:initiate_payment`, `payments/gateways/base.py`).
3. **Price is integer Rupiah** (`PositiveIntegerField`) — never float/decimal. Format with `menu_extras|rupiah`.
4. **OrderItem is a snapshot** — copy `item_name`/`item_price` at order creation; history must not change when MenuItem price changes.
5. **Cart is session + qr_token-bound** — `orders/cart.py`; never persist cart to DB; validate `is_active && is_available` and same-restaurant on add.
6. **Order number uniqueness** — per-restaurant, human-readable `ORD-...`. Generate in service, not view.
7. **DiningTable token** — `qr_token` unique global; `(restaurant, number)` unique together. Use `DiningTable`, never `Table`.
8. **Payment gateway abstraction** — `payments/gateways/base.py:PaymentGateway` with `create_payment(payment)` / `verify_callback(payload)`. `dummy` for dev, `midtrans` when keys exist. Never call provider SDK from views.
9. **`/` is landing** — `core/urls.py` root must stay `views.landing`. Auth CTAs must use `{% url 'login' %}` / `{% url 'register' %}` — `href="#"` only for in-page anchors.

---

## 6. Templates & Static Conventions

- **Layouts**: `layouts/base.html` for public; `layouts/dashboard.html` for staff. New dashboard page = `{% extends 'layouts/dashboard.html' %}` + `block dashboard_main` containing:
  ```html
  <header class="bg-white/80 backdrop-blur-md sticky top-0 ...">...</header>
  <div class="flex-1 overflow-y-auto p-6 custom-scroll">
    <div class="max-w-7xl mx-auto space-y-8 fade-in">...</div>
  </div>
  ```
  See `core/templates/core/pages/dashboard.html:36-289` as canonical.

- **Design → Template conversion**: Never edit `design/*.html` or `design/*.jsx`. Copy-convert to `core/templates/...`. Move inline CDN `tailwind.config` into `core/static/core/css/main.css` where possible; dashboard still uses CDN shim via `dashboard-*.js` — do not add a second config.

- **Tokens**: Colors `primary #1B4332 / primaryLight #2D6A4F / secondary #D8F3DC / accent #E07A5F / bg #F7F5F2 / dark #2D3436` (`DESIGN.md:2.1`), font `Plus Jakarta Sans`, radii `1.5–3rem`, shadows `card/soft/floating`. Customer theming via CSS vars in `menus/customer_menu.html:17-59` (`--menu-primary` etc., modifiers `data-header-style`, `data-button-style`, `data-layout-style`).

- **Icons**: Font Awesome 6.4.0 — `fa-utensils` (brand), `fa-qrcode`, `fa-receipt`, `fa-chart-pie`, etc.

- **Modals / Sheets**: Dashboard modal = `fixed inset-0 bg-black/50 backdrop-blur-sm + max-w-* rounded-2xl shadow-2xl`; customer sheet = bottom `fixed inset-0 + bg-black/45 backdrop + translate-y-full` with `[data-sheet-drag-zone]` and `Escape` close (`menus/customer_menu.html:324-355`). Always include `{% csrf_token %}` and `type="button"` where needed; deletes need `onsubmit="return confirm(...)"`.

- **Navigation**: Sidebar active = `bg-secondary/50 text-primary font-bold rounded-xl`; use `{% url ... %}` for every link.

---

## 7. Python & Template Style

Config lives in `pyproject.toml:1-32`.

```bash
# format & lint — run before every commit
.venv/bin/python -m ruff check .
.venv/bin/python -m ruff format .
.venv/bin/python -m djlint . --reformat --profile django
```

- `ruff`: target `py313`, line 88, select `E,F,I,B,DJ,UP`, ignore `DJ001`, quote `single`, exclude `.venv,**/migrations/**`.
- `djlint`: profile `django`, indent 4, max 120, ignore `H006,H021,H030,H031,T002,T003`.
- Never commit `.venv/`, `db.sqlite3`, or media uploads. Respect `exclude` lists.

---

## 8. Verification (Run Before Claiming Done)

Use the venv Python — `python` may not be the venv.

```bash
# 1. Django sanity
.venv/bin/python manage.py check
.venv/bin/python manage.py findstatic core/css/main.css core/js/main.js --verbosity 1

# 2. Migrations up to date
.venv/bin/python manage.py makemigrations --dry-run --check

# 3. Tests (add tests alongside every model/service/view change)
.venv/bin/python manage.py test

# 4. Lint
.venv/bin/python -m ruff check . && .venv/bin/python -m djlint --check .

# 5. Manual smoke (when flows change)
.venv/bin/python manage.py runserver 127.0.0.1:8000
# customer: /m/<qr_token>/ → add to cart → checkout → pay (dummy success) → /orders/<code>/status
# staff: login → /dashboard/ → CRUD category/menu → /dashboard/orders/ → advance status new→paid→processing→ready→completed
```

Seed demo data (if `restaurants/management/commands/seed_demo.py` exists): `.venv/bin/python manage.py seed_demo`.

---

## 9. Workflow for Agents

1. **Plan** — read §2 docs; if multi-step, write `TodoWrite` list (one `in_progress` at a time).
2. **Explore** — use `glob`/`grep` before guessing file paths; check `core/urls.py`, `core/settings.py`, sibling templates.
3. **Implement** — smallest diff; keep `design/` untouched; add service + test before view.
4. **Verify** — run §8 checks; fix lint/test before pushing.
5. **Document** — update `DESIGN.md` only when tokens/components change; do not create new `*.md` unless requested.
6. **Safety** — never force-push, never amend failed commits — fix forward; never commit secrets; use `workdir` param instead of `cd &&`.

Parallel sub-agents: dispatch via `task` tool only for independent work (no shared state); otherwise sequential.

---

## 10. Common Pitfalls

- Renaming ubiquitous terms (e.g. `Table`, `Product`, `Basket`) — caught by grep before commit.
- Using `href="#"` for login/register/dashboard — must be `{% url %}`.
- Storing cart in DB or ignoring `qr_token` binding.
- Recomputing order totals from live MenuItem price instead of OrderItem snapshot.
- Editing `design/` directly — always convert to template.
- Adding duplicate Tailwind config — consolidate into static, remove inline CDN where migrated.
- Missing `is_active && is_available` check on customer menu queries.
- Forgetting `csrf_token` in sheet/modal forms or `aria-*` on tabs/sheets.

---

## 11. Where to Look Up More

- Ubiquitous language → `CONTEXT.md`
- Colors, shells, components, page inventory → `DESIGN.md`
- MVP scope, entities, status machines, non-goals → `docs/PRD.md`
- Phased task list (Phase 0–10) → `docs/TASKS.md`
- Setup & roles → `README.md`
- Prototype source of truth → `design/` (landing-page.html, index.html, book-menu.html/.jsx, menu.html, management-menu.html, laporan.html, store.html, employee.html, login.html, register.html)
- Implemented templates → `core/templates/{layouts,core/pages,menus,dashboard}`
