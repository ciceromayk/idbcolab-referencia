def criar_grafico_macro(df: pd.DataFrame, data_lanc: datetime.date, color_sequence=None) -> px.timeline:
    hoje = datetime.date.today()
    lancamento = data_lanc
    inicio_projeto = df["Início"].min()
    max_date = df["Término"].max()
    if max_date.day != 1:
        next_month = (max_date.replace(day=1) + pd.Timedelta(days=32)).replace(day=1)
    else:
        next_month = max_date
    total_months = (next_month.year - inicio_projeto.year) * 12 + (next_month.month - inicio_projeto.month) + 1
    end_period = (inicio_projeto + pd.DateOffset(months=total_months))
    
    # lista de ticks mensal
    tickvals = []
    ticktext = []
    current_month = inicio_projeto.replace(day=1)
    for i in range(total_months):
        tickvals.append(current_month)
        ticktext.append(f"MÊS {i+1:02d}")
        year = current_month.year + (current_month.month // 12)
        month = (current_month.month % 12) + 1
        current_month = current_month.replace(year=year, month=month)
    
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

    inicio_obras = lancamento + datetime.timedelta(days=120)
    # Início de obras
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

    # Configura eixo X com todos os meses
    fig.update_xaxes(
        tickvals=tickvals,
        ticktext=ticktext,
        tickformat="%m-%y",
        range=[inicio_projeto, end_period],
        showgrid=True,
        gridcolor="lightgray",
        dtick="M1"
    )

    # Linhas horizontais para cada tarefa
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

    # Datas sempre visíveis, deslocadas pra fora
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

    # Garantir que as anotações das primeiras tarefas apareçam
    # Ajuste de deslocamento para tarefas com início próximo ou igual ao zero
    # já foram tratados ao usar deslocamento genérico
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
    data_lanc = st.sidebar.date_input("📅 LANÇAMENTO:", value=datetime.date.today(), format="DD-MM-YYYY")  # formato dd-mm-yyyy

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
