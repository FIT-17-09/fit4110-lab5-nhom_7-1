COMPOSE=docker compose

.PHONY: compose-up compose-down logs build test-compose

compose-up:
	$(COMPOSE) up -d --build

compose-down:
	$(COMPOSE) down

logs:
	$(COMPOSE) logs -f

build:
	$(COMPOSE) build --no-cache

test-compose:
	@echo "Run Newman/Postman tests against http://localhost:${APP_PORT}"
	@which npx || (echo "Node/npm not found; install Node.js to run tests"; exit 1)
	# ensure reports dir exists
	@mkdir -p reports
	# run newman and export reporters (JUnit XML + HTML)
	npx newman run postman/FIT4110_lab05_collection.json -e postman/environments/FIT4110_lab05_local.postman_environment.json --reporters cli,junit,html --reporter-junit-export reports/newman-lab05-compose.xml --reporter-html-export reports/newman-lab05-compose.html
.PHONY: install lint build run compose-up compose-down logs test-compose

# Install Node dependencies for Prism/Spectral/Newman
install:
	npm install

# Lint OpenAPI contracts with Spectral
lint:
	npx spectral lint contracts/*.yaml

# Build Docker image for API only
build:
	docker build -t fit4110/iot-ingestion:lab05 .

# Run API container standalone (not via compose)
run:
	docker run --rm --name fit4110-api-lab05 -p 8000:8000 --env-file .env.example fit4110/iot-ingestion:lab05

# Compose commands
compose-up:
	docker compose up -d --build

compose-down:
	docker compose down

logs:
	docker compose logs -f

# Run Newman tests on compose stack
test-compose:
	npm run test:compose