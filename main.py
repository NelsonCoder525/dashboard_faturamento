import streamlit as st
import pandas as pd
from data_loader import carregar_totais_mensais, carregar_procedimentos, carregar_cids
import plotly.express as px
import plotly.graph_objects as go



st.set_page_config(layout="wide", initial_sidebar_state="expanded")
st.markdown("""
    <style>
        [data-testid="stMain"] {
    background: linear-gradient(135deg, #2E5ED4, #191970) !important;
}
        [data-testid="stVerticalBlock"] {
    border: none !important;
    box-shadow: none !important;
} 
/* Remove margens/padding do topo da página */
        .stAppViewContainer {
            padding-top: 0 !important;
        }
        .block-container {
            padding-top: 0 !important;
            padding-left: 1rem !important;
        }
        
    [data-testid="stHeader"] {
    background: transparent;
}


[data-testid="stMultiSelect"] * {
    max-height: none !important;
    overflow: visible !important;
}
[data-testid="stSidebar"] {
    background: rgba(100, 149, 237, 0.15) !important;
}
        
    
    </style>
""", unsafe_allow_html=True)

def filtros_sidebar(ano, mes, df):
    df_filtrada = df[(df["ANO"] == ano) & (df["MES"].isin(mes))]
    return df_filtrada
    

df_valor_total = carregar_totais_mensais()
df_proc   = carregar_procedimentos()
df_cids   = carregar_cids()
df_valor_total["VALOR TOTAL"] = df_valor_total["VALOR TOTAL"].round(2)
df_valor_total["VALOR TOTAL"] = df_valor_total["VALOR TOTAL"].round(2)
df_valor_total["MEDIA"] = df_valor_total["MEDIA"].round(2)
df_valor_total["UTI ADULTO TIPO II"] = df_valor_total["UTI ADULTO TIPO II"].round(2)
df_valor_total["UTI NEO TIPO II"] = df_valor_total["UTI NEO TIPO II"].round(2)
df_valor_total["UTI COVID TIPO II"] = df_valor_total["UTI COVID TIPO II"].round(2)

def criar_card(icone, numero, texto, coluna_card, tamanho_icone):
    container = coluna_card.container(border=True)
    coluna_esquerda, coluna_direita = container.columns([1, 2.5])
    with coluna_esquerda:
        st.markdown("<div style='margin-top:18px;'>", unsafe_allow_html=True)
        st.image(f"imagens/{icone}", width=tamanho_icone)
        st.markdown("</div>", unsafe_allow_html=True)
    coluna_direita.metric(label=texto, value=numero)


with st.sidebar:
    st.title("Filtros")
    ano_filtro = st.sidebar.number_input(
    "Digite o ano", 
    min_value=2017, max_value=2026, value=2017, step=1
    )
    mes_filtro = st.sidebar.multiselect(
    "Selecione o mês", options=df_valor_total["MES"].unique(), default=df_valor_total["MES"].unique()
    )
    
    
    
    
    
cabecalho = st.container()
cabecalho.title("HOSPITAL REGIONAL JORGE ROSSMANN - FATURAMENTO SUS")
coluna1, coluna2, coluna3 = cabecalho.columns([1,1,1])


df = filtros_sidebar(ano_filtro, mes_filtro, df_valor_total)
criar_card("calc.png", f"{df['QUANTIDADE FATURADA'].sum():,.0f}", "AIH'S FATURADAS NO PERÍODO", coluna1, 70)
criar_card("saco.png", f"R${df['VALOR TOTAL'].sum():,.2f}", "VALOR TOTAL FATURADO NO PERÍODO", coluna2, 95)
criar_card("moeda.png", f"R${(df['VALOR TOTAL'].sum()/df['QUANTIDADE FATURADA'].sum()):,.2f}", "VALOR MÉDIO POR AIH NO PERÍODO", coluna3, 225)


corpo = st.container()
coluna1, coluna2, coluna3, coluna4 = corpo.columns([1,1,1,1], )

colunas = [coluna1, coluna2, coluna3, coluna4]
containers = {}
for i, coluna in enumerate(colunas):
    container_superior = coluna.container(height = 450)
    container_inferior = coluna.container(height = 450)
    containers[f"coluna{i+1}"] = {"superior": container_superior, "inferior": container_inferior}


with containers["coluna1"]["superior"]:
        
    df_filtrado = filtros_sidebar(ano_filtro, mes_filtro, df_valor_total)
    fig = px.bar(df_filtrado, x="MES", y="VALOR TOTAL", title = "VALOR TOTAL POR MÊS EM R$", color_discrete_sequence=["#40E0D0"], width=500, height=380, text="VALOR TOTAL", range_y = [0, df_filtrado["VALOR TOTAL"].max() * 1.1])
    fig.update_traces(texttemplate="%{y:,.2f}", textposition="inside", textfont_size=20, textfont_color="white", textangle=90)
    fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
    fig.update_layout(xaxis=dict(showgrid=False), yaxis=dict(showgrid=False), xaxis_title=None, yaxis_title=None)
    fig.update_layout(title=dict(x=0.5, xanchor="center"))
    st.plotly_chart(fig)

with containers["coluna2"]["superior"]:
    
    df_filtrado = filtros_sidebar(ano_filtro, mes_filtro, df_valor_total)
    fig = px.line(df_filtrado, x="MES", y="QUANTIDADE FATURADA", title = "QUANTIDADE FATURADA POR MÊS", color_discrete_sequence=["#F2F8F4"],width=500, height=380, markers = True, range_y = [300, df_filtrado["QUANTIDADE FATURADA"].max() * 1.1], text = "QUANTIDADE FATURADA")
    fig.update_traces(texttemplate="%{y:,.2f}",textposition="top center", textfont_size=10)
    fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
    fig.update_layout(xaxis=dict(showgrid=False), yaxis=dict(showgrid=False), xaxis_title=None, yaxis_title=None)
    fig.update_layout(title=dict(x=0.5, xanchor="center"))
    st.plotly_chart(fig)

with containers["coluna3"]["superior"]:
    
    df_filtrado = filtros_sidebar(ano_filtro, mes_filtro, df_valor_total)
    fig = px.bar(df_filtrado, y="MES", x="MEDIA", orientation = "h", title = "MÉDIA MENSAL POR AIH EM R$", color_discrete_sequence=["#C50DC5"],width=500, height=380, range_x = [100, df_filtrado["MEDIA"].max() * 1.2], text = "MEDIA")
    fig.update_traces(textposition="outside", textfont_size=12, width=0.7)
    fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
    fig.update_layout(xaxis=dict(showgrid=False), yaxis=dict(showgrid=False), xaxis_title=None, yaxis_title=None)
    fig.update_layout(title=dict(x=0.5, xanchor="center"))
    st.plotly_chart(fig)

with containers["coluna4"]["superior"]:
    
    df_filtrado = filtros_sidebar(ano_filtro, mes_filtro, df_valor_total)
    especialidades = ["CIRURGICA", "OBSTETRICA", "CLINICA", "PEDIATRICA", "HOSPITAL DIA"]
    df_especialidades = df_filtrado[especialidades].sum().reset_index()
    df_especialidades.columns = ["especialidade", "total"]

    fig = px.pie(df_especialidades, names="especialidade", values="total", hole = 0.80, title = "PARTICIPAÇÃO PERCENTUAL<br>POR ESPECIALIDADE", color_discrete_sequence=px.colors.qualitative.Set1, width=450, height=380)
    fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
    fig.update_traces(textfont_size=9, textfont_color="white")
    fig.update_layout(title=dict(x=0.5, xanchor="center"))
    st.plotly_chart(fig)
    

with containers["coluna1"]["inferior"]:
    
    df_filtrado = filtros_sidebar(ano_filtro, mes_filtro, df_valor_total)
    sexos = ["MASCULINO", "FEMININO"]
    df_sexos = df_filtrado[sexos].sum().reset_index()
    df_sexos.columns = ["sexo", "total"]

    fig = px.pie(df_sexos, names="sexo", values="total", hole = 0.80, title = "DISTRIBUIÇÃO PERCENTUAL<br>POR SEXO", color_discrete_sequence=px.colors.qualitative.Set2, width=450, height=380)
    fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
    fig.update_traces(textfont_size=9, textfont_color="white")
    fig.update_layout(title=dict(x=0.5, xanchor="center"))    
    st.plotly_chart(fig)
    
    
with containers["coluna2"]["inferior"]:
        
    df_filtrado = filtros_sidebar(ano_filtro, mes_filtro, df_valor_total)
    fig = px.bar(df_filtrado, x="MES", y="UTI ADULTO TIPO II", title = "DIÁRIAS DE UTI ADULTO EM R$", color_discrete_sequence=["#AA0909"], width=500, height=380, text="UTI ADULTO TIPO II", range_y = [0, df_filtrado["UTI ADULTO TIPO II"].max() * 1.1])
    fig.update_traces(texttemplate="%{y:,.2f}", textposition="inside", textfont_size=20, textfont_color="white", textangle=90)
    fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
    fig.update_layout(xaxis=dict(showgrid=False), yaxis=dict(showgrid=False), xaxis_title=None, yaxis_title=None)
    fig.update_layout(title=dict(x=0.5, xanchor="center"))
    st.plotly_chart(fig)   
    
    
with containers["coluna3"]["inferior"]:
        
    df_filtrado = filtros_sidebar(ano_filtro, mes_filtro, df_valor_total)
    fig = px.bar(df_filtrado, x="MES", y="UTI NEO TIPO II", title = "DIÁRIAS DE UTI NEO EM R$", color_discrete_sequence=["#ECE91D"], width=500, height=380, text="UTI NEO TIPO II", range_y = [0, df_filtrado["UTI NEO TIPO II"].max() * 1.1])
    fig.update_traces(texttemplate="%{y:,.2f}", textposition="inside", textfont_size=20, textfont_color="black", textangle=90)
    fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
    fig.update_layout(xaxis=dict(showgrid=False), yaxis=dict(showgrid=False), xaxis_title=None, yaxis_title=None)
    fig.update_layout(title=dict(x=0.5, xanchor="center"))
    st.plotly_chart(fig)      
    
    
with containers["coluna4"]["inferior"]:
        
    df_filtrado = filtros_sidebar(ano_filtro, mes_filtro, df_valor_total)
    fig = px.bar(df_filtrado, x="MES", y="UTI COVID TIPO II", title = "DIÁRIAS DE UTI COVID EM R$", color_discrete_sequence=["#7FB2BE"], width=500, height=380, text="UTI COVID TIPO II", range_y = [0, df_filtrado["UTI COVID TIPO II"].max() * 1.1])
    fig.update_traces(texttemplate="%{y:,.2f}",textposition="inside", textfont_size=20, textfont_color="white", textangle=90)
    fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
    fig.update_layout(xaxis=dict(showgrid=False), yaxis=dict(showgrid=False), xaxis_title=None, yaxis_title=None)
    fig.update_layout(title=dict(x=0.5, xanchor="center"))
    st.plotly_chart(fig)        
    
    
### GRÁFICOS DE CIDs E PROCEDIMENTOS (TOP 10) - FUNIS
rodape = st.container()

coluna_rodape1, coluna_rodape2 = rodape.columns([1.5,1.5])
with coluna_rodape1:
    
    df_filtrado = filtros_sidebar(ano_filtro, mes_filtro, df_cids)
    df_filtrado["cid_descricao"] = df_filtrado["cid"] + " - " + df_filtrado["descricao"]
    top_cids = df_filtrado.groupby("cid_descricao")["quantidade"].sum().reset_index().sort_values(by="quantidade", ascending=False).head(10)
    
    
    fig = px.funnel(top_cids, x="quantidade", y="cid_descricao", title = "TOP 10 CID'S (POR CATEGORIA)", color_discrete_sequence=px.colors.qualitative.Set3, width=500, height=380)
    fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
    fig.update_layout(xaxis=dict(showgrid=False), yaxis=dict(showgrid=False), xaxis_title=None, yaxis_title=None)
    fig.update_layout(title=dict(x=0.5, xanchor="center"))
    st.plotly_chart(fig)
    
with coluna_rodape2:
    
    df_filtrado = filtros_sidebar(ano_filtro, mes_filtro, df_proc)
    df_filtrado["proc_descricao"] = df_filtrado["codigo_procedimento"] + " - " + df_filtrado["descricao"]
    top_proc = df_filtrado.groupby("proc_descricao")["quantidade"].sum().reset_index().sort_values(by="quantidade", ascending=False).head(10)
    

    
    cores = px.colors.qualitative.Dark24
    fig = go.Funnel(
    y=top_proc["proc_descricao"],
    x=top_proc["quantidade"],
    textinfo="value",
    marker={"color": cores[:len(top_proc)]}
)
    fig = go.Figure(fig)

    
    fig.update_layout(
    title="TOP 10 PROCEDIMENTOS DE MAIOR FREQUENCIA",
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    showlegend=False,
    width=400,
    height=380,
    yaxis=dict(tickfont=dict(size=10))
)
    st.plotly_chart(fig)
    

with rodape:
    df_filtrado = filtros_sidebar(ano_filtro, mes_filtro, df_proc)
    df_filtrado["proc_descricao"] = df_filtrado["codigo_procedimento"] + " - " + df_filtrado["descricao"]
    top_proc = df_filtrado.groupby("proc_descricao")["valor"].sum().reset_index().sort_values(by="valor", ascending=False).head(10)
    
    top_proc["valor"] = top_proc["valor"].round(2)

    cores = px.colors.qualitative.Dark24
    fig = go.Funnel(
    y=top_proc["proc_descricao"],
    x=top_proc["valor"],
    textinfo="value",
    marker={"color": cores[:len(top_proc)]}
)
    fig = go.Figure(fig)

    
    fig.update_layout(
    title="TOP 10 PROCEDIMENTOS DE MAIOR VALOR TOTAL EM R$",
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    showlegend=False,
    width=450,
    height=380
)
    st.plotly_chart(fig)

with rodape:
    df_filtrado = filtros_sidebar(ano_filtro, mes_filtro, df_proc)
    df_filtrado["proc_descricao"] = df_filtrado["codigo_procedimento"] + " - " + df_filtrado["descricao"]
    
    
    df_filtrado = df_filtrado.dropna()
    df_filtrado = df_filtrado[df_filtrado["quantidade"] > 0]
    
    
    top_proc = df_filtrado.groupby("proc_descricao").agg(valor=("valor", "sum"), quantidade=("quantidade", "sum")).reset_index()

    top_proc["media"] = (top_proc["valor"] / top_proc["quantidade"]).round(2)
    top_proc = top_proc.sort_values(by="media", ascending=False).head(10)
       
    cores = px.colors.qualitative.Dark24
    fig = go.Funnel(
    y=top_proc["proc_descricao"],
    x=top_proc["media"],
    textinfo="value",
    marker={"color": cores[:len(top_proc)]}
)
    fig = go.Figure(fig)

    
    fig.update_layout(
    title="TOP 10 PROCEDIMENTOS DE MAIOR VALOR MÉDIO EM R$",
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    showlegend=False,
    width=450,
    height=380
)
    st.plotly_chart(fig)





    st.markdown("**Fonte:** DATASUS **(https://datasus.saude.gov.br/)**")    