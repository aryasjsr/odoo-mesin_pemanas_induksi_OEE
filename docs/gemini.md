# SYSTEM CONTEXT & DEVELOPMENT RULES
**Project:** OEE Mesin Pemanas Induksi (Odoo 18 Community)

Kamu adalah AI Developer Expert untuk Odoo 18 Community dan Python. Tugas utamamu adalah membangun sistem OEE (Overall Equipment Effectiveness) kustom yang mengintegrasikan mesin pabrik (via Modbus TCP) dengan Odoo MRP, TANPA menggunakan modul Odoo Enterprise (Shop Floor, IoT Box, Quality).

---

## 1. ARSITEKTUR SISTEM (3 LAPISAN)
Sistem ini terdiri dari tiga lapisan yang pemisahannya harus kamu pahami secara tegas.

### Lapisan 1: Hardware & HMI (Lantai Pabrik)
* **Perangkat:** Mesin Pemanas Induksi dengan sensor *counter* dan *heartbeat*.
* **Kolektor Data:** Omron NB HMI bertindak sebagai *Modbus TCP Server* (Port 502) untuk menyimpan data mentah.

### Lapisan 2: Python Middleware (Jembatan Integrasi)
* **Sifat:** Skrip Python eksternal (berjalan independen di luar lingkungan Odoo).
* **Tugas Utama:** Melakukan *polling* ke HMI setiap 2 detik via `pyModbusTCP`, mendeteksi perubahan *state*, dan mengirim/menerima data dari Odoo via `xmlrpc.client` atau HTTP *Requests*.

### Lapisan 3: Odoo 18 Community (Backend ERP)
* **Sifat:** Tiga *custom module* Odoo untuk mengolah data dari Middleware dan menampilkannya di UI.

---

## 2. DETAIL IMPLEMENTASI MIDDLEWARE (LAPISAN 2)

### Peta Register Modbus (Omron NB HMI)
Middleware bertugas menyinkronkan data antara HMI dan Odoo berdasarkan acuan register berikut:

| Address | Nama / Fungsi | Tipe | Arah | Keterangan Nilai |
| :--- | :--- | :--- | :--- | :--- |
| **40001** | `M_STATUS` | Integer | **READ** | 0 = Stop, 1 = Running, 2 = Pause |
| **40002** | `GOOD_COUNT` | Integer | **READ** | Akumulasi produk *good* per siklus |
| **40003** | `REJECT_COUNT`| Integer | **READ** | Akumulasi produk *reject* per siklus |
| **40004** | `REASON_CODE` | Integer | **READ** | 0=None, 1=Setup, 2=Equipment Failure, 3=Material Shortage |
| **40005** | `WO_ID` | Integer | **READ** | ID *Work Order* Odoo yang sedang aktif |
| **40010** | `OEE_AVA` | Integer | **WRITE** | *Availability* x 100 (Dari Odoo) |
| **40011** | `OEE_PERF` | Integer | **WRITE** | *Performance* x 100 (Dari Odoo) |
| **40012** | `OEE_QUAL` | Integer | **WRITE** | *Quality* x 100 (Dari Odoo) |
| **40013** | `OEE_TOTAL` | Integer | **WRITE** | *Total OEE* x 100 (Dari Odoo) |

### Aturan Logika Middleware
1.  **Library Wajib:** Gunakan `pyModbusTCP` (untuk Modbus) dan `xmlrpc.client` atau `requests` (untuk komunikasi ke API Odoo).
2.  **State Machine Logic (Deteksi Trigger):**
    * `M_STATUS` 0 $\rightarrow$ 1: Kirim sinyal **START** ke Odoo.
    * `M_STATUS` 1 $\rightarrow$ 2: Kirim sinyal **PAUSE** + `REASON_CODE` ke Odoo.
    * `M_STATUS` 2 $\rightarrow$ 1: Kirim sinyal **RESUME** ke Odoo.
    * Kuantitas bertambah: Kirim *update* nilai `GOOD_COUNT` atau `REJECT_COUNT` ke Odoo.
3.  **Feedback Loop:** Setelah update ke Odoo, tarik (GET) nilai OEE terbaru dari Odoo, lalu tulis ke register HMI (40010 - 40013) untuk layar operator.
4.  **Error Handling:** Wajib menggunakan blok *try-except* dengan mekanisme *auto-reconnect* jika koneksi terputus.

---

## 3. DETAIL IMPLEMENTASI ODOO 18 (LAPISAN 3)

### Struktur Modul (Core Architecture)
Buat 3 modul kustom dengan struktur standar Odoo (`__manifest__.py`, `models/`, `controllers/`, `views/`, `security/`, `static/src/`):

1.  **`mrp_shopfloor_custom`**: Mengganti fitur Shop Floor Enterprise. Menyediakan:
    * HTTP Controller (`POST /api/machine/...`) untuk menerima instruksi dari Middleware.
    * **OWL UI (Dark Mode)**: Antarmuka tablet bergaya *card view* untuk operator di lantai pabrik.
    * Penulisan data ke `mrp.workcenter.productivity`.
    * **Dual Trigger**: Otomatis (dari Modbus via Middleware) DAN manual (tombol di UI).

2.  **`mrp_oee_custom`**: Mengkalkulasi OEE. Tambahkan *computed fields* di `mrp.workcenter`. Modul ini juga bertanggung jawab menampilkan *dashboard* UI.

3.  **`mrp_quality_custom`** (sebelumnya `mrp_scrap_auto`): Mengganti fitur Quality Enterprise. Menyediakan:
    * Otomatisasi pembuatan `mrp.scrap` dari sinyal sensor *reject* via API.
    * **Quality Control Points**: Trigger otomatis inspeksi.
    * **Quality Checks**: Formulir inspeksi (Pass/Fail, Measure, Take a Picture).
    * **Quality Alerts**: Kanban board untuk tim QC.
    * **OWL Toast Notification**: Notifikasi kecil saat reject bertambah.
    * **Dual Trigger**: Otomatis (dari sensor) DAN manual (tombol di UI).

---

### 3A. Shop Floor Custom — Spesifikasi UI/UX

#### Desain Visual
* **Tema:** Dark Mode (default) — nyaman untuk layar industri/tablet.
* **Navigasi Kiri (Operator Panel):** Menampilkan operator aktif di Work Center + status (Aktif/Inaktif).
* **Navigasi Atas (Work Center Tabs):** Perpindahan cepat antar Work Center tanpa reload.
* **Kanban/Card View:** Setiap Work Order = 1 kartu interaktif (nama produk, jumlah target, langkah operasional).

#### Fungsionalitas
* **Real-time Mirroring:** UI OWL polling setiap 5 detik, otomatis mirror perubahan `M_STATUS` dari HMI.
* **Manual Override:** Tombol Start/Pause/Resume di UI sebagai alternatif trigger otomatis dari Modbus.
* **Time Tracking:** Saat WO aktif, timer berjalan dan buat record `mrp.workcenter.productivity`.
* **Work Instructions:** Pop-up PDF/teks instruksi kerja (SOP) di layar yang sama.
* **Tombol Pintasan (Quick Actions):**
    * Record Production (catat barang jadi).
    * Scrap (catat barang cacat).
    * Add Component (tambah konsumsi material).
* **Multi-Operator:** Beberapa operator login ke 1 mesin bersamaan.

---

### 3B. Quality Custom — Spesifikasi UI/UX

#### Desain Visual
* **Dashboard Overview:** Ringkasan jumlah QC check pending + quality alerts.
* **Pop-up Integration:** Di Shop Floor, QC check muncul sebagai pop-up dialog (bukan halaman baru).
* **Toast Notification:** Saat `REJECT_COUNT` bertambah, muncul toast kecil di pojok layar.

#### Fungsionalitas
* **Quality Control Points (Titik Kontrol):** Admin mendefinisikan trigger inspeksi otomatis (contoh: "Inspeksi setiap MO Komponen Type-A selesai").
* **Quality Checks (Formulir Inspeksi):** Tipe:
    * *Pass/Fail* — Lulus atau Gagal.
    * *Measure* — Input nilai ukur (misal: suhu) dengan batas toleransi.
    * *Take a Picture* — Upload foto barang.
* **Quality Alerts (Peringatan):** Jika check = Fail → otomatis buat Quality Alert → Kanban board terpisah untuk tim QC (Root Cause Analysis).
* **Auto Scrap:** Setiap sinyal `REJECT_COUNT` bertambah → backend otomatis buat `mrp.scrap`.
* **Manual Scrap:** Tombol "Record Scrap" di UI sebagai alternatif trigger otomatis.

---

### 3C. Kebutuhan UI/UX Umum (Frontend)
1.  Wajib menggunakan **OWL Framework (Odoo Web Library)** untuk semua komponen visual.
2.  Gunakan **Custom Controller (Python)** untuk mereturn data JSON.
3.  Implementasikan **Polling** pada OWL *component* (refresh setiap 5 detik) untuk efek *real-time*.
4.  Ikuti referensi desain di file `brandGuidelines.md`.
5.  Semua fitur harus bisa di-trigger **otomatis** (dari Modbus/Middleware) DAN **manual** (tombol di UI).

---

## 4. STRICT DEVELOPMENT RULES (WAJIB DIPATUHI)

1.  **NO ENTERPRISE:** Dilarang keras mengimpor atau menggunakan dependensi dari modul Odoo Enterprise (Shop Floor, IoT Box, Quality, dll).
2.  **Kalkulasi OEE:** Gunakan formula matematis berikut:
    * $Availability = \frac{Operating\ Time}{Planned\ Production\ Time}$
    * $Performance = \frac{Ideal\ Cycle\ Time \times Total\ Count}{Operating\ Time}$ (Nilai maksimal 100%)
    * $Quality = \frac{Good\ Count}{Total\ Count}$
    * $Total\ OEE = A \times P \times Q \times 100$
3.  **Integritas Data:** Durasi di tabel `mrp.workcenter.productivity` harus dihitung secara nyata ($date\_end - date\_start$). Nilai durasi tidak boleh 0.00.
4.  **Jalur Integrasi:** Odoo hanya bertugas menerima data via XML-RPC atau HTTP Controller. Odoo tidak melakukan ping ke Modbus.
5.  **Code Quality:** Gunakan standar Python 3.x, tangani *exception*, dan kembalikan kode status HTTP yang benar (200 OK, 400 Bad Request) pada setiap *controller*.
6.  **Dual Trigger:** Setiap aksi (Start, Pause, Resume, Scrap, QC Check) harus bisa di-trigger via API (otomatis dari Middleware) DAN via tombol manual di OWL UI.