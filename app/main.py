import os
import uvicorn
from fastapi import FastAPI, File, UploadFile, HTTPException, Query, Depends
from .security import verify_api_key
from .pdf_processor import process_pdf_to_chromadb
from .query_processor import cached_ask
from .config import UPLOAD_DIR

app = FastAPI(
    title="RAG Service",
    description="Retrieval Augmented Generation (RAG) dengan FastAPI, ChromaDB, dan Ollama (Model = Llama3.2)",
    version="1.0.0"
)

@app.post("/upload-pdf/", tags=["File Upload"])
async def upload_pdf(file: UploadFile = File(...), api_key: str = Depends(verify_api_key)):
    """
    Endpoint untuk mengunggah file PDF dan memproses isinya ke dalam ChromaDB.
    
    Parameter:
      - file: File PDF yang akan diupload.
      - api_key: API key untuk autentikasi.
    
    Returns:
      - Pesan sukses jika file berhasil diproses.
    """
    file_path = os.path.join(UPLOAD_DIR, file.filename)
    with open(file_path, "wb") as f:
        f.write(await file.read())
    
    process_pdf_to_chromadb(file_path)
    return {"message": "PDF processed successfully"}

@app.post("/ask/", tags=["Query"])
async def ask_question(query: str = Query(...), api_key: str = Depends(verify_api_key)):
    """
    Endpoint untuk mengajukan pertanyaan.
    
    Parameter:
      - query: Pertanyaan yang diajukan.
      - api_key: API key untuk autentikasi.
    
    Returns:
      - Jawaban dari LLM beserta dokumen sumber, waktu respons, dan token yang digunakan.
    """
    return cached_ask(query)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
 
