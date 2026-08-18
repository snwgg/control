import streamlit as st
import pandas as pd
from datetime import date
import database
import backend

st.set_page_config(page_title="Controle de Vendas", page_icon="📦", layout="wide")
database.criar_banco()

def formatar_moeda(valor):
    if valor is None: return "R$ 0,00"
    return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

def seletor_contato(label, tipo, key):
    df_contatos = backend.get_contatos(tipo=tipo)
    if df_contatos.empty:
        st.warning(f"Nenhum {tipo.lower()} cadastrado ainda.")
        return None
    opcoes = dict(zip(df_contatos["nome"], df_contatos["id"]))
    nome = st.selectbox(label, opcoes.keys(), key=key)
    return opcoes[nome]

st.sidebar.title("📦 Menu")
pagina = st.sidebar.radio("Navegação", ["Dashboard", "Registrar Compra", "Registrar Venda", "Atualizar Status", "Estoque (Tabela)", "Contatos"])

if pagina == "Dashboard":
    st.title("📊 Dashboard")
    capital = backend.get_capital_investido()
    fat_mes = backend.get_faturamento_mes()
    lucro_mes = backend.get_lucro_mes()
    tk_medio = backend.get_ticket_medio()
    
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Capital Investido", formatar_moeda(capital))
    c2.metric("Faturamento do Mês", formatar_moeda(fat_mes))
    c3.metric("Lucro Líquido do Mês", formatar_moeda(lucro_mes))
    c4.metric("Ticket Médio", formatar_moeda(tk_medio))

elif pagina == "Registrar Compra":
    st.title("🛒 Registrar Compra")
    with st.form("form_compra"):
        nome = st.text_input("Produto")
        cat = st.text_input("Categoria")
        dt = st.date_input("Data")
        forn = seletor_contato("Fornecedor", "Fornecedor", "f1")
        val = st.number_input("Valor (R$)", step=1.0)
        frete = st.number_input("Frete (R$)", step=1.0)
        extra = st.number_input("Extra (R$)", step=1.0)
        if st.form_submit_button("Salvar") and nome and forn:
            backend.add_produto(nome, cat, dt, forn, val, frete, extra)
            st.success("Salvo!")

elif pagina == "Registrar Venda":
    st.title("💰 Registrar Venda")
    df = backend.get_produtos("Em Estoque")
    if not df.empty:
        opcoes = {f"#{r['id']} - {r['nome_modelo']}": r["id"] for _, r in df.iterrows()}
        prod = st.selectbox("Item", opcoes.keys())
        with st.form("venda"):
            dt = st.date_input("Data")
            cli = seletor_contato("Cliente", "Cliente", "c1")
            venda = st.number_input("Valor Venda", step=1.0)
            taxa = st.number_input("Taxa Plataforma %", step=0.5)
            anuncio = st.number_input("Anúncio", step=1.0)
            envio = st.number_input("Frete Envio", step=1.0)
            if st.form_submit_button("Vender") and cli:
                backend.registrar_venda(opcoes[prod], dt, cli, venda, taxa, anuncio, envio)
                st.success("Vendido!")
                st.rerun()

elif pagina == "Atualizar Status":
    st.title("🔄 Atualizar Status")
    df = backend.get_produtos()
    if not df.empty:
        opcoes = {f"#{r['id']} - {r['nome_modelo']}": r["id"] for _, r in df.iterrows()}
        prod = st.selectbox("Item", opcoes.keys())
        status = st.selectbox("Status", ["Pendente", "Em Estoque", "Vendido", "Devolução"])
        if st.button("Salvar"):
            backend.update_status(opcoes[prod], status)
            st.success("Atualizado!")
            st.rerun()

elif pagina == "Estoque (Tabela)":
    st.title("📋 Tabela")
    df = backend.get_produtos_com_metricas()
    st.dataframe(df, use_container_width=True)

elif pagina == "Contatos":
    st.title("👥 Contatos")
    with st.form("form_c"):
        tipo = st.selectbox("Tipo", ["Cliente", "Fornecedor"])
        nome = st.text_input("Nome")
        tel = st.text_input("Telefone")
        notas = st.text_area("Notas")
        if st.form_submit_button("Salvar") and nome:
            backend.add_contato(tipo, nome, tel, notas)
            st.success("Salvo!")
