"""Ponto de entrada da API e do site da pizzaria Forno Rosso.

Execute ``uvicorn main:app --reload`` para iniciar o servidor localmente.
"""

from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.security import OAuth2PasswordBearer
from fastapi.staticfiles import StaticFiles
from passlib.context import CryptContext
from dotenv import load_dotenv
import os

load_dotenv()
Secret_Key = os.getenv("Secret_Key")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))

app = FastAPI()
BASE_DIR = Path(__file__).resolve().parent
app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")

bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated ="auto")
oauth2_schema = OAuth2PasswordBearer(tokenUrl="auth/login-form")

from auth_routes import auth_router
from orders_routes import orders_router

app.include_router(auth_router)
app.include_router(orders_router)


@app.get("/", include_in_schema=False)
async def frontend():
    """Entrega a página principal da pizzaria na rota raiz."""
    return FileResponse(BASE_DIR / "static" / "index.html")

