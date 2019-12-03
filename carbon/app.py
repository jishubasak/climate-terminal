import os
import numpy as np
import pandas as pd
import logging

import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go

from dash.dependencies import Input, Output, State
from IPython.display import display, IFrame, HTML

# turn off web logs
os.environ['FLASK_ENV'] = 'development'
logger = logging.getLogger('werkzeug')  # WSGI - web server gateway interface
logger.setLevel(logging.ERROR)

# adding __name__ fixes 'no css' issue
# app = dash.Dash(__name__, static_folder='assets/')
# app = dash.Dash(static_folder='assets/')

# External CSS
external_stylesheets=["assets/plotly_dash.css", "assets/bootstrap.min.css", "assets/custom.css"]

# Initializing the Default Constructor of Dash Framework and the Application
app = dash.Dash(__name__,  external_stylesheets=external_stylesheets)

# app = dash.Dash()
server = app.server

# read the GDP csv
df = pd.read_csv('dataset_pred.csv')
df.set_index('country_code', inplace=True)

min_year = 2012
max_year = 2020


def get_map_figure(year, colorstyle=0):
    '''Returns a map figure.
    Generates a map figure of all countries with their carbon parts per billion by volume (ppbv)
    as a determinant of the colors that will be used to represent those 
    countries. The map is that of the year that was passed as first parameter,  
    and the colorstyle used is based on the integer vlaue passed as second 
    paramater
    Parameters
    ----------
    year : int
        The year of the map.
    colorstyle : {0, 1}, optional
        The color style to be used. 0 is the default value and it uses the 
        colors ranging from red to purple. The value 1 just uses different
        hues of the color purple.
    Returns
    -------
    dict
        Return a map figure
    '''
    if colorstyle == 0:
        colorscale = [[0, "rgb(178, 34, 34)"], [1, "rgb(225, 215, 0)"]]
    elif colorstyle == 1:
        colorscale = [[1-(1/10)*10**(1), "rgb(103, 11, 99)"],
                      [1-(1/10)*10**(4/5), "rgb(145,40,140)"],
                      [1-(1/10)*10**(3/5), "rgb(168,60,163)"],
                      [1-(1/10)*10**(2/5), "rgb(206,101,201)"],
                      [1-(1/10)*10**(1/5), "rgb(221,135,218)"],
                      [1, "rgb(232,185,230)"]]
        
    data = [dict(
        type='choropleth',
        locations=df.index,
        z=df[str(year)],
        text=df['country'],
        colorscale=colorscale,
        autocolorscale=False,
        reversescale=True,
        marker=dict(
            line=dict(
                color='rgb(180,180,180)',
                width=0.9
            )),
        colorbar=dict(
            autotick=False,
            lenmode='fraction',
            len=0.8,
            thicknessmode='pixels',
            thickness=15,
            xanchor='right',
            y=0.5,
            x=0,
        ),

    )]

    layout = dict(
        title='Carbon parts per billion by volume (ppbv) ({})'.format(year),
        geo=dict(
            showframe=True,
            showcoastlines=False,
            projection=dict(
                type='Mercator'
            ),
            showocean=True,
            oceancolor='#0eb3ef',
        ),
        plot_bgcolor='#1A1C23',        
        paper_bgcolor='#1A1C23',
        font=dict(color='white')
    )

    fig = dict(data=data, layout=layout)
    return fig


def create_slider(id, value):
    '''Create a slider component.
    Creates a slider component with an id and initial value of the two 
    parameters passed to this function.
    Parameters
    ----------
    id : int
        The id of the slider component.
    value : int
        Accepts a value ranging from min_year to max_year. This is the initial value
        of the slider component.
        
    Returns
    -------
    dcc.Slider
        Return a slider component
    '''
    return dcc.Slider(
        id=id,
        min=min_year,
        max=max_year,
        step=1,
        value=value,
        marks={str(i): i for i in range(min_year, max_year)},
        className='year-slider'
    )

# resets the callbacks
app.callback_map = {} 
# sets the title
app.title = 'Carbon Statistics'
# html content
app.layout = html.Div([
    html.Div([
        html.H1(id='header', children='Carbon Insight Dashboard'),
        html.Div(id='sub-header'),
        html.Br(),
        html.Div([
            html.Span(children='''Carbon insights allow the user to view carbon emissions 
                that each country emits annually (measured in Carbon parts per billion by volume). 
                Users may scroll through the years and click/hover above any country to 
                know carbon emission trends throughout the years. Users may use the 
                information to derive local or regional actions that ultimately lower 
                the carbon emissions of the world.''')
        
        ], id="intro"),
    ], id='intro-section'),
    html.Div([
        dcc.Tabs([
            # Tab 1
            dcc.Tab([
                html.Div(id="graph-guide-text", className="tab-content top",
                         children='''The graphs are interactive. You can move 
                             the slider to show the carbon ppbv for a given 
                             year. You can also click on a country to display 
                             the carbon ppbv trends.'''),
                html.Div([
                    html.Div(id="year-slider-label",
                             className="year-slider-label", children="Year"),
                    create_slider('year-slider', 2017),
                    html.Div(id="year-slider-value",
                             className="year-slider-value")
                ], className="row justify-content-md-center \
                                align-items-center"),
                html.Div([
                    html.Div([
                        html.Div([
                            dcc.Graph(id="world-map", className="map")
                        ]),
                        html.Div(id='text-output')
                    ], className="col-left col-lg-7"),
                    html.Div([
                        dcc.Graph(id='country-gdp-graph')
                    ], className="col-right col-lg-5 v-center"),
                ], className="row align-items-center content-tab1")
            ], className="container-fluid", label="Overview",
                selected_style={
                    "border": "#1A1C23",
                    "primary": "#1A1C23",
                    "background": "#1A1C23",
                    "color": "white",
                }),
            # Tab 2
            dcc.Tab([
                html.Div([
                    html.Span(children='''To be implemented''')
                ])
            ], className="container-fluid",
                label="Insights",
                selected_style={
                    "border": "#1A1C23",
                    "primary": "#1A1C23",
                    "background": "#1A1C23",
                    "color": "white",
                })
        ], className="tabs-section",
            colors={
                "border": "#42454B",
                "primary": "#42454B",
                "background": "#42454B"
            })
    ], className="main-content"),
], className="main")


@app.callback(Output('world-map', 'figure'),
              [Input('year-slider', 'value')])
def update_map_1(year):
    '''Update the map in Tab 1 when slider in Tab 1 is used.
    A callback function that is triggered when the slider in Tab 1 is used.
    The function uses the slider value as input to the get_map_figure function
    and returns the generated map figure to the map in Tab 1.
    Parameters
    ----------
    year : int
        The year of the map.
    Returns
    -------
    dict
        Return a map figure
    '''
    return get_map_figure(year)

@app.callback(Output('year-slider-value', 'children'),
              [Input('year-slider', 'value')])
def update_year_value(year):
    '''Update the year label for the slider in Tab 1.
    A callback function that is triggered when the slider in Tab 1 is 
    used. The function uses the slider value to update the year label beside
    the slider component.
    Parameters
    ----------
    year : int
        The value of the slider.
    Returns
    -------
    str
        Return the updated year
    '''
    return str(year)

@app.callback(Output('country-gdp-graph', 'figure'),
              [Input('world-map', 'clickData')])
def update_graph(clickData):
    '''Update the carbon ppbv trend graph in Tab 1.
    A callback function that is triggered when a country in the map in Tab 1 is 
    clicked. The country is retrieved from the clickData and is then used to 
    generate a line graph showing the trends in carbon ppbv of a country
    across all years.
    Parameters
    ----------
    clickData : dict
        The dictionary containing the details of the clicked point on the map.
    Returns
    -------
    dict
        Return the updated carbon ppbv trend graph figure
    '''
    title = ''
    data = []
    if clickData:
        country = clickData['points'][0]['location']
    else:
        country = 'USA'
    data = [{'x': df.iloc[:, 1:].columns.tolist(),
             'y': df.loc[country].iloc[1:].values.tolist(),
             'type': 'line'}]
    title = df.loc[country, 'country']
    layout = dict(title='{} Carbon ppbv'.format(title),
                  xaxis={'title': 'year'},
                  yaxis={'title': 'Carbon ppbv'},
                    plot_bgcolor='#1A1C23',        
                    paper_bgcolor='#1A1C23',
                    font=dict(color='white')
                  )
    fig = dict(data=data, layout=layout)
    return fig


if __name__ == '__main__':
    app.css.config.serve_locally = True
    app.scripts.config.serve_locally = True
    port = int(os.environ.get('PORT', 5000))
    app.run_server(port=port, debug=False)
























# import os
# import numpy as np
# import pandas as pd
# import logging

# import dash
# import dash_core_components as dcc
# import dash_html_components as html
# import plotly.graph_objs as go

# from dash.dependencies import Input, Output, State
# from IPython.display import display, IFrame, HTML

# # turn off web logs
# os.environ['FLASK_ENV'] = 'development'
# logger = logging.getLogger('werkzeug')  # WSGI - web server gateway interface
# logger.setLevel(logging.ERROR)

# # adding __name__ fixes 'no css' issue
# # app = dash.Dash(__name__, static_folder='assets/')
# # app = dash.Dash(static_folder='assets/')

# # External CSS
# external_stylesheets=["assets/plotly_dash.css", "assets/bootstrap.min.css", "assets/custom.css"]

# # Initializing the Default Constructor of Dash Framework and the Application
# app = dash.Dash(__name__,  external_stylesheets=external_stylesheets)

# # app = dash.Dash()
# server = app.server

# # read the GDP csv
# df = pd.read_csv('dataset_pred.csv')
# df.set_index('country_code', inplace=True)

# min_year = 2012
# max_year = 2020


# def get_map_figure(year, colorstyle=0):
#     '''Returns a map figure.
#     Generates a map figure of all countries with their carbon parts per billion by volume (ppbv)
#     as a determinant of the colors that will be used to represent those 
#     countries. The map is that of the year that was passed as first parameter,  
#     and the colorstyle used is based on the integer vlaue passed as second 
#     paramater
#     Parameters
#     ----------
#     year : int
#         The year of the map.
#     colorstyle : {0, 1}, optional
#         The color style to be used. 0 is the default value and it uses the 
#         colors ranging from red to purple. The value 1 just uses different
#         hues of the color purple.
#     Returns
#     -------
#     dict
#         Return a map figure
#     '''
#     if colorstyle == 0:
#         colorscale = [[0, "rgb(178, 34, 34)"], [1, "rgb(225, 215, 0)"]]
#     elif colorstyle == 1:
#         colorscale = [[1-(1/10)*10**(1), "rgb(103, 11, 99)"],
#                       [1-(1/10)*10**(4/5), "rgb(145,40,140)"],
#                       [1-(1/10)*10**(3/5), "rgb(168,60,163)"],
#                       [1-(1/10)*10**(2/5), "rgb(206,101,201)"],
#                       [1-(1/10)*10**(1/5), "rgb(221,135,218)"],
#                       [1, "rgb(232,185,230)"]]
        
#     data = [dict(
#         type='choropleth',
#         locations=df.index,
#         z=df[str(year)],
#         text=df['country'],
#         colorscale=colorscale,
#         autocolorscale=False,
#         reversescale=True,
#         marker=dict(
#             line=dict(
#                 color='rgb(180,180,180)',
#                 width=0.9
#             )),
#         colorbar=dict(
#             autotick=False,
#             lenmode='fraction',
#             len=0.8,
#             thicknessmode='pixels',
#             thickness=15,
#             xanchor='right',
#             y=0.5,
#             x=0,
#         ),

#     )]

#     layout = dict(
#         title='Carbon parts per billion by volume (ppbv) ({})'.format(year),
#         geo=dict(
#             showframe=True,
#             showcoastlines=False,
#             projection=dict(
#                 type='Mercator'
#             ),
#             showocean=True,
#             oceancolor='#0eb3ef',
#         )
#     )

#     fig = dict(data=data, layout=layout)
#     return fig


# def create_slider(id, value):
#     '''Create a slider component.
#     Creates a slider component with an id and initial value of the two 
#     parameters passed to this function.
#     Parameters
#     ----------
#     id : int
#         The id of the slider component.
#     value : int
#         Accepts a value ranging from min_year to max_year. This is the initial value
#         of the slider component.
        
#     Returns
#     -------
#     dcc.Slider
#         Return a slider component
#     '''
#     return dcc.Slider(
#         id=id,
#         min=min_year,
#         max=max_year,
#         step=1,
#         value=value,
#         marks={str(i): i for i in range(min_year, max_year)},
#         className='year-slider'
#     )

# # resets the callbacks
# app.callback_map = {} 
# # sets the title
# app.title = 'A.I.R.'
# # html content
# app.layout = html.Div([
#     html.Div([
#         html.H1(id='header', children='Carbon Insight Dashboard'),
#         html.Div(id='sub-header'),
#         html.Br(),
#         html.Div([
#             html.Span(children='''Carbon insights allow the user to view carbon emissions 
#                 that each country emits annually (measured in Carbon parts per billion by volume). 
#                 Users may scroll through the years and click/hover above any country to 
#                 know carbon emission trends throughout the years. Users may use the 
#                 information to derive local or regional actions that ultimately lower 
#                 the carbon emissions of the world.''')
        
#         ], id="intro"),
#     ], id='intro-section'),
#     html.Div([
#         dcc.Tabs([
#             # Tab 1
#             dcc.Tab([
#                 html.Div(id="graph-guide-text", className="tab-content top",
#                          children='''The graphs are interactive. You can move 
#                              the slider to show the carbon ppbv for a given 
#                              year. You can also click on a country to display 
#                              the carbon ppbv trends.'''),
#                 html.Div([
#                     html.Div(id="year-slider-label",
#                              className="year-slider-label", children="Year"),
#                     create_slider('year-slider', 2017),
#                     html.Div(id="year-slider-value",
#                              className="year-slider-value")
#                 ], className="row justify-content-md-center \
#                                 align-items-center"),
#                 html.Div([
#                     html.Div([
#                         html.Div([
#                             dcc.Graph(id="world-map", className="map")
#                         ]),
#                         html.Div(id='text-output')
#                     ], className="col-left col-lg-7"),
#                     html.Div([
#                         dcc.Graph(id='country-gdp-graph')
#                     ], className="col-right col-lg-5 v-center"),
#                 ], className="row align-items-center content-tab1")
#             ], className="container-fluid", label="Overview"),
#             # Tab 2
#             dcc.Tab([
#                 html.Div([
#                     html.Span(children='''To be implemented''')
#                 ])
#             ], className="container-fluid",
#                 label="Insights")
#         ], className="tabs-section")
#     ], className="main-content"),
# ], className="main")


# @app.callback(Output('world-map', 'figure'),
#               [Input('year-slider', 'value')])
# def update_map_1(year):
#     '''Update the map in Tab 1 when slider in Tab 1 is used.
#     A callback function that is triggered when the slider in Tab 1 is used.
#     The function uses the slider value as input to the get_map_figure function
#     and returns the generated map figure to the map in Tab 1.
#     Parameters
#     ----------
#     year : int
#         The year of the map.
#     Returns
#     -------
#     dict
#         Return a map figure
#     '''
#     return get_map_figure(year)

# @app.callback(Output('year-slider-value', 'children'),
#               [Input('year-slider', 'value')])
# def update_year_value(year):
#     '''Update the year label for the slider in Tab 1.
#     A callback function that is triggered when the slider in Tab 1 is 
#     used. The function uses the slider value to update the year label beside
#     the slider component.
#     Parameters
#     ----------
#     year : int
#         The value of the slider.
#     Returns
#     -------
#     str
#         Return the updated year
#     '''
#     return str(year)

# @app.callback(Output('country-gdp-graph', 'figure'),
#               [Input('world-map', 'clickData')])
# def update_graph(clickData):
#     '''Update the carbon ppbv trend graph in Tab 1.
#     A callback function that is triggered when a country in the map in Tab 1 is 
#     clicked. The country is retrieved from the clickData and is then used to 
#     generate a line graph showing the trends in carbon ppbv of a country
#     across all years.
#     Parameters
#     ----------
#     clickData : dict
#         The dictionary containing the details of the clicked point on the map.
#     Returns
#     -------
#     dict
#         Return the updated carbon ppbv trend graph figure
#     '''
#     title = ''
#     data = []
#     if clickData:
#         country = clickData['points'][0]['location']
#     else:
#         country = 'USA'
#     data = [{'x': df.iloc[:, 1:].columns.tolist(),
#              'y': df.loc[country].iloc[1:].values.tolist(),
#              'type': 'line'}]
#     title = df.loc[country, 'country']
#     layout = dict(title='{} Carbon ppbv'.format(title),
#                   xaxis={'title': 'year'},
#                   yaxis={'title': 'Carbon ppbv'}
#                   )
#     fig = dict(data=data, layout=layout)
#     return fig


# if __name__ == '__main__':
#     app.css.config.serve_locally = True
#     app.scripts.config.serve_locally = True
#     port = int(os.environ.get('PORT', 5000))
#     app.run_server(port=port, debug=False)