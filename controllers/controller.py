from matplotlib.collections import PatchCollection
from matplotlib.patches import Wedge
from algorithms.odometry import Odometry
from sensors.laser_sensor import LaserSensor
from utils.geom_utils import convert_radian_to_degree
from utils.graphical_utils import draw_ellipse
import math
import matplotlib


def execute_simulation(ax, parameters):
    if parameters['shape'] == 'rect':
        points = get_rectangle_points()
        prepare_rectangle(ax)
    elif parameters['shape'] == 'circ':
        points = get_circle_points()
        prepare_rectangle(ax)

    a_values = parameters['a']
    landmarks = parameters['landmarks']

    if parameters['algorithm'] == 'odometry':
        algorithm = Odometry(a_values, points, landmarks)

    sensor = None
    if parameters['use_sensors']:
        sensor = LaserSensor(parameters['sensor_r'], parameters['sensor_theta'],
                             parameters['sensor_d_error'], parameters['sensor_theta_error'],
                             parameters['sensor_s_error'], landmarks)

    draw_initial_points(ax, points)
    plot_landmarks(ax, landmarks)

    number_of_samples = parameters['no_of_samples']
    distributions, example_path, sense_lines = algorithm.sample(number_of_samples, sensor=sensor)
    draw_result_points(ax, distributions, parameters['sample'])
    draw_path(ax, example_path)

    if parameters['use_sensors']:
        draw_sensor_arcs(ax, example_path, parameters['sensor_r'], parameters['sensor_theta'])
        draw_sense_lines(ax, sense_lines)


def prepare_rectangle(ax):
    ax.set_ylim([0, 5])
    ax.set_xlim([0, 9])


def draw_path(ax, example_path):
    for i in xrange(len(example_path) - 1):
        current_point = example_path[i]
        next_point = example_path[i+1]
        ax.arrow(current_point[0], current_point[1], next_point[0] - current_point[0], next_point[1] - current_point[1],
                 head_width=0.05, head_length=0.1)


def draw_sensor_arcs(ax, example_path, r, theta):
    patches = list()
    for elm in example_path:
        angle = convert_radian_to_degree(elm[2]) - theta / 2.0
        patches.append(Wedge((elm[0], elm[1]), r, angle, angle + theta))

    pc = PatchCollection(patches, cmap=matplotlib.cm.jet, alpha=0.4)
    ax.add_collection(pc)


def draw_sense_lines(ax, sense_lines):
    for sense_line in sense_lines:
        ax.plot([sense_line[0], sense_line[2]], [sense_line[1], sense_line[3]], 'r')


def draw_result_points(ax, distributions, sample):
    if sample:
        for distribution in distributions:
            ax.plot([p[0] for p in distribution.points], [p[1] for p in distribution.points],
                    'rcmy'[distribution.distribution_id % 4] + '.')
    else:
        for i in xrange(1, len(distributions)):
            draw_ellipse(distributions[i].mu[0], distributions[i].mu[1],
                          [[distributions[i].sigma[0][0], distributions[i].sigma[0][1]],
                          [distributions[i].sigma[1][0], distributions[i].sigma[1][1]]])


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
    for i in xrange(13):
        theta = (i * math.pi) / 6.0
        point_list.append((x_0 + r * math.cos(theta), y_0 + r * math.sin(theta)))

    return point_list