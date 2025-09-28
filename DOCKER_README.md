# 🐳 Dockerización y CI/CD Pipeline - Data Governance

Este documento describe la implementación completa de containerización y automatización para el proyecto de gobierno de datos de DeAcero.

## 📋 Tabla de Contenidos

- [Arquitectura Docker](#-arquitectura-docker)
- [CI/CD Pipeline](#-cicd-pipeline)
- [Comandos Útiles](#-comandos-útiles)
- [Configuración](#-configuración)
- [Monitoreo y Logs](#-monitoreo-y-logs)
- [Seguridad](#-seguridad)
- [Troubleshooting](#-troubleshooting)

## 🏗️ Arquitectura Docker

### Imagen Base
- **Base**: `python:3.11-slim`
- **Usuario**: `datagovernance` (no-root)
- **Directorio**: `/app`
- **Health Check**: Incluido

### Servicios Disponibles

| Servicio | Descripción | Comando |
|----------|-------------|---------|
| `data-governance` | Servicio base | `catalog_automation.py` |
| `catalog-automation` | Solo catalogación | `catalog_automation.py` |
| `data-masking` | Solo enmascaramiento | `data_masking.py` |
| `full-pipeline` | Pipeline completo | Ambos scripts |

### Volúmenes
- **Credenciales**: `./deacero-datagov-sa-key.json:/app/credentials/service-account-key.json:ro`
- **Configuración**: `./config:/app/config:ro`
- **Scripts**: `./scripts:/app/scripts:ro`
- **Logs**: `logs:/app/logs`

## 🚀 CI/CD Pipeline

### Workflows Implementados

#### 1. **Build & Deploy** (`.github/workflows/docker-build-deploy.yml`)
- **Trigger**: Push a `main`, `develop`, `daislas`
- **Jobs**:
  - `validate`: Validación de sintaxis y configuración
  - `build`: Construcción multi-arquitectura (AMD64, ARM64)
  - `integration-test`: Pruebas de integración
  - `deploy`: Deployment automático (solo en `main`)
  - `notify`: Notificaciones de estado

#### 2. **Security Scan** (`.github/workflows/security-scan.yml`)
- **Trigger**: Push, PRs, schedule semanal
- **Jobs**:
  - `code-security`: Bandit, Safety, pip-audit
  - `code-quality`: flake8, pylint, black, isort, mypy
  - `docker-security`: Trivy vulnerability scan
  - `docker-lint`: hadolint Dockerfile analysis
  - `security-summary`: Reporte consolidado

#### 3. **Dependabot** (`.github/dependabot.yml`)
- **Python**: Actualizaciones semanales de dependencias
- **GitHub Actions**: Actualizaciones de actions
- **Docker**: Actualizaciones de imagen base

### Features del Pipeline
- ✅ **Multi-arquitectura**: AMD64 y ARM64
- ✅ **Cache inteligente**: GitHub Actions cache
- ✅ **Security scanning**: Vulnerabilidades y calidad
- ✅ **Artifact attestation**: Provenance verification
- ✅ **Container registry**: GitHub Container Registry
- ✅ **Automated dependencies**: Dependabot updates

## 🛠️ Comandos Útiles

### Make Commands
```bash
# Ver todos los comandos disponibles
make help

# Setup de desarrollo
make dev-setup

# Construcción y testing
make build
make test
make security

# Docker Compose
make compose-up
make compose-logs
make compose-down

# Deployment
make deploy
make deploy-catalog
make deploy-full

# Limpieza
make clean
make clean-all
```

### Docker Commands
```bash
# Construcción
docker build -f docker/Dockerfile -t deacero-data-governance:latest .

# Ejecución
docker run --rm deacero-data-governance:latest

# Con credenciales
docker run --rm -v ./deacero-datagov-sa-key.json:/app/credentials/service-account-key.json:ro deacero-data-governance:latest

# Shell interactivo
docker run --rm -it deacero-data-governance:latest /bin/bash
```

### Docker Compose Commands
```bash
# Construcción
docker-compose build

# Iniciar servicios
docker-compose up -d

# Logs
docker-compose logs -f

# Servicios específicos
docker-compose up catalog-automation
docker-compose up data-masking
docker-compose up full-pipeline

# Detener
docker-compose down
```

## ⚙️ Configuración

### Variables de Entorno
```bash
# Requeridas
GOOGLE_CLOUD_PROJECT=your-project-id
GOOGLE_APPLICATION_CREDENTIALS=/app/credentials/service-account-key.json

# Opcionales
LOG_LEVEL=INFO
BIGQUERY_DATASET=stackoverflow_sample
BIGQUERY_LOCATION=US
```

### Archivos de Configuración
- `docker/Dockerfile`: Definición de imagen
- `docker-compose.yml`: Orquestación de servicios
- `.dockerignore`: Exclusiones de build
- `requirements.txt`: Dependencias Python

### Scripts de Deployment
- `deploy.sh`: Script de deployment automatizado
- `cleanup.sh`: Limpieza de recursos
- `Makefile`: Comandos de desarrollo

## 📊 Monitoreo y Logs

### Health Checks
```bash
# Verificar salud
make health

# Health check manual
docker run --rm deacero-data-governance:latest python -c "print('Health OK')"
```

### Logs
```bash
# Logs de compose
docker-compose logs -f

# Logs específicos
docker-compose logs -f catalog-automation
docker-compose logs -f data-masking

# Logs de contenedor específico
docker logs deacero-catalog-automation
```

### Monitoreo
```bash
# Estado de servicios
make compose-status

# Recursos
make monitor

# Contenedores activos
make ps
```

## 🔒 Seguridad

### Medidas Implementadas
- ✅ **Usuario no-root**: Contenedor ejecuta como `datagovernance`
- ✅ **Secrets management**: Credenciales por volúmenes
- ✅ **Vulnerability scanning**: Trivy y security tools
- ✅ **Minimal base image**: `python:3.11-slim`
- ✅ **Read-only mounts**: Configuración y credenciales
- ✅ **Network isolation**: Red dedicada

### Security Scanning
```bash
# Scan completo
make security

# Individual tools
bandit -r scripts/
safety check
pip-audit
```

### Best Practices
1. **Credenciales**: Nunca en imagen, solo por volúmenes
2. **Updates**: Dependabot mantiene dependencias actualizadas
3. **Scanning**: CI/CD incluye scans automáticos
4. **Permissions**: Principio de menor privilegio

## 🚨 Troubleshooting

### Problemas Comunes

#### 1. Error de credenciales
```bash
Error: Could not find service account key
```
**Solución**: Verificar que existe `deacero-datagov-sa-key.json`

#### 2. Error de permisos
```bash
Permission denied
```
**Solución**: 
```bash
chmod +x deploy.sh cleanup.sh
```

#### 3. Error de construcción
```bash
Failed to solve: process did not complete successfully
```
**Solución**: 
```bash
make clean-all
make build
```

#### 4. Contenedor no inicia
```bash
# Verificar logs
docker-compose logs service-name

# Debug interactivo
make shell
```

### Comandos de Debug
```bash
# Verificar configuración
make check-config

# Estado detallado
docker-compose ps
docker system df

# Limpieza selectiva
make clean-images
```

### Logs de Debug
```bash
# Construcción con debug
docker build --progress=plain -f docker/Dockerfile .

# Compose con logs detallados
docker-compose up --verbose
```

## 📈 Métricas y Rendimiento

### Tamaños de Imagen
- **Imagen base**: ~45MB (python:3.11-slim)
- **Con dependencias**: ~200MB
- **Cache layers**: Optimizado para rebuild rápido

### Tiempos de Construcción
- **Primera construcción**: ~3-5 minutos
- **Rebuilds con cache**: ~30-60 segundos
- **CI/CD pipeline**: ~5-8 minutos

### Recursos Recomendados
- **CPU**: 1-2 cores
- **RAM**: 1-2GB
- **Disco**: 500MB-1GB

---

## 🎯 Próximos Pasos

1. **Kubernetes**: Deployment en cluster K8s
2. **Helm Charts**: Templates para deployment
3. **Prometheus**: Métricas y monitoreo
4. **ArgoCD**: GitOps deployment
5. **RBAC**: Control de acceso granular

---

*Generado para el proyecto Data Governance de DeAcero - Septiembre 2025*
