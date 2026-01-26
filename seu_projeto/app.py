import streamlit as st
import pandas as pd
import os
from datetime import datetime
import plotly.express as px

# ======================================================
# CONFIGURAÇÃO DA PÁGINA
# ======================================================
st.set_page_config(
    page_title="URRO Clothing | ERP",
    layout="wide",
    page_icon="🖤"
)

# ======================================================
# CSS CORPORATIVO (NEUTRO)
# ======================================================
st.markdown("""
<style>
html, body, [class*="css"] {
    font-family: "Segoe UI", sans-serif;
}

section[data-testid="stSidebar"] {
    background-color: #111111;
}

section[data-testid="stSidebar"] * {
    color: #ffffff;
}

section[data-testid="stSidebar"] h1 {
    font-size: 26px;
    letter-spacing: 4px;
}

.stButton > button {
    background-color: #2b2b2b;
    color: #ffffff;
    border-radius: 6px;
    padding: 10px;
    border: none;
    font-weight: 500;
}

.stButton > button:hover {
    background-color: #000000;
}

input, textarea, select {
    border-radius: 6px !important;
}

.kpi-card {
    background: #ffffff;
    padding: 20px;
    border-radius: 8px;
    box-shadow: 0 2px 6px rgba(0,0,0,.08);
    text-align: center;
}

.kpi-title {
    font-size: 12px;
    color: #6b6b6b;
}

.kpi-value {
    font-size: 26px;
    font-weight: bold;
    margin-top: 6px;
}
</style>
""", unsafe_allow_html=True)

# ======================================================
# ARQUIVOS
# ======================================================
ARQUIVO_ESTOQUE = "estoque_urro.csv"
ARQUIVO_VENDAS = "historico_vendas_urro.csv"
ARQUIVO_CAIXA = "fluxo_caixa_urro.csv"

VENDEDORES = {
    "0802": "Pedro Reino",
    "3105": "Lucas Saboia",
    "2810": "Gabriel Gomes"
}

MODELOS = [
    "Preta Retrô", "Preta Strength", "Preta Become Gain",
    "Preta Monkey Bad", "Preta Malboro",
    "Branca Retrô", "Branca Become Gain",
    "Branca Bomba", "Branca Jacô", "Branca Reveillon"
]

TAMANHOS = ["P", "M", "G", "GG"]

# ======================================================
# FUNÇÕES
# ======================================================
def carregar_estoque():
    if os.path.exists(ARQUIVO_ESTOQUE):
        try:
            return pd.read_csv(
                ARQUIVO_ESTOQUE,
                sep=";",
                encoding="utf-8"
            )
        except:
            return pd.read_csv(
                ARQUIVO_ESTOQUE,
                sep=",",
                encoding="latin1"
            )

    return pd.DataFrame({
        "Produto": ["Camisa Oversized", "Camisa Suedine"],
        "Quantidade": [100, 50],
        "Preço Unitário": [80.0, 110.0]
    })

def carregar_vendas():
    if os.path.exists(ARQUIVO_VENDAS):
        return pd.read_csv(ARQUIVO_VENDAS)
    return pd.DataFrame(columns=[
        'Data', 'Vendedor', 'Cliente', 'Produto',
        'Modelo', 'Tamanho', 'Qtd', 'Desconto', 'Valor Total'
    ])

def carregar_caixa():
    if os.path.exists(ARQUIVO_CAIXA):
        return pd.read_csv(ARQUIVO_CAIXA)
    return pd.DataFrame(columns=['Data', 'Vendedor', 'Tipo', 'Descrição', 'Valor'])

def salvar(df, arquivo, index=False):
    df.to_csv(arquivo, index=index)

# ======================================================
# SESSION STATE
# ======================================================
if 'logado' not in st.session_state:
    st.session_state.logado = False
    st.session_state.vendedor = ""

# ======================================================
# LOGIN
# ======================================================
if not st.session_state.logado:
    st.markdown("<br><br><br>", unsafe_allow_html=True)
    _, c, _ = st.columns([1, 1.3, 1])

    with c:
        st.markdown("""
        <div style="text-align:center; margin-bottom:30px;">
            <h1 style="letter-spacing:6px;">URRO</h1>
            <p style="margin-top:-15px; color:#6b6b6b;">CLOTHING</p>
        </div>
        """, unsafe_allow_html=True)

        codigo = st.text_input("Código de Acesso", type="password")

        if st.button("ACESSAR SISTEMA", use_container_width=True):
            if codigo in VENDEDORES:
                st.session_state.logado = True
                st.session_state.vendedor = VENDEDORES[codigo]
                st.rerun()
            else:
                st.error("Código inválido")

    st.stop()

# ======================================================
# CARREGAMENTO
# ======================================================
df_estoque = carregar_estoque()
df_vendas = carregar_vendas()
df_caixa = carregar_caixa()

# ======================================================
# SIDEBAR
# ======================================================
with st.sidebar:
    st.markdown("<h1>URRO</h1><p style='margin-top:-20px;'>CLOTHING</p>", unsafe_allow_html=True)
    st.write(f"👤 **{st.session_state.vendedor}**")
    st.divider()

    aba = st.radio(
        "NAVEGAÇÃO",
        ["📊 Painel Geral", "💸 Vendas", "💰 Caixa", "📦 Estoque", "📄 Relatórios"]
    )

    if st.button("🚪 Logout"):
        st.session_state.logado = False
        st.rerun()

# ======================================================
# PAINEL GERAL
# ======================================================
if aba == "📊 Painel Geral":
    st.title("Painel Geral")

    faturamento = df_vendas['Valor Total'].sum()
    entradas = df_caixa[df_caixa['Tipo'] == 'Entrada']['Valor'].sum()
    saidas = df_caixa[df_caixa['Tipo'] == 'Saída']['Valor'].sum()
    saldo = (faturamento + entradas) - saidas

    c1, c2, c3 = st.columns(3)

    with c1:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-title">Faturamento Total</div>
            <div class="kpi-value">R$ {faturamento:,.2f}</div>
        </div>
        """, unsafe_allow_html=True)

    with c2:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-title">Saldo em Caixa</div>
            <div class="kpi-value">R$ {saldo:,.2f}</div>
        </div>
        """, unsafe_allow_html=True)

    with c3:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-title">Peças em Estoque</div>
            <div class="kpi-value">{int(df_estoque['Quantidade'].sum())}</div>
        </div>
        """, unsafe_allow_html=True)

# ======================================================
# VENDAS
# ======================================================
elif aba == "💸 Vendas":
    st.title("Ponto de Venda")

    colA, colB = st.columns([2, 1])

    with colA:
        cliente = st.text_input("Cliente")
        produto = st.selectbox("Produto", df_estoque.index)
        modelo = st.selectbox("Modelo", MODELOS)
        tamanho = st.selectbox("Tamanho", TAMANHOS)
        qtd = st.number_input("Quantidade", min_value=1)

    with colB:
        preco = float(df_estoque.loc[produto, 'Preço Unitário'])
        desconto = st.number_input("Desconto (R$)", min_value=0.0)
        total = (qtd * preco) - desconto

        st.metric("Preço Unitário", f"R$ {preco:.2f}")
        st.metric("Total da Venda", f"R$ {max(0,total):.2f}")

    if st.button("FINALIZAR VENDA", use_container_width=True):
        if df_estoque.loc[produto, 'Quantidade'] >= qtd:
            df_estoque.loc[produto, 'Quantidade'] -= qtd
            salvar(df_estoque, ARQUIVO_ESTOQUE, index=True)

            nova = {
                'Data': datetime.now().strftime("%d/%m/%Y %H:%M"),
                'Vendedor': st.session_state.vendedor,
                'Cliente': cliente,
                'Produto': produto,
                'Modelo': modelo,
                'Tamanho': tamanho,
                'Qtd': qtd,
                'Desconto': desconto,
                'Valor Total': total
            }

            df_vendas = pd.concat([df_vendas, pd.DataFrame([nova])], ignore_index=True)
            salvar(df_vendas, ARQUIVO_VENDAS)

            st.success("Venda realizada com sucesso!")
            st.rerun()
        else:
            st.error("Estoque insuficiente")

# ======================================================
# CAIXA
# ======================================================
elif aba == "💰 Caixa":
    st.title("Fluxo de Caixa")

    tipo = st.selectbox("Tipo", ["Entrada", "Saída"])
    desc = st.text_input("Descrição")
    valor = st.number_input("Valor", min_value=0.0)

    if st.button("Registrar", use_container_width=True):
        novo = {
            'Data': datetime.now().strftime("%d/%m/%Y"),
            'Vendedor': st.session_state.vendedor,
            'Tipo': tipo,
            'Descrição': desc,
            'Valor': valor
        }
        df_caixa = pd.concat([df_caixa, pd.DataFrame([novo])], ignore_index=True)
        salvar(df_caixa, ARQUIVO_CAIXA)
        st.rerun()

    st.dataframe(df_caixa, use_container_width=True)

# ======================================================
# RELATÓRIOS
# ======================================================
elif aba == "📄 Relatórios":
    st.title("Relatórios de Vendas")
    st.dataframe(df_vendas, use_container_width=True)

    if not df_vendas.empty:
        fig = px.pie(df_vendas, values="Valor Total", names="Vendedor", hole=0.4)
        st.plotly_chart(fig, use_container_width=True)

# ======================================================
# ESTOQUE
# ======================================================
elif aba == "📦 Estoque":
    st.title("Gestão de Estoque")

    df_edit = st.data_editor(df_estoque, use_container_width=True)

    if st.button("Salvar Estoque", use_container_width=True):
        salvar(df_edit, ARQUIVO_ESTOQUE, index=True)
        st.success("Estoque atualizado!")
