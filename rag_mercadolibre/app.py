import streamlit as st
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain_ollama import OllamaLLM
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough

# --- Configuración de la app
st.set_page_config(page_title="🛍️ Asistente de Catálogo Meli", layout="centered")
st.title("🛍️ Asistente del Catálogo MercadoLibre")

# --- 1️⃣ Embeddings
@st.cache_resource
def get_embeddings():
    return HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

# --- 2️⃣ Carga del vector store (asegúrate de tener ./chroma_db generado)
@st.cache_resource
def get_vectorstore():
    embeddings = get_embeddings()
    return Chroma(persist_directory="./chroma_db", embedding_function=embeddings)

# --- 3️⃣ Cargar el modelo local
@st.cache_resource
def get_llm():
    return OllamaLLM(model="mistral", temperature=0.1)

# --- 4️⃣ Construir el RAG pipeline
@st.cache_resource
def build_rag_chain():
    vectorstore = get_vectorstore()
    retriever = vectorstore.as_retriever(search_kwargs={"k": 2})
    llm = get_llm()

    prompt = ChatPromptTemplate.from_template("""
    Eres un asistente experto en el catálogo de productos.
    Responde solo con base en la información del contexto.
    Si no sabes la respuesta, di: "No tengo esa información en el catálogo."

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

# --- 5️⃣ Interfaz de usuario
query = st.text_input("Haz tu pregunta sobre los productos:")

if query:
    with st.spinner("Buscando en el catálogo..."):
        response = rag_chain.invoke(query)
    st.write("### 💬 Respuesta:")
    st.success(response)
