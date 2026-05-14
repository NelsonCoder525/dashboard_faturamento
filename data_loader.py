import sqlite3
import pandas as pd
import streamlit as st

BANCO = "saude.db"

def get_conn():
    return sqlite3.connect(BANCO)

# ============================================================
# TOTAIS MENSAIS
# Colunas: MES_ANO, MES, ANO, VALOR TOTAL, QUANTIDADE FATURADA,
#          MEDIA, CIRURGICA, OBSTETRICA, CLINICA, PEDIATRICA,
#          HOSPITAL DIA, MASCULINO, FEMININO,
#          UTI ADULTO TIPO II, UTI NEO TIPO II, UTI COVID TIPO II
# ============================================================
@st.cache_data
def carregar_totais_mensais():
    conn = get_conn()
    df = pd.read_sql(
        """
        SELECT * FROM totais_mensais
        ORDER BY ANO, CAST(substr(MES_ANO, 1, instr(MES_ANO, '/') - 1) AS INTEGER)
        """,
        conn
    )
    conn.close()
    return df

@st.cache_data
def carregar_procedimentos():
    conn = get_conn()
    df = pd.read_sql(
        """
        SELECT f.MES_ANO, f.MES, f.ANO,
               f.codigo_procedimento, p.descricao,
               f.quantidade, f.valor
        FROM faturamento_procedimentos f
        LEFT JOIN procedimentos p ON f.codigo_procedimento = p.codigo_procedimento
        ORDER BY f.ANO, CAST(substr(f.MES_ANO, 1, instr(f.MES_ANO, '/') - 1) AS INTEGER)
        """,
        conn
    )
    conn.close()
    return df
 
 
@st.cache_data
def carregar_cids():
    conn = get_conn()
    df = pd.read_sql(
        """
        SELECT f.MES_ANO, f.MES, f.ANO,
               f.cid, c.descricao, f.quantidade
        FROM faturamento_cids f
        LEFT JOIN cids c ON f.cid = c.cid
        ORDER BY f.ANO, CAST(substr(f.MES_ANO, 1, instr(f.MES_ANO, '/') - 1) AS INTEGER)
        """,
        conn
    )
    conn.close()
    return df

