# Setup Odoo Native Linux (Tanpa Docker)

Panduan lengkap untuk setup Odoo pada sistem Linux native tanpa menggunakan Docker.

## 📋 Prerequisites

- **OS**: Ubuntu 22.04 LTS atau lebih baru (Debian-based)
- **Python**: 3.10+
- **PostgreSQL**: 15+
- **Git**: Latest version
- **RAM**: Minimal 2GB (recommended 4GB+)
- **Disk**: Minimal 10GB free space

---

## 🚀 Installation Steps

### 1️⃣ Install PostgreSQL

```bash
# Update package manager
sudo apt update
sudo apt upgrade -y

# Install PostgreSQL
sudo apt install -y postgresql postgresql-contrib postgresql-server-dev-15

# Start PostgreSQL service
sudo systemctl start postgresql
sudo systemctl enable postgresql

# Verify installation
psql --version
```

### 2️⃣ Create Database User

```bash
# Login ke PostgreSQL
sudo -u postgres psql

# Jalankan commands di PostgreSQL:
postgres=# CREATE USER odoo WITH PASSWORD 'odoo' CREATEDB;
postgres=# ALTER ROLE odoo WITH CREATEDB;
postgres=# ALTER ROLE odoo CREATEDB CREATEROLE;
postgres=# \q
```

### 3️⃣ Install Python Dependencies

```bash
# Install system-level dependencies
sudo apt install -y python3-dev python3-venv python3-pip \
    build-essential libxslt-dev libzip-dev libldap2-dev \
    libsasl2-dev libssl-dev libjpeg-dev zlib1g-dev \
    graphviz default-libmysqlclient-dev

# Install additional packages for Odoo
sudo apt install -y libpq-dev npm
```

### 4️⃣ Clone Repository & Setup Virtual Environment

```bash
# Navigate to your workspace
cd ~/workspace

# Clone repository
git clone <YOUR_GITHUB_REPO_URL> odoo-project
cd odoo-project

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip setuptools wheel

# Install Python dependencies
pip install -r setup/requirements.txt
```

### 5️⃣ Configure Odoo

```bash
# Copy template config
mkdir -p ~/.config/odoo
cp setup/odoo.conf.template ~/.config/odoo/odoo.conf

# Edit konfigurasi sesuai environment Anda
nano ~/.config/odoo/odoo.conf
```

**Edit file config dengan parameter berikut:**

```ini
[options]
db_host = localhost
db_port = 5432
db_user = odoo
db_password = odoo
db_name = odoo
db_template = template0

addons_path = /path/to/project/addons

xmlrpc_port = 8069
dev_mode = all,reload,qweb
log_level = debug
```

### 6️⃣ Initialize Database (First Time Only)

```bash
# Activate virtual environment jika belum
source venv/bin/activate

# Create database dan init modules
odoo -c ~/.config/odoo/odoo.conf -d odoo -i base --no-demo

# Tunggu sampai proses selesai, bisa memakan waktu 5-10 menit
```

---

## ▶️ Running Odoo

### Start Odoo Server

```bash
# Activate virtual environment
source venv/bin/activate

# Run Odoo
odoo -c ~/.config/odoo/odoo.conf -d odoo

# Odoo akan accessible di: http://localhost:8069
```

### Start dengan Development Mode

```bash
odoo -c ~/.config/odoo/odoo.conf -d odoo --dev=all,reload,qweb
```

### Running in Background (Optional)

```bash
# Using nohup
nohup odoo -c ~/.config/odoo/odoo.conf -d odoo > odoo.log 2>&1 &

# Check status
ps aux | grep odoo

# Kill process
pkill -f "odoo"
```

### Create Systemd Service (Optional - For Production)

```bash
# Create service file
sudo nano /etc/systemd/system/odoo.service
```

Tambahkan content:

```ini
[Unit]
Description=Odoo
Requires=postgresql.service
After=postgresql.service

[Service]
Type=simple
SyslogIdentifier=odoo
User=odoo
Group=odoo
ExecStart=/home/odoo/odoo-project/venv/bin/python3 /home/odoo/odoo-project/odoo-bin -c /home/odoo/.config/odoo/odoo.conf
Restart=always
PrivateTmp=true

[Install]
WantedBy=multi-user.target
```

```bash
# Enable dan start service
sudo systemctl daemon-reload
sudo systemctl enable odoo
sudo systemctl start odoo
sudo systemctl status odoo
```

---

## 🔧 Development Workflow

### Activate Virtual Environment

```bash
source venv/bin/activate
```

### Update Custom Modules

```bash
# Setelah edit module Python:
# Restart Odoo server (Ctrl+C lalu jalankan lagi)

# Atau menggunakan Odoo CLI untuk install/update modules
odoo shell -c ~/.config/odoo/odoo.conf -d odoo

# Di dalam shell:
>>> from odoo import api
>>> env = api.Environment(cr, uid, context)
>>> module = env['ir.module.module'].search([('name','=','module_name')])
>>> module.button_immediate_upgrade()
```

### Database Backup

```bash
# Backup database
pg_dump -U odoo -h localhost odoo > backup_$(date +%Y%m%d_%H%M%S).sql

# Restore database
psql -U odoo -h localhost odoo < backup_file.sql
```

### View Logs

```bash
# Real-time logs (jika running on foreground)
# Logs akan terlihat di terminal

# Dari file (jika menggunakan nohup)
tail -f odoo.log
```

---

## 🐛 Troubleshooting

### PostgreSQL Connection Error

```bash
# Verify PostgreSQL is running
sudo systemctl status postgresql

# Check PostgreSQL logs
sudo tail -f /var/log/postgresql/postgresql-15-main.log

# Test connection
psql -U odoo -h localhost -d odoo
```

### Module Not Found Error

```bash
# Ensure addons_path is correct in config
# Check if custom modules exist in addons folder

# Reinstall module
odoo shell -c ~/.config/odoo/odoo.conf -d odoo

# Inside shell:
>>> env['ir.module.module'].search([('name','=','module_name')])
```

### Permission Denied on /var/lib/odoo

```bash
# Create odoo user (if using production setup)
sudo useradd -m -d /var/lib/odoo -s /bin/bash odoo

# Set proper permissions
sudo chown -R odoo:odoo /var/lib/odoo
sudo chown -R odoo:odoo /path/to/project
```

### Port Already in Use

```bash
# Find process using port 8069
sudo lsof -i :8069

# Kill process
sudo kill -9 <PID>

# Or change port in config file
# Change 'xmlrpc_port = 8069' to 'xmlrpc_port = 8070'
```

---

## 📚 Additional Resources

- [Odoo Official Documentation](https://www.odoo.com/documentation/18.0/)
- [Odoo Development Guide](https://www.odoo.com/documentation/18.0/developer/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)

---

## ❓ FAQ

### Bagaimana cara develop module baru?

```bash
# 1. Create folder di addons/
mkdir addons/my_module

# 2. Create files:
# - __init__.py
# - __manifest__.py
# - models/__init__.py
# - models/models.py

# 3. Add ke addons_path jika belum
# 4. Restart Odoo
# 5. Install module dari Odoo UI
```

### Bagaimana deploy di production?

Lihat dokumentasi production di folder `/docs/`

### Port 8069 sudah digunakan, bagaimana?

Edit file config:
```ini
xmlrpc_port = 8070  # Ganti ke port lain
```

---

Last updated: April 2026
