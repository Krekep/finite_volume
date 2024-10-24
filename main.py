from copy import deepcopy

import matplotlib.pyplot as plt
import numpy as np
from matplotlib import animation

from loader import load_from_file
from math_2d import Vector2D
from plotter import plot_points, plot_polys, plot_elements, create_frame
from solver import HeatEquationSolver


def scaling_u(elem_per_time: list[tuple[list[Vector2D], list[float]]]) -> float:
    scale = 256
    normalize_coefficient = 0
    for elem in elem_per_time:
        for u in elem[1]:
            normalize_coefficient = max(normalize_coefficient, u / scale)
    return normalize_coefficient


if __name__ == '__main__':
    filename = "circle_eye"
    points, polys, bound = load_from_file(filename)
    min_x, max_x = min(points[0]), max(points[0])
    min_y, max_y = min(points[1]), max(points[1])
    fig, ax = plt.subplots()
    ax.set_xlim(min_x - 0.5, max_x + 0.5)
    ax.set_ylim(min_y - 0.5, max_y + 0.5)
    # plot_points(points, ax)
    # plot_polys(polys, points, ax)
    # plt.show()
    # create_surface("p")


    world = HeatEquationSolver(domain=filename)
    world.create_volume_decomposition(points, polys, bound)

    count_times = 256

    elem_per_time: list[tuple[list[Vector2D], list[float]]] = [[] for _ in range(count_times)]
    for t in range(count_times):
        world.run_physics()

        plot_elements(world.elements, ax)
        vertices = [deepcopy(elem.vertex) for elem in world.elements]
        u = [elem.u for elem in world.elements]
        elem_per_time[t] = (vertices, u)

    norm_coeff = scaling_u(elem_per_time)
    ani = animation.FuncAnimation(fig, create_frame, fargs=[elem_per_time, norm_coeff, ax, (min_x, max_x, min_y, max_y)], frames=count_times)
    ani.save(f'heat_{filename}_{count_times}.gif', writer='pillow', fps=15)

