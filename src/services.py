from sqlalchemy.orm import Session
from sqlalchemy import func
from . import models

def processar_feedback_transacao(db: Session, usuario_id: int, categoria_str: str, valor_transacao: float) -> str:
    # 1. Converte a string da categoria para o formato do nosso Enum
    try:
        categoria = models.TipoCategoria(categoria_str)
    except ValueError:
        return f"Transação registrada, mas a categoria '{categoria_str}' não possui meta configurada."

    # 2. Busca o limite (teto) definido no Setup Inicial para esta categoria
    meta = db.query(models.MetaOrcamento).filter(
        models.MetaOrcamento.usuario_id == usuario_id,
        models.MetaOrcamento.categoria == categoria
    ).first()

    teto = meta.valor_limite if meta else 0.0

    # 3. Soma todas as transações (gastos) que o usuário já teve nessa categoria
    total_gasto = db.query(func.sum(models.Transacao.valor)).filter(
        models.Transacao.usuario_id == usuario_id,
        models.Transacao.categoria == categoria
    ).scalar() or 0.0

    # 4. Formata a resposta da IA
    if categoria == models.TipoCategoria.RECEITA:
        return f"Dinheiro na conta! Sua receita total registrada agora é R$ {total_gasto:.2f}."

    saldo = teto - total_gasto
    porcentagem = (total_gasto / teto * 100) if teto > 0 else 0

    if saldo < 0:
        return f"Atenção! Você gastou R$ {valor_transacao:.2f} e ESTOUROU o limite de {categoria.value}. Você passou R$ {abs(saldo):.2f} do planejado."
    
    return f"Você gastou R$ {valor_transacao:.2f} dos seus R$ {teto:.2f} de {categoria.value}. Novo saldo: R$ {saldo:.2f} (Você usou {porcentagem:.0f}% do limite)."

def calcular_saude_50_30_20(metas_dict: dict[str, float], gastos_dict: dict[str, float]) -> dict:
    receita_planejada = float(metas_dict.get("Receita", 0.0))
    receita_extra = float(gastos_dict.get("Receita", 0.0))
    receita_total = receita_planejada + receita_extra

    limite_nec = float(metas_dict.get("Despesa Fixa", 0.0)) + float(metas_dict.get("Despesa Variável", 0.0))
    limite_des = float(metas_dict.get("Despesa Adicional", 0.0))
    limite_fut = float(metas_dict.get("Investimento", 0.0))

    gasto_nec = float(gastos_dict.get("Despesa Fixa", 0.0)) + float(gastos_dict.get("Despesa Variável", 0.0))
    gasto_des = float(gastos_dict.get("Despesa Adicional", 0.0))
    gasto_fut = float(gastos_dict.get("Investimento", 0.0))

    total_alocado = limite_nec + limite_des + limite_fut
    saldo_livre = receita_planejada - total_alocado

    # Porcentagens de cada pilar relativas ao Salário Base
    p_nec = round((limite_nec / receita_planejada) * 100, 1) if receita_planejada > 0 else 0.0
    p_des = round((limite_des / receita_planejada) * 100, 1) if receita_planejada > 0 else 0.0
    p_fut = round((limite_fut / receita_planejada) * 100, 1) if receita_planejada > 0 else 0.0

    # =========================================================
    # PARTE 1: STATUS DO PLANEJAMENTO (Metas vs Salário Base)
    # =========================================================
    if total_alocado > receita_planejada:
        status_orcamento = "vermelho"  # Metas superam o Salário Base
    elif p_nec > 50 or p_des > 30 or (receita_planejada > 0 and p_fut < 20):
        status_orcamento = "amarelo"   # Cabe no salário, mas foge da regra 50/30/20
    else:
        status_orcamento = "verde"     # Segue 100% a proporção recomendada

    # =========================================================
    # PARTE 2: STATUS DOS PILARES (Gastos Reais vs Teto + Extra)
    # =========================================================
    def avaliar_pilar(gasto, limite, porcentagem):
        excesso = gasto - limite
        if excesso <= 0:
            status = "verde"
        elif receita_extra >= excesso:
            status = "amarelo"  # Estourou a meta, mas a Renda Extra cobre
        else:
            status = "vermelho" # Estourou a meta e não há Renda Extra suficiente

        return {
            "limite": limite,
            "gasto": gasto,
            "porcentagem": porcentagem,
            "status": status
        }

    return {
        "receita_planejada": receita_planejada,
        "receita_extra": receita_extra,
        "receita_total": receita_total,
        "total_alocado": total_alocado,
        "saldo_livre": saldo_livre,
        "status_orcamento": status_orcamento,
        "necessidades": avaliar_pilar(gasto_nec, limite_nec, p_nec),
        "desejos": avaliar_pilar(gasto_des, limite_des, p_des),
        "futuro": avaliar_pilar(gasto_fut, limite_fut, p_fut)
    }

def obter_acumulado_transacoes(db: Session, usuario_id: int):
    transacoes = db.query(models.Transacao).filter(models.Transacao.usuario_id == usuario_id).all()
    gastos = {}
    for t in transacoes:
        cat = t.categoria.value if hasattr(t.categoria, "value") else str(t.categoria)
        gastos[cat] = gastos.get(cat, 0.0) + float(t.valor)
    return gastos, transacoes