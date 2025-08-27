#### E-commerce-chatbot

Instructions for setup:

1. add GEMINI_API_KEY in .env file
2. start qdrant vector db via docker with command `docker run -p 6333:6333 -p 6334:6334 qdrant/qdrant`.
3. Create virtual environment: `python3.11 -m venv venv`
4. Activate virtual environment: `source venv/bin/activate`
5. Install requirements:  `pip install -r requirements.txt`.
6. Run streamlit app  `streamlit run app.py`.
