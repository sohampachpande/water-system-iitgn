import dash
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
import numpy as np
import plotly.graph_objs as go
from datetime import datetime as dt
from datetime import timedelta
import time
import sqlite3


def epoch_timestring(epoch_time):
    return time.strftime('%H:%M:%S', time.localtime(int(epoch_time)))


def date_epoch(date_string):
    utc_time = dt.strptime(date_string, "%Y-%m-%d")
    epoch_start_time = utc_time.timestamp()
    return epoch_start_time + 900, epoch_start_time + 86400


def daterange(start_date, end_date):
    for n in range(int((end_date - start_date).days)):
        yield start_date + timedelta(n)


external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

app.layout = html.Div([
    html.Div([
        html.H1(
            children='IIT Gandhinagar Water Network',
            style={'margin-left': '1%'}),
        html.P(
            'Please select water station from dropdown menus',
            style={'margin-left': '1%'}),
        html.Div([
            dcc.Dropdown(
                id='station',
                options=[{
                    'label': i,
                    'value': i
                } for i in ['CWPS', 'WSC-1-Fresh', 'WSC-1-Recycle']],
                placeholder="Select Source",
            )
        ],
                 style={
                     'width': '20%',
                     'margin-left': '1%',
                     'display': 'inline-block'
                 }),
        html.Div(
            [
                dcc.DatePickerSingle(
                    id='my-date-picker-single',
                    min_date_allowed=dt(2019, 3, 2),
                    max_date_allowed=dt(2019, 3, 8),
                    initial_visible_month=dt(2019, 3, 3)
                    # date=dt(2019, 3, 3)
                )
            ],
            style={
                'width': '20%',
                'margin-left': '1%'
            })
    ]),
    html.Div([dcc.Graph(id='indicator-graphic')], style={'width': '90%'})
])


@app.callback(
    dash.dependencies.Output('indicator-graphic', 'figure'), [
        dash.dependencies.Input('station', 'value'),
        dash.dependencies.Input('my-date-picker-single', 'date')
    ])
def update_graph(station, date):

    if date is not None:
        conn = sqlite3.connect('water_data.db')
        cursor = conn.cursor()
        print(date)

        date_string = date

        start_epoch, end_epoch = date_epoch(date_string)

        np_flow = []

        if station == 'CWPS':
            cursor.execute(
                'SELECT timeEpoch, Current_Flow, Daily_Flow FROM cwps WHERE timeEpoch>{} AND timeEpoch<{}'
                .format(start_epoch, end_epoch))
            np_flow = np.asarray(cursor.fetchall())

        elif station == 'WSC-1-Fresh':
            cursor.execute(
                'SELECT timeEpoch, current_flow, daily_flow FROM wsc1_fwp WHERE timeEpoch>{} AND timeEpoch<{}'
                .format(start_epoch, end_epoch))
            np_flow = np.asarray(cursor.fetchall())

        else:
            cursor.execute(
                'SELECT timeEpoch, current_flow, daily_flow FROM wsc1_rwp WHERE timeEpoch>{} AND timeEpoch<{}'
                .format(start_epoch, end_epoch))
            np_flow = np.asarray(cursor.fetchall())

        list_time = list(map(epoch_timestring, list(np_flow[:, 0])))

        return {
            'data': [
                go.Scatter(
                    x=list_time,
                    y=np_flow[:, 1],
                    name='Current Flow',
                    mode='lines+markers',
                    marker={
                        'size': 1,
                        'opacity': 0.5,
                        'line': {
                            'width': 0.1,
                            'color': 'white'
                        }
                    }),
                go.Scatter(
                    x=list_time,
                    y=np_flow[:, 2],
                    name='Daily Flow',
                    mode='lines+markers',
                    marker={
                        'size': 1,
                        'opacity': 0.25,
                        'line': {
                            'width': 0.1,
                            'color': 'white'
                        }
                    })
            ],
            'layout':
            go.Layout(
                xaxis={'title': 'Time'},
                yaxis={'title': 'Flow'},
                # margin={'l': 50, 'b': 100, 't': 100, 'r': 50},
                height=700,
                hovermode='closest')
        }


if __name__ == '__main__':
    app.run_server(debug=True)