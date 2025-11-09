# --- 1. USAR IMAGEN BASE ESTÁNDAR (Mejor compatibilidad y menor tamaño) ---
# Usamos python:3.11-slim-bookworm para un entorno ligero y estable y multi-arquitectura.
FROM python:3.11-slim-bookworm

# --- 2. Instalar dependencias del sistema para HuggingFace y Selenium ---
# Instalar Chromium (el navegador headless) y sus dependencias necesarias.
RUN apt-get update && apt-get install -y \
    chromium \
    chromium-driver \
    wget \
    gnupg \
    libnss3 \
    --no-install-recommends \
    && rm -rf /var/lib/apt/lists/*

# --- 3. Entorno Python y Dependencias ---
WORKDIR /app

# Instalar dependencias de Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# --- 4. Copiar la Aplicación ---
COPY main_workflow.py /app/
COPY servientrega_checker.py /app/
COPY chroma_db /app/chroma_db/
COPY ingest_weaviate.py /app/ 

# --- 5. Configuración de Entorno para Streamlit y Selenium ---
# Establecer el PATH del chromedriver.
ENV PATH="/usr/lib/chromium-browser:$PATH" 
# La variable OLLAMA_HOST fue eliminada ya que usamos Gemini.

EXPOSE 8501

# Comando para iniciar la aplicación Streamlit
CMD ["streamlit", "run", "main_workflow.py", "--server.port", "8501", "--server.enableCORS", "true"]