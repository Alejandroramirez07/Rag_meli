# Rag_meli
 Meli Hybrid Assistant: RAG and Tool-Use Chatbot

This project implements a sophisticated hybrid assistant built on Streamlit that combines two key functionalities:

Retrieval-Augmented Generation (RAG): Answers user questions based on an internal product catalog stored in a ChromaDB vector store.

Tool Use (Function Calling): Automatically detects tracking numbers and executes an external tool (Selenium) to fetch real-time shipment status from the Servientrega website.

The entire application is containerized using Docker Compose for easy deployment and manages a local LLM (Mistral) via Ollama.

 Features

Hybrid Intelligence: Seamlessly switches between RAG for catalog queries and a dedicated tool for real-time tracking.

Local LLM: Uses Mistral-7B served via Ollama for fast, private, and contextual responses.

Conversational Memory: Maintains full chat history, allowing users to ask follow-up questions.

Real-Time Tracking: Integration with servientrega_checker.py (using Selenium) for up-to-date shipment status retrieval (for 10-digit tracking numbers).

Containerized Deployment: Simple two-service deployment using Docker Compose (app and ollama).

🛠️ Architecture

The project is structured around three main components orchestrated by LangChain:

Component

Technology

Role

User Interface

Streamlit

Provides the web interface and manages session state (chat history).

Knowledge Base (RAG)

Ollama (Mistral) + ChromaDB + HuggingFace Embeddings

Stores the product catalog and retrieves contextually relevant information to augment the LLM's response.

Tool

Selenium / check_servientrega_status

Executes web scraping logic to find the status of a specific tracking number.

⚙️ Prerequisites

You must have the following installed on your system:

Docker: (Required for containerization).

Docker Compose: (Required for multi-service orchestration).

ChromaDB Initialized: You must run your data ingestion script (ingest.py or similar) to generate the ./chroma_db directory before building the Docker image. The Dockerfile copies this directory into the application container.

🚀 Setup and Run

Follow these steps to get the hybrid assistant running locally:

1. Build and Run Services

From the root directory of the project, use Docker Compose to build the application image and start both the app and ollama services:

docker compose up --build -d


(The --build flag forces a fresh build, ensuring the latest chroma_db is included.)

2. Verify Ollama Model

Wait about 30-60 seconds for the ollama service to start and download the mistral model (if it's not already cached).

3. Access the Application

The Streamlit application will be running on port 8501.

Open your browser and navigate to:

http://localhost:8501


 Usage

The assistant is designed to handle two types of queries:

A. Catalog Search (RAG)

Ask general questions about the products in the catalog. The system will use ChromaDB to find relevant text chunks and pass them to Mistral for a concise answer.

Examples:

¿Qué figuras hay de Naruto?

¿Hay figuras de Dragon Ball?

B. Shipment Tracking (Tool-Use)

The system automatically detects any 10-digit number and assumes it's a Servientrega guide to track.

Examples:

rastrea guía 1234567890

por favor, dime el estado del envío con código 9876543210

1112223334 (Just the number is enough)

🛑 Troubleshooting

Issue

Cause

Solution

Error: ''dict' object has no attribute 'replace''

LangChain serialization failure between RAG components and Ollama.

Ensure main_workflow.py is the latest version, which uses RunnableLambda to explicitly extract question and history strings.

Error al configurar la cadena RAG. ¿Está Ollama corriendo...?

The ollama service is not running or the mistral model is not downloaded.

Check docker logs ollama_server. Ensure the container is running and has completed the initial model download.

Tracking fails (ERROR al intentar rastrear...)

Selenium failed to connect or website structure changed.

Check the logs for the meli_asistente_rag container to see the detailed Selenium error.