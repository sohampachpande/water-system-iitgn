import dash
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
import plotly.graph_objs as go
from datetime import datetime as dt
import time

def epoch_timestring(epoch_time):
    return time.strftime('%H:%M:%S', time.localtime(int(epoch_time)))

# def epoch_datetime(epoch_time):
#     return dt.fromtimestamp(epoch_time)


def date_epoch(date_string):
    utc_time = dt.strptime(date_string, "%Y-%m-%d")
    epoch_start_time = utc_time.timestamp()
    return epoch_start_time, epoch_start_time+86400


external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)


df = pd.read_csv('network_data.csv', header=None)
df.columns = ['time', 'area', 'building', 'floor', 'count']

df.drop_duplicates(subset=['time', 'area', 'building', 'floor'], inplace=True)

dict_area = {'AC': 'Academic Area', 'SH': 'Student Housing', 'SFH': 'Faculty Housing'}
dict_building = {'A':'Aiban','B':'Beauki','C':'Chimair','D':'Duven','E':'Emiet','F':'Firpeal'}
for i in range(31):
    dict_building.update({'B{}'.format(i): 'Block {}'.format(i)})

dict_floor = {'GF':'Ground Floor', 'FF':'First Floor', 'SF':'Second Floor', 'TF':'Third Floor',}

app.layout = html.Div([
    html.Div([
        html.H1(children='IIT Gandhinagar Occupancy', style={'margin':'1%'}),
        html.P('Please select the area, building, floor and date from dropdown menus', style={'margin':'1%'}),
        html.Div([
            dcc.Dropdown(
                id='area',
                options=[{'label': dict_area[i], 'value': i} for i in df['area'].unique()],
                placeholder="Select Area",
                # value='SH'
            )
            ### checkboxes
            # dcc.RadioItems(
            #     id='xaxis-type',
            #     options=[{'label': i, 'value': i} for i in ['Linear', 'Log']],
            #     value='Linear',
            #     labelStyle={'display': 'inline-block'}
            # )
        ],style={'width': '20%', 'margin': '1%', 'display': 'inline-block'}),

        html.Div([
            dcc.Dropdown(
                id='building',
                # options=[{'label': i, 'value': i} for i in available_building],
                placeholder="Select Building",
                # value='B'
            )
        ],style={'width': '20%','margin': '1%', 'display': 'inline-block'}),

        html.Div([
            dcc.Dropdown(
                id='floor',
                # options=[{'label': i, 'value': i} for i in available_floor],
                placeholder="Select Floor",
                # value='FF'
            )
        ],style={'width': '20%', 'margin': '1%', 'display': 'inline-block'}),
        
        html.Div([
            dcc.DatePickerSingle(
                id='my-date-picker-single',
                min_date_allowed=dt(2019, 3, 2),
                max_date_allowed=dt(2019, 3, 8),
                initial_visible_month=dt(2019, 3, 3)
                # date=dt(2019, 3, 3)
            )
        ],style={'width': '20%','margin': '1%'})
    ]),

    dcc.Graph(id='indicator-graphic'),

    # dcc.Slider(
    #     id='year--slider',
    #     min=df['Year'].min(),
    #     max=df['Year'].max(),
    #     value=df['Year'].max(),
    #     marks={str(year): str(year) for year in df['Year'].unique()}
    # )
])


@app.callback(
    dash.dependencies.Output('building', 'options'),
    [dash.dependencies.Input('area', 'value')])
def set_buildings_options(chosen_area):
    return [{'label': dict_building[i], 'value': i} for i in df[df['area']==chosen_area]['building'].unique()]

@app.callback(
    dash.dependencies.Output('floor', 'options'),
    [dash.dependencies.Input('building', 'value')])
def set_floor_options(chosen_building):
    return [{'label': i, 'value': i} for i in df[df['building']==chosen_building]['floor'].unique()]




@app.callback(
    dash.dependencies.Output('indicator-graphic', 'figure'),
    [dash.dependencies.Input('area', 'value'),
     dash.dependencies.Input('building', 'value'),
     dash.dependencies.Input('floor', 'value'),
     dash.dependencies.Input('my-date-picker-single', 'date')])
def update_graph(area, building,
                 floor, date):
    
    if date is not None:
        print(date)
        # date = dt.strptime(date, '%Y-%m-%d') #%H:%M:%S')
        # date_string = date.strftime('%Y-%m-%d')
        
        date_string = date

        start_epoch, end_epoch = date_epoch(date_string)

        dff = df[(df['area']==area)&(df['building']==building)&(df['floor']==floor)&(df['time']>=start_epoch)&(df['time']<end_epoch)]

        dff = dff.drop(['area', 'building', 'floor'], axis=1, inplace=False)
        dff = dff.sort_values('time', inplace=False)

        list_count =list(dff['count'])
        list_time = list(map(epoch_timestring, list(dff['time'])))

        # print(list_time)
        return {
            'data': [go.Scatter(
                x=list_time,#list(range(0,len(list_count))),
                y=list_count,
                # text=list_time,
                mode = 'lines+markers',
                marker={
                    'size': 15,
                    'opacity': 0.5,
                    'line': {'width': 0.5, 'color': 'white'}
                }
            )],
            'layout': go.Layout(
                xaxis={
                    'title': 'Time'
                },
                yaxis={
                    'title': 'Count'
                },
                # margin={'l': 50, 'b': 100, 't': 100, 'r': 50},
                height=700,
                hovermode='closest'
            )
        }


if __name__ == '__main__':
    app.run_server(debug=True)