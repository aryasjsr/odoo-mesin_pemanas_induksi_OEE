# Odoo Enterprise Automation Project

Project Odoo dengan custom modules untuk Manufacturing Resource Planning (MRP), Quality Management, dan Shop Floor Integration.

---

## 📋 Project Overview

Platform otomasi enterprise berbasis Odoo 18.0 dengan fitur-fitur custom:
- **MRP OEE** - OEE (Overall Equipment Effectiveness) tracking untuk manufacturing
- **MRP OEE Modbus** - Integrasi Modbus untuk industrial devices
- **MRP Quality** - Quality management untuk production
- **MRP Shop Floor** - Shop floor management dan real-time monitoring
- **Web Brand Custom** - Custom branding untuk web interface

---

## 🏗️ Project Structure

```
.
├── addons/                           # Custom Odoo modules
│   ├── mrp_oee_custom/              # OEE tracking module
│   ├── mrp_oee_modbus/              # Modbus integration
│   ├── mrp_quality_custom/          # Quality management
│   ├── mrp_shopfloor_custom/        # Shop floor features
│   └── web_brand_custom/            # Web branding
├── docs/                             # Documentation
├── setup/                            # Setup files & configs
│   ├── requirements.txt              # Python dependencies
│   ├── odoo.conf.template            # Odoo config template
│   └── docker-compose.yml            # Docker configuration
├── config/                           # Configuration templates
│   └── .env.example                  # Environment variables template
├── .gitignore                        # Git ignore rules
└── README.md                         # This file
```

---

## 🚀 Quick Start

**Not sure which setup to choose?** → Read [docs/SETUP_GUIDE_MAPPING.md](docs/SETUP_GUIDE_MAPPING.md) for a quick decision matrix!

### Option 1: Using Docker (Recommended for consistency)

#### Prerequisites
- Docker & Docker Compose installed

#### Steps

```bash
# 1. Clone repository
git clone https://github.com/aryasjsr/odoo-mesin_pemanas_induksi_OEE.git
cd odoo-mesin_pemanas_induksi_OEE

# 2. Create .env file
cp config/.env.example .env
# Edit .env dengan credentials Anda

# 3. Start services
docker-compose -f setup/docker-compose.yml up -d

# 4. Wait for initialization (~2-5 minutes)
docker-compose -f setup/docker-compose.yml logs -f

# 5. Access Odoo
# Browser: http://localhost:8069
# Username: admin
# Password: (dari .env ADMIN_PASSWORD)
```

#### Stop Services

```bash
docker-compose -f setup/docker-compose.yml down
```

---

### Option 2: Native Linux Setup (For Linux Developers without Docker)

#### Prerequisites
- Ubuntu 22.04+ atau Debian-based Linux
- Python 3.10+
- PostgreSQL 15+
- Git

#### Steps

```bash
# 1. Clone repository
git clone https://github.com/aryasjsr/odoo-mesin_pemanas_induksi_OEE.git
cd odoo-project

# 2. Follow detailed guide
cat docs/SETUP_NATIVE_LINUX.md

# 3. Quick summary:
python3 -m venv venv
source venv/bin/activate
pip install -r setup/requirements.txt
```

**📖 Full guide**: [docs/SETUP_NATIVE_LINUX.md](docs/SETUP_NATIVE_LINUX.md)

---

### Option 3: Native Windows Setup (For Windows Developers without Docker)

#### Prerequisites
- Windows 10/11 (64-bit)
- Python 3.10+ (from python.org)
- PostgreSQL 15+ (Windows installer)
- Git for Windows
- Visual Studio Build Tools (for C++ compilation)

#### Steps

```bash
# 1. Clone repository
git clone https://github.com/aryasjsr/odoo-mesin_pemanas_induksi_OEE.git
cd odoo-mesin_pemanas_induksi_OEE

# 2. Follow detailed guide
start docs\SETUP_NATIVE_WINDOWS.md

# 3. Quick summary:
python -m venv venv
venv\Scripts\activate
pip install -r setup\requirements.txt
cp setup/odoo.conf.template ~/.config/odoo/odoo.conf
# Edit config file sesuai kebutuhan
odoo -c ~/.config/odoo/odoo.conf -d odoo
```

Untuk panduan lengkap, lihat [SETUP_NATIVE_LINUX.md](docs/SETUP_NATIVE_LINUX.md)

---

## 👥 Development Guide

### For Docker Users

```bash
# 1. Modify custom modules
# Edit files di addons/

# 2. Restart container untuk reload
docker-compose -f setup/docker-compose.yml restart web

# 3. Check logs
docker-compose -f setup/docker-compose.yml logs -f web
```

### For Native Linux Users

```bash
# 1. Activate environment
source venv/bin/activate

# 2. Modify custom modules
# Edit files di addons/

# 3. Restart server
# Stop current process (Ctrl+C)
# Rerun: odoo -c ~/.config/odoo/odoo.conf -d odoo

# 4. Use dev mode untuk auto-reload
odoo -c ~/.config/odoo/odoo.conf -d odoo --dev=all,reload,qweb
```

---

## 📦 Custom Modules

### MRP OEE Custom (`mrp_oee_custom/`)
Tracking Overall Equipment Effectiveness dengan API endpoints.

**Key Features:**
- OEE calculation
- REST API untuk OEE data
- Dashboard integration

**API Endpoints:**
- `GET /api/oee/status` - Get current OEE status
- `POST /api/oee/record` - Record OEE data

---

### MRP OEE Modbus (`mrp_oee_modbus/`)
Integrasi industrial devices via Modbus protocol.

**Key Features:**
- Modbus device connection
- Real-time data collection
- Data synchronization dengan Odoo

---

### MRP Quality Custom (`mrp_quality_custom/`)
Quality control dan management untuk production.

**Key Features:**
- Quality checks
- Defect tracking
- Quality reports

---

### MRP Shop Floor Custom (`mrp_shopfloor_custom/`)
Shop floor monitoring dan management dalam real-time.

**Key Features:**
- Real-time production status
- Worker assignment
- Production tracking

---

### Web Brand Custom (`web_brand_custom/`)
Custom branding untuk Odoo web interface.

---

## 🔧 Configuration

### Docker Environment Variables

File: `config/.env.example`

```env
DB_HOST=db
DB_PORT=5432
DB_USER=odoo
DB_PASSWORD=odoo_password
ODOO_PORT=8069
ADMIN_PASSWORD=admin_password
```

### Odoo Configuration

File: `setup/odoo.conf.template`

Key settings:
- `db_host` - Database host
- `db_user` - Database user
- `addons_path` - Custom modules path
- `xmlrpc_port` - Odoo server port
- `dev_mode` - Development mode settings

---

## 📚 Documentation

- [SETUP_NATIVE_LINUX.md](docs/SETUP_NATIVE_LINUX.md) - Native Linux setup guide
- [AddedFeature_Modbus.md](docs/AddedFeature_Modbus.md) - Modbus integration details
- [implementation_plan.md](docs/implementation_plan.md) - Project implementation plan
- [brandGuidelines.md](docs/brandGuidelines.md) - Branding guidelines
- [walkthrough.md](docs/walkthrough.md) - Project walkthrough

---

## 🔄 Git Workflow

### Clone Repository

```bash
git clone https://github.com/aryasjsr/odoo-mesin_pemanas_induksi_OEE.git
cd odoo-mesin_pemanas_induksi_OEE
```

### Branch Strategy

```bash
# Create feature branch
git checkout -b feature/your-feature-name

# Make changes
# Commit
git add .
git commit -m "feat: describe your changes"

# Push
git push origin feature/your-feature-name

# Create Pull Request
```

### Files NOT in Repository (Ignored)

```
- db-data/          (PostgreSQL data)
- odoo-data/        (Odoo filestore)
- .env              (Sensitive data)
- __pycache__/      (Compiled files)
- *.log             (Log files)
- venv/             (Virtual environment)
```

---

## 🐛 Troubleshooting

### Docker Issues

```bash
# Check container status
docker-compose -f setup/docker-compose.yml ps

# View logs
docker-compose -f setup/docker-compose.yml logs web

# Rebuild containers
docker-compose -f setup/docker-compose.yml build --no-cache

# Clean up
docker-compose -f setup/docker-compose.yml down -v
```

### Native Linux Issues

Lihat section **Troubleshooting** di [SETUP_NATIVE_LINUX.md](docs/SETUP_NATIVE_LINUX.md)

---

## 📋 Database Management

### Backup Database

```bash
# Docker
docker-compose -f setup/docker-compose.yml exec -T db pg_dump -U odoo odoo > backup.sql

# Native Linux
pg_dump -U odoo -h localhost odoo > backup.sql
```

### Restore Database

```bash
# Docker
docker-compose -f setup/docker-compose.yml exec -T db psql -U odoo odoo < backup.sql

# Native Linux
psql -U odoo -h localhost odoo < backup.sql
```

---

## 👨‍💼 Developer Information

### Adding New Developer

1. **For Docker User:**
   ```bash
   git clone https://github.com/aryasjsr/odoo-mesin_pemanas_induksi_OEE.git
   cd odoo-mesin_pemanas_induksi_OEE
   cp config/.env.example .env
   # Edit .env
   docker-compose -f setup/docker-compose.yml up -d
   ```

2. **For Native Linux User:**
   - Follow [SETUP_NATIVE_LINUX.md](docs/SETUP_NATIVE_LINUX.md)

---

## 📞 Support & Contact

Untuk pertanyaan atau issues:
- Buat GitHub Issues
- Check dokumentasi di `/docs/`
- Hubungi project maintainers

---

## 📄 License

[Specify your license here]

---

## 📝 Changelog

### Version 1.0 (Current)
- Initial setup dengan 5 custom modules
- Docker & Native Linux support
- Modbus integration untuk OEE
- Quality management module
- Shop floor monitoring

---

**Last updated:** April 2026
