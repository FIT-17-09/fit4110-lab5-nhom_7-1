COMPOSE = docker compose
REPORTS_DIR = reports

.PHONY: install lint build compose-up compose-down logs test-compose

install:
	npm install

lint:
	npx spectral lint contracts/*.yaml

build:
	$(COMPOSE) build --no-cache

compose-up:
	$(COMPOSE) up -d --build

compose-down:
	$(COMPOSE) down

logs:
	$(COMPOSE) logs -f

test-compose:
	@echo "Run Newman/Postman tests against http://localhost:${APP_PORT:-8000}"
	@command -v npx >/dev/null 2>&1 || (echo "Node/npm not found; install Node.js to run tests"; exit 1)
	@mkdir -p $(REPORTS_DIR)
	npm run test:compose