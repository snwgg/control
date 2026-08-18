import pandas as pd
from datetime import datetime, date
from database import get_connection

def add_contato(tipo, nome, telefone="", notas=""):
    conn = get_connection()
    conn.execute("INSERT INTO contatos (tipo, nome, telefone, notas) VALUES (?,?,?,?)", (tipo, nome, telefone, notas))
    conn.commit(); conn.close()

def get_contatos(tipo=None):
    conn = get_connection()
    q = "SELECT * FROM contatos WHERE tipo = ?" if tipo else "SELECT * FROM contatos"
    df = pd.read_sql_query(q, conn, params=(tipo,) if tipo else ())
    conn.close()
    return df

def add_produto(nome, cat, dt, forn, val, frete, extra):
    conn = get_connection()
    conn.execute("INSERT INTO produtos (nome_modelo, categoria, data_compra, fornecedor_id, valor_produto, frete_compra, custos_extras, status) VALUES (?,?,?,?,?,?,?,'Em Estoque')", (nome, cat, dt, forn, val, frete, extra))
    conn.commit(); conn.close()

def registrar_venda(id, dt, cli, venda, taxa, anuncio, envio):
    conn = get_connection()
    conn.execute("UPDATE produtos SET data_venda=?, cliente_id=?, valor_bruto_venda=?, taxa_plataforma_pct=?, custo_anuncio=?, frete_envio=?, status='Vendido' WHERE id=?", (dt, cli, venda, taxa, anuncio, envio, id))
    conn.commit(); conn.close()

def update_status(id, status):
    conn = get_connection()
    conn.execute("UPDATE produtos SET status=? WHERE id=?", (status, id))
    conn.commit(); conn.close()

def get_produtos(status=None):
    conn = get_connection()
    q = "SELECT p.*, f.nome as fornecedor_nome, c.nome as cliente_nome FROM produtos p LEFT JOIN contatos f ON p.fornecedor_id=f.id LEFT JOIN contatos c ON p.cliente_id=c.id"
    if status: q += " WHERE p.status=?"
    df = pd.read_sql_query(q, conn, params=(status,) if status else ())
    conn.close()
    return df

def calcular_metricas(p):
    val = p.get("valor_produto") or 0
    frete = p.get("frete_compra") or 0
    extra = p.get("custos_extras") or 0
    anuncio = p.get("custo_anuncio") or 0
    taxa_pct = p.get("taxa_plataforma_pct") or 0
    bruto = p.get("valor_bruto_venda") or 0
    envio = p.get("frete_envio") or 0
    
    taxa_val = bruto * (taxa_pct / 100)
    
    # FRETE ENVIO ADICIONADO AO CUSTO TOTAL AQUI:
    custo_total = val + frete + extra + anuncio + taxa_val + envio
    
    res = {"custo_total": custo_total, "lucro_liquido": None}
    if p.get("status") == "Vendido" and bruto > 0:
        res["lucro_liquido"] = bruto - custo_total
    return res

def get_produtos_com_metricas(status=None):
    df = get_produtos(status)
    if df.empty: return df
    mets = pd.DataFrame(list(df.apply(lambda r: calcular_metricas(r.to_dict()), axis=1)))
    return pd.concat([df.reset_index(drop=True), mets.reset_index(drop=True)], axis=1)

def get_capital_investido():
    df = get_produtos_com_metricas("Em Estoque")
    return df["custo_total"].sum() if not df.empty else 0.0

def get_faturamento_mes():
    df = get_produtos_com_metricas("Vendido")
    return df["valor_bruto_venda"].sum() if not df.empty else 0.0

def get_lucro_mes():
    df = get_produtos_com_metricas("Vendido")
    return df["lucro_liquido"].sum() if not df.empty else 0.0

def get_ticket_medio():
    df = get_produtos_com_metricas("Vendido")
    return df["valor_bruto_venda"].mean() if not df.empty else 0.0
