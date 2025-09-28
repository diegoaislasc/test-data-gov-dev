#!/bin/bash

# Script de limpieza para Data Governance
echo "🧹 Limpiando recursos de Data Governance..."

# Detener y remover contenedores
echo "🛑 Deteniendo contenedores..."
docker-compose down

# Remover imagen si existe
echo "🗑️ Removiendo imagen Docker..."
docker rmi deacero-data-governance:latest 2>/dev/null || echo "Imagen no encontrada"

# Limpiar volúmenes huérfanos
echo "🔧 Limpiando volúmenes..."
docker volume prune -f

# Limpiar network
echo "🌐 Limpiando networks..."
docker network prune -f

# Limpiar imágenes dangling
echo "🖼️ Limpiando imágenes huérfanas..."
docker image prune -f

echo "✅ Limpieza completada!"
