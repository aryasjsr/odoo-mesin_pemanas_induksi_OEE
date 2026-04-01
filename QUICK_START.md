# Quick Start Guide

Panduan cepat untuk memulai development dengan project ini.

> 💡 **First time?** Check [docs/DOC_INDEX.md](docs/DOC_INDEX.md) for full documentation map or [docs/SETUP_GUIDE_MAPPING.md](docs/SETUP_GUIDE_MAPPING.md) to choose the right setup for you!

---

## ⚡ 5-Minute Setup (Docker)

### Requirements
- Docker installed
- Git installed
- ~30GB disk space (for images & data)

### Steps

```bash
# 1. Clone
git clone <REPO_URL> && cd odoo-project

# 2. Copy env file
cp config/.env.example .env

# 3. Edit .env (optional, gunakan default jika ingin)
# nano .env

# 4. Start services
docker-compose -f setup/docker-compose.yml up -d

# 5. Wait 2-3 minutes for initialization
docker-compose -f setup/docker-compose.yml logs -f web

# 6. Open browser
# http://localhost:8069
# Login: admin / admin
```

**Stop services:**
```bash
docker-compose -f setup/docker-compose.yml down
```

---

## ⚡ Quick Setup (Native Linux)

### Requirements
- Ubuntu 22.04+ or Debian
- Python 3.10+
- PostgreSQL 15+
- ~5GB disk space

### Steps

```bash
# Read detailed guide
cat docs/SETUP_NATIVE_LINUX.md
```

---

## ⚡ Quick Setup (Native Windows)

### Requirements
- Windows 10/11 (64-bit)
- Python 3.10+ (python.org)
- PostgreSQL 15+
- Visual Studio Build Tools
- ~5GB disk space

### Steps

```bash
# Read detailed guide
start docs\SETUP_NATIVE_WINDOWS.md

# OR open in text editor:
type docs\SETUP_NATIVE_WINDOWS.md
```
sudo -u postgres psql -c "CREATE USER odoo WITH PASSWORD 'odoo' CREATEDB;"

# 3. Clone & setup
git clone <REPO_URL> && cd odoo-project
python3 -m venv venv && source venv/bin/activate
pip install -r setup/requirements.txt

# 4. Copy config
mkdir -p ~/.config/odoo
cp setup/odoo.conf.template ~/.config/odoo/odoo.conf

# 5. Edit config (change db_host to localhost)
nano ~/.config/odoo/odoo.conf

# 6. Run
odoo -c ~/.config/odoo/odoo.conf -d odoo
```

**Browser:** http://localhost:8069  
**Login:** admin / admin

---

## 📝 First Changes

### Edit custom module

```bash
# 1. Find module
cd addons/mrp_oee_custom/models/

# 2. Edit Python file
nano my_model.py

# 3. Restart Odoo (Docker: restart, Linux: Ctrl+C then rerun)

# 4. In Odoo UI: Apps > Update module list > Install/Update module
```

### Create new file

```bash
# Example: Add new model
# addons/mrp_oee_custom/models/new_model.py

from odoo import models, fields

class NewModel(models.Model):
    _name = 'new.model'
    _description = 'My New Model'
    
    name = fields.Char(required=True)
    value = fields.Float()
```

Then update `__init__.py`:
```python
from . import new_model
```

---

## 🔄 Git Workflow (3 Steps)

```bash
# 1. Create branch
git checkout -b feature/my-feature

# 2. Make changes
# Edit files...
git add .
git commit -m "feat: add my feature"

# 3. Push & PR
git push origin feature/my-feature
# Create PR on GitHub
```

---

## 🆘 Common Issues

### Port 8069 already in use (Docker)
```bash
# Change in .env or docker-compose.yml
ODOO_PORT=8070
```

### Database connection error (Linux)
```bash
# Check PostgreSQL
sudo systemctl status postgresql

# Check credentials in ~/.config/odoo/odoo.conf
```

### Module not found
```bash
# 1. Verify addons folder exists
# 2. Restart Odoo
# 3. In Odoo: Apps > Update module list
# 4. Search & install module
```

---

## 📚 Learn More

- Full README: [README.md](../README.md)
- Linux setup: [SETUP_NATIVE_LINUX.md](../docs/SETUP_NATIVE_LINUX.md)
- Contributing: [CONTRIBUTING.md](../CONTRIBUTING.md)

---

## 💡 Tips

- **Dev Mode:** Auto-reload on file changes (both Docker & Linux)
- **Logs:** Check logs when things break
- **Backup:** Always backup before major changes
- **Ask:** Check docs or ask maintainers if stuck

---

**Ready to code? Let's go!** 🚀

