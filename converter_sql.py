import pandas as pd
import sqlite3
import re

# ============================================================
# CONFIGURAÇÃO
# ============================================================
ARQUIVO_EXCEL = "VALOR TOTAL DE FATURAMENTO APROVADO.xlsx"
BANCO_SQLITE  = "saude.db"

# ============================================================
# 1. LÊ A PLANILHA
# ============================================================
print("Lendo planilha...")
df = pd.read_excel(ARQUIVO_EXCEL, sheet_name="tabela")
print(f"  Shape original: {df.shape[0]} linhas x {df.shape[1]} colunas")

# ============================================================
# 2. IDENTIFICA OS 3 BLOCOS DE COLUNAS
#    [0-15]    Colunas fixas (totais, categorias, UTIs)
#    [16-7752] CIDs  (ex: "A00   Colera")
#    [7753+]   Procedimentos com valor (ex: "(VALOR)0101010010 ...")
# ============================================================
COLUNAS_FIXAS = [
    'MÊS/ANO', 'MÊS', 'ANO', 'VALOR TOTAL', 'QUANTIDADE FATURADA',
    'MEDIA', 'CIRURGICA', 'OBSTETRICA', 'CLINICA', 'PEDIATRICA',
    'HOSPITAL DIA', 'MASCULINO', 'FEMININO',
    'UTI ADULTO TIPO II', 'UTI NEO TIPO II', 'UTI COVID TIPO II'   # ← incluída!
]

colunas_fixas    = [c for c in COLUNAS_FIXAS if c in df.columns]
colunas_cid      = [c for c in df.columns if re.match(r'^[A-Z]\d{2}\s', str(c))]
colunas_proc     = [c for c in df.columns if re.match(r'^\(VALOR\)', str(c))]

print(f"  Colunas fixas      : {len(colunas_fixas)}")
print(f"  Colunas de CID     : {len(colunas_cid)}")
print(f"  Colunas de proc.   : {len(colunas_proc)}")

ID_COLS = ['MÊS/ANO', 'MÊS', 'ANO']

# ============================================================
# 3. TABELA DE TOTAIS/CATEGORIAS (colunas fixas)
#    Uma linha por mês — pequena e rápida de consultar
# ============================================================
print("\nSalvando tabela de totais mensais...")
df_totais = df[colunas_fixas].copy()
df_totais.rename(columns={'MÊS/ANO': 'MES_ANO', 'MÊS': 'MES'}, inplace=True)

# ============================================================
# 4. TABELA DE CIDs (formato longo)
#    Extrai código e descrição do nome da coluna
#    Exemplo: "A00   Colera" → cid=A00, descricao=Colera
# ============================================================
print("Convertendo CIDs para formato longo (melt)...")

df_cid_wide = df[ID_COLS + colunas_cid].copy()

df_cid_long = df_cid_wide.melt(
    id_vars=ID_COLS,
    var_name='coluna_original',
    value_name='quantidade'
)

# Remove zeros e nulos
df_cid_long = df_cid_long[df_cid_long['quantidade'].notna() & (df_cid_long['quantidade'] != 0)]

def extrair_cid_codigo(col):
    match = re.match(r'^([A-Z]\d{2})\s+', str(col))
    return match.group(1) if match else col

def extrair_cid_descricao(col):
    match = re.match(r'^[A-Z]\d{2}\s+(.*)', str(col))
    return match.group(1).strip() if match else col

df_cid_long['cid']      = df_cid_long['coluna_original'].apply(extrair_cid_codigo)
df_cid_long['descricao'] = df_cid_long['coluna_original'].apply(extrair_cid_descricao)
df_cid_long.rename(columns={'MÊS/ANO': 'MES_ANO', 'MÊS': 'MES'}, inplace=True)
df_cid_long = df_cid_long[['MES_ANO', 'MES', 'ANO', 'cid', 'descricao', 'quantidade']]

print(f"  Total de registros CID (sem zeros): {len(df_cid_long):,}")

# ============================================================
# 5. TABELA DE PROCEDIMENTOS (formato longo)
#    Cada procedimento tem duas colunas na planilha:
#      "0101010010 DESCRICAO..."         → quantidade faturada
#      "(VALOR)0101010010 DESCRICAO..."  → valor aprovado
#    O melt é feito separado e depois junta pelos ids + código
# ============================================================
print("Convertendo procedimentos para formato longo (melt)...")

colunas_qtd  = [c for c in df.columns if re.match(r'^\d{10}', str(c))]
colunas_val  = [c for c in df.columns if re.match(r'^\(VALOR\)', str(c))]

def extrair_proc_codigo(col):
    match = re.search(r'(\d{10})', str(col))
    return match.group(1) if match else None

def extrair_proc_descricao(col):
    match = re.search(r'\d{10}\s+(.*)', str(col))
    return match.group(1).strip() if match else col

# Melt das quantidades
df_qtd = df[ID_COLS + colunas_qtd].melt(
    id_vars=ID_COLS, var_name='coluna_original', value_name='quantidade'
)
df_qtd['codigo_procedimento'] = df_qtd['coluna_original'].apply(extrair_proc_codigo)
df_qtd['descricao']           = df_qtd['coluna_original'].apply(extrair_proc_descricao)
df_qtd = df_qtd.drop(columns=['coluna_original'])

# Melt dos valores
df_val = df[ID_COLS + colunas_val].melt(
    id_vars=ID_COLS, var_name='coluna_original', value_name='valor'
)
df_val['codigo_procedimento'] = df_val['coluna_original'].apply(extrair_proc_codigo)
df_val = df_val.drop(columns=['coluna_original', 'MÊS', 'ANO'])  # evita duplicar no merge

# Junta quantidade + valor numa só linha por procedimento/mês
df_proc_long = df_qtd.merge(df_val, on=['MÊS/ANO', 'codigo_procedimento'], how='left')

# Remove linhas onde quantidade E valor são zero/nulos
df_proc_long = df_proc_long[
    df_proc_long['quantidade'].notna() | df_proc_long['valor'].notna()
]
df_proc_long = df_proc_long[
    (df_proc_long['quantidade'].fillna(0) != 0) | (df_proc_long['valor'].fillna(0) != 0)
]

df_proc_long.rename(columns={'MÊS/ANO': 'MES_ANO', 'MÊS': 'MES'}, inplace=True)
df_proc_long = df_proc_long[['MES_ANO', 'MES', 'ANO', 'codigo_procedimento', 'descricao', 'quantidade', 'valor']]

print(f"  Total de registros procedimentos (sem zeros): {len(df_proc_long):,}")

# ============================================================
# 6. TABELAS DICIONÁRIO
# ============================================================
df_dict_proc = df_proc_long[['codigo_procedimento', 'descricao']].drop_duplicates(subset='codigo_procedimento')
df_dict_cid  = df_cid_long[['cid', 'descricao']].drop_duplicates(subset='cid')
print(f"  Procedimentos únicos: {len(df_dict_proc):,}")
print(f"  CIDs únicos         : {len(df_dict_cid):,}")

# ============================================================
# 7. SALVA NO SQLITE
# ============================================================
print(f"\nSalvando no banco '{BANCO_SQLITE}'...")
conn = sqlite3.connect(BANCO_SQLITE)

df_totais.to_sql('totais_mensais', conn, if_exists='replace', index=False)
print("  ✅ Tabela 'totais_mensais' salva")

df_cid_long[['MES_ANO', 'MES', 'ANO', 'cid', 'quantidade']].to_sql(
    'faturamento_cids', conn, if_exists='replace', index=False
)
print("  ✅ Tabela 'faturamento_cids' salva")

df_proc_long[['MES_ANO', 'MES', 'ANO', 'codigo_procedimento', 'quantidade', 'valor']].to_sql(
    'faturamento_procedimentos', conn, if_exists='replace', index=False
)
print("  ✅ Tabela 'faturamento_procedimentos' salva")

df_dict_proc.to_sql('procedimentos', conn, if_exists='replace', index=False)
print("  ✅ Tabela 'procedimentos' (dicionário) salva")

df_dict_cid.to_sql('cids', conn, if_exists='replace', index=False)
print("  ✅ Tabela 'cids' (dicionário) salva")

# ============================================================
# 8. CRIA ÍNDICES PARA PERFORMANCE
# ============================================================
print("\nCriando índices...")
conn.execute("CREATE INDEX IF NOT EXISTS idx_fat_codigo  ON faturamento_procedimentos(codigo_procedimento)")
conn.execute("CREATE INDEX IF NOT EXISTS idx_fat_ano     ON faturamento_procedimentos(ANO)")
conn.execute("CREATE INDEX IF NOT EXISTS idx_fat_mesano  ON faturamento_procedimentos(MES_ANO)")
conn.execute("CREATE INDEX IF NOT EXISTS idx_cid_cod     ON faturamento_cids(cid)")
conn.execute("CREATE INDEX IF NOT EXISTS idx_cid_ano     ON faturamento_cids(ANO)")
conn.commit()
conn.close()
print("  ✅ Índices criados")

# ============================================================
# 9. RESUMO FINAL
# ============================================================
print("\n" + "="*50)
print("BANCO CRIADO COM SUCESSO!")
print("="*50)
print(f"Arquivo: {BANCO_SQLITE}")
print("\nTabelas disponíveis:")
print("  • totais_mensais            → valor total, qtd, média, clínica, cirúrgica, UTI COVID...")
print("  • faturamento_cids          → mês/ano, CID, quantidade (formato longo)")
print("  • faturamento_procedimentos → mês/ano, código, valor (formato longo)")
print("  • cids                      → dicionário CID → descrição")
print("  • procedimentos             → dicionário código → descrição")
print("\nExemplos de consulta no Streamlit:")
print("""
  # Total por mês
  SELECT MES_ANO, "VALOR TOTAL" FROM totais_mensais ORDER BY ANO, MES

  # Top 10 CIDs em 2024
  SELECT c.descricao, SUM(f.quantidade) as total
  FROM faturamento_cids f
  JOIN cids c ON f.cid = c.cid
  WHERE f.ANO = 2024
  GROUP BY f.cid ORDER BY total DESC LIMIT 10

  # Top 10 procedimentos em 2024
  SELECT p.descricao, SUM(f.valor) as total
  FROM faturamento_procedimentos f
  JOIN procedimentos p ON f.codigo_procedimento = p.codigo_procedimento
  WHERE f.ANO = 2024
  GROUP BY f.codigo_procedimento
  ORDER BY total DESC LIMIT 10

  # Evolução UTI COVID por mês
  SELECT MES_ANO, "UTI COVID TIPO II" FROM totais_mensais ORDER BY ANO, MES
""")