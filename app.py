# app.py - Versão completa com coluna de servidores
import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime, date
import plotly.express as px

# Configuração da página
st.set_page_config(
    page_title="Sistema de Controle de Ordens de Serviço - INCRA",
    page_icon="📋",
    layout="wide"
)

# Título do aplicativo
st.title("📋 Sistema de Controle de Ordens de Serviço")
st.markdown("---")

# ==================== CONFIGURAÇÃO DO BANCO DE DADOS ====================
def init_database():
    """Inicializa o banco de dados SQLite"""
    conn = sqlite3.connect('ordens_servico.db')
    cursor = conn.cursor()
    
    # Verificar se a coluna servidores existe, se não, adicionar
    cursor.execute("PRAGMA table_info(ordens_servico)")
    columns = [col[1] for col in cursor.fetchall()]
    
    if 'servidores' not in columns:
        cursor.execute("ALTER TABLE ordens_servico ADD COLUMN servidores TEXT")
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS ordens_servico (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sei_numero TEXT UNIQUE NOT NULL,
            processo TEXT NOT NULL,
            comunidade TEXT NOT NULL,
            municipio TEXT,
            data_publicacao DATE NOT NULL,
            prazo_dias INTEGER NOT NULL,
            data_termino DATE,
            tipo_acao TEXT NOT NULL,
            situacao TEXT DEFAULT 'Vigente',
            observacao TEXT,
            servidores TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.commit()
    conn.close()

def carregar_dados():
    """Carrega todos os dados do banco"""
    try:
        conn = sqlite3.connect('ordens_servico.db')
        df = pd.read_sql_query("SELECT * FROM ordens_servico ORDER BY data_termino", conn)
        conn.close()
        
        if not df.empty:
            # Converter colunas para tipos corretos
            df['prazo_dias'] = pd.to_numeric(df['prazo_dias'], errors='coerce').fillna(0).astype(int)
            df['sei_numero'] = df['sei_numero'].astype(str)
            df['processo'] = df['processo'].astype(str)
            df['comunidade'] = df['comunidade'].astype(str)
            df['tipo_acao'] = df['tipo_acao'].astype(str)
            df['situacao'] = df['situacao'].astype(str)
            df['servidores'] = df['servidores'].fillna('').astype(str)
            
            # Converter datas
            df['data_publicacao'] = pd.to_datetime(df['data_publicacao'], errors='coerce')
            df['data_termino'] = pd.to_datetime(df['data_termino'], errors='coerce')
            
            # Calcular dias restantes
            hoje = date.today()
            
            def calc_dias_restantes(row):
                if row['situacao'] == 'Vigente' and pd.notna(row['data_termino']):
                    try:
                        return (row['data_termino'].date() - hoje).days
                    except:
                        return 0
                return 0
            
            df['dias_restantes'] = df.apply(calc_dias_restantes, axis=1)
        
        return df
    except Exception as e:
        st.error(f"Erro ao carregar dados: {e}")
        return pd.DataFrame()

def inserir_ordem(sei_numero, processo, comunidade, municipio, data_publicacao, prazo_dias, tipo_acao, situacao, observacao, servidores):
    """Insere uma nova ordem de serviço"""
    try:
        conn = sqlite3.connect('ordens_servico.db')
        cursor = conn.cursor()
        
        # Calcular data de término
        data_pub = datetime.strptime(data_publicacao, '%Y-%m-%d').date()
        prazo_int = int(prazo_dias)
        
        # Se prazo for 0 ou negativo, não calcular data de término
        if prazo_int > 0:
            data_termino = data_pub + pd.Timedelta(days=prazo_int)
        else:
            data_termino = None
        
        # Verificar situação com base na data
        hoje = date.today()
        if data_termino and data_termino < hoje:
            situacao = 'Vencida'
        
        cursor.execute('''
            INSERT INTO ordens_servico 
            (sei_numero, processo, comunidade, municipio, data_publicacao, prazo_dias, 
             data_termino, tipo_acao, situacao, observacao, servidores)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (str(sei_numero), str(processo), str(comunidade), str(municipio) if municipio else None, 
              data_publicacao, prazo_int, data_termino, str(tipo_acao), str(situacao), 
              str(observacao) if observacao else None, str(servidores) if servidores else None))
        
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        st.error(f"Erro ao inserir ordem: {e}")
        return False

def atualizar_ordem(id, sei_numero, processo, comunidade, municipio, data_publicacao, prazo_dias, tipo_acao, situacao, observacao, servidores):
    """Atualiza uma ordem de serviço existente"""
    try:
        conn = sqlite3.connect('ordens_servico.db')
        cursor = conn.cursor()
        
        # Recalcular data de término
        data_pub = datetime.strptime(data_publicacao, '%Y-%m-%d').date()
        prazo_int = int(prazo_dias)
        
        # Se prazo for 0 ou negativo, não calcular data de término
        if prazo_int > 0:
            data_termino = data_pub + pd.Timedelta(days=prazo_int)
        else:
            data_termino = None
        
        # Verificar situação com base na data
        hoje = date.today()
        if data_termino and data_termino < hoje and situacao == 'Vigente':
            situacao = 'Vencida'
        
        cursor.execute('''
            UPDATE ordens_servico 
            SET sei_numero=?, processo=?, comunidade=?, municipio=?, data_publicacao=?, 
                prazo_dias=?, data_termino=?, tipo_acao=?, situacao=?, observacao=?, 
                servidores=?, updated_at=CURRENT_TIMESTAMP
            WHERE id=?
        ''', (str(sei_numero), str(processo), str(comunidade), str(municipio) if municipio else None, 
              data_publicacao, prazo_int, data_termino, str(tipo_acao), str(situacao), 
              str(observacao) if observacao else None, str(servidores) if servidores else None, int(id)))
        
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        st.error(f"Erro ao atualizar ordem: {e}")
        return False

def excluir_ordem(id):
    """Exclui uma ordem de serviço"""
    try:
        conn = sqlite3.connect('ordens_servico.db')
        cursor = conn.cursor()
        cursor.execute("DELETE FROM ordens_servico WHERE id=?", (int(id),))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        st.error(f"Erro ao excluir ordem: {e}")
        return False

def atualizar_situacoes():
    """Atualiza automaticamente as situações com base nas datas"""
    try:
        conn = sqlite3.connect('ordens_servico.db')
        cursor = conn.cursor()
        hoje = date.today()
        
        cursor.execute('''
            UPDATE ordens_servico 
            SET situacao = 'Vencida' 
            WHERE data_termino < ? AND situacao = 'Vigente' AND data_termino IS NOT NULL
        ''', (hoje,))
        
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        st.error(f"Erro ao atualizar situações: {e}")
        return False

# ==================== INTERFACE PRINCIPAL ====================

# Inicializar banco de dados
init_database()
atualizar_situacoes()

# Sidebar para navegação
st.sidebar.title("📌 Navegação")
menu = st.sidebar.radio(
    "Escolha uma opção:",
    ["📊 Dashboard", "📋 Listar Ordens", "➕ Cadastrar Ordem", "✏️ Alterar Ordem", "🗑️ Excluir Ordem"]
)

# Carregar dados
df = carregar_dados()

# ==================== DASHBOARD ====================
if menu == "📊 Dashboard":
    st.header("📊 Dashboard de Controle de Prazos")
    
    # Cards com métricas
    total_ordens = len(df) if not df.empty else 0
    vigentes = len(df[df['situacao'] == 'Vigente']) if not df.empty else 0
    vencidas = len(df[df['situacao'] == 'Vencida']) if not df.empty else 0
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total de Ordens", total_ordens)
    
    with col2:
        st.metric("Ordens Vigentes", vigentes)
    
    with col3:
        st.metric("Ordens Vencidas", vencidas)
    
    with col4:
        if not df.empty and vigentes > 0:
            df_vigentes = df[df['situacao'] == 'Vigente']
            if not df_vigentes.empty and pd.notna(df_vigentes['data_termino'].min()):
                proximo_vencimento = pd.to_datetime(df_vigentes['data_termino'].min()).date()
                dias_restantes = (proximo_vencimento - date.today()).days
                st.metric("Próximo Vencimento", proximo_vencimento.strftime('%d/%m/%Y'), delta=f"{dias_restantes} dias")
            else:
                st.metric("Próximo Vencimento", "N/A")
        else:
            st.metric("Próximo Vencimento", "N/A")
    
    st.markdown("---")
    
    # Gráficos
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📊 Distribuição por Situação")
        if not df.empty:
            situacao_counts = df['situacao'].value_counts()
            fig = px.pie(values=situacao_counts.values, names=situacao_counts.index, title="Situação das OS")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Nenhuma ordem cadastrada")
    
    with col2:
        st.subheader("📊 Distribuição por Tipo de Ação")
        if not df.empty:
            tipo_counts = df['tipo_acao'].value_counts().head(5)
            fig = px.bar(x=tipo_counts.index, y=tipo_counts.values, title="Top 5 Tipos de Ação")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Nenhuma ordem cadastrada")
    
    st.markdown("---")
    
    # Gráfico de prazos
    st.subheader("📅 Prazos por Comunidade")
    if not df.empty and vigentes > 0:
        df_vigentes = df[df['situacao'] == 'Vigente'].copy()
        if not df_vigentes.empty:
            df_vigentes['dias_restantes'] = df_vigentes.apply(
                lambda row: (row['data_termino'].date() - date.today()).days 
                if pd.notna(row['data_termino']) else 999,
                axis=1
            )
            df_vigentes = df_vigentes.sort_values('dias_restantes').head(10)
            
            fig = px.bar(
                df_vigentes, 
                x='dias_restantes', 
                y='comunidade',
                orientation='h',
                color='dias_restantes',
                color_continuous_scale=['green', 'yellow', 'red'],
                title="Ordens Vigentes - Dias Restantes"
            )
            st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Nenhuma ordem vigente para exibir")

# ==================== LISTAR ORDENS ====================
elif menu == "📋 Listar Ordens":
    st.header("📋 Lista de Ordens de Serviço")
    
    if df.empty:
        st.info("Nenhuma ordem cadastrada no sistema")
    else:
        # Filtros
        col1, col2, col3 = st.columns(3)
        
        with col1:
            filtro_situacao = st.selectbox("Filtrar por situação:", ["Todas", "Vigente", "Vencida"])
        
        with col2:
            comunidades = ["Todas"] + sorted(df['comunidade'].unique().tolist())
            filtro_comunidade = st.selectbox("Filtrar por comunidade:", comunidades)
        
        with col3:
            tipos = ["Todas"] + sorted(df['tipo_acao'].unique().tolist())
            filtro_tipo = st.selectbox("Filtrar por tipo de ação:", tipos)
        
        # Aplicar filtros
        df_filtrado = df.copy()
        
        if filtro_situacao != "Todas":
            df_filtrado = df_filtrado[df_filtrado['situacao'] == filtro_situacao]
        
        if filtro_comunidade != "Todas":
            df_filtrado = df_filtrado[df_filtrado['comunidade'] == filtro_comunidade]
        
        if filtro_tipo != "Todas":
            df_filtrado = df_filtrado[df_filtrado['tipo_acao'] == filtro_tipo]
        
        st.markdown(f"**Total de registros:** {len(df_filtrado)}")
        
        # Controle de quantidade de linhas
        col_linhas, col_export = st.columns([1, 3])
        with col_linhas:
            linhas_por_pagina = st.selectbox(
                "Linhas por página:", 
                [10, 20, 50, 100, 200, "Todos"],
                index=1  # índice 1 = 20 linhas (padrão)
            )
        
        # Exibir tabela com cores
        if not df_filtrado.empty:
            # Preparar dados para exibição - incluindo servidores
            colunas_exibir = ['id', 'sei_numero', 'processo', 'comunidade', 'municipio', 
                              'data_publicacao', 'prazo_dias', 'data_termino', 
                              'tipo_acao', 'situacao', 'dias_restantes', 'servidores']
            
            df_exibir = df_filtrado[colunas_exibir].copy()
            
            # Formatar colunas
            df_exibir['data_publicacao'] = pd.to_datetime(df_exibir['data_publicacao']).dt.strftime('%d/%m/%Y')
            df_exibir['data_termino'] = pd.to_datetime(df_exibir['data_termino']).dt.strftime('%d/%m/%Y') if 'data_termino' in df_exibir.columns else ''
            df_exibir['dias_restantes'] = df_exibir['dias_restantes'].fillna(0).astype(int)
            df_exibir['servidores'] = df_exibir['servidores'].fillna('').astype(str)
            
            # Aplicar limite de linhas
            if linhas_por_pagina != "Todos":
                df_exibir = df_exibir.head(int(linhas_por_pagina))
                st.caption(f"📄 Exibindo as primeiras {linhas_por_pagina} linhas. Total de {len(df_filtrado)} registros filtrados.")
            else:
                st.caption(f"📄 Exibindo todos os {len(df_filtrado)} registros.")
            
            # Função para colorir as linhas
            def highlight_rows(row):
                if row['situacao'] == 'Vencida':
                    return ['background-color: #f8d7da; color: #721c24'] * len(row)
                elif row['situacao'] == 'Vigente':
                    if row['dias_restantes'] <= 15:
                        return ['background-color: #fff3cd; color: #856404'] * len(row)
                    else:
                        return ['background-color: #d4edda; color: #155724'] * len(row)
                return [''] * len(row)
            
            # Aplicar estilo e exibir
            styled_df = df_exibir.style.apply(highlight_rows, axis=1)
            st.dataframe(styled_df, use_container_width=True, hide_index=True, height=600)
            
            # Legenda de cores
            st.markdown("---")
            st.markdown("**🎨 Legenda de Cores:**")
            col_leg1, col_leg2, col_leg3 = st.columns(3)
            with col_leg1:
                st.markdown('<span style="background-color: #d4edda; color: #155724; padding: 4px 8px; border-radius: 4px;">🟢 Vigente (mais de 15 dias)</span>', unsafe_allow_html=True)
            with col_leg2:
                st.markdown('<span style="background-color: #fff3cd; color: #856404; padding: 4px 8px; border-radius: 4px;">🟡 Vigente (até 15 dias - Atenção!)</span>', unsafe_allow_html=True)
            with col_leg3:
                st.markdown('<span style="background-color: #f8d7da; color: #721c24; padding: 4px 8px; border-radius: 4px;">🔴 Vencida</span>', unsafe_allow_html=True)
            
            # Botão para exportar
            st.markdown("---")
            csv = df_filtrado.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Exportar para CSV",
                data=csv,
                file_name=f"ordens_servico_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv"
            )
        else:
            st.info("Nenhuma ordem encontrada com os filtros selecionados")

# ==================== CADASTRAR ORDEM ====================
elif menu == "➕ Cadastrar Ordem":
    st.header("➕ Cadastrar Nova Ordem de Serviço")
    
    with st.form("cadastro_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            sei_numero = st.text_input("Nº SEI *", help="Ex: 26010277")
            processo = st.text_input("Nº do Processo *", help="Ex: 01089.000282/2017-31")
            comunidade = st.text_input("Comunidade *")
            municipio = st.text_input("Município")
        
        with col2:
            data_publicacao = st.date_input("Data de Publicação *", value=date.today())
            prazo_dias = st.number_input("Prazo (dias) *", min_value=0, max_value=720, value=120, 
                                          help="Use 0 para ordens sem prazo definido (ex: convalidação de atos)")
            tipo_acao = st.selectbox("Tipo de Ação *", [
                "Elaboração de RTID",
                "Vistoria e avaliação",
                "Inclusão de servidor",
                "Regularização ocupacional",
                "Convalidação de atos"
            ])
        
        situacao = st.selectbox("Situação", ["Vigente", "Vencida"])
        servidores = st.text_area("Servidores Responsáveis", height=100, 
                                   help="Liste os servidores designados, separados por vírgula")
        observacao = st.text_area("Observação", height=100)
        
        submitted = st.form_submit_button("✅ Cadastrar", use_container_width=True)
        
        if submitted:
            if not sei_numero or not processo or not comunidade or not tipo_acao:
                st.error("Preencha todos os campos obrigatórios (*)")
            else:
                sucesso = inserir_ordem(
                    sei_numero, processo, comunidade, municipio, 
                    data_publicacao.strftime('%Y-%m-%d'), prazo_dias, 
                    tipo_acao, situacao, observacao, servidores
                )
                if sucesso:
                    st.success(f"Ordem {sei_numero} cadastrada com sucesso!")
                    st.balloons()
                    st.rerun()

# ==================== ALTERAR ORDEM ====================
elif menu == "✏️ Alterar Ordem":
    st.header("✏️ Alterar Ordem de Serviço")
    
    if df.empty:
        st.warning("Nenhuma ordem cadastrada para alterar")
    else:
        # Selecionar ordem
        ordem_selecionada = st.selectbox(
            "Selecione a ordem para alterar:",
            options=df['id'].tolist(),
            format_func=lambda x: f"{x} - {df[df['id']==x]['sei_numero'].iloc[0]} - {df[df['id']==x]['comunidade'].iloc[0]}"
        )
        
        if ordem_selecionada:
            ordem = df[df['id'] == ordem_selecionada].iloc[0]
            
            with st.form("alteracao_form"):
                col1, col2 = st.columns(2)
                
                with col1:
                    sei_numero = st.text_input("Nº SEI *", value=str(ordem['sei_numero']))
                    processo = st.text_input("Nº do Processo *", value=str(ordem['processo']))
                    comunidade = st.text_input("Comunidade *", value=str(ordem['comunidade']))
                    municipio = st.text_input("Município", value=str(ordem['municipio']) if pd.notna(ordem['municipio']) else "")
                
                with col2:
                    data_publicacao = st.date_input("Data de Publicação *", 
                                                     value=pd.to_datetime(ordem['data_publicacao']).date())
                    prazo_dias = st.number_input("Prazo (dias) *", min_value=0, max_value=720, 
                                                  value=int(ordem['prazo_dias']),
                                                  help="Use 0 para ordens sem prazo definido")
                    tipo_acao = st.selectbox("Tipo de Ação *", [
                        "Elaboração de RTID",
                        "Vistoria e avaliação",
                        "Inclusão de servidor",
                        "Regularização ocupacional",
                        "Convalidação de atos"
                    ], index=["Elaboração de RTID", "Vistoria e avaliação", "Inclusão de servidor", 
                               "Regularização ocupacional", "Convalidação de atos"].index(ordem['tipo_acao']))
                
                situacao = st.selectbox("Situação", ["Vigente", "Vencida"], 
                                        index=0 if ordem['situacao'] == 'Vigente' else 1)
                servidores = st.text_area("Servidores Responsáveis", 
                                          value=str(ordem['servidores']) if pd.notna(ordem['servidores']) else "", 
                                          height=100,
                                          help="Liste os servidores designados, separados por vírgula")
                observacao = st.text_area("Observação", 
                                          value=str(ordem['observacao']) if pd.notna(ordem['observacao']) else "", 
                                          height=100)
                
                submitted = st.form_submit_button("💾 Salvar Alterações", use_container_width=True)
                
                if submitted:
                    if not sei_numero or not processo or not comunidade or not tipo_acao:
                        st.error("Preencha todos os campos obrigatórios (*)")
                    else:
                        sucesso = atualizar_ordem(
                            ordem_selecionada, sei_numero, processo, comunidade, municipio,
                            data_publicacao.strftime('%Y-%m-%d'), prazo_dias, tipo_acao, 
                            situacao, observacao, servidores
                        )
                        if sucesso:
                            st.success(f"Ordem {sei_numero} atualizada com sucesso!")
                            st.rerun()

# ==================== EXCLUIR ORDEM ====================
elif menu == "🗑️ Excluir Ordem":
    st.header("🗑️ Excluir Ordem de Serviço")
    
    if df.empty:
        st.warning("Nenhuma ordem cadastrada para excluir")
    else:
        ordem_selecionada = st.selectbox(
            "Selecione a ordem para excluir:",
            options=df['id'].tolist(),
            format_func=lambda x: f"{x} - {df[df['id']==x]['sei_numero'].iloc[0]} - {df[df['id']==x]['comunidade'].iloc[0]}"
        )
        
        if ordem_selecionada:
            ordem = df[df['id'] == ordem_selecionada].iloc[0]
            
            st.warning("⚠️ Atenção! Esta ação não pode ser desfeita.")
            
            col1, col2 = st.columns(2)
            with col1:
                st.write(f"**SEI:** {ordem['sei_numero']}")
                st.write(f"**Comunidade:** {ordem['comunidade']}")
                st.write(f"**Processo:** {ordem['processo']}")
            with col2:
                st.write(f"**Data Publicação:** {pd.to_datetime(ordem['data_publicacao']).strftime('%d/%m/%Y') if pd.notna(ordem['data_publicacao']) else 'N/A'}")
                st.write(f"**Data Término:** {pd.to_datetime(ordem['data_termino']).strftime('%d/%m/%Y') if pd.notna(ordem['data_termino']) else 'Sem prazo'}")
                st.write(f"**Situação:** {ordem['situacao']}")
            
            confirmar = st.checkbox("Confirmo que desejo excluir esta ordem permanentemente")
            
            if st.button("🗑️ Excluir", type="primary", use_container_width=True):
                if confirmar:
                    sucesso = excluir_ordem(ordem_selecionada)
                    if sucesso:
                        st.success(f"Ordem {ordem['sei_numero']} excluída com sucesso!")
                        st.rerun()
                else:
                    st.error("Marque o checkbox para confirmar a exclusão")

# ==================== RODAPÉ ====================
st.sidebar.markdown("---")
st.sidebar.info(
    """
    **Sistema de Controle de Ordens de Serviço**
    
    Desenvolvido para o INCRA/MA
    
    **Legenda de Cores:**
    - 🟢 Verde: Vigente (mais de 15 dias)
    - 🟡 Amarelo: Vigente (até 15 dias - Atenção!)
    - 🔴 Vermelho: Vencida
    
    **Prazo zero:** Ordens sem prazo definido
    """
)

if st.sidebar.button("🔄 Atualizar Situações", use_container_width=True):
    atualizar_situacoes()
    st.sidebar.success("Situações atualizadas!")
    st.rerun()