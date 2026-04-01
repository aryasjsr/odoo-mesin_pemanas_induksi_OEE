


Berikut adalah **analisis permasalahan dari Step by Step perocobaan** yang sudah dijalankan, serta keterkaitannya dengan **custom module Shop Floor, Quality, dan OEE** yang Anda buat:

***

## PERMASALAHAN PER STEP \& DAMPAK KE CUSTOM MODULE


***

### STEP 2 — Work Center (Mesin Pemanas Induksi 01)

**Masalah yang ditemukan:**


| \# | Masalah | Dampak ke Custom Module |
| :-- | :-- | :-- |
| 1 | **Loss Reason tidak bisa diakses via menu** (Step 3 tergabung di sini) — menu tersembunyi di Community edition | Custom OEE module kemungkinan bergantung pada `mrp.workcenter.productivity.loss` untuk mencatat downtime. Jika Loss Reason tidak diisi manual, OEE calculation bisa **salah atau kosong** |
| 2 | **OEE Target diset 85% tapi tidak ada validasi** apakah sudah terhubung ke custom OEE dashboard | Custom OEE module perlu memastikan field `oee_target` dibaca dari `mrp.workcenter`, bukan hardcoded di view |
| 3 | Menu Work Centers tidak langsung muncul di navbar — harus via Settings | Menandakan `mrp_workcenter` view mungkin **belum di-inherit** di custom module Anda untuk menampilkan field OEE tambahan (jika ada) |


***

### STEP 3 — Loss Reason

**Masalah yang ditemukan:**


| \# | Masalah | Dampak ke Custom Module |
| :-- | :-- | :-- |
| 1 | **Menu Loss Reason tidak tersedia** di Odoo Community — hanya ada di Enterprise | Jika custom OEE module Anda membuat menu Loss Reason sendiri, perlu dipastikan model `mrp.workcenter.productivity.loss` sudah di-`depends` dengan benar di `__manifest__.py` |
| 2 | Default Loss Reason tidak bisa dikustomisasi tanpa akses menu | Custom module seharusnya **menyediakan menu Loss Reason sendiri** di bawah Manufacturing → Configuration, bukan bergantung pada Enterprise |
| 3 | Tidak ada Loss Reason spesifik industri (misal: "Gangguan Mesin Induksi") | OEE report akan kurang informatif — custom module perlu seed data (`data/loss_reason_data.xml`) |


***

### STEP 4 — Employee (Budi)

**Masalah yang ditemukan:**


| \# | Masalah | Dampak ke Custom Module |
| :-- | :-- | :-- |
| 1 | **Modul HR harus diinstall manual** — tidak otomatis ter-depend | Jika custom Shop Floor module menggunakan `hr.employee` untuk login operator, maka `hr` harus masuk ke `depends` di `__manifest__.py` |
| 2 | **Tidak ada resource/calendar** yang di-assign ke Budi | Work Order Duration calculation di OEE bisa tidak akurat karena tidak ada jam kerja (working calendar) yang terdefinisi |
| 3 | Employee belum di-link ke Work Center sebagai operator | Custom Shop Floor module yang menampilkan "siapa operator aktif" tidak akan bisa bekerja jika relasi `employee_id` ↔ `workcenter_id` tidak disetup |


***

### STEP 5 — Produk (Komponen Induksi Type-A)

**Masalah yang ditemukan:**


| \# | Masalah | Dampak ke Custom Module |
| :-- | :-- | :-- |
| 1 | **Tidak ada Unit of Measure (UoM)** yang dikonfirmasi — default bisa salah | Jika custom module menampilkan output qty di Shop Floor, satuan bisa tidak match |
| 2 | **Tidak ada harga pokok (Cost)** yang diset | OEE \& manufacturing cost analysis tidak akan akurat |
| 3 | Route "Manufacture" diaktifkan tapi **tidak ada reorder rule** | Di skenario nyata, produksi tidak akan terpicu otomatis — mungkin tidak relevan di studi kasus ini, tapi perlu diperhatikan |


***

### STEP 6A — Bill of Materials + Routing

**Masalah yang ditemukan:**


| \# | Masalah | Dampak ke Custom Module |
| :-- | :-- | :-- |
| 1 | **Durasi operasi "Proses Induksi" = 2 menit** — sangat singkat, bisa menyebabkan OEE duration terlalu kecil untuk dianalisis | Custom OEE module yang menghitung `duration_expected` vs `duration` bisa menghasilkan angka OEE yang tidak realistis |
| 2 | **Tidak ada komponen (component)** yang ditambahkan di BoM | BoM kosong — jika custom module menampilkan komponen di Shop Floor tablet view, bagian itu akan kosong |
| 3 | **Tidak ada worksheet/work instruction** di operasi | Custom Shop Floor module yang punya fitur tampilkan instruksi kerja tidak akan menampilkan konten apapun |
| 4 | Hanya 1 operasi — tidak cukup untuk menguji **multi-step OEE** | Jika custom module mendukung tracking OEE per operasi, tidak bisa diuji dengan setup ini |


***

### STEP 6B — Quality Control Point (QCP)

**Masalah yang ditemukan:**


| \# | Masalah | Dampak ke Custom Module |
| :-- | :-- | :-- |
| 1 | **Trigger = "Manual trigger only"** — QCP tidak akan muncul otomatis saat Work Order dibuka | Jika custom Quality module didesain untuk auto-trigger saat operasi dimulai/selesai, ini tidak akan berjalan dengan setup manual |
| 2 | **Tidak ada instruksi** yang diisi di field Instructions | Custom module yang menampilkan instruksi QCP di tablet/Shop Floor akan menampilkan area kosong |
| 3 | **Check Type = Pass/Fail** saja — tidak ada toleransi numerik | Untuk kasus inspeksi mesin induksi, idealnya ada pengukuran suhu/tegangan dengan nilai min-max (Check Type: Measure) |
| 4 | **Tidak ada link ke Operation** (hanya Work Center) | QCP tidak akan muncul di tab Quality pada specific Work Order operation — hanya muncul di level MO secara umum |


***

## RINGKASAN REKOMENDASI PERBAIKAN UNTUK CUSTOM MODULE

```
Custom Module          Perbaikan yang Diperlukan
─────────────────────  ──────────────────────────────────────────────────
mrp_shopfloor_custom   - Tambah depends: ['hr', 'mrp_workcenter']
                       - Employee ↔ Work Center mapping
                       - Handle BoM tanpa komponen (graceful empty state)

mrp_oee_custom         - Tambah menu Loss Reason sendiri (Community fix)
                       - Seed data loss reason spesifik industri
                       - Validasi working calendar employee
                       - Gunakan oee_target dari mrp.workcenter (bukan hardcode)

mrp_quality_custom     - Support auto-trigger (selain manual)
                       - Tambah field instruksi wajib (required=True)
                       - Support Check Type: Measure (dengan min/max)
                       - Link QCP ke Operation, bukan hanya Work Center
```


***

**Intinya**, setup Step 2–6 sudah cukup sebagai **proof of concept**, tapi untuk custom module Anda bisa berjalan penuh, perlu ada penyesuaian di: `__manifest__.py` (dependencies), seed data Loss Reason, relasi Employee–WorkCenter, dan QCP trigger mode yang sesuai dengan alur Shop Floor Anda.

