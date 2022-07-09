import meshcat
import meshcat.geometry as g
import meshcat.transformations as tf
import numpy as np

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