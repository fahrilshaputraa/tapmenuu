# TapMenu — Design System

Source-of-truth snapshot synthesized from `design/` (static prototypes) and `core/templates/` (implemented Django templates) as of 2026-08-21.

---

## 1. Sources

| Source | Path | Role |
|---|---|---|
| Dashboard prototype | `design/index.html` (525 LOC) | Owner dashboard — hero stats, KPI cards, 7-day bar, recent orders, quick actions |
| Landing prototype | `design/landing-page.html` (694 LOC) | Public marketing page — navbar, hero phone mock, features, pricing, testimonials |
| Customer menu (HTML) | `design/book-menu.html` (421 LOC) | Mobile-first QR menu — card list, floating cart bar, bottom-sheet cart, success overlay |
| Customer menu (React) | `design/book-menu.jsx` (408 LOC) | Same as above as `CustomerMenu()` — banner/logo hero, sticky filter, drawer semantics |
| Order board | `design/menu.html` (551 LOC) | `menu.html` = order list (Kanban-ish grid) + status tabs + detail modal |
| Menu management | `design/management-menu.html` (916 LOC) | CRUD menu grid + 4-tab modal (basic/pricing/variants/stock) |
| Store profile | `design/store.html` (365 LOC) | Profil Toko — logo + banner upload, identitas, sosmed |
| Employee | `design/employee.html` (517 LOC) | Manajemen Karyawan — table, role badges, toggle, PIN modal |
| Reports | `design/laporan.html` (564 LOC) | Laporan & Keuangan — 3 summary cards, Chart.js line, top kasir, transaction table |
| Auth | `design/login.html` (256 LOC), `design/register.html` (297 LOC) | Split-screen auth with marketing panel left / form card right |
| Implemented base | `core/templates/layouts/base.html:1-19`, `core/templates/layouts/dashboard.html:1-34` | Shared layout shells |
| Implemented customer menu | `core/templates/menus/customer_menu.html:1-365` | Theming via CSS vars + bottom-sheet order sheets per item |
| Implemented dashboard | `core/templates/core/pages/dashboard.html:1-307` | Real data binding (revenue, AOV, recent orders) |
| Implemented menu mgmt | `core/templates/core/pages/management-menu.html:1-755` | Django-bound grid + AJAX FormData submit |

---

## 2. Design Tokens

### 2.1 Colors (`tailwind.config` in every prototype)

All prototypes share one config at e.g. `design/index.html:17-42`, `design/landing-page.html:20-39`:

```js
primary:      '#1B4332'  // Deep Emerald — headers, primary buttons, sidebar brand
primaryLight: '#2D6A4F'  // hover on primary
secondary:    '#D8F3DC'  // Mint — active nav, badges, pale cards
accent:       '#E07A5F'  // Terracotta — CTA, price, floating cart, highlights
bg:           '#F7F5F2'  // Bone White — page background
dark:         '#2D3436'  // Charcoal — body text

// contextual (dashboard/order board)
success:  '#10B981'   // ready / completed
warning:  '#F59E0B'   // pending / new-order border  design/menu.html:30
danger:   '#EF4444'   // stock critical / delete
info:     '#3B82F6'   // processing
pending:  '#F59E0B'   // design/menu.html alias
processing:'#3B82F6'
ready:    '#10B981'
```

Theming override (customer-facing only): `core/templates/menus/customer_menu.html:17-25` exposes CSS vars from `appearance_theme`:

```
--menu-primary  (default #1B4332)   --menu-secondary (#D8F3DC)
--menu-accent   (default #E07A5F)   --menu-bg        (#F7F5F2)
--menu-text     (default #1F2933)   --menu-card      (#FFFFFF)
--menu-font     (default 'Plus Jakarta Sans')
```

`data-menu-theme` remaps `.bg-primary`, `.text-primary`, `.bg-accent`, `.bg-white` article cards, etc. at `customer_menu.html:37-59`.

### 2.2 Typography

- Primary: `Plus Jakarta Sans` 400/500/600/700/800 via Google Fonts (every file). Customer menu additionally loads `Inter`, `Lora`, `Nunito`, `Poppins` at `customer_menu.html:11` to support `Appearance theme.font_family` switching (`:root --menu-font`).
- Tracking: labels use `tracking-[0.2em]` / `tracking-[0.18em]` uppercase microcopy (`design/index.html:175`, `design/login.html:161`).
- Scale: landing hero `text-4xl md:text-6xl lg:text-7xl font-extrabold leading-[1.1]`; KPI numbers `text-2xl font-extrabold`; card titles `text-xl font-extrabold`.

### 2.3 Spacing / Radius / Shadows

```js
boxShadow: {
  card: '0 2px 12px rgba(0,0,0,0.06)',       // all cards
  soft: '0 8px 32px -12px rgba(27,67,50,0.12)' // hero / landing
  floating: '0 -4px 20px rgba(0,0,0,0.1)'     // cart bar / sheets
}
// radii: pattern is large, friendly — 1.5rem / 1.75rem / 2rem / 2.5rem / 3rem
// e.g. dashboard card rounded-[1.75rem], hero rounded-[2rem], phone mock rounded-[2.5rem], CTA rounded-[3rem]
```

### 2.4 Icons & Media

- `font-awesome 6.4.0` everywhere (`design/index.html:14`). Canonical icons: `fa-utensils` (brand), `fa-qrcode`, `fa-receipt`, `fa-chart-pie`, `fa-wallet`, `fa-store`, `fa-users-gear`, `fa-plus/pen/trash/eye`.
- Images: Unsplash food shots (w=100–400, q=80) + `i.pravatar.cc` for people; fallbacks `cdn-icons-png.flaticon.com/512/2921/2921822.png` (logo) and `DEFAULT_BANNER` (Unsplash restaurant) in `design/book-menu.jsx:4-5`.

### 2.5 Animations

```css
fadeIn:      opacity 0->1 + translateY 5-6px 0.3-0.35s       // design/index.html:63-77, management-menu.html:64-78
slideUp:     translateY(100%) -> 0  0.3s cubic-bezier(.16,1,.3,1) // design/book-menu.html:61-68
pop:         scale 0.9->1.1->1  0.2s                         // qty stepper
float:       translateY 0/-10px rotate -2deg  6s infinite   // landing phone + login testimonial
blink-border: 2s infinite border-color #F59E0B <-> transparent // new order card design/menu.html:82-99
custom-scroll: 6px thumb #cbd5e1 rounded-full               // dashboard scroll areas
```

Chart is `Chart.js` line with gradient fill + tension 0.4 at `design/laporan.html:13, 457-533`.

---

## 3. Layout Shells

### 3.1 Public Shell (Landing / Login / Register)

```
design/landing-page.html:85-130  navbar fixed backdrop-blur + mobile dropdown toggleMenu()
design/login.html:66-242         min-h-screen grid lg:grid-cols-2
  left (hidden lg:flex): bg-primary rounded-[2.5rem] marketing panel (~50%)
  right: centered max-w-xl form card bg-white border rounded-[2rem] shadow-card
```

Landing sections in order: navbar → hero (2-col text + floating phone mock `design/landing-page.html:132-276`) → features 3-col grid → audience showcase → pricing 3-col (`Starter/Growth/Enterprise`) → testimonials 3-col → CTA dark pill → footer 4-col.

### 3.2 Dashboard Shell (`core/templates/layouts/dashboard.html:20-32`)

```
<div flex h-screen overflow-hidden>
  <aside w-64/72 bg-white border-r>  — brand + nav groups (Utama / Keuangan / Pengaturan) + profile footer
  <div data-dashboard-sidebar-backdrop fixed inset-0 bg-black/40 hidden md:hidden>
  <main flex-1 flex flex-col overflow-hidden>
    header sticky top-0 bg-white/80 backdrop-blur-md border-b  (title + actions + [data-dashboard-menu-button])
    div flex-1 overflow-y-auto p-6 custom-scroll  (page content)
  footer
</div>
<script dashboard-shell.js> handles [data-dashboard-menu-button] -> aria-expanded + backdrop
```

Implemented sidebar lives at `core/templates/core/partials/dashboard_sidebar.html`. Prototype sidebars are inline (e.g. `design/index.html:83-140`).

Every dashboard page follows: breadcrumb kicker (`text-xs uppercase tracking-[0.2em] text-gray-400`) + `h1 font-extrabold text-dark` + subtitle.

### 3.3 Customer Shell (`core/templates/menus/customer_menu.html:61-262`)

```
<body data-menu-theme data-layout-style data-header-style data-button-style>
  <main min-h-screen pb-40>
    <header bg-primary rounded-b-[2rem/3rem]>  (restaurant name + table badge, tagline/greeting, cart icon with qty badge)
    <nav category tabs>  [data-menu-tab] pills — active bg-primary, inactive bg-white border
    <section per-category panels> [data-menu-panel] grid 1 / sm:2 / xl:3 (grid|compact|featured via data-layout-style)
      <article fade-item bg-white rounded-[1.75rem] shadow-card>  (image 24/28, favorite/new chips, price text-accent, + variant hint)
    [order sheets] one fixed bottom sheet per item: handle bar + variant groups + qty/note + submit -> POST customer_cart_add
  </main>
</body>
```

Sticky offset handled by `scroll-mt-6`. Theming modifiers at `customer_menu.html:48-58`:

- `data-header-style`: `minimal` (flat), `hero` (gradient `primary->accent`, `min-h-[18rem]`), default `rounded` (rounded-b + blobs).
- `data-button-style`: `pill` (999px), `square` (0.65rem), default `rounded` (0.75rem / xl).
- `data-layout-style`: `compact` (tight padding, 4.5rem thumbs), `featured` (first card spans full row), default `grid`.

---

## 4. Page Inventory

| Route (impl) / File (design) | Prototype | Implemented Template | Notes |
|---|---|---|---|
| `/` | `design/landing-page.html` | `core/templates/core/landing.html` + `core/pages/landing.html` | pricing/Testimoni blocks kept; real auth links |
| `/accounts/login/` | `design/login.html` | `core/pages/login.html` | `Welcome Back` badge, `#FCFBF9` inputs, eye toggle `togglePassword()` |
| `/accounts/register/` | `design/register.html` | `core/pages/register.html` | 4-field + confirm + terms checkbox |
| `/dashboard/` | `design/index.html` | `core/pages/dashboard.html` | KPI hero + status toko + 5 stat cards + recent orders + quick actions |
| `/orders/` \| `/kitchen/` | `design/menu.html` | `core/pages/orders.html` + `dashboard/kitchen.html` + `dashboard/order_detail.html` | Status tabs (Baru/Diproses/Siap/Selesai) + card grid + detail modal; state machine `new→paid→processing→ready→completed` |
| `/menus/` | `design/management-menu.html` | `core/pages/management-menu.html` | Grid + 4-tab modal; implemented uses `FormData` + `fetch` to `menu_item_create/update` |
| `/restaurants/store/` | `design/store.html` | `core/pages/store.html` | Logo (circular) + banner (16:9) uploads, identitas, WA `+62` prefix, Maps link |
| `/onboarding/...` | — | `core/pages/onboarding-step{1,2,3}.html` | 3-step setup (restaurant → tables → menu) with desktop-responsive assets |
| `/menus/appearance/` | — | `core/pages/menu-appearance.html` | New vs prototype — controls `appearance_theme` (colors, font, layout/header/button style, greeting, show_category_tabs) consumed by customer menu vars |
| `/dashboard/tables/` | — | `core/pages/tables.html` | QR token per `DiningTable` (design has placeholder QR page link) |
| `/reports/` | `design/laporan.html` | `core/pages/reports.html` | Summary + chart + top kasir + transaction table; `today/week/month` toggle |
| `/employees/` | `design/employee.html` | `core/pages/employee.html` | Table with role badge, PIN masked, active toggle, avatar upload modal |
| `/categories/` | — | `core/pages/categories.html` | CRUD Menu Category (sort_order) — not in design folder, inferred from nav |
| `/cart/<qr>/`, `/order/success`, `/order/status`, `/receipt` | `design/book-menu.html` + `book-menu.jsx` | `menus/customer_cart.html`, `customer_order_success.html`, `customer_order_status.html`, `customer_receipt.html` | Cart bound to `qr_token`, sheet submits qty/note/variant_options; order code `ORD-...` |

---

## 5. Component Catalog

### 5.1 Navigation

- **Dashboard sidebar nav item**: active `bg-secondary/50 text-primary font-bold rounded-xl` + icon `w-5`; inactive `text-gray-500 hover:bg-gray-50` (`design/index.html:97-105`). Group headings `text-xs font-bold uppercase tracking-wider text-gray-400`. Footer profile: `bg-gray-50 rounded-2xl` with avatar + chevron.
- **Top header**: `bg-white/80 backdrop-blur-md sticky top-0 border-b` with mobile hamburger `[data-dashboard-menu-button]` → `dashboard-shell.js`.

### 5.2 Cards

- **Dashboard KPI**: `bg-white rounded-[1.75rem] p-5 border shadow-card` — icon `w-11 h-11 rounded-2xl bg-{color}-100` + tiny pill badge. Variant: hero primary card `xl:col-span-2 bg-primary rounded-[2rem] p-7` with two decorative blobs and inner `bg-white rounded-[1.75rem]` progress widget.
- **Order card** (`design/menu.html:400-454`): `bg-white rounded-2xl p-5 shadow-card border`, header `border-b`, preview list (max 2 items + `+N lainnya`), footer total `font-extrabold text-primary`, action button color-coded by status (primary / blue-600 / green-600), `new-order-card` blinking amber border.
- **Menu card** (`core/pages/management-menu.html:70`): `h-40` image + category chip `bg-black/60 backdrop-blur` + discount chip `bg-red-500`; body `p-4` with `rounded-2xl shadow-card`; footer toggle + Edit link.
- **Customer menu card** (`customer_menu.html:138-171`): `fade-item bg-white rounded-[1.75rem] p-4/5` with `w-24/h-24 sm:w-28/h-28 rounded-2xl` image, `is_favorite/is_new` chips, `text-accent` price, full-width `bg-accent rounded-xl` CTA.

### 5.3 Tabs & Filters

- **Status / category pills**: active `bg-primary text-white shadow-sm rounded-lg/xl` vs inactive `bg-white text-gray-500 border border-gray-200` (`design/menu.html:187-199`, `design/management-menu.html:182-189`). Customer tabs: circular `rounded-full` with `[data-menu-tab]` → `setActiveTab()` + `[data-menu-panel].hidden` (`customer_menu.html:264-291`).
- **Laporan period filter** (`design/laporan.html:167-181`): segmented control `bg-white border p-1 rounded-lg` with `bg-gray-100 text-dark font-bold` active vs `text-gray-500`.

### 5.4 Forms

- Inputs: `bg-[#FCFBF9] or bg-gray-50 border-gray-200 rounded-xl px-4 py-3.5 text-sm font-medium focus:border-primary focus:ring-4 focus:ring-secondary/60` with left icon `absolute left-4` (envelope/lock/store) and optional right eye toggle (`design/login.html:161-186`). WA input has `+62` prefix span (`design/store.html:265-271`).
- Textarea: `resize-none rounded-xl p-4`.
- Selects: same treatment + `appearance-none`.
- Price input: left `Rp` span + `text-lg font-bold` (`design/management-menu.html:312-314`).

### 5.5 Modals / Sheets

- **Order detail modal** (`design/menu.html:232-279`): `fixed inset-0 bg-black/50 backdrop-blur-sm` + center `max-w-md rounded-2xl shadow-2xl` with primary header + scroll `bg-[#F7F5F2]` body + 2-col footer `[Tutup | Proses Pesanan]`.
- **Menu CRUD modal** (`core/pages/management-menu.html:157-391`): `max-w-2xl max-h-[95vh]` + tab bar `border-b bg-gray-50 pt-2` with `border-primary text-primary` active vs `border-transparent text-gray-500`; body 4 panels (see §7); footer `[Batal | Simpan Menu]` on `bg-gray-50`.
- **Employee modal** (`design/employee.html:250-319`): `max-w-md` + centered avatar upload (`w-24 h-24 rounded-full border-4`) + camera button; PIN `tracking-widest` with eye toggle.
- **Customer bottom sheets** (`customer_menu.html:194-261` + `design/book-menu.html:129-180`): `fixed inset-0 z-50 hidden` + `bg-black/45` backdrop `[data-close-cart-sheet]` + bottom panel `rounded-t-[2rem] translate-y-full transition-transform` + handle `w-12 h-1.5 bg-gray-300`; header drag zones `[data-sheet-drag-zone]` with pointer capture; Escape closes all (`keydown Escape`).

### 5.6 Overlays

- **Success overlay** (`design/book-menu.html:182-201`, `customer_order_success.html`): `fixed inset-0 z-[60] bg-primary flex col center` + `w-24 h-24 bg-white/20 rounded-full animate-bounce` check + `bg-white/10 backdrop-blur-md border-white/10` estimate card + reload CTA.
- **Toast** (`core/pages/dashboard.html:291-306`): `#welcome-toast` `fixed top-6 right-6 max-w-sm bg-white rounded-2xl shadow-2xl border-green-100` for `show_welcome_toast`.
- **Floating cart bar** (`design/book-menu.html:107-126`, `customer_menu.html:272-289`): `fixed bottom-4 / sticky bottom-0 bg-primary rounded-2xl p-4 shadow-floating` showing `total_quantity` badge + `total_amount` + `Lihat Pesanan` accent button; hidden when cart empty.

---

## 6. Auth Patterns (Login / Register)

Split-screen identity consistent across `design/login.html` and `register.html`:

- Blob bgs: `bg-secondary rounded-full blur-3xl` + `bg-accent/15 rounded-full`.
- Left panel: `bg-primary rounded-[2.5rem]` with `bg-white/5`, `bg-accent/20` orbs; pill `bg-white/10 uppercase tracking-[0.2em]`; 2 feature cards `bg-white/10 border-white/10 backdrop-blur-sm`; floating bottom card (`floating-card`) — login: quote from owner; register: 2×2 benefits grid.
- Right panel: `bg-white border rounded-[2rem] shadow-card p-7 sm:p-10`; header pill `bg-secondary/70 text-primary tracking-[0.2em]`; inputs `#FCFBF9`; primary CTA `bg-accent text-white rounded-xl shadow-lg hover:bg-[#d06a50] hover:-translate-y-0.5`; divider `border-t + bg-white px-4`; secondary CTAs `border bg-white hover:border-primary`; helper card `bg-[#F7F5F2]` with icon.
- Behavior: `togglePassword(inputId, iconId)` swaps `password<->text` + `fa-eye <-> fa-eye-slash` (`design/login.html:244-253`, `register.html:285-293`).

---

## 7. Dashboard Deep Dives

### 7.1 Main Dashboard (`design/index.html` → `core/pages/dashboard.html`)

- Hero: `grid md:grid-cols-[1.4fr,1fr]` — left editorial + 2 CTAs (Laporan / QR), right target widget with `h-3` progress + 2× metrics (`Transaksi`, `AOV`).
- Implemented binds `total_orders`, `active_orders`, `revenue`, `paid_count`, `average_order_value`, `table_with_orders/table_total`, `menu_count`, `recent_orders` (loop `order.code / dining_table.table_number / created_at / total_amount`). Empty states are dashed-border cards, not the prototype's hardcoded lists.
- Status toko card shows `restaurant.name` and live counts; note the prototype's 4 extra metrics (QR scans, stok kritis) are not implemented — kept as static copy only in `design/index.html`.

### 7.2 Pesanan Board (`design/menu.html`)

- Tabs: Semua / Baru (badge `bg-red-500 text-[10px]`) / Diproses / Siap Saji / Selesai. Logic at `design/menu.html:379-491`: `currentFilter`, `searchVal` (by `id` + `table`), empty-state `hidden` toggle, per-status `statusBadge` + `actionBtn` + `cardClass`.
- Lifecycle: `new -> process -> ready -> completed` via `updateStatus()`; modal `openDetail()` shows variants + notes + total and next-step CTA (`Terima Pesanan` → `Selesai Masak` → `Antar & Selesai`).

### 7.3 Manajemen Menu — 4-Tab Modal

Prototype `design/management-menu.html:235-456` vs implemented `core/pages/management-menu.html:182-382` (same structure, Django-bound):

1. **Info Dasar**: square dashed image dropzone (`aspect-square border-2 border-dashed`) + preview `object-cover`; fields `Nama Menu*`, `Kategori*` (select), `Deskripsi` (textarea).
2. **Harga & Pajak**: `Harga Dasar*` (Rp prefix, `text-lg font-bold`), `Diskon %`, `Pajak %` (default 10), live preview card `bg-secondary/30 border-secondary` computing `final = price * (100-discount)/100` via `calculateFinalPrice()` (`design/management-menu.html:724-741`).
3. **Varian**: info banner `bg-blue-50 border-blue-100`; JS `addVariantGroup(data)` (grid `Nama Grup` + `Tipe [radio|checkbox]`) + `addVariantOption(groupId)` (`Nama Opsi` + `+Rp price_adjustment` + remove x) . `collectVariantData()` gathers to `variants[]` (`design/management-menu.html:754-852`).
4. **Stok & Lainnya**: stock toggle → reveals `Jumlah Stok`; labels `Favorit` (`#FFF0EB / accent`) & `Baru` (`secondary / primary`) peer-checked pills; `Tampilkan di Menu` (`is_active`) + `Tersedia` (`is_available`) toggles (`core/pages/management-menu.html:349-378`).

Grid JS: `filterMenu(category)` toggles `article[data-category]` display; `searchMenu()` matches `data-name | data-category | data-category-name`; `openAddModal()` resets, `openEditModal(cardEl)` hydrates from `data-item-*` + `fetch(variantsUrl)` (`core/pages/management-menu.html:414-560`); `saveMenu()` builds `FormData` + `variants=JSON.stringify(variantGroups)` + AJAX `fetch(form.action, {method:POST, body})` with `X-Requested-With: XMLHttpRequest`.

### 7.4 Laporan (`design/laporan.html:188-316`)

Three summary cards (Omzet green, Transaksi blue, Avg orange) with `animateValue(id, end, isCurrency)` count-up (500ms, `requestAnimationFrame`). Main `Grid lg:grid-cols-3` — left `lg:col-span-2` chart (`canvas#salesChart`) + right top-performer list (`#employee-stats-container`) sorted by total, first-place `bg-primary` bar width `percent = total / max *100`, badge `#n` colors gold/gray/bronze. Bottom: transaction history table with `Tunai` green vs `QRIS` blue pills (`design/laporan.html:324-560`). Implemented `core/pages/reports.html` reuses same structure with real `Order/Payment` aggregation.

---

## 8. Customer Journey (QR → Receipt)

1. **Menu** (`customer_menu.html`): header with restaurant + `Meja N`; category pills; card grid. Add → bottom sheet (variants + qty + note) → `POST customer_cart_add`. Appearance theming drives `primary/secondary/accent/bg/text/font/layout/header/button` — controlled from `menu-appearance` page.
2. **Cart** (`customer_cart.html`): bottom sheet / page mirrors `design/book-menu.html:156-180` bill (`Subtotal / Pajak 10% / Total` with `border-dashed` divider) — bound to session Cart keyed by `qr_token`.
3. **Checkout** (`customer_order_success.html` / `_status`): success overlay + order code `ORD-YYYYMMDD-XXXX` + receipt footer + estimasi `15-20 Menit`; polling order `status` (`new → paid → processing → ready → completed`) and `payment_status` (`unpaid/paid/refunded`).
4. **Receipt** (`customer_receipt.html`): 80mm thermal style `struk` printable (accessibility `aria`, monochrome friendly).

---

## 9. Responsive & Accessibility

- Breakpoints Lean Tailwind: `sm` (64), `md` (768, sidebar breakpoint), `lg`, `xl` (grid 3→4). Sidebars `hidden md:flex`; mobile hamburger `md:hidden` + backdrop + `dashboard-shell.js` toggles `hidden` + `aria-expanded`.
- Customer menu uses `maximum-scale=1.0 user-scalable=no` for kiosk feel but includes `aria-label` on cart, `aria-pressed` on tabs, `aria-hidden` on sheets, proper `<label for>` on qty/note (`customer_menu.html:82-89, 242-250`).
- Scroll: `.custom-scroll` (6px #cbd5e1 thumb) for dashboard panels; `.no-scrollbar` for category pills (scroll-snap).
- All primary actions are `type="button"` or `POST` with `{% csrf_token %}`; destructive (menu delete) has `onsubmit="return confirm(...)"`.

---

## 10. Prototype → Implementation Delta (what changed)

| Area | Prototype (`design/`) | Implemented (`core/templates/`) | Recommendation |
|---|---|---|---|
| Styling pipeline | Inline CDN `https://cdn.tailwindcss.com` + inline `tailwind.config` per file | `layouts/dashboard.html` still uses CDN (with `dashboard-*.js` shim) but `layouts/base.html` now serves `core/css/main.css` + `core/js/main.js` (built Tailwind) | Finish migration: remove CDN from dashboard layout; consolidate `tailwind.config` to one source. |
| Dashboard metrics | Hardcoded demo (“Rp 2.072.000”, “128 transaksi”) | Real `revenue = paid orders`, `AOV = revenue/total_orders`, `recent_orders` queryset | Keep; consider re-adding “QR scans / stock critical” once metrics exist — currently prototype-only. |
| Laporan chart | Chart.js CDN live toggle today/week/month | Same toggle wired to queryset | OK — keep animation (`animateValue`) for polish. |
| Menu management | Full JS array + `saveMenu()` → pushes to `menuList` | Django posts: `menu_item_create/update/delete` + `variants` JSON + `is_active/is_available` split + `fetch` + `window.location.reload()` | Parity achieved; drop discount/tax preview “*Belum termasuk PPN” copy if unused in pricing engine. |
| Customer theming | Static `primary/accent` only | `appearance_theme` vars + `menu-appearance` controls | Keep current — this is the main design divergence worth preserving. |
| Auth marketing copy | Full left storytelling panel + float card | Same concept but shorter onboarding steps (1→2→3) with toast `Toko berhasil dibuat! 🎉` | Align copy; reuse login panel illustration in onboarding. |

---

## 11. File Map

```
design/
  index.html              # dashboard prototype (sidebar 72, hero 2-col, 4 KPI, 7-day bars, orders, quick actions)
  landing-page.html       # public landing
  menu.html               # orders board (not “menu” — naming is historical)
  management-menu.html    # menu CRUD
  book-menu.html/.jsx     # customer menu + cart + success (HTML + React reference)
  store.html              # profil toko
  employee.html           # karyawan
  laporan.html            # laporan (Chart.js)
  login.html / register.html
  store.html

core/templates/
  layouts/base.html + dashboard.html
  core/partials/dashboard_sidebar.html + dashboard_footer.html
  core/{landing,index}.html
  core/pages/{dashboard,management-menu,store,employee,laporan→reports,tables,categories,
              menu-appearance,onboarding-step{1,2,3},orders,login,register}.html
  menus/{customer_menu,customer_cart,customer_order_success,customer_order_status,customer_receipt}.html
  dashboard/{order_detail,kitchen}.html
static/
  core/css/{main.css, pages/{dashboard-1,management-menu-1,book-menu-1}.css}
  core/js/{main.js, dashboard-shell.js, pages/{dashboard-1,management-menu-1,book-menu-1}.js}
```

---

## 12. How to Extend

- New dashboard page: `{% extends 'layouts/dashboard.html' %}` → put header + `<div flex-1 overflow-y-auto p-6 custom-scroll><div max-w-7xl mx-auto space-y-8 fade-in>` — see `core/pages/dashboard.html:36-289` as canonical.
- New customer-facing style: add CSS var in `customer_menu.html:17-25` and consume with `body[data-menu-theme] …` + expose control in `menu-appearance.html`.
- New modal: copy `fixed inset-0 z-50 hidden bg-black/50 backdrop-blur-sm flex items-center justify-center p-4 fade-in` wrapper + `max-w-* rounded-2xl shadow-2xl max-h-[90vh] overflow-hidden flex flex-col` + tab bar pattern from management-menu; sheets should use bottom `translate-y-full` + pointer drag pattern from `customer_menu.html:324-355`.

