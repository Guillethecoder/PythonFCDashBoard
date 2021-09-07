import dash
from dash import dcc
from dash import html

import dash_bootstrap_components as dbc
import matplotlib as mpl
from mplsoccer import Pitch, VerticalPitch, FontManager
import matplotlib.patheffects as path_effects
import pandas as pd
from matplotlib.colors import LinearSegmentedColormap
from scipy.ndimage import gaussian_filter
import matplotlib.pyplot as plt
import io
import base64

df = pd.read_csv('../my_proj/all_shots_16_20.csv')

# Fonts
robotto_regular = FontManager()

# path effects
path_eff = [path_effects.Stroke(linewidth=1.5, foreground='black'),
            path_effects.Normal()]

# see the custom colormaps example for more ideas on setting colormaps
pearl_earring_cmap = LinearSegmentedColormap.from_list("Pearl Earring - 10 colors",
                                                       ['#15242e', '#4393c4'], N=10)

# https://www.bootstrapcdn.com/bootswatch/
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.SOLAR],
                meta_tags=[{'name': 'viewport',
                            'content': 'width=device-width, initial-scale=1.0'}]
                )

### APP LAYOUT

nav_bar = dbc.NavbarSimple(
    children=[
        dbc.NavItem(dbc.NavLink("Page 1", href="#")),
        dbc.DropdownMenu(
            children=[
                dbc.DropdownMenuItem("More pages", header=True),
                dbc.DropdownMenuItem("Page 2", href="#"),
                dbc.DropdownMenuItem("Page 3", href="#"),
            ],
            nav=True,
            in_navbar=True,
            label="More",
        ),
    ],
    brand="Shooting Analysis with Python",
    brand_href="#",
    color="primary",
    dark=True,
)

container = dbc.Container([

    dbc.Row([
        dbc.Col(html.H1("Player Shooting Analysis"),
                className="text-center mb-4",
                width=12,
                )
    ]),
    dbc.Row([
        dbc.Col([
            html.H3('Competition:'),
            dcc.Dropdown(
                id='competition_select',
                multi=True,
                value=["La Liga"],
                options=[{'label': x, 'value': x} for x in df['competition_name'].unique()]
            )
        ], xs=12, sm=12, md=12, lg=5, xl=5
        ),

        dbc.Col([
            html.H3('Season:'),
            dcc.Dropdown(
                id='season_select',
                multi=True,
                value=["2019/2020"],
                options=[{'label': x, 'value': x} for x in df['season_name'].unique()]
            )
        ], xs=12, sm=12, md=12, lg=5, xl=5),

        dbc.Col([
            html.H3('Team: '),
            dcc.Dropdown(
                id='team_select',
                options=[{'label': x, 'value': x} for x in df['team_name'].unique()]
            ),
        ], xs=12, sm=12, md=12, lg=5, xl=5),

        dbc.Col([
            html.H3('Player: '),
            dcc.Dropdown(
                id='player_select',
                options=[{'label': x, 'value': x} for x in df['player_name'].unique()]
            ),
        ], xs=12, sm=12, md=12, lg=5, xl=5)

    ]),
    dbc.Row([
        html.Br()
    ]),
    dbc.Row([
        html.Hr()
    ]),
    dbc.Row([

        dbc.Col([
            dbc.Row([html.Div(id='card_number_shoots-output-container',
                              style={"justify-content": "center"})], align="center"),
            dbc.Row([html.Div(id='card_number_goals-output-container',
                              style={"justify-content": "center"})], align="center"),
            dbc.Row([html.Div(id='avg_goal_percent-output-container',
                              style={"justify-content": "center"})], align="center"),
        ], xs=12, sm=12, md=12, lg=3, xl=3, style={"justify-content": "center"}
        ),

    ])

], fluid=True)

app.layout = html.Div(
    [nav_bar, container]
)


################################################################################


@app.callback(
    dash.dependencies.Output('card_number_shoots-output-container', 'children'),
    [dash.dependencies.Input('competition_select', 'value')],
    [dash.dependencies.Input('season_select', 'value')],
    [dash.dependencies.Input('team_select', 'value')],
    [dash.dependencies.Input('player_select', 'value')])
def update_table(selected_competition, selected_season, team_select, player_select):
    dff = df
    if selected_competition:
        dff = df[df["competition_name"].isin(selected_competition)]
    if selected_season:
        dff = dff[dff["season_name"].isin(selected_season)]
    if team_select:
        dff = dff[dff['team_name'] == team_select]
    if player_select:
        dff = dff[dff['player_name'] == player_select]

    return dbc.Card(
        dbc.CardBody(
            [
                html.H5("Number of Shoots:", className="card-title"),
                html.H3(
                    "{}".format(len(dff)),
                    className="card-text",
                )
            ]
        ), color="warning", inverse=True, style={"width": "18rem"}
    )


@app.callback(
    dash.dependencies.Output('card_number_goals-output-container', 'children'),
    [dash.dependencies.Input('competition_select', 'value')],
    [dash.dependencies.Input('season_select', 'value')],
    [dash.dependencies.Input('team_select', 'value')],
    [dash.dependencies.Input('player_select', 'value')])
def update_table(selected_competition, selected_season, team_select, player_select):
    dff = df
    if selected_competition:
        dff = df[df["competition_name"].isin(selected_competition)]
    if selected_season:
        dff = dff[dff["season_name"].isin(selected_season)]
    if team_select:
        dff = dff[dff['team_name'] == team_select]
    if player_select:
        dff = dff[dff['player_name'] == player_select]

    return dbc.Card(
        dbc.CardBody(
            [
                html.H5("Number of Goals:", className="card-title"),
                html.H3(
                    "{}".format(len(dff[dff["Goal"]])),
                    className="card-text",
                )
            ]
        ), color="success", inverse=True, style={"width": "18rem", "margin-top": "5px"}
    )


@app.callback(
    dash.dependencies.Output('avg_goal_percent-output-container', 'children'),
    [dash.dependencies.Input('competition_select', 'value')],
    [dash.dependencies.Input('season_select', 'value')],
    [dash.dependencies.Input('team_select', 'value')],
    [dash.dependencies.Input('player_select', 'value')])
def update_table(selected_competition, selected_season, team_select, player_select):
    dff = df
    if selected_competition:
        dff = df[df["competition_name"].isin(selected_competition)]
    if selected_season:
        dff = dff[dff["season_name"].isin(selected_season)]
    if team_select:
        dff = dff[dff['team_name'] == team_select]
    if player_select:
        dff = dff[dff['player_name'] == player_select]

    return dbc.Card(
        dbc.CardBody(
            [
                html.H5("Average goal percentage:", className="card-title"),
                html.H3(
                    "{} %".format(round((len(dff[dff["Goal"]]) / len(dff)) * 100, 2)),
                    className="card-text",
                )
            ]
        ), color="primary", inverse=True, style={"width": "18rem", "margin-top": "5px"}
    )


@app.callback(
    dash.dependencies.Output('team_select', 'options'),
    [dash.dependencies.Input('competition_select', 'value')],
    [dash.dependencies.Input('season_select', 'value')])
def update_table(selected_competition, selected_season):
    dff = df
    if selected_competition:
        dff = dff[dff["competition_name"].isin(selected_competition)]
        if selected_season:
            dff = dff[dff["season_name"].isin(selected_season)]
    elif selected_season:
        dff = dff[dff["season_name"].isin(selected_season)]

    if len(dff) == 0:
        return ['']
    else:
        return [{'label': x, 'value': x} for x in dff['team_name'].unique()]


@app.callback(
    dash.dependencies.Output('player_select', 'options'),
    [dash.dependencies.Input('competition_select', 'value')],
    [dash.dependencies.Input('season_select', 'value')],
    [dash.dependencies.Input('team_select', 'value')])
def update_table(selected_competition, selected_season, team_select):
    dff = df
    if selected_competition:
        dff = df[df["competition_name"].isin(selected_competition)]
    if selected_season:
        dff = dff[dff["season_name"].isin(selected_season)]
    if team_select:
        dff = dff[dff['team_name'] == team_select]

    if len(dff) == 0:
        return ['']
    else:
        return [{'label': x, 'value': x} for x in dff['player_name'].unique()]


if __name__ == '__main__':
    app.run_server(port=3000, debug=True)
