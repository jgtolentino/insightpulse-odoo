.PHONY: dev down prod init freeze backup restore test release sha

dev:
	docker compose -f docker/docker-compose.yml up -d

down:
	docker compose -f docker/docker-compose.yml down -v

prod:
	docker compose -f docker/prod.compose.yml up -d

init:
	bash scripts/install_modules.sh

freeze:
	bash scripts/freeze-urls.sh

backup:
	bash scripts/backup-db.sh

restore:
	bash scripts/restore-db.sh

test:
	pytest -q

release:
	VER=$$(git describe --tags --always); \
	rm -rf dist && mkdir -p dist/insightpulse-odoo-$$VER/config; \
	rsync -a --delete addons/custom/ dist/insightpulse-odoo-$$VER/addons/custom/; \
	rsync -a --delete addons/oca/    dist/insightpulse-odoo-$$VER/addons/oca/; \
	rsync -a deploy/                 dist/insightpulse-odoo-$$VER/deploy/; \
	rsync -a scripts/                dist/insightpulse-odoo-$$VER/scripts/; \
	rsync -a sql/                    dist/insightpulse-odoo-$$VER/sql/; \
	install -m 0644 config/.env.example dist/insightpulse-odoo-$$VER/config/.env.example; \
	cp README.md dist/insightpulse-odoo-$$VER/README-INSTALL.md; \
	cd dist && zip -r insightpulse-odoo-$$VER.zip insightpulse-odoo-$$VER

sha:
	cd dist && sha256sum *.zip > SHA256SUMS
