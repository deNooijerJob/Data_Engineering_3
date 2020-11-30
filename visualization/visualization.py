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

app = dash.Dash()
X = deque(maxlen=20)
X.append(1)

Y = deque(maxlen=20)
Y.append(1)

server = flask.Flask(__name__)
app = dash.Dash(__name__, server=server)


@server.route('/test', methods=['POST'])
def test(): 
    requests = request.get_json()   
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
    X.append(X[-1] + 1)
    Y.append(Y[-1] + Y[-1] * random.uniform(-0.1, 0.1))

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

