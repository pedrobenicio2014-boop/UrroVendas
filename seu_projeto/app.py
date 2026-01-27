import streamlit as st
import pandas as pd
import os
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go

# ======================================================
# 1. SETUP E DESIGN SYSTEM (URRO BRANDING)
# ======================================================
st.set_page_config(page_title="URRO Admin | Gestão de Marca", layout="wide", page_icon="🐾")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;600;800&display=swap');
    
    html, body, [class*="css"] { font-family: 'Plus Jakarta Sans', sans-serif; }
    .main { background-color: #F8F9FB; }

    /* Cartões de Métrica Premium */
    [data-testid="stMetric"] {
        background: white !important;
        padding: 24px !important;
        border-radius: 20px !important;
        box-shadow: 0 10px 15px -3px rgba(0,0,0,0.03) !important;
        border: 1px solid #F1F3F5 !important;
    }

    [data-testid="stMetricLabel"] p { color: #000000 !important; }
    [data-testid="stMetricValue"] div { color: #000000 !important; }

    /* Sidebar Dark Stealth */
    [data-testid="stSidebar"] { background-color: #0A0A0A !important; border-right: 1px solid #1A1A1A; }
    [data-testid="stSidebar"] * { color: #8E8E93 !important; }
    .st-emotion-cache-1cypcdm { color: white !important; }

    /* Botões de Ação */
    .stButton > button {
        border-radius: 12px !important;
        background-color: #111111 !important;
        color: white !important;
        font-weight: 700 !important;
        padding: 14px 28px !important;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    }
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 20px rgba(0,0,0,0.2);
        background-color: #000000 !important;
    }

    /* Alerta de Estoque Baixo */
    .stock-alert {
        background: #FFF5F5;
        border: 1px solid #FEB2B2;
        padding: 10px;
        border-radius: 10px;
        color: #C53030;
        font-weight: 600;
        margin-bottom: 10px;
    }
</style>
""", unsafe_allow_html=True)

# ======================================================
# 2. FUNÇÕES DE DADOS E CONFIGURAÇÕES
# ======================================================
ARQUIVO_ESTOQUE = "estoque_urro.csv"
ARQUIVO_VENDAS = "historico_vendas_urro.csv"
ARQUIVO_CAIXA = "fluxo_caixa_urro.csv"
LOGO_PATH = "logo_urro.png" 

VENDEDORES = {"0802": "Pedro Reino", "3105": "Lucas Saboia", "0405": "Gabriel Gomes"}
MODELOS = ["Preta Retrô", "Preta Strength", "Preta Become Gain", "Preta Monkey Bad", "Preta Malboro", "Branca Retrô", "Branca Become Gain", "Branca Bomba", "Branca Jacô", "Branca Reveillon"]
TAMANHOS = ["P", "M", "G", "GG"]

def carregar_estoque():
    if os.path.exists(ARQUIVO_ESTOQUE):
        df = pd.read_csv(ARQUIVO_ESTOQUE)
        df.columns = [c.strip().capitalize() for c in df.columns]
        df = df.set_index(df.columns[0])
        return df
    return pd.DataFrame({'Quantidade': [100, 50], 'Preço unitário': [80.0, 110.0]}, index=['Camisa Oversized', 'Camisa Suedine'])

def carregar_vendas():
    if os.path.exists(ARQUIVO_VENDAS):
        df = pd.read_csv(ARQUIVO_VENDAS)
        if not df.empty:
            df['Data'] = pd.to_datetime(df['Data'], dayfirst=True, errors='coerce')
        return df
    return pd.DataFrame(columns=['Data', 'Vendedor', 'Cliente', 'Produto', 'Modelo', 'Tamanho', 'Qtd', 'Desconto', 'Valor Total'])

def carregar_caixa():
    if os.path.exists(ARQUIVO_CAIXA):
        return pd.read_csv(ARQUIVO_CAIXA)
    return pd.DataFrame(columns=['Data', 'Vendedor', 'Tipo', 'Descrição', 'Valor'])

def salvar(df, arquivo, index=False):
    df.to_csv(arquivo, index=index)

# ======================================================
# 3. LÓGICA DE ACESSO
# ======================================================
if 'logado' not in st.session_state: st.session_state.logado = False
if 'vendedor' not in st.session_state: st.session_state.vendedor = ""

if not st.session_state.logado:
    st.markdown("<br><br><br>", unsafe_allow_html=True)
    _, c, _ = st.columns([1, 0.8, 1])
    with c:
        if os.path.exists(LOGO_PATH):
            st.image(LOGO_PATH, use_container_width=True)
        else:
            st.markdown("<h1 style='text-align:center;'>URRO</h1>", unsafe_allow_html=True)
        
        st.markdown("<p style='text-align:center; letter-spacing:4px; color:#6b6b6b; margin-top:-15px;'>CLOTHING</p>", unsafe_allow_html=True)
        
        with st.container(border=True):
            codigo = st.text_input("Acesso do Colaborador", type="password", placeholder="Digite seu código")
            if st.button("ENTRAR NO SISTEMA", use_container_width=True):
                if codigo in VENDEDORES:
                    st.session_state.logado, st.session_state.vendedor = True, VENDEDORES[codigo]
                    st.rerun()
                else: st.error("Código inválido")
    st.stop()

df_estoque = carregar_estoque()
df_vendas = carregar_vendas()
df_caixa = carregar_caixa()

# ======================================================
# 4. SIDEBAR E NAVEGAÇÃO
# ======================================================
with st.sidebar:
    if os.path.exists(LOGO_PATH):
        st.image(LOGO_PATH, use_container_width=True)
    else:
        st.markdown("<h1 style='color:white; font-weight:800; margin-bottom:0;'>URRO</h1>", unsafe_allow_html=True)
    
    st.markdown("<small style='color:#555;'>ADMIN DASHBOARD</small>", unsafe_allow_html=True)
    st.markdown(f"<div style='background:#1A1A1A; padding:15px; border-radius:12px; margin:20px 0;'>👤 <b>{st.session_state.vendedor}</b></div>", unsafe_allow_html=True)
    
    aba = st.radio("MENU PRINCIPAL", ["📊 Dashboard", "🛒 Ponto de Venda", "📦 Estoque", "💰 Financeiro", "📄 Relatórios"])
    st.divider()
    if st.button("Sair"):
        st.session_state.logado = False
        st.rerun()

# ======================================================
# 5. DASHBOARD
# ======================================================
if aba == "📊 Dashboard":
    st.markdown("<h2 style='font-weight:800;'>Panorama Estratégico</h2>", unsafe_allow_html=True)
    
    low_stock = df_estoque[df_estoque['Quantidade'] < 5].index.tolist()
    if low_stock:
        for item in low_stock:
            st.markdown(f"<div class='stock-alert'>⚠️ Estoque Crítico: {item}</div>", unsafe_allow_html=True)

    faturamento = df_vendas['Valor Total'].sum() if not df_vendas.empty else 0
    estoque_total = int(df_estoque['Quantidade'].sum())
    ticket_medio = faturamento / len(df_vendas) if not df_vendas.empty else 0

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Faturamento", f"R$ {faturamento:,.2f}")
    c2.metric("Peças em Estoque", f"{estoque_total} un")
    c3.metric("Ticket Médio", f"R$ {ticket_medio:,.2f}")
    c4.metric("Total Vendas", len(df_vendas))

    st.markdown("<br>", unsafe_allow_html=True)
    col_vendas, col_ranking = st.columns([2, 1])
    
    with col_vendas:
        with st.container(border=True):
            st.subheader("📈 Tendência de Crescimento")
            if not df_vendas.empty:
                df_vendas_diarias = df_vendas.groupby(df_vendas['Data'].dt.date)['Valor Total'].sum().reset_index()
                fig = px.area(df_vendas_diarias, x='Data', y='Valor Total', color_discrete_sequence=['#111111'])
                fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', height=300, margin=dict(l=0,r=0,t=10,b=0))
                st.plotly_chart(fig, use_container_width=True)
            else: st.info("Aguardando primeiras vendas...")

    with col_ranking:
        with st.container(border=True):
            st.subheader("👕 Modelos em Alta")
            if not df_vendas.empty:
                df_prod = df_vendas.groupby('Modelo')['Qtd'].sum().reset_index().sort_values('Qtd', ascending=True)
                fig_bar = px.bar(df_prod, x='Qtd', y='Modelo', orientation='h', color_discrete_sequence=['#111111'])
                fig_bar.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', height=300, margin=dict(l=0,r=0,t=10,b=0))
                st.plotly_chart(fig_bar, use_container_width=True)
            else: st.info("Sem dados.")

# ======================================================
# 6. PONTO DE VENDA (PDV)
# ======================================================
elif aba == "🛒 Ponto de Venda":
    st.markdown("<h2 style='font-weight:800;'>Nova Operação</h2>", unsafe_allow_html=True)
    
    with st.container(border=True):
        col_form, col_recibo = st.columns([2, 1.2])
        with col_form:
            cliente = st.text_input("Cliente", placeholder="Nome ou Instagram")
            categoria = st.selectbox("Categoria de Camisa", df_estoque.index)
            c1, c2, c3 = st.columns(3)
            mod = c1.selectbox("Modelo", MODELOS)
            tam = c2.selectbox("Tamanho", TAMANHOS)
            qtd = c3.number_input("Quantidade", min_value=1, value=1)
        
        with col_recibo:
            st.markdown("### Resumo do Pedido")
            preco_un = float(df_estoque.loc[categoria, 'Preço unitário'])
            desc = st.number_input("Desconto (R$)", min_value=0.0, step=5.0)
            total = (qtd * preco_un) - desc
            
            st.markdown(f"""
                <div style='background:#F8F9FB; padding:20px; border-radius:12px; border: 1px solid #EEE;'>
                    <small style='color:#666;'>TOTAL A PAGAR</small>
                    <h1 style='color:#111; margin:0;'>R$ {max(0,total):,.2f}</h1>
                    <small>Preço unit: R$ {preco_un:.2f}</small>
                </div>
            """, unsafe_allow_html=True)
            
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("CONCLUIR VENDA", use_container_width=True):
                if df_estoque.loc[categoria, 'Quantidade'] >= qtd:
                    # 1. Atualiza Estoque
                    df_estoque.loc[categoria, 'Quantidade'] -= qtd
                    salvar(df_estoque, ARQUIVO_ESTOQUE, index=True)
                    
                    # 2. Registra Venda
                    data_atual = datetime.now().strftime("%d/%m/%Y %H:%M")
                    nova_venda = {'Data': data_atual, 'Vendedor': st.session_state.vendedor, 'Cliente': cliente, 
                                 'Produto': categoria, 'Modelo': mod, 'Tamanho': tam, 'Qtd': qtd, 'Desconto': desc, 'Valor Total': total}
                    df_vendas = pd.concat([df_vendas, pd.DataFrame([nova_venda])], ignore_index=True)
                    salvar(df_vendas, ARQUIVO_VENDAS)
                    
                    # 3. Registra Entrada no Caixa Automática
                    nova_mov = {
                        'Data': data_atual,
                        'Vendedor': st.session_state.vendedor,
                        'Tipo': 'Entrada',
                        'Descrição': f"Venda: {mod} ({cliente})",
                        'Valor': total
                    }
                    df_caixa = pd.concat([df_caixa, pd.DataFrame([nova_mov])], ignore_index=True)
                    salvar(df_caixa, ARQUIVO_CAIXA)

                    st.success("Venda finalizada e caixa atualizado!")
                    st.balloons()
                    st.rerun()
                else: st.error("Estoque Insuficiente!")

# ======================================================
# 7. ESTOQUE
# ======================================================
elif aba == "📦 Estoque":
    st.markdown("<h2 style='font-weight:800;'>📦 Inventário Urro</h2>", unsafe_allow_html=True)
    with st.container(border=True):
        df_edit = st.data_editor(df_estoque, use_container_width=True)
        if st.button("Salvar Modificações"):
            salvar(df_edit, ARQUIVO_ESTOQUE, index=True)
            st.success("Estoque atualizado!")

# ======================================================
# 8. FINANCEIRO (ENTRADAS E SAÍDAS)
# ======================================================
elif aba == "💰 Financeiro":
    st.markdown("<h2 style='font-weight:800;'>💰 Gestão de Caixa</h2>", unsafe_allow_html=True)
    
    # Formulário de Nova Movimentação
    with st.container(border=True):
        st.subheader("➕ Nova Movimentação Manual")
        f1, f2, f3, f4 = st.columns([1, 2, 1, 1])
        
        with f1:
            tipo_mov = st.selectbox("Tipo", ["Entrada", "Saída"])
        with f2:
            desc_mov = st.text_input("Descrição da Operação", placeholder="Ex: Pagamento Frete, Compra de Tecido...")
        with f3:
            valor_mov = st.number_input("Valor (R$)", min_value=0.0, step=10.0)
        with f4:
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("REGISTRAR", use_container_width=True):
                if desc_mov:
                    nova_mov = {
                        'Data': datetime.now().strftime("%d/%m/%Y %H:%M"),
                        'Vendedor': st.session_state.vendedor,
                        'Tipo': tipo_mov,
                        'Descrição': desc_mov,
                        'Valor': valor_mov if tipo_mov == "Entrada" else -valor_mov
                    }
                    df_caixa = pd.concat([df_caixa, pd.DataFrame([nova_mov])], ignore_index=True)
                    salvar(df_caixa, ARQUIVO_CAIXA)
                    st.success("Movimentação registrada!")
                    st.rerun()
                else:
                    st.error("Descreva a operação.")

    # Resumo Financeiro
    if not df_caixa.empty:
        entradas = df_caixa[df_caixa['Valor'] > 0]['Valor'].sum()
        saidas = df_caixa[df_caixa['Valor'] < 0]['Valor'].sum()
        saldo = entradas + saidas
        
        c1, c2, c3 = st.columns(3)
        c1.metric("Total Entradas", f"R$ {entradas:,.2f}")
        c2.metric("Total Saídas", f"R$ {abs(saidas):,.2f}", delta_color="inverse")
        c3.metric("Saldo em Caixa", f"R$ {saldo:,.2f}")

        st.markdown("<br>", unsafe_allow_html=True)
        st.subheader("📜 Fluxo de Caixa Detalhado")
        st.dataframe(df_caixa.sort_values('Data', ascending=False), use_container_width=True, hide_index=True)
    else:
        st.info("Sem movimentações no caixa.")

# ======================================================
# 9. RELATÓRIOS
# ======================================================
elif aba == "📄 Relatórios":
    st.markdown("<h2 style='font-weight:800;'>📄 Histórico de Vendas</h2>", unsafe_allow_html=True)
    st.dataframe(df_vendas.sort_values('Data', ascending=False), use_container_width=True, hide_index=True)
