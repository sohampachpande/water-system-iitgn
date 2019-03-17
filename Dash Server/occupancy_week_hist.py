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
    for n in range(int((end_date - start_date).days)):
        yield start_date + timedelta(n)


external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

dict_area = {
    'AC': 'Academic Area',
    'SH': 'Student Housing',
    'SFH': 'Faculty Housing',
    'all': 'all'
}
dict_building = {
    'A': 'Aiban',
    'B': 'Beauki',
    'C': 'Chimair',
    'D': 'Duven',
    'E': 'Emiet',
    'F': 'Firpeal',
    'all':'all'
}
for i in range(31):
    dict_building.update({'B{}'.format(i): 'Block {}'.format(i)})

dict_floor = {
    'GF': 'Ground Floor',
    'FF': 'First Floor',
    'SF': 'Second Floor',
    'TF': 'Third Floor',
    'all':'all'
}

cur = get_dbconn()
cur.execute('SELECT DISTINCT area from occupancy')
available_area = list(np.asarray(cur.fetchall())[:, 0])
available_area.append('all')

app.layout = html.Div([
    html.Div([
        html.H1(children='IIT Gandhinagar Occupancy', style={'margin': '1%'}),
        html.
        P('Please select the area, building, floor and date from dropdown menus',
          style={'margin': '1%'}),
        html.Div([
            dcc.Dropdown(
                id='area',
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
                     'display': 'inline-block'
                 }),
        html.Div(
            [
                dcc.Dropdown(
                    id='building',
                    # options=[{'label': i, 'value': i} for i in available_building],
                    placeholder="Select Building",
                    # value='B'
                )
            ],
            style={
                'width': '20%',
                'margin': '1%',
                'display': 'inline-block'
            }),
        html.Div(
            [
                dcc.Dropdown(
                    id='floor',
                    # options=[{'label': i, 'value': i} for i in available_floor],
                    placeholder="Select Floor",
                    # value='FF'
                )
            ],
            style={
                'width': '20%',
                'margin': '1%',
                'display': 'inline-block'
            }),
        html.Div(
            [
                dcc.DatePickerRange(
                    id='my-date-picker-range',
                    min_date_allowed=dt(2019, 3, 5),
                    max_date_allowed=dt(2019, 3, 8),
                    initial_visible_month=dt(2019, 3, 3)
                    # date=dt(2019, 3, 3)
                )
            ],
            style={
                'width': '15%',
                'margin': '1%',
                'display': 'inline-block'
            })
    ]),
    html.Div([dcc.Graph(id='indicator-graphic')],
             style={
                 'width': '90%',
                 'margin': '1%'
             })
])


@app.callback(
    dash.dependencies.Output('building', 'options'),
    [dash.dependencies.Input('area', 'value')])
def set_buildings_options(chosen_area):
    cur = get_dbconn()
    cur.execute(
        'SELECT DISTINCT building FROM occupancy WHERE area = "{}"'.format(
            chosen_area))
    available_building = list(np.asarray(cur.fetchall())[:, 0])
    available_building.append('all')
    return [{
        'label': dict_building[i],
        'value': i
    } for i in available_building]


@app.callback(
    dash.dependencies.Output('floor', 'options'),
    [dash.dependencies.Input('building', 'value')])
def set_floor_options(chosen_building):
    cur = get_dbconn()
    cur.execute(
        'SELECT DISTINCT floor FROM occupancy WHERE building = "{}"'.format(
            chosen_building))
    available_floor = list(np.asarray(cur.fetchall())[:, 0])
    available_floor.append('all')
    return [{'label': i, 'value': i} for i in available_floor]



@app.callback(
    dash.dependencies.Output('indicator-graphic', 'figure'), [
        dash.dependencies.Input('area', 'value'),
        dash.dependencies.Input('building', 'value'),
        dash.dependencies.Input('floor', 'value'),
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
            print(start_epoch, end_epoch)
            if (area == 'All'):
                cur.execute("SELECT count FROM occupancy WHERE timeEpoch>='{}' AND timeEpoch<'{}'".format(start_epoch, end_epoch))
                np_count = np.asarray(cur.fetchall())
            elif (building == 'All'):
                cur.execute("SELECT count FROM occupancy WHERE area = '{}' AND timeEpoch>='{}' AND timeEpoch<'{}'".format(area, start_epoch, end_epoch))
                np_count = np.asarray(cur.fetchall())
            elif (floor == 'All'):
                cur.execute("SELECT count FROM occupancy WHERE area = '{}' AND building = '{}' AND timeEpoch>='{}' AND timeEpoch<'{}'".format(area, building, start_epoch, end_epoch))
                np_count = np.asarray(cur.fetchall())
            else:
                print('Hi')
                print(date_string)
                cur.execute("SELECT count FROM occupancy WHERE area = '{}' AND building = '{}' AND floor = '{}' AND timeEpoch>='{}' AND timeEpoch<'{}'".format(area, building, floor, start_epoch, end_epoch))
                np_count = np.asarray(cur.fetchall())

            count = np_count.mean(axis=0)[0]
            dict_count[date_string] = count

        return {
            'data': [
                go.Scatter(
                    x=list(dict_count.keys()),
                    y=list(dict_count.values()),
                    # text=list_time,
                    mode='lines+markers',
                    marker={
                        'size': 15,
                        'opacity': 0.5,
                        'line': {
                            'width': 0.5,
                            'color': 'white'
                        }
                    })
            ],
            'layout':
            go.Layout(
                xaxis={'title': 'Time'},
                yaxis={'title': 'Average Count'},
                # margin={'l': 50, 'b': 100, 't': 100, 'r': 50},
                # height=700,
                hovermode='closest')
        }


if __name__ == '__main__':
    app.run_server(debug=True)