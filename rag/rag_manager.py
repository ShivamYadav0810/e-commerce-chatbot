import logging
import warnings

import fitz  # PyMuPDF
import os
from typing import List
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores import Qdrant
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.docstore.document import Document
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams
from langchain.chains import RetrievalQA

from config import *

# Suppress warnings
warnings.filterwarnings("ignore")
logger = logging.getLogger(__name__)

class RAGManager:
    def __init__(self):
        self.embedding_model = None
        self.vectorstore = None
        self.qdrant_client = None
        self.initialize_rag()
    
    def initialize_rag(self):
        """Initialize RAG components"""
        try:
            # Initialize embedding model
            self.embedding_model = HuggingFaceEmbeddings(
                model_name=EMBEDDING_MODEL
            )
            
            # Initialize Qdrant client
            self.qdrant_client = QdrantClient(host=QDRANT_HOST, port=QDRANT_PORT)
            
            # Setup vector store
            self.setup_vectorstore()
            
            logger.info("RAG Manager initialized successfully")
            
        except Exception as e:
            logger.error(f"Error initializing RAG Manager: {e}")
            raise
    
    def read_pdf(self, file_path: str) -> str:
        """Read text from a PDF file"""
        try:
            pdf = fitz.open(file_path)
            text = ""
            
            for page_num in range(len(pdf)):
                page = pdf[page_num]
                text += f"\\n--- Page {page_num + 1} ---\\n"
                text += page.get_text()
            
            pdf.close()
            return text
            
        except Exception as e:
            logger.error(f"Error reading PDF {file_path}: {e}")
            return ""
    
    def read_all_pdfs_in_folder(self, folder_path: str) -> List[str]:
        """Read all PDFs in a folder"""
        all_text = []
        
        try:
            if not os.path.exists(folder_path):
                logger.warning(f"Folder {folder_path} does not exist")
                return all_text
                
            for filename in os.listdir(folder_path):
                if filename.lower().endswith(".pdf"):
                    file_path = os.path.join(folder_path, filename)
                    logger.info(f"Reading: {file_path}")
                    text = self.read_pdf(file_path)
                    if text:
                        all_text.append(text)
            
            return all_text
            
        except Exception as e:
            logger.error(f"Error reading PDFs from folder {folder_path}: {e}")
            return []
    
    def setup_vectorstore(self):
        """Setup or connect to existing vector store"""
        try:
            # Check if collection exists
            collections = [c.name for c in self.qdrant_client.get_collections().collections]
            
            if COLLECTION_NAME not in collections:
                logger.info(f"Collection {COLLECTION_NAME} not found. Creating and ingesting documents...")
                self.ingest_documents()
            else:
                logger.info(f"Collection {COLLECTION_NAME} exists. Connecting...")
            
            # Initialize vector store
            self.vectorstore = Qdrant(
                client=self.qdrant_client,
                collection_name=COLLECTION_NAME,
                embeddings=self.embedding_model
            )
            
        except Exception as e:
            logger.error(f"Error setting up vector store: {e}")
            raise
    
    def ingest_documents(self):
        """Ingest PDF documents into vector store"""
        try:
            # Read PDFs from artifacts folder
            pdf_texts = self.read_all_pdfs_in_folder(ARTIFACTS_FOLDER)
            
            if not pdf_texts:
                logger.warning("No PDFs found or read successfully")
                return
            
            # Create documents
            documents = [Document(page_content=text) for text in pdf_texts]
            
            # Split documents into chunks
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=CHUNK_SIZE,
                chunk_overlap=CHUNK_OVERLAP
            )
            chunked_docs = text_splitter.split_documents(documents)
            
            # Create collection
            self.qdrant_client.create_collection(
                collection_name=COLLECTION_NAME,
                vectors_config=VectorParams(
                    size=self.embedding_model.client.get_sentence_embedding_dimension(),
                    distance=Distance.COSINE
                )
            )
            
            # Create vector store and add documents
            vectorstore = Qdrant(
                client=self.qdrant_client,
                collection_name=COLLECTION_NAME,
                embeddings=self.embedding_model
            )
            vectorstore.add_documents(chunked_docs)
            
            logger.info(f"Successfully ingested {len(chunked_docs)} chunks into Qdrant collection '{COLLECTION_NAME}'")
            
        except Exception as e:
            logger.error(f"Error ingesting documents: {e}")
            raise
    
    def get_context_for_query(self, query: str, llm) -> str:
        """Search for relevant documents"""
        try:
            if not self.vectorstore:
                logger.error("Vector store not initialized")
                return []
            
            retriever = self.vectorstore.as_retriever(search_kwargs={"k": 5})

            rag_chain = RetrievalQA.from_chain_type(
                llm=llm,
                retriever=retriever,
                return_source_documents=True
            )
            print(query,"_"*50)
            return rag_chain.invoke(query)
            
        except Exception as e:
            logger.error(f"Error searching documents: {e}")
            return []
  