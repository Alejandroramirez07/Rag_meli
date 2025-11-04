# Usamos una imagen base que ya incluye Java, Chrome y Chromedriver 
# para que Selenium pueda ejecutar el checker de Servientrega.
FROM selenium/standalone-chrome:latest

# Cambiar al usuario root para instalar paquetes
USER root

# Instalar Python 3.11, pip y dependencias necesarias para LLM/RAG
RUN apt-get update && apt-get install -y \
    python3.11 \
    python3-pip \
    python3.11-venv \
    build-essential \
    git \
    && rm -rf /var/lib/apt/lists/*

# Crear y activar un entorno virtual para aislar dependencias
ENV VIRTUAL_ENV=/opt/venv
RUN python3.11 -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

# Instalar las librerías de Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Directorio de trabajo en el contenedor
WORKDIR /app

# Copiar el código de la aplicación (asumiendo main_workflow.py y servientrega_checker.py)
COPY main_workflow.py /app/
COPY servientrega_checker.py /app/

# IMPORTANTE: Copiar la base de datos vectorial pre-construida (si existe)
# Asume que ya tienes el folder ./chroma_db creado localmente
COPY chroma_db /app/chroma_db/

# El puerto por defecto de Streamlit
EXPOSE 8501

# Comando para ejecutar la aplicación
# NOTA: La variable de entorno OLLAMA_HOST debe ser definida en docker-compose
CMD ["streamlit", "run", "main_workflow.py"]
