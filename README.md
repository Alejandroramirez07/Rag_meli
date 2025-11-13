MercadoLibre Catalog Assistant - RAG System
Project Overview

A sophisticated Retrieval-Augmented Generation (RAG) system that provides intelligent product search and shipment tracking capabilities for MercadoLibre catalog data. The application combines semantic search using vector embeddings with a conversational AI interface and administrative controls.
Architecture
Core Components

    Frontend: Streamlit web application with authentication and real-time chat interface

    Vector Database: Weaviate for storing and retrieving product embeddings

    Embedding Service: Google Gemini AI for generating semantic embeddings

    External Integration: Servientrega shipment tracking via Selenium automation

    Authentication: Role-based access control (Admin/User)

Data Flow

    Product data ingestion and vectorization

    Semantic search using cosine similarity

    Hybrid query processing (product search vs shipment tracking)

    Real-time conversation history management

    Administrative system monitoring and control

Features
User Features

    Natural language product search using semantic similarity

    Real-time shipment tracking with Servientrega integration

    Conversational chat interface with persistent history

    Intelligent query routing and intent detection

Administrative Features

    Complete data management (ingestion, validation, cleanup)

    System health monitoring and service control

    User management and access control

    Analytics and usage statistics

    Backup and recovery operations

    API configuration management

Technical Specifications
Dependencies

Core Framework

    Streamlit 1.28+ - Web application framework

    Weaviate Client 4.x - Vector database operations

    Google Generative AI - Embedding generation

Data Processing

    Pandas - Data manipulation and analysis

    Requests - HTTP client for API calls

    Python-dotenv - Environment configuration

Authentication & Security

    HMAC - Secure password verification

    SHA-256 - Password hashing

    Session-based authentication with timeout

External Services

    Selenium - Web automation for shipment tracking

    Docker - Containerized Weaviate deployment

Configuration
Environment Variables
text

ADMIN_PASSWORD_HASH=sha256_hash_of_admin_password
USER_PASSWORD_HASH=sha256_hash_of_user_password
GEMINI_API_KEY=your_google_gemini_api_key

Weaviate Configuration

    Host: localhost:8090

    Class: MercadoLibreProduct

    Vectorizer: None (custom embeddings via Gemini)

    Distance Metric: Cosine similarity

Installation & Setup
Prerequisites

    Python 3.8+

    Docker and Docker Compose

    Google Gemini API key

Installation Steps

    Clone and Setup Environment
    bash

git clone <repository-url>
cd rag_mercadolibre
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

Configure Environment
bash

# Generate password hashes
python create_users.py

# Create .env file with generated hashes
echo "ADMIN_PASSWORD_HASH=generated_admin_hash" > .env
echo "USER_PASSWORD_HASH=generated_user_hash" >> .env
echo "GEMINI_API_KEY=your_gemini_api_key" >> .env

Start Weaviate Database
bash

docker compose up -d

Ingest Product Data
bash

python ingest_weaviate.py

Launch Application
bash

streamlit run main_workflow.py

Usage Guide
Authentication

    Access the application at http://localhost:8501

    Default credentials:

        Admin: username admin, password admin

        User: username user, password user

Product Search

    Use natural language queries to find products

    Example: "action figures", "cotton underwear", "laptop backpacks"

    Results are ranked by semantic similarity to query

Shipment Tracking

    Enter 10-digit tracking numbers directly

    Example: "2259180939" or "track 2259180939"

    Real-time status retrieval from Servientrega

Administrative Functions

Admin users have access to comprehensive system management tools:

Data Management

    Bulk re-ingestion of product data

    Database validation and cleanup

    Selective re-processing of failed items

System Monitoring

    Real-time health checks

    Performance analytics

    Usage statistics and search analytics

User Management

    Add new users with role assignments

    Access control configuration

Maintenance

    Backup and restore operations

    System diagnostics

    Log viewing and cache management

Data Schema
Product Object Structure
python

{
    "title": "Product title",
    "category": "Product category",
    "character": "Character/theme (for collectibles)",
    "materials": "Construction materials",
    "is_articulated": boolean,
    "is_collectible": boolean,
    "height_cm": "Height in centimeters",
    "weight_g": "Weight in grams",
    "vector": [768-dimensional embedding]
}

API Endpoints
Internal Weaviate API

    GET /v1/objects?class=MercadoLibreProduct - Retrieve products

    POST /v1/objects - Create product entries

    GET /v1/.well-known/ready - Health check

External Services

    Servientrega Tracking: Mobile API integration via Selenium

    Google Gemini: Embedding generation and AI services

Security Considerations

    Passwords are hashed using SHA-256 with HMAC verification

    Session-based authentication with configurable timeout

    Environment variable configuration for sensitive data

    Input validation and sanitization for all user queries

    Secure container deployment for database services

Performance Characteristics

    Vector search response time: < 2 seconds

    Embedding generation: ~1 second per query

    Shipment tracking: 5-10 seconds (external API dependency)

    Concurrent user support: Limited by Weaviate configuration

Troubleshooting
Common Issues

Weaviate Connection Failures

    Verify Docker containers are running: docker compose ps

    Check port availability: netstat -an | grep 8090

    Validate Weaviate logs: docker compose logs weaviate

Authentication Problems

    Confirm .env file exists in correct directory

    Verify password hashes match generated values

    Check for session timeout (default: 1 hour)

Search Performance

    Monitor embedding API rate limits

    Check Weaviate resource allocation

    Validate product data completeness

Logs and Monitoring

    Application logs available in Streamlit interface

    Weaviate logs accessible via Docker commands

    System metrics available in admin dashboard

Development
Extending Functionality

Adding New Product Categories

    Update data ingestion script with new schema

    Modify search functions to handle new fields

    Update chat response formatting

Integrating Additional Services

    Create new service module following existing patterns

    Add route detection logic in main application

    Implement error handling and user feedback

Testing

    Unit tests for embedding generation

    Integration tests for Weaviate operations

    End-to-end testing for user workflows

Deployment Considerations
Production Requirements

    Secure Weaviate deployment with authentication

    SSL/TLS termination for web interface

    Environment-specific configuration management

    Monitoring and alerting infrastructure

    Regular backup procedures

Scaling Strategies

    Weaviate cluster configuration for high availability

    Load balancing for multiple application instances

    Caching layer for frequent queries

    Database sharding for large product catalogs

License and Attribution

This project utilizes:

    Weaviate vector database (Apache 2.0)

    Google Gemini AI services

    Streamlit web framework (Apache 2.0)

    Servientrega public tracking services

Support and Maintenance

For technical support and maintenance considerations, refer to the individual component documentation and ensure compliance with respective service terms and API usage policies.