"""Dependências compartilhadas pelas rotas da API."""

from fastapi import Depends, HTTPException
from models import db, Usuario
from sqlalchemy.orm import sessionmaker, Session
from jose import jwt, JWTError
from main import Secret_Key, ALGORITHM, oauth2_schema


def pegar_session():
    """Fornece uma sessão SQLAlchemy e a encerra após a requisição."""

    try:
        Session = sessionmaker(bind=db)     #criando uma sessão com o banco de dados
        session = Session()                 #criando uma sessão com o banco de dados

        yield session  #retorna a sessão mas não a fecha

    finally:

        session.close()

def verificar_token(token: str = Depends(oauth2_schema), session: Session = Depends(pegar_session)):
    """Valida o JWT recebido e retorna o usuário vinculado ao token.

    Raises:
        HTTPException: Se o token for inválido, expirado ou não apontar para um usuário.
    """
    try:
        dic_info = jwt.decode(token ,Secret_Key, algorithms=[ALGORITHM])
        id_usuario = int(dic_info.get("sub"))
    except JWTError:
        raise HTTPException(status_code=401, detail="Acesso Negado, verifique a validade do token!")
    #verifica se o token é válido
    #extrair o id do usuario do token
    usuario = session.query(Usuario).filter(Usuario.id == id_usuario).first()
    if not usuario:
        raise HTTPException(status_code=401, detail="Acesso Invalido")
    return usuario
