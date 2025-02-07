from fastapi import HTTPException, Depends
from fastapi.security import APIKeyHeader
from .config import API_KEY

# Menggunakan header "X-API-Key" untuk autentikasi
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=True)

def verify_api_key(api_key: str = Depends(api_key_header)):
    """
    Verifikasi API key yang dikirim melalui header.
    Jika tidak valid, akan mengembalikan HTTPException status 403.
    """
    if api_key != API_KEY:
        raise HTTPException(status_code=403, detail="Invalid API Key")
 
