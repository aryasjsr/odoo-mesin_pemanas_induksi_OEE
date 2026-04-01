# 📚 Documentation Index

Panduan lengkap semua dokumentasi project Odoo Enterprise Automation.

---

## 🚀 Getting Started

**New to project?** Start here:

1. **[README.md](README.md)** - Project overview & quick start
2. **[QUICK_START.md](QUICK_START.md)** - Setup in 5-30 minutes
3. **[docs/SETUP_GUIDE_MAPPING.md](docs/SETUP_GUIDE_MAPPING.md)** - Choose your setup option

---

## 📖 Setup Guides (Choose One)

### For Docker Users
- **File**: [README.md - Option 1](README.md#option-1-using-docker-recommended-for-consistency)
- **Time**: 5-10 minutes
- **Best for**: Consistent team setups
- **Command**: `docker-compose -f setup/docker-compose.yml up -d`

### For Linux Developers (Native)
- **File**: [docs/SETUP_NATIVE_LINUX.md](docs/SETUP_NATIVE_LINUX.md)
- **Time**: 20-30 minutes
- **Best for**: Linux-only teams
- **Command**: `python3 -m venv venv && pip install -r setup/requirements.txt`

### For Windows Developers (Native)
- **File**: [docs/SETUP_NATIVE_WINDOWS.md](docs/SETUP_NATIVE_WINDOWS.md)
- **Time**: 30-45 minutes
- **Best for**: Windows developers
- **Command**: `python -m venv venv && pip install -r setup\requirements.txt`

---

## 📁 Configuration Files

### Setup Folder
- **File**: [setup/README.md](setup/README.md)
- **Contains**:
  - `docker-compose.yml` - Docker configuration
  - `requirements.txt` - Python dependencies
  - `odoo.conf.template` - Odoo config template

### Config Folder
- **File**: [config/.env.example](config/.env.example)
- **Contains**: Environment variables template

---

## 👥 Development Guides

### For Contributors
- **File**: [CONTRIBUTING.md](CONTRIBUTING.md)
- **Topics**:
  - Workflow (branching, commits, PRs)
  - Code standards & conventions
  - Testing guidelines
  - Commit message format

### For Team Collaboration
- **File**: [docs/SETUP_GUIDE_MAPPING.md](docs/SETUP_GUIDE_MAPPING.md)
- **Topics**:
  - Setup comparison matrix
  - Team collaboration tips
  - Switching between setups
  - Troubleshooting by platform

---

## 🛠️ Common Tasks

### Setup Project
```bash
# Use one of:
docker-compose -f setup/docker-compose.yml up -d    # Docker
source venv/bin/activate && pip install -r setup/requirements.txt  # Linux
venv\Scripts\activate && pip install -r setup\requirements.txt     # Windows
```

### Run Development Server
```bash
# Docker
docker-compose -f setup/docker-compose.yml logs -f web

# Linux
source venv/bin/activate
odoo -c ~/.odoorc --dev=all

# Windows
venv\Scripts\activate
odoo -c %USERPROFILE%\.odoorc --dev=all
```

### Run Available Commands
```bash
make help       # Shows all available make commands
```

### Access Odoo
- **URL**: http://localhost:8069
- **Default Login**: admin / admin

---

## 📊 Project Files Tree

```
odoo-project/
├── README.md                          # Main documentation
├── QUICK_START.md                     # Quick setup guide
├── CONTRIBUTING.md                    # Contributor guide
├── Makefile                           # Development commands
├── .gitignore                         # Git ignore rules
│
├── addons/                            # Custom modules
│   ├── mrp_oee_custom/
│   ├── mrp_oee_modbus/
│   ├── mrp_quality_custom/
│   ├── mrp_shopfloor_custom/
│   └── web_brand_custom/
│
├── docs/                              # Documentation
│   ├── SETUP_NATIVE_LINUX.md         # Linux setup
│   ├── SETUP_NATIVE_WINDOWS.md       # Windows setup
│   ├── SETUP_GUIDE_MAPPING.md        # Setup comparison
│   ├── DOC_INDEX.md                  # This file
│   └── ...
│
├── setup/                             # Configuration files
│   ├── README.md                      # Setup folder guide
│   ├── docker-compose.yml
│   ├── requirements.txt
│   └── odoo.conf.template
│
├── config/                            # Config templates
│   └── .env.example
│
├── db-data/                           # Database (local only)
└── odoo-data/                         # Odoo data (local only)
```

---

## 🔍 Quick Search

| I want to... | Go to... |
|------------- |----------|
| **Setup project quickly** | [QUICK_START.md](QUICK_START.md) |
| **Setup with Docker** | [README.md - Option 1](README.md#option-1-using-docker-recommended-for-consistency) |
| **Setup on Linux (native)** | [docs/SETUP_NATIVE_LINUX.md](docs/SETUP_NATIVE_LINUX.md) |
| **Setup on Windows (native)** | [docs/SETUP_NATIVE_WINDOWS.md](docs/SETUP_NATIVE_WINDOWS.md) |
| **Choose setup platform** | [docs/SETUP_GUIDE_MAPPING.md](docs/SETUP_GUIDE_MAPPING.md) |
| **Contribute to project** | [CONTRIBUTING.md](CONTRIBUTING.md) |
| **Understand project** | [README.md](README.md) |
| **See all make commands** | `make help` or [Makefile](Makefile) |
| **Configure environment** | [config/.env.example](config/.env.example) |
| **Fix setup issues** | See troubleshooting in respective setup guide |

---

## ❓ FAQ

### Q: Which setup should I use?
**A**: See [docs/SETUP_GUIDE_MAPPING.md](docs/SETUP_GUIDE_MAPPING.md) - it has a decision matrix!

### Q: How long does setup take?
**A**:
- Docker: 5-10 minutes
- Linux Native: 20-30 minutes
- Windows Native: 30-45 minutes

### Q: I'm getting setup errors
**A**: Search in your platform's setup guide troubleshooting section:
- Docker: [README.md](README.md)
- Linux: [docs/SETUP_NATIVE_LINUX.md](docs/SETUP_NATIVE_LINUX.md)
- Windows: [docs/SETUP_NATIVE_WINDOWS.md](docs/SETUP_NATIVE_WINDOWS.md)

### Q: Can I use other setups after Docker?
**A**: Yes! See [docs/SETUP_GUIDE_MAPPING.md#-team-collaboration](docs/SETUP_GUIDE_MAPPING.md#-team-collaboration) for cleanup instructions.

### Q: How do I contribute?
**A**: Read [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

---

## 📞 Support & Contacts

- **Project Issues**: Create GitHub issue
- **Setup Help**: Check respective setup guide
- **General Questions**: Ask team lead
- **Module Specific Issues**: Check module README in `addons/`

---

## 🔗 Related Links

- **Odoo Documentation**: https://www.odoo.com/documentation/
- **PostgreSQL Docs**: https://www.postgresql.org/docs/
- **Python Docs**: https://docs.python.org/3/
- **Docker Docs**: https://docs.docker.com/

---

**Last Updated**: April 2026  
**Version**: 1.0
