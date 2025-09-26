#!/usr/bin/env python3
"""
Script de verificación final para la prueba técnica DeAcero
Valida que todos los entregables estén completos
"""

import os
import yaml
import logging
from pathlib import Path

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class DeliverableChecker:
    """Verificador de entregables para la prueba técnica"""
    
    def __init__(self, project_root: str = "."):
        """Inicializar verificador"""
        self.project_root = Path(project_root)
        self.checklist = {
            "codigo_configuracion": {
                "yaml_config": False,
                "scripts_python": False,
                "dockerfile": False,
                "docker_compose": False,
                "ci_cd_pipeline": False,
                "requirements": False
            },
            "documentacion": {
                "readme_updated": False,
                "instrucciones_docker": False,
                "analisis_gobernanza": False,
                "suposiciones": False
            },
            "evidencias": {
                "screenshots_directory": False,
                "structure_complete": False
            }
        }
        
    def check_code_artifacts(self):
        """Verificar artefactos de código"""
        logger.info("🔍 Verificando artefactos de código...")
        
        # YAML config
        yaml_path = self.project_root / "config/metadata_config.yaml"
        if yaml_path.exists():
            try:
                with open(yaml_path, 'r') as f:
                    config = yaml.safe_load(f)
                    if "tables" in config and len(config["tables"]) == 3:
                        self.checklist["codigo_configuracion"]["yaml_config"] = True
                        logger.info("✅ Archivo YAML de configuración válido")
            except Exception as e:
                logger.warning(f"⚠️ Error validando YAML: {e}")
        
        # Scripts Python
        scripts_dir = self.project_root / "scripts"
        required_scripts = ["catalog_automation.py", "aspect_types.py"]
        if all((scripts_dir / script).exists() for script in required_scripts):
            self.checklist["codigo_configuracion"]["scripts_python"] = True
            logger.info("✅ Scripts Python presentes")
        
        # Dockerfile
        dockerfile = self.project_root / "docker/Dockerfile"
        if dockerfile.exists():
            self.checklist["codigo_configuracion"]["dockerfile"] = True
            logger.info("✅ Dockerfile presente")
        
        # Docker Compose
        compose_file = self.project_root / "docker-compose.yml"
        if compose_file.exists():
            self.checklist["codigo_configuracion"]["docker_compose"] = True
            logger.info("✅ Docker Compose presente")
        
        # CI/CD Pipeline
        ci_file = self.project_root / ".github/workflows/data-governance-ci.yml"
        if ci_file.exists():
            self.checklist["codigo_configuracion"]["ci_cd_pipeline"] = True
            logger.info("✅ Pipeline CI/CD presente")
        
        # Requirements
        req_file = self.project_root / "requirements.txt"
        if req_file.exists():
            self.checklist["codigo_configuracion"]["requirements"] = True
            logger.info("✅ Requirements.txt presente")
    
    def check_documentation(self):
        """Verificar documentación"""
        logger.info("📚 Verificando documentación...")
        
        readme_path = self.project_root / "README.md"
        if readme_path.exists():
            try:
                with open(readme_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                    # Verificar secciones clave
                    if "Guía de Configuración y Ejecución" in content:
                        self.checklist["documentacion"]["readme_updated"] = True
                        logger.info("✅ README actualizado con configuración")
                    
                    if "docker build" in content and "docker-compose" in content:
                        self.checklist["documentacion"]["instrucciones_docker"] = True
                        logger.info("✅ Instrucciones Docker presentes")
                    
                    if "Análisis de Gobernanza de Datos" in content and "linaje" in content.lower():
                        self.checklist["documentacion"]["analisis_gobernanza"] = True
                        logger.info("✅ Análisis de gobernanza completo")
                    
                    if "Suposiciones Realizadas" in content:
                        self.checklist["documentacion"]["suposiciones"] = True
                        logger.info("✅ Suposiciones documentadas")
                        
            except Exception as e:
                logger.warning(f"⚠️ Error leyendo README: {e}")
    
    def check_evidence_structure(self):
        """Verificar estructura para evidencias"""
        logger.info("📸 Verificando estructura para evidencias...")
        
        # Directory para screenshots
        screenshots_dir = self.project_root / "screenshots"
        if screenshots_dir.exists():
            self.checklist["evidencias"]["screenshots_directory"] = True
            logger.info("✅ Directorio de screenshots creado")
        
        # Estructura completa
        required_dirs = ["config", "scripts", "docker", ".github/workflows", "docs"]
        if all((self.project_root / dir_name).exists() for dir_name in required_dirs):
            self.checklist["evidencias"]["structure_complete"] = True
            logger.info("✅ Estructura de directorios completa")
    
    def generate_report(self):
        """Generar reporte de verificación"""
        logger.info("📊 Generando reporte de verificación...")
        
        print("\n" + "="*80)
        print("🎯 REPORTE DE VERIFICACIÓN - PRUEBA TÉCNICA DEACERO")
        print("="*80)
        
        total_items = 0
        completed_items = 0
        
        for category, items in self.checklist.items():
            print(f"\n📋 {category.replace('_', ' ').title()}:")
            for item, status in items.items():
                total_items += 1
                if status:
                    completed_items += 1
                    print(f"  ✅ {item.replace('_', ' ').title()}")
                else:
                    print(f"  ❌ {item.replace('_', ' ').title()}")
        
        completion_rate = (completed_items / total_items) * 100
        print(f"\n📈 COMPLETITUD: {completed_items}/{total_items} ({completion_rate:.1f}%)")
        
        if completion_rate >= 90:
            print("🎉 ¡EXCELENTE! Todos los entregables están listos")
        elif completion_rate >= 75:
            print("👍 ¡BIEN! Casi todos los entregables están completos")
        else:
            print("⚠️ ATENCIÓN: Faltan varios entregables importantes")
        
        print("\n🚀 PRÓXIMOS PASOS:")
        print("1. Configurar Service Account en GCP")
        print("2. Crear Dataplex Lake y Zone")
        print("3. Ejecutar scripts de automatización")
        print("4. Capturar screenshots de evidencias")
        print("5. Probar pipeline CI/CD")
        print("6. Crear presentación final")
        
        print("\n" + "="*80)
        
        return completion_rate
    
    def run_verification(self):
        """Ejecutar verificación completa"""
        logger.info("🚀 Iniciando verificación de entregables...")
        
        self.check_code_artifacts()
        self.check_documentation()
        self.check_evidence_structure()
        
        completion_rate = self.generate_report()
        
        if completion_rate >= 90:
            logger.info("✅ Verificación completada exitosamente")
            return True
        else:
            logger.warning("⚠️ Verificación completada con observaciones")
            return False

def main():
    """Función principal"""
    try:
        checker = DeliverableChecker()
        success = checker.run_verification()
        
        if success:
            print("\n🎊 ¡PROYECTO LISTO PARA ENTREGA!")
        else:
            print("\n📝 Revisa los items pendientes antes de la entrega")
            
    except Exception as e:
        logger.error(f"Error en verificación: {e}")
        exit(1)

if __name__ == "__main__":
    main()
