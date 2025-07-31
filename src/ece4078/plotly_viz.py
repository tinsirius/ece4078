import os
import dash
from dash import dcc, html, Input, Output
import plotly.graph_objects as go
import numpy as np

class InteractiveApp:

    def __init__(self, host="0.0.0.0", port=8080, display_host="127.0.0.1"):
        self.host, self.port = host, port
        self.app = dash.Dash(__name__)
        self.app.layout = html.Div()
        self._demo_builders = {}
        self._current_demo = None
        self._server_thread = None
        self.register_demo("NotebookChecker", NotebookChecker)

        if "DEEPNOTE_PROJECT_ID" in os.environ:
            deepnote_id = os.environ["DEEPNOTE_PROJECT_ID"]
            self.display_url = f"https://{deepnote_id}.deepnoteproject.com"
            self.is_deepnote = True
        else:
            self.display_url = f"http://{display_host}:{self.port}"
            self.is_deepnote = False


    def register_demo(self, name: str, builder):
        self._demo_builders[name] = builder

    def use_demo(self, name: str, *args, **kwargs):
        if name not in self._demo_builders:
            raise KeyError(f"No demo named '{name}' registered")
        if self._current_demo is not None:
            self.app._callback_list = []
        builder = self._demo_builders[name]
        builder({"app": self.app}, *args, **kwargs)
        self._current_demo = name

    def run(self):
        self.app.run(jupyter_mode="external", host=self.host, port=self.port, debug=False, use_reloader=False)


def NotebookChecker(ctx, compute_fn = None):

    app = ctx["app"]
    x = np.linspace(0, 2 * np.pi, 400)

    base_fig = go.Figure(go.Scatter(x=x, y=np.sin(x), mode="lines"))
    base_fig.update_layout(
        margin=dict(t=20),
        xaxis_title="x",
        yaxis_title="sin(x)",
        height=500,
    )

    app.layout = html.Div([
        dcc.Slider(
            id="freq",
            min=1, max=10, step=1, value=1,
            marks={i: str(i) for i in range(1, 11)},
        ),
        dcc.Graph(id="sine-graph", figure=base_fig),
    ])

    @app.callback(
        Output("sine-graph", "figure"),
        Input("freq", "value"),
        prevent_initial_call=True,
    )
    
    def update(freq):
        if freq == 10:
            fig = go.Figure()
            fig.update_layout(
                margin=dict(t=20),
                xaxis=dict(visible=False),
                yaxis=dict(visible=False),
                annotations=[dict(
                    text="Isaac Asimov",
                    x=0.5, y=0.5, xref="paper", yref="paper",
                    showarrow=False, font=dict(size=28)
                )],
                height=500,
            )
            return fig

        y = np.sin(freq * x)
        fig = go.Figure(go.Scatter(x=x, y=y, mode="lines"))
        fig.update_layout(
            margin=dict(t=20),
            xaxis_title="x",
            yaxis_title=f"sin({freq}x)",
            height=500,
        )
        return fig
    
def labeled_slider(id, label, min, max, step, value, marks):
    return html.Div(
        style={'display': 'flex', 'alignItems': 'center', 'marginBottom': '0px'},
        children=[
            html.Label(label, style={'width': '12%', 'marginRight': '5%'}),
            html.Div(
                dcc.Slider(
                    id=id,
                    min=min,
                    max=max,
                    step=step,
                    value=value,
                    marks=marks,
                    updatemode="drag",
                    tooltip={"placement": "bottom"},
                ),
                style={'flex': '1'}
            )
        ]
    )