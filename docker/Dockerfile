# Dockerfile para Data Governance Automation
FROM python:3.11-slim

# Metadatos del contenedor
LABEL maintainer="DeAcero Data Governance Team"
LABEL description="Automatización de gobierno de datos para Stack Overflow dataset"
LABEL version="1.0"

# Configurar directorio de trabajo
WORKDIR /app

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    git \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Copiar archivos de dependencias
COPY requirements.txt .

# Instalar dependencias de Python
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copiar código fuente
COPY scripts/ ./scripts/
COPY config/ ./config/

# Crear directorio para credenciales
RUN mkdir -p /app/credentials

# Configurar variables de entorno
ENV PYTHONPATH=/app
# GOOGLE_APPLICATION_CREDENTIALS será configurado por docker-compose o runtime

# Crear usuario no-root
RUN useradd -m -u 1000 datagovernance && \
    chown -R datagovernance:datagovernance /app
USER datagovernance

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD python -c "import sys; sys.exit(0)" || exit 1

# Comando por defecto
CMD ["python", "scripts/catalog_automation.py"]


