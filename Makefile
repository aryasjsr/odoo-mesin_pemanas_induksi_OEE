.PHONY: help docker-up docker-down docker-logs docker-shell \
        linux-setup linux-run linux-stop linux-clean \
        windows-setup windows-run windows-clean \
        backup restore lint test clean

help:
	@echo "Odoo Project - Development Commands"
	@echo ""
	@echo "Docker Commands:"
	@echo "  make docker-up          Start Docker containers"
	@echo "  make docker-down        Stop Docker containers"
	@echo "  make docker-logs        Show Docker logs"
	@echo "  make docker-shell       Open Odoo container shell"
	@echo "  make docker-db          Open PostgreSQL shell in container"
	@echo ""
	@echo "Linux Native Commands:"
	@echo "  make linux-setup        Setup Python environment (one-time)"
	@echo "  make linux-run          Start Odoo server"
	@echo "  make linux-stop         Stop Odoo server"
	@echo "  make linux-shell        Open Odoo shell"
	@echo ""
	@echo "Windows Native Commands (use PowerShell):"
	@echo "  make windows-setup      Setup Python environment (one-time)"
	@echo "  make windows-run        Start Odoo server"
	@echo "  make windows-clean      Clean pycache and logs"
	@echo ""
	@echo "Backup/Restore:"
	@echo "  make backup             Backup Odoo database"
	@echo "  make restore FILE=...   Restore database from backup"
	@echo ""
	@echo "Utilities:"
	@echo "  make clean              Clean pycache and logs"
	@echo "  make lint               Check Python code style"
	@echo "  make test               Run tests (if available)"
	@echo ""

# ============================================================================
# DOCKER COMMANDS
# ============================================================================

docker-up:
	@docker-compose -f setup/docker-compose.yml up -d
	@echo "Odoo started! Access at http://localhost:8069"
	@echo "Login: admin / admin"
	@sleep 3
	@make docker-logs

docker-down:
	@docker-compose -f setup/docker-compose.yml down
	@echo "Odoo stopped!"

docker-logs:
	@docker-compose -f setup/docker-compose.yml logs -f web

docker-shell:
	@docker-compose -f setup/docker-compose.yml exec web bash

docker-db:
	@docker-compose -f setup/docker-compose.yml exec db psql -U odoo odoo

docker-restart:
	@docker-compose -f setup/docker-compose.yml restart web
	@echo "Odoo restarted!"

docker-build:
	@docker-compose -f setup/docker-compose.yml build --no-cache
	@echo "Docker images rebuilt!"

# ============================================================================
# LINUX NATIVE COMMANDS
# ============================================================================

linux-setup:
	@echo "Setting up Python environment..."
	@python3 -m venv venv
	@. venv/bin/activate && pip install --upgrade pip
	@. venv/bin/activate && pip install -r setup/requirements.txt
	@echo "Virtual environment created! Activate with: source venv/bin/activate"
	@echo "Don't forget to setup ~/.config/odoo/odoo.conf"

linux-run:
	@. venv/bin/activate && odoo -c ~/.config/odoo/odoo.conf -d odoo

linux-dev:
	@. venv/bin/activate && odoo -c ~/.config/odoo/odoo.conf -d odoo --dev=all,reload,qweb

linux-shell:
	@. venv/bin/activate && odoo shell -c ~/.config/odoo/odoo.conf -d odoo

linux-stop:
	@pkill -f "odoo"
	@echo "Odoo stopped!"

linux-clean:
	@rm -rf __pycache__ .pytest_cache
	@find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	@echo "Cache cleaned!"

# ============================================================================
# WINDOWS NATIVE COMMANDS
# ============================================================================

windows-setup:
	@echo "Setting up Python environment for Windows..."
	@python -m venv venv
	@venv\Scripts\activate && python -m pip install --upgrade pip
	@venv\Scripts\activate && pip install -r setup\requirements.txt
	@echo "Virtual environment created! Activate with: venv\Scripts\activate"
	@echo "Then configure: copy config\.env.example .env && edit .env"
	@echo "Read docs\SETUP_NATIVE_WINDOWS.md for details"

windows-run:
	@echo "Starting Odoo server..."
	@venv\Scripts\activate && odoo -c %USERPROFILE%\.odoorc --dev=all

windows-dev:
	@venv\Scripts\activate && odoo -c %USERPROFILE%\.odoorc --dev=all,reload,qweb

windows-clean:
	@echo "Cleaning pycache..."
	@for /d /r . %d in (__pycache__) do @if exist "%d" rmdir /s /q "%d" 2>nul
	@for /r . %f in (*.pyc) do @del /q "%f" 2>nul
	@echo "Cache cleaned!"

# ============================================================================
# BACKUP & RESTORE
# ============================================================================

backup:
	@mkdir -p backups
	@timestamp=$$(date +"%Y%m%d_%H%M%S"); \
	docker-compose -f setup/docker-compose.yml exec -T db pg_dump -U odoo odoo > "backups/odoo_$$timestamp.sql"; \
	echo "Backup created: backups/odoo_$$timestamp.sql"

backup-linux:
	@mkdir -p backups
	@timestamp=$$(date +"%Y%m%d_%H%M%S"); \
	pg_dump -U odoo -h localhost odoo > "backups/odoo_$$timestamp.sql"; \
	echo "Backup created: backups/odoo_$$timestamp.sql"

restore:
	@if [ -z "$(FILE)" ]; then \
		echo "Usage: make restore FILE=backups/odoo_20240401_120000.sql"; \
		exit 1; \
	fi
	@echo "Restoring from $(FILE)..."
	@docker-compose -f setup/docker-compose.yml exec -T db psql -U odoo odoo < "$(FILE)"
	@echo "Database restored!"

restore-linux:
	@if [ -z "$(FILE)" ]; then \
		echo "Usage: make restore-linux FILE=backups/odoo_20240401_120000.sql"; \
		exit 1; \
	fi
	@echo "Restoring from $(FILE)..."
	@psql -U odoo -h localhost odoo < "$(FILE)"
	@echo "Database restored!"

# ============================================================================
# UTILITIES
# ============================================================================

clean:
	@find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	@find . -type f -name "*.pyc" -delete
	@find . -type f -name "*.pyo" -delete
	@find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	@echo "Cache and compiled files cleaned!"

lint:
	@echo "Checking Python code style..."
	@. venv/bin/activate && python -m pylint addons/ --disable=all --enable=E 2>/dev/null || true

test:
	@echo "Tests configuration not yet added."
	@echo "Add pytest configuration when ready."

# ============================================================================
# ENV SETUP
# ============================================================================

env:
	@if [ ! -f .env ]; then \
		cp config/.env.example .env; \
		echo ".env file created! Edit if needed."; \
	else \
		echo ".env already exists"; \
	fi

# ============================================================================
# INFO
# ============================================================================

info:
	@echo "=== Odoo Project Info ==="
	@echo ""
	@echo "Project: Odoo Enterprise Automation"
	@echo "Version: 18.0"
	@echo ""
	@echo "Setup Environment:"
	@if [ -f .env ]; then \
		echo "✓ .env file exists"; \
	else \
		echo "✗ .env file missing (run: make env)"; \
	fi
	@if [ -d "venv" ]; then \
		echo "✓ Python venv exists"; \
	else \
		echo "✗ Python venv missing (run: make linux-setup)"; \
	fi
	@echo ""
	@echo "Docker Status:"
	@docker-compose -f setup/docker-compose.yml ps 2>/dev/null || echo "Docker not running"
	@echo ""
	@echo "Run 'make help' for all available commands"
