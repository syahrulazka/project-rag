import logging
import os
from fastapi import HTTPException
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_ollama import OllamaEmbeddings
from .config import CHROMA_DB_DIR

# Inisialisasi model embedding dan text splitter
embeddings = OllamaEmbeddings(model="nomic-embed-text")
text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)

def process_pdf_to_chromadb(file_path: str):
    """
    Memproses file PDF:
      - Membaca file PDF menggunakan PyPDFLoader.
      - Memecah dokumen menjadi chunk dengan RecursiveCharacterTextSplitter.
      - Menyimpan chunk ke dalam ChromaDB.
      
    Parameter:
      file_path (str): Path file PDF yang akan diproses.
    
    Raises:
      HTTPException: Jika terjadi kesalahan dalam pemrosesan file.
    """
    try:
        loader = PyPDFLoader(file_path)
        pages = loader.load()
        chunks = text_splitter.split_documents(pages)

        # Log untuk debugging
        logging.info(f"Total chunks: {len(chunks)}")
        for i, chunk in enumerate(chunks[:5]):
            logging.info(f"Chunk {i + 1}: {chunk.page_content[:200]}...")

        # Simpan dokumen ke ChromaDB
        Chroma.from_documents(
            documents=chunks,
            embedding=embeddings,
            persist_directory=CHROMA_DB_DIR,
            collection_name="pdf_documents",
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
 
