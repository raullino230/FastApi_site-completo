"""Schemas Pydantic usados para validar entradas e respostas da API."""

from pydantic import BaseModel
from typing import Optional, List


class UsuarioSchema(BaseModel):
    """Dados necessários para criar uma conta de usuário."""
    nome: str
    email: str
    senha: str
    ativo: Optional[bool]
    admin: Optional[bool]

    class Config:
        """Habilita a conversão de objetos ORM para este schema."""
        from_attributes = True

class PedidoSchema(BaseModel):
  """Identificador do usuário que será dono de um novo pedido."""
  id_usuario: int

  class Config:
    """Habilita a conversão de objetos ORM para este schema."""
    from_attributes = True

class LoginSchema(BaseModel):
   """Credenciais enviadas no login por JSON."""
   email: str
   senha: str

   class Config:
       """Habilita a conversão de objetos ORM para este schema."""
       from_attributes = True

class ItemPedidoSchemas(BaseModel):
   """Dados de uma pizza/item incluído em um pedido."""
   quantidade: int
   sabor: str
   tamanho: str
   preço_unitario: float

   class Config:
       """Habilita a conversão de objetos ORM para este schema."""
       from_attributes = True

class ResponsePedidoSchemas(BaseModel):
   """Representação resumida de um pedido retornado ao cliente."""
   id: int
   status: str
   preço: float
   itens: List[ItemPedidoSchemas]

   class Config:
       """Habilita a conversão de objetos ORM para este schema."""
       from_attributes = True
