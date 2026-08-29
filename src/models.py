from sqlalchemy import Column, Integer, String, Float, ForeignKey, Enum, DateTime
from sqlalchemy.orm import relationship
import enum
from datetime import datetime
from .database import Base

#  Categorias 
class TipoCategoria(str, enum.Enum):
    RECEITA = "Receita"
    DESPESA_FIXA = "Despesa Fixa"
    DESPESA_VARIAVEL = "Despesa Variável"
    DESPESA_ADICIONAL = "Despesa Adicional"
    INVESTIMENTO = "Investimento"

class Usuario(Base):
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String, index=True)
    email = Column(String, unique=True, index=True)

    # Relações
    metas = relationship("MetaOrcamento", back_populates="usuario")
    transacoes = relationship("Transacao", back_populates="usuario")

# TABELA 1: O Planejamento (O "Teto" do mês)
class MetaOrcamento(Base):
    __tablename__ = "metas_orcamento"

    id = Column(Integer, primary_key=True, index=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"))
    categoria = Column(Enum(TipoCategoria))
    valor_limite = Column(Float)

    usuario = relationship("Usuario", back_populates="metas")

# TABELA 2: O Dia a Dia (O "Realizado")
class Transacao(Base):
    __tablename__ = "transacoes"

    id = Column(Integer, primary_key=True, index=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"))
    categoria = Column(Enum(TipoCategoria))
    descricao = Column(String)
    valor = Column(Float)
    data = Column(DateTime, default=datetime.utcnow) # Marca a hora exata do gasto

    usuario = relationship("Usuario", back_populates="transacoes")

    