import matplotlib
matplotlib.use('Qt5Agg')

import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from controllers.controller import execute_simulation
from ui.widgets import NamedSlider, NamedTextArea
from ui.common import show_error_box, robot_colors
import PyQt5.QtWidgets as widgets


class MainWindow():
    def __init__(self):
        self.main_window = widgets.QMainWindow()
        self.figure = plt.figure()
        self.canvas = FigureCanvas(self.figure)
        self.init_gui()

    def init_gui(self):
        self.init_canvas()
        self.init_execution_parameters_frame()

        eval_type_frame = widgets.QFrame(self.main_window)
        eval_type_frame.setFrameStyle(widgets.QFrame.Box)
        eval_type_frame.setGeometry(800, 530, 200, 70)

        self.eval_type_group = widgets.QButtonGroup(eval_type_frame)

        self.eval_type_sample = widgets.QRadioButton('Sample', eval_type_frame)
        self.eval_type_sample.setGeometry(5, 5, 150, 30)
        self.eval_type_group.addButton(self.eval_type_sample)

        self.eval_type_direct = widgets.QRadioButton('Direct', eval_type_frame)
        self.eval_type_direct.setGeometry(5, 35, 150, 30)
        self.eval_type_group.addButton(self.eval_type_direct)

        self.number_of_samples = NamedTextArea(self.main_window)
        self.number_of_samples.init_gui('No. of Samples', 800, 600, 110, 50)

        button = widgets.QPushButton('Execute', self.main_window)
        button.clicked.connect(self.execute)
        button.setGeometry(800, 670, 100, 30)

        self.main_window.setGeometry(100, 100, 1024, 700)
        self.main_window.setFixedSize(1024, 768)
        self.main_window.setWindowTitle('Probabilistic Robotics')

        self.reset_canvas()

    def init_canvas(self):
        self.canvas.setParent(self.main_window)
        self.canvas.setGeometry(10, 10, 1000, 475)
        self.canvas.mpl_connect('button_press_event', self)

    def init_execution_parameters_frame(self):
        execution_parameters_frame = widgets.QFrame(self.main_window)
        execution_parameters_frame.setGeometry(10, 500, 750, 200)

        self.tab_widget = widgets.QTabWidget(execution_parameters_frame)
        self.tab_widget.setGeometry(0, 0, 750, 200)

        self.tab_widget.addTab(self.get_motion_model_tab(), 'Motion Model')
        self.tab_widget.addTab(self.get_sensor_model_tab(), 'Sensor Model')
        self.tab_widget.addTab(self.get_landmark_tab(), 'Landmarks')
        self.tab_widget.addTab(self.get_multirobot_tab(), 'Robots')

    def get_motion_model_tab(self):
        motion_model_parameters_frame = widgets.QFrame()

        self.odometry_errors = [None] * 4
        for i in range(len(self.odometry_errors)):
            self.odometry_errors[i] = NamedSlider(motion_model_parameters_frame, 100)
            self.odometry_errors[i].init_gui('a' + str(i + 1), 10, i*30, 30, 150, 40)

        return motion_model_parameters_frame

    def get_sensor_model_tab(self):
        sensor_model_parameters_frame = widgets.QFrame()

        self.sensing_distance = NamedTextArea(sensor_model_parameters_frame)
        self.sensing_distance.init_gui('Distance', 10, 10, 110, 40)

        self.laser_angle = NamedTextArea(sensor_model_parameters_frame)
        self.laser_angle.init_gui('Angle', 10, 40, 110, 40)

        self.sensing_distance_error = NamedSlider(sensor_model_parameters_frame, 100)
        self.sensing_distance_error.init_gui('Dist. error', 200, 10, 80, 150, 40)

        self.sensing_theta_error = NamedSlider(sensor_model_parameters_frame, 100)
        self.sensing_theta_error.init_gui('Theta error', 200, 40, 80, 150, 40)

        self.sensing_signature_error = NamedSlider(sensor_model_parameters_frame, 100)
        self.sensing_signature_error.init_gui('Sign. error', 200, 70, 80, 150, 40)

        self.enable_sensors = widgets.QCheckBox('Enable sensors', sensor_model_parameters_frame)
        self.enable_sensors.setGeometry(500, 10, 150, 20)

        return sensor_model_parameters_frame

    def get_landmark_tab(self):
        self.landmarks = list()

        landmark_frame = widgets.QFrame()

        self.landmark_list = widgets.QListWidget(landmark_frame)
        self.landmark_list.setGeometry(10, 10, 150, 145)

        remove_landmark_button = widgets.QPushButton('-', landmark_frame)
        remove_landmark_button.setGeometry(170, 50, 30, 30)
        remove_landmark_button.clicked.connect(self.remove_selected_landmark)

        clear_landmarks_button = widgets.QPushButton('Clear All', landmark_frame)
        clear_landmarks_button.setGeometry(300, 10, 150, 30)
        clear_landmarks_button.clicked.connect(self.remove_all_landmarks)

        return landmark_frame

    def get_multirobot_tab(self):
        multirobot_frame = widgets.QFrame()

        robot_frame = widgets.QFrame(multirobot_frame)
        robot_frame.setFrameStyle(widgets.QFrame.Box)
        robot_frame.setGeometry(10, 10, 110, 150)

        self.robot_group = widgets.QButtonGroup(multirobot_frame)

        self.robots = list()
        self.robot_points = list()

        for i in range(3):
            def make_lambda(index):
                return lambda: self.update_robot_list(index)

            robot = widgets.QRadioButton('Robot - ' + str(i+1), robot_frame)
            robot.setGeometry(5, 5 + i * 30, 100, 30)
            robot.clicked.connect(make_lambda(i))

            self.robots.append(robot)
            self.robot_group.addButton(robot)
            self.robot_points.append(list())

        self.robot_list = widgets.QListWidget(multirobot_frame)
        self.robot_list.setGeometry(150, 10, 150, 145)

        remove_robot_point = widgets.QPushButton('-', multirobot_frame)
        remove_robot_point.setGeometry(310, 50, 30, 30)
        remove_robot_point.clicked.connect(self.remove_selected_robot_point)

        clear_landmarks_button = widgets.QPushButton('Clear All', multirobot_frame)
        clear_landmarks_button.setGeometry(350, 10, 150, 30)
        clear_landmarks_button.clicked.connect(self.remove_all_robot_points)

        self.enable_communication = widgets.QCheckBox('Enable communication', multirobot_frame)
        self.enable_communication.setGeometry(520, 10, 200, 20)

        self.enable_one_way_update = widgets.QCheckBox('One way update', multirobot_frame)
        self.enable_one_way_update.setGeometry(520, 40, 200, 20)

        self.communication_distance = NamedTextArea(multirobot_frame)
        self.communication_distance.init_gui('Comm. Distance', 520, 120, 150, 40)

        return multirobot_frame

    def reset_canvas(self):
        ax = self.figure.gca()
        ax.cla()
        ax.set_ylim([0, 5])
        ax.set_xlim([0, 9])

        self.plot_landmarks()
        self.plot_robot_points()
        self.canvas.draw()

    def execute(self):
        a_values = list()
        for odometry_error in self.odometry_errors:
            a_values.append(odometry_error.get_value())

        ax = self.figure.gca()
        ax.cla()

        execution_parameters = dict()

        execution_parameters['points'] = self.get_robot_points()

        if len(execution_parameters['points']) == 0:
            show_error_box(self.main_window, 'En az 1 robot icin yol bilgisi girilmelidir')
            return

        execution_parameters['use_communication'] = self.enable_communication.isChecked()
        execution_parameters['one_way_update'] = self.enable_one_way_update.isChecked()
        execution_parameters['use_sensors'] = self.enable_sensors.isChecked()
        if execution_parameters['use_communication']:
            try:
                execution_parameters['comm_distance'] = float(self.communication_distance.get_text())
            except Exception:
                show_error_box(self.main_window, 'Hatali iletisim uzakligi')
                return

        if self.enable_sensors.isChecked():
            try:
                execution_parameters['sensor_r'] = float(self.sensing_distance.get_text())
            except Exception:
                show_error_box(self.main_window, 'Hatali sensor uzakligi')
                return

            try:
                execution_parameters['sensor_theta'] = float(self.laser_angle.get_text())
            except Exception:
                show_error_box(self.main_window, 'Hatali sensor acisi')
                return

            execution_parameters['sensor_d_error'] = float(self.sensing_distance_error.get_value())
            execution_parameters['sensor_theta_error'] = float(self.sensing_theta_error.get_value())
            execution_parameters['sensor_s_error'] = float(self.sensing_signature_error.get_value())

        execution_parameters['landmarks'] = self.landmarks
        try:
            execution_parameters['no_of_samples'] = int(self.number_of_samples.get_text())
        except Exception:
            show_error_box(self.main_window, 'Hatali ornek sayisi')
            return

        execution_parameters['a'] = a_values
        execution_parameters['sample'] = (self.eval_type_group.checkedButton() == self.eval_type_sample)

        execute_simulation(ax, execution_parameters)

        self.canvas.draw()

    def get_robot_points(self):
        return [(i, robot_list) for i, robot_list in enumerate(self.robot_points) if len(robot_list) > 0]

    def show(self):
        self.main_window.show()

    def __call__(self, event):
        current_tab = self.tab_widget.currentIndex()
        if current_tab == 2: #add landmarks
            self.add_landmark(event.xdata, event.ydata)
        elif current_tab == 3: #add robot point
            self.add_robot_point(event.xdata, event.ydata)

    def update_robot_list(self, index):
        num_of_points = len(self.robot_points[index])
        self.refresh_robot_list(num_of_points)

    def remove_selected_landmark(self):
        selected_items = list(self.landmark_list.selectedItems())
        for selected_item in selected_items:
            self.landmark_list.takeItem(self.landmark_list.row(selected_item))
            current_item_id = int(str(selected_item.text()))
            self.landmarks = [landmark for landmark in self.landmarks if landmark[2] != current_item_id]
        self.reset_canvas()

    def get_selected_robot_index(self):
        if self.robot_group.checkedButton() is None:
            return -1

        return [i for i in range(len(self.robot_points)) if self.robots[i] == self.robot_group.checkedButton()][0]

    def remove_selected_robot_point(self):
        current_robot_index = self.get_selected_robot_index()
        if current_robot_index == -1:
            return

        selected_items = [str(selected_item.text()) for selected_item in self.robot_list.selectedItems()]
        new_point_list = list()

        for i in range(len(self.robot_points[current_robot_index])):
            if str(i+1) not in selected_items:
                new_point_list.append(self.robot_points[current_robot_index][i])

        self.robot_points[current_robot_index] = new_point_list
        self.refresh_robot_list(len(new_point_list))
        self.reset_canvas()

    def remove_all_landmarks(self):
        self.landmark_list.clear()
        self.landmarks = list()
        self.reset_canvas()

    def remove_all_robot_points(self):
        self.robot_list.clear()
        self.robot_points = list()
        for robot_points in range(3):
            self.robot_points.append(list())
        self.reset_canvas()

    def add_landmark(self, x, y):
        landmark_id = 0 if len(self.landmarks) == 0 else max([landmark[2] for landmark in self.landmarks]) + 1
        self.landmarks.append((x, y, landmark_id))
        self.landmark_list.addItem(str(landmark_id))
        self.reset_canvas()

    def add_robot_point(self, x, y):
        current_robot_index = self.get_selected_robot_index()
        if current_robot_index == -1:
            return

        self.robot_points[current_robot_index].append((x, y))
        self.refresh_robot_list(len(self.robot_points[current_robot_index]))
        self.reset_canvas()

    def refresh_robot_list(self, num_of_points):
        self.robot_list.clear()
        for i in range(1, num_of_points + 1):
            self.robot_list.addItem(str(i))

    def plot_landmarks(self):
        ax = self.figure.gca()
        for landmark in self.landmarks:
            ax.plot([landmark[0]], [landmark[1]], 'go')
            ax.annotate(str(landmark[2]), xy=(landmark[0], landmark[1]), textcoords='offset points', xytext=(landmark[0], landmark[1]))
        self.canvas.draw()

    def plot_robot_points(self):
        ax = self.figure.gca()
        for i in range(len(self.robots)):
            ax.plot([p[0] for p in self.robot_points[i]], [p[1] for p in self.robot_points[i]], robot_colors[i] + 's')
            ax.plot([p[0] for p in self.robot_points[i]], [p[1] for p in self.robot_points[i]], robot_colors[i])