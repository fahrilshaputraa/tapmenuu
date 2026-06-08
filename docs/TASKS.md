# TapMenu Implementation Tasks

> **For Hermes:** Gunakan `subagent-driven-development` skill jika nanti task ini dieksekusi bertahap. Jalankan task satu per satu, verifikasi, lalu lanjut ke task berikutnya.

**Goal:** Membangun MVP TapMenu: website memiliki landing page publik, pelanggan scan QR meja, melihat menu, membuat pesanan, memilih pembayaran digital, dan staff/admin dapat mengelola pesanan serta menu.

**Architecture:** Django monolith dengan beberapa app modular: `accounts`, `restaurants`, `menus`, `orders`, `payments`, dan `dashboard`. Template global disimpan di `core/templates`, static global di `core/static`. Business logic penting seperti order calculation dan payment gateway abstraction dipisahkan ke service layer agar mudah dites.

**Tech Stack:** Python 3.13, Django 4.2, SQLite untuk development, Django Templates, CSS/JS static biasa, payment gateway abstraction untuk QRIS/Virtual Account/e-wallet.

---

## Prinsip Implementasi

- Mulai dari model dan test, baru lanjut ke view/template.
- Semua fitur penting wajib punya test minimal.
- Jangan langsung integrasi payment gateway real sebelum flow internal stabil.
- Simpan snapshot harga menu di `OrderItem`, supaya histori transaksi tidak berubah saat harga menu diedit.
- Root URL `/` harus membuka landing page publik, bukan dashboard.
- Customer tidak perlu login untuk order dari QR meja.
- Admin/staff wajib login untuk akses dashboard.
- Link utama login/register/dashboard tidak boleh menggunakan `href="#"`; pakai `{% url %}` atau URL Django yang valid.
- Desain source di folder `design/` jangan diubah dulu; copy/convert ke template Django saat task UI dimulai.

---

## Phase 0 — Project Baseline

### Task 0.1: Verifikasi struktur awal Django

**Objective:** Memastikan project `tapmenu` dan Django project `core` siap digunakan.

**Files:**
- Check: `manage.py`
- Check: `core/settings.py`
- Check: `core/urls.py`
- Check: `core/templates/layouts/base.html`
- Check: `core/static/core/css/main.css`
- Check: `core/static/core/js/main.js`

**Steps:**

1. Jalankan check Django:

```bash
cd /home/fahril/playground/project/tapmenu
.venv/bin/python manage.py check
```

Expected:

```text
System check identified no issues
```

2. Pastikan static global bisa ditemukan:

```bash
.venv/bin/python manage.py findstatic core/css/main.css core/js/main.js --verbosity 1
```

Expected:

```text
Found 'core/css/main.css'
Found 'core/js/main.js'
```

---

### Task 0.2: Buat route landing page publik di `/`

**Objective:** Menjadikan landing page sebagai halaman awal website TapMenu sebelum user masuk login/register/dashboard.

**Files:**
- Create: `core/views.py`
- Create/Modify: `core/templates/core/landing.html`
- Modify: `core/urls.py`
- Modify: `core/templates/layouts/base.html`
- Modify: `core/static/core/css/main.css`
- Modify: `core/static/core/js/main.js`

**Steps:**

1. Buat view landing di `core/views.py`:

```python
from django.shortcuts import render


def landing(request):
    return render(request, 'core/landing.html')
```

2. Tambahkan route root di `core/urls.py`:

```python
from django.contrib import admin
from django.urls import path

from . import views

urlpatterns = [
    path('', views.landing, name='landing'),
    path('admin/', admin.site.urls),
]
```

3. Buat placeholder `core/templates/core/landing.html` yang extends `layouts/base.html`.

4. Tambahkan CTA login/register sebagai placeholder URL yang nanti disambungkan ke Django auth ketika Task 6 berjalan. Jika URL auth belum ada, gunakan teks/button non-link dulu atau route yang sudah valid; jangan gunakan `href="#"` untuk aksi utama.

5. Verifikasi Django:

```bash
.venv/bin/python manage.py check
```

Expected: no issues.

6. Jalankan server dan cek root `/`:

```bash
.venv/bin/python manage.py runserver
```

Expected: halaman landing tampil di `http://127.0.0.1:8000/`.

**Acceptance Criteria:**

- `/` membuka landing page.
- Landing page punya hero, benefit singkat, cara kerja singkat, dan CTA login/register.
- Tidak ada link aksi utama yang masih `href="#"`.
- Static CSS/JS tetap berasal dari `core/static/core/`.

---

## Phase 1 — App Structure

### Task 1.1: Buat app `accounts`

**Objective:** Menyediakan tempat untuk user, role, dan akses staff/admin.

**Files:**
- Create: `accounts/`
- Modify: `core/settings.py`

**Steps:**

1. Buat app:

```bash
.venv/bin/python manage.py startapp accounts
```

2. Tambahkan ke `INSTALLED_APPS` di `core/settings.py`:

```python
INSTALLED_APPS = [
    ...
    'accounts',
]
```

3. Verifikasi:

```bash
.venv/bin/python manage.py check
```

Expected: no issues.

---

### Task 1.2: Buat app `restaurants`

**Objective:** Menyimpan data resto/kafe dan meja QR.

**Files:**
- Create: `restaurants/`
- Modify: `core/settings.py`

**Steps:**

```bash
.venv/bin/python manage.py startapp restaurants
```

Tambahkan:

```python
'restaurants',
```

ke `INSTALLED_APPS`.

Verifikasi:

```bash
.venv/bin/python manage.py check
```

---

### Task 1.3: Buat app `menus`

**Objective:** Menyimpan kategori dan item menu.

**Files:**
- Create: `menus/`
- Modify: `core/settings.py`

**Steps:**

```bash
.venv/bin/python manage.py startapp menus
```

Tambahkan:

```python
'menus',
```

ke `INSTALLED_APPS`.

Verifikasi:

```bash
.venv/bin/python manage.py check
```

---

### Task 1.4: Buat app `orders`

**Objective:** Menyimpan order dan detail item pesanan.

**Files:**
- Create: `orders/`
- Modify: `core/settings.py`

**Steps:**

```bash
.venv/bin/python manage.py startapp orders
```

Tambahkan:

```python
'orders',
```

ke `INSTALLED_APPS`.

Verifikasi:

```bash
.venv/bin/python manage.py check
```

---

### Task 1.5: Buat app `payments`

**Objective:** Menyimpan data pembayaran dan payment provider abstraction.

**Files:**
- Create: `payments/`
- Modify: `core/settings.py`

**Steps:**

```bash
.venv/bin/python manage.py startapp payments
```

Tambahkan:

```python
'payments',
```

ke `INSTALLED_APPS`.

Verifikasi:

```bash
.venv/bin/python manage.py check
```

---

### Task 1.6: Buat app `dashboard`

**Objective:** Menyediakan halaman admin/staff dashboard.

**Files:**
- Create: `dashboard/`
- Modify: `core/settings.py`

**Steps:**

```bash
.venv/bin/python manage.py startapp dashboard
```

Tambahkan:

```python
'dashboard',
```

ke `INSTALLED_APPS`.

Verifikasi:

```bash
.venv/bin/python manage.py check
```

---

## Phase 2 — Models dan Database

### Task 2.1: Buat model `Restaurant`

**Objective:** Menyimpan profil resto/kafe.

**Files:**
- Modify: `restaurants/models.py`
- Modify: `restaurants/admin.py`
- Test: `restaurants/tests.py`

**Model fields:**

```python
name = models.CharField(max_length=150)
slug = models.SlugField(max_length=180, unique=True)
description = models.TextField(blank=True)
address = models.TextField(blank=True)
phone = models.CharField(max_length=30, blank=True)
logo = models.ImageField(upload_to='restaurants/logos/', blank=True, null=True)
is_active = models.BooleanField(default=True)
created_at = models.DateTimeField(auto_now_add=True)
updated_at = models.DateTimeField(auto_now=True)
```

**Acceptance Criteria:**

- Restaurant bisa dibuat.
- `slug` unik.
- `__str__` mengembalikan nama resto.
- Terdaftar di Django Admin.

**Verification:**

```bash
.venv/bin/python manage.py makemigrations restaurants
.venv/bin/python manage.py migrate
.venv/bin/python manage.py test restaurants
```

---

### Task 2.2: Buat model `DiningTable`

**Objective:** Menyimpan data meja dan token QR unik.

**Files:**
- Modify: `restaurants/models.py`
- Modify: `restaurants/admin.py`
- Test: `restaurants/tests.py`

**Model fields:**

```python
restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE, related_name='tables')
number = models.CharField(max_length=30)
qr_token = models.SlugField(max_length=80, unique=True)
is_active = models.BooleanField(default=True)
created_at = models.DateTimeField(auto_now_add=True)
updated_at = models.DateTimeField(auto_now=True)
```

**Rules:**

- Kombinasi `restaurant + number` harus unik.
- `qr_token` harus unik global.
- Nama class pakai `DiningTable`, bukan `Table`, supaya tidak membingungkan dengan database table.

**Acceptance Criteria:**

- Meja bisa dibuat untuk resto.
- Satu resto tidak boleh punya nomor meja duplicate.
- QR token bisa dipakai untuk membuka menu customer.

---

### Task 2.3: Buat model `Category`

**Objective:** Menyimpan kategori menu per resto.

**Files:**
- Modify: `menus/models.py`
- Modify: `menus/admin.py`
- Test: `menus/tests.py`

**Model fields:**

```python
restaurant = models.ForeignKey('restaurants.Restaurant', on_delete=models.CASCADE, related_name='categories')
name = models.CharField(max_length=100)
sort_order = models.PositiveIntegerField(default=0)
is_active = models.BooleanField(default=True)
created_at = models.DateTimeField(auto_now_add=True)
updated_at = models.DateTimeField(auto_now=True)
```

**Rules:**

- Kategori diurutkan berdasarkan `sort_order`, lalu `name`.
- Nama kategori boleh sama di resto berbeda.

---

### Task 2.4: Buat model `MenuItem`

**Objective:** Menyimpan makanan/minuman yang dapat dipesan pelanggan.

**Files:**
- Modify: `menus/models.py`
- Modify: `menus/admin.py`
- Test: `menus/tests.py`

**Model fields:**

```python
restaurant = models.ForeignKey('restaurants.Restaurant', on_delete=models.CASCADE, related_name='menu_items')
category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True, related_name='items')
name = models.CharField(max_length=150)
description = models.TextField(blank=True)
price = models.PositiveIntegerField()
image = models.ImageField(upload_to='menus/items/', blank=True, null=True)
is_available = models.BooleanField(default=True)
is_active = models.BooleanField(default=True)
created_at = models.DateTimeField(auto_now_add=True)
updated_at = models.DateTimeField(auto_now=True)
```

**Rules:**

- Harga disimpan integer rupiah, bukan decimal.
- Menu tampil ke customer jika `is_active=True` dan `is_available=True`.

**Acceptance Criteria:**

- Menu bisa dibuat.
- Format harga bisa dibuat helper `formatted_price`.

---

### Task 2.5: Buat model `Order`

**Objective:** Menyimpan data pesanan pelanggan dari meja.

**Files:**
- Modify: `orders/models.py`
- Modify: `orders/admin.py`
- Test: `orders/tests.py`

**Model fields:**

```python
restaurant = models.ForeignKey('restaurants.Restaurant', on_delete=models.PROTECT, related_name='orders')
table = models.ForeignKey('restaurants.DiningTable', on_delete=models.PROTECT, related_name='orders')
order_number = models.CharField(max_length=30, unique=True)
customer_name = models.CharField(max_length=100, blank=True)
customer_note = models.TextField(blank=True)
status = models.CharField(max_length=20, choices=OrderStatus.choices, default=OrderStatus.NEW)
payment_status = models.CharField(max_length=20, choices=PaymentStatus.choices, default=PaymentStatus.PENDING)
total_amount = models.PositiveIntegerField(default=0)
created_at = models.DateTimeField(auto_now_add=True)
updated_at = models.DateTimeField(auto_now=True)
```

**Status order:**

```python
NEW = 'new'
PAID = 'paid'
PROCESSING = 'processing'
READY = 'ready'
COMPLETED = 'completed'
CANCELLED = 'cancelled'
```

**Acceptance Criteria:**

- Order number unik.
- Order terkait restaurant dan table.
- Default status adalah `new` dan payment `pending`.

---

### Task 2.6: Buat model `OrderItem`

**Objective:** Menyimpan snapshot item pesanan.

**Files:**
- Modify: `orders/models.py`
- Modify: `orders/admin.py`
- Test: `orders/tests.py`

**Model fields:**

```python
order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
menu_item = models.ForeignKey('menus.MenuItem', on_delete=models.PROTECT)
item_name = models.CharField(max_length=150)
item_price = models.PositiveIntegerField()
quantity = models.PositiveIntegerField(default=1)
note = models.CharField(max_length=255, blank=True)
subtotal = models.PositiveIntegerField(default=0)
```

**Rules:**

- `item_name` dan `item_price` diambil dari `MenuItem` saat order dibuat.
- `subtotal = item_price * quantity`.
- Jangan bergantung pada harga menu setelah transaksi dibuat.

---

### Task 2.7: Buat model `Payment`

**Objective:** Menyimpan metode dan status pembayaran order.

**Files:**
- Modify: `payments/models.py`
- Modify: `payments/admin.py`
- Test: `payments/tests.py`

**Model fields:**

```python
order = models.OneToOneField('orders.Order', on_delete=models.CASCADE, related_name='payment')
method = models.CharField(max_length=30, choices=PaymentMethod.choices)
provider = models.CharField(max_length=50, blank=True)
amount = models.PositiveIntegerField()
status = models.CharField(max_length=20, choices=PaymentStatus.choices, default=PaymentStatus.PENDING)
reference = models.CharField(max_length=120, blank=True)
payment_url = models.URLField(blank=True)
qr_string = models.TextField(blank=True)
paid_at = models.DateTimeField(blank=True, null=True)
created_at = models.DateTimeField(auto_now_add=True)
updated_at = models.DateTimeField(auto_now=True)
```

**Payment methods:**

```python
QRIS = 'qris'
VIRTUAL_ACCOUNT = 'virtual_account'
EWALLET = 'ewallet'
CASH = 'cash'
```

**Acceptance Criteria:**

- Payment hanya satu per order.
- Status default `pending`.
- Method dapat memilih QRIS, Virtual Account, e-wallet.

---

## Phase 3 — Service Layer

### Task 3.1: Buat order service `create_order_from_cart`

**Objective:** Membuat order dari item cart secara aman dan terpusat.

**Files:**
- Create: `orders/services.py`
- Test: `orders/tests.py`

**Function contract:**

```python
def create_order_from_cart(*, table, cart_items, customer_name='', customer_note=''):
    """Create Order and OrderItem rows from cart_items.

    cart_items format:
    [
        {'menu_item': MenuItem, 'quantity': 2, 'note': 'tanpa pedas'},
    ]
    """
```

**Rules:**

- Reject empty cart.
- Reject unavailable menu.
- Reject menu from different restaurant.
- Calculate subtotal and total.
- Generate unique order number.

**Acceptance Criteria:**

- Order dibuat dengan total benar.
- OrderItem menyimpan snapshot name/price.
- Test mencakup empty cart dan unavailable item.

---

### Task 3.2: Buat payment gateway interface

**Objective:** Menyiapkan abstraction agar payment provider bisa diganti tanpa mengubah flow utama.

**Files:**
- Create: `payments/gateways/base.py`
- Create: `payments/gateways/dummy.py`
- Test: `payments/tests.py`

**Interface minimal:**

```python
class PaymentGateway:
    def create_payment(self, payment):
        raise NotImplementedError

    def verify_callback(self, payload):
        raise NotImplementedError
```

**Dummy gateway behavior:**

- Untuk QRIS, isi `qr_string` dummy.
- Untuk VA/e-wallet, isi `payment_url` dummy.
- Return reference dummy.

**Acceptance Criteria:**

- Payment gateway dummy bisa dipakai di development.
- Tidak ada dependency payment provider real di MVP awal.

---

### Task 3.3: Buat payment service `initiate_payment`

**Objective:** Membuat payment untuk order dan menghubungkannya ke gateway.

**Files:**
- Create: `payments/services.py`
- Test: `payments/tests.py`

**Function contract:**

```python
def initiate_payment(*, order, method):
    """Create Payment for order and initialize payment gateway request."""
```

**Rules:**

- Order yang sudah punya payment tidak boleh dibuatkan payment kedua.
- Amount harus sama dengan `order.total_amount`.
- Default provider pakai dummy gateway dulu.

---

## Phase 4 — Customer Flow

### Task 4.1: Buat URL customer menu dari QR token

**Objective:** Customer bisa membuka menu berdasarkan QR meja.

**Files:**
- Create: `menus/urls.py`
- Create: `menus/views.py`
- Modify: `core/urls.py`
- Create: `menus/templates/menus/customer_menu.html`
- Test: `menus/tests.py`

**Route:**

```python
path('m/<slug:qr_token>/', views.customer_menu, name='customer_menu')
```

**Acceptance Criteria:**

- QR token valid menampilkan menu aktif.
- QR token invalid return 404.
- Menu unavailable tidak tampil.

---

### Task 4.2: Buat template customer menu mobile-first

**Objective:** Menampilkan daftar kategori dan menu yang nyaman dipakai dari HP.

**Files:**
- Create/Modify: `menus/templates/menus/customer_menu.html`
- Modify: `core/static/core/css/main.css`

**UI Content:**

- Nama resto.
- Nomor meja.
- Kategori menu.
- Card menu: nama, deskripsi, harga, tombol tambah.
- Cart floating button.

**Acceptance Criteria:**

- Halaman bisa dibuka di mobile.
- Semua item aktif tampil sesuai kategori.

---

### Task 4.3: Buat cart berbasis session

**Objective:** Customer bisa menambahkan item ke keranjang tanpa login.

**Files:**
- Create: `orders/cart.py`
- Modify: `orders/views.py`
- Create: `orders/urls.py`
- Modify: `core/urls.py`
- Test: `orders/tests.py`

**Routes:**

```python
path('cart/add/<int:item_id>/', views.cart_add, name='cart_add')
path('cart/', views.cart_detail, name='cart_detail')
path('cart/update/<int:item_id>/', views.cart_update, name='cart_update')
path('cart/remove/<int:item_id>/', views.cart_remove, name='cart_remove')
```

**Rules:**

- Cart disimpan di `request.session`.
- Cart item menyimpan `item_id`, `quantity`, `note`.
- Quantity minimal 1.

---

### Task 4.4: Buat halaman cart dan checkout

**Objective:** Customer bisa review pesanan dan checkout.

**Files:**
- Create: `orders/templates/orders/cart_detail.html`
- Create: `orders/templates/orders/checkout.html`
- Modify: `orders/views.py`
- Test: `orders/tests.py`

**Routes:**

```python
path('checkout/', views.checkout, name='checkout')
```

**Acceptance Criteria:**

- Cart detail menampilkan item, quantity, subtotal, total.
- Checkout membuat order dari cart.
- Setelah checkout, cart dikosongkan.

---

### Task 4.5: Buat halaman pilih pembayaran

**Objective:** Customer bisa memilih QRIS, Virtual Account, atau e-wallet.

**Files:**
- Create: `payments/urls.py`
- Create: `payments/views.py`
- Create: `payments/templates/payments/select_method.html`
- Create: `payments/templates/payments/payment_detail.html`
- Modify: `core/urls.py`
- Test: `payments/tests.py`

**Routes:**

```python
path('orders/<str:order_number>/pay/', views.select_payment_method, name='select_payment_method')
path('payments/<int:payment_id>/', views.payment_detail, name='payment_detail')
```

**Acceptance Criteria:**

- Customer bisa pilih metode pembayaran.
- Payment record dibuat.
- Payment detail menampilkan QR string atau payment URL dummy.

---

### Task 4.6: Buat halaman status order

**Objective:** Customer bisa melihat status order dan pembayaran.

**Files:**
- Modify: `orders/views.py`
- Create: `orders/templates/orders/order_status.html`
- Test: `orders/tests.py`

**Route:**

```python
path('orders/<str:order_number>/status/', views.order_status, name='order_status')
```

**Acceptance Criteria:**

- Menampilkan status order.
- Menampilkan status payment.
- Bisa diakses tanpa login, tapi hanya dengan order number.

---

## Phase 5 — Admin / Staff Dashboard

### Task 5.1: Buat dashboard layout

**Objective:** Membuat layout admin yang konsisten.

**Files:**
- Create: `core/templates/layouts/dashboard.html`
- Create: `core/templates/partials/dashboard_sidebar.html`
- Modify: `core/static/core/css/main.css`

**Layout sections:**

- Sidebar
- Header
- Content block
- Flash messages

---

### Task 5.2: Buat dashboard home

**Objective:** Menampilkan ringkasan bisnis resto.

**Files:**
- Create: `dashboard/urls.py`
- Create: `dashboard/views.py`
- Create: `dashboard/templates/dashboard/index.html`
- Modify: `core/urls.py`
- Test: `dashboard/tests.py`

**Cards:**

- Total menu aktif.
- Order hari ini.
- Payment pending.
- Revenue hari ini.

**Acceptance Criteria:**

- Harus login.
- Query tidak error saat data kosong.

---

### Task 5.3: Buat CRUD Restaurant

**Objective:** Owner/admin bisa mengatur profil resto.

**Files:**
- Create: `restaurants/forms.py`
- Create: `restaurants/views.py`
- Create: `restaurants/urls.py`
- Create: `restaurants/templates/restaurants/form.html`
- Create: `restaurants/templates/restaurants/detail.html`
- Modify: `core/urls.py`
- Test: `restaurants/tests.py`

**Acceptance Criteria:**

- Admin bisa edit nama, deskripsi, alamat, phone.
- Halaman butuh login.

---

### Task 5.4: Buat CRUD DiningTable dan QR token

**Objective:** Owner/admin bisa membuat meja dan melihat URL QR.

**Files:**
- Modify: `restaurants/forms.py`
- Modify: `restaurants/views.py`
- Create: `restaurants/templates/restaurants/table_list.html`
- Create: `restaurants/templates/restaurants/table_form.html`
- Test: `restaurants/tests.py`

**Acceptance Criteria:**

- Admin bisa tambah/edit/hapus meja.
- QR token auto-generate jika kosong.
- Tampil URL menu: `/m/<qr_token>/`.

---

### Task 5.5: Buat CRUD Category

**Objective:** Owner/admin bisa mengatur kategori menu.

**Files:**
- Create: `menus/forms.py`
- Modify: `menus/views.py`
- Create: `menus/templates/menus/category_list.html`
- Create: `menus/templates/menus/category_form.html`
- Test: `menus/tests.py`

**Acceptance Criteria:**

- Bisa tambah/edit/nonaktifkan kategori.
- Sort order bekerja.

---

### Task 5.6: Buat CRUD MenuItem

**Objective:** Owner/admin bisa mengatur makanan/minuman.

**Files:**
- Modify: `menus/forms.py`
- Modify: `menus/views.py`
- Create: `menus/templates/menus/item_list.html`
- Create: `menus/templates/menus/item_form.html`
- Test: `menus/tests.py`

**Acceptance Criteria:**

- Bisa tambah/edit/nonaktifkan menu.
- Bisa set tersedia/tidak tersedia.
- Harga wajib integer positif.

---

### Task 5.7: Buat list dan detail order staff

**Objective:** Staff bisa melihat order masuk.

**Files:**
- Modify: `orders/views.py`
- Create: `orders/templates/orders/admin_order_list.html`
- Create: `orders/templates/orders/admin_order_detail.html`
- Test: `orders/tests.py`

**Acceptance Criteria:**

- Halaman butuh login.
- Bisa filter status.
- Detail menampilkan item pesanan dan pembayaran.

---

### Task 5.8: Buat update status order

**Objective:** Staff bisa mengubah status order.

**Files:**
- Modify: `orders/views.py`
- Modify: `orders/templates/orders/admin_order_detail.html`
- Test: `orders/tests.py`

**Allowed transition MVP:**

- `new` → `processing`
- `paid` → `processing`
- `processing` → `ready`
- `ready` → `completed`
- `new` → `cancelled`
- `processing` → `cancelled`

**Acceptance Criteria:**

- Status invalid tidak diterima.
- Update status tercatat.

---

## Phase 6 — Authentication dan Authorization

### Task 6.1: Pakai Django auth login/logout

**Objective:** Admin/staff bisa login dan logout.

**Files:**
- Modify: `core/urls.py`
- Create: `accounts/templates/registration/login.html`
- Create: `accounts/templates/registration/logged_out.html`
- Modify: `core/settings.py`

**Settings:**

```python
LOGIN_URL = 'login'
LOGIN_REDIRECT_URL = 'dashboard:index'
LOGOUT_REDIRECT_URL = 'login'
```

**Acceptance Criteria:**

- Login page tampil.
- Logout bekerja.
- Dashboard redirect ke login jika belum login.

---

### Task 6.2: Buat role staff sederhana

**Objective:** Menyiapkan role owner/admin/kasir/dapur.

**Files:**
- Modify: `accounts/models.py`
- Modify: `accounts/admin.py`
- Test: `accounts/tests.py`

**MVP approach:**

Gunakan `UserProfile` OneToOne ke Django User.

**Fields:**

```python
user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
restaurant = models.ForeignKey('restaurants.Restaurant', on_delete=models.CASCADE, null=True, blank=True)
role = models.CharField(max_length=20, choices=Role.choices, default=Role.STAFF)
```

**Acceptance Criteria:**

- User punya role.
- User bisa dikaitkan ke restaurant.

---

## Phase 7 — Payment Callback dan Status

### Task 7.1: Buat dummy payment success endpoint

**Objective:** Untuk development, payment bisa diubah menjadi paid tanpa gateway real.

**Files:**
- Modify: `payments/views.py`
- Modify: `payments/urls.py`
- Test: `payments/tests.py`

**Route:**

```python
path('payments/<int:payment_id>/dummy-success/', views.dummy_payment_success, name='dummy_payment_success')
```

**Rules:**

- Hanya aktif saat `DEBUG=True`.
- Mengubah payment status ke `paid`.
- Mengubah order payment_status ke `paid`.
- Bisa mengubah order status ke `paid`.

---

### Task 7.2: Buat webhook endpoint placeholder

**Objective:** Menyiapkan endpoint callback payment provider untuk future integration.

**Files:**
- Modify: `payments/views.py`
- Modify: `payments/urls.py`
- Test: `payments/tests.py`

**Route:**

```python
path('payments/webhook/<str:provider>/', views.payment_webhook, name='payment_webhook')
```

**Acceptance Criteria:**

- Endpoint menerima POST.
- Untuk MVP, log payload dan return 200.
- Tidak memproses data sebelum provider real dipilih.

---

## Phase 8 — UI Conversion dari Folder Design

### Task 8.1: Convert landing page final dari desain

**Objective:** Memindahkan desain landing dari `design/landing-page.html` ke Django template final, menggantikan placeholder landing dari Task 0.2.

**Files:**
- Source: `design/landing-page.html`
- Modify: `core/templates/core/landing.html`
- Modify: `core/urls.py`
- Modify: `core/static/core/css/main.css`
- Modify: `core/static/core/js/main.js`

**Rules:**

- Jangan edit file `design/landing-page.html`.
- Replace link login/register/dashboard ke URL Django.
- Root `/` tetap mengarah ke landing page.
- Pindahkan CSS/JS inline ke static jika shared.
- Landing page harus responsive dan tidak merusak flow QR/customer/dashboard.

---

### Task 8.2: Convert login/register design

**Objective:** Menyesuaikan desain login/register ke Django auth.

**Files:**
- Source: `design/login.html`
- Source: `design/register.html`
- Modify: `accounts/templates/registration/login.html`
- Create: `accounts/templates/registration/register.html`

**Acceptance Criteria:**

- Login submit ke Django auth.
- Register bisa placeholder dulu jika belum implement self-registration.

---

### Task 8.3: Convert customer menu design

**Objective:** Menyesuaikan desain menu customer dari `design/menu.html` atau `design/book-menu.html`.

**Files:**
- Source: `design/menu.html`
- Source: `design/book-menu.html`
- Modify: `menus/templates/menus/customer_menu.html`

**Acceptance Criteria:**

- Data menu dinamis dari database.
- Add to cart berfungsi.

---

### Task 8.4: Convert dashboard design

**Objective:** Menyesuaikan dashboard/admin dari file desain lama.

**Files:**
- Source: `design/index.html`
- Source: `design/management-menu.html`
- Source: `design/laporan.html`
- Source: `design/store.html`
- Source: `design/employee.html`
- Modify: `core/templates/layouts/dashboard.html`
- Modify: `dashboard/templates/dashboard/index.html`
- Modify: templates admin app terkait.

**Acceptance Criteria:**

- Dashboard pakai layout shared.
- Sidebar link pakai `{% url %}`.
- Tidak ada link utama yang masih `href="#"` kecuali memang anchor section.

---

## Phase 9 — Reports dan Polish MVP

### Task 9.1: Buat laporan transaksi sederhana

**Objective:** Owner bisa melihat transaksi dan revenue dasar.

**Files:**
- Create: `dashboard/templates/dashboard/reports.html`
- Modify: `dashboard/views.py`
- Modify: `dashboard/urls.py`
- Test: `dashboard/tests.py`

**Metrics MVP:**

- Revenue hari ini.
- Total order hari ini.
- Menu terlaris sederhana.
- Payment pending.

---

### Task 9.2: Tambahkan empty state dan error message

**Objective:** UI tetap rapi saat data kosong/error.

**Files:**
- Modify: semua template list/detail utama.

**Acceptance Criteria:**

- Menu kosong menampilkan pesan.
- Cart kosong menampilkan CTA balik ke menu.
- Order kosong menampilkan empty state.
- Payment failed/expired tampil jelas.

---

### Task 9.3: Tambahkan seed data development

**Objective:** Memudahkan testing manual tanpa input data satu per satu.

**Files:**
- Create: `restaurants/management/commands/seed_demo.py`

**Command:**

```bash
.venv/bin/python manage.py seed_demo
```

**Seed data:**

- 1 resto demo.
- 5 meja.
- 4 kategori.
- 12 menu item.
- 1 user admin demo.

---

## Phase 10 — Final Verification

### Task 10.1: Full test suite

**Objective:** Memastikan semua test lulus.

**Command:**

```bash
.venv/bin/python manage.py test
```

Expected:

```text
OK
```

---

### Task 10.2: Manual smoke test customer flow

**Objective:** Memastikan flow pelanggan berjalan end-to-end.

**Steps:**

1. Jalankan server:

```bash
.venv/bin/python manage.py runserver 127.0.0.1:8000
```

2. Buka URL QR meja demo:

```text
http://127.0.0.1:8000/m/<qr_token>/
```

3. Tambah menu ke cart.
4. Checkout.
5. Pilih QRIS.
6. Buka payment detail.
7. Klik dummy success.
8. Buka order status.

**Expected:**

- Order dibuat.
- Payment berubah `paid`.
- Order status/payment status terlihat benar.

---

### Task 10.3: Manual smoke test admin flow

**Objective:** Memastikan admin/staff dapat mengelola operasional.

**Steps:**

1. Login admin.
2. Buka dashboard.
3. Tambah kategori.
4. Tambah menu.
5. Buka daftar order.
6. Update status order sampai `completed`.

**Expected:**

- Semua halaman admin terbuka.
- CRUD menu berhasil.
- Status order berhasil berubah.

---

## Target Folder Structure Setelah MVP

```text
tapmenu/
├── accounts/
│   ├── migrations/
│   │   └── __init__.py
│   ├── templates/
│   │   └── registration/
│   │       ├── logged_out.html
│   │       ├── login.html
│   │       └── register.html
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── models.py
│   ├── tests.py
│   └── views.py
├── core/
│   ├── static/
│   │   └── core/
│   │       ├── css/
│   │       │   └── main.css
│   │       ├── img/
│   │       │   └── .gitkeep
│   │       └── js/
│   │           └── main.js
│   ├── templates/
│   │   ├── core/
│   │   │   ├── index.html
│   │   │   └── landing.html
│   │   ├── layouts/
│   │   │   ├── base.html
│   │   │   └── dashboard.html
│   │   └── partials/
│   │       ├── dashboard_sidebar.html
│   │       └── .gitkeep
│   ├── __init__.py
│   ├── asgi.py
│   ├── settings.py
│   ├── urls.py
│   ├── views.py
│   └── wsgi.py
├── dashboard/
│   ├── migrations/
│   │   └── __init__.py
│   ├── templates/
│   │   └── dashboard/
│   │       ├── index.html
│   │       └── reports.html
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── tests.py
│   ├── urls.py
│   └── views.py
├── design/
│   ├── book-menu.html
│   ├── book-menu.jsx
│   ├── employee.html
│   ├── index.html
│   ├── landing-page.html
│   ├── laporan.html
│   ├── login.html
│   ├── management-menu.html
│   ├── menu.html
│   ├── register.html
│   └── store.html
├── docs/
│   ├── PRD.md
│   └── TASKS.md
├── menus/
│   ├── migrations/
│   │   └── __init__.py
│   ├── templates/
│   │   └── menus/
│   │       ├── category_form.html
│   │       ├── category_list.html
│   │       ├── customer_menu.html
│   │       ├── item_form.html
│   │       └── item_list.html
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── forms.py
│   ├── models.py
│   ├── tests.py
│   ├── urls.py
│   └── views.py
├── orders/
│   ├── migrations/
│   │   └── __init__.py
│   ├── templates/
│   │   └── orders/
│   │       ├── admin_order_detail.html
│   │       ├── admin_order_list.html
│   │       ├── cart_detail.html
│   │       ├── checkout.html
│   │       └── order_status.html
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── cart.py
│   ├── models.py
│   ├── services.py
│   ├── tests.py
│   ├── urls.py
│   └── views.py
├── payments/
│   ├── gateways/
│   │   ├── __init__.py
│   │   ├── base.py
│   │   └── dummy.py
│   ├── migrations/
│   │   └── __init__.py
│   ├── templates/
│   │   └── payments/
│   │       ├── payment_detail.html
│   │       └── select_method.html
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── models.py
│   ├── services.py
│   ├── tests.py
│   ├── urls.py
│   └── views.py
├── restaurants/
│   ├── management/
│   │   └── commands/
│   │       └── seed_demo.py
│   ├── migrations/
│   │   └── __init__.py
│   ├── templates/
│   │   └── restaurants/
│   │       ├── detail.html
│   │       ├── form.html
│   │       ├── table_form.html
│   │       └── table_list.html
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── forms.py
│   ├── models.py
│   ├── tests.py
│   ├── urls.py
│   └── views.py
└── manage.py
```
