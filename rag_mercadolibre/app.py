# app.py
import streamlit as st
from rag_pipeline import create_or_load_vectorstore, create_qa_chain

st.set_page_config(page_title="Chatbot de Catálogo", layout="wide")
st.title("🛍️ Chatbot de Catálogo (Mercado Libre + Shopify)")

if "qa_chain" not in st.session_state:
    with st.spinner("Cargando índice (si es la primera vez, puede tardar un poco)..."):
        vectordb = create_or_load_vectorstore(recreate=False)
        st.session_state.qa_chain = create_qa_chain(vectordb)
        st.success("Índice cargado.")

qa = st.session_state.qa_chain

col1, col2 = st.columns([3,1])
with col1:
    user_q = st.text_input("Haz una pregunta sobre tu catálogo:", key="query_input")
    if user_q:
        with st.spinner("Buscando respuesta..."):
            out = qa({"query": user_q})
            answer = out["result"]
            st.markdown("**Respuesta:**")
            st.write(answer)
            if out.get("source_documents"):
                st.markdown("**Documentos fuente (IDs):**")
                ids = [d.metadata.get("source_id") for d in out["source_documents"]]
                st.write(ids)
with col2:
    st.markdown("**Sugerencias de ejemplo**")
    st.write("- ¿Qué diferencia hay entre el modelo A y el modelo B?")
    st.write("- ¿Qué productos tienen envío gratis?")
    st.write("- ¿Puedo cambiar el color después de comprar?")

st.markdown("---")
st.info("Para regenerar la base de conocimiento, borra la carpeta 'chroma_db' y vuelve a cargar la app.")
