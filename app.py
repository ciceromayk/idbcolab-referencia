import datetime
import pandas as pd
import plotly.express as px
import streamlit as st

def calcular_cronograma_macro(data_lancamento: datetime.date, additional_info: dict = None) -> tuple:
offsets = {
"CONCEPÇÃO DO PRODUTO": (0, 180),
"INCORPORAÇÃO": (180, 420),
"ANTEPROJETOS": (240, 390),
"PROJETOS EXECUTIVOS": (330, 660),
"ORÇAMENTO": (390, 690),
"PLANEJAMENTO": (435, 720),
"LANÇAMENTO": (240, 540),
"PRÉ-OBRA": (420, 720),
}
day_zero = data_lancamento - datetime.timedelta(days=offsets["LANÇAMENTO"][1])
records = []
for tarefa, (i0, i1) in offsets.items():
    start = day_zero + datetime.timedelta(days=i0)
    end = day_zero + datetime.timedelta(days=i1)
    record = {"Tarefa": tarefa.upper(), "Início": start, "Término": end}
    if additional_info and tarefa.upper() in additional_info:
        record.update(additional_info[tarefa.upper()])
    else:
        record.update({"Responsável": "N/A", "Status": "Pendente", "Notas": ""})
    records.append(record)

tarefas_ordenadas = [
    "CONCEPÇÃO DO PRODUTO",
    "INCORPORAÇÃO",
    "ANTEPROJETOS",
    "PROJETOS EXECUTIVOS",
    "ORÇAMENTO",
    "PLANEJAMENTO",
    "LANÇAMENTO",
    "PRÉ-OBRA"
]

df = pd.DataFrame(records)
df["Início"] = pd.to_datetime(df["Início"])
df["Término"] = pd.to_datetime(df["Término"])
df["Tarefa"] = pd.Categorical(df["Tarefa"], categories=tarefas_ordenadas, ordered=True)
df = df.sort_values("Tarefa").reset_index(drop=True)

return df, day_zero

def criar_grafico_macro(df: pd.DataFrame, data_lanc: datetime.date, color_sequence=None) -> px.timeline:
hoje = datetime.date.today()
lancamento = data_lanc
inicio_projeto = df["Início"].min()
max_date = df["Término"].max()

# Define o fim do período ao final do último Término + um mês
if max_date.day != 1:
    next_month = (max_date.replace(day=1) + pd.Timedelta(days=32)).replace(day=1)
else:
    next_month = max_date
total_months = (next_month.year - inicio_projeto.year) * 12 + (next_month.month - inicio_projeto.month) + 1
end_period = (inicio_projeto + pd.DateOffset(months=total_months))

# Montar lista de ticks para cada mês com datas no formato MMM-YY
tickvals = []
ticktext = []
current_month = inicio_projeto.replace(day=1)
for i in range(total_months):
    tickvals.append(current_month)
    ticktext.append(current_month.strftime("%b-%y"))  # formato MMM-YY
    year = current_month.year + (current_month.month // 12)
    month = (current_month.month % 12) + 1
    current_month = current_month.replace(year=year, month=month)

# Criar gráfico
fig = px.timeline(
    df,
    x_start="Início",
    x_end="Término",
    y="Tarefa",
    color="Tarefa",
    height=650,
    color_discrete_sequence=color_sequence,
    hover_data=["Responsável", "Status", "Notas"]
)

# Marcos
fig.add_shape(
    type="line",
    x0=inicio_projeto,
    x1=inicio_projeto,
    y0=0,
    y1=1,
    xref="x",
    yref="paper",
    line=dict(color="green", width=2, dash="dot"),
)
fig.add_annotation(
    x=inicio_projeto,
    y=1,
    xref="x",
    yref="paper",
    text="INÍCIO DO PROJETO",
    font=dict(color="green", size=12),
    showarrow=False,
    xanchor="center",
    yanchor="bottom"
)

fig.add_shape(
    type="line",
    x0=hoje,
    x1=hoje,
    y0=0,
    y1=1,
    xref="x",
    yref="paper",
    line=dict(color="red", width=2, dash="dot"),
)
fig.add_annotation(
    x=hoje,
    y=1,
    xref="x",
    yref="paper",
    text="HOJE",
    font=dict(color="red", size=12),
    showarrow=False,
    xanchor="center",
    yanchor="bottom"
)

# Lançamento
fig.add_shape(
    type="line",
    x0=lancamento,
    x1=lancamento,
    y0=0,
    y1=1,
    xref="x",
    yref="paper",
    line=dict(color="blue", width=2, dash="dot"),
)
fig.add_annotation(
    x=lancamento,
    y=1,
    xref="x",
    yref="paper",
    text="LANÇAMENTO",
    font=dict(color="blue", size=12),
    showarrow=False,
    xanchor="center",
    yanchor="bottom"
)

# Início de obras
inicio_obras = lancamento + datetime.timedelta(days=120)
fig.add_shape(
    type="line",
    x0=inicio_obras,
    x1=inicio_obras,
    y0=0,
    y1=1,
    xref="x",
    yref="paper",
    line=dict(color="purple", width=2, dash="dot"),
)
fig.add_annotation(
    x=inicio_obras,
    y=1,
    xref="x",
    yref="paper",
    text="INÍCIO DE OBRAS",
    font=dict(color="purple", size=12),
    showarrow=False,
    xanchor="center",
    yanchor="bottom"
)

# Configuração eixo x
fig.update_xaxes(
    tickvals=tickvals,
    ticktext=ticktext,
    range=[inicio_projeto, end_period],
    showgrid=True,
    gridcolor="lightgray",
    dtick="M1"
)

# Grade horizontal
fig.update_yaxes(
    showgrid=True,
    gridcolor="lightgray",
    title_text=None,
    title_font={'size': 16}
)

# Linhas fundo alternadas
n = len(df)
for i in range(n):
    if i % 2 == 0:
        y0 = 1 - (i + 1) / n
        y1 = 1 - i / n
        fig.add_shape(
            type="rect",
            xref="paper",
            yref="paper",
            x0=0,
            x1=1,
            y0=y0,
            y1=y1,
            fillcolor="lightgray",
            opacity=0.2,
            line_width=0,
            layer="below"
        )

# Datas deslocadas para fora
deslocamento = pd.Timedelta(days=3)
annotations = []
for _, row in df.iterrows():
    ini = row["Início"]
    ter = row["Término"]
    if pd.notnull(ini):
        annotations.append(dict(
            x=ini - deslocamento,
            y=row["Tarefa"],
            text=f"<b>{ini:%d-%m-%Y}</b>",
            showarrow=False,
            font=dict(color="black", size=12),
            xanchor="right",
            yanchor="middle"
        ))
    if pd.notnull(ter):
        annotations.append(dict(
            x=ter + deslocamento,
            y=row["Tarefa"],
            text=f"<b>{ter:%d-%m-%Y}</b>",
            showarrow=False,
            font=dict(color="black", size=12),
            xanchor="left",
            yanchor="middle"
        ))

# Layout
fig.update_layout(
    annotations=annotations,
    margin=dict(l=250, r=40, t=20, b=40),
    showlegend=False
)

return fig
