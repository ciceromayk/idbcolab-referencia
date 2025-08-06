import streamlit as st
import pandas as pd
from datetime import timedelta, datetime
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode
from io import BytesIO
from tinydb import TinyDB, Query
import io

# Inicializa o banco de dados do TinyDB
db = TinyDB('cronogramas_db.json')
Cronograma = Query()

# Configuração da página
st.set_page_config(page_title="Editor de Cronograma", layout="wide")
st.title("Editor de Cronograma Interativo")

# ----------------------------------------------------------------
# Sidebar: Carregar cronograma salvo (se houver)
st.sidebar.header("Carregar Cronograma")
saved_records = db.all()
nomes_salvos = [record['nome'] for record in saved_records]
cronograma_selecionado = st.sidebar.selectbox("Selecione um cronograma salvo:", [""] + nomes_salvos)

if cronograma_selecionado != "":
    record = db.get(Cronograma.nome == cronograma_selecionado)
    df = pd.DataFrame(record["dados"])
    df["Início"] = pd.to_datetime(df["Início"])
else:
    # Dados iniciais caso nenhum cronograma salvo seja selecionado
    dados_iniciais = {
        "Tarefa": ["Projeto Executivo", "Licenciamento", "Obra"],
        "Início": ["2024-07-01", "2024-07-15", "2024-08-01"],
        "Duração (dias)": [14, 10, 60],
        "Responsável": ["Engenharia", "Ambiental", "Construtora"]
    }
    df = pd.DataFrame(dados_iniciais)
    df["Início"] = pd.to_datetime(df["Início"])

# ----------------------------------------------------------------
# Lista de responsáveis (pode ser expandida ou vinda de uma fonte externa)
lista_responsaveis = ["Engenharia", "Ambiental", "Financeiro", "Jurídico", "Construtora", "Cliente"]

# Configuração da AgGrid para edição do cronograma
gb = GridOptionsBuilder.from_dataframe(df)
gb.configure_default_column(editable=True, resizable=True)
# Configurar coluna "Início" para exibir data no formato "yyyy-MM-dd"
gb.configure_column(
    "Início", 
    type=["dateColumnFilter", "customDateTimeFormat"], 
    custom_format_string="yyyy-MM-dd", 
    editable=True
)
# Configurar coluna "Responsável" como lista suspensa (combo box)
gb.configure_column(
    "Responsável", 
    editable=True, 
    cellEditor="agSelectCellEditor", 
    cellEditorParams={"values": lista_responsaveis}
)
grid_options = gb.build()

st.subheader("Edite o cronograma aqui:")
grid_response = AgGrid(
    df,
    gridOptions=grid_options,
    update_mode=GridUpdateMode.MODEL_CHANGED,
    allow_unsafe_jscode=True,
    enable_enterprise_modules=False,
    fit_columns_on_grid_load=True,
    height=300,
    key='cronograma_tabela'
)

# Obter os dados editados
df_editado = pd.DataFrame(grid_response["data"])
df_editado["Início"] = pd.to_datetime(df_editado["Início"], errors="coerce")
df_editado["Término"] = df_editado["Início"] + pd.to_timedelta(df_editado["Duração (dias)"], unit="D")

st.markdown("---")
st.subheader("Cronograma Final:")
st.dataframe(df_editado, use_container_width=True)

# ----------------------------------------------------------------
# Seção para salvar o cronograma (versões)
st.subheader("Salvar Cronograma")
nome_novo = st.text_input("Nome desta versão do cronograma:")
if st.button("Salvar versão"):
    if nome_novo.strip():
        df_to_save = df_editado.copy()
        # Converter as datas para string para salvar no banco de dados
        df_to_save["Início"] = df_to_save["Início"].dt.strftime("%Y-%m-%d")
        df_to_save["Término"] = df_to_save["Término"].dt.strftime("%Y-%m-%d")
        if db.contains(Cronograma.nome == nome_novo):
            db.update({"dados": df_to_save.to_dict(orient="records")}, Cronograma.nome == nome_novo)
            st.success(f"Cronograma '{nome_novo}' atualizado com sucesso!")
        else:
            db.insert({"nome": nome_novo, "dados": df_to_save.to_dict(orient="records")})
            st.success(f"Cronograma '{nome_novo}' salvo com sucesso!")
    else:
        st.error("Digite um nome para salvar o cronograma.")

# ----------------------------------------------------------------
# Função para gerar o arquivo Excel para download
def gerar_download_excel(dataframe):
    output = BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        dataframe.to_excel(writer, index=False, sheet_name="Cronograma")
    return output.getvalue()

excel_data = gerar_download_excel(df_editado)
st.download_button(
    label="Baixar Cronograma em Excel",
    data=excel_data,
    file_name="cronograma.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)

# ----------------------------------------------------------------
# Seção para gerenciar (excluir) cronogramas salvos
with st.expander("Gerenciar Cronogramas Salvos"):
    if nomes_salvos:
        nome_para_deletar = st.selectbox("Selecione um cronograma para excluir:", nomes_salvos)
        if st.button("Excluir Cronograma"):
            db.remove(Cronograma.nome == nome_para_deletar)
            st.success(f"Cronograma '{nome_para_deletar}' removido com sucesso!")
            st.experimental_rerun()
    else:
        st.info("Nenhum cronograma salvo.")
