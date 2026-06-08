# PRD TapMenu

## 1. Ringkasan Produk

TapMenu adalah aplikasi pemesanan digital untuk restoran, kafe, dan bisnis F&B. Aplikasi ini memungkinkan pelanggan memesan makanan atau minuman langsung dari meja mereka melalui QR menu, lalu melakukan pembayaran digital tanpa harus antre di kasir.

Selain flow QR menu, TapMenu juga memiliki landing page website di root `/` sebagai pintu masuk utama untuk calon owner/admin. Landing page menjelaskan manfaat produk, cara kerja, fitur utama, dan menyediakan CTA menuju login/register/dashboard.

Tujuan utama TapMenu adalah mempercepat proses pemesanan, mengurangi antrean pembayaran, membantu operasional resto/kafe menjadi lebih efisien, dan memberikan pengalaman pelanggan yang lebih modern.

## 2. Latar Belakang Masalah

Banyak restoran dan kafe masih menggunakan alur manual:

- Pelanggan menunggu pelayan untuk melihat menu atau mencatat pesanan.
- Pelayan harus bolak-balik dari meja ke kasir/dapur.
- Pelanggan harus antre untuk membayar di kasir.
- Pesanan rentan salah catat.
- Owner sulit memantau transaksi, menu terlaris, dan performa penjualan secara real-time.

TapMenu dibuat untuk menyelesaikan masalah tersebut dengan alur digital dari meja pelanggan sampai pembayaran.

## 3. Visi Produk

Menjadi platform menu, pemesanan, dan pembayaran digital yang mudah digunakan oleh restoran, kafe, dan UMKM kuliner di Indonesia.

## 4. Target Pengguna

### 4.1 Pelanggan Resto/Kafe

Pelanggan yang datang ke restoran atau kafe dan ingin:

- Melihat menu dari HP.
- Memesan langsung dari meja.
- Membayar tanpa antre.
- Menggunakan metode pembayaran digital seperti QRIS, Virtual Account, dan e-wallet.

### 4.2 Owner / Admin Resto

Pemilik atau pengelola restoran/kafe yang ingin:

- Mengelola daftar menu.
- Melihat pesanan masuk.
- Mengelola status pesanan.
- Melihat laporan transaksi.
- Mengatur metode pembayaran.

### 4.3 Staff / Kasir / Dapur

Tim operasional yang bertugas:

- Menerima pesanan.
- Mengubah status pesanan.
- Melihat pembayaran masuk.
- Menyiapkan pesanan pelanggan.

### 4.4 Visitor / Calon Owner

Pengunjung website yang belum login dan ingin memahami produk TapMenu sebelum menggunakan sistem. Mereka membutuhkan:

- Landing page yang menjelaskan value proposition TapMenu.
- CTA jelas untuk login/register.
- Ringkasan cara kerja: setup resto, generate QR meja, pelanggan scan, order masuk dashboard.
- Tampilan profesional agar produk terlihat siap dipakai UMKM/resto/kafe.

## 5. Tujuan Produk

- Mempermudah pelanggan untuk memesan dari meja masing-masing.
- Mengurangi antrean pembayaran di kasir.
- Mempercepat proses order dari pelanggan ke dapur/kasir.
- Mengurangi kesalahan pencatatan pesanan.
- Memberikan dashboard sederhana untuk resto/kafe.
- Mendukung pembayaran digital: QRIS, Virtual Account, dan e-wallet.
- Menyediakan landing page publik sebagai halaman awal website dan pintu masuk ke login/register.

## 6. Ruang Lingkup MVP

MVP TapMenu fokus pada fitur dasar agar alur utama bisa berjalan dari pelanggan scan QR sampai pembayaran.

### 6.1 Fitur Pelanggan

- Scan QR meja.
- Melihat daftar menu.
- Melihat detail menu.
- Menambahkan menu ke keranjang.
- Mengatur jumlah item.
- Mengisi catatan pesanan, misalnya “tidak pedas” atau “tanpa es”.
- Checkout pesanan.
- Memilih metode pembayaran.
- Melihat status pembayaran dan status pesanan.

### 6.2 Fitur Admin / Owner

- Login admin.
- Dashboard ringkasan.
- CRUD menu.
- CRUD kategori menu.
- Melihat daftar pesanan masuk.
- Mengubah status pesanan.
- Melihat detail transaksi.
- Mengatur data resto/kafe.
- Mengatur meja dan QR code.

### 6.3 Fitur Staff / Dapur

- Melihat pesanan baru.
- Melihat detail pesanan.
- Mengubah status pesanan:
  - Pesanan baru
  - Diproses
  - Siap disajikan
  - Selesai
  - Dibatalkan

### 6.4 Fitur Pembayaran

Metode pembayaran yang ditargetkan:

- QRIS
- Virtual Account
- E-wallet

Untuk MVP, integrasi pembayaran dapat dibuat sebagai payment gateway abstraction agar nanti mudah disambungkan ke provider seperti Midtrans, Xendit, Duitku, atau payment gateway lain.

### 6.5 Fitur Landing Page / Website Publik

Landing page adalah halaman awal website TapMenu dan harus tersedia sejak awal MVP.

Fitur landing page:

- Route root `/` membuka landing page, bukan dashboard.
- Navbar dengan link ke section landing page dan CTA login/register.
- Hero section yang menjelaskan TapMenu secara singkat.
- Section benefit untuk resto/kafe/UMKM.
- Section cara kerja TapMenu.
- Section fitur utama: QR menu, order meja, dashboard, pembayaran digital, laporan.
- CTA menuju login dan register menggunakan URL Django, bukan `href="#"`.
- Footer sederhana.
- Responsive untuk mobile dan desktop.

## 7. Alur Utama Produk

### 7.1 Alur Pelanggan Memesan

1. Pelanggan duduk di meja.
2. Pelanggan scan QR code meja.
3. Sistem membuka halaman menu sesuai resto dan nomor meja.
4. Pelanggan memilih menu.
5. Pelanggan menambahkan item ke keranjang.
6. Pelanggan checkout.
7. Sistem membuat order.
8. Pelanggan memilih metode pembayaran.
9. Pelanggan melakukan pembayaran.
10. Sistem mengubah status pembayaran.
11. Staff menerima pesanan.
12. Pesanan diproses dan disajikan.

### 7.2 Alur Admin Mengelola Menu

1. Admin login.
2. Admin masuk dashboard.
3. Admin membuka halaman manajemen menu.
4. Admin menambah, mengubah, atau menghapus menu.
5. Menu langsung tampil di QR menu pelanggan.

### 7.3 Alur Staff Mengelola Pesanan

1. Staff membuka dashboard pesanan.
2. Staff melihat order baru.
3. Staff mengubah status menjadi “Diproses”.
4. Setelah selesai, staff mengubah status menjadi “Siap disajikan”.
5. Setelah pesanan diterima pelanggan, status menjadi “Selesai”.

### 7.4 Alur Visitor dari Landing Page

1. Visitor membuka website TapMenu di `/`.
2. Sistem menampilkan landing page.
3. Visitor membaca benefit, fitur, dan cara kerja.
4. Visitor klik CTA login atau register.
5. Sistem membuka halaman login/register sesuai URL Django.
6. Setelah login, admin/staff diarahkan ke dashboard.

## 8. Entitas Data Utama

### 8.1 Restaurant

Mewakili data resto atau kafe.

Field awal:

- Nama resto
- Deskripsi
- Alamat
- Nomor telepon
- Logo
- Status aktif

### 8.2 Table / Meja

Mewakili meja pelanggan.

Field awal:

- Restaurant
- Nomor meja
- QR code token
- Status aktif

### 8.3 Category

Kategori menu.

Field awal:

- Restaurant
- Nama kategori
- Urutan tampil
- Status aktif

### 8.4 Menu Item

Data makanan/minuman.

Field awal:

- Restaurant
- Category
- Nama menu
- Deskripsi
- Harga
- Gambar
- Status tersedia
- Status aktif

### 8.5 Order

Data pesanan pelanggan.

Field awal:

- Restaurant
- Table
- Nomor order
- Status order
- Status pembayaran
- Total harga
- Catatan pelanggan
- Waktu dibuat

### 8.6 Order Item

Detail item dalam pesanan.

Field awal:

- Order
- Menu item
- Nama item saat transaksi
- Harga item saat transaksi
- Quantity
- Catatan item
- Subtotal

### 8.7 Payment

Data pembayaran.

Field awal:

- Order
- Metode pembayaran
- Provider pembayaran
- Nominal
- Status pembayaran
- Payment reference
- Payment URL / QR string jika ada
- Waktu pembayaran

### 8.8 User / Staff

Pengguna internal resto.

Role awal:

- Owner
- Admin
- Kasir
- Dapur

## 9. Status Order

Status pesanan awal:

- `new` — pesanan baru dibuat
- `paid` — pembayaran berhasil
- `processing` — pesanan sedang diproses
- `ready` — pesanan siap disajikan
- `completed` — pesanan selesai
- `cancelled` — pesanan dibatalkan

## 10. Status Pembayaran

Status pembayaran awal:

- `pending` — menunggu pembayaran
- `paid` — pembayaran berhasil
- `failed` — pembayaran gagal
- `expired` — pembayaran kedaluwarsa
- `refunded` — pembayaran dikembalikan

## 11. Kebutuhan Halaman MVP

### 11.1 Halaman Publik / Customer

- Landing page website (`/`)
  - Hero
  - Benefit
  - Cara kerja
  - Fitur utama
  - CTA login/register
  - Footer
- Halaman QR menu
- Detail menu
- Keranjang
- Checkout
- Halaman pembayaran
- Halaman status order

### 11.2 Halaman Admin

- Login
- Dashboard
- Manajemen menu
- Manajemen kategori
- Manajemen meja dan QR
- Daftar pesanan
- Detail pesanan
- Riwayat transaksi
- Pengaturan resto

## 12. Kriteria Sukses MVP

MVP dianggap berhasil jika:

- Pelanggan bisa membuka menu dari QR meja.
- Pelanggan bisa membuat pesanan dari meja.
- Admin/staff bisa melihat pesanan masuk.
- Admin/staff bisa mengubah status pesanan.
- Pelanggan bisa memilih metode pembayaran digital.
- Sistem bisa menyimpan status pembayaran.
- Owner bisa mengelola menu dan meja.
- Visitor bisa membuka landing page di `/` dan tombol login/register mengarah ke URL yang benar.

## 13. Non-Goals untuk MVP

Fitur berikut belum menjadi fokus awal:

- Aplikasi mobile native.
- Loyalty point.
- Membership pelanggan.
- Multi-cabang kompleks.
- Integrasi akuntansi.
- Inventory bahan baku detail.
- Split bill.
- Reservasi meja.

## 14. Risiko dan Catatan

- Integrasi payment gateway perlu dipilih sejak awal agar struktur pembayaran tidak berubah besar.
- QR meja harus memiliki token unik agar meja tidak mudah dimanipulasi.
- Harga item di order harus disimpan sebagai snapshot agar histori transaksi tidak berubah ketika harga menu diupdate.
- Dashboard staff harus ringan dan cepat karena akan dipakai saat jam ramai.
- Sistem harus tetap bisa menangani pembayaran pending atau expired.

## 15. Prioritas Implementasi Awal

Urutan implementasi yang disarankan:

1. Setup project Django dan struktur template/static.
2. Buat landing page publik di `/` sebagai halaman awal website.
3. Buat app utama untuk restoran/menu/order/payment.
4. Buat model Restaurant, Table, Category, MenuItem.
5. Buat model Order, OrderItem, Payment.
6. Buat halaman customer menu dari QR meja.
7. Buat cart dan checkout sederhana.
8. Buat dashboard admin untuk melihat order.
9. Buat CRUD menu dan kategori.
10. Buat status order.
11. Buat abstraction payment gateway.
12. Integrasi payment gateway pertama.

## 16. Catatan Desain Produk

TapMenu harus terasa:

- Cepat
- Simpel
- Mobile-first
- Mudah digunakan pelanggan tanpa login
- Mudah dikelola owner resto/kafe
- Cocok untuk UMKM Indonesia

Desain awal perlu punya dua pintu masuk yang jelas:

- Visitor/calon owner masuk dari landing page website di `/`.
- Pelanggan resto masuk dari QR meja ke halaman menu customer.

Landing page menggunakan source desain `design/landing-page.html` dan harus dikonversi ke template Django tanpa mengubah file source desain. Pengalaman scan QR tetap menjadi fokus utama customer flow, tetapi landing page menjadi pintu utama website untuk owner/admin.
