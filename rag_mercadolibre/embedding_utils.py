import os
import time
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

EMBEDDING_MODEL = "models/embedding-001"

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
else:
    print(" ADVERTENCIA: GEMINI_API_KEY no encontrada en embedding_utils")

def get_embedding(text: str, retries=3) -> list[float]:
    """Genera el embedding para un texto dado, con reintentos."""
    if not GEMINI_API_KEY:
        print(" Error: No hay API key de Gemini configurada")
        return None
        
    for attempt in range(retries):
        try:
            print(f"🔄 Generando embedding para: '{text[:50]}...'")
            
            result = genai.embed_content(
                model=EMBEDDING_MODEL,
                content=text
            )
            
            if hasattr(result, 'embedding'):
                embedding = result.embedding
                print(f" Embedding generado: {len(embedding)} dimensiones")
                return embedding
            elif isinstance(result, dict) and 'embedding' in result:
                embedding = result['embedding']
                print(f" Embedding generado: {len(embedding)} dimensiones")
                return embedding
            else:
                print(f" Estructura de respuesta inesperada: {type(result)}")
                
        except Exception as e:
            print(f" Error en intento {attempt + 1}: {e}")
            if attempt < retries - 1:
                time.sleep(2)
    
    print(f" Fallo después de {retries} intentos")
    return None