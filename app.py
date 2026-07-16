import streamlit as st
import pandas as pd
import sqlite3
import hashlib
import os
import re
from datetime import datetime
import pdf_generator

# Configuração da Página
st.set_page_config(page_title="Master Tech - Sistema de Gestão", layout="wide")

PASTA_PROJETO = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(PASTA_PROJETO, "mastertech.db")

def conectar():
    return sqlite3.connect(DB_PATH)

def inicializar_banco_seguro():
    conn = conectar()
    cursor = conn.cursor()
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS usuarios (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        usuario TEXT UNIQUE,
        senha_hash TEXT,
        nome TEXT
    )""")
    
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
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS tipos_aparelho (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT UNIQUE
    )""")
    
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
    
    try:
        cursor.execute("ALTER TABLE ordens_servico ADD COLUMN data_aprovacao TEXT")
    except sqlite3.OperationalError:
        pass  
    try:
        cursor.execute("ALTER TABLE ordens_servico ADD COLUMN data_pronto TEXT")
    except sqlite3.OperationalError:
        pass
    try:
        cursor.execute("ALTER TABLE ordens_servico ADD COLUMN data_retirada TEXT")
    except sqlite3.OperationalError:
        pass
    try:
        cursor.execute("ALTER TABLE ordens_servico ADD COLUMN garantia_tempo TEXT")
    except sqlite3.OperationalError:
        pass
    
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
    
    cursor.execute("SELECT COUNT(*) FROM usuarios")
    if cursor.fetchone()[0] == 0:
        senha_padrao = hashlib.sha256("MasterTech2026".encode()).hexdigest()
        cursor.execute("INSERT INTO usuarios (usuario, senha_hash, nome) VALUES ('kelly', ?, 'Kelly')", (senha_padrao,))
        cursor.execute("INSERT INTO usuarios (usuario, senha_hash, nome) VALUES ('littiery', ?, 'Littiery')", (senha_padrao,))
    
    cursor.execute("SELECT COUNT(*) FROM tipos_aparelho")
    if cursor.fetchone()[0] == 0:
        tipos_iniciais = ["Celular", "Notebook", "CPU", "Televisão", "Tablet", "Console/Videogame", "Outros"]
        for tipo in tipos_iniciais:
            cursor.execute("INSERT OR IGNORE INTO tipos_aparelho (nome) VALUES (?)", (tipo,))
            
    conn.commit()
    conn.close()

def garantir_colunas_extras():
    conn = conectar()
    cursor = conn.cursor()
    # Tenta adicionar as colunas uma a uma. Se já existirem, o erro é ignorado.
    try: cursor.execute("ALTER TABLE ordens_servico ADD COLUMN valor_pago REAL")
    except: pass
    try: cursor.execute("ALTER TABLE ordens_servico ADD COLUMN forma_pagamento_os TEXT")
    except: pass
    conn.commit()
    conn.close()

inicializar_banco_seguro()
garantir_colunas_extras()

def aplicar_mascara_telefone(tel_raw):
    numeros = re.sub(r"\D", "", tel_raw)
    numeros = numeros[:11]
    length = len(numeros)
    if length == 0:
        return ""
    elif length <= 2:
        return f"({numeros}"
    elif length <= 6:
        return f"({numeros[:2]}) {numeros[2:]}"
    elif length <= 10:
        return f"({numeros[:2]}) {numeros[2:6]}-{numeros[6:]}"
    else:
        return f"({numeros[:2]}) {numeros[2:7]}-{numeros[7:]}"

# Função inteligente para colocar as barras "/" automaticamente nas datas de forma imediata
def formatar_data_automatica(texto_data):
    if not texto_data:
        return ""
    apenas_numeros = re.sub(r"\D", "", texto_data)
    if len(apenas_numeros) == 8:
        return f"{apenas_numeros[:2]}/{apenas_numeros[2:4]}/{apenas_numeros[4:]}"
    elif len(apenas_numeros) == 6:
        ano_completo = f"20{apenas_numeros[4:]}"
        return f"{apenas_numeros[:2]}/{apenas_numeros[2:4]}/{ano_completo}"
    return texto_data

if 'logado' not in st.session_state:
    st.session_state.logado = False
    st.session_state.usuario_id = None
    st.session_state.usuario_nome = ""

if 'venda_concluida' not in st.session_state:
    st.session_state.venda_concluida = False
    st.session_state.dados_pdf_venda = None

if 'os_cadastrada' not in st.session_state:
    st.session_state.os_cadastrada = False
    st.session_state.dados_pdf_os = None

def tela_login():
    st.markdown("<h2 style='text-align: center;'>Master Tech Telecomunicações e Informática</h2>", unsafe_allow_html=True)
    st.markdown("<h4 style='text-align: center; color: gray;'>Controle de Estoque, Caixa e Ordens de Serviço</h4>", unsafe_allow_html=True)
    
    with st.form("login_form", clear_on_submit=True):
        st.write("### Acesso ao Sistema")
        user = st.text_input("Usuário (kelly ou littiery)").strip().lower()
        password = st.text_input("Senha", type="password")
        submetido = st.form_submit_button("Entrar")
        
        if submetido:
            conn = conectar()
            cursor = conn.cursor()
            hash_senha = hashlib.sha256(password.encode()).hexdigest()
            cursor.execute("SELECT id, nome FROM usuarios WHERE usuario = ? AND senha_hash = ?", (user, hash_senha))
            resultado = cursor.fetchone()
            conn.close()
            
            if resultado:
                st.session_state.logado = True
                st.session_state.usuario_id = resultado[0]
                st.session_state.usuario_nome = resultado[1]
                st.rerun()
            else:
                st.error("Usuário ou senha incorretos.")

if not st.session_state.logado:
    tela_login()
else:
    st.sidebar.title(f"Olá, {st.session_state.usuario_nome.split()[0]}!")
    opcao = st.sidebar.radio("Navegação", [
        "📊 Dashboard Geral", 
        "🛒 Frente de Caixa (Vendas)", 
        "🔧 Ordens de Serviço", 
        "📦 Controle de Estoque", 
        "💰 Fluxo de Caixa (Despesas)"
    ])
    
    if st.sidebar.button("Sair do Sistema"):
        st.session_state.logado = False
        st.session_state.usuario_id = None
        st.rerun()

    if opcao == "📊 Dashboard Geral":
        st.title("📊 Painel de Controle Master Tech")
        conn = conectar()
        vendas_totais = pd.read_sql_query("SELECT SUM(valor_total) FROM vendas", conn).iloc[0,0] or 0.0
        servicos_totais = pd.read_sql_query("SELECT SUM(valor_servico) FROM ordens_servico WHERE status = 'Entregue/Finalizado'", conn).iloc[0,0] or 0.0
        despesas_totais = pd.read_sql_query("SELECT SUM(valor) FROM despesas", conn).iloc[0,0] or 0.0
        faturamento = vendas_totais + servicos_totais
        saldo = faturamento - despesas_totais
        
        col1, col2, col3 = st.columns(3)
        col1.metric("Faturamento Bruto", f"R$ {faturamento:.2f}")
        col2.metric("Total de Despesas", f"R$ {despesas_totais:.2f}", delta_color="inverse")
        col3.metric("Saldo em Caixa", f"R$ {saldo:.2f}")
        
        st.subheader("⚠️ Alertas de Estoque Baixo")
        df_produtos = pd.read_sql_query("SELECT nome, categoria, quantidade_atual, estoque_minimo FROM produtos WHERE quantidade_atual <= estoque_minimo", conn)
        if not df_produtos.empty:
            st.dataframe(df_produtos, use_container_width=True)
        else:
            st.success("Todos os produtos estão com níveis de estoque seguros!")
            
        st.subheader("🔧 Resumo das Ordens de Serviço")
        df_os_resumo = pd.read_sql_query("SELECT status, COUNT(*) as Total FROM ordens_servico GROUP BY status", conn)
        st.bar_chart(df_os_resumo.set_index('status'))
        conn.close()

    elif opcao == "🛒 Frente de Caixa (Vendas)":
        st.title("🛒 Frente de Caixa")
        conn = conectar()
        produtos_df = pd.read_sql_query("SELECT id, nome, preco_venda, quantidade_atual FROM produtos", conn)
        
        if produtos_df.empty:
            st.warning("Nenhum produto cadastrado no estoque ainda.")
        else:
            lista_produtos = {row['nome']: row for _, row in produtos_df.iterrows()}
            with st.form("venda_form"):
                produto_selecionado = st.selectbox("Selecione o Produto", list(lista_produtos.keys()))
                qtd_venda = st.number_input("Quantidade", min_value=1, step=1)
                forma_pgto = st.selectbox("Forma de Pagamento", ["Dinheiro", "Pix", "Cartão de Crédito", "Cartão de Débito"])
                prod_info = lista_produtos[produto_selecionado]
                valor_total_venda = prod_info['preco_venda'] * qtd_venda
                st.write(f"**Valor Unitário:** R$ {prod_info['preco_venda']:.2f} | **Total:** R$ {valor_total_venda:.2f}")
                botao_venda = st.form_submit_button("Concluir Venda")
                
                if botao_venda:
                    if qtd_venda > prod_info['quantidade_atual']:
                        st.error(f"Estoque insuficiente! Apenas {prod_info['quantidade_atual']} unidades disponíveis.")
                    else:
                        cursor = conn.cursor()
                        data_atual = datetime.now().strftime("%d/%m/%Y %H:%M")
                        cursor.execute("INSERT INTO vendas (produto_id, quantidade, valor_total, forma_pagamento, data, usuario_id) VALUES (?, ?, ?, ?, ?, ?)",
                                       (prod_info['id'], qtd_venda, valor_total_venda, forma_pgto, data_atual, st.session_state.usuario_id))
                        venda_id = cursor.lastrowid
                        nova_qtd = prod_info['quantidade_atual'] - qtd_venda
                        cursor.execute("UPDATE produtos SET quantidade_atual = ? WHERE id = ?", (nova_qtd, prod_info['id']))
                        cursor.execute("INSERT INTO movimentacoes_estoque (produto_id, tipo, quantidade, data, motivo, usuario_id) VALUES (?, 'Saída', ?, ?, ?, ?)",
                                       (prod_info['id'], qtd_venda, data_atual, f"Venda ID {venda_id}", st.session_state.usuario_id))
                        conn.commit()
                        st.session_state.venda_concluida = True
                        st.session_state.dados_pdf_venda = {
                            "venda_id": venda_id, "produto": produto_selecionado, "qtd": qtd_venda, "total": valor_total_venda, "pagamento": forma_pgto
                        }
            
            if st.session_state.venda_concluida:
                v = st.session_state.dados_pdf_venda
                st.success(f"🎉 Venda realizada com sucesso!")
                pdf_bytes_venda = bytes(pdf_generator.gerar_pdf_recibo(v['venda_id'], v['produto'], v['qtd'], v['total'], v['pagamento']))
                st.download_button("📥 Imprimir Recibo (PDF)", data=pdf_bytes_venda, file_name=f"recibo_venda_{v['venda_id']}.pdf", mime="application/pdf")
                if st.button("Nova Venda (Limpar)"):
                    st.session_state.venda_concluida = False
                    st.session_state.dados_pdf_venda = None
                    st.rerun()
        conn.close()

    elif opcao == "🔧 Ordens de Serviço":
        st.title("🔧 Gerenciamento de Ordens de Serviço (O.S.)")
        tab1, tab2 = st.tabs(["Nova O.S.", "Gerenciar O.S. Existentes"])
        
        with tab1:
            st.write("### Abrir Nova Ordem de Serviço")
            tel_digitado = st.text_input("Telefone do Cliente", value=st.session_state.get('temp_tel', ''), help="Ex: 62985703663")
            tel_formatado = aplicar_mascara_telefone(tel_digitado)
            if tel_formatado != tel_digitado:
                st.session_state['temp_tel'] = tel_formatado
                st.rerun()
                
            with st.form("nova_os_form"):
                cliente = st.text_input("Nome do Cliente")
                conn = conectar()
                df_tipos = pd.read_sql_query("SELECT nome FROM tipos_aparelho ORDER BY nome ASC", conn)
                conn.close()
                lista_tipos = list(df_tipos['nome'])
                lista_tipos.append("➕ Cadastrar Novo Tipo...")
                tipo_aparelho_sel = st.selectbox("Tipo de Aparelho", lista_tipos)
                novo_tipo_aparelho = ""
                if tipo_aparelho_sel == "➕ Cadastrar Novo Tipo...":
                    novo_tipo_aparelho = st.text_input("Escreva o Nome do Novo Tipo de Aparelho (Ex: Caixa de Som)")
                marca_modelo = st.text_input("Marca / Modelo")
                num_serie = st.text_input("Número de Série / IMEI")
                estado_fisico = st.text_area("Estado Físico do Aparelho")
                defeito_relatado = st.text_area("Defeito Relatado pelo Cliente")
                valor_est = st.number_input("Valor Estimado do Serviço (R$)", min_value=0.0, step=10.0, format="%.2f")
                salvar_os = st.form_submit_button("Salvar e Gerar O.S.")
                
                if salvar_os:
                    conn = conectar()
                    cursor = conn.cursor()
                    tipo_final = tipo_aparelho_sel
                    if tipo_aparelho_sel == "➕ Cadastrar Novo Tipo..." and novo_tipo_aparelho.strip() != "":
                        tipo_final = novo_tipo_aparelho.strip()
                        cursor.execute("INSERT OR IGNORE INTO tipos_aparelho (nome) VALUES (?)", (tipo_final,))
                        conn.commit()
                    
                    data_in = datetime.now().strftime("%d/%m/%Y")
                    cursor.execute("""
                        INSERT INTO ordens_servico (nome_cliente, telefone_cliente, tipo_aparelho, marca_modelo, numero_serie, estado_fisico, defeito_relatado, valor_servico, status, data_entrada, usuario_id, garantia_tempo) 
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'Aberto', ?, ?, '90 dias')""",
                        (cliente, tel_formatado, tipo_final, marca_modelo, num_serie, estado_fisico, defeito_relatado, valor_est, data_in, st.session_state.usuario_id))
                    os_id = cursor.lastrowid
                    conn.commit()
                    conn.close()
                    
                    st.session_state.os_cadastrada = True
                    st.session_state.dados_pdf_os = {
                        "os_id": os_id, "cliente": cliente, "telefone": tel_formatado, 
                        "tipo": tipo_final, "modelo": marca_modelo, "serie": num_serie, 
                        "estado": estado_fisico, "defeito": defeito_relatado, "valor": valor_est, 
                        "data": data_in
                    }

            if st.session_state.os_cadastrada:
                d = st.session_state.dados_pdf_os
                st.success(f"🎉 Ordem de Serviço Nº {d['os_id']} cadastrada com sucesso!")
                pdf_bytes_os = bytes(pdf_generator.gerar_pdf_os(
                    os_id=d['os_id'], cliente=d['cliente'], telefone=d['telefone'], tipo=d['tipo'],
                    modelo=d['modelo'], serie=d['serie'], estado=d['estado'], defeito=d['defeito'],
                    valor=d['valor'], status="Aberto", data_entrada=d['data']
                ))
                st.download_button(label="📥 Imprimir Duas Vias da O.S. (PDF)", data=pdf_bytes_os, file_name=f"OS_{d['os_id']}.pdf", mime="application/pdf")
                if st.button("Abrir Nova O.S. (Limpar)"):
                    st.session_state.os_cadastrada = False
                    st.session_state.dados_pdf_os = None
                    st.session_state['temp_tel'] = ''
                    st.rerun()
        
        with tab2:
            st.write("### Buscar e Atualizar O.S.")
            conn = conectar()
            df_os = pd.read_sql_query("SELECT id, nome_cliente, tipo_aparelho, status, valor_servico FROM ordens_servico", conn)
            st.dataframe(df_os, use_container_width=True)
            
            os_selecionada = st.number_input("Digite o número da O.S. que deseja editar/imprimir", min_value=1, step=1)
            
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, nome_cliente, telefone_cliente, tipo_aparelho, marca_modelo, 
                       numero_serie, estado_fisico, defeito_relatado, defeito_constatado, 
                       pecas_usadas, valor_servico, status, data_entrada, data_saida, 
                       usuario_id, data_aprovacao, data_pronto, data_retirada, garantia_tempo 
                FROM ordens_servico WHERE id = ?
            """, (os_selecionada,))
            dados_os = cursor.fetchone()
            
            if dados_os:
                st.write(f"**Cliente:** {dados_os[1]} | **Aparelho:** {dados_os[3]} ({dados_os[4]})")
                
                # Campos Normais de Edição
                novo_status = st.selectbox("Alterar Status Manualmente", ["Aberto", "Em Análise", "Aguardando Peça", "Pronto", "Entregue/Finalizado"], index=["Aberto", "Em Análise", "Aguardando Peça", "Pronto", "Entregue/Finalizado"].index(dados_os[11]))
                def_constatado = st.text_area("Defeito Constatado / Solucionado", value=dados_os[8] or "")
                pecas = st.text_input("Peças Usadas", value=dados_os[9] or "")
                valor_fin = st.number_input("Valor Final do Serviço (R$)", value=dados_os[10] or 0.0)
                
                # Novos campos de controle de datas e garantia dinâmicos com formatação imediata ao pressionar Enter
                st.write("---")
                st.write("📅 **Controle de Datas Interno (Digite os números e dê Enter para autoformatar com as barras `/`)**")
                
                col_d1, col_d2, col_d3 = st.columns(3)
                
                # Inicializa no session_state para manter o controle em tempo real dos valores modificados e formatados
                k_aprov = f"da_{os_selecionada}"
                k_pronto = f"dp_{os_selecionada}"
                k_retirada = f"dr_{os_selecionada}"
                
                if k_aprov not in st.session_state:
                    st.session_state[k_aprov] = dados_os[15] or ""
                if k_pronto not in st.session_state:
                    st.session_state[k_pronto] = dados_os[16] or ""
                if k_retirada not in st.session_state:
                    st.session_state[k_retirada] = dados_os[17] or ""
                
                with col_d1:
                    raw_aprov = st.text_input("Data de Aprovação do Serviço", value=st.session_state[k_aprov], placeholder="Ex: 15072026")
                    formatted_aprov = formatar_data_automatica(raw_aprov)
                    if formatted_aprov != raw_aprov:
                        st.session_state[k_aprov] = formatted_aprov
                        st.rerun()
                        
                with col_d2:
                    raw_pronto = st.text_input("Data que o Serviço Ficou Pronto", value=st.session_state[k_pronto], placeholder="Ex: 15072026")
                    formatted_pronto = formatar_data_automatica(raw_pronto)
                    if formatted_pronto != raw_pronto:
                        st.session_state[k_pronto] = formatted_pronto
                        st.rerun()
                        
                with col_d3:
                    raw_retirada = st.text_input("Data de Retirada do Aparelho", value=st.session_state[k_retirada], placeholder="Ex: 15072026")
                    formatted_retirada = formatar_data_automatica(raw_retirada)
                    if formatted_retirada != raw_retirada:
                        st.session_state[k_retirada] = formatted_retirada
                        st.rerun()
                
                # Campo para o tempo de garantia
                garantia_tempo = st.text_input("Tempo de Garantia", value=dados_os[18] or "90 dias", help="Ex: 90 dias, 30 dias, 6 meses")

                valor_pago = st.number_input("Valor Pago pelo Cliente (R$)", min_value=0.0, value=float(dados_os[19] if len(dados_os) > 19 and dados_os[19] is not None else 0.0))

                opcoes_pagamento = ["Dinheiro", "Pix", "Cartão", "Não Informado"]
                valor_atual_pgto = dados_os[20] if len(dados_os) > 20 and dados_os[20] in opcoes_pagamento else "Não Informado"
                forma_pagamento_os = st.selectbox("Forma de Pagamento", opcoes_pagamento, index=opcoes_pagamento.index(valor_atual_pgto))

                st.write("---")

                if st.button("Atualizar Dados da O.S."):
                        data_aprov = st.session_state[k_aprov]
                        data_pronto = st.session_state[k_pronto]
                        data_retirada = st.session_state[k_retirada]
                        
                        status_final = novo_status 
                        
                        if data_retirada.strip() != "":
                            status_final = "Entregue/Finalizado"
                        elif data_pronto.strip() != "":
                            status_final = "Pronto"
                        elif data_aprov.strip() != "" and status_final == "Aberto":
                            status_final = "Em Análise"
                            
                        data_out = datetime.now().strftime("%d/%m/%Y") if status_final == "Entregue/Finalizado" else dados_os[13]
                        
                        cursor.execute("""
                            UPDATE ordens_servico 
                            SET status = ?, defeito_constatado = ?, pecas_usadas = ?, valor_servico = ?, data_saida = ?,
                                data_aprovacao = ?, data_pronto = ?, data_retirada = ?, garantia_tempo = ?,
                                valor_pago = ?, forma_pagamento_os = ?
                            WHERE id = ?""", 
                            (status_final, def_constatado, pecas, valor_fin, data_out, data_aprov, data_pronto, data_retirada, garantia_tempo, valor_pago, forma_pagamento_os, os_selecionada))
                        
                        conn.commit()
                        st.success(f"Ordem de serviço atualizada! Status: **{status_final}**")
                        st.rerun()
                
                # Colunas para downloads de documentos
                st.write("### 🖨️ Documentos para Impressão")
                col_btn1, col_btn2 = st.columns(2)
                
                data_aprov_print = st.session_state[k_aprov]
                data_pronto_print = st.session_state[k_pronto]
                data_retirada_print = st.session_state[k_retirada]
                
                with col_btn1:
                    pdf_reimpressao = bytes(pdf_generator.gerar_pdf_os(
                        os_id=dados_os[0], cliente=dados_os[1], telefone=dados_os[2], tipo=dados_os[3],
                        modelo=dados_os[4], serie=dados_os[5], estado=dados_os[6], defeito=dados_os[7],
                        valor=valor_fin, status=dados_os[11], data_entrada=dados_os[12],
                        data_aprovacao=data_aprov_print, data_pronto=data_pronto_print, data_retirada=data_retirada_print
                    ))
                    st.download_button("🖨️ Reimprimir Ficha de O.S. (Duas Vias)", data=pdf_reimpressao, file_name=f"OS_{os_selecionada}_reimpressa.pdf")
                
                if dados_os[11] == "Entregue/Finalizado" or data_retirada_print.strip() != "":
                    with col_btn2:
                        data_ent_doc = data_retirada_print if data_retirada_print.strip() != "" else datetime.now().strftime("%d/%m/%Y")
                        
                        pdf_recibo_garantia = bytes(pdf_generator.gerar_pdf_recibo_entrega(
                            os_id=dados_os[0], cliente=dados_os[1], telefone=dados_os[2], tipo=dados_os[3],
                            modelo=dados_os[4], serie=dados_os[5], defeito_constatado=def_constatado,
                            pecas_usadas=pecas, valor=valor_fin, data_entrega=data_ent_doc, 
                            garantia=garantia_tempo, forma_pagamento=forma_pagamento_os
                        ))
                        st.download_button("📥 Imprimir Recibo de Entrega e Garantia (PDF)", data=pdf_recibo_garantia, file_name=f"recibo_entrega_OS_{os_selecionada}.pdf", type="primary")
            else:
                st.info("Digite um número de O.S. válido acima para gerenciar.")
            conn.close()

    elif opcao == "📦 Controle de Estoque":
        st.title("📦 Controle de Estoque")
        tab_cad, tab_lista = st.tabs(["Cadastrar / Abastecer", "Lista de Produtos"])
        with tab_cad:
            with st.form("prod_form"):
                st.write("### Cadastrar Novo Produto")
                nome_prod = st.text_input("Nome do Produto")
                cat_prod = st.selectbox("Categoria", ["Celulares", "Acessórios de Celular", "Informática", "Controles Remotos", "Capas", "Carregadores", "Outros Eletrônicos"])
                qtd_inicial = st.number_input("Quantidade Inicial", min_value=0, step=1)
                custo_prod = st.number_input("Preço de Custo (R$)", min_value=0.0, step=0.50)
                venda_prod = st.number_input("Preço de Venda (R$)", min_value=0.0, step=0.50)
                min_prod = st.number_input("Estoque Mínimo de Alerta", min_value=0, step=1)
                salvar_prod = st.form_submit_button("Cadastrar Produto")
                if salvar_prod and nome_prod:
                    conn = conectar()
                    cursor = conn.cursor()
                    cursor.execute("INSERT INTO produtos (nome, categoria, quantidade_atual, preco_custo, preco_venda, estoque_minimo) VALUES (?, ?, ?, ?, ?, ?)",
                                   (nome_prod, cat_prod, qtd_inicial, custo_prod, venda_prod, min_prod))
                    conn.commit()
                    conn.close()
                    st.success(f"Produto '{nome_prod}' adicionado com sucesso!")
        
        with tab_lista:
            conn = conectar()
            df_estoque = pd.read_sql_query("SELECT id, nome, categoria, quantidade_atual, preco_venda, estoque_minimo FROM produtos", conn)
            st.dataframe(df_estoque, use_container_width=True)
            conn.close()

    elif opcao == "💰 Fluxo de Caixa (Despesas)":
        st.title("💰 Lançamento de Despesas da Loja")
        with st.form("despesa_form"):
            desc_desp = st.text_input("Descrição da Despesa (Ex: Conta de Luz, Fornecedor X)")
            cat_desp = st.selectbox("Categoria", ["Aluguel", "Luz", "Internet", "Fornecedores", "Impostos", "Outros"])
            valor_desp = st.number_input("Valor Pago (R$)", min_value=0.0, step=5.0)
            salvar_desp = st.form_submit_button("Lançar Despesa")
            if salvar_desp and desc_desp:
                conn = conectar()
                cursor = conn.cursor()
                data_atual = datetime.now().strftime("%d/%m/%Y")
                cursor.execute("INSERT INTO despesas (descricao, categoria, valor, data, usuario_id) VALUES (?, ?, ?, ?, ?)",
                               (desc_desp, cat_desp, valor_desp, data_atual, st.session_state.usuario_id))
                conn.commit()
                conn.close()
                st.success("Despesa registrada com sucesso!")