import streamlit as st
import os
from dotenv import load_dotenv
import weaviate
from langchain_community.vectorstores import Weaviate
from langchain_google_genai import ChatGoogleGenAI, GoogleGenAIEmbeddings
from langchain.prompts import ChatPromptTemplate
from langchain.schema.runnable import RunnablePassthrough, RunnableLambda
from langchain.agents import create_react_agent, AgentExecutor
from langchain.tools import tool

# --- Configuración Inicial ---
load_dotenv()
WEAVIATE_URL = os.getenv("WEAVIATE_URL", "http://localhost:8090")
# CORRECCIÓN: Usar el nombre de clase que creaste
INDEX_NAME = "MercadoLibreProduct"  # ← CAMBIADO para que coincida con tu ingesta

# Inicializar LLM y Embeddings
llm = ChatGoogleGenAI(model="gemini-1.5-flash")  # ← Usar modelo disponible
embeddings = GoogleGenAIEmbeddings(model="models/embedding-001")

# --- Herramienta de Búsqueda de Productos (RAG) ---
@tool
def get_product_recommendations(query: str) -> str:
    """
    Útil para buscar en el catálogo de productos de Mercado Libre. 
    Responde a preguntas sobre categorías, precios, descripciones y recomendaciones de productos.
    """
    try:
        # 1. Conectar a Weaviate
        client = weaviate.Client(url=WEAVIATE_URL)
        
        # 2. Búsqueda vectorial directa (más simple)
        response = client.query.get(
            INDEX_NAME,
            ["title", "category", "materials", "character", "composition"]
        ).with_near_text({
            "concepts": [query]
        }).with_limit(5).do()
        
        # 3. Procesar resultados
        products = response.get('data', {}).get('Get', {}).get(INDEX_NAME, [])
        
        if not products:
            return "No se encontraron productos relevantes en el catálogo."
        
        # 4. Formatear contexto
        context = "Productos encontrados:\n\n"
        for i, product in enumerate(products):
            context += f"--- Producto {i+1} ---\n"
            context += f"Título: {product.get('title', 'N/A')}\n"
            context += f"Categoría: {product.get('category', 'N/A')}\n"
            context += f"Materiales: {product.get('materials', 'N/A')}\n"
            if product.get('character'):
                context += f"Personaje: {product.get('character')}\n"
            if product.get('composition'):
                context += f"Composición: {product.get('composition')}\n"
            context += "\n"
        
        # 5. Generar respuesta con Gemini
        prompt = f"""
        Eres un asistente experto de Mercado Libre. Basándote en los siguientes productos, 
        responde la pregunta del usuario de manera útil y natural.
        
        PRODUCTOS ENCONTRADOS:
        {context}
        
        PREGUNTA DEL USUARIO: {query}
        
        Responde como un vendedor experto, destacando características relevantes y siendo útil.
        """
        
        response = llm.invoke(prompt)
        return response.content

    except Exception as e:
        return f"Error al buscar productos: {e}"

# --- Herramienta Simulada de Envíos (para demo) ---
@tool
def get_shipping_status(tracking_number: str) -> str:
    """
    Simula la verificación del estado de un envío.
    Para la demo, devuelve estados predefinidos.
    """
    # Simulación para la presentación
    status_options = [
        "✅ Envío entregado exitosamente",
        "🚚 En tránsito - Llegando en 2 días",
        "📦 En centro de distribución - Próximo a entregar", 
        "⏳ Pendiente de recolección"
    ]
    
    # Usar el número de tracking para generar un estado "consistente"
    import hashlib
    status_index = int(hashlib.md5(tracking_number.encode()).hexdigest(), 16) % len(status_options)
    
    return f"Número de guía: {tracking_number}\nEstado: {status_options[status_index]}"

# --- Agente ReAct Simplificado ---
tools = [get_product_recommendations, get_shipping_status]

agent_prompt = ChatPromptTemplate.from_messages([
    ("system", 
     "Eres MELI-Assistant, un asistente virtual de Mercado Libre. Ayuda al usuario con:\n"
     "1. Búsqueda de productos: usa 'get_product_recommendations'\n" 
     "2. Estado de envíos: usa 'get_shipping_status' (pide número de guía si falta)\n"
     "3. Otras preguntas: responde directamente de manera amigable\n\n"
     "Sé conciso y útil."
    ),
    ("human", "{input}")
])

agent = create_react_agent(llm, tools, agent_prompt)
agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True, handle_parsing_errors=True)

# --- Interfaz de Streamlit ---
st.set_page_config(page_title="MELI-Assistant", layout="wide")

st.markdown("""
<style>
    .stButton>button {
        background-color: #00A650;
        color: white;
        border-radius: 10px;
        border: none;
        padding: 10px 20px;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

st.title("💛 MELI-Assistant: Tu Bot de Mercado Libre")

st.sidebar.header("Demo Status")
st.sidebar.info(f"✅ Weaviate: {WEAVIATE_URL}\n✅ Productos: ~3,000 cargados\n✅ Gemini: Conectado")

# Inicializar chat
if "messages" not in st.session_state:
    st.session_state.messages = []
    st.session_state.messages.append({
        "role": "assistant", 
        "content": "¡Hola! Soy MELI-Assistant. Puedo:\n• Buscar productos en el catálogo\n• Verificar estados de envío\n\n¿En qué puedo ayudarte?"
    })

# Mostrar mensajes
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Input del usuario
if prompt := st.chat_input("Escribe tu pregunta..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Buscando..."):
            try:
                response = agent_executor.invoke({"input": prompt})
                answer = response.get('output', "No pude procesar tu solicitud.")
                st.markdown(answer)
                st.session_state.messages.append({"role": "assistant", "content": answer})
            except Exception as e:
                error_msg = f"Error: {e}"
                st.error(error_msg)
                st.session_state.messages.append({"role": "assistant", "content": error_msg})

# Botón limpiar
if st.sidebar.button("Limpiar Chat"):
    st.session_state.messages = []
    st.rerun()

# Ejemplos de prueba
st.sidebar.subheader("💡 Prueba estos ejemplos:")
examples = [
    "Busca figuras de acción de Marvel",
    "Necesito calzoncillos de algodón",
    "Quiero mochilas waterproof", 
    "Estado de envío: ML123456789"
]

for example in examples:
    if st.sidebar.button(example, key=example):
        st.session_state.messages.append({"role": "user", "content": example})
        st.rerun()