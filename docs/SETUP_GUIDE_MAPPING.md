# Platform Setup Guide Mapping

Panduan cepat untuk developer dalam memilih setup option yang sesuai.

---

## 🎯 Choose Your Setup

### 📦 **Option 1: Docker** (Recommended)

**Best for:**
- ✅ Teams dengan mixed OS environments (Windows, macOS, Linux)
- ✅ Consistent setup across team
- ✅ No local database installation needed
- ✅ Isolated environment

**Pros:**
- Setup cepat (5 menit)
- Konsisten di semua developer
- Mudah cleanup (cukup `docker-compose down`)
- Tidak perlu install PostgreSQL, Python system-wide

**Cons:**
- Requires Docker installed
- Uses ~30GB disk space (images + data)
- Slightly slower performance pada Windows/macOS

**Platform Support:** Windows, macOS, Linux

**📖 Guide:** [README.md](README.md#-quick-start)

---

### 🐧 **Option 2: Native Linux**

**Best for:**
- ✅ Linux-only development teams
- ✅ Direct hardware access
- ✅ No Docker overhead
- ✅ Native Linux development

**Pros:**
- Better performance
- Direct system integration
- Familiar Linux development workflow
- Smaller footprint (~5GB)

**Cons:**
- Linux only
- Need to install PostgreSQL + Python manually
- Database management manual
- Potential OS-specific issues

**Platform Support:** Linux (Ubuntu 22.04+, Debian, etc.)

**📖 Guide:** [docs/SETUP_NATIVE_LINUX.md](docs/SETUP_NATIVE_LINUX.md)

**⚡ Quick Start:**
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r setup/requirements.txt
# Then follow docs/SETUP_NATIVE_LINUX.md
```

---

### 🪟 **Option 3: Native Windows**

**Best for:**
- ✅ Windows-only development teams
- ✅ Native Windows development environment
- ✅ VSCode / JetBrains IDEs integration
- ✅ Direct hardware access

**Pros:**
- Native Windows development
- Good IDE integration
- Better performance than Docker on Windows
- Smaller footprint (~5GB)

**Cons:**
- Windows only
- Need to install PostgreSQL + Python manually
- Database management manual
- Windows-specific path issues

**Platform Support:** Windows 10/11 (64-bit)

**📖 Guide:** [docs/SETUP_NATIVE_WINDOWS.md](docs/SETUP_NATIVE_WINDOWS.md)

**⚡ Quick Start:**
```bash
python -m venv venv
venv\Scripts\activate
pip install -r setup\requirements.txt
# Then follow docs/SETUP_NATIVE_WINDOWS.md
```

---

## 📋 Quick Decision Matrix

| Criteria | Docker | Linux Native | Windows Native |
|----------|--------|--------------|----------------|
| **Setup Time** | 5 min | 20 min | 30 min |
| **Performance** | Good | Excellent | Excellent |
| **Disk Space** | 30GB | 5GB | 5GB |
| **Cross-Platform** | ✅ Yes | ❌ No | ❌ No |
| **IDE Integration** | OK | Good | Excellent |
| **Database Mgmt** | Easy | Manual | Manual |
| **Windows Support** | ✅ | ❌ | ✅ |
| **Linux Support** | ✅ | ✅ | ❌ |
| **macOS Support** | ✅ | ❌ | ❌ |

---

## 🔄 Team Collaboration

### Mixed Environment Teams

Jika team memiliki developer dengan OS berbeda:

**Option A: Semua pakai Docker** (Recommended)
- Consistency terjamin
- Setup sama untuk semua
- Mudah troubleshoot

**Option B: Hybrid Setup**
```
Developer A (Windows) → Native Windows
Developer B (Linux)   → Native Linux
Developer C (macOS)   → Docker

✅ Supported!
```

**Key Tips:**
1. Use `.gitignore` ✅ (semua setup)
2. Share config templates ✅ (`.env.example`)
3. Document differences ✅ (in respective guides)
4. Use Git for collaboration ✅

---

## 🆘 Troubleshooting

### "Setup failed, which option should I choose?"

1. **Windows user?** → Try Docker first, if issues → Native Windows
2. **Linux user?** → Try Native Linux first, if issues → Docker
3. **macOS user?** → Use Docker
4. **Team dev?** → Recommend Docker for consistency

### "I'm switching from one setup to another"

**Clean up first:**
```bash
# Docker
docker-compose -f setup/docker-compose.yml down
docker volume prune

# Native
rm -rf venv/
rm -rf ~/.odoorc
rm -rf ~/.config/odoo/

# Windows Native
rmdir /s venv
del %USERPROFILE%\.odoorc
```

Then follow new setup guide.

---

## 📚 Additional Resources

- **Odoo Documentation**: https://www.odoo.com/documentation/
- **PostgreSQL Docs**: https://www.postgresql.org/docs/
- **Python Virtual Environments**: https://docs.python.org/3/tutorial/venv.html
- **Docker Guide**: https://docs.docker.com/

---

## 📞 Need Help?

| Issue | Solution |
|-------|----------|
| Docker issues | See README.md troubleshooting |
| Linux issues | See docs/SETUP_NATIVE_LINUX.md troubleshooting |
| Windows issues | See docs/SETUP_NATIVE_WINDOWS.md troubleshooting |
| Other | Ask team lead / create GitHub issue |

---

**Last Updated**: April 2026
