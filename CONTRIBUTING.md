# Contributing Guide

Panduan untuk kontributor yang ingin berkontribusi pada project Odoo Enterprise Automation.

---

## 📋 Before You Start

1. **Choose your environment** - Pick one:
   - 🐳 Docker: See [README.md - Option 1](README.md#option-1-using-docker-recommended-for-consistency)
   - 🐧 Linux Native: See [docs/SETUP_NATIVE_LINUX.md](docs/SETUP_NATIVE_LINUX.md)
   - 🪟 Windows Native: See [docs/SETUP_NATIVE_WINDOWS.md](docs/SETUP_NATIVE_WINDOWS.md)
   - 🤔 Not sure? See [docs/SETUP_GUIDE_MAPPING.md](docs/SETUP_GUIDE_MAPPING.md)

2. **Fork repository** - Buat fork repo di GitHub Anda

3. **Clone repository** - `git clone https://github.com/aryasjsr/odoo-mesin_pemanas_induksi_OEE.git`

4. **Create branch** - Buat branch untuk fitur/fix Anda

---

## 🔄 Workflow

### 1. Create Feature Branch

```bash
git checkout -b feature/FEATURE-NAME
# atau untuk bugfix:
git checkout -b bugfix/BUG-NAME
```

**Branch naming convention:**
- `feature/short-description` - Fitur baru
- `bugfix/short-description` - Bug fix
- `docs/short-description` - Dokumentasi
- `refactor/short-description` - Refactoring

---

### 2. Make Changes

**Guidelines:**
- ✅ Follow Odoo development standards
- ✅ Write clean, readable code
- ✅ Add docstrings untuk functions/classes
- ✅ Test changes sebelum commit

**Example: Adding New Feature**

```python
# models/my_model.py

class MyModel(models.Model):
    """Description dari model ini.
    
    Lorem ipsum dolor sit amet...
    """
    _name = 'my.model'
    _description = 'My Model'
    
    name = fields.Char(string='Name', required=True)
    
    def my_method(self):
        """Deskripsi method.
        
        Returns:
            str: Return value description
        """
        # Code here
        return result
```

---

### 3. Commit Changes

**Commit message format:**

```bash
git add .
git commit -m "type: description

Optional longer explanation here.
- Point 1
- Point 2
"
```

**Type:**
- `feat:` - New feature
- `fix:` - Bug fix
- `docs:` - Documentation
- `refactor:` - Code refactoring
- `test:` - Adding tests
- `chore:` - Maintenance

**Examples:**
```bash
git commit -m "feat: add OEE calculation for workcenter"
git commit -m "fix: resolve Modbus connection timeout issue"
git commit -m "docs: update native Linux setup guide"
```

---

### 4. Push & Create Pull Request

```bash
# Push branch
git push origin feature/FEATURE-NAME

# Create Pull Request di GitHub
```

**PR Description Template:**

```markdown
## Description
Jelaskan perubahan yang Anda buat.

## Type of Change
- [ ] New feature
- [ ] Bug fix
- [ ] Breaking change
- [ ] Documentation update

## How to Test
Jelaskan cara testing:
1. Step 1
2. Step 2

## Checklist
- [ ] Code follows style guidelines
- [ ] Documentation updated
- [ ] No breaking changes
- [ ] Tested locally
```

---

## 🧪 Testing

### Manual Testing

```bash
# 1. Activate environment
source venv/bin/activate  # Linux
# atau
venv\Scripts\activate  # Windows

# 2. Restart Odoo
# Ctrl+C lalu rerun

# 3. Test di Odoo UI
# Navigate ke module yang diubah
```

### Module Installation

```bash
# Jika membuat module baru:

# 1. Ensure folder structure:
addons/
└── my_module/
    ├── __init__.py
    ├── __manifest__.py
    ├── models/
    ├── views/
    └── security/

# 2. Dalam __init__.py:
from . import models

# 3. Dalam __manifest__.py:
{
    'name': 'My Module',
    'version': '18.0.1.0.0',
    'category': 'Manufacturing',
    'summary': 'Module description',
    'depends': ['base', 'mrp'],
    'data': [
        'security/ir.model.access.csv',
        'views/my_model_views.xml',
    ],
    'installable': True,
}

# 4. Restart Odoo & install module dari UI
```

---

## 📐 Code Standards

### Python Code Style

**Follow PEP 8:**

```python
# Good
class WorkcenterOEE(models.Model):
    _name = 'workcenter.oee'
    
    def calculate_oee(self):
        """Calculate OEE for this workcenter."""
        return (availability * performance * quality) / 100

# Bad
class WorkcenterOEE(models.Model):
    _name = 'workcenter.oee'
    def calculate_oee(self):
        return (a*b*c)/100
```

### XML (Views) Standard

```xml
<odoo>
    <data>
        <record id="view_my_model_form" model="ir.ui.view">
            <field name="name">my.model.form</field>
            <field name="model">my.model</field>
            <field name="arch" type="xml">
                <form>
                    <sheet>
                        <group>
                            <field name="name"/>
                        </group>
                    </sheet>
                </form>
            </field>
        </record>
    </data>
</odoo>
```

### Security (CSV)

```csv
id,name,model_id:id,group_id:id,perm_read,perm_write,perm_create,perm_unlink
access_my_model_user,my.model user,model_my_model,base.group_user,1,1,1,0
access_my_model_manager,my.model manager,model_my_model,base.group_system,1,1,1,1
```

---

## 📚 Documentation Requirements

Setiap PR harus include:

1. **Code comments** - Untuk logic yang kompleks
2. **Docstrings** - Untuk functions/classes
3. **README update** - Jika ada feature baru
4. **API documentation** - Jika ada API endpoints

---

## ✅ Pre-Submission Checklist

- [ ] Code tested locally
- [ ] No syntax errors
- [ ] Follows code style guide
- [ ] Documentation updated
- [ ] No breaking changes
- [ ] Commit messages are clear
- [ ] Branch updated dengan main
- [ ] All tasks completed

---

## 🚫 What NOT to Do

❌ Don't commit:
- Database files (db-data/)
- Odoo filestore (odoo-data/)
- .env files dengan credentials
- __pycache__ folders
- Log files
- Virtual environment files

❌ Don't:
- Force push ke main branch
- Commit secrets/passwords
- Make huge commits (split into logical chunks)
- Skip documentation
- Skip testing

---

## 📞 Questions?

- Check existing documentation di `/docs/`
- Review similar commits di Git history
- Ask in PR comments
- Contact maintainers

---

## 🎉 Thank You!

Terima kasih telah berkontribusi pada project ini!

---

**Last updated:** April 2026
