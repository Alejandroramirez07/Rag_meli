# rag_pipeline.py
import os
import json
from typing import List, Dict
from langchain.document_loaders import TextLoader
from langchain.schema import Document

# LangChain imports
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import Chroma
from langchain.chat_models import ChatOpenAI
from langchain.chains import RetrievalQA

JSONL_PATH = "/mnt/data/product_documents.jsonl"
CHROMA_PERSIST_DIR = "chroma_db"

def load_documents_from_jsonl(path: str) -> List[Document]:
    docs = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            item = json.loads(line)
            # item expected: {"id": <int>, "text": "<joined text>"}
            text = item.get("text", "")
            metadata = {"source_id": item.get("id")}
            docs.append(Document(page_content=text, metadata=metadata))
    return docs

def create_or_load_vectorstore(recreate: bool=False):
    embeddings = OpenAIEmbeddings()  # requires OPENAI_API_KEY in env
    if recreate:
        if os.path.exists(CHROMA_PERSIST_DIR):
            # remove or recreate manually
            pass
    # load documents and create vectorstore if needed
    vectordb = None
    try:
        vectordb = Chroma(persist_directory=CHROMA_PERSIST_DIR, embedding_function=embeddings)
        # quick sanity: if empty, rebuild
        if vectordb._collection.count() == 0:
            raise Exception("Empty collection; rebuilding.")
    except Exception:
        docs = load_documents_from_jsonl(JSONL_PATH)
        vectordb = Chroma.from_documents(docs, embedding=embeddings, persist_directory=CHROMA_PERSIST_DIR)
        vectordb.persist()
    return vectordb

def create_qa_chain(vectordb):
    retriever = vectordb.as_retriever(search_kwargs={"k": 3})
    llm = ChatOpenAI(temperature=0)  # customize model and temperature
    qa = RetrievalQA.from_chain_type(llm=llm, chain_type="stuff", retriever=retriever, return_source_documents=True)
    return qa

if __name__ == "__main__":
    v = create_or_load_vectorstore(recreate=False)
    qa = create_qa_chain(v)
    # quick test
    q = "¿Qué productos tienen envío gratis?"
    res = qa({"query": q})
    print(res["result"])
