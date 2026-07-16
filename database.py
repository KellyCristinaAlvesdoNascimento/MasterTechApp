import sqlite3

DB_NAME = "mastertech.db"

def conectar():
    return sqlite3.connect(DB_NAME)

def criar_tabelas():
    conn = conectar()
    cursor = conn.cursor()
    
    # Tabela de Usuários
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS usuarios (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        usuario TEXT UNIQUE,
        senha_hash TEXT,
        nome TEXT
    )""")
    
    # Tabela de Produtos
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS produtos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT,
        categoria TEXT,
        quantidade_atual INTEGER,
        preco_custo REAL,
        preco_venda REAL,
        estoque_minimo INTEGER
    )""")
    
    # Tabela de Vendas
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS vendas (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        produto_id INTEGER,
        quantidade INTEGER,
        valor_total REAL,
        forma_pagamento TEXT,
        data TEXT,
        usuario_id INTEGER,
        FOREIGN KEY(produto_id) REFERENCES produtos(id),
        FOREIGN KEY(usuario_id) REFERENCES usuarios(id)
    )""")
    
    # Tabela de Tipos de Aparelho (Nova!)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS tipos_aparelho (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT UNIQUE
    )""")
    
    # Tabela de Ordens de Serviço
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS ordens_servico (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome_cliente TEXT,
        telefone_cliente TEXT,
        tipo_aparelho TEXT,
        marca_modelo TEXT,
        numero_serie TEXT,
        estado_fisico TEXT,
        defeito_relatado TEXT,
        defeito_constatado TEXT,
        pecas_usadas TEXT,
        valor_servico REAL,
        status TEXT,
        data_entrada TEXT,
        data_saida TEXT,
        usuario_id INTEGER,
        FOREIGN KEY(usuario_id) REFERENCES usuarios(id)
    )""")
    
    # Tabela de Despesas
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS despesas (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        descricao TEXT,
        categoria TEXT,
        valor REAL,
        data TEXT,
        usuario_id INTEGER,
        FOREIGN KEY(usuario_id) REFERENCES usuarios(id)
    )""")
    
    # Tabela de Movimentações de Estoque
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS movimentacoes_estoque (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        produto_id INTEGER,
        tipo TEXT,
        quantidade INTEGER,
        data TEXT,
        motivo TEXT,
        usuario_id INTEGER,
        FOREIGN KEY(produto_id) REFERENCES produtos(id),
        FOREIGN KEY(usuario_id) REFERENCES usuarios(id)
    )""")
    
    # Insere usuário padrão caso não exista
    cursor.execute("SELECT COUNT(*) FROM usuarios")
    if cursor.fetchone()[0] == 0:
        import hashlib
        senha_padrao = hashlib.sha256("MasterTech2026".encode()).hexdigest()
        cursor.execute("INSERT INTO usuarios (usuario, senha_hash, nome) VALUES ('kelly', ?, 'Kelly')", (senha_padrao,))
        cursor.execute("INSERT INTO usuarios (usuario, senha_hash, nome) VALUES ('littiery', ?, 'Littiery')", (senha_padrao,))
    
    # Insere tipos padrão de aparelho caso a tabela esteja vazia
    cursor.execute("SELECT COUNT(*) FROM tipos_aparelho")
    if cursor.fetchone()[0] == 0:
        tipos_iniciais = ["Celular", "Notebook", "CPU", "Televisão", "Tablet", "Console/Videogame", "Outros"]
        for tipo in tipos_iniciais:
            cursor.execute("INSERT OR IGNORE INTO tipos_aparelho (nome) VALUES (?)", (tipo,))
            
    conn.commit()
    conn.close()