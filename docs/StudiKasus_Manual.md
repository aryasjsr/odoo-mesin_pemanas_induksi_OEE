# buatkan studi kasus step by step terkait kasus manual trigger,  dari setting product sampai akhir.

Berikut tutorial **step-by-step lengkap** dari nol — mulai setting produk hingga melihat hasil OEE — menggunakan studi kasus Budi di Odoo 17 Enterprise.

***

## OVERVIEW ALUR

```
SETUP AWAL (sekali)          PRODUKSI HARIAN
─────────────────────        ──────────────────────────────────
Step 1: Aktifkan Settings    Step 7 : Supervisor buat MO
Step 2: Buat Work Center     Step 8 : Budi login Shop Floor
Step 3: Buat Loss Reason     Step 9 : Budi START Work Order
Step 4: Buat Employee        Step 10: Budi update Qty (Register Production)
Step 5: Buat Product         Step 11: Budi catat Downtime (Block)
Step 6: Buat BoM + Routing   Step 12: Budi Resume
         + QCP               Step 13: Budi input Scrap/Reject
                             Step 14: Budi Close Production
                             Step 15: Lihat OEE Report
```


***

## ═══ SETUP AWAL (Dilakukan Sekali) ═══


***

### STEP 1 — Aktifkan Settings \& Modul

**Path:** `Manufacturing → Configuration → Settings`

Aktifkan semua fitur berikut, lalu klik **Save:**

1. **Work Orders** ✅
→ Wajib agar routing \& operasi aktif di BoM
2. **Shop Floor** ✅
→ Mengaktifkan menu Shop Floor untuk operator
3. **Workcenter Time Off** ✅
→ Mendukung tracking jam kerja planned
4. Install modul **Quality** dari Apps jika belum terpasang:
→ `Apps → search "Quality Control" → Install`

***

### STEP 2 — Buat Work Center "Mesin Pemanas Induksi 01"

**Path:** `Manufacturing → Configuration → Work Centers → New`

Isi field berikut:


| Field | Nilai |
| :-- | :-- |
| **Work Center Name** | `Mesin Pemanas Induksi 01` |
| **Time Efficiency** | `100%` |
| **OEE Target** | `85` |
| **Capacity** | `1` |
| **Working Hours** | `Shift Pagi (07:00–15:00)` |
| **Time Before Prod.** | `0` |
| **Time After Prod.** | `0` |
| **time_cycle_manual** | `2` (menit/pcs = Ideal Cycle Time) |

> ⚠️ Field `time_cycle_manual` muncul di tab **General** dengan label **"Default Duration"** atau **"Duration per Unit"** — pastikan diisi **2 menit** karena ini adalah referensi perhitungan **Performance OEE**.

Klik **Save.**

***

### STEP 3 — Buat Loss Reason (Kategori Downtime)

**Path:** `Manufacturing → Configuration → Workcenter Losses → New`

Buat 3 kategori berikut:[^1]


| Loss Name | Loss Type | Keterangan |
| :-- | :-- | :-- |
| `Equipment Failure` | Availability Loss | Kerusakan mesin |
| `Material Shortage` | Availability Loss | Kekurangan bahan |
| `Setup & Adjustment` | Availability Loss | Penyetelan mesin |

Untuk setiap kategori:

1. Klik **New**
2. Isi **Loss Name** dan **Loss Type = Availability**
3. Klik **Save**

***

### STEP 4 — Buat Employee "Budi"

**Path:** `Employees → New`


| Field | Nilai |
| :-- | :-- |
| **Employee Name** | `Budi` |
| **Job Position** | `Operator Mesin` |
| **Work Location** | `Lantai Produksi` |

Klik **Save.**

> 💡 Employee ini penting agar record `mrp.workcenter.productivity` memiliki field employee terisi dan **Duration tidak 0.00** (masalah yang ditemukan sebelumnya).

***

### STEP 5 — Buat Produk "Komponen Induksi Type-A"

**Path:** `Manufacturing → Products → Products → New`

**Tab General Information:**


| Field | Nilai |
| :-- | :-- |
| **Product Name** | `Komponen Induksi Type-A` |
| **Product Type** | `Storable Product` |
| **Unit of Measure** | `Units (pcs)` |
| **Sales Price** | *(isi sesuai kebutuhan)* |

**Tab Inventory:**

- Centang ✅ **Can be Manufactured** di bagian Routes

Klik **Save.**

***

### STEP 6A — Buat Bill of Materials (BoM)

**Path:** `Manufacturing → Products → Bills of Materials → New`


| Field | Nilai |
| :-- | :-- |
| **Product** | `Komponen Induksi Type-A` |
| **Quantity** | `1 pcs` |
| **BoM Type** | `Manufacture this product` |

**Tab Components** (opsional untuk ujicoba, bisa dikosongkan):

- Klik **Add a line** → tambahkan bahan baku jika ada

**Tab Operations:**
Klik **Add a line**, isi:


| Field | Nilai |
| :-- | :-- |
| **Operation** | `Proses Induksi` |
| **Work Center** | `Mesin Pemanas Induksi 01` |
| **Default Duration** | `2 menit` |
| **Duration per Unit** | ✅ Centang (agar 200 pcs = 400 menit) |

Klik **Save.**

***

### STEP 6B — Buat Quality Control Point (QCP)

**Path:** `Quality → Configuration → Control Points → New`


| Field | Nilai |
| :-- | :-- |
| **Name** | `Inspeksi Akhir Induksi` |
| **Product** | `Komponen Induksi Type-A` |
| **Operation** | `Proses Induksi` |
| **Work Center** | `Mesin Pemanas Induksi 01` |
| **Control Frequency** | `All Operations` |
| **Type** | `Pass - Fail` |
| **Team** | *(opsional)* |

Klik **Save.**

> ✅ **Setup selesai.** Semua langkah di atas hanya dilakukan sekali. Mulai Step 7 adalah alur harian produksi.

***

## ═══ ALUR PRODUKSI HARIAN ═══


***

### STEP 7 — Supervisor Buat Manufacturing Order (06:50)

**Path:** `Manufacturing → Operations → Manufacturing Orders → New`


| Field | Nilai |
| :-- | :-- |
| **Product** | `Komponen Induksi Type-A` |
| **Bill of Materials** | *auto-terisi* |
| **Quantity** | `200` |
| **Scheduled Date** | `Hari ini, 07:00` |
| **Responsible** | `Budi` |

Klik **Confirm** → Status MO berubah: `Draft → Confirmed`

Cek tab **Work Orders** → otomatis muncul:

```
Operation  : Proses Induksi
Work Center: Mesin Pemanas Induksi 01
Expected   : 400 menit (2 menit × 200 pcs)
Status     : To Do
```


***

### STEP 8 — Budi Login ke Shop Floor (07:00)

**Path:** `Manufacturing → Shop Floor`

1. Halaman Shop Floor terbuka → tampil daftar Work Center
2. Di **pojok kiri bawah**, klik ikon **👤 (Worker)**
3. Muncul daftar employee → klik **"Budi"**
4. Masukkan PIN jika diminta → klik **Confirm**
5. Status berubah: **"Budi is now working ✅"**

> ⚠️ **WAJIB** login employee terlebih dahulu sebelum mulai.

***

### STEP 9 — Budi START Work Order (07:05)

1. Di Shop Floor, klik Work Center **"Mesin Pemanas Induksi 01"**
2. Tampil kartu Work Order: *"Komponen Induksi Type-A — 200 pcs"*
3. Klik tombol **▶ (Play/Start)**
4. Status WO berubah: `To Do → In Progress`
5. **Timer mulai berjalan** → tampil `00:01, 00:02, ...`

Odoo otomatis membuat record di `mrp.workcenter.productivity`:

```
Employee   : Budi
Type       : Fully Productive Time
Date Start : 07:05
Date End   : (masih kosong, sedang berjalan)
Duration   : (berjalan real-time)
```


***

### STEP 10 — Budi Update Qty Produksi (Berkala)

Setiap interval ±30 menit, Budi melakukan ini di Shop Floor:

1. Klik kartu Work Order → kartu expand
2. Cari baris **"Register Production"** di bagian bawah kartu
3. Klik baris tersebut → muncul field angka
4. Input jumlah unit yang sudah selesai → klik **✔ Apply**

**Jadwal input Budi:**


| Jam | Qty Input | Keterangan |
| :-- | :-- | :-- |
| 08:00 | `60` | Produksi berjalan normal |
| 09:00 | `120` | Produksi berjalan normal |
| 09:30 | `145` | Sebelum mesin mati |


***

### STEP 11 — Budi Catat Downtime / Block (09:30)

Mesin berhenti karena gangguan coil induksi:

1. Di kartu Work Order (saat masih In Progress) → klik tombol **⏸ (Pause)**
atau klik ikon **🔧 (Block Workcenter)**
2. Muncul popup **"Block Workcenter"**
3. Pilih **Loss Reason: `Equipment Failure`**
4. Klik **Confirm**

Odoo otomatis:

- Menutup record *Productive*: `Date End = 09:30`
- Membuat record baru *Availability Loss*: `Date Start = 09:30`

```
Employee   : Budi
Type       : Equipment Failure (Availability Loss)
Date Start : 09:30
Date End   : (masih berjalan)
Duration   : (akumulasi downtime)
```


***

### STEP 12 — Budi Resume Setelah Perbaikan (10:00)

Mesin selesai diperbaiki jam 10:00:

1. Di kartu Work Order yang ter-block → klik tombol **▶ (Resume / Unblock)**
2. Odoo menutup record Loss: `Date End = 10:00`
3. **Downtime = 30 menit** ✅ (09:30 → 10:00)
4. Record *Productive* baru dimulai: `Date Start = 10:00`

Produksi kembali berjalan. Budi lanjut update qty:


| Jam | Qty Input |
| :-- | :-- |
| 11:00 | `160` |
| 12:00 | `175` |
| 13:30 | `190` |
| 14:30 | `200` → produksi selesai |


***

### STEP 13 — Input Scrap / Reject (14:30)

Setelah total 200 pcs tercapai, Budi mencatat 7 pcs reject:

**Cara A — via Shop Floor (Direkomendasikan):**

1. Di kartu Work Order → klik ikon **⋮ (titik tiga)**
2. Pilih **"Scrap"**
3. Isi:
    - **Product:** `Komponen Induksi Type-A`
    - **Quantity:** `7`
4. Klik **Validate**

**Cara B — via Manufacturing Order:**

1. Buka MO → klik tombol **"Scrap"** di header
2. Isi product + qty `7` → klik **Validate**[^3]

Record `mrp.scrap` dibuat:

```
Production ID : MO/00001
Product       : Komponen Induksi Type-A
Qty Scrap     : 7 pcs
```


***

### STEP 14 — Quality Check \& Close Production (15:00)

1. Di Shop Floor, klik tombol **"Close Production"** pada kartu WO
2. Odoo otomatis memunculkan **Quality Check popup** (karena QCP sudah dikonfigurasi di Step 6B)[^4]
3. Form Quality Check tampil:
    - **Inspection:** `Inspeksi Akhir Induksi`
    - **Result:** pilih **Pass** (karena scrap sudah dicatat terpisah)
4. Klik **Validate**
5. Status Work Order → **Done**
6. Status MO → klik **Produce All** → **Done**

***

### STEP 15 — Lihat Laporan OEE (Supervisor)

**Path:** `Manufacturing → OEE ->Dashboard`

Filter:

- **Work Center:** `Mesin Pemanas Induksi 01`
- **Date:** hari ini

**Hasil yang tampil:**[^5]

```
┌─────────────────────────────────────────────┐
│   OEE REPORT — MESIN PEMANAS INDUKSI 01     │
├───────────────────┬─────────────────────────┤
│ Availability      │ 93.75%  ✅              │
│ Performance       │ 88.89%  ✅              │
│ Quality           │ 96.50%  ✅              │
│ OEE Total         │ 80.44%  🟡              │
├───────────────────┼─────────────────────────┤
│ Operating Time    │ 450 menit               │
│ Lost Time         │ 30 menit (Equip. Fail.) │
│ Good Count        │ 193 pcs                 │
│ Reject Count      │ 7 pcs                   │
└───────────────────┴─────────────────────────┘
```

Supervisor juga bisa klik **"Lost Hours"** untuk melihat breakdown downtime per kategori per mesin.

***

## Ringkasan Alur Lengkap

```
[STEP 1-3] Admin Setting     → Aktifkan WO, Shop Floor, Loss Reason
[STEP 4]   Admin Employee    → Daftarkan Budi
[STEP 5-6] Admin Master Data → Product + BoM + Routing + QCP
              ─────── SETUP SELESAI ───────
[STEP 7]   Supervisor        → Buat MO (200 pcs)
[STEP 8]   Budi Shop Floor   → Login Employee (WAJIB!)
[STEP 9]   Budi Shop Floor   → START → timer jalan, record Productive dibuat
[STEP 10]  Budi Shop Floor   → Register Production (update qty berkala)
[STEP 11]  Budi Shop Floor   → BLOCK → pilih "Equipment Failure" (09:30)
[STEP 12]  Budi Shop Floor   → RESUME → downtime 30 menit tercatat (10:00)
[STEP 13]  Budi Shop Floor   → SCRAP → input 7 pcs reject
[STEP 14]  Budi Shop Floor   → CLOSE → QCP popup → Validate → MO Done
[STEP 15]  Supervisor Odoo   → Reporting → OEE → 80.44% ✅
```