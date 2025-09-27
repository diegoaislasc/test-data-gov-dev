#!/usr/bin/env python3
"""
Script para catalogación automatizada de metadatos en Google Cloud Data Catalog
Parte 2 de la prueba técnica DeAcero
"""

import yaml
import logging
from google.cloud import datacatalog_v1
from google.cloud import bigquery
from typing import Dict, List, Any
import os
import sys

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class DataCatalogAutomation:
    """Automatización de Data Catalog para metadatos de tablas"""
    
    def __init__(self, project_id: str, location: str = "us-central1"):
        """
        Inicializar cliente de Data Catalog
        
        Args:
            project_id: ID del proyecto de GCP
            location: Región donde están los recursos
        """
        self.project_id = project_id
        self.location = location
        self.dc_client = datacatalog_v1.DataCatalogClient()
        self.bq_client = bigquery.Client(project=project_id)
        
    def load_metadata_config(self, config_path: str) -> Dict[str, Any]:
        """
        Cargar configuración de metadatos desde archivo YAML
        
        Args:
            config_path: Ruta al archivo YAML de configuración
            
        Returns:
            Diccionario con la configuración
        """
        try:
            with open(config_path, 'r', encoding='utf-8') as file:
                config = yaml.safe_load(file)
                logger.info(f"Configuración cargada desde {config_path}")
                return config
        except Exception as e:
            logger.error(f"Error cargando configuración: {e}")
            raise
            
    def create_tag_template(self, template_id: str, display_name: str, 
                          fields: Dict[str, str]) -> str:
        """
        Crear template de tags en Data Catalog
        
        Args:
            template_id: ID del template
            display_name: Nombre mostrado del template
            fields: Diccionario de campos del template
            
        Returns:
            Nombre del template creado
        """
        try:
            # Crear template de tags
            location_path = f"projects/{self.project_id}/locations/{self.location}"
            
            tag_template = datacatalog_v1.TagTemplate()
            tag_template.display_name = display_name
            
            # Agregar campos al template
            for field_id, field_type in fields.items():
                field = datacatalog_v1.TagTemplateField()
                if field_type == "string":
                    field.type_.primitive_type = datacatalog_v1.FieldType.PrimitiveType.STRING
                field.display_name = field_id.replace('_', ' ').title()
                tag_template.fields[field_id] = field
            
            # Crear el template
            template = self.dc_client.create_tag_template(
                parent=location_path,
                tag_template_id=template_id,
                tag_template=tag_template
            )
            
            logger.info(f"Template de tags creado: {template.name}")
            return template.name
            
        except Exception as e:
            if "already exists" in str(e).lower():
                template_path = f"projects/{self.project_id}/locations/{self.location}/tagTemplates/{template_id}"
                logger.info(f"Template ya existe: {template_path}")
                return template_path
            else:
                logger.error(f"Error creando template: {e}")
                raise
                
    def get_table_entry(self, project_id: str, dataset_id: str, table_id: str) -> str:
        """
        Obtener la entrada de Data Catalog para una tabla de BigQuery
        
        Args:
            project_id: ID del proyecto donde está la tabla
            dataset_id: ID del dataset
            table_id: ID de la tabla
            
        Returns:
            Nombre de la entrada en Data Catalog
        """
        try:
            # Construir resource name de BigQuery
            resource_name = f"//bigquery.googleapis.com/projects/{project_id}/datasets/{dataset_id}/tables/{table_id}"
            
            # Buscar entrada en Data Catalog
            entry = self.dc_client.lookup_entry(
                request={"linked_resource": resource_name}
            )
            
            logger.info(f"Entrada encontrada para {table_id}: {entry.name}")
            return entry.name
            
        except Exception as e:
            logger.error(f"Error obteniendo entrada para {table_id}: {e}")
            raise
            
    def update_table_description(self, entry_name: str, description: str):
        """
        Actualizar descripción de una tabla
        
        Args:
            entry_name: Nombre de la entrada en Data Catalog
            description: Nueva descripción
        """
        try:
            # Obtener entrada actual
            entry = self.dc_client.get_entry(name=entry_name)
            
            # Actualizar descripción
            entry.description = description
            
            # Actualizar entrada
            self.dc_client.update_entry(entry=entry)
            
            logger.info(f"Descripción actualizada para: {entry_name}")
            
        except Exception as e:
            logger.error(f"Error actualizando descripción: {e}")
            raise
            
    def create_tags_for_table(self, entry_name: str, template_name: str, 
                            tags: List[str], data_steward: str):
        """
        Crear tags para una tabla
        
        Args:
            entry_name: Nombre de la entrada en Data Catalog
            template_name: Nombre del template de tags
            tags: Lista de tags a aplicar
            data_steward: Email del data steward
        """
        try:
            # Crear tag con metadatos
            tag = datacatalog_v1.Tag()
            tag.template = template_name
            
            # Agregar campos
            tag.fields["tags"] = datacatalog_v1.TagField()
            tag.fields["tags"].string_value = ", ".join(tags)
            
            tag.fields["data_steward"] = datacatalog_v1.TagField()
            tag.fields["data_steward"].string_value = data_steward
            
            # Crear el tag
            created_tag = self.dc_client.create_tag(
                parent=entry_name,
                tag=tag
            )
            
            logger.info(f"Tags creados para: {entry_name}")
            
        except Exception as e:
            if "already exists" in str(e).lower():
                logger.info(f"Tags ya existen para: {entry_name}")
            else:
                logger.error(f"Error creando tags: {e}")
                raise
                
    def process_tables(self, config: Dict[str, Any]):
        """
        Procesar todas las tablas según la configuración
        
        Args:
            config: Configuración de metadatos
        """
        try:
            # Crear template de tags si no existe
            template_name = self.create_tag_template(
                template_id="deacero_governance_template",
                display_name="DeAcero Governance Template",
                fields={
                    "tags": "string",
                    "data_steward": "string"
                }
            )
            
            # Procesar cada tabla
            for table_config in config.get("tables", []):
                table_id = table_config["table_id"]
                description = table_config["description"]
                data_steward = table_config["data_steward"]
                tags = table_config["tags"]
                
                logger.info(f"Procesando tabla: {table_id}")
                
                # Obtener entrada de la tabla
                entry_name = self.get_table_entry(self.project_id, "stackoverflow", table_id)
                
                # Intentar actualizar descripción (puede fallar si es entrada sincronizada)
                try:
                    self.update_table_description(entry_name, description)
                    logger.info(f"Descripción actualizada para: {table_id}")
                except Exception as e:
                    if "synced entries" in str(e).lower():
                        logger.warning(f"No se puede actualizar descripción para entrada sincronizada: {table_id}")
                    else:
                        logger.error(f"Error actualizando descripción para {table_id}: {e}")
                
                # Crear tags
                self.create_tags_for_table(entry_name, template_name, tags, data_steward)
                
                logger.info(f"Tabla {table_id} procesada exitosamente")
                
        except Exception as e:
            logger.error(f"Error procesando tablas: {e}")
            raise

def main():
    """Función principal"""
    try:
        # Obtener project ID desde variable de entorno
        project_id = os.getenv("GOOGLE_CLOUD_PROJECT")
        if not project_id:
            logger.error("Variable de entorno GOOGLE_CLOUD_PROJECT no definida")
            sys.exit(1)
            
        # Inicializar automatización
        automation = DataCatalogAutomation(project_id)
        
        # Cargar configuración
        config_path = "config/metadata_config.yaml"
        config = automation.load_metadata_config(config_path)
        
        # Procesar tablas
        automation.process_tables(config)
        
        logger.info("Catalogación automatizada completada exitosamente")
        
    except Exception as e:
        logger.error(f"Error en catalogación automatizada: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()


