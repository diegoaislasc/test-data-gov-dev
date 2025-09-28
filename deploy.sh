#!/bin/bash

# Script de deployment para Data Governance
set -e

echo "🚀 Iniciando deployment de Data Governance..."

# Verificar que Docker esté corriendo
if ! docker info > /dev/null 2>&1; then
    echo "❌ Error: Docker no está corriendo. Por favor inicia Docker Desktop."
    exit 1
fi

# Verificar que existe el archivo de credenciales
if [ ! -f "deacero-datagov-sa-key.json" ]; then
    echo "❌ Error: Archivo de credenciales no encontrado (deacero-datagov-sa-key.json)"
    exit 1
fi

# Configurar variables de entorno por defecto si no existen
export GOOGLE_CLOUD_PROJECT=${GOOGLE_CLOUD_PROJECT:-"deacero-data-governance"}

echo "📦 Construyendo imagen Docker..."
docker compose build --no-cache

echo "🔄 Iniciando servicios..."
docker compose up -d

echo "📊 Estado de los contenedores:"
docker compose ps

echo "📋 Para ver logs:"
echo "  docker compose logs -f data-governance"
echo "  docker compose logs -f catalog-automation"
echo "  docker compose logs -f data-masking"

echo "🛑 Para detener:"
echo "  docker compose down"

echo "✅ Deployment completado!"
