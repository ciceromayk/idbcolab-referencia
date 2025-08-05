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

    # Lista de ticks no formato MM-YY
    tickvals = []
    ticktext_MMYY = []
    current_month = inicio_projeto.replace(day=1)
    for _ in range(total_months):
        tickvals.append(current_month)
        ticktext_MMYY.append(f"{current_month.month:02d}-{str(current_month.year)[-2:]}")
        year = current_month.year + (current_month.month // 12)
        month = (current_month.month % 12) + 1
        current_month = current_month.replace(year=year, month=month)

    # Criar o gráfico
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

    # Marcar início do projeto
    fig.add_shape(
        type="line",
        x0=inicio_projeto,
        x1=inicio_projeto,
        y0=0,
        y1=1,
        xref="x",
        yref="paper",
        line=dict(color="green", width=2, dash="dot")
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

    # Marcar hoje
    fig.add_shape(
        type="line",
        x0=hoje,
        x1=hoje,
        y0=0,
        y1=1,
        xref="x",
        yref="paper",
        line=dict(color="red", width=2, dash="dot")
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

    # Marcar lançamento
    fig.add_shape(
        type="line",
        x0=lancamento,
        x1=lancamento,
        y0=0,
        y1=1,
        xref="x",
        yref="paper",
        line=dict(color="blue", width=2, dash="dot")
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

    # Marcar início de obras
    inicio_obras = lancamento + datetime.timedelta(days=120)
    fig.add_shape(
        type="line",
        x0=inicio_obras,
        x1=inicio_obras,
        y0=0,
        y1=1,
        xref="x",
        yref="paper",
        line=dict(color="purple", width=2, dash="dot")
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

    # Configuração eixo principal
    fig.update_xaxes(
        tickvals=tickvals,
        ticktext=ticktext_MMYY,  # usar a variável correta aqui
        tickformat="%m-%y",
        range=[inicio_projeto, end_period],
        showgrid=True,
        gridcolor="lightgray",
        dtick="M1"
    )

    # Configuração eixo secundário MM-YY
    fig.update_layout(
        margin=dict(l=250, r=40, t=20, b=150),
        # Definindo o eixo secundário, sobreposto ao principal
        xaxis2=dict(
            domain=[0, 1],  # ocupar toda a largura
            overlaying="x",
            anchor="y",
            side='bottom',  # na parte inferior
            tickvals=tickvals,
            ticktext=ticktext_MMYY,
            showticklabels=True,
            showgrid=False,
            tickfont=dict(size=10),
            position=0.05  # posição quase na parte de baixo
        ),
        # Anotação para label do eixo secundário
        annotations=[
            dict(
                text="Mês (MM-YY)",
                xref="x2",
                yref="paper",
                x=0.5,
                y=0.02,
                showarrow=False,
                font=dict(size=12)
            )
        ]
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

    # Anotações externas
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

    # Atualizar layout
    fig.update_layout(
        annotations=annotations,
        showlegend=False,
        margin=dict(l=250, r=40, t=20, b=180),
    )

    return fig
