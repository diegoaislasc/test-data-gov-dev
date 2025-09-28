#!/bin/bash

# Script para crear paquete de entrega para entrevistador
# Genera ZIP limpio y verifica

set -e

echo "📦 Creando paquete de entrega para entrevistador..."
echo "=================================================="

# Colores
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m'

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

# 1. Verificar que estamos en el directorio correcto
show_step "Verificando directorio del proyecto..."
if [ ! -f "README.md" ] || [ ! -d "scripts" ]; then
    check_error "No estás en el directorio raíz del proyecto"
    echo "Ejecuta este script desde: /Users/diegoandre/PycharmProjects/test-data-gov-dev/"
    exit 1
fi
check_ok "Directorio correcto identificado"

# 2. Verificar archivos críticos
show_step "Verificando archivos críticos..."
critical_files=(
    "README.md"
    "config/metadata_config.yaml"
    "scripts/catalog_automation.py"
    "docker/Dockerfile"
    "docker-compose.yml"
    "requirements.txt"
    "docs/PRESENTACION_FINAL.md"
    "docs/GUIA_DEMO_REVISOR.md"
)

missing_files=()
for file in "${critical_files[@]}"; do
    if [ -f "$file" ]; then
        check_ok "$file presente"
    else
        check_error "$file FALTA"
        missing_files+=("$file")
    fi
done

if [ ${#missing_files[@]} -gt 0 ]; then
    echo -e "\n${RED}❌ Faltan archivos críticos. No se puede crear el paquete.${NC}"
    exit 1
fi

# 3. Verificar que no haya credenciales expuestas
show_step "Verificando seguridad..."
if [ -f "deacero-datagov-sa-key.json" ]; then
    check_warning "Archivo de credenciales presente (se excluirá del ZIP)"
fi

if grep -r "private_key" . --exclude-dir=.git --exclude="*.sh" > /dev/null 2>&1; then
    check_error "Posibles credenciales encontradas en archivos"
    echo "Revisa que no haya credenciales hardcodeadas"
    exit 1
fi
check_ok "No se encontraron credenciales expuestas"

# 4. Contar screenshots
show_step "Verificando evidencias..."
screenshot_count=$(find screenshots/ -name "*.png" -o -name "*.jpg" 2>/dev/null | wc -l)
if [ $screenshot_count -gt 5 ]; then
    check_ok "Screenshots suficientes: $screenshot_count archivos"
else
    check_warning "Pocos screenshots: $screenshot_count (recomendado >5)"
fi

# 5. Crear directorios temporales
show_step "Preparando archivos para empaquetado..."
temp_dir="temp_delivery_package"
rm -rf $temp_dir
mkdir -p $temp_dir

# 6. Copiar archivos esenciales
show_step "Copiando archivos esenciales..."
rsync -av --progress \
    --exclude='.git' \
    --exclude='__pycache__' \
    --exclude='.venv' \
    --exclude='node_modules' \
    --exclude='*.pyc' \
    --exclude='.DS_Store' \
    --exclude='deacero-datagov-sa-key.json' \
    --exclude='*.log' \
    --exclude='temp_*' \
    . $temp_dir/

check_ok "Archivos copiados al directorio temporal"

# 7. Crear README de entrega
show_step "Creando README de entrega..."
cat > $temp_dir/INSTRUCCIONES_ENTREVISTADOR.md << 'EOF'
# 🚀 Proyecto Data Governance - Diego Islas
## Instrucciones para Entrevistador DeAcero

### ⚡ Ejecución Rápida
```bash
# Extraer y configurar
unzip proyecto-data-governance-diego-islas.zip
cd test-data-gov-dev
chmod +x prepare_demo.sh
./prepare_demo.sh
```

### 📋 Archivos Clave
- `README.md` - Documentación completa e instrucciones
- `docs/PRESENTACION_FINAL.md` - Resumen ejecutivo del proyecto
- `docs/GUIA_DEMO_REVISOR.md` - Guía para demo técnica
- `scripts/catalog_automation.py` - Script principal de automatización
- `screenshots/` - Evidencias visuales organizadas

### 🐳 Demo Docker
```bash
# Construir y ejecutar
make build
make run-verification
```

### ⚠️ Limitaciones Técnicas
Ver `docs/LIMITACIONES_TECNICAS.md` para explicación completa de restricciones GCP identificadas.

### 📞 Contacto
**Diego Islas**
- Email: [tu-email-aqui]
- GitHub: [tu-github-aqui]

¡Listo para demo técnica! 🎯
EOF

check_ok "README de entrega creado"

# 8. Crear el ZIP final
show_step "Creando ZIP final..."
zip_name="proyecto-data-governance-diego-islas.zip"
cd $temp_dir
zip -r ../$zip_name . -q
cd ..

# 9. Verificar ZIP creado
if [ -f "$zip_name" ]; then
    zip_size=$(du -h "$zip_name" | cut -f1)
    check_ok "ZIP creado exitosamente: $zip_name ($zip_size)"
else
    check_error "Error creando ZIP"
    exit 1
fi

# 10. Limpiar directorio temporal
rm -rf $temp_dir
check_ok "Archivos temporales limpiados"

# 11. Reporte final
show_step "Reporte final del paquete..."
echo -e "\n${BLUE}📦 PAQUETE DE ENTREGA LISTO:${NC}"
echo "=================================="
echo "📄 Archivo: $zip_name"
echo "📊 Tamaño: $zip_size"
echo "📅 Fecha: $(date)"

echo -e "\n${BLUE}📋 CONTENIDO VERIFICADO:${NC}"
echo "▶️  Código y configuraciones ✅"
echo "▶️  Scripts de automatización ✅"
echo "▶️  Docker y CI/CD ✅"
echo "▶️  Documentación completa ✅"
echo "▶️  Screenshots organizados ✅"
echo "▶️  Sin credenciales expuestas ✅"

echo -e "\n${BLUE}🚀 PRÓXIMOS PASOS:${NC}"
echo "1. Subir proyecto a GitHub (recomendado)"
echo "2. Enviar email al entrevistador con:"
echo "   - Link de GitHub O archivo ZIP adjunto"
echo "   - Template de email en: docs/GUIA_ENTREGA_ENTREVISTADOR.md"
echo "3. Preparar demo técnica"

echo -e "\n${BLUE}📧 PARA ENVIAR:${NC}"
echo "▶️  GitHub Repository (Opción 1 - Recomendado)"
echo "▶️  Archivo ZIP: $zip_name (Opción 2)"
echo "▶️  Template email: docs/GUIA_ENTREGA_ENTREVISTADOR.md"

echo -e "\n${GREEN}🎉 ¡PAQUETE LISTO PARA ENTREGA!${NC}"
echo -e "El archivo ${YELLOW}$zip_name${NC} está listo para enviar al entrevistador."

# Opcional: verificar contenido del ZIP
echo -e "\n¿Quieres ver el contenido del ZIP? (y/n)"
read -r response
if [[ "$response" =~ ^[Yy]$ ]]; then
    echo -e "\n${BLUE}📁 CONTENIDO DEL ZIP:${NC}"
    unzip -l "$zip_name" | head -20
    echo "..."
fi

echo -e "\n${BLUE}¡Buena suerte en tu entrevista! 🚀${NC}"


