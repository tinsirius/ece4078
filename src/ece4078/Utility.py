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

def Set2DView(vis, scale = 30):
    vis['/Grid'].set_property('visible', False)
    vis['/Background'].set_property("top_color", [1, 1, 1])
    vis['/Background'].set_property("bottom_color", [1, 1, 1]) 
    a = np.array(   [[ 1.,  0.,  0., 0.],
                    [ 0.,  1.,  0., 0.],
                    [ 0.,  0.,  1., scale*1.0],
                    [ 0.,  0.,  0.,  1.]])

    camera = g.OrthographicCamera(left = -scale, right = scale, top = scale, bottom = -scale, near = -1000, far = 1000)
    vis['/Cameras/default/rotated'].set_object(camera)
    vis['/Cameras/default'].set_transform(a)
    vis['/Cameras/default/rotated/<object>'].set_property('position', [0.0, 0.0
    , 0.0])

def Set3DView(vis, pos = [2.0, 1.0, -1.0]):
    camera = g.PerspectiveCamera()
    vis['/Cameras/default/rotated'].set_object(camera)
    vis['/Cameras/default'].set_transform(np.identity(4))
    vis['/Cameras/default/rotated/<object>'].set_property('position', pos) # y, z, x
    vis['/Grid'].set_property('visible', True)

def add_thick_triad(vis, name, opacity = 1.0, thickness = 0.01, length = 0.5):
    axes = ['z', 'y', 'x']
    colors = [0x0000ff, 0x00ff00, 0xff0000]
    vis[name].delete()
    for i in range(3):
        rot_vector = [0]*3
        rot_vector[i] = 1
        trans_vector = [value * length/2 for value in rot_vector][::-1]
        vis[name][axes[i]].set_object(
                                    g.Cylinder(length, radius = thickness), 
                                    g.MeshLambertMaterial(
                                        color=colors[i],
                                        opacity = opacity)
                                    )
        vis[name][axes[i]].set_transform(
                tf.translation_matrix(trans_vector)
                @ tf.rotation_matrix(np.pi/2, rot_vector)
            )

    vis[name]["origin"].set_object(g.Sphere(2 * thickness), g.MeshLambertMaterial(
                                color=0x000000,
                                opacity = opacity))

    return vis[name]

def printMatrix(vis, rot, size, pos = np.identity(4)):
    if rot.ndim == 2:
        for i, row in enumerate(rot):
            vis["print"]["row" + str(i)].set_transform(
                tf.translation_matrix([size/2, size/2 - i*size/10, 0])
                )

            vis["print"]["row" + str(i)].set_object(g.SceneText(str(np.round(rot[i, :], 2)), 
                                        width=size,
                                        height=size, 
                                        font_size = size))
        vis['print'].set_transform(pos)
    else:
        pass

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

def _start_meshcat_deepnote(restart_nginx=False):
    """Returns a Meshcat object suitable for use on Deepnote's cloud.
    """
    host = os.environ["DEEPNOTE_PROJECT_ID"]
    if restart_nginx or not _is_listening(8080):
        _install_deepnote_nginx()
    vis = meshcat.Visualizer()
    port = urlparse(vis.url()).port
    url = f"https://{host}.deepnoteproject.com/{port}/static/"
    display(HTML(f"Meshcat URL if you are on Deepnote: <a href='{url}' target='_blank'>{url}</a>"))
    return vis


def StartMeshcat():
    """
    Constructs a Meshcat instance, with extra support for Deepnote.

    On most platforms, this function is equivalent to simply constructing a
    ``pydrake.geometry.Meshcat`` object with default arguments.

    On Deepnote, however, this does extra work to expose Meshcat to the public
    internet by setting up a reverse proxy for the single available network
    port. To access it, you must enable "Allow incoming connections" in the
    Environment settings pane.
    """
    if "DEEPNOTE_PROJECT_ID" in os.environ:
        return _start_meshcat_deepnote()
    else:
        vis = meshcat.Visualizer()
        url = vis.url()
        display(HTML(f"Meshcat URL if you are on local machine: <a href='{url}' target='_blank'>{url}</a>"))
        return vis
