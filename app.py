import datetime
import pandas as pd
import plotly.figure_factory as ff
import streamlit as st

def calcular_cronograma_macro(data_lancamento: datetime.date, additional_info=None):
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
        rec = {"Tarefa": tarefa.upper(), "Início": start, "Término": end}
        if additional_info and tarefa.upper() in additional_info:
            rec.update(additional_info[tarefa.upper()])
        else:
            rec.update({"Responsável": "N/A"})
        records.append(rec)

    df = pd.DataFrame(records)
    df["Início"] = pd.to_datetime(df["Início"])
    df["Término"] = pd.to_datetime(df["Término"])
    return df

def criar_grafico_gantt(df: pd.DataFrame, data_lanc: datetime.date):
    # Preparar tarefas no formato do create_gantt
    tasks = []
    for _, row in df.iterrows():
        tasks.append(dict(
            Task=row['Tarefa'],
            Start=row['Início'].strftime('%Y-%m-%d'),
            Finish=row['Término'].strftime('%Y-%m-%d'),
            Resource=row['Responsável']
        ))

    # Criar o gráfico Gantt
    fig = ff.create_gantt(
        tasks,
        group_tasks=True,
        show_colorbar=True,
        bar_width=0.4,
        height=650,
        index_col='Task'  # para cores diferentes por tarefa se desejar
    )

    # Adicionando marcos temporais
    inicio_projeto = df["Início"].min()
    hoje = datetime.date.today()
    lancamento = data_lanc
    inicio_obras = lancamento + datetime.timedelta(days=120)

    # Marcos no gráfico
    for label, x, color in [
        ("INÍCIO DO PROJETO", inicio_projeto, "green"),
        ("HOJE", hoje, "red"),
        ("LANÇAMENTO", lancamento, "blue"),
        ("INÍCIO DE OBRAS", inicio_obras, "purple")
    ]:
        fig.add_shape(
            dict(
                type="line",
                x0=x,
                y0=0,
                x1=x,
                y1=len(df)+0.5,
                xref='x',
                yref='y',
                line=dict(color=color, width=2, dash="dot")
            )
        )
        fig.add_annotation(
            dict(
                x=x,
                y=len(df)+0.5,
                text=label,
                showarrow=False,
                xref='x',
                yref='y',
                font=dict(size=12, color=color),
                xanchor='center',
                yanchor='bottom'
            )
        )

    # Configurações finais
    # Mostrar todos os meses entre início e fim
    max_date = df["Término"].max()
    if max_date.day != 1:
        next_month = (max_date.replace(day=1) + pd.Timedelta(days=32)).replace(day=1)
    else:
        next_month = max_date
    total_months = (next_month.year - inicio_projeto.year) * 12 + (next_month.month - inicio_projeto.month) + 1

    # criar ticks mensais e labels
    tickvals = []
    ticktext = []
    current_month = inicio_projeto.replace(day=1)
    for i in range(total_months):
        tickvals.append(current_month)
        ticktext.append(f"MÊS {i+1:02d}")
        year = current_month.year + (current_month.month // 12)
        month = (current_month.month % 12) + 1
        current_month = current_month.replace(year=year, month=month)

    fig.update_layout(
        xaxis=dict(
            tickmode='array',
            tickvals=tickvals,
            ticktext=ticktext,
            tickformat="%m-%y",
            showgrid=True,
            gridcolor="lightgray"
        ),
        yaxis=dict(
            autorange='reversed',  # para tarefas de cima pra baixo
            showgrid=True,
            gridcolor="lightgray"
        ),
        height=700,
        margin=dict(l=150, r=50, t=50, b=50),
        showlegend=False
    )

    return fig

def main():
    st.set_page_config(page_title="IDBCOLAB - Gantt", layout="wide")
    st.sidebar.image(
        "https://raw.githubusercontent.com/ciceromayk/idbcolab-referencia/main/LOGO%20IDBCOLAB.png",
        use_container_width=True
    )
    st.sidebar.markdown("## IDIBRA PARTICIPAÇÕES")
    nome = st.sidebar.text_input("📝 Nome do Projeto")
    data_lanc = st.sidebar.date_input("📅 LANÇAMENTO:", value=datetime.date.today(), format="DD-MM-YYYY")

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
    gerar = st.sidebar.button("🚀 GERAR GANTT")

    st.title("IDBCOLAB - Gantt do Projeto")
    st.subheader("Cronograma do Projeto")

    if nome:
        st.markdown(f"**Projeto:** {nome.upper()}")

    if gerar or ("gerar_grafico" in st.session_state and st.session_state.gerar_grafico):
        df = calcular_cronograma_macro(data_lanc)
        st.session_state.data_frame = df

        fig = criar_grafico_gantt(df, data_lanc)
        st.plotly_chart(fig, use_container_width=True)

        # Métricas
        hoje = datetime.date.today()
        inicio_projeto = df["Início"].min()
        lancamento = data_lanc
        inicio_obras = lancamento + datetime.timedelta(days=120)

        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("**INÍCIO DO PROJETO**", inicio_projeto.strftime("%d/%m/%Y"))
        with col2:
            st.metric("**HOJE**", hoje.strftime("%d/%m/%Y"))
        with col3:
            st.metric("**LANÇAMENTO**", lancamento.strftime("%d/%m/%Y"))
        with col4:
            st.metric("**INÍCIO DE OBRAS**", inicio_obras.strftime("%d/%m/%Y"))

        # Download CSV
        csv_bytes = df.to_csv(index=False).encode('utf-8-sig')
        st.sidebar.download_button("📥 Baixar Cronograma em CSV", csv_bytes, "cronograma.csv", "text/csv")
        # Limpa a sessão
        if "gerar_grafico" in st.session_state:
            del st.session_state.gerar_grafico
    else:
        st.info("Preencha o nome e a data de lançamento, depois clique em GERAR GANTT.")

if __name__ == "__main__":
    main()
