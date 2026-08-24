# src/main.py
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

# Importa os módulos do nosso projeto
from . import models, schemas, ai_service, services
from .database import engine, SessionLocal

# Cria as tabelas no banco (incluindo as novas)
models.Base.metadata.create_all(bind=engine)

# Inicia o app FastAPI
app = FastAPI()

# Permite que o index.html converse com a API (CORS)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def home():
    return {"status": "API FinanceAI rodando com sucesso!"}

# Função para conectar ao banco de dados em cada requisição
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ROTA 1: Salva Usuario
@app.post("/usuarios/", response_model=schemas.UsuarioResponse, status_code=status.HTTP_201_CREATED)
def criar_usuario(usuario: schemas.UsuarioCreate, db: Session = Depends(get_db)):
    db_usuario = models.Usuario(nome=usuario.nome, email=usuario.email)
    db.add(db_usuario)
    db.commit()
    db.refresh(db_usuario)
    return db_usuario

# ROTA 2: Salva as Metas do Setup Inicial e devolve análise com histórico
@app.post("/usuarios/{usuario_id}/setup-inicial/", status_code=status.HTTP_201_CREATED)
def cadastrar_setup_inicial(usuario_id: int, setup: schemas.SetupInicialCreate, db: Session = Depends(get_db)):
    usuario = db.query(models.Usuario).filter(models.Usuario.id == usuario_id).first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuário não encontrado.")
    
    db.query(models.MetaOrcamento).filter(models.MetaOrcamento.usuario_id == usuario_id).delete()
    
    novas_metas = [
        models.MetaOrcamento(
            usuario_id=usuario_id,
            categoria=meta.categoria,
            valor_limite=meta.valor_limite
        )
        for meta in setup.metas
    ]
    
    db.add_all(novas_metas)
    db.commit()

    metas_dict = {meta.categoria.value: meta.valor_limite for meta in setup.metas}
    gastos_dict, transacoes = services.obter_acumulado_transacoes(db, usuario_id)
    analise = services.calcular_saude_50_30_20(metas_dict, gastos_dict)

    return {"metas": setup.metas, "analise": analise, "gastos": gastos_dict, "transacoes": transacoes}

# ROTA 3: Recebe o texto, usa a IA, salva a transação e devolve o feedback
@app.post("/usuarios/{usuario_id}/transacao-ia/")
def adicionar_transacao_por_texto(
    usuario_id: int, 
    payload: schemas.TransacaoIATexto, 
    db: Session = Depends(get_db)
):
    usuario = db.query(models.Usuario).filter(models.Usuario.id == usuario_id).first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuário não encontrado.")

    # 1. A IA (Gemini) interpreta o texto
    dados_extraidos = ai_service.interpretar_transacao(payload.texto)

    # 2. Salva o gasto real no extrato
    nova_transacao = models.Transacao(
        usuario_id=usuario_id,
        categoria=dados_extraidos["categoria"],
        descricao=dados_extraidos["descricao"],
        valor=dados_extraidos["valor"]
    )
    db.add(nova_transacao)
    db.commit()

    # 3. Calcula a matemática para gerar a mensagem inteligente
    mensagem_feedback = services.processar_feedback_transacao(
        db=db,
        usuario_id=usuario_id,
        categoria_str=dados_extraidos["categoria"],
        valor_transacao=dados_extraidos["valor"]
    )

    return {
        "categoria": dados_extraidos["categoria"],
        "descricao": dados_extraidos["descricao"],
        "valor": dados_extraidos["valor"],
        "feedback_ia": mensagem_feedback
    }

# ROTA 4: Buscar as metas salvas do usuário e os gastos acumulados
@app.get("/usuarios/{usuario_id}/metas/")
def obter_metas(usuario_id: int, db: Session = Depends(get_db)):
    usuario = db.query(models.Usuario).filter(models.Usuario.id == usuario_id).first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuário não encontrado.")
    
    metas_dict = {m.categoria.value: m.valor_limite for m in usuario.metas}
    gastos_dict, transacoes = services.obter_acumulado_transacoes(db, usuario_id)
    analise = services.calcular_saude_50_30_20(metas_dict, gastos_dict)

    return {"metas": usuario.metas, "analise": analise, "gastos": gastos_dict, "transacoes": transacoes}

# Rota 5 para verificar se já existe algum usuário no banco
@app.get("/usuarios/primeiro/")
def obter_primeiro_usuario(db: Session = Depends(get_db)):
    # Correção: Usar models.Usuario ao invés de apenas usuario
    primeiro_user = db.query(models.Usuario).first()
    if not primeiro_user:
        raise HTTPException(status_code=404, detail="Nenhum usuário cadastrado.")
    return primeiro_user

# ROTA PARA RESETAR TODOS OS DADOS FINANCEIROS
@app.delete("/reset/")
def resetar_dados(db: Session = Depends(get_db)):
    try:
        # Usa o synchronize_session=False e o nome correto da tabela: MetaOrcamento
        db.query(models.Transacao).delete(synchronize_session=False)
        db.query(models.MetaOrcamento).delete(synchronize_session=False)
        db.commit()
        return {"mensagem": "Dados financeiros resetados com sucesso!"}
    except Exception as e:
        db.rollback()
        print(f"ERRO GRAVE AO RESETAR: {str(e)}") 
        raise HTTPException(status_code=500, detail="Erro interno ao apagar dados.")


@app.delete("/usuarios/{usuario_id}/transacoes/{transacao_id}/")
def deletar_transacao(usuario_id: int, transacao_id: int, db: Session = Depends(get_db)):
    # Correção: usar models.Transacao
    transacao = db.query(models.Transacao).filter(
        models.Transacao.id == transacao_id, 
        models.Transacao.usuario_id == usuario_id
    ).first()
    
    if not transacao:
        raise HTTPException(status_code=404, detail="Transação não encontrada")
    
    # Apaga do banco e salva
    db.delete(transacao)
    db.commit()
    
    return {"mensagem": "Lançamento apagado com sucesso!"}