# USAR UNA IMAGEN BASE QUE YA TIENE PYTHON Y MUCHAS LIBRERÍAS DE DL (como PyTorch)
# Esto acelera enormemente el paso 5 de la construcción.
FROM nvidia/cuda:12.1.1-runtime-ubuntu22.04

# --- 1. Instalar Google Chrome y dependencias (Para Selenium) ---
# Instalar dependencias necesarias para Chrome (basado en Ubuntu)
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    libnss3 \
    libgconf-2-4 \
    --no-install-recommends \
    && rm -rf /var/lib/apt/lists/*

# Instalar Google Chrome
# Nota: La base de NVIDIA ya tiene un entorno Linux, por lo que podemos instalar Chrome.
RUN wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb && \
    apt install -y ./google-chrome-stable_current_amd64.deb && \
    rm google-chrome-stable_current_amd64.deb

# --- 2. Entorno Python y Dependencias ---
# La imagen base ya tiene Python y Pip.
WORKDIR /app

# Instalar dependencias de Python (debe ser muy rápido, ya que torch ya está preinstalado)
COPY requirements.txt .
# Usamos --break-system-packages para instalar paquetes en el Python del sistema de la imagen base
RUN pip install --no-cache-dir -r requirements.txt --break-system-packages

# --- 3. Copiar la Aplicación ---
COPY main_workflow.py /app/
COPY servientrega_checker.py /app/
# CRÍTICO: Copiar la base de datos vectorial
COPY chroma_db /app/chroma_db/

# --- 4. Configuración de Entorno para Streamlit y Selenium ---
# Asegurar que los binarios de Chrome/Chromedriver estén en el PATH
ENV PATH="/usr/bin/:$PATH"
# CRÍTICO: Configurar la URL de Ollama para la app
ENV OLLAMA_HOST "http://ollama:11434"

EXPOSE 8501

# Comando para iniciar la aplicación Streamlit
CMD ["streamlit", "run", "main_workflow.py", "--server.port", "8501", "--server.enableCORS", "true"]


