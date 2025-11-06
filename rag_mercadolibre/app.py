import streamlit as st
import re
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain_ollama import OllamaLLM
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough, RunnableLambda # <-- Se agregó RunnableLambda
from langchain_core.messages import HumanMessage, AIMessage
from servientrega_checker import check_servientrega_status 

# --- Configuración de Streamlit UI ---
st.set_page_config(page_title="🤖 Asistente de Catálogo Meli", layout="wide")
st.title("🛒 Asistente de Catálogo Meli")
st.caption("Pregúntame sobre productos o rastrea un envío (ej: rastrea guía 2259180939)")

# --- Configuración de LangChain/RAG (Asegúrate de que Ollama esté corriendo Mistral) ---
@st.cache_resource
def setup_rag_chain():
    # 1. Embeddings
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

    # 2. Vector DB (Cargando la DB persistente)
    vectorstore = Chroma(persist_directory="./chroma_db", embedding_function=embeddings)
    
    # Recuperación y contexto
    retriever = vectorstore.as_retriever(search_kwargs={"k": 4}) 

    # 3. LLM local
    llm = OllamaLLM(model="mistral", temperature=0.3, num_ctx=1024)

    # 4. Prompt: Usamos from_template para manejar el historial como texto plano.
    prompt_template = """
    Eres un asistente experto en el catálogo de productos de la tienda.
    Tu objetivo es responder a las preguntas del usuario sobre el catálogo.

    Instrucciones de respuesta:
    1. Responde concisa y solo con base en la información del contexto.
    2. Si el contexto no es suficiente para responder la pregunta actual, haz un resumen de los productos mencionados en el contexto.

    ---
    Historial de Conversación:
    {history}
    ---
    
    Contexto de Catálogo (Documentos RAG):
    {context}
    
    Pregunta Actual:
    {question}

    Respuesta en español:
    """
    prompt = ChatPromptTemplate.from_template(prompt_template)
    
    # Serializa la lista de documentos en una sola cadena de texto.
    def format_docs(docs):
        # Los une usando un separador claro
        return "\n\n---\n\n".join(doc.page_content for doc in docs)


    # 5. RAG Chain:
    # RunnableLambda para extraer explícitamente solo el valor de la clave.
    rag_chain = (
        {
            # 'question' (string) al retriever
            "context": RunnableLambda(lambda x: x["question"]) | retriever | format_docs,
            
            # Pasa el valor de 'question' y 'history' directamente al prompt
            "question": RunnableLambda(lambda x: x["question"]),   
            "history": RunnableLambda(lambda x: x["history"])     
        }
        | prompt
        | llm
    )
    return rag_chain

# Inicializar la chain global
try:
    rag_chain = setup_rag_chain()
except Exception as e:
    st.error(f"Error al configurar la cadena RAG. ¿Está Ollama corriendo y el modelo 'mistral' cargado? Error: {e}")
    st.stop()


# --- 1. Inicialización del Historial de Chat ---
if "messages" not in st.session_state:
    st.session_state["messages"] = [
        {"role": "assistant", "content": "¡Hola! Soy tu asistente de Catálogo Meli. Pregúntame sobre nuestros productos o dame un número de guía para rastrear tu envío."}
    ]

# --- 2. Renderizar Mensajes Anteriores ---
for msg in st.session_state.messages:
    # Usamos st.chat_message para mostrar los iconos de 'user' o 'assistant'
    st.chat_message(msg["role"]).write(msg["content"])


# --- 3. Manejo de Nueva Entrada del Usuario ---
if prompt := st.chat_input("Escribe tu pregunta o número de guía aquí..."):
    
    # Añadir el mensaje del usuario al historial y mostrarlo inmediatamente
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)

    # Iniciar el contenedor para la respuesta del asistente
    with st.chat_message("assistant"):
        
        # Preparamos el contexto para el LLM: El historial y la pregunta
        history_text = ""
        for msg in st.session_state.messages:
            # Excluimos el mensaje actual para que vaya en la variable {question}
            if msg["content"] != prompt:
                 history_text += f"[{msg['role'].capitalize()}]: {msg['content']}\n"
        
        # Si el historial está vacío (primer mensaje), evitamos enviar una línea de más
        if not history_text:
             history_text = "N/A"
        
        # --- LÓGICA DE BIFURCACIÓN HÍBRIDA (RAG o Herramienta) ---
        
        # 1. Intentar detectar un número de guía de Servientrega (10 dígitos)
        tracking_number_match = re.search(r'\b(\d{10})\b', prompt)
        
        if tracking_number_match:
            tracking_number = tracking_number_match.group(1)
            
            # --- Ruta de Herramienta (Selenium) ---
            response_placeholder = st.empty()
            response_placeholder.info(f"Ruta de Herramienta: Detectado número de guía **{tracking_number}**.")
            
            with st.spinner(f"🌐 Consultando estado de envío para {tracking_number} en Servientrega..."):
                try:
                    status_result = check_servientrega_status(tracking_number)
                    final_response = f"**📦 Estado del Envío {tracking_number}:**\n\n{status_result}"
                    response_placeholder.success("Consulta completada. Mostrando resultado.")

                except Exception as e:
                    final_response = f"⚠️ Hubo un error al intentar rastrear el envío {tracking_number}. Por favor, verifica el número e intenta más tarde. Detalle del error: {e}"
                    response_placeholder.error("Error en la consulta de rastreo.")
            
            st.markdown(final_response)

        else:
            # --- Ruta RAG (Consulta de Catálogo) ---
            response_placeholder = st.empty()
            response_placeholder.info("Ruta RAG: Consultando Catálogo de Productos...")
            
            try:
                # La nueva estructura RAG requiere ambas claves: question y history
                chain_input = {
                    "question": prompt, 
                    "history": history_text
                }
                
                with st.spinner("🧠 Generando respuesta con Ollama Mistral..."):
                    final_response = rag_chain.invoke(chain_input)
                
                response_placeholder.success("Respuesta generada.")

            except Exception as e:
                # El error detallado para el desarrollador
                print(f"ERROR RAG: {e}")
                final_response = f"⚠️ Ocurrió un error al comunicarse con el modelo LLM. Asegúrate de que Ollama esté activo. Error: '{e}'"
                response_placeholder.error("Error en la generación RAG.")
                
            st.markdown(final_response)


        # --- 4. Almacenar la Respuesta del Asistente en el Historial ---
        st.session_state.messages.append({"role": "assistant", "content": final_response})