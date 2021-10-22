import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

from app import app
from apps import Water, occupancy_line_graph, occupancy_week_hist

app.layout = html.Div(
    [dcc.Location(id='url', refresh=False),
     html.Div(id='page-content')])

index_page = html.Div([
    html.H1(
        children='Welcome to IIT Gandhinagar Resource Monitoring Dashboard',
        style={'margin': '1%'}),
    html.H3(
        children='IIT Gandhinagar Occupancy - Line Graphs',
        style={'margin': '1%'}),
    html.
    P('IIT Gandhinagar has a robust Wireless network. We derive Occupancy details anonymously using logs from the network. The Line Graphs give a good understanding about human patterns throughout the day',
      style={'margin': '1%'}),
    html.Div([dcc.Link(
        'Navigate to Occupancy Analysis- Line Graphs',
        href='/OccupancyLineGraph')],style={'margin': '1%'}),
    html.Br(),
    
    html.H3(
        children='IIT Gandhinagar Occupancy - Bar Graphs',
        style={'margin': '1%'}),
    html.
    P('IIT Gandhinagar has a robust Wireless network. We derive Occupancy details anonymously using logs from the network. Bar Graphs would give a good understanding on occupancy patterns',
      style={'margin': '1%'}),
    html.Div([dcc.Link(
            'Navigate to Occupancy Analysis- Bar Graphs',
            href='/OccupancyWeeklyHistogram')],style={'margin': '1%'}),
    html.Br(),
    
    html.H3(
        children='IIT Gandhinagar Water Flow',
        style={'margin': '1%'}),
    html.
    P('IIT Gandhinagar has a complex Water and Sanitation system. We have interfaced sensors from water treatment plant to study water consumption patterns',
      style={'margin': '1%'}),
    html.Div([dcc.Link('Navigate to Water Consumption Analysis', href='/water')],style={'margin': '1%'})
])


@app.callback(Output('page-content', 'children'), [Input('url', 'pathname')])
def display_page(pathname):
    if pathname == '/water':
        return Water.layout
    elif pathname == '/OccupancyLineGraph':
        return occupancy_line_graph.layout
    elif pathname == '/OccupancyWeeklyHistogram':
        return occupancy_week_hist.layout
    elif pathname == '/home' or pathname=='/':
        return index_page
    else:
        return 404


if __name__ == '__main__':
    app.run_server(debug=False)