import meshcat
import meshcat.geometry as g
import meshcat.transformations as tf
import numpy as np

import os
import socket
import subprocess
import sys
import errno
from urllib.parse import urlparse
from IPython.display import display, HTML
import pickle
import ipywidgets as widgets
import signal


class ece4078_viz(meshcat.Visualizer):

    def Set2DView(self, scale = 30, center = None):
        self['/Grid'].set_property('visible', False)
        self['/Background'].set_property("top_color", [1, 1, 1])
        self['/Background'].set_property("bottom_color", [1, 1, 1])
        self["/Lights/PointLightNegativeX/<object>"].set_property("intensity", 0.0)
        self["/Lights/PointLightPositiveX/<object>"].set_property("intensity", 0.0)
        a = np.array(   [[ 1.,  0.,  0., 0.],
                        [ 0.,  1.,  0., 0.],
                        [ 0.,  0.,  1., scale*1.0],
                        [ 0.,  0.,  0.,  1.]])
        if center is None:
            camera = g.OrthographicCamera(left = -scale, right = scale, top = scale, bottom = -scale, near = -1000, far = 1000)
        else:
            camera = g.OrthographicCamera(left = center[0], right = center[1], 
                                        top = center[2], bottom = center[3], 
                                        near = -1000, far = 1000)
        
        self['/Cameras/default/rotated'].set_object(camera)
        self['/Cameras/default'].set_transform(a)
        self['/Cameras/default/rotated/<object>'].set_property('position', [0.0, 0.0, 0.0])

    def Set3DView(self, pos = [2.0, 1.0, -1.0]):
        camera = g.PerspectiveCamera()
        self['/Cameras/default/rotated'].set_object(camera)
        self['/Cameras/default'].set_transform(np.identity(4))
        self['/Cameras/default/rotated/<object>'].set_property('position', pos) # y, z, x
        self['/Grid'].set_property('visible', True)

    def ResetView(self):
        self.Set3DView(pos = [5.0, 1.0, 0])
        self["/Axes"].set_property('visible', True)
        self['/Background'].set_property("top_color", [135.0/255, 206.0/255, 250.0/255])
        self['/Background'].set_property("bottom_color", [25.0/255, 25.0/255, 112.0/255])

    def setPNGView(self, scale, center = None):
        self.Set2DView(scale, center)
        self["/Axes"].set_property('visible', False)
        self["/Lights/PointLightNegativeX/<object>"].set_property("intensity", 0.5)
        self["/Lights/PointLightPositiveX/<object>"].set_property("intensity", 0.5)
        self["/Lights/FillLight/<object>"].set_property("intensity", 0.5)

    def add_thick_triad(self, name, opacity = 1.0, thickness = 0.01, length = 0.5):
        axes = ['z', 'y', 'x']
        colors = [0x0000ff, 0x00ff00, 0xff0000]
        self[name].delete()
        for i in range(3):
            rot_vector = [0]*3
            rot_vector[i] = 1
            trans_vector = [value * length/2 for value in rot_vector][::-1]
            self[name][axes[i]].set_object(
                                        g.Cylinder(length, radius = thickness), 
                                        g.MeshLambertMaterial(
                                            color=colors[i],
                                            opacity = opacity)
                                        )
            self[name][axes[i]].set_transform(
                    tf.translation_matrix(trans_vector)
                    @ tf.rotation_matrix(np.pi/2, rot_vector)
                )

        self[name]["origin"].set_object(g.Sphere(2 * thickness), g.MeshLambertMaterial(
                                    color=0x000000,
                                    opacity = opacity))

        return self[name]

    def printMatrix(self, rot, size, pos = np.identity(4)):
        if rot.ndim == 2:
            for i, row in enumerate(rot):
                self["print"]["row" + str(i)].set_transform(
                    tf.translation_matrix([size/2, size/2 - i*size/10, 0])
                    )

                self["print"]["row" + str(i)].set_object(g.SceneText(str(np.round(rot[i, :], 2)), 
                                            width=size,
                                            height=size, 
                                            font_size = size))
            self['print'].set_transform(pos)
        else:
            pass

    def initialize_inline(self, url):
        self.ece4078_url = url
        self.init_inline = False

    def show_inline(self, height = 400):
        HTML_string = """
                <div style="height: {height}px; width: 100%; overflow-x: auto; overflow-y: hidden; resize: both">
                <iframe src="{url}" style="width: 100%; height: 100%; border: none"></iframe>
                </div>
                """.format(url=self.ece4078_url, height=height)

        if not self.init_inline:
            self.HTML_widgets = widgets.HTML(HTML_string)
            self.init_inline = True
        else:
            self.HTML_widgets.close()
            self.HTML_widgets = widgets.HTML(HTML_string)

        return self.HTML_widgets

    def mask_origin(self):
        self["origin_mask"].set_object(g.LineSegments(
            g.PointsGeometry(position=np.array([
                [0, 0, 0], [0.5, 0, 0],
                [0, 0, 0], [0, 0.5, 0],
                [0, 0, 0], [0, 0, 0.5]]).astype(np.float32).T,
                color=np.array([
                [0, 0, 0], [0, 0, 0],
                [0, 0, 0], [0, 0, 0],
                [0, 0, 0], [0, 0, 0]]).astype(np.float32).T
            ),
            g.LineBasicMaterial(vertexColors=True)))

        return self["origin_mask"]

def _eval_timeout_print_str():
    return """
import signal, sys
def eval_timeout_print(statement_str):
    def handler(signum, frame):
        raise Exception("Infinite Loop")
    signal.alarm(5)
    signal.signal(signal.SIGALRM, handler)
    sys.stdout.write('skip '); result = eval(statement_str) # doctest:+ELLIPSIS
    signal.alarm(0)
    return result
"""    

def enumerate_pickle(pickle_list, path = "pickle/"):
    l = [] 
    for my_pickle in pickle_list:
        a_file = open(path + my_pickle, "rb")
        pk_result = pickle.load(a_file)
        l.append(pk_result)
    return l


# The following functions are HEAVILY inspired (i.e. copypasta) from Russ Tedrake's team
# https://github.com/RobotLocomotion/drake/blob/master/bindings/pydrake/_geometry_extra.py
# The idea is very similar, you essentially want to run a set up for nginx so that it 
# fowward port 7000-7099 through the only port that Deepnote exposed: 8080

def _is_listening(port):
    """Returns True iff the port number (on localhost) is listening for
    connections.
    """
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        return sock.connect_ex(("127.0.0.1", port)) == 0
    finally:
        sock.close()


def _install_deepnote_nginx():
    """Uses Ubuntu to install the NginX web server and configures it to serve
    as a reverse proxy for MeshCat on Deepnote. The server will proxy
    https://DEEPNOTE_PROJECT_ID:8080/PORT/ to http://127.0.0.1:PORT/ so
    that multiple notebooks can all be served via Deepnote's only open port.
    """
    print("Installing NginX server for MeshCat on Deepnote...")
    script_dir = os.path.abspath( os.path.join(
            os.path.dirname(__file__), "install_nginx"))

    if os.path.isfile(script_dir):
        proc = subprocess.run(
            ["bash", script_dir], stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT)
        if proc.returncode == 0:
            return
        print(proc.stdout, file=sys.stderr, end="")
        proc.check_returncode()
    else:
        print("no nginx installation script available")
        raise FileNotFoundError(errno.ENOENT, os.strerror(errno.ENOENT), script_dir)

def _start_meshcat_deepnote_nginx(restart_nginx=False):
    """Returns a Meshcat object suitable for use on Deepnote's cloud.
    """
    host = os.environ["DEEPNOTE_PROJECT_ID"]
    if restart_nginx or not _is_listening(8080):
        _install_deepnote_nginx()
    vis = ece4078_viz()
    port = urlparse(vis.url()).port
    url = f"https://{host}.deepnoteproject.com/{port}/static/"
    vis.initialize_inline(url)
    display(HTML(f"Meshcat URL if you are on Deepnote: <a href='{url}' target='_blank'>{url}</a>"))
    return vis

def _start_meshcat_deepnote_pickle(data):
    """Returns a Meshcat object suitable for use on Deepnote's cloud.
    Set by the address defined in init.ipynb
    """
    web_url = data['web_url']
    zmq_url = data['zmq_url']
    vis = ece4078_viz(zmq_url)
    vis.initialize_inline(web_url)
    display(HTML(f"Meshcat URL if you are on Deepnote: <a href='{web_url}' target='_blank'>{web_url}</a>"))

    return vis

def _start_meshcat_vanilla():
    vis = ece4078_viz()
    url = vis.url()
    vis.initialize_inline(url)
    display(HTML(f"Meshcat URL if you are on local machine: <a href='{url}' target='_blank'>{url}</a>"))
    return vis


def StartMeshcat(nginx = False):
    """
    Constructs a Meshcat instance, with extra support for Deepnote.

    On most platforms, this function is equivalent to simply constructing a
    ``pydrake.geometry.Meshcat`` object with default arguments.

    On Deepnote, however, this does extra work to expose Meshcat to the public
    internet by setting up a reverse proxy for the single available network
    port. To access it, you must enable "Allow incoming connections" in the
    Environment settings pane.
    """
    try:
        data = pickle.load(
            open(os.path.expanduser('~')+'/.deepnote_meshcat.conf', "rb"))
    except (OSError, IOError) as e:
        data = None

    if "DEEPNOTE_PROJECT_ID" in os.environ:
        if nginx:
            return _start_meshcat_deepnote_nginx()
        else:
            if data is not None:
                return _start_meshcat_deepnote_pickle(data)
            else:
                return _start_meshcat_vanilla()
    else:
        return _start_meshcat_vanilla()
