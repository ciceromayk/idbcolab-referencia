import streamlit as st
import pandas as pd
from datetime import timedelta
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode
from io import BytesIO

Configuração da página
st.set_page_config(page_title="Editor de Cronograma", layout="wide")
st.title("📋 Editor de Cronograma Interativo")

🎯 Dados iniciais do cronograma
dados_iniciais = {
"Tarefa": ["Projeto Executivo", "Licenciamento", "Obra"],
"Início": ["2024-07-01", "2024-07-15", "2024-08-01"],
"Duração (dias)": [14, 10, 60],
"Responsável": ["Engenharia", "Ambiental", "Construtora"]
}

df = pd.DataFrame(dados_iniciais)
df["Início"] = pd.to_datetime(df["Início"])

Sugestões de responsáveis (poderia vir de um banco de dados futuramente)
lista_responsaveis = ["Engenharia", "Ambiental", "Financeiro", "Jurídico", "Construtora", "Cliente"]

🔧 Configurando a tabela com AgGrid
gb = GridOptionsBuilder.from_dataframe(df)
gb.configure_default_column(editable=True, resizable=True)

Coluna de data
gb.configure_column("Início", type=["dateColumnFilter","customDateTimeFormat"], custom_format_string="yyyy-MM-dd", editable=True)

Combo de responsáveis
gb.configure_column("Responsável", editable=True, cellEditor="agSelectCellEditor", cellEditorParams={"values": lista_responsaveis})

grid_options = gb.build()

✅ Tabela interativa
st.subheader("📝 Edite o cronograma aqui:")
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

df_editado = pd.DataFrame(grid_response["data"])
df_editado["Início"] = pd.to_datetime(df_editado["Início"], errors='coerce')

🧮 Cálculo da data de término
df_editado["Término"] = df_editado["Início"] + pd.to_timedelta(df_editado["Duração (dias)"], unit="D")

✅ Visualização final
st.markdown("---")
st.subheader("📅 Cronograma Final:")

st.dataframe(df_editado, use_container_width=True)

📤 Exportar para Excel
def gerar_download_excel(df):
output = BytesIO()
with pd.ExcelWriter(output, engine="openpyxl") as writer:
df.to_excel(writer, index=False, sheet_name="Cronograma")
processed_data = output.getvalue()
return processed_data

excel_data = gerar_download_excel(df_editado)

st.download_button(
label="⬇️ Baixar Cronograma em Excel",
data=excel_data,
file_name="cronograma.xlsx",
mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)
