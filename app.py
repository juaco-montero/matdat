#!/usr/bin/env python

"""matdat.py: Plotly based analyse tool for specific material data."""

__author__ = "Christoph Jahnke"
__copyright__ = "Copyright 2020, Universität der Bundeswehr"
__credits__ = ["Christoph Jahnke"]
__license__ = "GPL"
__version__ = "1.0.0"
__maintainer__ = "Christoph Jahnke"
__email__ = "jahnke.mailbox@gmx.de"
__status__ = "Testing"


import dash
import dash_html_components as html

import dash_daq as daq
import dash_core_components as dcc
import plotly.express as px
import plotly.graph_objects as go

from dash.dependencies import Input, Output

import pandas as pd
external_stylesheets = ['https://codepen.io/anon/pen/mardKv.css']

#Load the CSV Data
df = pd.read_csv('propertiesmap-v2.csv')

# Initialise the app
app = dash.Dash(__name__)

# Associating server
server = app.server
app.title = 'matdat - UNIBW'
app.config.suppress_callback_exceptions = True

#Compare Options for graphselector
all_options = {
    'Tensile : Yield': ['Ductility_Percentage', 'Yield_Mpa'],
    'Tensile : UTS': ['Ductility_Percentage', 'UTS_Mpa'],
    }

##################################################
# INFO TABLE
##################################################

def update_info_table():
    fig = go.Figure(data=[go.Table(
    header=dict(values=list(['Author', 'LPBF System', 'Laser Power [W]', 'Scanning Speed [mm/s]', 'Layer Height [μm]']),
                line_color='darkslategray',
                fill_color='lightskyblue',
                font = dict(color = 'darkslategray', size = 14),
                align='left'),
    cells=dict(values=list(['', '', '', '', '']),
               line_color='darkslategray',
                fill_color='lightskyblue',
                font = dict(color = 'darkslategray', size = 14),
               align='left')
    )
    ])
    fig.update_layout(
            colorway=["#03f2ff", '#FF4F00', '#375CB1', '#FF7400', '#FFF400', '#FF0056'],
            template='plotly_dark',
            paper_bgcolor='rgba(0, 0, 0, 0)',
            plot_bgcolor='rgba(0, 0, 0, 0)',
            margin={'b': 15},
            autosize=True,)
    
    return fig
##################################################


# Define the app style={'textAlign': 'center', 'color': '#ffbc03'}
app.layout = html.Div(children=[
        html.Div(className='div-user-controls', children=[
                html.H1('Laser Powder Bed Fusion Material Properties', style={'textAlign': 'center'}),
                html.Div(className='four columns', style={'padding-top': '64px'}, children=[
                dcc.Dropdown(
                        id='graphselector', 
                        className='div-for-dropdown',
                        options=[{'label': k, 'value': k} for k in all_options.keys()], 
                        value='Tensile : Yield',
                        clearable=False
                        ), 
                html.Div(className='div-for-dropdown', children=[
                html.Span('Error', className='two-columns', style={'float': 'left'}),
                daq.BooleanSwitch(
                                id='error_switch',
                                on=True,
                                style={'float': 'right'}
                                )
                ])
                ])
                        ]),
                    
                      html.Div(className='row',  # Define the row element
                               children=[
                                # Define the left element
                                  html.Div(className='eight columns div-for-charts ',
                                           children=[
                                                   html.H4('Material Properties of L-PBF Ti6V4Al'),
                                                   html.H5('Produced via Laser Power bed Fusion'),
                                               dcc.Graph(
                                                       id='graph_main',
                                                       style={'padding-top': '-30px'},
                                                       hoverData={'points': [{'curveNumber': 0, 'pointNumber': 10, 'pointIndex': 10, 'x': 1.9, 'y': 900}]}, 
                                                       config={'displayModeBar': False}
                                                       )
                                               ]
                                                ),  
                                  # Define the right element
                                  html.Div(className='four columns div-for-charts',
                                           children=[
                                                   html.H4('Termal History in Post-Processing'),
                                                   html.H5('Post Termal Processing Type:x'),
                                                   dcc.Graph(id='graph_temp', config={'displayModeBar': False})
                                                    ]),
                                  ]),
                                           
                                                html.Table(
                                                        className='eleven columns div-user-controls', 
                                                        children=[
                                                                dcc.Graph(id='info_table',figure = update_info_table(), config={'displayModeBar': False})
                                                                ]
                                                        )
                                ])


#The Callback
@app.callback(Output('graph_main', 'figure'),
              [Input('graphselector', 'value'), Input('error_switch', 'on')])
def update_main_graph(selected_dropdown_value, error_on):
    dff = df
  #  print(errorselect)
    figure = go.Figure(
        data=go.Scatter(
            x=dff[f'{all_options[selected_dropdown_value][0]}'],
            y=dff[f'{all_options[selected_dropdown_value][1]}'],
            error_y=dict(
            type='data', # value of error bar given in data coordinates
            array=dff[f'{all_options[selected_dropdown_value][1]}_Error'],
            visible=error_on),
            error_x=dict(
            type='data', # value of error bar given in data coordinates
            array=dff[f'{all_options[selected_dropdown_value][0]}_Error'],
            visible=error_on),
            mode='markers',),
        layout=go.Layout(
            colorway=["#ffbc03", '#FF4F00', '#375CB1', '#FF7400', '#FFF400', '#FF0056'],
            template='plotly_dark',
            paper_bgcolor='rgba(0, 0, 0, 0)',
            plot_bgcolor='rgba(0, 0, 0, 0)',
            margin={'b': 15},
         #   hovermode='x',
            autosize=True,
            ))
    figure.update_xaxes(title=f'{all_options[selected_dropdown_value][0]}')
    figure.update_yaxes(title=f'{all_options[selected_dropdown_value][1]}')
    
    return figure

##############################################
#FUNCTION THAT HANDLE HOVER DATA TO TEMP GRAPH
##############################################
@app.callback(
    dash.dependencies.Output('graph_temp', 'figure'),
    [dash.dependencies.Input('graph_main', 'hoverData'),
     ])
def update_y_timeseries(hoverData):
    dff=df
  #  print(hoverData)
    work = hoverData['points'][0]['pointIndex']
    back = dff.iloc[work:(work+1), 1:5]
    temp1 = back.iloc[0,0]
    temp2 = back.iloc[0,2]
    time1 = back.iloc[0,1]
    time2 = back.iloc[0,3]
    post_processing = (dff.iloc[work:(work+1),25:26]).iloc[0,0]
    back_new = pd.DataFrame({'temp': [temp1, temp1, temp2], 
                             'time': [0, time1, time2]},
                            index=['1', '2', '3'])
    return create_time_series(back_new, post_processing)
##############################################

##################################
# FUNCTION FOR PLOTTING TEMP GRAPH
##################################
def create_time_series(back_new, post_processing):
    #print(post_processing)
    
    # set up plotly figure
    figure = go.Figure()
    # add line / trace 1 to figure
    figure.add_trace(go.Scatter(
        x=back_new['time'],
        y=back_new['temp'],
        mode='lines+markers',
        connectgaps=True,
        hovertemplate =
        '<br><b>Time</b>: %{x} h<br>'+
        '<br><b>Temp</b>: %{y} °C<br>',
         showlegend=False,
    ))
    figure.update_xaxes(title='Time[h]')
    figure.update_yaxes(title='Temperature[°C]')
    #text = ('Thermal history in Post-Processing <br> Post Processing type : ' + post_processing)
   # print(text)
    figure.update_layout(
            #title=text,
            colorway=["#03f2ff", '#FF4F00', '#375CB1', '#FF7400', '#FFF400', '#FF0056'],
            template='plotly_dark',
            paper_bgcolor='rgba(0, 0, 0, 0)',
            plot_bgcolor='rgba(0, 0, 0, 0)',
            margin={'b': 15},
            hovermode='x',
            autosize=True,)
    return figure
###################################
#############
# HOVER TABLE
#############
#@app.callback(
#    dash.dependencies.Output('hover_table', 'figure'),
#    [dash.dependencies.Input('graph_main', 'hoverData'),
#     Input('graphselector', 'value')
#     ])
#def update_hovertable(hoverData, value):
#    dff=df
#    #print(all_options[value][0])
#    work = hoverData['points'][0]['pointIndex']
#    #print(dff.at[work,f'{all_options[value][0]}'])
#    back = []
#    val1 = dff.at[work,f'{all_options[value][0]}']
#    back.append(val1)
#    val2 = dff.at[work,f'{all_options[value][1]}']
#    back.append(val2)
#    val3 = dff.at[work,'post_processing']
#    back.append(val3)
#    #print(back)
#    
#    return create_hover_table(back, value)
#
#def create_hover_table(back, value):
#    dff=df
#    fig = go.Figure(data=[go.Table(
#    header=dict(values=list([f'{all_options[value][0]}', f'{all_options[value][1]}', 'Post Processing']),
#                line_color='darkslategray',
#                fill_color='lightskyblue',
#                font = dict(color = 'darkslategray', size = 14),
#                align='left'),
#    cells=dict(values=list([f'{(back[0])}', f'{(back[1])}', f'{(back[2])}']),
#               line_color='darkslategray',
#                fill_color='lightskyblue',
#                font = dict(color = 'darkslategray', size = 14),
#               align='left')
#    )
#    ])
#    fig.update_layout(
#            title='Information about the Datapoint:',
#            colorway=["#03f2ff", '#FF4F00', '#375CB1', '#FF7400', '#FFF400', '#FF0056'],
#            template='plotly_dark',
#            paper_bgcolor='rgba(0, 0, 0, 0)',
#         #   plot_bgcolor='rgba(0, 0, 0, 0)',
#            margin={'b': 15},
#            height=200,
#            autosize=True,)
#    return fig
#############



# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)
