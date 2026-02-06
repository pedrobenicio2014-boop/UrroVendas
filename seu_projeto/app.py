import streamlit as st
import pandas as pd
import os
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go
import io
from streamlit_gsheets import GSheetsConnection

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

   /* FORÇAR COR PRETA NOS NOMES E VALORES DAS MÉTRICAS */
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

## ======================================================
# 2. FUNÇÕES DE DADOS E CONFIGURAÇÕES (ADAPTADO PARA GOOGLE SHEETS)
# ======================================================
ARQUIVO_ESTOQUE = "estoque_urro.csv"
ARQUIVO_VENDAS = "historico_vendas_urro.csv"
ARQUIVO_CAIXA = "fluxo_caixa_urro.csv"
LOGO_PATH = "logo_urro.png" 

# --- LÓGICA DE CONEXÃO SEGURA ---
# Criamos uma cópia das secrets em um dicionário comum (que permite alteração)
if "connections" in st.secrets and "gsheets" in st.secrets.connections:
    creds = dict(st.secrets.connections.gsheets)
    # Removemos o erro de formatação da chave privada (trocando \n de texto por quebra de linha real)
    if "private_key" in creds:
        creds["private_key"] = creds["private_key"].replace("\\n", "\n")
    
    # Iniciamos a conexão passando as credenciais limpas via **kwargs
    conn = st.connection("gsheets", type=GSheetsConnection, **creds)
else:
    # Fallback caso as secrets não estejam configuradas ainda
    conn = st.connection("gsheets", type=GSheetsConnection)

# --- FUNÇÕES DE CARREGAMENTO ---
def carregar_estoque():
    try:
        df = conn.read(worksheet="Estoque", ttl=0)
        if not df.empty:
            df.columns = [c.strip().capitalize() for c in df.columns]
            df = df.set_index(df.columns[0])
            return df
    except: pass
    return pd.DataFrame({
        'Quantidade': [100, 50], 
        'Preço unitário': [80.0, 110.0],
        'Custo unitário': [40.0, 55.0]
    }, index=['Camisa Oversized', 'Camisa Suedine'])

def carregar_vendas():
    try:
        df = conn.read(worksheet="Vendas", ttl=0)
        if not df.empty:
            df['Data'] = pd.to_datetime(df['Data'], dayfirst=True, errors='coerce')
            return df
    except: pass
    return pd.DataFrame(columns=['Data', 'Vendedor', 'Cliente', 'Produto', 'Modelo', 'Tamanho', 'Qtd', 'Desconto', 'Valor Total', 'Pagamento', 'Lucro'])

def carregar_caixa():
    try:
        df = conn.read(worksheet="Caixa", ttl=0)
        if not df.empty: return df
    except: pass
    return pd.DataFrame(columns=['Data', 'Vendedor', 'Tipo', 'Descrição', 'Valor', 'Metodo'])

def salvar(df, arquivo, index=False):
    # Mapeia o nome do arquivo para a aba correta da planilha
    aba = "Estoque" if arquivo == ARQUIVO_ESTOQUE else ("Vendas" if arquivo == ARQUIVO_VENDAS else "Caixa")
    df_para_salvar = df.reset_index() if index else df
    conn.update(worksheet=aba, data=df_para_salvar)

VENDEDORES = {
   "0802": "Pedro Reino",
   "0808": "Lucas Saboia",
   "0405": "Gabriel Gomes"
}

MODELOS = ["Preta Retrô", "Preta Strength", "Preta Become Gain", "Preta Monkey Bad", "Preta Malboro", "Branca Retrô", "Branca Become Gain", "Branca Bomba", "Branca Jacô", "Branca Reveillon"]
TAMANHOS = ["P", "M", "G", "GG"]
FORMAS_PAGAMENTO = ["Pix", "Cartão de Crédito", "Cartão de Débito", "Dinheiro", "Fiado / A Pagar"]

def carregar_estoque():
    try:
        df = conn.read(worksheet="Estoque", ttl=0)
        if not df.empty:
            df.columns = [c.strip().capitalize() for c in df.columns]
            df = df.set_index(df.columns[0])
            return df
    except: pass
    return pd.DataFrame({
        'Quantidade': [100, 50], 
        'Preço unitário': [80.0, 110.0],
        'Custo unitário': [40.0, 55.0]
    }, index=['Camisa Oversized', 'Camisa Suedine'])

def carregar_vendas():
    try:
        df = conn.read(worksheet="Vendas", ttl=0)
        if not df.empty:
            df['Data'] = pd.to_datetime(df['Data'], dayfirst=True, errors='coerce')
            return df
    except: pass
    return pd.DataFrame(columns=['Data', 'Vendedor', 'Cliente', 'Produto', 'Modelo', 'Tamanho', 'Qtd', 'Desconto', 'Valor Total', 'Pagamento', 'Lucro'])

def carregar_caixa():
    try:
        df = conn.read(worksheet="Caixa", ttl=0)
        if not df.empty: return df
    except: pass
    return pd.DataFrame(columns=['Data', 'Vendedor', 'Tipo', 'Descrição', 'Valor', 'Metodo'])

def salvar(df, arquivo, index=False):
    # Mapeia o nome do arquivo para a aba correta da planilha
    aba = "Estoque" if arquivo == ARQUIVO_ESTOQUE else ("Vendas" if arquivo == ARQUIVO_VENDAS else "Caixa")
    df_para_salvar = df.reset_index() if index else df
    conn.update(worksheet=aba, data=df_para_salvar)

def converter_para_excel(df):
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Relatorio_Urro')
    return output.getvalue()

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
           codigo = st.text_input("Acesso do Colaborador", type="password", placeholder="Digite seu código").strip()
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
  
   aba = st.radio("MENU PRINCIPAL", ["📊 Dashboard", "🛒 Ponto de Venda", "📦 Estoque", "💰 Financeiro", "📄 Relatórios", "👥 Devedores"])
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
   lucro_total = df_vendas['Lucro'].sum() if 'Lucro' in df_vendas.columns else 0
   estoque_total = int(df_estoque['Quantidade'].sum())
   ticket_medio = faturamento / len(df_vendas) if not df_vendas.empty else 0

   c1, c2, c3, c4 = st.columns(4)
   c1.metric("Faturamento", f"R$ {faturamento:,.2f}")
   c2.metric("Peças em Estoque", f"{estoque_total} un")
   c3.metric("Lucro Líquido", f"R$ {lucro_total:,.2f}", delta=f"{ (lucro_total/faturamento*100) if faturamento>0 else 0:.1f}% margem")
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
           pagamento = st.selectbox("Forma de Pagamento", FORMAS_PAGAMENTO)
      
       with col_recibo:
           st.markdown("### Resumo do Pedido")
           preco_un = float(df_estoque.loc[categoria, 'Preço unitário'])
           desc = st.number_input("Desconto (R$)", min_value=0.0, step=5.0)
           total = (qtd * preco_un) - desc
           
           custo_un = float(df_estoque.loc[categoria, 'Custo unitário'])
           lucro_venda = total - (qtd * custo_un)
          
           st.markdown(f"""
               <div style='background:#F8F9FB; padding:20px; border-radius:12px; border: 1px solid #EEE;'>
                   <small style='color:#666;'>TOTAL A PAGAR</small>
                   <h1 style='color:#111; margin:0;'>R$ {max(0,total):,.2f}</h1>
                   <small>Pagamento: {pagamento}</small>
               </div>
           """, unsafe_allow_html=True)
          
           st.markdown("<br>", unsafe_allow_html=True)
           if st.button("CONCLUIR VENDA", use_container_width=True):
               if df_estoque.loc[categoria, 'Quantidade'] >= qtd:
                   df_estoque.loc[categoria, 'Quantidade'] -= qtd
                   salvar(df_estoque, ARQUIVO_ESTOQUE, index=True)
                   
                   nova_venda = {
                        'Data': datetime.now().strftime("%d/%m/%Y %H:%M"), 
                        'Vendedor': st.session_state.vendedor, 
                        'Cliente': cliente, 
                        'Produto': categoria, 
                        'Modelo': mod, 
                        'Tamanho': tam, 
                        'Qtd': qtd, 
                        'Desconto': desc, 
                        'Valor Total': total,
                        'Pagamento': pagamento,
                        'Lucro': lucro_venda
                    }
                   df_vendas = pd.concat([df_vendas, pd.DataFrame([nova_venda])], ignore_index=True)
                   salvar(df_vendas, ARQUIVO_VENDAS)
                   
                   if pagamento != "Fiado / A Pagar":
                       nova_mov_caixa = {
                           'Data': datetime.now().strftime("%d/%m/%Y"), 
                           'Vendedor': st.session_state.vendedor, 
                           'Tipo': 'Entrada', 
                           'Descrição': f"Venda: {mod} ({cliente})", 
                           'Valor': total, 
                           'Metodo': pagamento
                       }
                       df_caixa = pd.concat([df_caixa, pd.DataFrame([nova_mov_caixa])], ignore_index=True)
                       salvar(df_caixa, ARQUIVO_CAIXA)

                   st.success("Venda finalizada!")
                   st.balloons()
                   st.rerun()
               else: st.error("Estoque Insuficiente!")

# ======================================================
# 7. ESTOQUE
# ======================================================
elif aba == "📦 Estoque":
   st.title("📦 Inventário Urro")
   with st.container(border=True):
       df_edit = st.data_editor(df_estoque, use_container_width=True)
       if st.button("Salvar Modificações"):
           salvar(df_edit, ARQUIVO_ESTOQUE, index=True)
           st.success("Estoque atualizado!")

# ======================================================
# 8. FINANCEIRO
# ======================================================
elif aba == "💰 Financeiro":
    st.title("💰 Gestão de Caixa")

    if not df_caixa.empty:
        df_caixa["Valor"] = pd.to_numeric(df_caixa["Valor"], errors="coerce").fillna(0)

    entradas = df_caixa[df_caixa["Tipo"] == "Entrada"]["Valor"].sum()
    saidas = df_caixa[df_caixa["Tipo"] == "Saída"]["Valor"].sum()
    saldo = entradas - saidas

    c1, c2, c3 = st.columns(3)
    c1.metric("Entradas", f"R$ {entradas:,.2f}")
    c2.metric("Saídas", f"R$ {saidas:,.2f}")
    c3.metric("Saldo Atual", f"R$ {saldo:,.2f}")

    st.divider()

    st.markdown("### ➕ Nova Movimentação")
    col1, col2 = st.columns(2)
    with col1:
        tipo_mov = st.selectbox("Tipo", ["Entrada", "Saída"])
        desc_mov = st.text_input("Descrição", placeholder="Ex: Compra de tecido, aluguel...")
    with col2:
        valor_mov = st.number_input("Valor (R$)", min_value=0.0, step=10.0, format="%.2f", key="valor_manual_fin_pd")
        metodo_mov = st.selectbox("Método", FORMAS_PAGAMENTO)
        data_mov = st.date_input("Data", value=datetime.now())

    if st.button("Registrar Movimentação", use_container_width=True):
        if valor_mov > 0 and desc_mov:
            nova_mov = {
                "Data": data_mov.strftime("%d/%m/%Y"),
                "Vendedor": st.session_state.vendedor,
                "Tipo": tipo_mov,
                "Descrição": desc_mov,
                "Valor": float(valor_mov),
                "Metodo": metodo_mov
            }
            df_caixa = pd.concat([df_caixa, pd.DataFrame([nova_mov])], ignore_index=True)
            salvar(df_caixa, ARQUIVO_CAIXA)
            st.success("Movimentação registrada!")
            st.rerun()
        else:
            st.error("Informe descrição e valor válido.")

    st.divider()
    st.markdown("### 📊 Histórico Financeiro")
    st.dataframe(df_caixa.sort_values("Data", ascending=False), use_container_width=True)

# ======================================================
# 9. RELATÓRIOS
# ======================================================
elif aba == "📄 Relatórios":
   st.title("📄 Histórico Detalhado")
   
   with st.container(border=True):
       st.markdown("🔍 **Busca Avançada**")
       col_b1, col_b2 = st.columns(2)
       filtro_nome = col_b1.text_input("Filtrar por Cliente", placeholder="Nome ou @insta")
       filtro_modelo = col_b2.multiselect("Filtrar por Modelos", MODELOS)

   df_final = df_vendas.copy()
   if filtro_nome:
       df_final = df_final[df_final['Cliente'].str.contains(filtro_nome, case=False, na=False)]
   if filtro_modelo:
       df_final = df_final[df_final['Modelo'].isin(filtro_modelo)]
   
   col_header, col_btn = st.columns([4, 1])
   with col_btn:
       if not df_final.empty:
           excel_file = converter_para_excel(df_final)
           st.download_button(
               label="📥 EXPORTAR FILTRADO",
               data=excel_file,
               file_name=f"relatorio_urro_{datetime.now().strftime('%Y%m%d')}.xlsx",
               mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
               use_container_width=True
           )
   
   st.dataframe(df_final, use_container_width=True)

# ======================================================
# 10. DEVEDORES
# ======================================================
elif aba == "👥 Devedores":
   st.title("👥 Controle de Clientes Devedores")
   
   df_dividas = df_vendas[df_vendas['Pagamento'] == "Fiado / A Pagar"].copy()
   
   if not df_dividas.empty:
       total_fiado = df_dividas['Valor Total'].sum()
       st.markdown(f"""
           <div style='background:#FFF5F5; padding:25px; border-radius:15px; border:1px solid #FEB2B2; margin-bottom:20px;'>
               <small style='color:#C53030;'>TOTAL A RECEBER NA RUA</small>
               <h1 style='color:#C53030; margin:0;'>R$ {total_fiado:,.2f}</h1>
           </div>
       """, unsafe_allow_html=True)
       
       st.markdown("### Ranking de Devedores")
       df_nomes_div = df_dividas.groupby('Cliente')['Valor Total'].sum().reset_index().sort_values('Valor Total', ascending=False)
       st.dataframe(df_nomes_div, use_container_width=True, hide_index=True)
       
       st.divider()
       st.markdown("### Histórico de Fiados")
       st.dataframe(df_dividas[['Data', 'Cliente', 'Modelo', 'Valor Total']], use_container_width=True)
   else:
       st.success("Tudo certo! Ninguém devendo no momento.")

# Bloco de Diagnóstico Temporário
if "connections" in st.secrets:
    credenciais = st.secrets.connections.gsheets
    st.sidebar.write("### 🛠️ Debug de Conexão")
    st.sidebar.write(f"Chave detectada: {credenciais.get('private_key', '')[:25]}...")
    if "\\n" in credenciais.get("private_key", ""):
        st.sidebar.error("❌ Erro: O Streamlit está lendo o '\\n' como texto puro. Use aspas duplas nas Secrets.")
    else:
        st.sidebar.success("✅ Formato da chave parece correto.")
