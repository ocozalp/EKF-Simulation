from algorithms.odometry import Odometry
import matplotlib.pyplot as plt


def execute_simulation(ax, parameters):
    if parameters['shape'] == 'rect':
        points = get_rectangle_points()
        prepare_rectangle(ax)

    a_values = parameters['a']

    if parameters['algorithm'] == 'odometry':
        algorithm = Odometry(a_values, points)

    landmarks = parameters['landmarks']

    draw_initial_points(ax, points)
    plot_landmarks(ax, landmarks)

    number_of_samples = parameters['no_of_samples']
    result_points = algorithm.sample(number_of_samples)
    draw_result_points(ax, result_points)


def draw_distributions(ax, distributions):
    for distribution in distributions:
        plt.pcolormesh(distribution[0], distribution[1], distribution[2], cmap='Greys')


def prepare_rectangle(ax):
    ax.set_ylim([0, 5])
    ax.set_xlim([0, 5])


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