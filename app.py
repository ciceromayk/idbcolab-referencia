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
    inicio_obras = lancamento + datetime.timedelta(days=120)

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

    # ---- MARCOS ----
    fig.add_shape(
        type="line", x0=inicio_projeto, x1=inicio_projeto,
        y0=0, y1=1, xref="x", yref="paper",
        line=dict(color="green", width=2, dash="dot"),
    )
    fig.add_annotation(
        x=inicio_projeto, y=1,
        xref="x", yref="paper",
        text="INÍCIO DO PROJETO",
        font=dict(color="green", size=12),
        showarrow=False,
        xanchor="center", yanchor="bottom"
    )

    fig.add_shape(
        type="line", x0=hoje, x1=hoje,
        y0=0, y1=1, xref="x", yref="paper",
        line=dict(color="red", width=2, dash="dot"),
    )
    fig.add_annotation(
        x=hoje, y=1,
        xref="x", yref="paper",
        text="HOJE",
        font=dict(color="red", size=12),
        showarrow=False,
        xanchor="center", yanchor="bottom"
    )

    fig.add_shape(
        type="line", x0=lancamento, x1=lancamento,
        y0=0, y1=1, xref="x", yref="paper",
        line=dict(color="blue", width=2, dash="dot"),
    )
    fig.add_annotation(
        x=lancamento, y=1,
        xref="x", yref="paper",
        text="LANÇAMENTO",
        font=dict(color="blue", size=12),
        showarrow=False,
        xanchor="center", yanchor="bottom"
    )

    fig.add_shape(
        type="line", x0=inicio_obras, x1=inicio_obras,
        y0=0, y1=1, xref="x", yref="paper",
        line=dict(color="purple", width=2, dash="dot"),
    )
    fig.add_annotation(
        x=inicio_obras, y=1,
        xref="x", yref="paper",
        text="INÍCIO DE OBRAS",
        font=dict(color="purple", size=12),
        showarrow=False,
        xanchor="center", yanchor="bottom"
    )

    # EIXO X: meses/ano + linha de grade vertical
    fig.update_xaxes(
        tickformat="%b/%Y",  # Ex: Jan/2025
        showgrid=True,
        gridcolor="lightgray",
    )

    # Eixo Y: título maior
    fig.update_yaxes(title_text=None, title_font={'size': 16})

    n = len(df)
    for i in range(n):
        if i % 2 == 0:
            y0 = 1 - (i + 1) / n
            y1 = 1 - i / n
            fig.add_shape(
                type="rect",
                xref="paper", yref="paper",
                x0=0, x1=1, y0=y0, y1=y1,
                fillcolor="lightgray", opacity=0.2,
                line_width=0, layer="below"
            )

    # Anotações: início à ESQUERDA, término à DIREITA, fora das barras, fonte 12pt
    deslocamento = pd.Timedelta(days=3)  # desloca data pra fora da barra
    annotations = []
    for _, row in df.iterrows():
        if pd.notnull(row["Início"]):
            annotations.append(dict(
                x=row["Início"] - deslocamento, y=row["Tarefa"],
                text=f"<b>{row['Início']:%d/%m/%Y}</b>",
                showarrow=False,
                font=dict(color="black", size=12),
                xanchor="right", yanchor="middle"
            ))
        if pd.notnull(row["Término"]):
            annotations.append(dict(
                x=row["Término"] + deslocamento, y=row["Tarefa"],
                text=f"<b>{row['Término']:%d/%m/%Y}</b>",
                showarrow=False,
                font=dict(color="black", size=12),
                xanchor="left", yanchor="middle"
            ))
    fig.update_layout(
        annotations=annotations,
        margin=dict(l=250, r=40, t=20, b=40),
        showlegend=False
    )

    return fig

def main():
    st.set_page_config(page_title="IDBCOLAB - COMITÊ DE PRODUTO", layout="wide")
    st.sidebar.image(
        "https://raw.githubusercontent.com/ciceromayk/idbcolab-referencia/main/LOGO%20IDBCOLAB.png",
        use_container_width=True
    )
    st.sidebar.markdown("## IDIBRA PARTICIPAÇÕES")
    nome = st.sidebar.text_input("📝 Nome do Projeto")
    data_lanc = st.sidebar.date_input("📅 LANÇAMENTO:", value=datetime.date.today(), format="DD/MM/YYYY")

    st.sidebar.markdown("## Opções de Personalização")
    color_palettes = {
        "Default": None,
        "Viridis": px.colors.sequential.Viridis,
        "Cividis": px.colors.sequential.Cividis,
        "Plotly": px.colors.qualitative.Plotly,
        "Dark2": px.colors.qualitative.Dark2
    }

    if "selected_palette" not in st.session_state:
        st.session_state.selected_palette = "Default"

    selected_palette = st.sidebar.selectbox("Selecione a paleta de cores", list(color_palettes.keys()))
    if selected_palette != st.session_state.selected_palette:
        st.session_state.selected_palette = selected_palette
        st.session_state.gerar_grafico = True

    color_sequence = color_palettes[st.session_state.selected_palette]
    gerar = st.sidebar.button("🚀 GERAR CRONOGRAMA")

    st.title("IDBCOLAB - COMITÊ DE PRODUTO")
    st.subheader("Cronograma do Projeto")

    if nome:
        st.markdown(f"**Projeto:** {nome.upper()}")

    if gerar or ("gerar_grafico" in st.session_state and st.session_state.gerar_grafico):
        df, day_zero = calcular_cronograma_macro(data_lanc)
        st.session_state.data_frame = df  

        hoje = datetime.date.today()
        lancamento = data_lanc
        inicio_projeto = df["Início"].min()
        inicio_obras = lancamento + datetime.timedelta(days=120)
        
        fig = criar_grafico_macro(df, data_lanc, color_sequence=color_sequence)
        st.plotly_chart(fig, use_container_width=True, config={"locale": "pt-BR"})

        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("**INÍCIO DO PROJETO**", inicio_projeto.strftime("%d/%m/%Y"))
        with col2:
            st.metric("**HOJE**", hoje.strftime("%d/%m/%Y"))
        with col3:
            st.metric("**LANÇAMENTO**", lancamento.strftime("%d/%m/%Y"))
        with col4:
            st.metric("**INÍCIO DE OBRAS**", inicio_obras.strftime("%d/%m/%Y"))

        csv_data = df.to_csv(index=False).encode('utf-8-sig')
        st.sidebar.download_button("📥 Baixar Cronograma em CSV", csv_data, "cronograma.csv", "text/csv")

        if "gerar_grafico" in st.session_state:
            del st.session_state.gerar_grafico

    else:
        st.info("Preencha o nome e a data de lançamento, depois clique em GERAR CRONOGRAMA.")

if __name__ == "__main__":
    main()
