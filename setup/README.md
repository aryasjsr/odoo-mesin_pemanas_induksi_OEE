# Setup Configuration Files

Folder ini berisi configuration files untuk berbagai setup environment.

## 📁 Files Breakdown

### `docker-compose.yml`
- **Untuk**: Docker users (Linux, macOS, Windows dengan Docker Desktop)
- **Fitur**: PostgreSQL + Odoo services, automatic initialization, volume management
- **Usage**: `docker-compose -f setup/docker-compose.yml up -d`

### `requirements.txt`
- **Untuk**: Native Python setup (Linux & Windows)
- **Konten**: Python dependencies untuk Odoo 18.0
- **Usage**: `pip install -r setup/requirements.txt`

### `odoo.conf.template`
- **Untuk**: Native setup (Linux & Windows)
- **Konten**: Odoo configuration template
- **Usage**: 
  - Linux: `cp odoo.conf.template ~/.config/odoo/odoo.conf`
  - Windows: `copy odoo.conf.template %USERPROFILE%\.odoorc`

---

## 🚀 Quick Reference

| Environment | Command | Guide |
|-------------|---------|-------|
| **Docker** | `docker-compose -f setup/docker-compose.yml up -d` | [README.md](../README.md) |
| **Linux Native** | `pip install -r setup/requirements.txt` | [docs/SETUP_NATIVE_LINUX.md](../docs/SETUP_NATIVE_LINUX.md) |
| **Windows Native** | `pip install -r setup/requirements.txt` | [docs/SETUP_NATIVE_WINDOWS.md](../docs/SETUP_NATIVE_WINDOWS.md) |

---

## 📝 Configuration Files Location

After setup, config files akan berada di:

```
# Docker
docker-compose.yml (in this folder)

# Linux Native
~/.config/odoo/odoo.conf
~/.odoorc

# Windows Native
%USERPROFILE%\.odoorc
C:\Users\<YourUsername>\.odoorc
```

---

## 💾 Dependency Versions

Current `requirements.txt` includes:
- Odoo 18.0
- psycopg2-binary 2.9.9 (PostgreSQL adapter)
- python-dateutil 2.8.2
- requests 2.31.0

Update dengan: `pip install --upgrade -r setup/requirements.txt`

---

For detailed setup instructions, see:
- Docker: [README.md](../README.md#option-1-using-docker-recommended-for-consistency)
- Linux: [docs/SETUP_NATIVE_LINUX.md](../docs/SETUP_NATIVE_LINUX.md)
- Windows: [docs/SETUP_NATIVE_WINDOWS.md](../docs/SETUP_NATIVE_WINDOWS.md)
