"""Rotas para criação, consulta e gerenciamento de pedidos de pizza."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from dependecies import pegar_session, verificar_token
from schemas import PedidoSchema, ItemPedidoSchemas, ResponsePedidoSchemas
from models import Pedido, Usuario, ItemPedido
from typing import List

orders_router = APIRouter(prefix="/orders", tags=["Ordens"], dependencies=[Depends(verificar_token)])
#dominio do site/orders

@orders_router.get("/")
async def pedidos():
    """Informa que o módulo de pedidos está disponível ao usuário autenticado."""
    return {"Mensagem": "Você acessou a rota de pedidos!"}

@orders_router.post("/pedido")
async def criar_pedido(pedido_schemas: PedidoSchema, session: Session = Depends(pegar_session)):
    """Cria um pedido vazio para o usuário informado."""
    novo_pedido = Pedido(usuario = pedido_schemas.id_usuario)
    session.add(novo_pedido)
    session.commit()
    return {"Mensagem": f"Pedido criado com sucesso. Id do pedido: {novo_pedido.id}"}

@orders_router.post("/pedido/canacelar/{id_pedido}")
async def cancelar_pedido(id_pedido: int, session: Session = Depends(pegar_session), usuario: Usuario = Depends(verificar_token)):
    """Cancela um pedido quando o solicitante é o dono ou administrador."""
    # usuario.admin = True
    # usuario.id = pedido.usuario 
    pedido = session.query(Pedido).filter(Pedido.id == id_pedido).first()
    if not pedido:
        raise HTTPException(status_code=400, detail="Pedido não encontrado")
    
    if not usuario.admin and usuario.id != pedido.usuario:
        raise HTTPException(status_code=400, detail="Você não tem autorização para fazer essa alteração")

    pedido.status = "Cancelado"
    session.commit()
    return {
        "Mensagem": f"Pedido {pedido.id} cancelado com sucesso",
        "Pedido": pedido
    }

@orders_router.get("/listar")
async def listar_pedidos(session: Session = Depends(pegar_session), usuario: Usuario = Depends(verificar_token)):
    """Lista todos os pedidos; acesso permitido somente a administradores."""
    if not usuario.admin:
        raise HTTPException(status_code=401, detail="Você não tem autorização para fazer essa operação")
    else:
        pedidos = session.query(Pedido).all()
        return {
            "Pedidos": pedidos
        }

@orders_router.post("/pedido/adicionar-item/{id_pedido}")
async def adicionar_item_pedido(id_pedido: int ,item_pedido_schemas: ItemPedidoSchemas,session: Session = Depends(pegar_session), usuario: Usuario = Depends(verificar_token)):
    """Adiciona uma pizza ao pedido e atualiza o valor total."""
    pedido = session.query(Pedido).filter(Pedido.id == id_pedido).first()
    if not pedido:
        raise HTTPException(status_code=400, detail="Pedido não existente!")
    
    if not usuario.admin and usuario.id != pedido.usuario:
        raise HTTPException(status_code=401, detail="Você não tem autorização para fazer essa alteração!")
    item_pedido = ItemPedido(item_pedido_schemas.quantidade, item_pedido_schemas.sabor, item_pedido_schemas.tamanho, item_pedido_schemas.preço_unitario, id_pedido)

    session.add(item_pedido)
    pedido.calcular_preço()
    session.commit()
    return {
        "Mensagem": "Item adicionado com sucesso!",
        "item_id": item_pedido.id,
        "Preço_Pedido": pedido.preço
    }

@orders_router.post("/pedido/remover-item/{id_item_pedido}")
async def remover_item_pedido(id_item_pedido: int ,session: Session = Depends(pegar_session), usuario: Usuario = Depends(verificar_token)):
    """Remove um item do pedido quando o solicitante possui permissão."""
    item_pedido = session.query(ItemPedido).filter(ItemPedido.id == id_item_pedido).first()
    if not item_pedido:
        raise HTTPException(status_code=400, detail="Item no pedido não existente!")
    
    pedido = session.query(Pedido).filter(Pedido.id == item_pedido.pedido).first()
    if not pedido:
        raise HTTPException(status_code=400, detail="Pedido do item nao existente!")

    if not usuario.admin and usuario.id != pedido.usuario:
        raise HTTPException(status_code=401, detail="Você não tem autorização para fazer essa alteração!")
    
    session.delete(item_pedido)
    pedido.calcular_preço()
    session.commit()
    return {
        "Mensagem": "Item removido com sucesso!",
        "Quantidade_Itens_Pedido": len(pedido.itens),
        "Pedido": pedido
    }

#finalizar um pedido

@orders_router.post("/pedido/finalizar/{id_pedido}")
async def finalizar_pedido(id_pedido: int, session: Session = Depends(pegar_session), usuario: Usuario = Depends(verificar_token)):
    """Marca um pedido como finalizado para o dono ou administrador."""
    # usuario.admin = True
    # usuario.id = pedido.usuario 
    pedido = session.query(Pedido).filter(Pedido.id == id_pedido).first()
    if not pedido:
        raise HTTPException(status_code=400, detail="Pedido não encontrado")
    
    if not usuario.admin and usuario.id != pedido.usuario:
        raise HTTPException(status_code=400, detail="Você não tem autorização para fazer essa alteração")

    pedido.status = "Finalizado"
    session.commit()
    return {
        "Mensagem": f"Pedido {pedido.id} finalizado com sucesso",
        "Pedido": pedido
    }

#visualizar 1 pedido
@orders_router.get("/pedido/{id_pedido}")
async def visualizar_pedido(id_pedido: int, session: Session = Depends(pegar_session), usuario: Usuario = Depends(verificar_token)):
    """Retorna um pedido específico e a quantidade de itens que ele possui."""
    pedido = session.query(Pedido).filter(Pedido.id == id_pedido).first()
    if not pedido:
        raise HTTPException(status_code=400, detail="Pedido não encontrado")
        
    if not usuario.admin and usuario.id != pedido.usuario:
       raise HTTPException(status_code=400, detail="Você não tem autorização para ver esse pedido!")

    return{
        "Quantidade_itens_pedido": len(pedido.itens),
        "Pedido": pedido
    }
    
 
# visualiza todos os pedidos de 1 usuario

@orders_router.get("/listar/pedidos-usuario", response_model=List[ResponsePedidoSchemas])
async def visualizar_pedido(session: Session = Depends(pegar_session), usuario: Usuario = Depends(verificar_token)):
    """Lista os pedidos pertencentes ao usuário autenticado."""
    pedido = session.query(Pedido).filter(Pedido.usuario == usuario.id).all()
    return pedido
