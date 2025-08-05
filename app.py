import datetime
import pandas as pd
import plotly.figure_factory as ff
import plotly.express as px
import streamlit as st

def calcular_cronograma_macro(data_lancamento: datetime.date, additional_info=None):
def calcular_cronograma_macro(data_lancamento: datetime.date, additional_info: dict = None) -> tuple:
    offsets = {
        "CONCEPÇÃO DO PRODUTO": (0, 180),
        "INCORPORAÇÃO": (180, 420),
@@ -20,195 +20,289 @@ def calcular_cronograma_macro(data_lancamento: datetime.date, additional_info=No
    for tarefa, (i0, i1) in offsets.items():
        start = day_zero + datetime.timedelta(days=i0)
        end = day_zero + datetime.timedelta(days=i1)
        rec = {"Tarefa": tarefa.upper(), "Início": start, "Término": end}
        record = {"Tarefa": tarefa.upper(), "Início": start, "Término": end}
        if additional_info and tarefa.upper() in additional_info:
            rec.update(additional_info[tarefa.upper()])
            record.update(additional_info[tarefa.upper()])
        else:
            rec.update({"Responsável": "N/A"})
        records.append(rec)
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

    # Ordenar tarefas de cima para baixo
    df["Ordem"] = range(len(df), 0, -1)
    df = df.sort_values("Ordem")
    return df

def criar_grafico_gantt(df: pd.DataFrame, data_lanc: datetime.date):
    tasks = []
    for _, row in df.iterrows():
        tasks.append(dict(
            Task=row['Tarefa'],
            Start=row['Início'].strftime('%Y-%m-%d'),
            Finish=row['Término'].strftime('%Y-%m-%d'),
            Resource=row['Responsável']
        ))

    fig = ff.create_gantt(
        tasks,
        group_tasks=True,
        show_colorbar=False,
        bar_width=0.4,
        height=700,
        index_col='Task'
    )
    return df, day_zero

    # Marcos
    inicio_projeto = df["Início"].min()
def criar_grafico_macro(df: pd.DataFrame, data_lanc: datetime.date, color_sequence=None) -> px.timeline:
    hoje = datetime.date.today()
    lancamento = data_lanc
    inicio_obras = lancamento + datetime.timedelta(days=120)

    marcadores = [
        ("INÍCIO DO PROJETO", inicio_projeto, "green"),
        ("HOJE", hoje, "red"),
        ("LANÇAMENTO", lancamento, "blue"),
        ("INÍCIO DE OBRAS", inicio_obras, "purple")
    ]

    y_top = len(df) + 0.5

    for label, x, color in marcadores:
        # Linha vertical do marco
        fig.add_shape({
            "type": "line",
            "x0": x,
            "x1": x,
            "y0": 0,
            "y1": y_top,
            "xref": "x",
            "yref": "y",
            "line": {"color": color, "width": 2, "dash": "dot"}
        })
        # Texto do marco na parte superior da linha
        fig.add_annotation({
            "x": x,
            "y": y_top,
            "text": label,
            "showarrow": False,
            "xref": "x",
            "yref": "y",
            "font": {"size": 12, "color": color},
            "xanchor": "center",
            "yanchor": "bottom"
        })

    # Inserir datas ao lado esquerdo e direito de cada barra
    for _, row in df.iterrows():
        # Data de início à esquerda da barra
        fig.add_annotation({
            "x": row['Início'],
            "y": row['Ordem'],
            "text": f"<b>{row['Início'].strftime('%d/%m/%Y')}</b>",
            "showarrow": False,
            "xanchor": "right",
            "yanchor": "middle",
            "font": {"size": 10},
        })
        # Data de término à direita da barra
        fig.add_annotation({
            "x": row['Término'],
            "y": row['Ordem'],
            "text": f"<b>{row['Término'].strftime('%d/%m/%Y')}</b>",
            "showarrow": False,
            "xanchor": "left",
            "yanchor": "middle",
            "font": {"size": 10},
        })

    # Configurando o eixo X para múltiplos meses
    inicio_projeto = df["Início"].min()
    max_date = df["Término"].max()

    # Define o fim do período ao final do último Término + um mês
    if max_date.day != 1:
        next_month = (max_date.replace(day=1) + pd.Timedelta(days=32)).replace(day=1)
    else:
        next_month = max_date
    total_months = (next_month.year - df["Início"].min().year) * 12 + (next_month.month - df["Início"].min().month) + 1
    total_months = (next_month.year - inicio_projeto.year) * 12 + (next_month.month - inicio_projeto.month) + 1
    end_period = (inicio_projeto + pd.DateOffset(months=total_months))

    # Montar lista de ticks para cada mês
    tickvals = []
    ticktext = []
    current_month = df["Início"].min().replace(day=1)
    current_month = inicio_projeto.replace(day=1)
    for i in range(total_months):
        tickvals.append(current_month)
        ticktext.append(f"MÊS {i+1:02d}")
        year = current_month.year + (current_month.month // 12)
        month = (current_month.month % 12) + 1
        current_month = current_month.replace(year=year, month=month)

    # Layout geral
    fig.update_layout({
        "xaxis": {
            "tickmode": "array",
            "tickvals": tickvals,
            "ticktext": ticktext,
            "tickformat": "%m-%y",
            "showgrid": True,
            "gridcolor": "lightgray",
        },
        "yaxis": {
            "autorange": "reversed",
            "showgrid": True,
            "gridcolor": "lightgray",
            "dtick": 1,
        },
        "margin": {"l": 150, "r": 50, "t": 50, "b": 50},
        "height": 700,
        "showlegend": False,
    })
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

    # Configuração eixo X
    fig.update_xaxes(
        tickvals=tickvals,
        ticktext=ticktext,
        tickformat="%m-%y",
        range=[inicio_projeto, end_period],
        showgrid=True,
        gridcolor="lightgray",
        dtick="M1"  # marca de 1 mês
    )

    # Grade horizontal para cada tarefa
    fig.update_yaxes(
        showgrid=True,
        gridcolor="lightgray",
        title_text=None,
        title_font={'size': 16}
    )

    # Linhas de fundo alternadas
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

    # Datas visíveis, deslocadas para fora
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

    # Garantir que as anotações das tarefas com datas próximas apareçam
    # já estão ajustadas pelo deslocamento de 3 dias
    fig.update_layout(
        annotations=annotations,
        margin=dict(l=250, r=40, t=20, b=40),
        showlegend=False
    )

    return fig

def main():
    st.set_page_config(page_title="IDBCOLAB - Gantt", layout="wide")
    st.set_page_config(page_title="IDBCOLAB - COMITÊ DE PRODUTO", layout="wide")
    st.sidebar.image(
        "https://raw.githubusercontent.com/ciceromayk/idbcolab-referencia/main/LOGO%20IDBCOLAB.png",
        use_container_width=True
    )
    st.sidebar.markdown("## IDIBRA PARTICIPAÇÕES")
    # Chaves exclusivas para evitar conflitos
    nome = st.sidebar.text_input("📝 Nome do Projeto", key='nome_projeto')
    data_lanc = st.sidebar.date_input("📅 LANÇAMENTO:", value=datetime.date.today(), format="DD-MM-YYYY", key='data_lancamento')
    nome = st.sidebar.text_input("📝 Nome do Projeto")
    data_lanc = st.sidebar.date_input(
        "📅 LANÇAMENTO:", value=datetime.date.today(), format="DD-MM-YYYY"
    )  # formato dd-mm-yyyy

    st.sidebar.markdown("## Opções de Personalização")
    color_palettes = {
        "Default": None,
        "Viridis": ["#440154", "#21908d", "#fde725"],
        "Cividis": ["#00224E", "#00A6D9", "#FDE725"],
        "Plotly": ["#636EFA", "#EF553B", "#00CC96"],
        "Dark2": ["#1B9E77", "#D95F02", "#7570B3"]
        "Viridis": px.colors.sequential.Viridis,
        "Cividis": px.colors.sequential.Cividis,
        "Plotly": px.colors.qualitative.Plotly,
        "Dark2": px.colors.qualitative.Dark2
    }

    if "selected_palette" not in st.session_state:
        st.session_state.selected_palette = "Default"

    selected_palette = st.sidebar.selectbox("Selecione a paleta de cores", list(color_palettes.keys()))
    selected_palette = st.sidebar.selectbox(
        "Selecione a paleta de cores", list(color_palettes.keys())
    )

    if selected_palette != st.session_state.selected_palette:
        st.session_state.selected_palette = selected_palette
        st.session_state.gerar_grafico = True

    color_sequence = color_palettes[st.session_state.selected_palette]
    gerar = st.sidebar.button("🚀 GERAR GANTT")
    gerar = st.sidebar.button("🚀 GERAR CRONOGRAMA")

    st.title("IDBCOLAB - Gantt do Projeto")
    st.title("IDBCOLAB - COMITÊ DE PRODUTO")
    st.subheader("Cronograma do Projeto")

    if nome:
        st.markdown(f"**Projeto:** {nome.upper()}")

    if gerar or ("gerar_grafico" in st.session_state and st.session_state.gerar_grafico):
        df = calcular_cronograma_macro(data_lanc)
        df, _ = calcular_cronograma_macro(data_lanc)
        st.session_state.data_frame = df

        fig = criar_grafico_gantt(df, data_lanc)
        st.plotly_chart(fig, use_container_width=True)

        # Métricas
        hoje = datetime.date.today()
        inicio_projeto = df["Início"].min()
        lancamento = data_lanc
        inicio_projeto = df["Início"].min()
        inicio_obras = lancamento + datetime.timedelta(days=120)

        fig = criar_grafico_macro(df, data_lanc, color_sequence=color_sequence)
        st.plotly_chart(fig, use_container_width=True, config={"locale": "pt-BR"})

        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("**INÍCIO DO PROJETO**", inicio_projeto.strftime("%d/%m/%Y"))
@@ -219,16 +313,16 @@ def main():
        with col4:
            st.metric("**INÍCIO DE OBRAS**", inicio_obras.strftime("%d/%m/%Y"))

        # Download CSV
        csv_bytes = df.to_csv(index=False).encode('utf-8-sig')
        csv_data = df.to_csv(index=False).encode("utf-8-sig")
        st.sidebar.download_button(
            "📥 Baixar Cronograma em CSV", csv_bytes, "cronograma.csv", "text/csv"
            "📥 Baixar Cronograma em CSV", csv_data, "cronograma.csv", "text/csv"
        )

        if "gerar_grafico" in st.session_state:
            del st.session_state.gerar_grafico

    else:
        st.info("Preencha o nome e a data de lançamento, depois clique em GERAR GANTT.")
        st.info("Preencha o nome e a data de lançamento, depois clique em GERAR CRONOGRAMA.")

if __name__ == "__main__":
    main()
