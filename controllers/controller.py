from algorithms.odometry import Odometry
import math


def execute_simulation(ax, parameters):
    if parameters['shape'] == 'rect':
        points = get_rectangle_points()
        prepare_rectangle(ax)
    elif parameters['shape'] == 'circ':
        points = get_circle_points()
        prepare_rectangle(ax)

    a_values = parameters['a']

    if parameters['algorithm'] == 'odometry':
        algorithm = Odometry(a_values, points)

    landmarks = parameters['landmarks']

    draw_initial_points(ax, points)
    plot_landmarks(ax, landmarks)

    number_of_samples = parameters['no_of_samples']
    result_points, example_path = algorithm.sample(number_of_samples)
    draw_result_points(ax, result_points)
    draw_path(ax, example_path)


def prepare_rectangle(ax):
    ax.set_ylim([0, 5])
    ax.set_xlim([0, 9])


def draw_path(ax, example_path):
    for i in xrange(len(example_path) - 1):
        current_point = example_path[i]
        next_point = example_path[i+1]
        ax.arrow(current_point[0], current_point[1], next_point[0] - current_point[0], next_point[1] - current_point[1],
                 head_width=0.05, head_length=0.1)


def draw_result_points(ax, result_points):
    for result_point in result_points:
        ax.plot([result_point[0]], [result_point[1]], 'rcmy'[result_point[3] % 4] + '.')


def draw_initial_points(ax, point_list):
    for point in point_list:
        ax.plot([point[0]], [point[1]], 'bo')


def plot_landmarks(ax, landmarks):
    for landmark in landmarks:
        ax.plot([landmark[0]], [landmark[1]], 'go')
        ax.annotate(str(landmark[2]), xy=(landmark[0], landmark[1]), textcoords='offset points')


def get_rectangle_points():
    point_list = list()
    point_list.append((1, 1))
    point_list.append((2, 1))
    point_list.append((3, 1))
    point_list.append((4, 1))
    point_list.append((4, 2))
    point_list.append((4, 3))
    point_list.append((4, 4))
    point_list.append((3, 4))
    point_list.append((2, 4))
    point_list.append((1, 4))

    return point_list


def get_circle_points():
    point_list = list()
    x_0 = 4
    y_0 = 2
    r = 1.5
    for i in xrange(12):
        theta = (i * math.pi) / 6.0
        point_list.append((x_0 + r * math.cos(theta), y_0 + r * math.sin(theta)))

    return point_list