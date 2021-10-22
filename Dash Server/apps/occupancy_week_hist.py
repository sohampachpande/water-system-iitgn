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


def get_dbconn():
    cur = sqlite3.connect('occupancy_data.db')
    cur = cur.cursor()
    return cur


def epoch_timestring(epoch_time):
    return time.strftime('%H:%M:%S', time.localtime(int(epoch_time)))


def date_epoch(date_string):
    utc_time = dt.strptime(date_string, "%Y-%m-%d")
    epoch_start_time = utc_time.timestamp()
    return epoch_start_time, epoch_start_time + 86400


def daterange(start_date, end_date):
    for n in range(int((end_date - start_date).days)+1):
        yield start_date + timedelta(n)


from app import app

dict_area = {
    'AC': 'Academic Area',
    'SH': 'Student Housing',
    'SFH': 'Faculty Housing'
}
dict_building = {
    'A': 'Aiban',
    'B': 'Beauki',
    'C': 'Chimair',
    'D': 'Duven',
    'E': 'Emiet',
    'F': 'Firpeal'
}
for i in range(31):
    dict_building.update({'B{}'.format(i): 'Block {}'.format(i)})

dict_floor = {
    'GF': 'Ground Floor',
    'FF': 'First Floor',
    'SF': 'Second Floor',
    'TF': 'Third Floor',
    'Ground Floor':'GF',
    'First Floor':'FF',
    'Second Floor':'SF',
    'Third Floor':'TF'
}

cur = get_dbconn()
cur.execute('SELECT DISTINCT area from occupancy')
available_area = list(np.asarray(cur.fetchall())[:, 0])

layout = html.Div([
    html.Div([
        html.H1(children='IIT Gandhinagar Occupancy - Average Daily Occupancy', style={'margin': '1%'}),
        html.
        P('Please select the area, building, floor and date from dropdown menus',
          style={'margin': '1%'}),
        html.Div([
            dcc.Dropdown(
                id='hist_area',
                options=[{
                    'label': dict_area[i],
                    'value': i
                } for i in available_area],
                placeholder="Select Area",
            )
        ],
                 style={
                     'width': '20%',
                     'margin': '1%',
                     'display': 'inline-block',
                     'verticalAlign': 'top'
                 }),
        html.Div(
            [
                dcc.Dropdown(
                    id='hist_building',
                    # options=[{'label': i, 'value': i} for i in available_building],
                    placeholder="Select Building",
                    # value='B'
                )
            ],
            style={
                'width': '20%',
                'margin': '1%',
                'display': 'inline-block',
                'verticalAlign': 'top'
            }),
        html.Div(
            [
                dcc.Dropdown(
                    id='hist_floor',
                    # options=[{'label': i, 'value': i} for i in available_floor],
                    placeholder="Select Floor",
                    # value='FF'
                )
            ],
            style={
                'width': '20%',
                'margin': '1%',
                'display': 'inline-block',
                'verticalAlign': 'top'
            }),
        html.Div(
            [
                dcc.DatePickerRange(
                    id='my-date-picker-range',
                    min_date_allowed=dt(2019, 3, 5),
                    max_date_allowed=dt(2019, 3, 9),
                    initial_visible_month=dt(2019, 3, 3)
                    # date=dt(2019, 3, 3)
                )
            ],
            style={
                'width': '15%',
                'margin': '1%',
                'display': 'inline-block',
                'verticalAlign': 'top'
            })
    ]),
    html.Div([dcc.Graph(id='indicator-graphic-hist')],
             style={
                 'width': '90%',
                 'margin': '1%'
             }),
    dcc.Link('Go back to home', href='/home')
])


@app.callback(
    dash.dependencies.Output('hist_building', 'options'),
    [dash.dependencies.Input('hist_area', 'value')])
def set_buildings_options(chosen_area):
    cur = get_dbconn()
    cur.execute(
        'SELECT DISTINCT building FROM occupancy WHERE area = "{}"'.format(
            chosen_area))
    available_building = list(np.asarray(cur.fetchall())[:, 0])
    return [{
        'label': dict_building[i],
        'value': i
    } for i in available_building]


@app.callback(
    dash.dependencies.Output('hist_floor', 'options'),
    [dash.dependencies.Input('hist_building', 'value')])
def set_floor_options(chosen_building):
    cur = get_dbconn()
    cur.execute(
        'SELECT DISTINCT floor FROM occupancy WHERE building = "{}"'.format(
            chosen_building))
    available_floor = list(np.asarray(cur.fetchall())[:, 0])
    return [{'label': i, 'value': dict_floor[i]} for i in available_floor]



@app.callback(
    dash.dependencies.Output('indicator-graphic-hist', 'figure'), [
        dash.dependencies.Input('hist_area', 'value'),
        dash.dependencies.Input('hist_building', 'value'),
        dash.dependencies.Input('hist_floor', 'value'),
        dash.dependencies.Input('my-date-picker-range', 'start_date'),
        dash.dependencies.Input('my-date-picker-range', 'end_date')
    ])
def update_graph(area, building, floor, start_date, end_date):

    if (start_date is not None) and (end_date is not None):

        start_date = dt.strptime(start_date, '%Y-%m-%d')
        end_date = dt.strptime(end_date, '%Y-%m-%d')

        dict_count = {}
        cur = get_dbconn()

        for single_date in daterange(start_date, end_date):
            date_string = single_date.strftime("%Y-%m-%d")
            # date_string = date.strftime('%Y-%m-%d')
            start_epoch, end_epoch = date_epoch(date_string)
            if (area == 'all'):
                cur.execute("SELECT count FROM occupancy WHERE timeEpoch>='{}' AND timeEpoch<'{}'".format(start_epoch, end_epoch))
                np_count = np.asarray(cur.fetchall())
            elif (building == 'all'):
                cur.execute("SELECT count FROM occupancy WHERE area = '{}' AND timeEpoch>='{}' AND timeEpoch<'{}'".format(area, start_epoch, end_epoch))
                np_count = np.asarray(cur.fetchall())
            elif (floor == 'all'):
                cur.execute("SELECT count FROM occupancy WHERE area = '{}' AND building = '{}' AND timeEpoch>='{}' AND timeEpoch<'{}'".format(area, building, start_epoch, end_epoch))
                np_count = np.asarray(cur.fetchall())
            else:
                cur.execute("SELECT count FROM occupancy WHERE area = '{}' AND building = '{}' AND floor = '{}' AND timeEpoch>='{}' AND timeEpoch<'{}'".format(area, building, dict_floor[floor], start_epoch, end_epoch))
                np_count = np.asarray(cur.fetchall())

            count = np_count.mean(axis=0)[0]
            dict_count[date_string] = count

            print(dict_count)

        return {
            'data': [
                go.Bar(
                    x=list(dict_count.keys()),
                    y=list(dict_count.values()),
                    # text=list_time,
                    name='Occupancy',
                    hovertemplate = '<i>Time</i>: %{x}'+'<br><b>Count</b>: %{y}<br>')
            ],
            'layout':
            go.Layout(
                xaxis={'title': 'Time'},
                yaxis={'title': 'Average Count'},
                # margin={'l': 50, 'b': 100, 't': 100, 'r': 50},
                # height=700,
                hovermode='closest')
        }
    else:
        return dash.no_update


if __name__ == '__main__':
    app.run_server(debug=True)