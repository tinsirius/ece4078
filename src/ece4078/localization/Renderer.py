import json, base64
from pathlib import Path
import plotly.graph_objects as go
from string import Template
from IPython.display import IFrame

class Renderer:
    def __init__(self, state, true_state, robot_cov = None, measurements = None, add_aruco = False):
        current_dir = Path(__file__).resolve().parent

        fig = go.Figure(
            layout=dict(
                plot_bgcolor="white",
                margin=dict(l=0, r=0, t=50, b=0),
                xaxis=dict(range=[-4, -1.5], title="<b>X(m)</b>", showgrid = False,
                           showline=True, linecolor="black", mirror=True),
                yaxis=dict(range=[-3.5, -1.5], title="<b>Y(m)</b>",
                           showline=True, linecolor="black", mirror=True,
                           scaleratio=1, scaleanchor="x", showgrid = False),
                showlegend=True,
                autosize=False,
                title = dict(
                    x=0.5,
                    text = "Overhead View",
                    xanchor="center",
                    xref="paper"
                    )
            )
        )

        fig.add_trace(go.Scatter(x=true_state[:, 0].tolist(), 
                                y=true_state[:, 1].tolist(), 
                                mode="lines", 
                                line=dict(width=2, color="rgba(255, 0, 0, 0.4)"), 
                                name = "True state (from data)"))

        if add_aruco:
            marker_world_width = 0.3
            img_path = current_dir / "images"
            for ii, path in enumerate(sorted(img_path.glob("M*.png"))):
                parts = path.stem.split('_')
                mp    = [float(parts[1]), float(parts[2])]
                encoded = base64.b64encode(path.read_bytes()).decode()
            
                fig.add_layout_image(
                    dict(
                        source=f"data:image/png;base64,{encoded}",
                        x=mp[0] - marker_world_width / 2,
                        y=mp[1] + marker_world_width / 2,
                        sizex=marker_world_width,
                        sizey=marker_world_width,
                        xref="x", yref="y",
                        layer="below"
                    )
                )

                fig.add_annotation(
                    x=mp[0], y=mp[1],
                    text=f"<b>{ii}</b>",
                    showarrow=False,
                    font=dict(color="red", size=14)
                )

        measurements = [] if measurements is None else self.get_measurements_dict(measurements)

        fig_json = fig.to_plotly_json()
        X, Y, THETA = state[:, 0].tolist(), state[:, 1].tolist(), state[:, 2].tolist()
        N = len(X)
        COV2by2 = [] if robot_cov is None else robot_cov[:, :2, :2].tolist() 
            
        tpl_text = (current_dir /  "template.html").read_text()
        self.html = Template(tpl_text).substitute(
            fig_json = json.dumps(fig_json),
            X = json.dumps(X),
            Y = json.dumps(Y),
            THETA = json.dumps(THETA), 
            COV2x2 = json.dumps(COV2by2),
            N = N-1,
            GUESSES = json.dumps(measurements),
        )

    def get_measurements_dict(self, measurements):
        mes_replay = []
        for mes in measurements:
            tmp_dict = {}
            for m in mes:
                tmp_dict.update({m.tag:  m.position.squeeze().tolist()})
            mes_replay.append(tmp_dict)
        return mes_replay
        
    def get_IFrame(self, width = 750, height = 500):
        b64 = base64.b64encode(self.html.encode('utf-8')).decode('ascii')
        data_uri = f"data:text/html;base64,{b64}"
        return IFrame(data_uri, width=width, height=height)