import os
from dotenv import load_dotenv

# Muat variabel lingkungan dari file .env
load_dotenv()

# Direktori untuk penyimpanan file PDF yang diupload dan database Chroma
UPLOAD_DIR = os.getenv("UPLOAD_DIR", "upload")
CHROMA_DB_DIR = os.getenv("CHROMA_DB_DIR", "./data/chroma_db")

# API Key untuk autentikasi (pastikan diset melalui .env)
API_KEY = os.getenv("API_KEY", "defaultapikey")

# Pastikan direktori yang diperlukan ada
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(CHROMA_DB_DIR, exist_ok=True)
 
