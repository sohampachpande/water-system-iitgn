import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
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


def downsample(data, factor):
    np_data = np.asarray(data)
    np_sliced = np_data[::factor]

    return np_sliced

from app import app

layout = html.Div([
    html.Div([
        html.H1(
            children='IIT Gandhinagar Water Network - Daily Consumption',
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
                } for i in ['all', 'CWPS', 'WSC-1-Fresh', 'WSC-1-Recycle']],
                placeholder="Select Source",
            )
        ],
                 style={
                     'width': '20%',
                     'margin-left': '1%',
                     'display': 'inline-block'
                 }),
        html.Div([
            dcc.Dropdown(
                id='flow_type',
                options=[{
                    'label': i,
                    'value': i
                } for i in ['all', 'daily', 'current']],
                placeholder="Select Flow type",
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
                    max_date_allowed=dt(2019, 3, 18),
                    initial_visible_month=dt(2019, 3, 3)
                    # date=dt(2019, 3, 3)
                )
            ],
            style={
                'width': '20%',
                'margin-left': '1%'
            })
    ]),
    html.Div([dcc.Graph(id='indicator-graphic')], style={'width': '90%'}),
    dcc.Link('Go back to home', href='/home')
])


@app.callback(
    dash.dependencies.Output('indicator-graphic', 'figure'), [
        dash.dependencies.Input('station', 'value'),
        dash.dependencies.Input('flow_type', 'value'),
        dash.dependencies.Input('my-date-picker-single', 'date')
    ])
def update_graph(station, flow_type, date):
    sampling_f = 10

    if date is not None:
        conn = sqlite3.connect('water_data.db')
        cursor = conn.cursor()
        print(date)

        date_string = date

        start_epoch, end_epoch = date_epoch(date_string)

        np_flow = []
        np_flow_cwps, np_flow_wsc1_fw, np_flow_wsc1_rw = [], [], []

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

        elif station == 'WSC-1-Recycle':
            cursor.execute(
                'SELECT timeEpoch, current_flow, daily_flow FROM wsc1_rwp WHERE timeEpoch>{} AND timeEpoch<{}'
                .format(start_epoch, end_epoch))
            np_flow = np.asarray(cursor.fetchall())

        else:
            cursor.execute(
                'SELECT timeEpoch, Current_Flow, Daily_Flow FROM cwps WHERE timeEpoch>{} AND timeEpoch<{}'
                .format(start_epoch, end_epoch))
            np_flow_cwps = np.asarray(cursor.fetchall())

            cursor.execute(
                'SELECT timeEpoch, current_flow, daily_flow FROM wsc1_fwp WHERE timeEpoch>{} AND timeEpoch<{}'
                .format(start_epoch, end_epoch))
            np_flow_wsc1_fw = np.asarray(cursor.fetchall())

            cursor.execute(
                'SELECT timeEpoch, current_flow, daily_flow FROM wsc1_rwp WHERE timeEpoch>{} AND timeEpoch<{}'
                .format(start_epoch, end_epoch))
            np_flow_wsc1_rw = np.asarray(cursor.fetchall())

        if station == 'all':
            list_time = list(map(epoch_timestring, list(np_flow_cwps[:, 0])))
            list_time = downsample(list_time, sampling_f)
            if flow_type == 'all':
                return {
                    'data': [
                        go.Scatter(
                            x=list_time,
                            y=downsample(np_flow_cwps[:, 1], sampling_f),
                            name='CWPS Current Flow',
                        ),
                        go.Scatter(
                            x=list_time,
                            y=downsample(np_flow_cwps[:, 2], sampling_f),
                            name='CWPS Daily Flow',
                        ),
                        go.Scatter(
                            x=list_time,
                            y=downsample(np_flow_wsc1_rw[:, 1], sampling_f),
                            name='WSC-1-Recycle Current Flow',
                        ),
                        go.Scatter(
                            x=list_time,
                            y=downsample(np_flow_wsc1_rw[:, 2], sampling_f),
                            name='WSC-1-Recycle Daily Flow',
                        ),
                        go.Scatter(
                            x=list_time,
                            y=downsample(np_flow_wsc1_rw[:, 1], sampling_f) +
                            downsample(np_flow_wsc1_fw[:, 1], sampling_f),
                            name='WSC-1 Fresh+Recycle Current Flow',
                        ),
                        go.Scatter(
                            x=list_time,
                            y=downsample(np_flow_wsc1_rw[:, 2], sampling_f) +
                            downsample(np_flow_wsc1_fw[:, 2], sampling_f),
                            name='WSC-1 Fresh+Recycle Daily Flow',
                        ),
                        go.Scatter(
                            x=list_time,
                            y=downsample(np_flow_wsc1_fw[:, 1], sampling_f),
                            name='WSC-1-Fresh Current Flow',
                        ),
                        go.Scatter(
                            x=list_time,
                            y=downsample(np_flow_wsc1_fw[:, 2], sampling_f),
                            name='WSC-1-Fresh Daily Flow',
                        )
                    ],
                    'layout':
                    go.Layout(
                        xaxis={'title': 'Time'},
                        yaxis={'title': 'Flow'},
                        # margin={'l': 50, 'b': 100, 't': 100, 'r': 50},
                        height=700,
                        hovermode='closest')
                }
            elif flow_type == 'current':
                return {
                    'data': [
                        go.Scatter(
                            x=list_time,
                            y=downsample(np_flow_cwps[:, 1], sampling_f),
                            name='CWPS Current Flow',
                        ),
                        go.Scatter(
                            x=list_time,
                            y=downsample(np_flow_wsc1_rw[:, 1], sampling_f),
                            name='WSC-1-Recycle Current Flow',
                        ),
                        go.Scatter(
                            x=list_time,
                            y=downsample(np_flow_wsc1_rw[:, 1], sampling_f) +
                            downsample(np_flow_wsc1_fw[:, 1], sampling_f),
                            name='WSC-1 Fresh+Recycle Current Flow',
                        ),
                        go.Scatter(
                            x=list_time,
                            y=downsample(np_flow_wsc1_fw[:, 1], sampling_f),
                            name='WSC-1-Fresh Current Flow',
                        ),
                    ],
                    'layout':
                    go.Layout(
                        xaxis={'title': 'Time'},
                        yaxis={'title': 'Flow'},
                        # margin={'l': 50, 'b': 100, 't': 100, 'r': 50},
                        height=700,
                        hovermode='closest')
                }
            else:
                return {
                    'data': 
                    [
                        go.Scatter(
                            x=list_time,
                            y=downsample(np_flow_cwps[:, 2], sampling_f),
                            name='CWPS Daily Flow',
                        ),
                        go.Scatter(
                            x=list_time,
                            y=downsample(np_flow_wsc1_rw[:, 2], sampling_f),
                            name='WSC-1-Recycle Daily Flow',
                        ),
                        go.Scatter(
                            x=list_time,
                            y=downsample(np_flow_wsc1_rw[:, 2], sampling_f) +
                            downsample(np_flow_wsc1_fw[:, 2], sampling_f),
                            name='WSC-1 Fresh+Recycle Daily Flow',
                        ),
                        go.Scatter(
                            x=list_time,
                            y=downsample(np_flow_wsc1_fw[:, 2], sampling_f),
                            name='WSC-1-Fresh Daily Flow',
                        )
                    ],
                    'layout':
                    go.Layout(
                        xaxis={'title': 'Time'},
                        yaxis={'title': 'Flow'},
                        # margin={'l': 50, 'b': 100, 't': 100, 'r': 50},
                        height=700,
                        hovermode='closest')
                }

        else:
            list_time = list(map(epoch_timestring, list(np_flow[:, 0])))
            list_time = downsample(list_time, sampling_f)
            return {
                'data': [
                    go.Scatter(
                        x=list_time,
                        y=downsample(np_flow[:, 1], sampling_f),
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
                        y=downsample(np_flow[:, 2], sampling_f),
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
    else:
        dash.no_update


if __name__ == '__main__':
    app.run_server(debug=True)