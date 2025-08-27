import os
import logging
from dotenv import load_dotenv

# Load environment variables once when module is imported
load_dotenv()
# API Configuration
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Database Configuration
SQLITE_DB_PATH = "data/orders.db"

# Vector Database Configuration
COLLECTION_NAME = "e-commerce-compliance"
QDRANT_HOST = "localhost"
QDRANT_PORT = 6333

# Text Processing Configuration
CHUNK_SIZE = 500
CHUNK_OVERLAP = 50

# LLM Configuration
LLM_MODEL = "gemini-2.0-flash"
LLM_TEMPERATURE = 0.3

# Embedding Configuration
EMBEDDING_MODEL = "sentence-transformers/bert-base-nli-mean-tokens"

# Application Configuration
MAX_CONVERSATION_HISTORY = 10
MAX_RETRIEVAL_DOCS = 5

# Logging Configuration
LOG_LEVEL = logging.INFO
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'

# File Paths
ARTIFACTS_FOLDER = "artefacts"
DATA_FOLDER = "data"

# Ensure required directories exist
os.makedirs(DATA_FOLDER, exist_ok=True)
os.makedirs(ARTIFACTS_FOLDER, exist_ok=True)

# SSL Configuration (from your original code)
os.environ['CURL_CA_BUNDLE'] = ''
os.environ['REQUESTS_CA_BUNDLE'] = ''
os.environ['HF_HUB_DISABLE_SSL_VERIFY'] = '1'