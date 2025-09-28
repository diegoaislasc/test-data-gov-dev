#!/bin/bash

# Script de preparación para demo del proyecto Data Governance
# Ejecutar antes de hacer la demo con un revisor externo

set -e

echo "🎬 Preparando demo de Data Governance - DeAcero"
echo "================================================="

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Función para mostrar pasos
show_step() {
    echo -e "\n${BLUE}📋 $1${NC}"
}

# Función para verificaciones
check_ok() {
    echo -e "${GREEN}✅ $1${NC}"
}

check_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

check_error() {
    echo -e "${RED}❌ $1${NC}"
}

# 1. Verificar Docker
show_step "Verificando Docker..."
if docker info > /dev/null 2>&1; then
    check_ok "Docker está corriendo"
    docker --version
else
    check_error "Docker no está corriendo. Por favor inicia Docker Desktop."
    exit 1
fi

# 2. Verificar estructura del proyecto
show_step "Verificando estructura del proyecto..."

required_files=(
    "scripts/catalog_automation.py"
    "scripts/verification_checklist.py"
    "config/metadata_config.yaml"
    "docker/Dockerfile"
    "docker-compose.yml"
    "Makefile"
    "requirements.txt"
)

missing_files=()

for file in "${required_files[@]}"; do
    if [ -f "$file" ]; then
        check_ok "$file existe"
    else
        check_error "$file NO ENCONTRADO"
        missing_files+=("$file")
    fi
done

if [ ${#missing_files[@]} -gt 0 ]; then
    echo -e "\n${RED}❌ Faltan archivos críticos. Demo no puede continuar.${NC}"
    exit 1
fi

# 3. Verificar credenciales
show_step "Verificando credenciales..."
if [ -f "deacero-datagov-sa-key.json" ]; then
    check_ok "Archivo de credenciales encontrado"
    # Verificar que es un JSON válido
    if python3 -c "import json; json.load(open('deacero-datagov-sa-key.json'))" 2>/dev/null; then
        check_ok "Archivo de credenciales es JSON válido"
    else
        check_warning "Archivo de credenciales no es JSON válido"
    fi
else
    check_warning "Archivo de credenciales no encontrado (demo funcionará en modo limitado)"
fi

# 4. Verificar variables de entorno
show_step "Verificando variables de entorno..."
if [ -n "$GOOGLE_CLOUD_PROJECT" ]; then
    check_ok "GOOGLE_CLOUD_PROJECT configurado: $GOOGLE_CLOUD_PROJECT"
else
    check_warning "GOOGLE_CLOUD_PROJECT no configurado"
    echo "  Ejecuta: export GOOGLE_CLOUD_PROJECT='tu-project-id'"
fi

if [ -n "$GOOGLE_APPLICATION_CREDENTIALS" ]; then
    check_ok "GOOGLE_APPLICATION_CREDENTIALS configurado"
else
    check_warning "GOOGLE_APPLICATION_CREDENTIALS no configurado"
    echo "  Ejecuta: export GOOGLE_APPLICATION_CREDENTIALS='$(pwd)/deacero-datagov-sa-key.json'"
fi

# 5. Verificar dependencias Python
show_step "Verificando dependencias Python..."
if command -v python3 &> /dev/null; then
    check_ok "Python3 disponible: $(python3 --version)"
    
    # Verificar dependencias críticas
    if python3 -c "import yaml" 2>/dev/null; then
        check_ok "PyYAML disponible"
    else
        check_warning "PyYAML no disponible (se instalará en Docker)"
    fi
else
    check_warning "Python3 no encontrado en PATH"
fi

# 6. Construir imagen Docker para demo
show_step "Construyendo imagen Docker para demo..."
echo "Esto puede tomar algunos minutos la primera vez..."

if docker build -f docker/Dockerfile -t deacero-data-governance:latest . > /tmp/docker_build.log 2>&1; then
    check_ok "Imagen Docker construida exitosamente"
else
    check_error "Error construyendo imagen Docker"
    echo "Ver logs en: /tmp/docker_build.log"
    tail -20 /tmp/docker_build.log
    exit 1
fi

# 7. Probar imagen Docker
show_step "Probando imagen Docker..."
if docker run --rm deacero-data-governance:latest python -c "print('✅ Container health OK')" > /dev/null 2>&1; then
    check_ok "Contenedor funciona correctamente"
else
    check_error "Error ejecutando contenedor"
    exit 1
fi

# 8. Verificar docker-compose
show_step "Verificando docker-compose..."
if docker compose config > /dev/null 2>&1; then
    check_ok "docker-compose.yml es válido"
else
    check_error "Error en docker-compose.yml"
    exit 1
fi

# 9. Preparar comandos de demo
show_step "Preparando comandos de demo..."

cat > /tmp/demo_commands.txt << 'EOF'
# 🎬 Comandos para Demo - Data Governance DeAcero

## 1. Mostrar estructura del proyecto
tree -L 2 -I '__pycache__|*.pyc'

## 2. Ver configuración
cat config/metadata_config.yaml

## 3. Ver script principal (primeras 30 líneas)
head -30 scripts/catalog_automation.py

## 4. Ver Dockerfile
cat docker/Dockerfile

## 5. Verificar servicios Docker
docker compose config --services

## 6. Construir y ejecutar verificación
make run-verification

## 7. Ver logs
docker compose logs verification

## 8. Entrar al contenedor (opcional)
make shell

## 9. Limpiar después de demo
make clean
EOF

check_ok "Comandos de demo preparados en /tmp/demo_commands.txt"

# 10. Verificación final
show_step "Verificación final de preparación..."

echo -e "\n${BLUE}📊 RESUMEN DE PREPARACIÓN:${NC}"
echo "================================"

if [ -f "deacero-datagov-sa-key.json" ] && [ -n "$GOOGLE_CLOUD_PROJECT" ]; then
    echo -e "🟢 ${GREEN}MODO COMPLETO${NC} - Credenciales válidas, demo completa disponible"
    demo_mode="COMPLETO"
else
    echo -e "🟡 ${YELLOW}MODO LIMITADO${NC} - Demo de estructura y contenedores sin conexión a GCP"
    demo_mode="LIMITADO"
fi

echo -e "\n${BLUE}🎯 CHECKLIST PRE-DEMO:${NC}"
echo "▶️  Docker funcionando ✅"
echo "▶️  Imagen construida ✅"
echo "▶️  Proyecto estructurado ✅"
echo "▶️  Comandos preparados ✅"

echo -e "\n${BLUE}📋 PRÓXIMOS PASOS:${NC}"
echo "1. Revisar la guía: docs/GUIA_DEMO_REVISOR.md"
echo "2. Practicar los comandos: cat /tmp/demo_commands.txt"
echo "3. Preparar screenshots de GCP Console"
echo "4. Revisar limitaciones técnicas: docs/LIMITACIONES_TECNICAS.md"
echo "5. ¡Ejecutar la demo!"

echo -e "\n${YELLOW}⚠️  NOTA IMPORTANTE:${NC}"
echo "El proyecto incluye 2 limitaciones técnicas de GCP que son RESTRICCIONES"
echo "DE PLATAFORMA, no errores de implementación:"
echo "• Datasets públicos no permiten assets de Dataplex"
echo "• Policy Rules requieren Google Cloud Organization"
echo "Ver documentación completa en: docs/LIMITACIONES_TECNICAS.md"

echo -e "\n${BLUE}⚡ COMANDOS RÁPIDOS PARA LA DEMO:${NC}"
echo "make run-verification    # Ejecutar verificación"
echo "make shell              # Entrar al contenedor"
echo "make clean              # Limpiar después"

echo -e "\n${GREEN}🎉 ¡DEMO LISTA PARA EJECUTAR!${NC}"
echo -e "Modo de demo: ${demo_mode}"
echo -e "Tiempo estimado: 15-20 minutos"

# Opcional: abrir guía de demo
if command -v open &> /dev/null; then
    echo -e "\n¿Abrir guía de demo? (y/n)"
    read -r response
    if [[ "$response" =~ ^[Yy]$ ]]; then
        open docs/GUIA_DEMO_REVISOR.md 2>/dev/null || echo "Abrir manualmente: docs/GUIA_DEMO_REVISOR.md"
    fi
fi

echo -e "\n${BLUE}¡Buena suerte con tu demo! 🚀${NC}"
