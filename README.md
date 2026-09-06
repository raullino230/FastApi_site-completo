# Forno Rosso — API e Pizzaria Web

Aplicação de pedidos para uma pizzaria. O projeto combina uma API em **FastAPI**, banco de dados **SQLite** com **SQLAlchemy/Alembic**, autenticação por **JWT** e uma interface web responsiva, servida pela própria aplicação.

## O que é possível fazer

- Criar uma conta e entrar com e-mail e senha.
- Adicionar pizzas do cardápio ao carrinho, escolher tamanho e quantidade.
- Criar um pedido e enviar cada item para a API.
- Consultar os pedidos do usuário autenticado e cancelar pedidos pendentes.
- Visualizar todos os pedidos caso o usuário seja administrador.
- Acessar uma página web completa em `/` e a documentação interativa do FastAPI em `/docs`.

## Tecnologias

| Área | Ferramentas |
| --- | --- |
| API | FastAPI e Uvicorn |
| Persistência | SQLAlchemy, SQLite e Alembic |
| Autenticação | JWT (`python-jose`), SHA-256 e bcrypt |
| Interface | HTML, CSS e JavaScript sem framework |
| Configuração | python-dotenv |

## Estrutura do projeto

```text
.
├── alembic/                 # Histórico das migrações do banco
├── static/
│   ├── index.html           # Estrutura da página da pizzaria
│   ├── styles.css           # Layout responsivo e identidade visual
│   └── app.js               # Carrinho, login e chamadas à API
├── auth_routes.py           # Rotas de cadastro, login e renovação de token
├── orders_routes.py         # Rotas de pedidos e itens
├── models.py                # Modelos SQLAlchemy e conexão SQLite
├── schemas.py               # Contratos Pydantic de entrada e resposta
├── dependecies.py           # Sessão do banco e validação do token
├── main.py                  # Aplicação FastAPI e entrega dos arquivos estáticos
├── requirements.txt         # Dependências diretas do projeto
└── .env.example             # Modelo de variáveis de ambiente
```

## Instalação

Pré-requisito: Python 3.11 ou superior.

No PowerShell, na pasta do projeto:

```powershell
py -m venv Venv
.\Venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
alembic upgrade head
uvicorn main:app --reload
```

Se a execução de scripts estiver bloqueada no PowerShell, ative o ambiente somente para a sessão atual:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\Venv\Scripts\Activate.ps1
```

Depois, abra:

| Endereço | Finalidade |
| --- | --- |
| `http://127.0.0.1:8000/` | Site da pizzaria |
| `http://127.0.0.1:8000/docs` | Swagger UI / documentação interativa |
| `http://127.0.0.1:8000/redoc` | Documentação ReDoc |

## Variáveis de ambiente

Crie o arquivo `.env` com base no `.env.example`:

```env
Secret_Key=uma-chave-longa-e-aleatoria
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

| Variável | Descrição |
| --- | --- |
| `Secret_Key` | Chave usada para assinar os tokens JWT. Não a publique. |
| `ALGORITHM` | Algoritmo de assinatura do JWT. O projeto usa `HS256`. |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Duração do token de acesso, em minutos. |

> O `.env` e bancos `*.db` são ignorados pelo Git. Em produção, use segredos fornecidos pelo ambiente de hospedagem, nunca uma chave de exemplo.

## Banco de dados

O banco padrão é o arquivo SQLite `banco.db`. Os modelos possuem as seguintes relações:

```text
Usuario (1) ──── (N) Pedido (1) ──── (N) ItemPedido
```

| Tabela | Campos principais |
| --- | --- |
| `usuarios` | `id`, `nome`, `email`, `senha`, `ativo`, `admin` |
| `pedidos` | `id`, `status`, `usuario`, `preço` |
| `itens_pedido` | `id`, `quantidade`, `sabor`, `tamanho`, `preço_unitario`, `pedido` |

### Migrações

```powershell
# Aplica todas as migrações pendentes
alembic upgrade head

# Cria uma migração após alterar models.py
alembic revision --autogenerate -m "descricao da alteracao"

# Desfaz a última migração
alembic downgrade -1
```

## Autenticação

Após um login bem-sucedido, a API retorna um `access_token`. Envie-o nas rotas protegidas usando o cabeçalho:

```http
Authorization: Bearer SEU_ACCESS_TOKEN
```

As rotas em `/orders` exigem autenticação. O front-end guarda o token no `localStorage` do navegador para manter a sessão e o envia automaticamente nas requisições.

## Referência da API

### Autenticação

| Método | Rota | Autenticação | Corpo / finalidade |
| --- | --- | --- | --- |
| `GET` | `/auth/` | Não | Verifica a rota de autenticação. |
| `POST` | `/auth/criar_conta` | Não | Cria um usuário. |
| `POST` | `/auth/login` | Não | Faz login com JSON. |
| `POST` | `/auth/login-form` | Não | Faz login com formulário OAuth2 (`username` recebe o e-mail). |
| `GET` | `/auth/refresh` | Sim | Gera um novo token de acesso. |

#### Criar conta

```http
POST /auth/criar_conta
Content-Type: application/json

{
  "nome": "Ana Silva",
  "email": "ana@example.com",
  "senha": "uma-senha-segura",
  "ativo": true,
  "admin": false
}
```

#### Login

```http
POST /auth/login
Content-Type: application/json

{
  "email": "ana@example.com",
  "senha": "uma-senha-segura"
}
```

Resposta resumida:

```json
{
  "access_token": "eyJ...",
  "refresh_token": "eyJ...",
  "token_type": "Bearer"
}
```

### Pedidos

Todas as rotas desta seção exigem `Authorization: Bearer <token>`.

| Método | Rota | Permissão | Finalidade |
| --- | --- | --- | --- |
| `GET` | `/orders/` | Usuário autenticado | Verifica a rota de pedidos. |
| `POST` | `/orders/pedido` | Usuário autenticado | Cria um pedido vazio. |
| `POST` | `/orders/pedido/adicionar-item/{id_pedido}` | Dono do pedido ou admin | Adiciona uma pizza ao pedido. |
| `POST` | `/orders/pedido/remover-item/{id_item_pedido}` | Dono do pedido ou admin | Remove um item. |
| `POST` | `/orders/pedido/canacelar/{id_pedido}` | Dono do pedido ou admin | Cancela um pedido. |
| `POST` | `/orders/pedido/finalizar/{id_pedido}` | Dono do pedido ou admin | Marca um pedido como finalizado. |
| `GET` | `/orders/pedido/{id_pedido}` | Dono do pedido ou admin | Consulta um pedido. |
| `GET` | `/orders/listar/pedidos-usuario` | Usuário autenticado | Lista os pedidos do usuário atual. |
| `GET` | `/orders/listar` | Admin | Lista todos os pedidos. |

> A rota de cancelamento contém `canacelar` no endereço por compatibilidade com a implementação atual. Ao criar uma nova versão da API, o ideal é expor também a grafia `/cancelar/`.

#### Criar um pedido

```http
POST /orders/pedido
Authorization: Bearer SEU_ACCESS_TOKEN
Content-Type: application/json

{
  "id_usuario": 1
}
```

O ID do pedido retornado é usado para adicionar os itens.

#### Adicionar item ao pedido

```http
POST /orders/pedido/adicionar-item/1
Authorization: Bearer SEU_ACCESS_TOKEN
Content-Type: application/json

{
  "quantidade": 2,
  "sabor": "Margherita",
  "tamanho": "M",
  "preço_unitario": 49.0
}
```

## Front-end

O front-end fica em `static/` e é publicado pelo `main.py`:

- `index.html` contém as seções institucionais, os diálogos de autenticação e pedidos, e o painel lateral do carrinho.
- `styles.css` implementa a identidade visual, ilustrações em CSS, estados de interface e responsividade.
- `app.js` mantém o estado do carrinho, renderiza o cardápio, consome a API com `fetch` e gerencia o token JWT.

O catálogo atual é local ao arquivo `static/app.js`, pois a API ainda não possui uma rota de produtos/cardápio. Quando esse endpoint existir, a constante `products` poderá ser substituída por uma requisição à API.

## Fluxo de compra no site

1. O cliente escolhe pizzas, tamanho e quantidade.
2. Ao finalizar, o site pede login caso não exista uma sessão válida.
3. O navegador cria um pedido com `POST /orders/pedido`.
4. Cada pizza do carrinho é enviada para `POST /orders/pedido/adicionar-item/{id}`.
5. O carrinho é limpo e o pedido aparece em **Meus pedidos**.

## Pontos de evolução recomendados

- Criar uma entidade e rotas de `Produto` para que o cardápio venha do banco.
- Usar `DELETE` para remoção e `PATCH` para mudança de status, em vez de `POST` em todas as alterações.
- Validar no servidor que `id_usuario` do pedido corresponde ao usuário extraído do token.
- Adicionar endereço, taxa de entrega, forma de pagamento e acompanhamento de preparo.
- Implementar testes automatizados para as rotas e o fluxo de compra.
- Configurar CORS apenas se o front-end for publicado em outro domínio.

## Licença

Projeto de estudo. Adicione uma licença apropriada antes de distribuir ou usar comercialmente.
