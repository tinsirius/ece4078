import matplotlib.pyplot as plt
import ipywidgets as widgets
import io
import numpy as np
import meshcat.geometry as g

def intro(vis):
    secret_msg = ["Hello", "students", "welcome", "to", "ECE4078"]
    w_slider = widgets.IntSlider(value=0, min=0, max=len(secret_msg)-1, step=1, description='Omega',
                                                continuous_update=False)
    
    size = 8
    def f(change):
        vis["render"].set_object(g.SceneText(secret_msg[change], width=size, height=size, font_size = size))
    interactive_plot = widgets.interactive_output(f, {'change': w_slider})
    return interactive_plot, w_slider


def NotebookChecker(vis):
    w_slider = widgets.IntSlider(value=0, min=0, max=10, step=1, description='Omega',
                                                continuous_update=False)
    def f(change):
        fig = plt.figure(figsize=(5, 5))
        ax = plt.gca()

        x = np.linspace(1, 2 * np.pi, 100)
        y = np.sin(x*change)
        ax.plot(x, y)
        image_data = io.BytesIO()
        fig.savefig(image_data, bbox_inches = 'tight', 
                        facecolor='white', transparent=False)
        plt.close()
        size = 8
        if change == 10:
            vis.delete()
            vis["render"].set_object(g.SceneText("Isaac Asimov",
                                            width=size,
                                            height=size,
                                            font_size = size))
        else:
            vis["render"].set_object(
            g.Plane(width=1, height=1),
            g.MeshPhongMaterial(
                map=g.ImageTexture(image=g.PngImage(image_data.getvalue())), 
                transparent=True, needsUpdate=True))

    interactive_plot = widgets.interactive_output(f, {'change': w_slider})
    return interactive_plot, w_slider