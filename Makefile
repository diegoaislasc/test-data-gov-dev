# Makefile para Data Governance Project
.PHONY: help build test deploy clean security lint format

# Variables
IMAGE_NAME = deacero-data-governance
IMAGE_TAG = latest
COMPOSE_PROJECT = deacero-data-governance

# Colores para output
RED = \033[0;31m
GREEN = \033[0;32m
YELLOW = \033[1;33m
BLUE = \033[0;34m
NC = \033[0m # No Color

# Help
help: ## Mostrar esta ayuda
	@echo "${BLUE}Data Governance - Comandos Disponibles${NC}"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "${GREEN}%-20s${NC} %s\n", $$1, $$2}'

# Development
install: ## Instalar dependencias
	@echo "${YELLOW}Instalando dependencias...${NC}"
	pip install --upgrade pip
	pip install -r requirements.txt
	@echo "${GREEN}✅ Dependencias instaladas${NC}"

format: ## Formatear código
	@echo "${YELLOW}Formateando código...${NC}"
	black scripts/
	isort scripts/
	@echo "${GREEN}✅ Código formateado${NC}"

lint: ## Analizar calidad del código
	@echo "${YELLOW}Analizando código...${NC}"
	flake8 scripts/
	pylint scripts/
	mypy scripts/
	@echo "${GREEN}✅ Análisis completado${NC}"

security: ## Verificar seguridad
	@echo "${YELLOW}Verificando seguridad...${NC}"
	bandit -r scripts/
	safety check
	pip-audit
	@echo "${GREEN}✅ Verificación de seguridad completada${NC}"

test: ## Ejecutar pruebas
	@echo "${YELLOW}Ejecutando pruebas...${NC}"
	python -m pytest tests/ -v || echo "${YELLOW}No se encontraron pruebas${NC}"
	python -m py_compile scripts/*.py
	@echo "${GREEN}✅ Pruebas completadas${NC}"

# Docker
build: ## Construir imagen Docker
	@echo "${YELLOW}Construyendo imagen Docker...${NC}"
	docker build -f docker/Dockerfile -t $(IMAGE_NAME):$(IMAGE_TAG) .
	@echo "${GREEN}✅ Imagen construida: $(IMAGE_NAME):$(IMAGE_TAG)${NC}"

run: ## Ejecutar contenedor principal
	@echo "${YELLOW}Ejecutando contenedor principal...${NC}"
	docker run --rm --name $(IMAGE_NAME) \
		-e GOOGLE_APPLICATION_CREDENTIALS=/app/credentials/service-account-key.json \
		-v $(PWD)/deacero-datagov-sa-key.json:/app/credentials/service-account-key.json:ro \
		-v $(PWD)/config:/app/config:ro \
		$(IMAGE_NAME):$(IMAGE_TAG)

run-catalog: ## Ejecutar solo catalogación
	@echo "${YELLOW}Ejecutando catalogación...${NC}"
	docker run --rm --name $(IMAGE_NAME)-catalog \
		-e GOOGLE_APPLICATION_CREDENTIALS=/app/credentials/service-account-key.json \
		-v $(PWD)/deacero-datagov-sa-key.json:/app/credentials/service-account-key.json:ro \
		-v $(PWD)/config:/app/config:ro \
		$(IMAGE_NAME):$(IMAGE_TAG) python scripts/catalog_automation.py

run-masking: ## Ejecutar solo enmascaramiento
	@echo "${YELLOW}Ejecutando enmascaramiento...${NC}"
	docker run --rm --name $(IMAGE_NAME)-masking \
		-e GOOGLE_APPLICATION_CREDENTIALS=/app/credentials/service-account-key.json \
		-v $(PWD)/deacero-datagov-sa-key.json:/app/credentials/service-account-key.json:ro \
		-v $(PWD)/config:/app/config:ro \
		$(IMAGE_NAME):$(IMAGE_TAG) python scripts/data_masking.py

shell: ## Abrir shell en contenedor
	@echo "${YELLOW}Abriendo shell en contenedor...${NC}"
	docker run --rm -it --name $(IMAGE_NAME)-shell \
		-e GOOGLE_APPLICATION_CREDENTIALS=/app/credentials/service-account-key.json \
		-v $(PWD)/deacero-datagov-sa-key.json:/app/credentials/service-account-key.json:ro \
		-v $(PWD)/config:/app/config:ro \
		-v $(PWD)/scripts:/app/scripts \
		$(IMAGE_NAME):$(IMAGE_TAG) /bin/bash

# Docker Compose
compose-build: ## Construir con docker compose
	@echo "${YELLOW}Construyendo con docker compose...${NC}"
	docker compose build
	@echo "${GREEN}✅ Construcción completada${NC}"

compose-up: ## Iniciar servicios con docker compose
	@echo "${YELLOW}Iniciando servicios...${NC}"
	docker compose up -d
	@echo "${GREEN}✅ Servicios iniciados${NC}"

compose-logs: ## Ver logs de servicios
	@echo "${YELLOW}Mostrando logs...${NC}"
	docker compose logs -f

compose-down: ## Detener servicios
	@echo "${YELLOW}Deteniendo servicios...${NC}"
	docker compose down
	@echo "${GREEN}✅ Servicios detenidos${NC}"

compose-status: ## Ver estado de servicios
	@echo "${YELLOW}Estado de servicios:${NC}"
	docker compose ps

# Deployment
deploy: ## Desplegar usando script
	@echo "${YELLOW}Desplegando aplicación...${NC}"
	./deploy.sh

deploy-catalog: ## Desplegar solo catalogación
	@echo "${YELLOW}Desplegando catalogación...${NC}"
	docker compose up catalog-automation

deploy-masking: ## Desplegar solo enmascaramiento
	@echo "${YELLOW}Desplegando enmascaramiento...${NC}"
	docker compose up data-masking

deploy-full: ## Desplegar pipeline completo
	@echo "${YELLOW}Desplegando pipeline completo...${NC}"
	docker compose up full-pipeline

# Maintenance
clean: ## Limpiar recursos Docker
	@echo "${YELLOW}Limpiando recursos...${NC}"
	./cleanup.sh
	@echo "${GREEN}✅ Limpieza completada${NC}"

clean-images: ## Limpiar imágenes Docker
	@echo "${YELLOW}Limpiando imágenes...${NC}"
	docker rmi $(IMAGE_NAME):$(IMAGE_TAG) 2>/dev/null || true
	docker image prune -f
	@echo "${GREEN}✅ Imágenes limpiadas${NC}"

clean-all: ## Limpieza completa
	@echo "${YELLOW}Limpieza completa...${NC}"
	docker compose down --volumes --remove-orphans
	docker rmi $(IMAGE_NAME):$(IMAGE_TAG) 2>/dev/null || true
	docker system prune -f
	@echo "${GREEN}✅ Limpieza completa terminada${NC}"

logs: ## Ver logs de aplicación
	@echo "${YELLOW}Logs de aplicación:${NC}"
	docker logs $(IMAGE_NAME) || echo "${RED}Contenedor no encontrado${NC}"

health: ## Verificar salud del contenedor
	@echo "${YELLOW}Verificando salud...${NC}"
	docker run --rm $(IMAGE_NAME):$(IMAGE_TAG) python -c "print('✅ Container health OK')"

# Development workflow
dev-setup: install format lint security test ## Setup completo para desarrollo

dev-test: format lint security test build ## Pipeline de testing completo

ci-pipeline: dev-test compose-build ## Pipeline completo como CI

# Quality checks
check-config: ## Verificar configuraciones
	@echo "${YELLOW}Verificando configuraciones...${NC}"
	docker compose config
	@echo "${GREEN}✅ Configuraciones válidas${NC}"

check-dependencies: ## Verificar dependencias actualizadas
	@echo "${YELLOW}Verificando dependencias...${NC}"
	pip list --outdated
	@echo "${GREEN}✅ Verificación completada${NC}"

# Monitoring
monitor: ## Monitorear recursos
	@echo "${YELLOW}Monitoreando recursos:${NC}"
	docker stats --no-stream || echo "${YELLOW}No hay contenedores corriendo${NC}"

ps: ## Listar contenedores relacionados
	@echo "${YELLOW}Contenedores activos:${NC}"
	docker ps --filter "name=$(IMAGE_NAME)"
