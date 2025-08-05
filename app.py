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
        # Inclui informações adicionais se fornecidas, senão usa padrões
        if additional_info and tarefa.upper() in additional_info:
            record.update(additional_info[tarefa.upper()])
        else:
            record.update({"Responsável": "N/A", "Status": "Pendente", "Notas": ""})
        records.append(record)

    df = pd.DataFrame(records)
    
    # Ordenar as tarefas conforme pré-definido
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
    
    df['Tarefa'] = pd.Categorical(df['Tarefa'], categories=tarefas_ordenadas, ordered=True)
    df = df.sort_values('Tarefa').reset_index(drop=True)

    return df, day_zero

def criar_grafico_macro(df: pd.DataFrame, data_lancamento: datetime.date, color_sequence=None) -> px.timeline:
    # Configura o gráfico incluindo informações extras no hover
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

    fig.update_yaxes(title_text=None, autorange="reversed")
    fig.update_xaxes(tickformat="%d/%m/%Y")

    # Alterna fundo para diferenciar as linhas do gráfico
    n = len(df)
    for i in range(n):
        if i % 2 == 0:
            y0 = 1 - (i + 1) / n
            y1 = 1 - i / n
            fig.add_shape(
                type="rect", xref="paper", yref="paper",
                x0=0, x1=1, y0=y0, y1=y1,
                fillcolor="lightgray", opacity=0.2,
                line_width=0, layer="below"
            )

    # Adiciona as anotações de data (INÍCIO / TÉRMINO) dentro do gráfico
    annotations = []
    for _, row in df.iterrows():
        meio = row["Início"] + (row["Término"] - row["Início"]) / 2
        text = f"<b>INÍCIO: {row['Início']:%d/%m/%Y}<br>TÉRMINO: {row['Término']:%d/%m/%Y}</b>"
        annotations.append(dict(
            x=meio, y=row["Tarefa"], text=text,
            showarrow=False,
            font=dict(color="black", size=10),
            xanchor="center", yanchor="middle"
        ))
    fig.update_layout(annotations=annotations, margin=dict(l=250, r=40, t=40, b=40), showlegend=False)

    # Adiciona linhas de marcador para datas importantes
    def add_marker(date: datetime.date, label: str, color: str):
        fig.add_shape(
            type="line", x0=date, x1=date,
            y0=0, y1=1, xref="x", yref="paper",
            line=dict(color=color, width=2, dash="dot")
        )
        fig.add_annotation(
            x=date, y=0, xref="x", yref="paper",
            text=f"<b>{label.upper()}</b>",
            showarrow=False, textangle=-90,
            font=dict(color="black", size=10),
            xanchor="left", yanchor="bottom", xshift=5
        )

    hoje = datetime.date.today()
    inicio_obras = data_lancamento + datetime.timedelta(days=120)

    add_marker(hoje, "HOJE", "red")
    add_marker(data_lancamento, "LANÇAMENTO", "blue")
    add_marker(inicio_obras, "INÍCIO DE OBRAS", "orange")

    return fig

def main():
    # Configura a página
    st.set_page_config(page_title="IDBCOLAB - COMITÊ DE PRODUTO", layout="wide")

    st.sidebar.markdown("## IDIBRA PARTICIPAÇÕES")
    nome = st.sidebar.text_input("📝 Nome do Projeto")
    data_lanc = st.sidebar.date_input("📅 LANÇAMENTO:", value=datetime.date.today(), format="DD/MM/YYYY")
    
    # Opção 3: Seleção de paleta de cores para o gráfico
    st.sidebar.markdown("## Opções de personalização")
    color_palettes = {
        "Default": None,
        "Viridis": px.colors.sequential.Viridis,
        "Cividis": px.colors.sequential.Cividis,
        "Plotly": px.colors.qualitative.Plotly,
        "Dark2": px.colors.qualitative.Dark2
    }
    selected_palette = st.sidebar.selectbox("Selecione a paleta de cores", list(color_palettes.keys()))
    color_sequence = color_palettes[selected_palette]

    # Opção 5: Informações adicionais para cada tarefa
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
    with st.sidebar.expander("Informações adicionais para cada tarefa", expanded=False):
        dados_adicionais = {}
        for tarefa in tarefas_ordenadas:
            st.markdown(f"**{tarefa}**")
            resp = st.text_input(f"Responsável", value="N/A", key=f"resp_{tarefa}")
            status = st.selectbox("Status", ["Pendente", "Em andamento", "Concluído"], key=f"status_{tarefa}")
            notas = st.text_area("Notas", value="", key=f"notas_{tarefa}")
            dados_adicionais[tarefa] = {"Responsável": resp, "Status": status, "Notas": notas}
    
    gerar = st.sidebar.button("🚀 GERAR CRONOGRAMA")

    st.title("IDBCOLAB - COMITÊ DE PRODUTO")
    st.subheader("Cronograma do Projeto")

    if nome:
        st.markdown(f"**Projeto:** {nome.upper()}")

    if gerar:
        try:
            # Calcula o cronograma incluindo as informações adicionais
            df, day_zero = calcular_cronograma_macro(data_lanc, additional_info=dados_adicionais)
            fig = criar_grafico_macro(df, data_lanc, color_sequence=color_sequence)
            st.plotly_chart(fig, use_container_width=True, config={"locale": "pt-BR"})

            # Exibe os cartões com datas importantes
            inicio_projeto = df['Início'].min()
            hoje = datetime.date.today()
            lancamento = data_lanc
            inicio_obras = data_lanc + datetime.timedelta(days=120)

            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("**INÍCIO DO PROJETO**", inicio_projeto.strftime("%d/%m/%Y"))
            with col2:
                st.metric("**HOJE**", hoje.strftime("%d/%m/%Y"))
            with col3:
                st.metric("**LANÇAMENTO**", lancamento.strftime("%d/%m/%Y"))
            with col4:
                st.metric("**INÍCIO DE OBRAS**", inicio_obras.strftime("%d/%m/%Y"))

            # Opção 4: Botão para exportar o cronograma em CSV
            @st.cache_data
            def convert_df(df):
                return df.to_csv(index=False).encode('utf-8')

            csv_data = convert_df(df)
            st.download_button("📥 Baixar Cronograma em CSV", csv_data, "cronograma.csv", "text/csv")
            
        except Exception as e:
            st.error(f"❌ ERRO: {e}")
    else:
        st.info("Preencha o nome e a data de lançamento, depois clique em GERAR CRONOGRAMA.")

if __name__ == "__main__":
    main()

