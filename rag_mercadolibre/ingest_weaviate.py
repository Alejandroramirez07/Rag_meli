import os
import sys
import pandas as pd
from dotenv import load_dotenv
from tqdm import tqdm
import time 

# --- 1. CONFIGURACIÓN DE DEPENDENCIAS EXTERNAS ---
try:
    import google.generativeai as genai
    from weaviate import WeaviateClient 
    from weaviate.connect import ConnectionParams
    from weaviate.collections.classes.config import Configure, DataType, Property, VectorDistances 
except ImportError as e:
    print(f"❌ Error de importación: {e}") 
    sys.exit(1)

# --- 2. CONSTANTES DE CONFIGURACIÓN ---
WEAVIATE_CLASS_NAME = "MercadoLibreProduct"
WEAVIATE_HOST = "localhost"
WEAVIATE_PORT = 8090 
EMBEDDING_MODEL = "models/embedding-001"
EXCEL_FILE_PATH = "data/Fichas_tecnicas-2025_10_30-22_24.xlsx" 

# Campos más importantes para embeddings (reduce costos)
IMPORTANT_FIELDS = ['Título', 'Categoria', 'Materiales', 'Personaje', 'Composición', 'Tipo de calzoncillo', 'Tipo de medias', 'Capacidad de la mochila']

# Mapeo de columnas de Excel a propiedades de Weaviate
SCHEMA_MAP = {
    'Título': {'name': 'title', 'data_type': DataType.TEXT, 'vectorize': True},
    'Personaje': {'name': 'character', 'data_type': DataType.TEXT, 'vectorize': True},
    'Materiales': {'name': 'materials', 'data_type': DataType.TEXT, 'vectorize': True},
    'Peso': {'name': 'weight_g', 'data_type': DataType.NUMBER, 'vectorize': False},
    'Unidad de Peso': {'name': 'weight_unit', 'data_type': DataType.TEXT, 'vectorize': False},
    'Es articulada': {'name': 'is_articulated', 'data_type': DataType.BOOL, 'vectorize': False},
    'Es coleccionable': {'name': 'is_collectible', 'data_type': DataType.BOOL, 'vectorize': False},
    'Es bobblehead': {'name': 'is_bobblehead', 'data_type': DataType.BOOL, 'vectorize': False},
    'Incluye pilas': {'name': 'includes_batteries', 'data_type': DataType.BOOL, 'vectorize': False},
    'Talla': {'name': 'size', 'data_type': DataType.TEXT, 'vectorize': True},
    'Tipo de calzoncillo': {'name': 'brief_type', 'data_type': DataType.TEXT, 'vectorize': True},
    'Composición': {'name': 'composition', 'data_type': DataType.TEXT, 'vectorize': True},
    'Material principal': {'name': 'main_material', 'data_type': DataType.TEXT, 'vectorize': True},
    'Tiro del calzoncillo': {'name': 'brief_rise', 'data_type': DataType.TEXT, 'vectorize': True},
    'Tipo de medias': {'name': 'sock_type', 'data_type': DataType.TEXT, 'vectorize': True},
    'Tipo de largo': {'name': 'sock_length', 'data_type': DataType.TEXT, 'vectorize': True},
    'Tipo de pantie': {'name': 'pantie_type', 'data_type': DataType.TEXT, 'vectorize': True},
    'Tiro de la pantie': {'name': 'pantie_rise', 'data_type': DataType.TEXT, 'vectorize': True},
    'Capacidad de la mochila': {'name': 'capacity_liters', 'data_type': DataType.TEXT, 'vectorize': True},
    'Altura': {'name': 'height_cm', 'data_type': DataType.TEXT, 'vectorize': False},
    'Ancho': {'name': 'width_cm', 'data_type': DataType.TEXT, 'vectorize': False},
    'Profundidad': {'name': 'depth_cm', 'data_type': DataType.TEXT, 'vectorize': False},
    'Con compartimento para portátil': {'name': 'has_laptop_compartment', 'data_type': DataType.BOOL, 'vectorize': False},
    'Con ruedas': {'name': 'has_wheels', 'data_type': DataType.BOOL, 'vectorize': False},
    'Es a prueba de agua': {'name': 'is_waterproof', 'data_type': DataType.BOOL, 'vectorize': False},
    'Categoria': {'name': 'category', 'data_type': DataType.TEXT, 'vectorize': True},
}

def initialize_clients():
    """Inicializa y autentica los clientes de Gemini y Weaviate."""
    print("⚙️ Inicializando clientes...")
    
    load_dotenv()
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

    if not GEMINI_API_KEY:
        print("❌ ERROR: La clave 'GEMINI_API_KEY' no se encontró en el archivo .env.")
        sys.exit(1)

    print("✅ Clave GEMINI_API_KEY cargada")

    # Inicialización del cliente Gemini
    try:
        genai.configure(api_key=GEMINI_API_KEY)
        print("✅ Cliente Gemini inicializado")
        
        # Probar la conexión
        print("🧪 Probando conexión a Gemini...")
        test_embedding = get_embedding("test")
        if test_embedding:
            print(f"✅ Conexión a Gemini verificada - Embedding de {len(test_embedding)} dimensiones")
        else:
            print("❌ No se pudo generar embedding de prueba")
            
    except Exception as e:
        print(f"❌ Error al inicializar Gemini: {e}")
        sys.exit(1)

    # Inicialización del cliente Weaviate
    weaviate_client = None
    for attempt in range(5):
        try:
            weaviate_client = WeaviateClient(
                ConnectionParams.from_params(
                    http_host=WEAVIATE_HOST,
                    http_port=WEAVIATE_PORT,
                    http_secure=False,
                    grpc_host=WEAVIATE_HOST,
                    grpc_port=50051,
                    grpc_secure=False
                )
            )
            weaviate_client.connect()
            
            if weaviate_client.is_live():
                print(f"✅ Conexión exitosa con Weaviate")
                return weaviate_client 
            else:
                raise Exception("Weaviate no responde")
                
        except Exception as e:
            print(f"⏳ (Intento {attempt + 1}/5) Error conectando a Weaviate: {e}")
            if attempt < 4:
                time.sleep(5)
            else:
                print("❌ Falló la conexión a Weaviate")
                sys.exit(1)

def optimize_text_for_embedding(text: str, max_length: int = 400) -> str:
    """
    Optimiza el texto para reducir costos de embedding.
    
    Args:
        text: Texto original
        max_length: Longitud máxima en caracteres
    
    Returns:
        Texto optimizado para embedding
    """
    # Remover espacios extras
    text = ' '.join(text.split())
    
    # Limitar longitud si es necesario
    if len(text) > max_length:
        # Intentar cortar en un límite lógico
        truncated = text[:max_length]
        # Buscar el último separador para cortar limpiamente
        last_separator = max(
            truncated.rfind(' | '),
            truncated.rfind('. '),
            truncated.rfind(', ')
        )
        if last_separator > max_length * 0.7:  # Si encontramos un buen punto de corte
            text = truncated[:last_separator]
        else:
            text = truncated + "..."
    
    return text

def get_embedding(text: str, retries=3) -> list[float]:
    """Genera el embedding para un texto dado, con reintentos."""
    # Optimizar texto para reducir costos
    optimized_text = optimize_text_for_embedding(text)
    
    # Mostrar ahorro de caracteres
    original_len = len(text)
    optimized_len = len(optimized_text)
    if original_len != optimized_len:
        savings = original_len - optimized_len
        print(f"💰 Optimizado: {original_len} → {optimized_len} chars (ahorro: {savings} chars)")
    
    for attempt in range(retries):
        try:
            print(f"🔄 Generando embedding (intento {attempt + 1})...")
            
            result = genai.embed_content(
                model=EMBEDDING_MODEL,
                content=optimized_text
            )
            
            print(f"✅ Llamada a API exitosa")
            
            if hasattr(result, 'embedding'):
                embedding = result.embedding
                print(f"✅ Embedding extraído: {len(embedding)} dimensiones")
                return embedding
            elif isinstance(result, dict) and 'embedding' in result:
                embedding = result['embedding']
                print(f"✅ Embedding extraído: {len(embedding)} dimensiones")
                return embedding
            
            print(f"❌ No se pudo extraer embedding - estructura: {type(result)}")
                
        except Exception as e:
            error_msg = str(e)
            print(f"⚠️ Error en intento {attempt + 1}: {error_msg}")
            
            if attempt < retries - 1:
                time.sleep(2)
    
    print(f"❌ Fallo después de {retries} intentos")
    return None

def create_schema(client: WeaviateClient):
    """Crea la clase de Weaviate."""
    
    if client.collections.exists(WEAVIATE_CLASS_NAME):
        print(f"⚠️ Clase '{WEAVIATE_CLASS_NAME}' ya existe. Eliminándola...")
        client.collections.delete(WEAVIATE_CLASS_NAME)
    
    properties_list = [
        Property(name=prop_config['name'], data_type=prop_config['data_type'])
        for prop_config in SCHEMA_MAP.values()
    ]

    client.collections.create(
        name=WEAVIATE_CLASS_NAME,
        properties=properties_list,
        vectorizer_config=Configure.Vectorizer.none(),
        vector_index_config=Configure.VectorIndex.hnsw(
            distance_metric=VectorDistances.COSINE,
        ),
    )
    print(f"✅ Esquema '{WEAVIATE_CLASS_NAME}' creado")

def load_and_preprocess_data(file_path: str) -> pd.DataFrame:
    """Carga el archivo Excel, combina hojas y prepara los datos."""
    print("⚙️ Analizando y combinando hojas de cálculo...")
    
    all_data = []

    try:
        with pd.ExcelFile(file_path) as xls:
            sheet_names = xls.sheet_names
            
            for sheet_name in tqdm(sheet_names, desc="Procesando hojas"):
                
                if sheet_name.lower() in ["hidden", "presentacion"]:
                    continue
                    
                try:
                    df = pd.read_excel(xls, sheet_name=sheet_name, header=3)
                    
                    if 'Título' not in df.columns:
                        print(f"⚠️ Saltando {sheet_name}: falta la columna 'Título'.")
                        continue

                    df['Categoria'] = sheet_name.split('(')[0].strip()
                    
                    valid_cols = [col for col in df.columns if col in SCHEMA_MAP or col == 'Categoria']
                    df = df[valid_cols].copy()
                    
                    # Limpieza: Convertir booleanos
                    bool_cols = ['Es articulada', 'Es coleccionable', 'Es bobblehead', 'Incluye pilas', 'Con compartimento para portátil', 'Con ruedas', 'Es a prueba de agua']
                    for col in bool_cols:
                        if col in df.columns:
                            df[col] = df[col].astype(str).str.strip().str.lower().map({'sí': True, 'sì': True, 'no': False, 'nan': pd.NA, 'none': pd.NA, '': pd.NA})
                    
                    # CONVERSIÓN CRÍTICA: Convertir columnas numéricas a string para Weaviate
                    text_columns = ['height_cm', 'width_cm', 'depth_cm', 'capacity_liters', 'weight_g']
                    for col in text_columns:
                        if col in df.columns:
                            df[col] = df[col].astype(str)
                            
                    df = df.dropna(subset=['Título'])

                    print(f"✅ Hoja procesada: {sheet_name} ({len(df)} filas)")
                    all_data.append(df)
                    
                except Exception as e:
                    if "Data Validation extension is not supported" not in str(e):
                        print(f"❌ Error al procesar la hoja '{sheet_name}': {e}")
                    continue

    except FileNotFoundError:
        print(f"❌ ERROR: Archivo no encontrado en la ruta: {file_path}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ ERROR al leer el archivo Excel: {e}")
        sys.exit(1)

    if not all_data:
        print("❌ ERROR: No se encontraron datos válidos para la ingesta.")
        sys.exit(1)

    combined_df = pd.concat(all_data, ignore_index=True)
    
    rename_map = {k: v['name'] for k, v in SCHEMA_MAP.items() if k in combined_df.columns}
    combined_df = combined_df.rename(columns=rename_map)

    print(f"\n📊 Data combinada final: {len(combined_df)} productos.")
    return combined_df

def generate_vector_text(row: pd.Series) -> str:
    """
    Genera la cadena de texto optimizada para la vectorización.
    Solo incluye los campos más importantes para reducir costos.
    """
    
    text_parts = []
    
    # Solo usar campos importantes para embeddings (reduce costos)
    for col_name_es in IMPORTANT_FIELDS:
        if col_name_es not in SCHEMA_MAP:
            continue
            
        prop_name_en = SCHEMA_MAP[col_name_es]['name']
        value = row.get(prop_name_en)
        
        if pd.isna(value) or value is None or str(value).strip() == "":
            continue
            
        if isinstance(value, bool):
            value_str = 'Sí' if value else 'No'
        else:
            value_str = str(value).strip()
            
        text_parts.append(f"{col_name_es}: {value_str}")

    return " | ".join(text_parts)

def clean_object_for_weaviate(obj: dict) -> dict:
    """Limpia y convierte los valores del objeto para Weaviate."""
    cleaned = {}
    for key, value in obj.items():
        if pd.isna(value) or value is None:
            cleaned[key] = None
        elif isinstance(value, (int, float)):
            # Convertir números a string si la propiedad es TEXT en Weaviate
            if key in ['height_cm', 'width_cm', 'depth_cm', 'capacity_liters']:
                cleaned[key] = str(value)
            else:
                cleaned[key] = value
        elif isinstance(value, bool):
            cleaned[key] = value
        else:
            cleaned[key] = str(value).strip() if str(value).strip() != "" else None
    return cleaned

def calculate_cost_savings(data_df: pd.DataFrame) -> dict:
    """Calcula y muestra el ahorro de costos esperado."""
    print("\n💰 CALCULANDO AHORRO DE COSTOS...")
    
    # Generar textos de ejemplo para calcular longitud promedio
    sample_texts = []
    for _, row in data_df.head(10).iterrows():
        full_text = generate_vector_text(row)
        optimized_text = optimize_text_for_embedding(full_text)
        sample_texts.append((len(full_text), len(optimized_text)))
    
    avg_original = sum(t[0] for t in sample_texts) / len(sample_texts)
    avg_optimized = sum(t[1] for t in sample_texts) / len(sample_texts)
    
    total_products = len(data_df)
    cost_per_1k_chars = 0.0001  # $0.0001 per 1000 characters
    
    original_cost = (total_products * avg_original / 1000) * cost_per_1k_chars
    optimized_cost = (total_products * avg_optimized / 1000) * cost_per_1k_chars
    savings = original_cost - optimized_cost
    savings_percent = (savings / original_cost) * 100 if original_cost > 0 else 0
    
    print(f"📊 Estadísticas de texto:")
    print(f"   • Longitud promedio original: {avg_original:.0f} caracteres")
    print(f"   • Longitud promedio optimizada: {avg_optimized:.0f} caracteres")
    print(f"   • Reducción: {avg_original - avg_optimized:.0f} caracteres por producto")
    print(f"   • Porcentaje de reducción: {((avg_original - avg_optimized) / avg_original * 100):.1f}%")
    print(f"\n💰 Estimación de costos:")
    print(f"   • Costo original: ${original_cost:.3f}")
    print(f"   • Costo optimizado: ${optimized_cost:.3f}")
    print(f"   • Ahorro total: ${savings:.3f} ({savings_percent:.1f}%)")
    
    return {
        'original_avg_chars': avg_original,
        'optimized_avg_chars': avg_optimized,
        'original_cost': original_cost,
        'optimized_cost': optimized_cost,
        'savings': savings
    }

def batch_ingest(weaviate_client: WeaviateClient, data_df: pd.DataFrame):
    """Vectoriza y carga los datos en Weaviate de forma eficiente."""
    
    print("⚙️ Iniciando ingesta por lotes en Weaviate...")

    # Calcular ahorro de costos primero
    cost_info = calculate_cost_savings(data_df)
    
    # Procesar dataset completo
    test_mode = False  # Cambiar a False para procesar todo
    if test_mode:
        data_df = data_df.head(3)
        print("🧪 MODO PRUEBA: Procesando solo 3 productos")
    else:
        print("🚀 PROCESANDO DATASET COMPLETO")

    # Usar .loc para evitar el warning
    data_df = data_df.copy()
    data_df.loc[:, 'vector_text'] = data_df.apply(generate_vector_text, axis=1)

    example_text = data_df['vector_text'].iloc[0]
    optimized_example = optimize_text_for_embedding(example_text)
    print(f"✅ Texto del producto generado (ejemplo original):\n{example_text}")
    print(f"✅ Texto optimizado (ejemplo):\n{optimized_example}")
    print(f"⚙️ {len(data_df)} documentos listos para vectorización.")
    
    product_collection = weaviate_client.collections.get(WEAVIATE_CLASS_NAME)
    
    successful_count = 0
    failed_count = 0
    
    with product_collection.batch.dynamic() as batch:
        for _, row in tqdm(data_df.iterrows(), total=len(data_df), desc="Ingestando productos"):
            
            vector = get_embedding(row['vector_text']) 
            
            if vector is None:
                print(f"⚠️ Saltando producto (vector nulo): {row.get('title', 'N/A')}")
                failed_count += 1
                continue 

            data_object = row.drop(['vector_text']).to_dict()
            
            # LIMPIAR EL OBJETO PARA WEAVIATE
            cleaned_object = clean_object_for_weaviate(data_object)

            try:
                batch.add_object(
                    properties=cleaned_object,
                    vector=vector
                )
                successful_count += 1
                if successful_count % 100 == 0:  # Log cada 100 productos
                    print(f"📦 Progreso: {successful_count}/{len(data_df)} productos procesados")
            except Exception as e:
                print(f"❌ Error al añadir objeto: {e}")
                failed_count += 1
            
    print(f"\n📊 Resumen de ingesta:")
    print(f"✅ Objetos exitosos: {successful_count}")
    print(f"❌ Objetos fallidos: {failed_count}")
    print(f"💰 Costo estimado: ${cost_info['optimized_cost']:.3f}")
    print(f"💰 Ahorro estimado: ${cost_info['savings']:.3f}")

def verify_ingestion(weaviate_client: WeaviateClient):
    """Verifica que los datos se hayan ingerido correctamente."""
    print("\n🔍 Verificando ingesta...")
    
    product_collection = weaviate_client.collections.get(WEAVIATE_CLASS_NAME)
    
    # Contar objetos
    count = product_collection.aggregate.over_all(total_count=True)
    print(f"📊 Total de productos en Weaviate: {count.total_count}")
    
    # Obtener algunos ejemplos
    examples = product_collection.query.fetch_objects(limit=3)
    print(f"📝 Ejemplos de productos:")
    for i, obj in enumerate(examples.objects):
        print(f"  {i+1}. {obj.properties.get('title', 'N/A')}")

# --- 4. FUNCIÓN PRINCIPAL ---

if __name__ == "__main__":
    print("--- 🚀 Iniciando Ingestión de Catálogo (OPTIMIZADO) ---")
    
    weaviate_client = initialize_clients() 
    data_df = load_and_preprocess_data(EXCEL_FILE_PATH)
    create_schema(weaviate_client)
    batch_ingest(weaviate_client, data_df)
    verify_ingestion(weaviate_client)
    weaviate_client.close()
        
    print("--- ✅ Proceso de Ingestión Finalizado ---")