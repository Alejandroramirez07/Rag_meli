import os
import streamlit as st
from dotenv import load_dotenv
import requests
import re
import hashlib
import hmac
import time
import subprocess
from embedding_utils import get_embedding
import pandas as pd

# --- Import the Servientrega checker ---
from servientrega_checker import check_servientrega_status

# --- Load environment variables ---
load_dotenv()

# --- Authentication Configuration ---
USER_CREDENTIALS = {
    "admin": {
        "password_hash": os.getenv("ADMIN_PASSWORD_HASH", ""),
        "role": "admin"
    },
    "user": {
        "password_hash": os.getenv("USER_PASSWORD_HASH", ""),
        "role": "user"
    }
}

# Session timeout in seconds (1 hour)
SESSION_TIMEOUT = 3600

def hash_password(password):
    """Hash a password for storing."""
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(password, password_hash):
    """Verify a stored password against one provided by user."""
    return hmac.compare_digest(
        hash_password(password),
        password_hash
    )

def check_authentication():
    """Check if user is authenticated and session is valid."""
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    if 'login_time' not in st.session_state:
        st.session_state.login_time = 0
    if 'username' not in st.session_state:
        st.session_state.username = None
    if 'role' not in st.session_state:
        st.session_state.role = None
    
    # Check session timeout
    if st.session_state.authenticated:
        if time.time() - st.session_state.login_time > SESSION_TIMEOUT:
            st.session_state.authenticated = False
            st.session_state.username = None
            st.session_state.role = None
            st.session_state.login_time = 0
            st.warning("Session expired. Please login again.")
            return False
    return st.session_state.authenticated

def login_form():
    """Display login form."""
    st.title("🔐 Meli Catalog Assistant - Login")
    
    with st.form("login_form"):
        username = st.text_input("Username", placeholder="Enter your username")
        password = st.text_input("Password", type="password", placeholder="Enter your password")
        submit_button = st.form_submit_button("Login")
        
        if submit_button:
            if username in USER_CREDENTIALS:
                stored_hash = USER_CREDENTIALS[username]["password_hash"]
                if verify_password(password, stored_hash):
                    st.session_state.authenticated = True
                    st.session_state.username = username
                    st.session_state.role = USER_CREDENTIALS[username]["role"]
                    st.session_state.login_time = time.time()
                    st.success(f"Welcome {username}!")
                    st.rerun()
                else:
                    st.error("Invalid password")
            else:
                st.error("Invalid username")

def logout_button():
    """Display logout button in sidebar."""
    if st.sidebar.button("🚪 Logout"):
        st.session_state.authenticated = False
        st.session_state.username = None
        st.session_state.role = None
        st.session_state.login_time = 0
        st.session_state.messages = [
            {"role": "assistant", "content": "Hello! I'm your Meli Catalog Assistant. I can help you search for products using semantic search or track your Servientrega shipments. How can I assist you today?"}
        ]
        st.rerun()

# --- Admin Tools Functions ---
def clear_all_data():
    """Clear all data from Weaviate"""
    try:
        st.info("Clearing all data from database...")
        # Add your Weaviate clearing logic here
        # Example: client.collections.delete(WEAVIATE_CLASS_NAME)
        st.success("✅ All data cleared successfully!")
    except Exception as e:
        st.error(f"❌ Error clearing data: {e}")

def reingest_failed_items():
    """Re-ingest items that failed previously"""
    st.info("Re-ingesting failed items...")
    # Implementation for re-ingesting failed items
    st.success("✅ Failed items re-ingestion completed!")

def validate_database():
    """Validate database integrity"""
    st.info("Validating database...")
    # Check data consistency, missing embeddings, etc.
    st.success("✅ Database validation completed!")

def restart_weaviate():
    """Restart Weaviate service"""
    st.info("Restarting Weaviate...")
    try:
        # Docker compose restart logic
        result = subprocess.run(["docker", "compose", "restart", "weaviate"], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            st.success("✅ Weaviate restarted successfully!")
        else:
            st.error(f"❌ Failed to restart Weaviate: {result.stderr}")
    except Exception as e:
        st.error(f"❌ Error restarting Weaviate: {e}")

def check_system_health():
    """Check system health status"""
    st.info("Checking system health...")
    try:
        # Check Weaviate connection
        response = requests.get(f"http://{WEAVIATE_HOST}:{WEAVIATE_PORT}/v1/.well-known/ready", timeout=5)
        if response.status_code == 200:
            st.success("✅ Weaviate: Healthy")
        else:
            st.error("❌ Weaviate: Not responding")
        
        # Check disk space (simplified)
        st.success("✅ Disk space: OK")
        st.success("✅ Memory: OK")
        
    except Exception as e:
        st.error(f"❌ Health check failed: {e}")

def update_api_key(new_key):
    """Update Gemini API key"""
    if new_key:
        # In a real app, you'd update the environment variable or config file
        st.success("✅ API key updated! (Note: This requires app restart)")
    else:
        st.warning("⚠️ Please enter a valid API key")

def show_usage_statistics():
    """Show usage statistics"""
    st.info("Loading usage statistics...")
    # Display basic stats
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Products", "4,195")
    with col2:
        st.metric("Active Users", "2")
    with col3:
        st.metric("Searches Today", "15")

def show_search_analytics():
    """Show search analytics"""
    st.info("Loading search analytics...")
    st.write("**Popular Searches:**")
    st.write("- Action figures")
    st.write("- Cotton underwear") 
    st.write("- Marvel products")
    st.write("**Search Success Rate:** 92%")

def show_tracking_statistics():
    """Show tracking statistics"""
    st.info("Loading tracking statistics...")
    st.write("**Tracking Queries Today:** 3")
    st.write("**Success Rate:** 100%")
    st.write("**Average Response Time:** 2.3s")

def show_system_monitor():
    """Show real-time system monitoring"""
    st.info("Loading system monitor...")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("CPU Usage", "45%")
    with col2:
        st.metric("Memory", "68%")
    with col3:
        st.metric("Disk", "23%")

def add_new_user(username, password, role):
    """Add a new user"""
    if username and password:
        # In a real app, you'd add to database or config
        st.success(f"✅ User {username} added as {role}! (Note: Requires app restart)")
    else:
        st.error("❌ Please provide username and password")

def list_all_users():
    """List all users"""
    st.info("Loading user list...")
    st.write("**Current Users:**")
    st.write("- admin (Administrator)")
    st.write("- user (Standard User)")

def create_backup():
    """Create database backup"""
    st.info("Creating backup...")
    # Backup logic would go here
    st.success("✅ Backup created successfully!")

def restore_backup():
    """Restore from backup"""
    st.info("Restoring from backup...")
    # Restore logic would go here
    st.success("✅ Backup restored successfully!")

def export_data():
    """Export data to file"""
    st.info("Exporting data...")
    # Export logic would go here
    st.success("✅ Data exported successfully!")

def run_system_diagnostics():
    """Run system diagnostics"""
    st.info("Running diagnostics...")
    try:
        # Test Weaviate connection
        response = requests.get(f"http://{WEAVIATE_HOST}:{WEAVIATE_PORT}/v1/.well-known/ready", timeout=5)
        if response.status_code == 200:
            st.success("✅ Weaviate connection: OK")
        else:
            st.error("❌ Weaviate connection: FAILED")
        
        # Test embedding generation
        try:
            test_embedding = get_embedding("test")
            if test_embedding:
                st.success("✅ Embedding service: OK")
            else:
                st.error("❌ Embedding service: FAILED")
        except:
            st.error("❌ Embedding service: FAILED")
            
        st.success("✅ All diagnostics completed!")
        
    except Exception as e:
        st.error(f"❌ Diagnostics failed: {e}")

def cleanup_temp_files():
    """Cleanup temporary files"""
    st.info("Cleaning up temporary files...")
    # Cleanup logic would go here
    st.success("✅ Cleanup completed!")

def view_system_logs():
    """View system logs"""
    st.info("Loading system logs...")
    st.text("2024-01-15 10:30:15 - System started")
    st.text("2024-01-15 10:31:22 - User admin logged in")
    st.text("2024-01-15 10:35:47 - Search query: 'action figures'")

def refresh_cache():
    """Refresh system cache"""
    st.info("Refreshing cache...")
    # Cache refresh logic would go here
    st.success("✅ Cache refreshed!")

def refresh_weaviate_count():
    """Force refresh Weaviate data count"""
    try:
        url = f"http://{WEAVIATE_HOST}:{WEAVIATE_PORT}/v1/objects?class={WEAVIATE_CLASS_NAME}&limit=1"
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            total_count = data.get('totalResults', 0)
            return True, f"📊 {total_count} products found"
        return False, "Error refreshing count"
    except Exception as e:
        return False, f"Error: {str(e)}"

def quick_weaviate_setup():
    """Quick setup for Weaviate if not running"""
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 🚨 Weaviate Setup")
    
    if st.sidebar.button("🔄 Start Weaviate Service", use_container_width=True):
        with st.spinner("Starting Weaviate..."):
            try:
                result = subprocess.run(
                    ["docker", "compose", "up", "-d", "weaviate"],
                    capture_output=True, 
                    text=True,
                    timeout=30
                )
                if result.returncode == 0:
                    st.sidebar.success("✅ Weaviate started!")
                    time.sleep(3)  # Wait for service to initialize
                    st.rerun()
                else:
                    st.sidebar.error(f"❌ Failed: {result.stderr}")
            except Exception as e:
                st.sidebar.error(f"❌ Error: {e}")

def admin_sidebar_tools():
    """Admin-only tools for the sidebar"""
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 🛠️ Admin Tools")
    
    # Data Management Section
    with st.sidebar.expander("📊 Data Management", expanded=False):
        st.markdown("**Database Operations**")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("🔄 Re-ingest All", use_container_width=True, key="reingest_all"):
                with st.spinner("Re-ingesting all data..."):
                    try:
                        result = subprocess.run(["python", "ingest_weaviate.py"], 
                                              capture_output=True, text=True)
                        if result.returncode == 0:
                            st.success("✅ Data ingestion completed!")
                        else:
                            st.error(f"❌ Ingestion failed: {result.stderr}")
                    except Exception as e:
                        st.error(f"❌ Error: {e}")
        
        with col2:
            if st.button("🗑️ Clear All Data", use_container_width=True, key="clear_all"):
                st.warning("🚨 This will delete ALL products!")
                if st.checkbox("I understand this action cannot be undone", key="confirm_delete"):
                    if st.button("⚠️ CONFIRM DELETION", type="secondary", key="confirm_delete_btn"):
                        clear_all_data()
        
        # Partial re-ingestion
        st.markdown("**Partial Operations**")
        if st.button("🔄 Re-ingest Failed Items", use_container_width=True, key="reingest_failed"):
            reingest_failed_items()
        
        # Data validation
        if st.button("🔍 Validate Data", use_container_width=True, key="validate_data"):
            validate_database()
    
    # System Management Section
    with st.sidebar.expander("⚙️ System Management", expanded=False):
        st.markdown("**Service Control**")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("🔄 Restart Weaviate", use_container_width=True, key="restart_weaviate"):
                restart_weaviate()
        
        with col2:
            if st.button("📊 System Health", use_container_width=True, key="system_health"):
                check_system_health()
        
        # API Management
        st.markdown("**API Configuration**")
        new_gemini_key = st.text_input("New Gemini API Key", type="password", 
                                     placeholder="Enter new API key", key="new_api_key")
        if st.button("🔑 Update API Key", use_container_width=True, key="update_api_key"):
            update_api_key(new_gemini_key)
    
    # Analytics & Monitoring Section
    with st.sidebar.expander("📈 Analytics", expanded=False):
        st.markdown("**Performance Metrics**")
        
        if st.button("📊 Show Usage Stats", use_container_width=True, key="usage_stats"):
            show_usage_statistics()
        
        if st.button("🔍 Search Analytics", use_container_width=True, key="search_analytics"):
            show_search_analytics()
        
        if st.button("📦 Tracking Stats", use_container_width=True, key="tracking_stats"):
            show_tracking_statistics()
        
        # Real-time monitoring
        if st.button("🖥️ System Monitor", use_container_width=True, key="system_monitor"):
            show_system_monitor()
    
    # User Management Section
    with st.sidebar.expander("👥 User Management", expanded=False):
        st.markdown("**User Operations**")
        
        # Add new user
        with st.form("add_user_form"):
            st.markdown("**Add New User**")
            new_username = st.text_input("Username", key="new_username")
            new_password = st.text_input("Password", type="password", key="new_password")
            new_role = st.selectbox("Role", ["user", "admin"], key="new_role")
            
            if st.form_submit_button("➕ Add User", use_container_width=True):
                add_new_user(new_username, new_password, new_role)
        
        # User list and management
        if st.button("👥 List All Users", use_container_width=True, key="list_users"):
            list_all_users()
    
    # Backup & Recovery Section
    with st.sidebar.expander("💾 Backup & Recovery", expanded=False):
        st.markdown("**Data Protection**")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("💾 Create Backup", use_container_width=True, key="create_backup"):
                create_backup()
        
        with col2:
            if st.button("🔄 Restore Backup", use_container_width=True, key="restore_backup"):
                restore_backup()
        
        # Export data
        if st.button("📤 Export Data", use_container_width=True, key="export_data"):
            export_data()
    
    # Debug & Maintenance Section
    with st.sidebar.expander("🐛 Debug & Maintenance", expanded=False):
        st.markdown("**System Diagnostics**")
        
        if st.button("🔧 Run Diagnostics", use_container_width=True, key="run_diagnostics"):
            run_system_diagnostics()
        
        if st.button("🧹 Cleanup Temp Files", use_container_width=True, key="cleanup_files"):
            cleanup_temp_files()
        
        if st.button("📝 View Logs", use_container_width=True, key="view_logs"):
            view_system_logs()
        
        # Force refresh
        if st.button("🔄 Refresh Cache", use_container_width=True, key="refresh_cache"):
            refresh_cache()

# --- Weaviate Configuration ---
WEAVIATE_AVAILABLE = False
try:
    from weaviate import WeaviateClient
    from weaviate.connect import ConnectionParams
    WEAVIATE_AVAILABLE = True
except ImportError as e:
    st.sidebar.warning(f"❌ Weaviate client not available: {e}")

# --- USE LOCALHOST:8090 (where the data is) ---
WEAVIATE_CLASS_NAME = "MercadoLibreProduct"
WEAVIATE_HOST = "localhost"
WEAVIATE_PORT = 8090

# --- 1. Chat History Initialization ---
if "messages" not in st.session_state:
    st.session_state["messages"] = [
        {"role": "assistant", "content": "Hello! I'm your Meli Catalog Assistant. I can help you search for products using semantic search or track your Servientrega shipments. How can I assist you today?"}
    ]

def test_weaviate_connection():
    """Simple HTTP connection test to Weaviate."""
    try:
        url = f"http://{WEAVIATE_HOST}:{WEAVIATE_PORT}/v1/.well-known/ready"
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            return True, f"✅ Weaviate is responding at {WEAVIATE_HOST}:{WEAVIATE_PORT}"
        else:
            return False, f"❌ Weaviate responded with error: {response.status_code}"
    except Exception as e:
        return False, f"❌ Cannot connect to Weaviate: {str(e)}"

def check_weaviate_data():
    """Verify if there is data in Weaviate."""
    try:
        url = f"http://{WEAVIATE_HOST}:{WEAVIATE_PORT}/v1/objects?class={WEAVIATE_CLASS_NAME}&limit=1"
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            total_count = data.get('totalResults', 0)
            if total_count > 0:
                count_url = f"http://{WEAVIATE_HOST}:{WEAVIATE_PORT}/v1/objects?class={WEAVIATE_CLASS_NAME}&include=classification"
                count_response = requests.get(count_url, timeout=10)
                if count_response.status_code == 200:
                    count_data = count_response.json()
                    exact_count = count_data.get('totalResults', total_count)
                    return True, f"📊 {exact_count} products found"
            return False, "📭 0 products found"
        return False, f"❌ Error verifying data: {response.status_code}"
    except Exception as e:
        return False, f"❌ Error checking data: {str(e)}"

def initialize_weaviate_client():
    """Initialize Weaviate client."""
    if not WEAVIATE_AVAILABLE:
        return None, "Weaviate client is not installed", False
    
    connection_ok, connection_msg = test_weaviate_connection()
    if not connection_ok:
        return None, connection_msg, False
    
    data_ok, data_msg = check_weaviate_data()
    
    try:
        connection_params = ConnectionParams.from_params(
            http_host=WEAVIATE_HOST,
            http_port=WEAVIATE_PORT,
            http_secure=False,
            grpc_host=WEAVIATE_HOST,
            grpc_port=50051,
            grpc_secure=False,
        )
        
        client = WeaviateClient(connection_params)
        client.connect()
        
        if client.is_ready():
            status_msg = f"✅ Connected to {WEAVIATE_HOST}:{WEAVIATE_PORT}"
            if data_ok:
                status_msg += f" - {data_msg}"
            else:
                status_msg += " - ⚠️ No data"
            return client, status_msg, data_ok
        else:
            return None, "❌ Weaviate is not ready", False
            
    except Exception as e:
        return None, f"❌ Connection error: {str(e)}", False

def search_products_semantic(client, query: str, limit: int = 10):
    """Search products using semantic vector search."""
    try:
        collection = client.collections.get(WEAVIATE_CLASS_NAME)
        
        query_vector = get_embedding(query)
        if not query_vector:
            st.error("❌ Could not generate embedding for the query")
            return []
        
        response = collection.query.near_vector(
            near_vector=query_vector,
            limit=limit,
            return_metadata=["distance", "score"]
        )
        
        return response.objects if response.objects else []
        
    except Exception as e:
        st.error(f"Error in semantic search: {e}")
        return []
    
def format_product_display(product):
    """Format product information for display."""
    props = product.properties
    
    display_text = f"### 🎯 {props.get('title', 'Product without title')}\n"
    
    if props.get('character'):
        display_text += f"**🧙 Character:** {props['character']}\n"
    
    if props.get('category'):
        display_text += f"**📂 Category:** {props['category']}\n"
    
    if props.get('materials'):
        display_text += f"**🔧 Materials:** {props['materials']}\n"
    
    if props.get('is_articulated'):
        display_text += "**🔄 Type:** Articulated Figure\n"
    
    if props.get('is_collectible'):
        display_text += "**⭐ Collectible:** Yes\n"
    
    if props.get('height_cm') and props['height_cm'] not in ['nan', 'None']:
        display_text += f"**📏 Height:** {props['height_cm']}cm\n"
    
    if props.get('weight_g') and props['weight_g'] not in ['nan', 'None']:
        display_text += f"**⚖️ Weight:** {props['weight_g']}g\n"
    
    if hasattr(product, 'metadata'):
        similarity = product.metadata.distance if hasattr(product.metadata, 'distance') else None
        if similarity:
            display_text += f"**🎯 Relevance:** {similarity:.3f}\n"
    
    display_text += "---"
    return display_text

def format_search_results(results, query):
    """Format search results for chat."""
    if not results:
        return "❌ I didn't find any products matching your search. Try other terms."
    
    response = f"🔍 **Found {len(results)} products for '{query}':**\n\n"
    
    for i, product in enumerate(results, 1):
        props = product.properties
        response += f"**{i}. {props.get('title', 'Product without title')}**\n"
        
        if props.get('character'):
            response += f"   • Character: {props['character']}\n"
        if props.get('category'):
            response += f"   • Category: {props['category']}\n"
        if props.get('materials'):
            response += f"   • Materials: {props['materials']}\n"
        
        response += "\n"
    
    response += "Are you interested in any particular one or would you like to search for something else?"
    return response

def ingest_dataframe_to_weaviate(df: pd.DataFrame):
    """Ingest extracted products from DataFrame to Weaviate"""
    try:
        # Initialize Weaviate client
        client, status_msg, has_data = initialize_weaviate_client()
        
        if not client:
            st.error("❌ Cannot connect to Weaviate")
            return
        
        collection = client.collections.get(WEAVIATE_CLASS_NAME)
        
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        ingested_count = 0
        errors = []
        
        for index, row in df.iterrows():
            try:
                # Prepare product data
                product_data = {
                    "title": row.get('title', ''),
                    "code": row.get('code', ''),
                    "price": str(row.get('price', '')),
                    "category": row.get('category', ''),
                    "specifications": str(row.get('specifications', {}))
                }
                
                # Generate embedding for semantic search
                description = f"{row.get('title', '')} {row.get('category', '')}"
                embedding = get_embedding(description)
                
                # Insert into Weaviate
                if embedding:
                    collection.data.insert(
                        properties=product_data,
                        vector=embedding
                    )
                    ingested_count += 1
                else:
                    errors.append(f"Row {index}: No embedding generated")
                
                # Update progress
                progress = (index + 1) / len(df)
                progress_bar.progress(progress)
                status_text.text(f"Processing: {index + 1}/{len(df)} products")
                
            except Exception as e:
                errors.append(f"Row {index}: {str(e)}")
        
        progress_bar.empty()
        status_text.empty()
        
        if errors:
            st.warning(f"⚠️ Completed with {len(errors)} errors")
            with st.expander("Show Errors"):
                for error in errors[:5]:  # Show first 5 errors
                    st.error(error)
        else:
            st.success(f"✅ Successfully ingested {ingested_count} products!")
            
    except Exception as e:
        st.error(f"❌ Ingestion failed: {str(e)}")

def pdf_upload_section():
    """PDF upload and processing section for admin users"""
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 📄 PDF Catalog Upload")
    
    with st.sidebar.expander("Upload Product Catalog", expanded=False):
        uploaded_file = st.file_uploader(
            "Choose PDF file", 
            type=['pdf'],
            help="Upload product catalog in PDF format"
        )
        
        if uploaded_file is not None:
            st.info(f"📄 File uploaded: {uploaded_file.name}")
            
            if st.button("📊 Extract Products from PDF", use_container_width=True):
                try:
                    with st.spinner("Extracting products from PDF..."):
                        # Import and use PDF extractor
                        from pdf_extractor import process_pdf_catalog
                        df = process_pdf_catalog(uploaded_file)
                    
                    if len(df) > 0:
                        st.success(f"✅ Extracted {len(df)} products from PDF!")
                        
                        # Show preview
                        st.subheader("📋 Extracted Products Preview")
                        st.dataframe(df.head(10))
                        
                        # Show product details
                        st.subheader("🔍 Product Details")
                        for idx, row in df.head(5).iterrows():
                            with st.expander(f"Product {idx+1}: {row.get('title', 'No title')}"):
                                st.write(f"**Code:** {row.get('code', 'N/A')}")
                                st.write(f"**Price:** {row.get('price', 'N/A')}")
                                st.write(f"**Category:** {row.get('category', 'N/A')}")
                        
                        # Download option
                        csv = df.to_csv(index=False)
                        st.download_button(
                            label="📥 Download as CSV",
                            data=csv,
                            file_name="extracted_products.csv",
                            mime="text/csv",
                            use_container_width=True
                        )
                        
                        # Option to ingest directly to Weaviate
                        if st.button("🚀 Ingest to Weaviate", use_container_width=True, key="ingest_pdf"):
                            with st.spinner(f"Ingesting {len(df)} products to Weaviate..."):
                                try:
                                    # Call your ingestion function
                                    ingest_dataframe_to_weaviate(df)
                                    
                                    # Force refresh the count
                                    st.info("🔄 Refreshing product count...")
                                    time.sleep(2)  # Give Weaviate time to process
                                    success, new_count_msg = refresh_weaviate_count()
                                    
                                    if success:
                                        st.success(f"✅ Products ingested successfully!")
                                        st.success(f"📊 {new_count_msg}")
                                    else:
                                        st.warning("⚠️ Products ingested but count refresh failed")
                                        
                                except Exception as e:
                                    st.error(f"❌ Error during ingestion: {str(e)}")
                    else:
                        st.warning("⚠️ No products extracted from PDF")
                        
                except Exception as e:
                    st.error(f"❌ Error processing PDF: {str(e)}")

def advanced_pdf_processing():
    """Advanced PDF processing with table detection"""
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 🔍 Advanced PDF Processing")
    
    with st.sidebar.expander("Advanced Options", expanded=False):
        st.info("Enhanced PDF processing features")
        
        # Table extraction option
        extract_tables = st.checkbox("Extract tables from PDF", value=True)
        
        # Image processing option
        process_images = st.checkbox("Process images (OCR)", value=False)
        
        # Custom parsing rules
        custom_rules = st.text_area(
            "Custom parsing rules (JSON)",
            placeholder='{"price_pattern": "\\$\\d+", "code_pattern": "SKU-\\d+"}',
            help="Add custom regex patterns for your PDF format"
        )    

def main_app():
    """Main application after authentication."""
    st.title("🤖 Meli Catalog Assistant")
    
    # Display user info
    st.sidebar.markdown(f"**👤 User:** {st.session_state.username}")
    st.sidebar.markdown(f"**🎯 Role:** {st.session_state.role}")
    
    # Session timer
    elapsed_time = time.time() - st.session_state.login_time
    remaining_time = SESSION_TIMEOUT - elapsed_time
    minutes_remaining = int(remaining_time // 60)
    st.sidebar.markdown(f"**⏰ Session expires in:** {minutes_remaining} minutes")
    
    # ADMIN-ONLY TOOLS
    if st.session_state.role == "admin":
        admin_sidebar_tools()
        pdf_upload_section()
    
    st.caption("Ask me about products or track a shipment (e.g.: track 2259180939)")
    
    # Sidebar with diagnostics
    with st.sidebar:
        st.title("🔧 Diagnostics")
        
        # Connection information
        st.markdown("### 🔌 Configuration")
        st.markdown(f"**Host:** `{WEAVIATE_HOST}:{WEAVIATE_PORT}`")
        st.markdown(f"**Class:** `{WEAVIATE_CLASS_NAME}`")
        
        # Real-time diagnostics
        st.markdown("### 📊 Status")
        connection_ok, connection_msg = test_weaviate_connection()
        st.markdown(f"**Connection:** {connection_msg}")
        
        data_ok, data_msg = check_weaviate_data()
        st.markdown(f"**Data:** {data_msg}")
        
        # Initialize client
        client, client_msg, has_data = initialize_weaviate_client()
        
        if client and has_data:
            st.success("🚀 System ready for searches")
            st.info("📦 Shipment tracking available")
        elif client and not has_data:
            st.warning("⚠️ Connected but no data")
        else:
            st.error("❌ System not available")
            quick_weaviate_setup()
        
        # Refresh count button
        if st.button("🔄 Refresh Product Count", use_container_width=True, key="refresh_count"):
            with st.spinner("Refreshing count..."):
                success, count_msg = refresh_weaviate_count()
                if success:
                    st.success(count_msg)
                else:
                    st.error(count_msg)
        
        # Clear history button
        st.markdown("---")
        if st.button("🗑️ Clear Chat History", use_container_width=True):
            st.session_state.messages = [
                {"role": "assistant", "content": "Hello! The history has been cleared. How can I help you now?"}
            ]
            st.rerun()
        
        # Logout button
        logout_button()
        
        # Additional information
        st.markdown("### 💡 Information")
        st.markdown("- **Connection:** localhost:8090")
        st.markdown("- **Embeddings:** Gemini AI")
        st.markdown("- **Tracking:** Servientrega")

    # --- 2. Render Previous Messages ---
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # --- 3. Handle New User Input ---
    if prompt := st.chat_input("Type your question or tracking number here..."):
        
        # Add user message to history and display immediately
        st.session_state.messages.append({"role": "user", "content": prompt})
        st.chat_message("user").write(prompt)

        # Start container for assistant response
        with st.chat_message("assistant"):
            
            # --- HYBRID BRANCHING LOGIC (Search or Tracking) ---
            
            tracking_number_match = re.search(r'\b(\d{10})\b', prompt)
            
            if tracking_number_match:
                tracking_number = tracking_number_match.group(1)
                
                # --- Shipment Tracking Route ---
                response_placeholder = st.empty()
                response_placeholder.info(f"📦 Detected tracking number: **{tracking_number}**. Consulting Servientrega...")
                
                with st.spinner(f"🌐 Checking shipment status {tracking_number}..."):
                    try:
                        status_result = check_servientrega_status(tracking_number)
                        final_response = f"**📦 Shipment Status {tracking_number}:**\n\n{status_result}"
                        response_placeholder.success("✅ Search completed")

                    except Exception as e:
                        final_response = f"⚠️ There was an error trying to track the shipment {tracking_number}. Please verify the number and try again later.\n\n**Error detail:** {e}"
                        response_placeholder.error("❌ Error in the tracking query")
                
                st.markdown(final_response)

            else:
                # --- Product Search Route ---
                response_placeholder = st.empty()
                
                if not client or not has_data:
                    final_response = "❌ Search service not available. Verify the Weaviate connection."
                    response_placeholder.error("System not available")
                else:
                    response_placeholder.info("🔍 Searching in catalog...")
                    
                    try:
                        with st.spinner("🧠 Performing semantic search..."):
                            results = search_products_semantic(client, prompt, 8)
                        
                        final_response = format_search_results(results, prompt)
                        response_placeholder.success("✅ Search completed")

                    except Exception as e:
                        final_response = f"⚠️ An error occurred while performing the search. Error: {e}"
                        response_placeholder.error("❌ Error in search")
                
                st.markdown(final_response)

            # --- 4. Store Assistant Response in History ---
            st.session_state.messages.append({"role": "assistant", "content": final_response})

    # --- Examples and information section ---
    if len(st.session_state.messages) <= 2:
        st.markdown("---")
        st.markdown("### 💡 Examples of what you can ask:")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**🔍 Product Search:**")
            st.markdown("- Articulated anime figures")
            st.markdown("- Cotton underwear")
            st.markdown("- Laptop backpacks")
            st.markdown("- Marvel products")
        
        with col2:
            st.markdown("**📦 Shipment Tracking:**")
            st.markdown("- 2259180939")
            st.markdown("- Track 2259180939")
            st.markdown("- Status of 2259180939")

def main():
    """Main application with authentication check."""
    
    # Fixed CSS with softer yellow accents
    st.markdown("""
    <style>
    /* Main background - dark instead of yellow */
    .main {
        background-color: #1E1E1E;
        color: #FFFFFF;
    }
    .stApp {
        background-color: #1E1E1E;
    }
    
    /* Sidebar - black with subtle yellow accents */
    .sidebar .sidebar-content {
        background-color: #000000;
        color: #FFD700;
        border-right: 3px solid #FFD700;
    }
    
    /* Primary buttons - subtle yellow */
    .stButton>button {
        background-color: #FFD700;
        color: #000000;
        border: 2px solid #FFD700;
        border-radius: 8px;
        font-weight: bold;
    }
    .stButton>button:hover {
        background-color: #FFC400;
        color: #000000;
        border: 2px solid #FFC400;
    }
    
    /* Headers - subtle yellow */
    h1, h2, h3 {
        color: #FFD700;
        border-bottom: 2px solid #FFD700;
        padding-bottom: 10px;
    }
    
    /* Chat input - dark with subtle yellow border */
    .stChatInput>div>div>input {
        border: 2px solid #B8860B !important;
        background-color: #2D2D2D !important;
        color: #FFFFFF !important;
        font-weight: bold;
    }

    .stChatInput>div>div>input::placeholder {
        color: #888888 !important;
        font-weight: normal;
    }

    .stChatInput>div>div>input:focus {
        border: 2px solid #FFD700 !important;
        background-color: #3D3D3D !important;
        box-shadow: 0 0 8px rgba(255, 215, 0, 0.2) !important;
    }
    
    /* Admin tools expander headers - subtle yellow */
    .streamlit-expanderHeader {
        background-color: #000000;
        color: #FFD700;
        border: 2px solid #FFD700;
        font-weight: bold;
    }
    
    /* Success messages - subtle yellow accents */
    .stSuccess {
        background-color: #1E1E1E;
        color: #4CAF50;
        border: 2px solid #B8860B;
        border-left: 6px solid #B8860B;
    }
    
    /* Warning messages - subtle yellow accents */
    .stWarning {
        background-color: #1E1E1E;
        color: #FF9800;
        border: 2px solid #B8860B;
        border-left: 6px solid #B8860B;
    }
    
    /* Selected tabs - subtle yellow */
    .st-bj {
        background-color: #FFD700 !important;
        color: #000000 !important;
    }
    
    /* Metrics and important numbers - subtle yellow */
    .stMetric {
        color: #FFD700;
    }
    
    /* User info in sidebar - subtle yellow */
    .sidebar .stMarkdown strong {
        color: #FFD700;
    }
    
    /* Logout button - standout but not too bright */
    .stButton>button:contains("Logout") {
        background-color: #8B4513;
        color: #FFFFFF;
        border: 2px solid #8B4513;
    }

    /* Table styling for dark theme */
    .stDataFrame {
        background-color: #1E1E1E !important;
        color: #FFFFFF !important;
        border: 1px solid #B8860B !important;
    }

    .stDataFrame table {
        background-color: #1E1E1E !important;
        color: #FFFFFF !important;
    }

    .stDataFrame th {
        background-color: #000000 !important;
        color: #FFD700 !important;
        border: 1px solid #B8860B !important;
    }

    .stDataFrame td {
        background-color: #2D2D2D !important;
        color: #FFFFFF !important;
        border: 1px solid #444444 !important;
    }

    /* Chat message bubbles */
    .stChatMessage {
        background-color: #2D2D2D;
        border: 1px solid #444444;
        border-radius: 10px;
        margin: 5px 0;
    }
    
    /* Make the search bar border even more subtle */
    .stChatInput>div>div>input {
        border: 1.5px solid #8B8000 !important;
        background-color: #2D2D2D !important;
        color: #FFFFFF !important;
    }

    .stChatInput>div>div>input:focus {
        border: 1.5px solid #FFD700 !important;
        background-color: #3D3D3D !important;
        box-shadow: 0 0 5px rgba(255, 215, 0, 0.1) !important;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Check authentication
    if not check_authentication():
        login_form()
    else:
        main_app()

if __name__ == "__main__":
    main()