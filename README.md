# Prueba Técnica: Data Governance Developer

## Introducción y Contexto del Problema 📝

¡Bienvenido/a al proceso de selección para **Governance Developer** en **DeAcero**!

Tu misión es demostrar tus habilidades en la implementación de un marco de gobierno de datos de extremo a extremo utilizando **Google Cloud Platform**. Para ello, trabajarás con el conocido dataset público de Stack Overflow, simulando que es la base de conocimiento interna de nuestra organización.

El objetivo es catalogar los activos clave, proteger la privacidad de los usuarios, asegurar la integridad de los datos, automatizar el proceso y demostrar cómo medirías y comunicarías el valor de estas iniciativas.

**Dataset Público a Utilizar**: `bigquery-public-data.stackoverflow`

---

## Objetivos Principales 🎯

- ✅ Catalogar activos clave de forma automatizada usando un archivo de configuración YAML
- ✅ Implementar una política de seguridad para proteger la información personal de los usuarios mediante el enmascaramiento de datos
- ✅ Implementar una política de calidad para asegurar la integridad de los datos
- ✅ Containerizar la solución con Docker y CI/CD
- ✅ Analizar y documentar conceptos clave de gobernanza como el linaje, las métricas de cumplimiento y la comunicación con stakeholders

---

## Tareas Específicas a Realizar

### **Parte 1: Configuración del Entorno en Dataplex**

1. Crea un **Dataplex Lake** en una región de tu elección (ej. `us-central1`)
2. Dentro de ese Lake, crea una **Dataplex Zone** de tipo **Curated Zone**
3. Asocia la Zone que creaste con el dataset completo de BigQuery: `bigquery-public-data.stackoverflow`
4. Asegúrate de que Dataplex descubra los assets (las tablas) correctamente

---

### **Parte 2: Catalogación Automatizada con YAML**

Crea un **archivo YAML** para definir los metadatos de las siguientes tres tablas: `users`, `posts_questions`, y `posts_answers`. 

Desarrolla un **script en Python** que lea este archivo y utilice la biblioteca cliente de Google Cloud para **Data Catalog** para actualizar las descripciones y adjuntar los tags a las tablas correspondientes en Dataplex.

#### **Información requerida en el yaml**


tables:
  - table_id: users
    description: "Tabla maestra de usuarios. Contiene información personal identificable (PII) y debe ser tratada como sensible."
    data_steward: "identity_management@deacero.com"
    tags:
      - "PII_Direct"
      - "User Data"
      - "Sensitive"

  - table_id: posts_questions
    description: "Contiene todas las preguntas creadas por los usuarios. El contenido es generado por el usuario."
    data_steward: "knowledge_management@deacero.com"
    tags:
      - "User Generated Content"
      - "Knowledge Base"

  - table_id: posts_answers
    description: "Contiene las respuestas a las preguntas. Vinculada a las preguntas y a los usuarios."
    data_steward: "knowledge_management@deacero.com"
    tags:
      - "User Generated Content"
      - "Transactional Data"


---

### **Parte 3: Configuración de Aspect Types en Dataplex** 📊

Crea un **Aspect Type personalizado** en Dataplex para enriquecer los metadatos de las tablas con información de gobierno de datos adicional.

#### **Definir Aspect Type:**
Usando las funcionalidades de Dataplex, crea un nuevo Aspect Type llamado `"data_governance_aspect"` con los siguientes campos:

- **Owner**: Campo de texto para especificar el propietario de los datos (`dataowner@deacero.com`)
- **Freshness**: Campo de enumeración para indicar la frecuencia de actualización (`daily`, `weekly`, `monthly`)

#### **Aplicar Aspect Type:**
Asigna este Aspect Type a las tres tablas principales (`users`, `posts_questions`, `posts_answers`) con los siguientes valores:
- **Owner**: `"dataowner@deacero.com"`
- **Freshness**: `"daily"`

#### **Verificación:**
Demuestra que los Aspect Types se han aplicado correctamente a las tablas en la UI de Dataplex.

---

### **Parte 4: Implementación de Seguridad y Enmascaramiento de Datos** 🔒

La tabla `users` contiene datos que deben ser protegidos. Tu tarea es implementar una **política de enmascaramiento**.

#### **Definir la Política:**
Usando las funcionalidades de "Policies", crea una nueva regla de política de datos.

#### **Configurar la Regla:**
- **Recurso**: Aplica la política a las columnas `display_name` y `location` de la tabla `bigquery-public-data.stackoverflow.users`
- **Roles/Principales**: Asigna la política a tu propia cuenta de usuario
- **Tipo de Enmascaramiento**: Configura la regla para que enmascare los datos usando un hash **SHA-256**

#### **Verificación:**
Ejecuta una consulta en BigQuery:
```sql
SELECT display_name, location 
FROM `bigquery-public-data.stackoverflow.users` 
LIMIT 10;
```
Demuestra que los valores aparecen enmascarados para tu usuario.

---

### **Parte 5: Implementación de una Regla de Calidad de Datos**

El equipo de negocio ha reportado que a veces se crean preguntas sin un autor asignado, lo cual es un **problema de integridad**. Tu tarea es crear una regla que monitoree este problema.

#### **Crear Regla de Calidad:**
Utilizando la funcionalidad de **Data Quality** dentro de Dataplex, crea una nueva regla para la tabla `posts_questions`.

#### **Configurar la Regla:**
La regla debe verificar que la columna `owner_user_id` **nunca sea nula**.

#### **Ejecutar y Verificar:**
Ejecuta el "job" de calidad de datos y proporciona un **screenshot del resultado**, mostrando el **porcentaje de cumplimiento** de la regla.

---

### **Parte 6: Dockerización y CI/CD Pipeline** 🐳

Para hacer la solución **reproducible y escalable**, implementa la containerización y automatización del proceso.



---

### **Parte 7: Análisis de Gobernanza (Conceptual)**

Esta parte **no requiere código adicional**, sino tu análisis como experto en gobernanza. En tu archivo `README.md`, crea una sección dedicada a este análisis y responde a lo siguiente:

#### **Análisis de Linaje:**
Explica la relación de linaje principal entre `users`, `posts_questions` y `posts_answers`. ¿Por qué un "Community Manager" se beneficiaría de poder visualizar este linaje? Escribe un párrafo breve (**máximo 100 palabras**) explicándole en términos sencillos qué es el linaje de datos y por qué es importante que él/ella sepa que la tabla `posts_questions` está conectada a la tabla `users`.

---

## Entregables 📬

Crea un **fork** de este repositorio que contenga:

### **Código y Configuración:**
- ✅ Todos los artefactos, scripts, documentos que creaste
- ✅ Archivo YAML de configuración de metadatos
- ✅ Scripts Python para cada parte de la implementación
- ✅ `Dockerfile` y `docker-compose.yml`
- ✅ Pipeline de CI/CD (github, gitlab o bitbucket)
- ✅ Archivo `requirements.txt`

### **Documentación:**
- ✅ **README.md** con:
  - Instrucciones claras de configuración y ejecución
  - Comandos Docker para ejecutar la solución
  - Plan de implementación para la Parte 6
  - Análisis de gobernanza completo de la Parte 7
  - Cualquier suposición que hayas hecho

### **Evidencias:**
- ✅ **Screenshots** de:
  - Resultado de la carga de metadatos en la UI de Dataplex
  - Resultado de la consulta en BigQuery que demuestra el enmascaramiento
  - Resultado del job de Calidad de Datos
  - Pipeline de CI/CD ejecutándose exitosamente
  - Contenedor Docker funcionando

### **Presentación:**
- ✅ **Documento final** para presentar tu trabajo (PowerPoint, PDF, etc.)

---


---

## 🚀 Recursos de Apoyo


### **Dataset de Prueba:**
- **Proyecto**: `bigquery-public-data`
- **Dataset**: `stackoverflow`
- **Tablas principales**: `users`, `posts_questions`, `posts_answers`



## 🚀 Guía de Configuración y Ejecución

### Prerrequisitos

1. **Cuenta de Google Cloud Platform** con los siguientes APIs habilitados:
   - Dataplex API
   - Data Catalog API
   - BigQuery API
   - Cloud Storage API

2. **Herramientas requeridas:**
   - Python 3.11+
   - Docker & Docker Compose
   - Git
   - gcloud CLI (opcional)

### Configuración Inicial

#### 1. Clonar el Repositorio
```bash
git clone <repository-url>
cd test-data-gov-dev
```

#### 2. Configurar Service Account
```bash
# 1. Crear Service Account en GCP Console
# 2. Asignar roles: BigQuery Data Editor, Data Catalog Admin, Dataplex Admin
# 3. Descargar key JSON como 'service-account-key.json'
# 4. Configurar variables de entorno

export GOOGLE_APPLICATION_CREDENTIALS="path/to/service-account-key.json"
export GOOGLE_CLOUD_PROJECT="your-project-id"
```

#### 3. Instalar Dependencias
```bash
pip install -r requirements.txt
```

### Comandos de Ejecución

#### Ejecutar Scripts Individuales
```bash
# Catalogación automatizada
python scripts/catalog_automation.py

# Aplicar Aspect Types
python scripts/aspect_types.py
```

#### Ejecutar con Docker
```bash
# Construir imagen
docker build -f docker/Dockerfile -t deacero-data-governance:latest .

# Ejecutar servicios individuales
docker-compose run catalog-automation
docker-compose run aspect-types

# Ejecutar pipeline completo
docker-compose run full-pipeline
```

#### CI/CD Pipeline
```bash
# El pipeline se ejecuta automáticamente en:
# - Push a main/develop
# - Pull requests a main
# - Ejecución manual via GitHub Actions
```

### Verificación de Resultados

1. **Dataplex UI:** Verificar metadatos y Aspect Types aplicados
2. **BigQuery:** Confirmar enmascaramiento de datos sensibles
3. **Data Quality:** Revisar porcentajes de cumplimiento
4. **Docker:** Validar contenedores funcionando correctamente

### Estructura del Proyecto

```
test-data-gov-dev/
├── config/
│   └── metadata_config.yaml      # Configuración de metadatos
├── scripts/
│   ├── catalog_automation.py     # Script de catalogación
│   └── aspect_types.py          # Script de Aspect Types
├── docker/
│   └── Dockerfile               # Imagen Docker
├── .github/workflows/
│   └── data-governance-ci.yml   # Pipeline CI/CD
├── docs/                        # Documentación adicional
├── screenshots/                 # Evidencias visuales
├── docker-compose.yml          # Orquestación de contenedores
├── requirements.txt            # Dependencias Python
└── README.md                  # Este archivo
```

### Suposiciones Realizadas

1. **Proyecto GCP:** Se asume acceso completo a un proyecto de GCP
2. **Permisos:** Usuario con roles administrativos para Dataplex/BigQuery
3. **Región:** us-central1 como región por defecto
4. **Dataset:** Acceso al dataset público `bigquery-public-data.stackoverflow`
5. **Autenticación:** Service Account con permisos apropiados

---

**¡Demuestra tu expertise en gobierno de datos y buena suerte!** 🎯

---

## 📊 Análisis de Gobernanza de Datos

### Análisis de Linaje de Datos

El **linaje de datos** es el mapeo completo del flujo de información desde su origen hasta su destino final, mostrando todas las transformaciones, dependencias y relaciones entre datasets. En nuestro caso de Stack Overflow, el linaje principal conecta tres entidades fundamentales:

**Relación de Linaje Principal:**
- `users` → `posts_questions` → `posts_answers`

La tabla `users` es la entidad maestra que contiene la información de identidad de los usuarios (PII). La tabla `posts_questions` se conecta a `users` a través del campo `owner_user_id`, estableciendo qué usuario creó cada pregunta. Similarmente, `posts_answers` se vincula tanto a `users` (quien respondió) como a `posts_questions` (a qué pregunta responde).

**Valor para el Community Manager:**
Para un Community Manager, entender este linaje es crucial porque le permite rastrear el impacto completo de cualquier cambio o problema de calidad. Si detecta contenido inapropiado en una respuesta, puede identificar inmediatamente al usuario responsable, revisar todas sus preguntas y respuestas relacionadas, y tomar decisiones informadas sobre moderación. El linaje también facilita análisis de engagement, identificando usuarios más activos y patrones de participación en la comunidad.

### Métricas de Cumplimiento Implementadas

1. **Cobertura de Metadatos:** 100% de las tablas críticas catalogadas
2. **Seguridad de Datos:** Enmascaramiento aplicado a campos PII
3. **Calidad de Datos:** Monitoreo de integridad referencial
4. **Automatización:** Pipeline CI/CD para governance-as-code

### Comunicación con Stakeholders

- **Ejecutivos:** Dashboards de cumplimiento y métricas de gobierno
- **Equipos Técnicos:** Documentación automatizada y alertas de calidad
- **Usuarios de Negocio:** Catálogo de datos self-service

---

**© 2025 DeAcero Analytics Team**
