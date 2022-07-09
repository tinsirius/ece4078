import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.lines import Line2D
import numpy as np
import math

def plot_obstacles(obstacles, ax):
    for obs in obstacles:
        ox, oy = obs.plot_obstacle()
        ax.scatter(ox, oy, s=7, c='k')

def animate_path_bug1(initial_robot_pos,goal_pos,path,obstacles):
    # Set plot variables
    fig = plt.figure()
    ax = fig.add_subplot(111, aspect='equal', autoscale_on=False,
                         xlim=(0, 50), ylim=(0, 60))
    ax.grid()

    goal, = ax.plot([], [], 'o', lw=2, c='g')
    path_line, = ax.plot([], [], 'r', lw=2)
    robot, = ax.plot([], [], 'ob', lw=3)
    plot_obstacles(obstacles, ax)
    steps_text = ax.text(0.02, 0.95, '', transform=ax.transAxes)

    # Define the start and goal positions 
    g_x, g_y = goal_pos
    s_x, s_y = initial_robot_pos
    
    if len(path) == 0:
        print("Path was not found!!")
        ani = 0
        return
        
    else:
        # Animation code
        def init():
            goal.set_data(g_x, g_y)
            robot.set_data(s_x, s_y)
            path_line.set_data(s_x, s_y)
            steps_text.set_text('')
            return robot, goal, path_line, steps_text

        def animate(i):
            """perform animation step"""
            if i < path.shape[0]:
                pos = path[i,:]
                robot.set_data(pos[0], pos[1])
                path_line.set_data(path[:i, 0], path[:i, 1])
                steps_text.set_text('Steps: %.1f' % i)
            return robot, path_line

        ani = animation.FuncAnimation(fig, animate, frames=600, repeat=False, interval=10, init_func=init)
        return ani


def animate_path_bug2(initial_robot_pos,goal_pos,path,obstacles):
    # Set plot variables
    fig = plt.figure()
    ax = fig.add_subplot(111, aspect='equal', autoscale_on=False,
                         xlim=(0, 50), ylim=(0, 60))
    ax.grid()

    goal, = ax.plot([], [], 'o', lw=2, c='g')
    line, = ax.plot([], [], 'r--', lw=1)
    path_line, = ax.plot([], [], 'g', lw=2)
    robot, = ax.plot([], [], 'ob', lw=4)
    steps_text = ax.text(0.02, 0.95, '', transform=ax.transAxes)
    custom_lines = [Line2D([0], [0], color='r', lw=4)]
    ax.legend(custom_lines, ['start-goal line'])

    plot_obstacles(obstacles, ax)

    s_x, s_y = initial_robot_pos
    g_x, g_y = goal_pos
    
    if len(path)==0:
        print("Path was not found!!")
    else:
        # Animation code
        def init():
            goal.set_data(g_x, g_y)
            robot.set_data(s_x, s_y)
            path_line.set_data(s_x, s_y)
            steps_text.set_text('')
            line.set_data([s_x, g_x], [s_y, g_y])
            return robot, goal, path_line, steps_text

        def animate(i):
            """perform animation step"""
            pos = path[i,:]
            robot.set_data(pos[0], pos[1])
            path_line.set_data(path[:i, 0], path[:i, 1])
            steps_text.set_text('Steps: %.1f' % i)
            return robot, path_line

        ani = animation.FuncAnimation(fig, animate, frames=700, blit=True, interval=10, init_func=init)
        return ani
    
def plot_circle(ax, x, y, size, color="-b"):  
        deg = list(range(0, 360, 5))
        deg.append(0)
        xl = [x + size * math.cos(np.deg2rad(d)) for d in deg]
        yl = [y + size * math.sin(np.deg2rad(d)) for d in deg]
        ax.plot(xl, yl, color)    
    
def animate_path_rrt(rrt):
    path = rrt.planning()
    
    fig = plt.figure(figsize=(8, 6))
    ax = fig.add_subplot(111, aspect='equal', autoscale_on=False,
                         xlim=(0, 16), ylim=(0, 12))
    ax.grid()

    ax.plot(rrt.start.x, rrt.start.y, "^r", lw=5)
    ax.plot(rrt.end.x, rrt.end.y, "^c", lw=5)

    for obs in rrt.obstacle_list:
        cx, cy = obs.center
        plot_circle(ax, cx, cy, obs.radius)

    for node in rrt.node_list:
        if node.parent:
            ax.plot(node.path_x, node.path_y, "g.-")

    line_path, = ax.plot([], [], "b", lw=3)

    if path is not None:
        path_in_order = np.flipud(path)
        start_pos = path_in_order[0,:]

        def init():
            line_path.set_data(path_in_order[0], path_in_order[1])
            return line_path

        def animate(i):
            """perform animation step"""
            line_path.set_data(path_in_order[:i,0], path_in_order[:i, 1])
            return line_path

        ani = animation.FuncAnimation(fig, animate, frames=30, blit=True, interval=100, init_func=init)
        return ani
    else:
        print("Path was not found!!")
    
def animate_path_rrtc(rrtc):
    path = rrtc.planning()
    
    fig = plt.figure(figsize=(8, 6))
    ax = fig.add_subplot(111, aspect='equal', autoscale_on=False,
                         xlim=(0, 16), ylim=(0, 12))
    ax.grid()

    ax.plot(rrtc.start.x, rrtc.start.y, "^r", lw=5)
    ax.plot(rrtc.end.x, rrtc.end.y, "^c", lw=5)

    for obs in rrtc.obstacle_list:
        cx, cy = obs.center
        plot_circle(ax, cx, cy, obs.radius)

    for node in rrtc.start_node_list:
        if node.parent:
            ax.plot(node.path_x, node.path_y, "g.-")

    for node in rrtc.end_node_list:
        if node.parent:
            ax.plot(node.path_x, node.path_y, "b.-")
            
    line_path, = ax.plot([], [], "r", lw=3)
    custom_lines = [Line2D([0], [0], color='g', lw=4), Line2D([0], [0], color='b', lw=4)]
    ax.legend(custom_lines, ['Start tree', 'End tree'])

    if path is not None:
        path = np.array(path)
        start_pos = path[0,:]
        
        def init():
            line_path.set_data(start_pos[0], start_pos[1])
            return line_path

        def animate(i):
            """perform animation step"""
            line_path.set_data(path[:i,0], path[:i, 1])
            return line_path

        ani = animation.FuncAnimation(fig, animate, frames=30, repeat=False, interval=100, init_func=init)
        return ani
    else:
        print("Path was not found!!")
        
def animate_path_prm(rmap,start, goal, num_samples, robot_size, max_distance, max_neighbours):
    fig = plt.figure(figsize=(8, 6))
    ax = fig.add_subplot(111, aspect='equal', autoscale_on=False,
                         xlim=(-10, 70), ylim=(-10, 70))
    plt.grid(True)

    obs = rmap.obstacles.data
    ax.plot(obs[:,0], obs[:,1], ".k")

    rmap.__generate_roadmap__(num_samples, max_distance, max_neighbours, robot_size)

    for i, v_edges in enumerate(rmap.edges):
        for e_idx in v_edges:
            v_from = rmap.vertices[i,:]
            v_to = rmap.vertices[e_idx,:]

            ax.plot([v_from[0], v_to[0]],
                    [v_from[1], v_to[1]], "k--", lw=0.5)
    
    path = rmap.plan(start, goal)

    # Animation code
    start_plot, = ax.plot([], [], "^r", lw=5)
    goal_plot, = ax.plot([], [], "^c", lw=5)
    line_path, = ax.plot([], [], "b", lw=2)    

    if path is not None:
        path_in_order = np.flipud(path)
        start_pos = path_in_order[0,:]

        def init():
            print(init)
            start_plot.set_data(start[0], start[1])
            goal_plot.set_data(goal[0], goal[1])
            line_path.set_data([], [])
            return line_path, start_plot, goal_plot

        def animate(i):
            """perform animation step"""
            line_path.set_data(path_in_order[:i,0], path_in_order[:i, 1])
            return line_path

        ani = animation.FuncAnimation(fig, animate, frames=30, blit=True, interval=30, init_func=init)
        return ani
    else:
        print("Path was not found!!")