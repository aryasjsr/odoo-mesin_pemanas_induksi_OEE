# Platform Support Summary

Quick reference untuk dukungan setup di berbagai platform.

---

## ✅ Supported Setups

### 🐳 Docker
| OS | Support | Notes |
|----|---------|-------|
| Windows 10/11 | ✅ Full | Requires Docker Desktop |
| macOS | ✅ Full | Works on Intel & Apple Silicon |
| Linux | ✅ Full | All distributions |

**Setup Time**: 5-10 minutes  
**Guide**: [README.md](../README.md#option-1-using-docker-recommended-for-consistency)

### 🐧 Linux Native
| Distro | Support | Version |
|--------|---------|---------|
| Ubuntu | ✅ Full | 22.04 LTS+ |
| Debian | ✅ Full | 11+ |
| CentOS | ⚠️ Partial | 9+ (not tested) |
| Fedora | ⚠️ Partial | (not tested) |

**Setup Time**: 20-30 minutes  
**Guide**: [docs/SETUP_NATIVE_LINUX.md](SETUP_NATIVE_LINUX.md)

### 🪟 Windows Native
| Version | Support | Bit |
|---------|---------|-----|
| Windows 11 | ✅ Full | 64-bit |
| Windows 10 | ✅ Full | 64-bit |
| Windows Server | ⚠️ Partial | Not tested |

**Setup Time**: 30-45 minutes  
**Guide**: [docs/SETUP_NATIVE_WINDOWS.md](SETUP_NATIVE_WINDOWS.md)

---

## 📊 Setup Comparison

| Feature | Docker | Linux Native | Windows Native |
|---------|--------|--------------|---|
| **Windows** | ✅ | ❌ | ✅ |
| **macOS** | ✅ | ❌ | ❌ |
| **Linux** | ✅ | ✅ | ❌ |
| **Setup Time** | 5 min | 20 min | 30 min |
| **IDE Integration** | OK | Good | Excellent |
| **Performance** | Good | Excellent | Excellent |
| **Disk Space** | 30GB | 5GB | 5GB |
| **Database Mgmt** | Easy | Manual | Manual |
| **Team Consistency** | ✅ | ❌ | ❌ |

---

## 🎯 Recommendations

### For Consistent Team Development
**Use**: 🐳 **Docker**
- Team: Mixed OS developers
- Priority: Consistency & easy onboarding

### For Linux-Only Teams
**Use**: 🐧 **Linux Native**
- Team: All Linux developers
- Priority: Performance & native integration

### For Windows-Only Teams
**Use**: 🪟 **Windows Native**
- Team: All Windows developers
- Priority: Performance & IDE integration

### For Mixed Teams (Windows + Linux)
**Option A** (Recommended): 🐳 **Docker for everyone**  
**Option B**: Each dev uses their native setup

---

## 🔄 Switching Between Setups

### From Docker to Linux Native
```bash
# 1. Stop Docker
docker-compose -f setup/docker-compose.yml down

# 2. Export data (optional)
docker-compose -f setup/docker-compose.yml exec db pg_dump -U odoo odoo > backup.sql

# 3. Follow Linux setup
bash docs/SETUP_NATIVE_LINUX.md
```

### From Docker to Windows Native
```bash
# 1. Stop Docker
docker-compose -f setup/docker-compose.yml down

# 2. Export data (optional)
docker-compose -f setup/docker-compose.yml exec db pg_dump -U odoo odoo > backup.sql

# 3. Follow Windows setup
start docs\SETUP_NATIVE_WINDOWS.md
```

### From Linux to Windows Native (or vice versa)
```bash
# On current system:
# 1. Export database
pg_dump -U odoo localhost -d odoo > backup.sql

# 2. Transfer backup file to new machine

# 3. Setup new environment following new platform guide

# 4. Import database
psql -U odoo localhost -d odoo < backup.sql
```

---

## 🐛 Troubleshooting by Platform

### Docker Issues
- **Where**: See [README.md troubleshooting](../README.md)
- **Common**: Port conflicts, image size, Docker service stopped

### Linux Issues
- **Where**: See [docs/SETUP_NATIVE_LINUX.md troubleshooting](SETUP_NATIVE_LINUX.md)
- **Common**: Permission errors, PostgreSQL not running, Python version mismatch

### Windows Issues
- **Where**: See [docs/SETUP_NATIVE_WINDOWS.md troubleshooting](SETUP_NATIVE_WINDOWS.md)
- **Common**: Python not in PATH, PostgreSQL service not running, Visual C++ build tools missing

---

## 📋 Environment Prerequisites Comparison

### Docker Requirements
- Docker Desktop (Windows/macOS) or Docker (Linux)
- Git
- 30GB free disk space

### Linux Native Requirements
- Ubuntu 22.04+ or Debian 11+
- Python 3.10+
- PostgreSQL 15+
- C++ build tools
- 5GB free disk space

### Windows Native Requirements
- Windows 10/11 (64-bit)
- Python 3.10+ (from python.org)
- PostgreSQL 15+
- Visual Studio Build Tools
- Git for Windows
- 5GB free disk space

---

## 🚀 Quick Access Links

| I want to... | Link |
|-------------|------|
| Setup with Docker | [README.md](../README.md#option-1-using-docker-recommended-for-consistency) |
| Setup on Linux | [docs/SETUP_NATIVE_LINUX.md](SETUP_NATIVE_LINUX.md) |
| Setup on Windows | [docs/SETUP_NATIVE_WINDOWS.md](SETUP_NATIVE_WINDOWS.md) |
| Compare setups | [docs/SETUP_GUIDE_MAPPING.md](SETUP_GUIDE_MAPPING.md) |
| See all docs | [docs/DOC_INDEX.md](DOC_INDEX.md) |

---

**Last Updated**: April 2026
