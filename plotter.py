import matplotlib.pyplot
from matplotlib.patches import Polygon
import numpy as np
from element import Element
from math_2d import Vector2D


def plot_points(points: list[list[float]], plt):
    plt.scatter(*points, s=2)


def plot_polys(polys: list[list[int]], points: list[list[float]], plt):
    colors = ["blue", "orange", "green", "red", "purple", "brown", "pink", "gray", "olive", "cyan"]
    current_color_id = 0
    for i, j, k, _ in zip(*polys):
        i_ind, j_ind, k_ind = int(i), int(j), int(k)
        # points
        x = (points[0][i_ind], points[1][i_ind])
        y = (points[0][j_ind], points[1][j_ind])
        z = (points[0][k_ind], points[1][k_ind])

        current_color = colors[current_color_id]
        plt.plot([x[0], y[0]], [x[1], y[1]], color=f"tab:{current_color}")  # first x and the y
        plt.plot([y[0], z[0]], [y[1], z[1]], color=f"tab:{current_color}")
        plt.plot([z[0], x[0]], [z[1], x[1]], color=f"tab:{current_color}")
        current_color_id = (current_color_id + 1) % len(colors)


def get_color(value: int):
    return matplotlib.pyplot.cm.viridis(value)


def plot_element(element: Element, max_value, ax):
    vertices = np.array([[element.vertex[i][0], element.vertex[i][1]] for i in range(len(element.vertex))])
    polygon = Polygon(
        vertices,
        facecolor=get_color(int(element.u / max_value)),
        edgecolor=get_color(int(element.u / max_value))
    )
    ax.add_patch(polygon)


def plot_elements(elements: list[Element], ax):
    scale = 256
    normalize_coefficient = 0
    for elem in elements:
        normalize_coefficient = max(normalize_coefficient, elem.u / scale)

    for elem in elements:
        plot_element(elem, normalize_coefficient, ax)


def plot_u_polygon(vertex: list[Vector2D], u, max_value, ax):
    vertices = np.array([[vertex[i][0], vertex[i][1]] for i in range(len(vertex))])
    color = get_color(int(u / max_value))
    polygon = Polygon(
        vertices,
        facecolor=color,
        edgecolor=color
    )
    ax.add_patch(polygon)


def plot_polygons(data, norm_coeff, ax):
    for vertex, u in zip(*data):
        plot_u_polygon(vertex, u, norm_coeff, ax)


def create_frame(i, data_per_time, norm_coeff, ax, axes_sizes: tuple[float, float, float, float]):
    matplotlib.pyplot.cla()
    ax.set_xlim(axes_sizes[0] - 0.5, axes_sizes[1] + 0.5)
    ax.set_ylim(axes_sizes[2] - 0.5, axes_sizes[3] + 0.5)
    plot_polygons(data_per_time[i], norm_coeff, ax)
    # ax.legend()
    ax.set_title(f"Time {i}")


