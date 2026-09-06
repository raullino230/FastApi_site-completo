"""Rotas responsáveis por cadastro, login e renovação de tokens JWT."""

from fastapi import APIRouter, Depends, HTTPException
from models import Usuario
from dependecies import pegar_session, verificar_token
import hashlib
import bcrypt  
from schemas import UsuarioSchema, LoginSchema
from sqlalchemy.orm import Session
from jose import jwt, JWTError
from datetime import datetime, timedelta, timezone
from main import Secret_Key, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES
from fastapi.security import OAuth2PasswordRequestForm

auth_router = APIRouter(prefix="/auth", tags=["Autenticação"])

def criar_token(id_usuario, duração_token = timedelta(minutes = int(ACCESS_TOKEN_EXPIRE_MINUTES))):
    """Cria um JWT para o usuário com o período de validade informado."""
    data_expiração = datetime.now(timezone.utc) + duração_token

    dic_info = {"sub": str(id_usuario), "exp": data_expiração}
    jwt_codificado = jwt.encode(dic_info, Secret_Key , ALGORITHM)

    return jwt_codificado

def autenticar_usuario(email, senha, session):
    """Confere e-mail e senha e retorna o usuário autenticado ou ``False``."""
    """
    Verifica se o email e senha estão corretos.
    """
    usuario = session.query(Usuario).filter(Usuario.email == email).first()
    
    if not usuario:
        return False
    
    # 1º passo: SHA-256 (mesmo que na criação)
    senha_sha = hashlib.sha256(senha.encode()).hexdigest()
    
    # 2º passo: Verifica com bcrypt nativo
    if bcrypt.checkpw(senha_sha.encode(), usuario.senha.encode()):
        return usuario
    
    return False

def hash_senha_segura(senha: str) -> str:
    """Gera o hash bcrypt da senha após aplicar SHA-256."""
    """
    Criptografa a senha usando SHA-256 + bcrypt (sem passlib).
    """
  
    senha_sha = hashlib.sha256(senha.encode()).hexdigest()
    
  
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(senha_sha.encode(), salt).decode()


@auth_router.get("/")
async def home():
    """Informa que o módulo de autenticação está disponível."""
    return {"Mensagem": "Você acessou a rota de autenticação", "Autenticação": False}


@auth_router.post("/criar_conta")
async def criar_conta(usuario_schemas: UsuarioSchema, session: Session = Depends(pegar_session)):
    """Cria uma conta após garantir que o e-mail ainda não foi usado."""

    usuario = session.query(Usuario).filter(Usuario.email == usuario_schemas.email).first()
    if usuario:
        raise HTTPException(status_code=400, detail="Email do usuario já existe!")
    else:
        senha_cripitografada = hash_senha_segura(usuario_schemas.senha) 
        novo_usuario = Usuario(usuario_schemas.nome, usuario_schemas.email, senha_cripitografada, usuario_schemas.ativo, usuario_schemas.admin)
        session.add(novo_usuario)
        session.commit()
        return {"Mensagem": f"Usuario cadastrado com sucesso! {usuario_schemas.email}"}


@auth_router.post("/login")
async def login(login_schemas: LoginSchema, session: Session = Depends(pegar_session)):
    """Autentica com JSON e devolve tokens de acesso e renovação."""

    usuario = autenticar_usuario(login_schemas.email, login_schemas.senha, session)
    if not usuario:
        raise HTTPException(status_code=400, detail="Email do usuario não existe!, ou credenciais inválidas!")
    else:
        access_token = criar_token(usuario.id)
        refresh_token = criar_token(usuario.id, duração_token = timedelta(days=7))
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "Bearer",
            }


@auth_router.post("/login-form")
async def login_form(dados_formulario: OAuth2PasswordRequestForm = Depends(), session: Session = Depends(pegar_session)):
    """Autentica o formulário OAuth2 usado pelo Swagger e pelo fluxo de token."""

    usuario = autenticar_usuario(dados_formulario.username, dados_formulario.password, session)
    if not usuario:
        raise HTTPException(status_code=400, detail="Email do usuario não existe!, ou credenciais inválidas!")
    else:
        access_token = criar_token(usuario.id)
        return {
            "access_token": access_token,
            "token_type": "Bearer",
            }


@auth_router.get("/refresh")
async def use_refresh_token(usuario: Usuario = Depends(verificar_token)):
    """Emite um novo token de acesso para o usuário autenticado."""
    access_token = criar_token(usuario.id)
    return {
            "access_token": access_token,
            "token_type": "Bearer",
            }
