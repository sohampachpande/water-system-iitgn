import dash
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
import numpy as np
import plotly.graph_objs as go
from datetime import datetime as dt
import time
import sqlite3


def get_dbconn():
    cur = sqlite3.connect('occupancy_data.db')
    cur = cur.cursor()
    return cur


def epoch_timestring(epoch_time):
    return time.strftime('%H:%M', time.localtime(int(epoch_time)))


def date_epoch(date_string):
    utc_time = dt.strptime(date_string, "%Y-%m-%d")
    epoch_start_time = utc_time.timestamp()
    return epoch_start_time, epoch_start_time + 86400


external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__)

app.css.append_css({"external_url": "https://codepen.io/chriddyp/pen/bWLwgP.css"})
app.css.append_css({"external_url": "https://codepen.io/chriddyp/pen/brPBPO.css"})

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
}

cur = get_dbconn()
cur.execute('SELECT DISTINCT area from occupancy')
available_area = np.asarray(cur.fetchall())[:, 0]

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
                dcc.DatePickerSingle(
                    id='my-date-picker-single',
                    min_date_allowed=dt(2019, 3, 5),
                    max_date_allowed=dt(2019, 3, 8),
                    initial_visible_month=dt(2019, 3, 3)
                    # date=dt(2019, 3, 3)
                )
            ],
            style={
                'width': '20%',
                'margin': '1%'
            })
    ]),
    dcc.Graph(id='indicator-graphic'),
])


@app.callback(
    dash.dependencies.Output('building', 'options'),
    [dash.dependencies.Input('area', 'value')])
def set_buildings_options(chosen_area):
    cur = get_dbconn()
    cur.execute(
        'SELECT DISTINCT building FROM occupancy WHERE area = "{}"'.format(
            chosen_area))
    available_building = np.asarray(cur.fetchall())[:, 0]
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
    available_floor = np.asarray(cur.fetchall())[:, 0]
    return [{'label': i, 'value': i} for i in available_floor]


@app.callback(
    dash.dependencies.Output('indicator-graphic', 'figure'), [
        dash.dependencies.Input('area', 'value'),
        dash.dependencies.Input('building', 'value'),
        dash.dependencies.Input('floor', 'value'),
        dash.dependencies.Input('my-date-picker-single', 'date')
    ])
def update_graph(area, building, floor, date):

    if date is not None:
        print(date)
        # date = dt.strptime(date, '%Y-%m-%d') #%H:%M:%S')
        # date_string = date.strftime('%Y-%m-%d')

        date_string = date

        start_epoch, end_epoch = date_epoch(date_string)

        cur = get_dbconn()
        cur.execute(
            'SELECT timeEpoch, count FROM occupancy WHERE area = "{}" AND building = "{}" AND floor = "{}" AND timeEpoch>="{}" AND timeEpoch<"{}"'
            .format(area, building, floor, start_epoch, end_epoch))

        np_time_count = np.asarray(cur.fetchall())

        list_count = list(np_time_count[:, 1])
        list_time = list(map(epoch_timestring, list(np_time_count[:, 0])))

        return {
            'data': [
                go.Scatter(
                    x=list_time,
                    y=list_count,
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
                yaxis={'title': 'Count'},
                # margin={'l': 50, 'b': 100, 't': 100, 'r': 50},
                height=700,
                hovermode='closest')
        }


if __name__ == '__main__':
    app.run_server(debug=True)