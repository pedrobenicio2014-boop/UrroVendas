import streamlit as st
import pandas as pd
import os
from datetime import datetime
import plotly.express as px

# --- Configurações da página ---
st.set_page_config(page_title="URRO Admin", layout="wide", page_icon="🐾")

# Estilo da URRO - deixei o CSS aqui em cima pra facilitar
estilo_custom = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;600;800&display=swap');
    
    * { font-family: 'Plus Jakarta Sans', sans-serif; }
    
    /* Deixar os cards brancos e limpos */
    [data-testid="stMetric"] {
        background: white !important;
        padding: 20px !important;
        border-radius: 15px !important;
        border: 1px solid #eee !important;
    }

    [data-testid="stMetricLabel"] p { color: #555 !important; }
    [data-testid="stMetricValue"] div { color: #000 !important; }

    /* Estilo da barra lateral */
    [data-testid="stSidebar"] { background-color: #0d0d0d !important; }
    
    .stButton > button {
        border-radius: 8px !important;
        background-color: #000 !important;
        color: white !important;
        height: 3em;
        width: 100%;
    }
</style>
"""
st.markdown(estilo_custom, unsafe_allow_html=True)

# Arquivos do banco de dados (CSV)
file_estoque = "estoque_urro.csv"
file_vendas = "historico_vendas_urro.csv"
img_logo = "logo_urro.png"

# Pessoal que tem acesso
equipe = {
    "0802": "Pedro Reino", 
    "3105": "Lucas Saboia", 
    "0405": "Gabriel Gomes"
}

# Opções das Oversized
modelos_camisas = [
    "Preta Retrô", "Preta Strength", "Preta Become Gain", 
    "Preta Monkey Bad", "Preta Malboro", "Branca Retrô", 
    "Branca Become Gain", "Branca Bomba", "Branca Jacô", "Branca Reveillon"
]
grades = ["P", "M", "G", "GG"]

# --- Funções para ler e salvar os dados ---
def puxar_estoque():
    if os.path.exists(file_estoque):
        dados = pd.read_csv(file_estoque)
        dados.columns = [c.strip().capitalize() for c in dados.columns]
        # print("Estoque carregado com sucesso") # Debug
        return dados.set_index(dados.columns[0])
    return pd.DataFrame({'Quantidade': [100, 50], 'Preço unitário': [80.0, 110.0]}, index=['Camisa Oversized', 'Camisa Suedine'])

def puxar_vendas():
    if os.path.exists(file_vendas):
        vnds = pd.read_csv(file_vendas)
        if not vnds.empty:
            vnds['Data'] = pd.to_datetime(vnds['Data'], dayfirst=True, errors='coerce')
        return vnds
    return pd.DataFrame(columns=['Data', 'Vendedor', 'Cliente', 'Produto', 'Modelo', 'Tamanho', 'Qtd', 'Desconto', 'Valor Total'])

def atualizar_arquivo(df_para_salvar, nome_arq, com_index=False):
    df_para_salvar.to_csv(nome_arq, index=com_index)

# --- Sistema de Login ---
if 'logado' not in st.session_state:
    st.session_state.logado = False

if not st.session_state.logado:
    st.markdown("<br><br>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col2:
        if os.path.exists(img_logo):
            st.image(img_logo)
        else:
            st.title("URRO CLOTHING")
            
        with st.form("login_form"):
            senha = st.text_input("Código de Acesso", type="password")
            entrar = st.form_submit_button("ACESSAR PAINEL")
            
            if entrar:
                if senha in equipe:
                    st.session_state.logado = True
                    st.session_state.user = equipe[senha]
                    st.rerun()
                else:
                    st.error("Código incorreto, tenta de novo.")
    st.stop()

# Carregando o que precisa
db_estoque = puxar_estoque()
db_vendas = puxar_vendas()

# --- Menu Lateral ---
with st.sidebar:
    if os.path.exists(img_logo):
        st.image(img_logo)
    
    st.write(f"Logado como: **{st.session_state.user}**")
    
    escolha = st.radio("Navegação", ["Dashboard", "PDV - Venda", "Estoque", "Relatórios"])
    
    if st.button("Deslogar"):
        st.session_state.logado = False
        st.rerun()

# --- Área do Dashboard ---
if escolha == "Dashboard":
    st.header("Resumo da Marca")
    
    # Cálculos rápidos
    total_grana = db_vendas['Valor Total'].sum() if not db_vendas.empty else 0
    total_pecas = int(db_estoque['Quantidade'].sum())
    
    c1, c2, c3 = st.columns(3)
    c1.metric("Faturamento Total", f"R$ {total_grana:,.2f}")
    c2.metric("Peças em Estoque", f"{total_pecas} un")
    c3.metric("Vendas Realizadas", len(db_vendas))

    st.write("---")
    
    # Gráfico de vendas
    if not db_vendas.empty:
        vendas_dia = db_vendas.groupby(db_vendas['Data'].dt.date)['Valor Total'].sum().reset_index()
        figura = px.line(vendas_dia, x='Data', y='Valor Total', title="Vendas por Dia", color_discrete_sequence=['#000'])
        st.plotly_chart(figura, use_container_width=True)
    else:
        st.info("Nenhuma venda registrada ainda.")

# --- Área de Venda (PDV) ---
elif escolha == "PDV - Venda":
    st.header("Registrar Nova Venda")
    
    with st.container():
        nome_cliente = st.text_input("Quem comprou?")
        tipo_peca = st.selectbox("O que comprou?", db_estoque.index)
        
        col_m, col_t, col_q = st.columns(3)
        item_modelo = col_m.selectbox("Modelo", modelos_camisas)
        item_tamanho = col_t.selectbox("Tam", grades)
        item_qtd = col_q.number_input("Qtd", min_value=1, value=1)
        
        preco_base = float(db_estoque.loc[tipo_peca, 'Preço unitário'])
        desconto = st.number_input("Teve desconto? (R$)", min_value=0.0)
        
        valor_final = (item_qtd * preco_base) - desconto
        st.subheader(f"Total: R$ {valor_final:.2f}")
        
        if st.button("FECHAR VENDA"):
            # Verificando se tem no estoque antes
            if db_estoque.loc[tipo_peca, 'Quantidade'] >= item_qtd:
                db_estoque.loc[tipo_peca, 'Quantidade'] -= item_qtd
                atualizar_arquivo(db_estoque, file_estoque, com_index=True)
                
                # Montando a linha da venda
                venda_agora = {
                    'Data': datetime.now().strftime("%d/%m/%Y %H:%M"),
                    'Vendedor': st.session_state.user,
                    'Cliente': nome_cliente,
                    'Produto': tipo_peca,
                    'Modelo': item_modelo,
                    'Tamanho': item_tamanho,
                    'Qtd': item_qtd,
                    'Desconto': desconto,
                    'Valor Total': valor_final
                }
                
                db_vendas = pd.concat([db_vendas, pd.DataFrame([venda_agora])], ignore_index=True)
                atualizar_arquivo(db_vendas, file_vendas)
                
                st.success("Vendido com sucesso!")
                st.balloons()
            else:
                st.error("Não tem tudo isso no estoque!")

# --- Visualização Simples ---
elif escolha == "Estoque":
    st.header("Gerenciar Inventário")
    edit_estoque = st.data_editor(db_estoque, use_container_width=True)
    if st.button("Salvar Alterações"):
        atualizar_arquivo(edit_estoque, file_estoque, com_index=True)
        st.success("Tudo atualizado!")

elif escolha == "Relatórios":
    st.header("Histórico Completo")
    st.dataframe(db_vendas, use_container_width=True)
