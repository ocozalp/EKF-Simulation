import PyQt4.QtGui as gui
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from odometry import Odometry
from widgets import NamedSlider, NamedTextArea
from dead_reckoning import DeadReckoning
import math


class MainWindow():
    def __init__(self):
        self.main_window = gui.QMainWindow()
        self.figure = plt.figure()
        self.canvas = FigureCanvas(self.figure)
        self.init_gui()

    def init_gui(self):
        self.init_canvas()
        self.init_common_frame()
        self.init_motion_model_frame()

        self.eval_type_button_selected()
        self.algorithm_button_selected()
        self.shape_button_selected()

        self.main_window.setGeometry(100, 100, 1024, 768)
        #self.main_window.setFixedSize(1024, 768)
        self.main_window.setWindowTitle('Probabilistic Robotics')

    def init_canvas(self):
        self.canvas.setParent(self.main_window)
        self.canvas.setGeometry(10, 10, 1000, 475)

    def init_common_frame(self):
        common_frame = gui.QFrame(self.main_window)
        common_frame.setFrameStyle(gui.QFrame.Box)
        common_frame.setGeometry(10, 500, 240, 300)

        self.init_algorithm_frame(common_frame)
        self.init_eval_type_frame(common_frame)
        self.init_shape_frame(common_frame)

        button = gui.QPushButton('Execute', common_frame)
        button.clicked.connect(self.execute)
        button.setGeometry(130, 245, 100, 30)

    def init_algorithm_frame(self, parent_frame):
        algorithm_frame = gui.QFrame(parent_frame)
        algorithm_frame.setFrameStyle(gui.QFrame.Box)
        algorithm_frame.setGeometry(10, 10, 220, 70)

        self.algorithm_group = gui.QButtonGroup(algorithm_frame)

        self.dead_reckoning_button = gui.QRadioButton('Dead Reckoning', algorithm_frame)
        self.dead_reckoning_button.setGeometry(5, 5, 150, 30)
        self.dead_reckoning_button.clicked.connect(self.algorithm_button_selected)
        self.algorithm_group.addButton(self.dead_reckoning_button)

        self.odometry_button = gui.QRadioButton('Odometry', algorithm_frame)
        self.odometry_button.setGeometry(5, 35, 150, 30)
        self.odometry_button.clicked.connect(self.algorithm_button_selected)
        self.algorithm_group.addButton(self.odometry_button)

    def init_eval_type_frame(self, parent_frame):
        eval_type_frame = gui.QFrame(parent_frame)
        eval_type_frame.setFrameStyle(gui.QFrame.Box)
        eval_type_frame.setGeometry(10, 90, 220, 70)

        self.eval_type_group = gui.QButtonGroup(eval_type_frame)

        self.sampled_execution = gui.QRadioButton('Sampled', eval_type_frame)
        self.sampled_execution.setGeometry(5, 5, 150, 30)
        self.sampled_execution.clicked.connect(self.eval_type_button_selected)
        self.eval_type_group.addButton(self.sampled_execution)

        self.direct_evaluation = gui.QRadioButton('Direct', eval_type_frame)
        self.direct_evaluation.setGeometry(5, 35, 150, 30)
        self.direct_evaluation.clicked.connect(self.eval_type_button_selected)
        self.eval_type_group.addButton(self.direct_evaluation)

    def init_shape_frame(self, parent_frame):
        shape_frame = gui.QFrame(parent_frame)
        shape_frame.setFrameStyle(gui.QFrame.Box)
        shape_frame.setGeometry(10, 170, 220, 70)

        self.shape_group = gui.QButtonGroup(shape_frame)

        self.circular_shape = gui.QRadioButton('Circular', shape_frame)
        self.circular_shape.setGeometry(5, 5, 150, 30)
        self.circular_shape.clicked.connect(self.shape_button_selected)
        self.shape_group.addButton(self.circular_shape)

        self.rectangular_shape = gui.QRadioButton('Rectangular', shape_frame)
        self.rectangular_shape.setGeometry(5, 35, 150, 30)
        self.rectangular_shape.clicked.connect(self.shape_button_selected)
        self.shape_group.addButton(self.rectangular_shape)

    def init_motion_model_frame(self):
        motion_model_frame = gui.QFrame(self.main_window)
        motion_model_frame.setFrameStyle(gui.QFrame.Box)
        motion_model_frame.setGeometry(260, 500, 750, 200)

        self.sliders = [None] * 6
        for i in xrange(len(self.sliders)):
            self.sliders[i] = NamedSlider(motion_model_frame, 10)
            self.sliders[i].init_gui('a' + str(i + 1), 10, i*30, 30, 150, 40)

        self.radius = NamedTextArea(motion_model_frame)
        self.radius.init_gui('r', 350, 0, 50, 50)

        self.number_of_points = NamedTextArea(motion_model_frame)
        self.number_of_points.init_gui('Points', 350, 30, 50, 50)

        self.number_of_samples = NamedTextArea(motion_model_frame)
        self.number_of_samples.init_gui('No. of Samples', 500, 0, 110, 50)

    def eval_type_button_selected(self):
        selected_button = self.eval_type_group.checkedButton()
        self.reset_canvas()
        if selected_button == self.sampled_execution:
            self.prepare_sampled_widgets()
        else:
            self.prepare_direct_widgets()

    def prepare_sampled_widgets(self):
        self.number_of_samples.setVisible(True)

    def prepare_direct_widgets(self):
        self.number_of_samples.setVisible(False)

    def shape_button_selected(self):
        selected_button = self.shape_group.checkedButton()
        self.reset_canvas()
        if selected_button == self.circular_shape:
            self.prepare_circular_widgets()
        else:
            self.prepare_rectangular_widgets()

    def prepare_circular_widgets(self):
        self.number_of_points.setVisible(True)

    def prepare_rectangular_widgets(self):
        self.number_of_points.setVisible(False)

    def algorithm_button_selected(self):
        selected_button = self.algorithm_group.checkedButton()
        self.reset_canvas()
        if selected_button == self.dead_reckoning_button:
            self.prepare_dead_reckoning_widgets()
        else:
            self.prepare_odometry_widgets()

    def prepare_dead_reckoning_widgets(self):
        #self.radius.setVisible(True)
        self.sliders[4].setVisible(True)
        self.sliders[5].setVisible(True)

    def prepare_odometry_widgets(self):
        #self.radius.setVisible(False)
        self.sliders[4].setVisible(False)
        self.sliders[5].setVisible(False)

    def reset_canvas(self):
        ax = self.figure.gca()
        ax.cla()
        ax.set_ylim([0, 10])
        ax.set_xlim([0, 10])
        self.canvas.draw()

    def execute(self):
        a_values = list()
        for i in xrange(6):
            a_values.append(self.sliders[i].get_value())

        ax = self.figure.gca()
        ax.cla()

        if self.algorithm_group.checkedButton() == self.dead_reckoning_button:
            results = self.execute_dead_reckoning(a_values, ax)
        elif self.algorithm_group.checkedButton() == self.odometry_button:
            results = self.execute_odometry(a_values, ax)

        for result in results:
            ax.plot([result[0]], [result[1]], 'r.')

        self.canvas.draw()

    def execute_odometry(self, a_values, ax):
        algorithm = Odometry(a_values)

        if self.shape_group.checkedButton() == self.circular_shape:
            if self.eval_type_group.checkedButton() == self.sampled_execution:
                r = float(self.radius.get_text())
                no_of_pts = int(self.number_of_points.get_text())
                no_of_samples = int(self.number_of_samples.get_text())
                self.prepare_circular(ax, r, no_of_pts)
                return algorithm.sample_circular(r, r+1, r+1, no_of_pts, no_of_samples)
        elif self.shape_group.checkedButton() == self.rectangular_shape:
            if self.eval_type_group.checkedButton() == self.sampled_execution:
                no_of_samples = int(self.number_of_samples.get_text())
                point_list = self.prepare_rectanglar(ax)
                return algorithm.sample_rectangular(point_list, no_of_samples)

        return list()

    def execute_dead_reckoning(self, a_values, ax):
        algorithm = DeadReckoning(a_values)

        if self.shape_group.checkedButton() == self.circular_shape:
            if self.eval_type_group.checkedButton() == self.sampled_execution:
                r = float(self.radius.get_text())
                no_of_pts = int(self.number_of_points.get_text())
                no_of_samples = int(self.number_of_samples.get_text())
                self.prepare_circular(ax, r, no_of_pts)
                return algorithm.sample_circular(r, r+1, r+1, no_of_pts, no_of_samples)
        elif self.shape_group.checkedButton() == self.rectangular_shape:
            if self.eval_type_group.checkedButton() == self.sampled_execution:
                r = float(self.radius.get_text())
                no_of_samples = int(self.number_of_samples.get_text())
                point_list = self.prepare_rectanglar(ax)
                return algorithm.sample_rectangular(r, point_list, no_of_samples)

    def prepare_circular(self, ax, r, no_of_pts):
        ax.set_ylim([0, 2*r + 2])
        ax.set_xlim([0, 2*r + 2])
        ax.plot([r+1], [r+1], 'b.')

        for i in xrange(no_of_pts):
            ax.plot([r+1 + r*math.sin(2*i*math.pi / no_of_pts)], [r+1 - r*math.cos(2*i*math.pi / no_of_pts)], 'bo')

    def prepare_rectanglar(self, ax):
        point_list = list()
        point_list.append((1, 1))
        point_list.append((2, 1))
        point_list.append((3, 1))
        point_list.append((4, 1))
        point_list.append((4, 2))
        point_list.append((4, 3))
        point_list.append((3, 3))
        point_list.append((2, 3))

        ax.set_ylim([0, 5])
        ax.set_xlim([0, 5])
        ax.plot([1], [1], 'b.')
        for point in point_list:
            ax.plot([point[0]], [point[1]], 'b.')

        return point_list

    def show(self):
        self.main_window.show()


