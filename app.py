import streamlit as st
import json
from datetime import datetime
from typing import List, Dict, Any
import logging

# Import our custom modules
from config import *
from services.generate_response import GenerateResponseService
import config
import os

# Configure logging
logging.basicConfig(level=logging.INFO)
# logger = logging.get# logger(__name__)
os.environ["GEMINI_API_KEY"] = config.GEMINI_API_KEY

class ChatbotApp:
    def __init__(self):
        self.generate_response_service = GenerateResponseService()
        
    def initialize_session_state(self):
        """Initialize session state variables"""
        if "messages" not in st.session_state:
            st.session_state.messages = []
        if "conversation_history" not in st.session_state:
            st.session_state.conversation_history = []
            
    def setup_page_config(self):
        """Configure Streamlit page settings"""
        st.set_page_config(
            page_title="ShopEZ Customer Support",
            page_icon="🛒",
            layout="wide",
            initial_sidebar_state="expanded"
        )
        
    def render_sidebar(self):
        """Render the sidebar with app information"""
        with st.sidebar:
            st.title("🛒 ShopEZ Support")
            st.markdown("### How can I help you today?")
            
            st.markdown("""
            **I can assist you with:**
            - 📦 Order status and tracking
            - 🔄 Returns and exchanges
            - 💳 Payment and billing
            - 🚚 Shipping information
            - 📋 General policies
            - 💬 General questions
            """)
            
            st.markdown("---")
            
            if st.button("🗑️ Clear Chat History", type="secondary"):
                st.session_state.messages = []
                st.session_state.conversation_history = []
                st.rerun()
                
            # st.markdown("---")
            # st.markdown("**Sample Order IDs:**")
            # st.code("ABC-123, XYZ-456, DEF-789")
                        
    def render_chat_interface(self):
        """Render the main chat interface"""
        st.title("🛒 ShopEZ Customer Support")
        st.markdown("Welcome! I'm here to help you with orders, returns, policies, and general questions.")
        
        # Chat messages container
        chat_container = st.container()
        
        # with chat_container:
            # Display chat messages
        for message in st.session_state.messages:
            # with st.chat_message(message["role"]):
            if message["role"] == "assistant":
                # st.markdown(message["content"])
                with chat_container:
                    st.markdown(f"""
                    <div style="background-color:#000000; padding: 1rem; border-radius: 10px; color: white; margin-bottom: 0.5rem;">
                        <strong>assistant:</strong><br>{message["content"]}
                    </div>
                    """, unsafe_allow_html=True)
                # st.caption(f"⏰ {message['timestamp']}")
            else:
                # st.markdown(message["content"])
                with chat_container:
                    st.markdown(f"""
                    <div style="background-color:#000000; padding: 1rem; border-radius: 10px; color: white; margin-bottom: 0.5rem;">
                        <strong>User:</strong><br>{message["content"]}
                    </div>
                    """, unsafe_allow_html=True)
        
        # Chat input
        if prompt := st.chat_input("Type your message here..."):
            # Add user message
            print(f"messages: {prompt}")
            st.session_state.messages.append({
                "role": "user", 
                "content": prompt
            })
            
            # Display user message immediately
            # with st.chat_message("user"):
            #     st.markdown(prompt)
            with chat_container:
                st.markdown(f"""
                <div style="background-color:#000000; padding: 1rem; border-radius: 10px; color: white; margin-bottom: 0.5rem;">
                    <strong>User:</strong><br>{prompt}
                </div>
                """, unsafe_allow_html=True)
                        
            # Process and display assistant response
            # with st.chat_message("assistant"):
            with chat_container:
                with st.spinner("Thinking..."):
                    response = self.generate_response_service.generate_response(prompt, st.session_state.messages)
                
                st.markdown(f"""
                <div style="background-color:#333333; padding: 1rem; border-radius: 10px; color: white; margin-bottom: 0.5rem;">
                    <strong>Assistant:</strong><br>{response}
                </div>
                """, unsafe_allow_html=True)
                
                # Add assistant message with timestamp
                current_time = datetime.now().strftime("%H:%M")
                st.session_state.messages.append({
                    "role": "assistant", 
                    "content": response,
                    "timestamp": current_time
                })
                
                st.caption(f"⏰ {current_time}")
    
    def run(self):
        """Main application entry point"""
        self.setup_page_config()
        self.initialize_session_state()
        
        # Custom CSS for better styling
        st.markdown("""
        <style>
        .main {
            padding-top: 2rem;
        }
        .stChatMessage {
            background-color: #f8f9fa;
            border-radius: 10px;
            padding: 1rem;
            margin: 0.5rem 0;
        }
        .stChatMessage[data-testid="user"] {
            background-color: #000000;
        }
        .stChatMessage[data-testid="assistant"] {
            background-color: #000000;
        }
        .status-indicator {
            padding: 0.5rem;
            border-radius: 5px;
            margin: 0.2rem;
        }
        </style>
        """, unsafe_allow_html=True)
        
        # Render components
        self.render_sidebar()
        
        # Main content area
        main_col, status_col = st.columns([4, 1])
        
        with main_col:
            self.render_chat_interface()
            

if __name__ == "__main__":
    try:
        app = ChatbotApp()
        app.run()
    except Exception as e:
        st.error(f"Failed to initialize application: {e}")
        # logger.error(f"Application initialization error: {e}")