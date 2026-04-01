# OEE System — Walkthrough (REVISED)

## Summary

**70 files** across 4 Odoo 18 modules.

| Module | Highlights |
|---|---|
| `mrp_shopfloor_custom` | Dark-mode OWL tablet UI, WO cards, operator clock-in/out, manual Start/Pause/Resume, modals. |
| `mrp_oee_custom` | OEE computed fields + circular gauge dashboard. |
| `mrp_quality_custom` | Control points, checks, alerts, quality dashboard, toast notifications, manual/auto scrap. |
| `mrp_oee_modbus` | Modbus TCP config, mapping, pymodbus service, test wizard, cron background polling. |

---

## 🛠 Panduan Testing Modbus (dengan Modbus Poll)

Berikut adalah langkah-langkah untuk melakukan simulasi dan testing Modbus TCP menggunakan aplikasi **Modbus Poll** di komputer Anda (Windows).

### 1. Setup Modbus Poll (Simulator Panel HMI)
Kita akan menjadikan Modbus Poll sebagai server Modbus simulasi (seandainya HMI belum tersedia).
1. Buka Modbus Poll.
2. Karena kita ingin Odoo yang membaca/menulis ke HMI, Modbus Poll harus bertindak sebagai **Modbus Server**. Pergi ke `Connection` → `Connect...`. 
*(Note: Jika Modbus Poll Anda bertindak sebagai Client, gunakan **ModRSsim2** yang secara default adalah Modbus Server TCP di Port 502).*
3. Buat dua window di simulator:
   * **Window 1: Holding Registers (4x)**: Address 0 - 15.
   * **Window 2: Coils (0x)**: Address 0.

4. **Isi Data Dummy (Simulasi HMI)** pada Holding Registers:
   * **Address 0** (Planned Time): `480`
   * **Address 1** (Run Time): `400`
   * **Address 2** (Downtime): `80`
   * **Address 3** (Produced Qty): `1000`
   * **Address 4** (Ideal Qty): `1200`
   * **Address 5** (Defect Qty): `50`
   * **Coil 0** (Machine Status): `1` (ON)

*(Note: Address Odoo sudah diset 0-based. Jadi di Modbus Poll / HMI Omron, Holding Register address 0 = register 40001).*

### 2. Setup Modbus Configuration di Odoo
1. Di Odoo, buka menu **Manufacturing → Modbus → Configurations**.
2. Klik **New** untuk membuat konfigurasi baru:
   * **Profile Name:** `Mesin Induksi #1 Simulasi`
   * **Host / IP:** Jika Odoo dan Modbus Simulator berada di laptop yang sama dan Odoo berjalan di Docker, gunakan IP `host.docker.internal` (atau IP LAN laptop Anda, misal `192.168.1.10`).
   * **Port:** `502`
3. Simpan (Save). Odoo akan mencoba memuat template register map dari default yang kita siapkan. Jika register map kosong, klik tombol **Action → Duplicate** dari *Default Omron NB HMI Template* lalu ganti host IP-nya.
4. Klik tombol **🔌 Test Connection**. Wizard akan terbuka, mencoba membaca semua register, dan menampilkan status ✅ hijau jika berhasil terhubung dengan Modbus Poll Anda.

### 3. Testing Sync OEE & Polling
Ada dua cara menguji sinkronisasi Modbus:

**A. Manual Sync (Test Per-Mesin)**
1. Buka **Manufacturing → Configuration → Work Centers**.
2. Pilih salah satu mesin (contoh: Assembly Line 1).
3. Pada tab utama, isi field **Modbus Configuration** dengan konfigurasi `Mesin Induksi #1 Simulasi` yang baru saja dibuat.
4. Klik tulisan (tombol) **📡 Sync OEE from Modbus** yang ada di bagian atas (header).
5. Odoo akan menarik nilai dummy dari Modbus Poll, mengkalkulasi OEE, menulis hasilnya kembali, dan menampilkan notifikasi sukses.
6. Cek kembali aplikasi **Modbus Poll** Anda. Pada address `10`, `11`, `12`, dan `13`, angkanya akan terisi oleh Odoo:
   * Address 10 (Availability) = `8333` (83.33%)
   * Address 11 (Performance) = `8333` (83.33%)
   * Address 12 (Quality) = `9500` (95.00%)
   * Address 13 (Overall OEE) = `6596` (65.96%)

**B. Auto Polling (Background)**
1. Masuk kembali ke Modbus Configuration (`Mesin Induksi #1 Simulasi`).
2. Jangan lupa set `Work Center` yang ingin di-link pada config ini.
3. Klik tombol **▶ Start Polling**. 
4. Odoo akan otomatis menjalankan sinkronisasi Modbus secara konstan setiap 5 detik (sesuai setting `Polling Interval`).
5. Uji dengan mengganti nilai di Modbus Poll secara *real-time* (misal: ubah Run Time dari 400 ke 450). Tunggu maksimal 5 detik, dan nilai OEE di address 10-13 akan otomatis ter-update oleh Odoo!
6. Untuk berhenti, klik **⏹ Stop Polling**.
