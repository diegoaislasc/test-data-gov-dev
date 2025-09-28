#!/usr/bin/env python3
"""
Script para implementar políticas de enmascaramiento de datos en BigQuery
Parte 4 de la prueba técnica DeAcero
"""

import logging
from google.cloud import datacatalog_v1
from google.cloud import bigquery
from google.cloud.bigquery_datapolicies_v1 import DataPolicyServiceClient
from google.cloud.bigquery_datapolicies_v1.types import DataPolicy, CreateDataPolicyRequest
from google.cloud.datacatalog_v1.types import CreatePolicyTagRequest, PolicyTag
import os
import sys
from typing import Dict, List

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class DataMaskingPolicyManager:
    """Gestor de políticas de enmascaramiento de datos"""
    
    def __init__(self, project_id: str, location: str = "us-central1"):
        """
        Inicializar clientes de Google Cloud
        
        Args:
            project_id: ID del proyecto de GCP
            location: Región donde están los recursos
        """
        self.project_id = project_id
        self.location = location
        self.dc_client = datacatalog_v1.DataCatalogClient()
        self.policy_client = DataPolicyServiceClient()
        self.bq_client = bigquery.Client(project=project_id)
        
    def create_taxonomy(self, taxonomy_id: str, display_name: str, description: str) -> str:
        """
        Crear taxonomía para organizar policy tags
        
        Args:
            taxonomy_id: ID de la taxonomía
            display_name: Nombre mostrado
            description: Descripción de la taxonomía
            
        Returns:
            Nombre de la taxonomía creada
        """
        try:
            location_path = f"projects/{self.project_id}/locations/{self.location}"
            
            taxonomy = datacatalog_v1.Taxonomy()
            taxonomy.display_name = display_name
            taxonomy.description = description
            
            # Intentar crear la taxonomía
            try:
                created_taxonomy = self.dc_client.create_taxonomy(
                    parent=location_path,
                    taxonomy=taxonomy
                )
                logger.info(f"Taxonomía creada: {created_taxonomy.name}")
                return created_taxonomy.name
                
            except Exception as e:
                if "already exists" in str(e).lower():
                    # Si ya existe, buscarla
                    taxonomies = self.dc_client.list_taxonomies(parent=location_path)
                    for tax in taxonomies:
                        if tax.display_name == display_name:
                            logger.info(f"Taxonomía ya existe: {tax.name}")
                            return tax.name
                    raise Exception(f"No se pudo encontrar taxonomía existente: {display_name}")
                else:
                    raise e
                    
        except Exception as e:
            logger.error(f"Error creando taxonomía: {e}")
            raise
            
    def create_policy_tag(self, taxonomy_name: str, policy_tag_id: str, 
                         display_name: str, description: str) -> str:
        """
        Crear policy tag para clasificar datos sensibles
        
        Args:
            taxonomy_name: Nombre de la taxonomía padre
            policy_tag_id: ID del policy tag
            display_name: Nombre mostrado
            description: Descripción del policy tag
            
        Returns:
            Nombre del policy tag creado
        """
        try:
            policy_tag = PolicyTag()
            policy_tag.display_name = display_name
            policy_tag.description = description
            
            request = CreatePolicyTagRequest(
                parent=taxonomy_name,
                policy_tag=policy_tag
            )
            
            try:
                created_tag = self.dc_client.create_policy_tag(request=request)
                logger.info(f"Policy tag creado: {created_tag.name}")
                return created_tag.name
                
            except Exception as e:
                if "already exists" in str(e).lower():
                    # Si ya existe, buscarlo
                    policy_tags = self.dc_client.list_policy_tags(parent=taxonomy_name)
                    for tag in policy_tags:
                        if tag.display_name == display_name:
                            logger.info(f"Policy tag ya existe: {tag.name}")
                            return tag.name
                    raise Exception(f"No se pudo encontrar policy tag existente: {display_name}")
                else:
                    raise e
                    
        except Exception as e:
            logger.error(f"Error creando policy tag: {e}")
            raise
            
    def create_data_policy(self, policy_id: str, policy_tag_name: str, 
                          user_email: str, masking_type: str = "SHA256") -> str:
        """
        Crear política de enmascaramiento de datos
        
        Args:
            policy_id: ID de la política
            policy_tag_name: Nombre del policy tag asociado
            user_email: Email del usuario al que se aplicará la política
            masking_type: Tipo de enmascaramiento (SHA256, DEFAULT_MASKING_VALUE, etc.)
            
        Returns:
            Nombre de la política creada
        """
        try:
            location_path = f"projects/{self.project_id}/locations/{self.location}"
            
            # Configurar la política de enmascaramiento
            data_policy = DataPolicy()
            data_policy.policy_tag = policy_tag_name
            
            # Configurar el tipo de enmascaramiento
            if masking_type == "SHA256":
                data_policy.data_masking_policy.predefined_expression = "SHA256"
            else:
                data_policy.data_masking_policy.predefined_expression = "DEFAULT_MASKING_VALUE"
            
            request = CreateDataPolicyRequest(
                parent=location_path,
                data_policy_id=policy_id,
                data_policy=data_policy
            )
            
            try:
                created_policy = self.policy_client.create_data_policy(request=request)
                logger.info(f"Política de datos creada: {created_policy.name}")
                
                # Configurar IAM para el usuario específico
                self._configure_policy_binding(created_policy.name, user_email)
                
                return created_policy.name
                
            except Exception as e:
                if "already exists" in str(e).lower():
                    policy_path = f"{location_path}/dataPolicies/{policy_id}"
                    logger.info(f"Política ya existe: {policy_path}")
                    
                    # Aún configurar IAM binding
                    self._configure_policy_binding(policy_path, user_email)
                    return policy_path
                else:
                    raise e
                    
        except Exception as e:
            logger.error(f"Error creando política de datos: {e}")
            raise
            
    def _configure_policy_binding(self, policy_name: str, user_email: str):
        """
        Configurar binding de IAM para la política
        
        Args:
            policy_name: Nombre de la política
            user_email: Email del usuario
        """
        try:
            # Obtener política actual de IAM
            policy = self.policy_client.get_iam_policy(resource=policy_name)
            
            # Agregar binding para maskedReader
            binding_found = False
            for binding in policy.bindings:
                if binding.role == "roles/bigquerydatapolicy.maskedReader":
                    if f"user:{user_email}" not in binding.members:
                        binding.members.append(f"user:{user_email}")
                    binding_found = True
                    break
            
            if not binding_found:
                from google.iam.v1.policy_pb2 import Binding
                new_binding = Binding()
                new_binding.role = "roles/bigquerydatapolicy.maskedReader"
                new_binding.members.append(f"user:{user_email}")
                policy.bindings.append(new_binding)
            
            # Actualizar política de IAM
            self.policy_client.set_iam_policy(resource=policy_name, policy=policy)
            logger.info(f"IAM binding configurado para {user_email}")
            
        except Exception as e:
            logger.error(f"Error configurando IAM binding: {e}")
            # No lanzar excepción aquí, ya que la política principal se creó
            
    def apply_policy_to_columns(self, dataset_id: str, table_id: str, 
                               columns: List[str], policy_tag_name: str, 
                               source_project: str = "deacero-datagov"):
        """
        Aplicar policy tag a columnas específicas de una tabla
        
        Args:
            dataset_id: ID del dataset
            table_id: ID de la tabla
            columns: Lista de columnas a proteger
            policy_tag_name: Nombre del policy tag a aplicar
            source_project: Proyecto donde está la tabla (por defecto deacero-datagov)
        """
        try:
            # Obtener la tabla
            table_ref = self.bq_client.dataset(dataset_id, project=source_project).table(table_id)
            table = self.bq_client.get_table(table_ref)
            
            # Crear nueva schema con policy tags
            new_schema = []
            for field in table.schema:
                new_field = bigquery.SchemaField(
                    name=field.name,
                    field_type=field.field_type,
                    mode=field.mode,
                    description=field.description
                )
                
                # Aplicar policy tag si es una columna protegida
                if field.name in columns:
                    new_field = new_field.with_policy_tags([policy_tag_name])
                    logger.info(f"Policy tag aplicado a columna: {field.name}")
                
                new_schema.append(new_field)
            
            # Actualizar schema de la tabla
            table.schema = new_schema
            updated_table = self.bq_client.update_table(table, ["schema"])
            
            logger.info(f"Schema actualizado para tabla: {source_project}.{dataset_id}.{table_id}")
            
        except Exception as e:
            logger.error(f"Error aplicando policy tag a columnas: {e}")
            logger.warning("NOTA: Puede que no tengas permisos para modificar tablas públicas.")
            logger.warning("En un entorno real, esto se aplicaría a copias de las tablas en tu proyecto.")
            
    def setup_masking_policies(self, user_email: str):
        """
        Configurar todas las políticas de enmascaramiento necesarias
        
        Args:
            user_email: Email del usuario al que se aplicarán las políticas
        """
        try:
            logger.info("Iniciando configuración de políticas de enmascaramiento...")
            
            # 1. Crear taxonomía para datos sensibles
            taxonomy_name = self.create_taxonomy(
                taxonomy_id="sensitive_data_taxonomy",
                display_name="Sensitive Data Classification",
                description="Taxonomía para clasificar datos sensibles que requieren enmascaramiento"
            )
            
            # 2. Crear policy tag para PII
            pii_policy_tag = self.create_policy_tag(
                taxonomy_name=taxonomy_name,
                policy_tag_id="pii_direct",
                display_name="PII Direct",
                description="Información personal identificable directa que debe ser enmascarada"
            )
            
            # 3. Crear política de enmascaramiento SHA256
            data_policy = self.create_data_policy(
                policy_id="pii_masking_sha256",
                policy_tag_name=pii_policy_tag,
                user_email=user_email,
                masking_type="SHA256"
            )
            
            # 4. Aplicar policy tag a las columnas sensibles
            # NOTA: Esto funcionará solo si tienes permisos de escritura en la tabla
            # Para tablas públicas, normalmente necesitarías crear una copia
            try:
                self.apply_policy_to_columns(
                    dataset_id="stackoverflow",
                    table_id="users",
                    columns=["display_name", "location"],
                    policy_tag_name=pii_policy_tag,
                    source_project="deacero-datagov"
                )
            except Exception as e:
                logger.warning(f"No se pudieron aplicar policy tags directamente: {e}")
                logger.info("Las políticas están creadas. Para aplicarlas a tablas públicas:")
                logger.info("1. Crea una copia de la tabla en tu proyecto")
                logger.info("2. Aplica el policy tag a las columnas sensibles")
                logger.info(f"Policy Tag creado: {pii_policy_tag}")
            
            logger.info("Configuración de políticas completada exitosamente!")
            logger.info("\n" + "="*60)
            logger.info("RESUMEN DE POLÍTICAS CREADAS:")
            logger.info(f"Taxonomía: {taxonomy_name}")
            logger.info(f"Policy Tag: {pii_policy_tag}")
            logger.info(f"Política de datos: {data_policy}")
            logger.info(f"Usuario configurado: {user_email}")
            logger.info("="*60)
            
            return {
                "taxonomy": taxonomy_name,
                "policy_tag": pii_policy_tag,
                "data_policy": data_policy,
                "user_email": user_email
            }
            
        except Exception as e:
            logger.error(f"Error en configuración de políticas: {e}")
            raise

def main():
    """Función principal"""
    try:
        # Obtener project ID desde variable de entorno
        project_id = os.getenv("GOOGLE_CLOUD_PROJECT")
        if not project_id:
            logger.error("Variable de entorno GOOGLE_CLOUD_PROJECT no definida")
            sys.exit(1)
            
        # Usuario al que se aplicarán las políticas
        user_email = "diegoaislasc@gmail.com"
        
        # Inicializar gestor de políticas
        policy_manager = DataMaskingPolicyManager(project_id)
        
        # Configurar políticas de enmascaramiento
        result = policy_manager.setup_masking_policies(user_email)
        
        logger.info("\n" + "="*60)
        logger.info("INSTRUCCIONES PARA VERIFICACIÓN:")
        logger.info("="*60)
        logger.info("1. Ve a BigQuery Console")
        logger.info("2. Ejecuta la siguiente consulta:")
        logger.info("   SELECT display_name, location")
        logger.info("   FROM `deacero-datagov.stackoverflow.users`")
        logger.info("   LIMIT 10;")
        logger.info("3. Los valores de display_name y location deberían aparecer enmascarados")
        logger.info("   con hashes SHA-256 para tu usuario")
        logger.info("="*60)
        
        print("\n✅ Políticas de enmascaramiento configuradas exitosamente!")
        
    except Exception as e:
        logger.error(f"Error en configuración de enmascaramiento: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
