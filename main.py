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
        dbc.NavItem(dbc.NavLink("Player XGoal Analysis", href="/", active='exact')),
        dbc.NavItem(dbc.NavLink("Heat Map League Analysis", href="/heat_map", active='exact')),
    ],
    brand="Shooting Analysis with Python",
    brand_href="/",
    color="primary",
    dark=True,
)

page_content = html.Div(id = "page_content", children=[])

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
            dbc.Row([html.Div(id='player_card_number_shoots-output-container',
                              style={"justify-content": "center"})], align="center"),
            dbc.Row([html.Div(id='player_card_number_goals-output-container',
                              style={"justify-content": "center"})], align="center"),
            dbc.Row([html.Div(id='player_avg_goal_percent-output-container',
                              style={"justify-content": "center"})], align="center"),
        ], xs=12, sm=12, md=12, lg=3, xl=3, style={"justify-content": "center"}
        ),
        dbc.Col([
            html.Img(id='shooting_xg')

        ], xs=12, sm=12, md=12, lg=4, xl=4)

    ])

], fluid=True)


container_2 = dbc.Container([
    dbc.Row([
        dbc.Col(html.H1("Goals Analysis"),
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
            html.H3('Top Scorers:')
        ], xs=12, sm=12, md=12, lg=4, xl=5)
    ]),
    dbc.Row([

        dbc.Col([
            html.Div(id='table_top_scorers-output-container')
        ], xs=12, sm=12, md=12, lg=3, xl=3),

        dbc.Col([
            dbc.Row([html.Div(id='card_number_shoots-output-container',
                              style={"justify-content": "center"})], align="center"),
            dbc.Row([html.Div(id='card_number_goals-output-container',
                              style={"justify-content": "center"})], align="center"),
            dbc.Row([html.Div(id='avg_goal_percent-output-container',
                              style={"justify-content": "center"})], align="center"),
        ], xs=12, sm=12, md=12, lg=2, xl=2, style={"justify-content": "center"}
        ),

        dbc.Col([
            html.Img(id='shoot_heatmap')

        ], xs=12, sm=12, md=12, lg=4, xl=4)
    ])

], fluid=True)

container_3 = dbc.Container([])


app.layout = html.Div(
    [dcc.Location(id='url', refresh=False),
    nav_bar,
    page_content]
)




################################################################################



@app.callback(
    dash.dependencies.Output('player_card_number_shoots-output-container', 'children'),
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
    dash.dependencies.Output('player_card_number_goals-output-container', 'children'),
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
    dash.dependencies.Output('player_avg_goal_percent-output-container', 'children'),
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


@app.callback(
    dash.dependencies.Output('shooting_xg', 'src'),
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

    mpl.rcParams.update({'text.color': "white",
                         'axes.labelcolor': "white"})

    dff_goals = dff[dff.Goal == True].copy()
    dff_non_goals = dff[dff.Goal != True].copy()

    buf = io.BytesIO()
    

    pitch = VerticalPitch(pad_bottom=0.5,  # pitch extends slightly below halfway line
                      half=True,  # half of a pitch
                      goal_type='box',
                      goal_alpha=0.8,
                      pitch_color='grass',
                      line_color='white',
                      stripe=True
                     )

    fig, ax = pitch.draw(figsize=(12, 10))

    # plot non-goal shots with hatch
    sc1 = pitch.scatter(dff_non_goals.X, dff_non_goals.Y,
                    # size varies between 100 and 1900 (points squared)
                    s=(dff_non_goals.my_xg * 1900) + 100,
                    edgecolors='#b94b75',  # give the markers a charcoal border
                    c='None',  # no facecolor for the markers
                    hatch='///',  # the all important hatch (triple diagonal lines)
                    # for other markers types see: https://matplotlib.org/api/markers_api.html
                    marker='o',
                    ax=ax)

    # plot goal shots with a football marker
    # 'edgecolors' sets the color of the pentagons and edges, 'c' sets the color of the hexagons
    pitch.scatter(dff_goals.X, dff_goals.Y,
                   
                    s=(dff_goals.my_xg * 1900) + 100,
                    edgecolors='blue',
                    linewidth=0.6,
                    c='white',
                    marker='football',
                    ax=ax)
    if player_select:
        ax.text(x=40, y=80, s='{}\n{}'.format(player_select, selected_competition[0]),
                size=30,
                color=pitch.line_color,
                va='center', ha='center')
    elif selected_competition:
        ax.text(x=40, y=80, s='{}'.format(selected_competition[0]),
                size=30,
                color=pitch.line_color,
                va='center', ha='center')
    else:
        ax.text(x=40, y=80, s='XGoal Analysis',
                size=30,
                color=pitch.line_color,
                va='center', ha='center')

    

    plt.savefig(buf, format="png", bbox_inches='tight')

    plt.close()
    data = base64.b64encode(buf.getbuffer()).decode("utf8")  # encode to html elements
    return "data:image/png;base64,{}".format(data)



@app.callback(
    dash.dependencies.Output('table_top_scorers-output-container', 'children'),
    [dash.dependencies.Input('competition_select', 'value')],
    [dash.dependencies.Input('season_select', 'value')])
def update_table(selected_competition, selected_season):
    if selected_competition:
        dff = df[df["competition_name"].isin(selected_competition)]
        if selected_season:
            dff = dff[dff["season_name"].isin(selected_season)]
    elif selected_season:
        dff = df[df["season_name"].isin(selected_season)]
    else:
        dff = df
    return dbc.Table.from_dataframe(pd.concat([dff[["team_name", "player_name"]],
                                               dff['Goal'].groupby(dff['player_name']).transform('sum')],
                                              axis=1).drop_duplicates().sort_values("Goal",
                                                                                    ascending=False).head(7),
                                    striped=True,
                                    bordered=True, hover=True)


@app.callback(
    dash.dependencies.Output('card_number_shoots-output-container', 'children'),
    [dash.dependencies.Input('competition_select', 'value')],
    [dash.dependencies.Input('season_select', 'value')])
def update_table(selected_competition, selected_season):
    if selected_competition:
        dff = df[df["competition_name"].isin(selected_competition)]
        if selected_season:
            dff = dff[dff["season_name"].isin(selected_season)]
    elif selected_season:
        dff = df[df["season_name"].isin(selected_season)]
    else:
        dff = df

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
    [dash.dependencies.Input('season_select', 'value')])
def update_table(selected_competition, selected_season):
    if selected_competition:
        dff = df[df["competition_name"].isin(selected_competition)]
        if selected_season:
            dff = dff[dff["season_name"].isin(selected_season)]
    elif selected_season:
        dff = df[df["season_name"].isin(selected_season)]
    else:
        dff = df

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
    [dash.dependencies.Input('season_select', 'value')])
def update_table(selected_competition, selected_season):
    if selected_competition:
        dff = df[df["competition_name"].isin(selected_competition)]
        if selected_season:
            dff = dff[dff["season_name"].isin(selected_season)]
    elif selected_season:
        dff = df[df["season_name"].isin(selected_season)]
    else:
        dff = df

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
    dash.dependencies.Output('shoot_heatmap', 'src'),
    [dash.dependencies.Input('competition_select', 'value')],
    [dash.dependencies.Input('season_select', 'value')])
def update_table(selected_competition, selected_season):
    if selected_competition:
        dff = df[df["competition_name"].isin(selected_competition)]
        if selected_season:
            dff = dff[dff["season_name"].isin(selected_season)]
    elif selected_season:
        dff = df[df["season_name"].isin(selected_season)]
    else:
        dff = df

    mpl.rcParams.update({'text.color': "white",
                         'axes.labelcolor': "white"})

    buf = io.BytesIO()
    pitch = VerticalPitch(pitch_type='statsbomb', line_zorder=2,
                          pitch_color='#22312b', line_color='#efefef', half=True)
    # draw
    fig, ax = pitch.draw(nrows=1, ncols=2, figsize=(10, 6))
    fig.set_facecolor('#22312b')
    bin_statistic = pitch.bin_statistic(dff.X, dff.Y, statistic='count', bins=(45, 45))
    bin_statistic['statistic'] = gaussian_filter(bin_statistic['statistic'], 1)
    pcm = pitch.heatmap(bin_statistic, ax=ax[0], cmap='hot', edgecolors='#22312b')
#    cbar = fig.colorbar(pcm, ax=ax[0], shrink=0.3)
#    cbar.outline.set_edgecolor('#efefef')
#    cbar.ax.yaxis.set_tick_params(color='#efefef')
#    plt.setp(plt.getp(cbar.ax.axes, 'yticklabels'), color='#efefef')
    

    dff = dff[dff['Goal']]
    bin_statistic = pitch.bin_statistic(dff.X, dff.Y, statistic='count', bins=(45, 45))
    bin_statistic['statistic'] = gaussian_filter(bin_statistic['statistic'], 1)
    pcm = pitch.heatmap(bin_statistic, ax=ax[1], cmap='hot', edgecolors='#22312b')
#    cbar = fig.colorbar(pcm, ax=ax[1], shrink=0.3)

    ax[0].text(x=40, y=80, s='Shoots',
              size=30,
              color=pitch.line_color,
              va='center', ha='center')

    ax[1].text(x=40, y=80, s='Goals',
              size=30,
              color=pitch.line_color,
              va='center', ha='center')

    

    plt.savefig(buf, format="png", bbox_inches='tight')

    plt.close()
    data = base64.b64encode(buf.getbuffer()).decode("utf8")  # encode to html elements
    return "data:image/png;base64,{}".format(data)


@app.callback(dash.dependencies.Output('page_content', 'children'),
              [dash.dependencies.Input('url', 'pathname')])
def display_page(pathname):
    if pathname == '/':
        return container
    if pathname == '/heat_map':
        return container_2


if __name__ == '__main__':
    app.run_server(port=3000, debug=True)
