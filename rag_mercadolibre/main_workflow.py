import os
import streamlit as st
from dotenv import load_dotenv
import requests
import re
import hashlib
import hmac
import time
from embedding_utils import get_embedding

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
    # Check authentication
    if not check_authentication():
        login_form()
    else:
        main_app()

if __name__ == "__main__":
    main()