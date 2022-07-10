# This script is heavily inspired by Russ Tedrake's team
# https://github.com/RobotLocomotion/drake/blob/master/bindings/pydrake/_geometry_extra.py
# The idea is very similar, you essentially want to run a set up
# for nginx so that it fowward port 7000-7099 through the only port
# that deepnote exposed: 8080

import os
import socket
import subprocess
import sys
import errno
import meshcat
from urllib.parse import urlparse
from IPython.display import display, HTML

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
            ["sh", script_dir], stdout=subprocess.PIPE,
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
