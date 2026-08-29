from pydantic import BaseModel, Field
from datetime import datetime
from .models import TipoCategoria

# 1. Usuário 
class UsuarioCreate(BaseModel):
    nome: str = Field(..., examples=["Ana Silva"])
    email: str = Field(..., examples=["ana@email.com"])

class UsuarioResponse(UsuarioCreate):
    id: int

    class Config:
        from_attributes = True

# 2. Metas do Orçamento (O Planejamento / "Teto")
class MetaOrcamentoCreate(BaseModel):
    categoria: TipoCategoria
    valor_limite: float = Field(..., gt=0, description="Valor limite estabelecido para o mês")

class MetaOrcamentoResponse(MetaOrcamentoCreate):
    id: int
    usuario_id: int

    class Config:
        from_attributes = True

# 3. Setup Inicial (Para receber todas as metas de uma vez do frontend)
class SetupInicialCreate(BaseModel):
    metas: list[MetaOrcamentoCreate]

# 4. Transações (O Gasto/Ganho Real do Dia a Dia)
class TransacaoCreate(BaseModel):
    categoria: TipoCategoria
    descricao: str = Field(..., examples=["Uber", "Festa", "Salário"])
    valor: float = Field(..., gt=0)

class TransacaoResponse(TransacaoCreate):
    id: int
    usuario_id: int
    data: datetime

    class Config:
        from_attributes = True

# 5. Entrada de Texto para Inteligência Artificial
class TransacaoIATexto(BaseModel):
    texto: str = Field(..., examples=["Gastei 100 reais numa festa ontem"])