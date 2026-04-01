# UI/UX & BRAND GUIDELINES

## 1. Identitas Visual
* **Nama Sistem:** OEE Mesin Pemanas Induksi
* **Modul UI:** 3 antarmuka (OEE Dashboard, Shop Floor, Quality)

---

## 2. Color Palette — OEE Dashboard (Light Theme)
* **Primary Blue:** `#1E3A8A` (header, border utama).
* **Accent Blue:** `#3B82F6` (progress bar, tombol aktif).
* **Background:** `#F3F4F6` (abu-abu terang).
* **Card Background:** `#FFFFFF` (putih murni).
* **Text Dark:** `#111827` (hitam keabu-abuan).
* **Status Colors:**
    * *Good (>80%):* `#10B981` (Hijau)
    * *Warning (60%-80%):* `#F59E0B` (Kuning)
    * *Critical (<60%):* `#EF4444` (Merah)

## 3. Color Palette — Shop Floor (Dark Theme)
* **Background:** `#111827` (gelap pekat, nyaman untuk layar industri).
* **Surface/Card:** `#1F2937` (kartu WO).
* **Surface Hover:** `#374151` (hover state kartu).
* **Primary Accent:** `#3B82F6` (tombol aktif, tab terpilih).
* **Text Primary:** `#F9FAFB` (putih lembut).
* **Text Secondary:** `#9CA3AF` (abu-abu terang).
* **Border:** `#374151` (garis pemisah halus).
* **Status Running:** `#10B981` (Hijau, badge + glow effect).
* **Status Paused:** `#F59E0B` (Kuning).
* **Status Stop:** `#6B7280` (Abu-abu).
* **Danger/Scrap:** `#EF4444` (Merah, untuk reject/scrap).

## 4. Color Palette — Quality Module
* Menggunakan palette yang sama dengan **Shop Floor (Dark Theme)** ketika di-embed di Shop Floor.
* Menggunakan palette **OEE Dashboard (Light Theme)** untuk halaman standalone (Quality Alerts Kanban, Dashboard).

---

## 5. Komponen UI — OEE Dashboard (OWL)
* **Layout:** Grid Bootstrap responsif.
* **Gauges:** 4 circular progress (Availability, Performance, Quality, Total OEE).
* **Typography:** Font Inter/Roboto. Angka OEE: `font-size: 2rem; font-weight: bold;`.

## 6. Komponen UI — Shop Floor (OWL)
* **Layout:** Full-screen, 3 kolom → Left Panel (Operator) | Main Content (Cards) | (optional right panel).
* **Top Tabs:** Work Center tabs, horizontal scroll. Tab aktif = accent border-bottom.
* **Work Order Cards:** Rounded corners (`12px`), subtle shadow, status indicator dot (glow).
* **Timer Display:** Monospaced font, `font-size: 1.5rem`, warna accent.
* **Quick Action Buttons:** Icon + label, rounded, hover = scale(1.05) + glow.
* **Pop-up Modal:** Glassmorphism background (`backdrop-filter: blur`), smooth `opacity` transition.

## 7. Komponen UI — Quality (OWL)
* **Toast Notification:** Muncul di pojok kanan-atas, background `#EF4444`, auto-dismiss 5 detik, slide-in animation.
* **QC Check Dialog:** Pop-up modal di Shop Floor (bukan halaman baru), form input sesuai tipe (Pass/Fail toggle, number input + tolerance bar, image upload).
* **Quality Alerts Kanban:** Card-based kanban (New → In Progress → Done), warna border kiri sesuai severity.

---

## 8. Perilaku Interaktif (OWL & Polling)
* Semua komponen OWL: fetch data asinkron (`onWillStart` atau `useEffect`).
* Polling: `setInterval` setiap 5 detik ke endpoint JSON masing-masing.
* Wajib `clearInterval` pada `onWillUnmount` / `onWillDestroy`.
* Transisi angka: CSS transitions pada progress bar dan counter.
* Toast: CSS `@keyframes` slide-in dari kanan, auto-dismiss.
