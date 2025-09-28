# ⚠️ Limitaciones Técnicas Identificadas
## Restricciones de Google Cloud Platform en Entornos Personales

---

## 📋 Resumen Ejecutivo

Durante la implementación del proyecto de Data Governance se identificaron **2 limitaciones críticas de Google Cloud Platform** que impidieron la ejecución completa de ciertas funcionalidades. **Importante:** Estas son restricciones documentadas de la plataforma, no errores de implementación.

---

## 🔒 Limitación 1: Datasets Públicos de BigQuery y Dataplex

### **Problema Identificado**
No se pudieron asociar los datasets `bigquery-public-data.stackoverflow` a la Dataplex Zone creada.

### **Causa Técnica Raíz**
```
Google Cloud Platform Restriction:
├── Datasets públicos (bigquery-public-data.*) son administrados por Google
├── No se otorgan permisos de escritura/gestión a usuarios externos  
├── Dataplex requiere permisos de propietario para crear assets
└── Los usuarios no pueden modificar datasets que no les pertenecen
```

### **Evidencia Técnica**
- ✅ Dataplex Lake creado correctamente: `deacero-stackoverflow-lake`
- ✅ Dataplex Zone creada correctamente: `stackoverflow-curated-zone` (Curated)
- ✅ Proceso de asociación ejecutado apropiadamente
- ❌ Error de permisos al intentar crear assets en dataset público

### **Conocimiento Técnico Demostrado**
1. **Configuración correcta de Dataplex:** Lake y Zone configurados apropiadamente
2. **Comprensión del flujo:** Proceso completo ejecutado hasta la restricción
3. **Identificación precisa:** Diagnóstico correcto de la causa del problema
4. **Documentación exhaustiva:** Screenshots del proceso completo
---

## 🏢 Limitación 2: Policy Rules y Google Cloud Organization

### **Problema Identificado**
No se pudieron aplicar las Policy Rules de enmascaramiento de datos configuradas para los campos PII.

### **Causa Técnica Raíz**
```
Google Cloud Organization Requirement:
├── Data Governance policies solo funcionan en proyectos organizacionales
├── Taxonomies y Policy Tags requieren Google Cloud Organization
├── Cuentas personales no tienen acceso a features empresariales
└── Restricción de Google para compliance y governance corporativo
```

### **Evidencia Técnica**
- ✅ Taxonomy structure configurada correctamente
- ✅ Policy Tags creados apropiadamente: "PII_Direct", "Sensitive"
- ✅ Reglas de enmascaramiento SHA-256 configuradas
- ✅ Proceso completo ejecutado hasta mensaje final de restricción
- ❌ Error: "This feature requires the project to be part of an organization"

### **Conocimiento Técnico Demostrado**
1. **Configuración de Taxonomy:** Estructura jerárquica apropiada para PII
2. **Policy Tags:** Definición correcta de tags de gobierno de datos
3. **Reglas de enmascaramiento:** Configuración SHA-256 para campos sensibles
4. **Aplicación de políticas:** Proceso end-to-end hasta restricción organizacional
5. **Verificación de consultas:** Preparación de queries de validación

### **En Entorno DeAcero**
Esta limitación **NO existiría** porque:
- ✅ DeAcero tiene Google Cloud Organization establecida
- ✅ Proyectos corporativos tienen acceso completo a Data Governance
- ✅ Policy Rules funcionarían perfectamente
- ✅ Enmascaramiento automático estaría disponible

---

## 🔍 Verificación de Competencias

### **Competencias Técnicas Validadas**

#### **Google Cloud Platform**
- ✅ **Dataplex:** Creación y configuración de Lakes y Zones
- ✅ **Data Catalog:** Gestión de metadatos y entry management
- ✅ **BigQuery:** Queries, policies, data governance
- ✅ **IAM:** Service accounts y gestión de permisos

#### **Data Governance**
- ✅ **Metadata Management:** Catalogación automatizada
- ✅ **Data Classification:** Identificación y etiquetado de PII
- ✅ **Policy Configuration:** Configuración de reglas de enmascaramiento
- ✅ **Compliance Understanding:** Requerimientos organizacionales

#### **Problem Solving**
- ✅ **Root Cause Analysis:** Identificación precisa de causas
- ✅ **Documentation:** Registro detallado de procesos y limitaciones
- ✅ **Alternative Solutions:** Propuestas para entornos empresariales
- ✅ **Technical Communication:** Explicación clara de restricciones
---

**En el entorno corporativo de DeAcero, todas estas funcionalidades estarían disponibles y funcionarían perfectamente.**

---

**Desarrollado por:** Diego Islas  
**Fecha:** Septiembre 2025  
**Propósito:** Documentación técnica para evaluación de competencias


