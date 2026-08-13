# TapMenu Context

TapMenu is a digital ordering and payment platform for Indonesian F&B businesses (restaurants, cafes, UMKM kuliner). Customers order directly from their table by scanning a QR code and pay digitally without queueing at the cashier; staff and owners manage operations from a dashboard.

## Language

### Ordering

**Customer**:
A diner at a restaurant table who scans the QR code to browse the menu and place an order. They do not log in.
_Avoid_: User, guest, client

**DiningTable**:
A physical table in the restaurant, identified by a unique `qr_token` that opens the customer menu for that table. One restaurant cannot have duplicate table numbers.
_Avoid_: Table (ambiguous with database table)

**Menu Category**:
A grouping of menu items for a restaurant (e.g., "Makanan", "Minuman"), ordered by `sort_order`.
_Avoid_: Section, group

**MenuItem**:
A single sellable food or beverage with a price stored as integer Rupiah. May have variants (e.g., "Level Pedas"), a discount percent, and tax percent. A menu item is only visible to customers when both `is_active` and `is_available` are true.
_Avoid_: Product, dish, food

**Cart**:
A session-scoped collection of line items a customer is building before checkout. Each cart line records the menu item id, quantity, note, and selected variant option ids. The cart is bound to a specific dining table's QR token.
_Avoid_: Basket, shopping cart

**Order**:
A customer's placed order from a dining table. Contains order items (price snapshots), a unique order code per restaurant, customer name/note, order status, payment status, and total amount.
_Avoid_: Transaction, ticket, booking

**Order Item**:
A snapshot line within an order: the menu item name and unit price at the time of ordering, quantity, notes, and line total. Never re-derived from the current menu price after the order is placed.
_Avoid_: Line item (keep OrderItem)

**Order Status**:
The lifecycle state of an order, enforced as a state machine. Sequence: `new` → `paid` → `processing` → `ready` → `completed`; cancellable from `new` and `processing` (`cancelled`).
_Avoid_: The previous vocabulary `pending/confirmed/preparing` (drifted from PRD and now retired)

**Payment Status**:
The state of payment for an order: `unpaid`, `paid`, `refunded`. Tracked on the order separately from order status, and mirrored on the Payment record.
_Avoid_: Payment state

**Order code**:
A human-readable unique identifier for an order within a restaurant (e.g., `ORD-20260808-AB12CD34`). Used by customers and staff to reference an order without login.

### Payments

**Payment**:
A payment attempt for an order using a chosen method. One order can have payments (first successful marks the order paid). Records method, amount, status, provider, reference, and timing.
_Avoid_: Charge, transaction

**Payment method**:
How the customer pays: `cash`, `qris`, `bank_transfer`, or `ewallet`.
_Avoid_: Payment type, channel

**Payment gateway**:
A pluggable adapter behind a common interface (`create_payment`, `verify_callback`) that talks to a payment provider. `dummy` is the default for development (no network); `midtrans` is the real provider (QRIS + Virtual Account + e-wallet via Snap) activated when keys exist.
_Avoid_: Payment provider (provider is the specific company, gateway is our adapter)

**Receipt (struk)**:
A printable 80mm thermal-style summary of an order and its payment, available to the customer after ordering and to staff from the order detail page.
_Avoid_: Invoice, bill

### Staff & Access

**Staff role**:
The access level of an internal user. Roles: `owner`, `admin`, `kasir`, `dapur`. Owner/Admin have full access; Kasir handles orders and payments; Dapur sees a kitchen-focused order board and can only advance food statuses.
_Avoid_: User type, permission group

**UserProfile**:
A OneToOne extension of the Django User carrying the staff `role` and the `restaurant` the user belongs to.
_Avoid_: Account, member

### Branding

**Appearance theme**:
A restaurant's customer-facing look and feel: colors, font, layout style, header/button style, plus banner image, tagline/greeting, receipt footer text, and contact info. Applies to the customer menu, cart, and order-success/receipt pages.
_Avoid_: Theme, skin (keep Appearance theme)
