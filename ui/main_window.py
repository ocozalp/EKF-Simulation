import PyQt4.QtGui as gui
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from controllers.controller import execute_simulation
from ui.widgets import NamedSlider, NamedTextArea


class MainWindow():
    def __init__(self):
        self.main_window = gui.QMainWindow()
        self.figure = plt.figure()
        self.canvas = FigureCanvas(self.figure)
        self.init_gui()


    def init_gui(self):
        self.init_canvas()
        self.init_common_frame()
        self.init_execution_parameters_frame()

        self.eval_type_button_selected()

        self.main_window.setGeometry(100, 100, 1024, 768)
        self.main_window.setFixedSize(1024, 768)
        self.main_window.setWindowTitle('Probabilistic Robotics')

    def init_canvas(self):
        self.canvas.setParent(self.main_window)
        self.canvas.setGeometry(10, 10, 1000, 475)
        self.canvas.mpl_connect('button_press_event', self)

    def init_common_frame(self):
        common_frame = gui.QFrame(self.main_window)
        common_frame.setFrameStyle(gui.QFrame.Box)
        common_frame.setGeometry(10, 500, 240, 220)

        eval_type_frame = gui.QFrame(common_frame)
        eval_type_frame.setFrameStyle(gui.QFrame.Box)
        eval_type_frame.setGeometry(10, 10, 220, 70)

        self.eval_type_group = gui.QButtonGroup(eval_type_frame)

        self.sampled_execution = gui.QRadioButton('Sampled', eval_type_frame)
        self.sampled_execution.setGeometry(5, 5, 150, 30)
        self.sampled_execution.clicked.connect(self.eval_type_button_selected)
        self.eval_type_group.addButton(self.sampled_execution)

        self.direct_evaluation = gui.QRadioButton('Direct', eval_type_frame)
        self.direct_evaluation.setGeometry(5, 35, 150, 30)
        self.direct_evaluation.clicked.connect(self.eval_type_button_selected)
        self.eval_type_group.addButton(self.direct_evaluation)

        button = gui.QPushButton('Execute', common_frame)
        button.clicked.connect(self.execute)
        button.setGeometry(130, 165, 100, 30)

    def init_execution_parameters_frame(self):
        execution_parameters_frame = gui.QFrame(self.main_window)
        execution_parameters_frame.setGeometry(260, 500, 750, 220)

        tab_widget = gui.QTabWidget(execution_parameters_frame)
        tab_widget.setGeometry(0, 0, 750, 220)

        tab_widget.addTab(self.get_motion_model_tab(), 'Motion Model')
        tab_widget.addTab(self.get_sensor_model_tab(), 'Sensor Model')
        tab_widget.addTab(self.get_landmark_tab(), 'Landmarks')

    def get_motion_model_tab(self):
        motion_model_parameters_frame = gui.QFrame()

        self.sliders = [None] * 4
        for i in xrange(len(self.sliders)):
            self.sliders[i] = NamedSlider(motion_model_parameters_frame, 100)
            self.sliders[i].init_gui('a' + str(i + 1), 10, i*30, 30, 150, 40)

        self.number_of_samples = NamedTextArea(motion_model_parameters_frame)
        self.number_of_samples.init_gui('No. of Samples', 350, 0, 110, 50)

        return motion_model_parameters_frame

    def get_sensor_model_tab(self):
        sensor_model_parameters_frame = gui.QFrame()

        self.sensing_distance = NamedTextArea(sensor_model_parameters_frame)
        self.sensing_distance.init_gui('Distance', 10, 10, 110, 40)

        self.laser_angle = NamedTextArea(sensor_model_parameters_frame)
        self.laser_angle.init_gui('Angle', 10, 40, 110, 40)

        return sensor_model_parameters_frame

    def get_landmark_tab(self):
        self.landmarks = list()

        landmark_frame = gui.QFrame()

        self.landmark_list = gui.QListWidget(landmark_frame)
        self.landmark_list.setGeometry(10, 10, 150, 165)

        remove_landmark_button = gui.QPushButton('-', landmark_frame)
        remove_landmark_button.setGeometry(170, 50, 30, 30)
        remove_landmark_button.clicked.connect(self.remove_selected_landmark)

        clear_landmarks_button = gui.QPushButton('Clear All', landmark_frame)
        clear_landmarks_button.setGeometry(300, 10, 150, 30)
        clear_landmarks_button.clicked.connect(self.remove_all_landmarks)

        return landmark_frame

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

    def reset_canvas(self):
        ax = self.figure.gca()
        ax.cla()
        ax.set_ylim([0, 5])
        ax.set_xlim([0, 5])
        self.plot_landmarks()
        self.canvas.draw()

    def execute(self):
        a_values = list()
        for slider in self.sliders:
            a_values.append(slider.get_value())

        ax = self.figure.gca()
        ax.cla()

        execution_parameters = dict()
        execution_parameters['algorithm'] = 'odometry'
        execution_parameters['shape'] = 'rect'
        execution_parameters['landmarks'] = self.landmarks
        execution_parameters['no_of_samples'] = int(self.number_of_samples.get_text())
        execution_parameters['a'] = a_values

        execute_simulation(ax, execution_parameters)

        self.canvas.draw()

    def show(self):
        self.main_window.show()

    def __call__(self, event):
        self.add_landmark(event.xdata, event.ydata)

    def remove_selected_landmark(self):
        selected_items = list(self.landmark_list.selectedItems())
        for selected_item in selected_items:
            self.landmark_list.takeItem(self.landmark_list.row(selected_item))
            current_item_id = int(str(selected_item.text()))
            self.landmarks = [landmark for landmark in self.landmarks if landmark[2] != current_item_id]
        self.reset_canvas()

    def remove_all_landmarks(self):
        self.landmark_list.clear()
        self.landmarks = list()
        self.reset_canvas()

    def add_landmark(self, x, y):
        landmark_id = 0 if len(self.landmarks) == 0 else max([landmark[2] for landmark in self.landmarks]) + 1
        self.landmarks.append((x, y, landmark_id))
        self.landmark_list.addItem(str(landmark_id))
        self.reset_canvas()

    def plot_landmarks(self):
        ax = self.figure.gca()
        for landmark in self.landmarks:
            ax.plot([landmark[0]], [landmark[1]], 'go')
            ax.annotate(str(landmark[2]), xy=(landmark[0], landmark[1]), textcoords='offset points')
        self.canvas.draw()