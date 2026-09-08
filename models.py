"""Modelos SQLAlchemy e configuração do banco de dados."""

import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, Column, String, Integer, Boolean, Float, ForeignKey
from sqlalchemy.orm import declarative_base, relationship

load_dotenv()

# Conexão com o banco
# Em produção (Vercel): usa DATABASE_URL (PostgreSQL)
# Em desenvolvimento: usa SQLite local
DATABASE_URL = os.getenv("DATABASE_URL")

if DATABASE_URL:
    # Produção: PostgreSQL no Neon
    if DATABASE_URL.startswith("postgres://"):
        DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)
    db = create_engine(DATABASE_URL)
else:
    # Desenvolvimento: SQLite local
    db = create_engine("sqlite:///banco.db")

# Criar a base do banco de dados
Base = declarative_base()

# Criar as classes/tabelas do banco de dados:

class Usuario(Base):
    """Usuário que pode autenticar-se e realizar pedidos."""
    __tablename__ = "usuarios"

    id = Column("id", Integer, primary_key=True, autoincrement=True)
    nome = Column("nome", String)
    email = Column("email", String, nullable=False, unique=True)
    senha = Column("senha", String, nullable=False)
    ativo = Column("ativo", Boolean)
    admin = Column("admin", Boolean, default=False)

    def __init__(self, nome, email, senha, ativo=True, admin=False):
        """Inicializa um usuário com suas credenciais já criptografadas."""
        self.nome = nome
        self.email = email
        self.senha = senha
        self.ativo = ativo
        self.admin = admin


class Pedido(Base):
    """Pedido de pizzas associado a um usuário."""
    __tablename__ = "pedidos"

    id = Column("id", Integer, primary_key=True, autoincrement=True)
    status = Column("status", String)
    usuario = Column("usuario", ForeignKey("usuarios.id"))
    preço = Column("preço", Float)
    itens = relationship("ItemPedido", cascade="all, delete")

    def __init__(self, usuario, status="Pendente", preço=0):
        """Cria um pedido pendente com preço inicial igual a zero."""
        self.usuario = usuario
        self.status = status
        self.preço = preço

    def calcular_preço(self):
        """Recalcula o valor total a partir dos itens do pedido."""
        self.preço = sum(item.preço_unitario * item.quantidade for item in self.itens)


class ItemPedido(Base):
    """Pizza individual, sua quantidade e preço dentro de um pedido."""
    __tablename__ = "itens_pedido"

    id = Column("id", Integer, primary_key=True, autoincrement=True)
    quantidade = Column("quantidade", Integer)
    sabor = Column("sabor", String)
    tamanho = Column("tamanho", String)
    preço_unitario = Column("preço_unitario", Float)
    pedido = Column("pedido", ForeignKey("pedidos.id"))

    def __init__(self, quantidade, sabor, tamanho, preço_unitario, pedido):
        """Inicializa um item ligado ao identificador de um pedido."""
        self.quantidade = quantidade
        self.sabor = sabor
        self.tamanho = tamanho
        self.preço_unitario = preço_unitario
        self.pedido = pedido