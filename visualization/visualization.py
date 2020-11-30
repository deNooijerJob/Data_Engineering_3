import dash
import dash_core_components as dcc
from dash.dependencies import Output, Input
import dash_html_components as html
import plotly
from collections import deque
import random
import plotly.graph_objs as go
import flask
from flask import json, request
import numpy as np

app = dash.Dash()
X = deque(maxlen=20)
X.append(1)

Y = deque(maxlen=20)
Y.append(0.5)

server = flask.Flask(__name__)
app = dash.Dash(__name__, server=server)


@server.route('/update_avg', methods=['POST'])
def changeSentiment():
    requests = request.get_json()
    newAvg = np.round(float(requests['avg']), 2)
    X.append(X[-1] + 1)
    Y.append(newAvg)
    return json.dumps({"message": "nice"}, sort_keys=False, indent=4), 200


app.layout = html.Div(
    [
        dcc.Graph(id='live-graph', animate=True),
        dcc.Interval(
            id='graph-update',
            interval=1000,
            n_intervals=0
        ),
    ]
)


@app.callback(
    Output('live-graph', 'figure'),
    [Input('graph-update', 'n_intervals')]
)
def update_graph_scatter(n):


    data = plotly.graph_objs.Scatter(
        x=list(X),
        y=list(Y),
        name='Scatter',
        mode='lines+markers'
    )

    return {'data': [data],
            'layout': go.Layout(xaxis=dict(range=[min(X), max(X)]), yaxis=dict(range=[min(Y), max(Y)]), )}


if __name__ == '__main__':
    app.run_server(host='0.0.0.0')

