from dash import Dash, dcc, html, Input, Output
import plotly.express as px
import pandas as pd

app = Dash(__name__)

df = pd.read_csv(
    "https://raw.githubusercontent.com/ThuwarakeshM/geting-started-with-plottly-dash/main/life_expectancy.csv"
)

colors = {"background": "#011833", "text": "#7FDBFF"}

app.layout = html.Div(
    [
        html.H1(
            "My Dazzling Dashboard",
        ),
        html.Div(
            [
                html.Div(
                    [
                        html.Label("Developing Status of the Country"),
                        dcc.Dropdown(
                            id="status-dropdown",
                            options=[
                                {"label": s, "value": s} for s in df.Status.unique()
                            ],
                            className="dropdown",
                        ),
                    ]
                ),
                html.Div(
                    [
                        html.Label("Average schooling years grater than"),
                        dcc.Dropdown(
                            id="schooling-dropdown",
                            options=[
                                {"label": y, "value": y}
                                for y in range(
                                    int(df.Schooling.min()), int(df.Schooling.max()) + 1
                                )
                            ],
                            className="dropdown",
                        ),
                    ]
                ),
            ],
            className="row",
        ), 
        html.Div(dcc.Graph(id="life-exp-vs-gdp"), className="chart"),
        dcc.Slider(
            id="year-slider",
            min=df.Year.min(),
            max=df.Year.max(),
            step=None,
            marks={year: str(year) for year in range(df.Year.min(), df.Year.max() + 1)},
            value=df.Year.min(),
        ),
    ],
    className="container",
)


@app.callback(
    Output("life-exp-vs-gdp", "figure"),
    Input("year-slider", "value"),
    Input("status-dropdown", "value"),
    Input("schooling-dropdown", "value"),
)
def update_figure(selected_year, country_status, schooling):
    filtered_dataset = df[(df.Year == selected_year)]

    if schooling:
        filtered_dataset = filtered_dataset[filtered_dataset.Schooling <= schooling]

    if country_status:
        filtered_dataset = filtered_dataset[filtered_dataset.Status == country_status]

    fig = px.scatter(
        filtered_dataset,
        x="GDP",
        y="Life expectancy",
        size="Population",
        color="continent",
        hover_name="Country",
        log_x=True,
        size_max=60,
    )

    fig.update_layout(
        plot_bgcolor=colors["background"],
        paper_bgcolor=colors["background"],
        font_color=colors["text"],
    )

    return fig


if __name__ == "__main__":
    app.run_server(debug=True)


##############################################################################################

# from dash import Dash, html, Input, Output, ctx

# app = Dash(__name__)

# app.layout = html.Div([
#     html.Button('Button 1', id='btn-nclicks-1', n_clicks=0),
#     html.Button('Button 2', id='btn-nclicks-2', n_clicks=0),
#     html.Button('Button 3', id='btn-nclicks-3', n_clicks=0),
#     html.Div(id='container-button-timestamp')
# ])

# @app.callback(
#     Output('container-button-timestamp', 'children'),
#     Input('btn-nclicks-1', 'n_clicks'),
#     Input('btn-nclicks-2', 'n_clicks'),
#     Input('btn-nclicks-3', 'n_clicks')
# )
# def displayClick(btn1, btn2, btn3):
#     msg = "None of the buttons have been clicked yet"
#     if "btn-nclicks-1" == ctx.triggered_id:
#         msg = "Button 1 was most recently clicked"
#     elif "btn-nclicks-2" == ctx.triggered_id:
#         msg = "Button 2 was most recently clicked"
#     elif "btn-nclicks-3" == ctx.triggered_id:
#         msg = "Button 3 was most recently clicked"
#     return html.Div(msg)

# if __name__ == '__main__':
#     app.run_server(debug=True)