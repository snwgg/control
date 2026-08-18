import sqlite3
def get_connection():
    conn = sqlite3.connect("vendas.db")
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn

def criar_banco():
    conn = get_connection()
    conn.execute("CREATE TABLE IF NOT EXISTS contatos (id INTEGER PRIMARY KEY, tipo TEXT, nome TEXT, telefone TEXT, notas TEXT)")
    conn.execute("CREATE TABLE IF NOT EXISTS produtos (id INTEGER PRIMARY KEY, nome_modelo TEXT, categoria TEXT, data_compra DATE, fornecedor_id INTEGER, valor_produto REAL DEFAULT 0, frete_compra REAL DEFAULT 0, custos_extras REAL DEFAULT 0, data_venda DATE, cliente_id INTEGER, valor_bruto_venda REAL DEFAULT 0, taxa_plataforma_pct REAL DEFAULT 0, custo_anuncio REAL DEFAULT 0, frete_envio REAL DEFAULT 0, status TEXT DEFAULT 'Pendente')")
    conn.commit()
    conn.close()
if __name__=="__main__": criar_banco()
