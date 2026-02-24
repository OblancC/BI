import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(page_title="BI Vendas Asfalto", page_icon="📊", layout="wide")

@st.cache_data
def load_data():
    return pd.read_csv("dados_processados.csv")

df = load_data()

# CSS
st.markdown("""<style>
.main-header {font-size: 2.5rem; font-weight: bold; color: #1f77b4; text-align: center;}
</style>""", unsafe_allow_html=True)

# Header
st.markdown('<h1 class="main-header">📊 Dashboard BI - Vendas de Asfalto</h1>', unsafe_allow_html=True)
st.markdown("**Fonte:** ANP | **Período:** 1992-2024")
st.markdown("---")

# Sidebar
st.sidebar.title("🎛️ Filtros")
anos = st.sidebar.slider("📅 Período:", int(df['Ano'].min()), int(df['Ano'].max()), 
                         (int(df['Ano'].min()), int(df['Ano'].max())))

regioes_disp = ['Todas'] + sorted(df['Regiao'].unique().tolist())
regioes = st.sidebar.multiselect("🗺️ Região:", regioes_disp, default=['Todas'])

if 'Todas' not in regioes and len(regioes) > 0:
    ufs_disp = sorted(df[df['Regiao'].isin(regioes)]['UF'].unique().tolist())
else:
    ufs_disp = sorted(df['UF'].unique().tolist())

ufs_disp = ['Todas'] + ufs_disp
ufs = st.sidebar.multiselect("🏛️ UF:", ufs_disp, default=['Todas'])

# Filtrar
df_f = df[(df['Ano'] >= anos[0]) & (df['Ano'] <= anos[1])]
if 'Todas' not in regioes and len(regioes) > 0:
    df_f = df_f[df_f['Regiao'].isin(regioes)]
if 'Todas' not in ufs and len(ufs) > 0:
    df_f = df_f[df_f['UF'].isin(ufs)]

# Tabs
tab1, tab2, tab3, tab4 = st.tabs(["🏠 Visão Geral", "🗺️ Geográfico", "📈 Temporal", "⚠️ Pergunta 13"])

with tab1:
    st.header("🏠 Visão Geral Brasil")
    col1, col2, col3, col4, col5 = st.columns(5)
    col1.metric("📦 Total Vendas", f"{df_f['VendasTon'].sum():,.0f} ton")
    col2.metric("🏘️ Municípios", f"{df_f['CodigoIBGE'].nunique():,}")
    col3.metric("🏛️ UFs", f"{df_f['UF'].nunique()}")
    col4.metric("📊 Média Anual", f"{df_f.groupby('Ano')['VendasTon'].sum().mean():,.0f} ton")
    col5.metric("📅 Anos", f"{df_f['Ano'].nunique()}")
    
    st.markdown("---")
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📈 Evolução Temporal")
        ev = df_f.groupby('Ano')['VendasTon'].sum().reset_index()
        fig = px.line(ev, x='Ano', y='VendasTon', markers=True)
        fig.update_traces(line_color='#1f77b4', line_width=3)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("🗺️ Participação Regional")
        reg = df_f.groupby('Regiao')['VendasTon'].sum().reset_index()
        fig = px.pie(reg, values='VendasTon', names='Regiao', hole=0.4)
        st.plotly_chart(fig, use_container_width=True)
    
    col3, col4 = st.columns(2)
    
    with col3:
        st.subheader("🏆 Top 10 UFs")
        top = df_f.groupby('UF')['VendasTon'].sum().nlargest(10).reset_index()
        fig = px.bar(top, x='VendasTon', y='UF', orientation='h', color='VendasTon')
        st.plotly_chart(fig, use_container_width=True)
    
    with col4:
        st.subheader("📊 Por Década")
        dec = df_f.groupby('Decada')['VendasTon'].sum().reset_index()
        fig = px.bar(dec, x='Decada', y='VendasTon', color='VendasTon')
        st.plotly_chart(fig, use_container_width=True)

with tab2:
    st.header("🗺️ Análise Geográfica")
    
    st.subheader("🌎 Mapa do Brasil")
    mapa = df_f.groupby('UF')['VendasTon'].sum().reset_index()
    fig = px.choropleth(mapa, locations='UF', locationmode='USA-states',
                        color='VendasTon', scope='south america',
                        color_continuous_scale='YlOrRd')
    fig.update_geos(fitbounds="locations", visible=False)
    st.plotly_chart(fig, use_container_width=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📊 Ranking UFs")
        rank = df_f.groupby(['UF', 'Regiao']).agg({'VendasTon': 'sum', 'CodigoIBGE': 'nunique'}).reset_index()
        rank.columns = ['UF', 'Região', 'Vendas (ton)', 'Municípios']
        st.dataframe(rank.sort_values('Vendas (ton)', ascending=False).head(15), use_container_width=True, hide_index=True)
    
    with col2:
        st.subheader("🏆 Top 20 Municípios")
        top_m = df_f.groupby(['MunicipioOficial', 'UF'])['VendasTon'].sum().reset_index()
        top_m = top_m.nlargest(20, 'VendasTon')
        top_m.columns = ['Município', 'UF', 'Vendas (ton)']
        st.dataframe(top_m, use_container_width=True, hide_index=True)

with tab3:
    st.header("📈 Série Temporal")
    
    st.subheader("📊 Evolução por Região")
    ev_r = df_f.groupby(['Ano', 'Regiao'])['VendasTon'].sum().reset_index()
    fig = px.line(ev_r, x='Ano', y='VendasTon', color='Regiao', markers=True)
    st.plotly_chart(fig, use_container_width=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📊 Área Acumulada")
        fig = px.area(ev_r, x='Ano', y='VendasTon', color='Regiao')
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("📈 Taxa Crescimento")
        cresc = df_f.groupby('Ano')['VendasTon'].sum().reset_index()
        cresc['Crescimento_%'] = cresc['VendasTon'].pct_change() * 100
        cresc = cresc.dropna()
        fig = px.bar(cresc, x='Ano', y='Crescimento_%', color='Crescimento_%',
                     color_continuous_scale=['red','yellow','green'], color_continuous_midpoint=0)
        st.plotly_chart(fig, use_container_width=True)

with tab4:
    st.header("⚠️ Pergunta 13: Governança - Inconsistência Código IBGE")
    
    st.markdown("""
    ### 🎯 Objetivo
    Detectar casos onde um mesmo **CÓDIGO IBGE** está associado a diferentes **nomes de municípios**.
    """)
    
    total_m = df['CodigoIBGE'].nunique()
    incons = df[df['TemInconsistencia']=='Sim']['CodigoIBGE'].nunique()
    taxa = (incons/total_m)*100
    
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("🏘️ Total Municípios", f"{total_m:,}")
    col2.metric("⚠️ Com Inconsistência", f"{incons:,}", delta=f"{taxa:.2f}%")
    col3.metric("✅ Sem Problema", f"{total_m-incons:,}")
    col4.metric("📊 Taxa OK", f"{100-taxa:.2f}%")
    
    st.markdown("---")
    
    if incons > 0:
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("📊 Distribuição")
            dist = df['TemInconsistencia'].value_counts().reset_index()
            dist.columns = ['Categoria', 'Quantidade']
            fig = px.pie(dist, values='Quantidade', names='Categoria', hole=0.4,
                        color='Categoria', color_discrete_map={'Sim':'#ff7f0e', 'Não':'#2ca02c'})
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.subheader("📊 Por UF (Top 10)")
            incons_uf = df[df['TemInconsistencia']=='Sim'].groupby('UF')['CodigoIBGE'].nunique().reset_index()
            incons_uf.columns = ['UF', 'Quantidade']
            incons_uf = incons_uf.sort_values('Quantidade', ascending=False).head(10)
            fig = px.bar(incons_uf, x='UF', y='Quantidade', color='Quantidade', color_continuous_scale='Reds')
            st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("---")
    st.success(f"""
    ### ✅ Solução Implementada: Dimensão Mestre
    
    **Campo criado:** `MunicipioOficial`  
    **Inconsistências corrigidas:** {incons:,} municípios  
    **Taxa de inconsistência:** {taxa:.2f}%
    
    **Regras de Governança:**
    1. Nome que aparece em mais anos (maior frequência temporal)
    2. Em caso de empate: nome do ano mais recente
    3. Em caso de empate: ordem alfabética
    
    **Como funciona:**
    - Todos os gráficos usam o campo `MunicipioOficial`
    - O `CodigoIBGE` é a chave primária única
    - Garante consistência em todas as agregações
    - Elimina duplicidade em relatórios
    """)
    
    st.info("""
    **💡 Exemplo Prático:**
    
    ❌ **SEM Dimensão Mestre:**
```python
    df.groupby('Municipio')['VendasTon'].sum()  # Pode duplicar!
```
    
    ✅ **COM Dimensão Mestre:**
```python
    df.groupby('MunicipioOficial')['VendasTon'].sum()  # Sem duplicidade!
```
    """)

st.markdown("---")
st.markdown("<p style='text-align:center;color:#666;'>Dashboard desenvolvido com Streamlit | Fonte: ANP</p>", 
            unsafe_allow_html=True)
