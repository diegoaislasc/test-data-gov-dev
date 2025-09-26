#!/usr/bin/env python3
"""
Script para crear y aplicar Aspect Types en Dataplex
Parte 3 de la prueba técnica DeAcero
"""

import logging
from google.cloud import dataplex_v1
from google.cloud import bigquery
import os
import sys

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class DataplexAspectManager:
    """Gestor de Aspect Types en Dataplex"""
    
    def __init__(self, project_id: str, location: str = "us-central1"):
        """
        Inicializar cliente de Dataplex
        
        Args:
            project_id: ID del proyecto de GCP
            location: Región donde están los recursos
        """
        self.project_id = project_id
        self.location = location
        self.dataplex_client = dataplex_v1.CatalogServiceClient()
        
    def create_aspect_type(self) -> str:
        """
        Crear Aspect Type personalizado para governance
        
        Returns:
            Nombre del Aspect Type creado
        """
        try:
            # Definir el parent path
            parent = f"projects/{self.project_id}/locations/{self.location}"
            
            # Definir campos del Aspect Type
            aspect_type = dataplex_v1.AspectType()
            aspect_type.display_name = "Data Governance Aspect"
            aspect_type.description = "Aspect Type personalizado para metadatos de gobernanza de datos"
            
            # Campo Owner (texto)
            owner_field = dataplex_v1.AspectType.MetadataTemplate()
            owner_field.name = "owner"
            owner_field.type_ = "string"
            owner_field.annotations.display_name = "Data Owner"
            owner_field.annotations.description = "Propietario responsable de los datos"
            owner_field.constraints.required = True
            
            # Campo Freshness (enumeración)
            freshness_field = dataplex_v1.AspectType.MetadataTemplate()
            freshness_field.name = "freshness"
            freshness_field.type_ = "enum"
            freshness_field.annotations.display_name = "Data Freshness"
            freshness_field.annotations.description = "Frecuencia de actualización de los datos"
            freshness_field.constraints.required = True
            
            # Valores de enumeración para freshness
            freshness_field.type_ref = "freshness_enum"
            freshness_enum = dataplex_v1.AspectType.MetadataTemplate()
            freshness_enum.enum_values = ["daily", "weekly", "monthly"]
            
            # Agregar campos al template
            aspect_type.metadata_template = {
                "owner": owner_field,
                "freshness": freshness_field
            }
            
            # Crear el Aspect Type
            aspect_type_id = "data_governance_aspect"
            
            operation = self.dataplex_client.create_aspect_type(
                parent=parent,
                aspect_type_id=aspect_type_id,
                aspect_type=aspect_type
            )
            
            # Esperar a que la operación complete
            result = operation.result()
            
            logger.info(f"Aspect Type creado: {result.name}")
            return result.name
            
        except Exception as e:
            if "already exists" in str(e).lower():
                aspect_type_name = f"projects/{self.project_id}/locations/{self.location}/aspectTypes/data_governance_aspect"
                logger.info(f"Aspect Type ya existe: {aspect_type_name}")
                return aspect_type_name
            else:
                logger.error(f"Error creando Aspect Type: {e}")
                raise
                
    def apply_aspect_to_entry(self, entry_resource_name: str, aspect_type_name: str, 
                            owner: str, freshness: str):
        """
        Aplicar Aspect a una entrada específica
        
        Args:
            entry_resource_name: Nombre del recurso de la entrada
            aspect_type_name: Nombre del Aspect Type
            owner: Propietario de los datos
            freshness: Frecuencia de actualización
        """
        try:
            # Crear el Aspect
            aspect = dataplex_v1.Aspect()
            aspect.aspect_type = aspect_type_name
            
            # Agregar metadatos
            aspect.data = {
                "owner": owner,
                "freshness": freshness
            }
            
            # Aplicar el Aspect
            aspect_id = "governance_metadata"
            
            created_aspect = self.dataplex_client.create_aspect(
                parent=entry_resource_name,
                aspect_id=aspect_id,
                aspect=aspect
            )
            
            logger.info(f"Aspect aplicado a: {entry_resource_name}")
            
        except Exception as e:
            if "already exists" in str(e).lower():
                logger.info(f"Aspect ya existe para: {entry_resource_name}")
            else:
                logger.error(f"Error aplicando aspect: {e}")
                raise
                
    def get_catalog_entry_name(self, dataset_id: str, table_id: str) -> str:
        """
        Obtener el nombre de la entrada en el catálogo para una tabla
        
        Args:
            dataset_id: ID del dataset
            table_id: ID de la tabla
            
        Returns:
            Nombre de la entrada en el catálogo
        """
        try:
            # Para datasets públicos, el formato es diferente
            if "bigquery-public-data" in dataset_id:
                # Formato para datasets públicos
                entry_name = f"projects/{self.project_id}/locations/{self.location}/entryGroups/@bigquery/entries/{dataset_id}_{table_id}"
            else:
                # Formato para datasets del proyecto
                entry_name = f"projects/{self.project_id}/locations/{self.location}/entryGroups/@bigquery/entries/{dataset_id}_{table_id}"
            
            logger.info(f"Nombre de entrada generado: {entry_name}")
            return entry_name
            
        except Exception as e:
            logger.error(f"Error generando nombre de entrada: {e}")
            raise
            
    def process_all_tables(self):
        """
        Procesar todas las tablas principales con Aspect Types
        """
        try:
            # Crear Aspect Type
            aspect_type_name = self.create_aspect_type()
            
            # Lista de tablas a procesar
            tables = [
                {"table_id": "users", "dataset_id": "bigquery-public-data.stackoverflow"},
                {"table_id": "posts_questions", "dataset_id": "bigquery-public-data.stackoverflow"},
                {"table_id": "posts_answers", "dataset_id": "bigquery-public-data.stackoverflow"}
            ]
            
            # Procesar cada tabla
            for table in tables:
                table_id = table["table_id"]
                dataset_id = table["dataset_id"]
                
                logger.info(f"Procesando tabla: {table_id}")
                
                # Obtener nombre de entrada
                entry_name = self.get_catalog_entry_name(dataset_id, table_id)
                
                # Aplicar Aspect
                self.apply_aspect_to_entry(
                    entry_resource_name=entry_name,
                    aspect_type_name=aspect_type_name,
                    owner="dataowner@deacero.com",
                    freshness="daily"
                )
                
                logger.info(f"Tabla {table_id} procesada con Aspect Type")
                
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
            
        # Inicializar gestor de Aspects
        aspect_manager = DataplexAspectManager(project_id)
        
        # Procesar todas las tablas
        aspect_manager.process_all_tables()
        
        logger.info("Aspect Types aplicados exitosamente")
        
    except Exception as e:
        logger.error(f"Error en Aspect Types: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()


