# TapMenu 🍽️

TapMenu adalah aplikasi pemesanan dan pembayaran digital modern berbasis web untuk restoran, kafe, dan bisnis F&B (Food & Beverage). Aplikasi ini dirancang untuk mempercepat proses pemesanan dengan memungkinkan pelanggan memesan langsung dari meja mereka melalui scan QR code, serta melakukan pembayaran digital secara instan dan mandiri.

---

## 📂 Dokumentasi Utama (Defend ke `/docs`)

Seluruh rancangan produk, daftar tugas implementasi, dan spesifikasi teknis dikelola secara terpusat di dalam folder [docs/](file:///home/fahril/playground/project/tapmenu/docs). Sesuai dengan standar pengembangan kami, pastikan untuk selalu merujuk dan memperbarui dokumentasi berikut:

*   **[Product Requirement Document (PRD)](file:///home/fahril/playground/project/tapmenu/docs/PRD.md)**: Dokumen spesifikasi kebutuhan produk, alur pengguna (user flow), visi produk, entitas data utama, status pesanan/pembayaran, serta ruang lingkup MVP.
*   **[Implementation Tasks (TASKS.md)](file:///home/fahril/playground/project/tapmenu/docs/TASKS.md)**: Panduan langkah-demi-langkah implementasi (Phases 0-11) yang digunakan sebagai acuan pengembangan bertahap (*subagent-driven development*).

---

## ✨ Fitur Utama

### 1. Sisi Pelanggan (Tanpa Login)
*   **Scan QR Meja**: Mengarahkan pelanggan langsung ke menu resto sesuai nomor meja secara instan.
*   **Menu Digital**: Jelajahi menu makanan & minuman beserta kategori dan detailnya secara interaktif.
*   **Keranjang Belanja**: Kelola item pesanan dan tambahkan catatan khusus (misal: "tidak pedas").
*   **Checkout & Pembayaran**: Pilih metode pembayaran digital (QRIS, Virtual Account, E-wallet) dengan integrasi payment gateway.
*   **Real-time Order Status**: Pantau status pesanan (baru, diproses, disajikan, selesai) dari peramban.

### 2. Sisi Landing Page Publik
*   **Landing Page (`/`)**: Pintu masuk utama bagi calon pemilik/owner restoran untuk memahami keunggulan, cara kerja, dan fitur utama TapMenu, lengkap dengan CTA login/register.

### 3. Sisi Merchant / Restoran (Wajib Login)
*   **Dashboard Utama**: Ringkasan performa penjualan harian, pesanan aktif, dan statistik penting lainnya.
*   **Manajemen Menu & Kategori**: CRUD menu dan kategori secara real-time yang langsung terupdate pada menu pelanggan.
*   **Manajemen Meja & QR**: Generate QR Code meja unik dengan token pengaman.
*   **Dashboard Pesanan (Dapur/Staff)**: Panel operasional untuk mengubah status pesanan secara bertahap.
*   **Laporan Transaksi**: Histori pembayaran dan pesanan masuk secara detail.

---

## 🛠️ Tech Stack & Alat Pengembangan

*   **Runtime & Framework**: Python 3.13 & Django 4.2+ (Django Monolith)
*   **Database**: SQLite (untuk lingkungan pengembangan lokal)
*   **Styling & UI**: Vanilla CSS & JavaScript (Modern, Premium, and Responsive layouts)
*   **Linter & Formatter**:
    *   **[Ruff](https://github.com/astral-sh/ruff)**: Linter & formatter Python super cepat.
    *   **[djLint](https://github.com/djlint/djLint)**: Linter & formatter HTML Django template.

---

## 📁 Struktur Project

Project ini terbagi ke dalam beberapa aplikasi modular Django:

```text
tapmenu/
├── core/               # Konfigurasi project Django, global URL, base templates, dan static files
├── accounts/           # Registrasi, login, manajemen user (Owner, Admin, Kasir, Dapur)
├── restaurants/        # Profil restoran, meja, dan generator QR code token
├── menus/              # Kategori menu dan menu item (makanan/minuman)
├── orders/             # Pembuatan order, keranjang belanja (cart), dan status tracking
├── payments/           # Abstraksi gateway pembayaran (QRIS, VA, E-wallet)
├── dashboard/          # Panel kontrol admin, kasir, dan dapur
├── design/             # Aset desain awal landing page dan layout
├── docs/               # Berkas dokumentasi utama (PRD.md, TASKS.md)
└── manage.py           # Django CLI tool
```

---

## 🚀 Cara Memulai (Setup Lokal)

Ikuti langkah-langkah di bawah ini untuk menjalankan aplikasi TapMenu secara lokal:

### 1. Clone Repositori dan Masuk ke Direktori Project
```bash
git clone <url-repository>
cd tapmenu
```

### 2. Persiapkan Virtual Environment & Instal Dependensi
Gunakan virtual environment bawaan project:
```bash
# Aktifkan virtual environment
source .venv/bin/activate  # Untuk Linux/macOS
# atau
.venv\Scripts\activate     # Untuk Windows

# Instal dependensi tambahan untuk development
pip install -r requirements-dev.txt
```

### 3. Verifikasi Integrasi Project
Jalankan pengecekan Django untuk memastikan konfigurasi berjalan dengan baik:
```bash
python manage.py check
```

Pastikan file static global dapat ditemukan dengan benar:
```bash
python manage.py findstatic core/css/main.css core/js/main.js
```

### 4. Jalankan Migrasi Database
```bash
python manage.py migrate
```

### 5. Buat Superuser (Untuk Akses Dashboard Admin)
```bash
python manage.py createsuperuser
```

### 6. Jalankan Local Development Server
```bash
python manage.py runserver
```
Aplikasi dapat diakses melalui browser di alamat **[http://127.0.0.1:8000/](http://127.0.0.1:8000/)**.

---

## 🛡️ Aturan Kode & Kepatuhan Linter
Kami menggunakan **Ruff** dan **djLint** untuk menjaga kerapian kode. Sebelum melakukan commit, Anda disarankan untuk menjalankan linter berikut:

```bash
# Menjalankan Ruff untuk linter Python
ruff check .

# Memformat kode Python secara otomatis dengan Ruff
ruff format .

# Memformat Django HTML Templates dengan djLint
djlint . --reformat
```

Semua konfigurasi linter dapat dilihat pada berkas `pyproject.toml`.
