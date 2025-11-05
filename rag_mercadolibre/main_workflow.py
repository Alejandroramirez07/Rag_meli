import streamlit as st
import re 
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain_ollama import OllamaLLM
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough

# Import Servientrega checker function
from servientrega_checker import check_servientrega_status 

# --- Configuración de la app
st.set_page_config(page_title="🛍️ Asistente de Catálogo Meli", layout="centered")
st.title("🛍️ Asistente del Catálogo MercadoLibre")

# ---  Embeddings
@st.cache_resource
def get_embeddings():
    
    return HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

# ---  Carga del vector store (asegúrate de tener ./chroma_db generado)
@st.cache_resource
def get_vectorstore():
    embeddings = get_embeddings()
    return Chroma(persist_directory="./chroma_db", embedding_function=embeddings)

# ---  Cargar el modelo local
@st.cache_resource
def get_llm():
    return OllamaLLM(model="mistral", temperature=0.3)

# ---  Construir el RAG pipeline
@st.cache_resource
def build_rag_chain():
    vectorstore = get_vectorstore()
    retriever = vectorstore.as_retriever(search_kwargs={"k": 3})
    llm = get_llm()

    prompt = ChatPromptTemplate.from_template("""
    Eres un asistente experto en el catálogo de productos.
    Responde solo con base en la información del contexto.
    Si no sabes la respuesta, realiza un resumen de los productos en el catálogo.
    Lo mismo aplica si la consulta es vaga o general. Si hablan de productos, también se refieren a figuras"

    Contexto:
    {context}

    Pregunta:
    {question}

    Respuesta en español:
    """)

    return (
        {"context": retriever, "question": RunnablePassthrough()}
        | prompt
        | llm
    )

rag_chain = build_rag_chain()

# ---  Interfaz de usuario y Lógica de Ramificación
query = st.text_input("Haz tu pregunta sobre los productos o el estado de tu envío (ej: rastrea guía 2259180939):")

if query:
    # Lógica de Ramificación para el Rastreo de Servientrega
    
    # 1. Convertir la consulta a minúsculas para un manejo más fácil
    lower_query = query.lower()
    
    # 2. Buscar un patrón de número de guía (10 dígitos)
    # Patrón: \d{10} busca exactamente 10 dígitos.
    tracking_number_match = re.search(r'\d{10}', lower_query)
    
    # --- RAMIFICACIÓN DE EJECUCIÓN ---
    if tracking_number_match:
        #  Caso A: Un número de rastreo de 10 dígitos fue encontrado. 
        # Ejecutar el checker (PRIORIDAD AL RASTREO).
        tracking_number = tracking_number_match.group(0)
        
        st.info(f"Detectada consulta de rastreo. Buscando estado de guía: **{tracking_number}**")
        
        with st.spinner(f"Contactando a Servientrega para la guía {tracking_number}..."):
            # Llama a tu función del otro archivo
            status_result = check_servientrega_status(tracking_number)
        
        st.write("### 🚚 Estado del Envío:")
        
        # Muestra el resultado
        if "ERROR" in status_result:
            st.error(status_result)
        else:
            # Output limpio y exitoso basado en tu prueba
            st.success(f"Guía **{tracking_number}** - **{status_result}**")
            
    else:
        # 📚 Caso B: No se encontró un número de 10 dígitos. Ejecutar el pipeline RAG.
        st.info("Detectada consulta de catálogo. Buscando con RAG...")
        
        with st.spinner("Buscando en el catálogo..."):
            response = rag_chain.invoke(query)
            
        st.write("### 💬 Respuesta del Catálogo:")
        st.success(response)