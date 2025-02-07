import time
import logging
from functools import lru_cache
from fastapi import HTTPException
from langchain_core.prompts import ChatPromptTemplate
from langchain_chroma import Chroma
from langchain_ollama import OllamaLLM, OllamaEmbeddings
from langchain.chains import ConversationalRetrievalChain
from .config import CHROMA_DB_DIR

# Inisialisasi LLM dan embeddings
llm = OllamaLLM(model="llama3.2")
embeddings = OllamaEmbeddings(model="nomic-embed-text")

# Definisikan prompt untuk QA
qa_system_prompt = qa_system_prompt = """
You are an assistant for question-answering tasks. Use the following context to provide a clear, accurate, and concise answer. 
If the context does not contain enough information, say "I don't know." Do not make up answers.

Context: {context}

Question: {question}

Answer:
"""

qa_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", qa_system_prompt),
        ("human", "Question: {question}"),
    ]
)

def process_query(query: str):
    """
    Memproses query pertanyaan dengan langkah-langkah:
      - Mengambil dokumen relevan dari ChromaDB.
      - Menggunakan ConversationalRetrievalChain dengan LLM untuk mendapatkan jawaban.
      - Menghitung waktu respons dan jumlah token yang digunakan.
    
    Parameter:
      query (str): Pertanyaan yang diajukan.
      
    Returns:
      dict: Berisi jawaban, dokumen sumber, waktu respons, dan token yang digunakan.
      
    Raises:
      HTTPException: Jika tidak ada dokumen atau terjadi error pada pemrosesan.
    """
    start_time = time.time()
    try:
        vector_store = Chroma(
            persist_directory=CHROMA_DB_DIR,
            collection_name="pdf_documents",
            embedding_function=embeddings,
        )

        # Pastikan koleksi dokumen ada
        if not vector_store.get():
            raise HTTPException(status_code=404, detail="No documents found. Upload a PDF first.")

        # Ambil dokumen relevan
        retriever = vector_store.as_retriever()
        relevant_docs = retriever.get_relevant_documents(query)

        logging.info(f"Retrieved {len(relevant_docs)} documents for query: {query}")
        for i, doc in enumerate(relevant_docs):
            logging.info(f"Document {i + 1}: {doc.page_content[:200]}...")

        # Buat chain QA
        qa_chain = ConversationalRetrievalChain.from_llm(
            llm=llm,
            retriever=retriever,
            combine_docs_chain_kwargs={"prompt": qa_prompt},
            return_source_documents=True,
        )
        response = qa_chain.invoke({"question": query, "chat_history": []})
        total_time = time.time() - start_time

        # Penghitungan token
        token_usage = len(query.split()) + sum(len(doc.page_content.split()) for doc in relevant_docs)
        logging.info(f"Response time: {total_time:.2f} seconds, Tokens used: {token_usage}")

        return {
            "answer": response["answer"],
            "source_documents": relevant_docs,
            "response_time": total_time,
            "tokens_used": token_usage
        }
    except HTTPException:
        raise
    except Exception as e:
        total_time = time.time() - start_time
        logging.error(f"Error processing query: {e}, response time: {total_time:.2f} seconds")
        raise HTTPException(status_code=500, detail=str(e))

# Caching hasil query untuk optimasi performa
@lru_cache(maxsize=100)
def cached_ask(query: str):
    return process_query(query)
 
