# Setup Odoo Native Windows (Tanpa Docker)

Panduan lengkap untuk setup Odoo development di Windows tanpa menggunakan Docker.

## ✅ Prerequisites

- **Windows 10/11** (64-bit recommended)
- **Python 3.10+** (dari python.org)
- **PostgreSQL 15+** (Windows installer)
- **Git for Windows** (untuk version control)
- **Visual Studio Build Tools** (untuk compile Python packages)

---

## 📋 Step-by-Step Installation

### 1️⃣ Install Visual Studio Build Tools

Beberapa Python packages memerlukan C++ compiler untuk diinstall.

```bash
# Download dari Microsoft:
# https://visualstudio.microsoft.com/visual-cpp-build-tools/

# Saat install, pilih:
# - Desktop development with C++
# - Windows 10 SDK
```

### 2️⃣ Install Python 3.10+

1. Download dari: https://www.python.org/downloads/
2. **Penting**: Centang `Add Python to PATH` saat install
3. Verifikasi instalasi:

```bash
python --version
pip --version
```

### 3️⃣ Install PostgreSQL 15

1. Download dari: https://www.postgresql.org/download/windows/
2. Jalankan installer (pilih default: `C:\Program Files\PostgreSQL\15`)
3. Set password superuser (ingat password ini!)
4. Verifikasi instalasi di Command Prompt:

```bash
# Buka cmd.exe
psql --version

# Atau test koneksi:
psql -U postgres -h localhost
```

### 4️⃣ Create PostgreSQL User untuk Odoo

Buka **pgAdmin 4** (datang dengan PostgreSQL):

```sql
-- Atau gunakan Command Prompt:
psql -U postgres

postgres=# CREATE USER odoo WITH PASSWORD 'odoo_password_123';
postgres=# ALTER USER odoo WITH SUPERUSER;
postgres=# \q
```

**Alternatif via pgAdmin UI:**
- Login sebagai `postgres`
- Klik kanan `Login/Group Roles` → Create
- Username: `odoo`
- Password: `odoo_password_123`
- Privileges tab: ✅ Superuser

### 5️⃣ Clone Project

```bash
# Buka Command Prompt / PowerShell
cd D:\ARYA\SEMESTER 8\ENTERPRISE AUTOMATION
git clone <your-repo-url>
cd Odoo
```

### 6️⃣ Setup Python Virtual Environment

```bash
# Buka PowerShell di project folder
python -m venv venv

# Activate virtual environment
venv\Scripts\activate

# Upgrade pip
python -m pip install --upgrade pip
```

Setelah ini, terminal Anda akan menampilkan `(venv)` prefix:
```
(venv) PS C:\path\to\Odoo>
```

### 7️⃣ Install Python Dependencies

```bash
# Pastikan venv sudah aktif (tanda (venv))
pip install -r setup\requirements.txt
```

**Jika ada error** (terutama psycopg2):
```bash
# Alternatif wheels version:
pip install psycopg2-binary==2.9.9
```

### 8️⃣ Configure Odoo

#### Option A: Via Environment File (Recommended)

```bash
# Copy template
copy config\.env.example .env

# Edit .env dengan Notepad/VSCode
# Baris yang penting:
```

Edit file `.env`:
```env
# Windows Native Setup
DB_HOST=localhost
DB_PORT=5432
DB_USER=odoo
DB_PASSWORD=odoo_password_123
ODOO_PORT=8069
ODOO_LOG_LEVEL=info
```

#### Option B: Via Odoo Config File

```bash
# Copy template config
copy setup\odoo.conf.template %USERPROFILE%\.odoorc

# Edit dengan Notepad
```

Edit `C:\Users\<YourUsername>\.odoorc`:
```ini
[options]
admin_passwd = admin_password_123
db_host = localhost
db_port = 5432
db_user = odoo
db_password = odoo_password_123
db_name = odoo_dev
addons_path = D:\ARYA\SEMESTER 8\ENTERPRISE AUTOMATION\Odoo\addons
log_level = info
dev_mode = True
```

### 9️⃣ Create Initial Database

```bash
# Pastikan venv aktif
# Option 1: Tanpa config file (interactive)
odoo -d odoo_dev -i base --db_user=odoo --db_password=odoo_password_123

# Option 2: Dengan config file
odoo -c %USERPROFILE%\.odoorc -d odoo_dev -i base
```

**Proses ini akan:**
- ✅ Create database `odoo_dev`
- ✅ Install modul `base`
- ✅ Setup Odoo (memakan 2-5 menit, tunggu sampai selesai!)

### 🔟 Run Odoo Development Server

```bash
# Terminal 1: Jalankan Odoo
odoo -c %USERPROFILE%\.odoorc --dev=all

# Atau dengan environment file:
# (Pastikan .env file sudah dikonfigurasi di `.odoorc`)
```

**Output Anda akan terlihat seperti:**
```
2026-04-01 10:15:30,123 INFO ? odoo.sql_db: Connection to PostgreSQL established
2026-04-01 10:15:35,456 INFO ? odoo.addons.web: Web: Ready for connections
2026-04-01 10:15:37,789 INFO ? odoo.http: Routes call `web.webclient` took 0.01s
```

### 1️⃣1️⃣ Access Odoo

Buka browser dan akses:
```
http://localhost:8069
```

**Login credentials:**
- Email: `admin`
- Password: `admin` (atau sesuai `admin_passwd` di config)

---

## 🛠️ Development Tips for Windows

### A. Activate Virtual Environment Every Time

```bash
# PowerShell
venv\Scripts\activate

# Command Prompt (cmd.exe)
venv\Scripts\activate.bat

# Git Bash
source venv/Scripts/activate
```

### B. IDE Setup (VSCode Recommended)

1. Install extension: `Python` (Microsoft)
2. Install extension: `Pylance`
3. Open Command Palette (`Ctrl+Shift+P`):
   - Type: `Python: Select Interpreter`
   - Pilih: `./venv/Scripts/python.exe`

### C. Edit Custom Modules

```
D:\ARYA\SEMESTER 8\ENTERPRISE AUTOMATION\Odoo\addons\
├── mrp_oee_custom\
├── mrp_oee_modbus\
├── mrp_quality_custom\
└── mrp_shopfloor_custom\
```

Setiap edit di files ini, restart Odoo dengan:
- `Ctrl+C` (stop server)
- Naik ke terminal, jalankan `odoo -c %USERPROFILE%\.odoorc --dev=all` lagi

Atau enable `auto-reload` di development mode (`--dev=all` sudah include ini).

### D. Database Management

#### List Databases
```bash
# Gunakan pgAdmin 4 GUI
# Atau command line:
psql -U odoo -h localhost -l
```

#### Backup Database
```bash
# Command Prompt
pg_dump -U odoo -h localhost -d odoo_dev > odoo_backup_2026-04-01.sql
```

#### Restore Database
```bash
psql -U odoo -h localhost -d odoo_dev < odoo_backup_2026-04-01.sql
```

#### Reset Database (Development Only)
```bash
# DROP database (hati-hati!)
dropdb -U odoo -h localhost odoo_dev

# Recreate fresh
odoo -d odoo_dev -i base --db_user=odoo --db_password=odoo_password_123
```

---

## 🚨 Common Issues & Solutions

### ❌ Issue: `python: command not found`

**Solusi:**
- Python tidak di-add ke PATH saat install
- Reinstall Python, **pastikan centang `Add Python to PATH`**
- Atau manual add ke PATH:
  - Settings → System → Environment Variables
  - Add: `C:\Users\<YourUsername>\AppData\Local\Programs\Python\Python310`

### ❌ Issue: PostgreSQL Connection Error

```
psycopg2.OperationalError: could not connect to server
```

**Solusi:**
```bash
# Cek apakah PostgreSQL jalan
# Services (services.msc) → Cari "postgresql" → pastikan "Running"

# Atau restart via Command Prompt:
net stop postgresql-x64-15
net start postgresql-x64-15

# Test koneksi:
psql -U postgres -h localhost
```

### ❌ Issue: Port 8069 Already in Use

```
Address already in use
```

**Solusi:**
```bash
# Gunakan port lain:
odoo -c %USERPROFILE%\.odoorc --xmlrpc-port=8070

# Atau kill proses yang pakai port 8069:
# Task Manager → Cari "odoo" → End Task
```

### ❌ Issue: Module Not Found (psycopg2, lxml, etc)

```
ImportError: No module named psycopg2
```

**Solusi:**
```bash
# Pastikan venv aktif (tanda (venv) di terminal)
pip install psycopg2-binary==2.9.9
pip install lxml
```

### ❌ Issue: Permission Denied saat Write

```
PermissionError: [Errno 13] Permission denied
```

**Solusi:**
- Jalankan PowerShell/CMD **sebagai Administrator** (Run as admin)

---

## 📦 Maintenance & Cleanup

### Update Dependencies
```bash
# Pastikan venv aktif
pip install --upgrade -r setup\requirements.txt
```

### Clean Cache Files
```bash
# Windows Command Prompt
del /s __pycache__
del /s *.pyc
del /s .pytest_cache
rmdir /s __pycache__
```

### Virtual Environment Storage
```
Virtual environment: ~500MB
Install dependencies: ~200MB
Total: ~700MB
```

---

## 🎯 Quick Reference Commands

| Command | Purpose |
|---------|---------|
| `venv\Scripts\activate` | Aktifkan virtual env |
| `deactivate` | Matikan virtual env |
| `pip install -r setup\requirements.txt` | Install dependencies |
| `odoo -c %USERPROFILE%\.odoorc --dev=all` | Run dev server |
| `odoo -d odoo_dev -i base --db_user=odoo` | Buat database baru |
| `psql -U odoo -h localhost` | PostgreSQL CLI |
| `python -m pytest addons\` | Run tests |

---

## ✨ Next Steps

1. ✅ Setup selesai
2. ✅ Edit custom modules di `addons/`
3. ✅ Test deployment ke production
4. ✅ Share project dengan collaborators

**Hubungi team lead jika ada issue!**

---

## 📞 Support

- **PostgreSQL Issues**: https://www.postgresql.org/support/
- **Odoo Documentation**: https://www.odoo.com/documentation/
- **Python Issues**: https://docs.python.org/3/
- **Team**: Ping di [Your Slack/Teams Channel]

