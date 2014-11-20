from PyQt4 import QtGui as gui
from PyQt4 import QtCore as core


class NamedTextArea(gui.QWidget):
    def __init__(self, parent=None):
        super(gui.QWidget, self).__init__(parent=parent)
        
    def init_gui(self, text, x, y, label_length=150, text_length=250):
        label = gui.QLabel(self)
        label.setText(text)
        label.setGeometry(0, 5, label_length, 30)
        
        self.text_area = gui.QLineEdit(self)
        self.text_area.setGeometry(label_length, 5, text_length, 30)
        
        self.setGeometry(x, y, label_length + text_length, 40)
        
    def set_text(self, text):
        self.text_area.setText(text)
        
    def get_text(self):
        return str(self.text_area.text())


class NamedSlider(gui.QWidget):
    def __init__(self, parent, resolution):
        super(gui.QWidget, self).__init__(parent=parent)
        self.resolution = resolution

    def init_gui(self, text, x, y, label_length=30, slider_length=150, text_length=30):
        label = gui.QLabel(self)
        label.setText(text)
        label.setGeometry(0, 5, label_length, 30)

        self.slider = gui.QSlider(self)
        self.slider.setOrientation(core.Qt.Horizontal)
        self.slider.setMinimum(-50)
        self.slider.setMaximum(50)
        self.slider.setTickInterval(1)
        self.slider.setGeometry(label_length, 5, slider_length, 30)

        self.text_value = gui.QLineEdit(self)
        self.text_value.setText('0.0')
        self.text_value.setGeometry(label_length + slider_length, 5, text_length, 30)
        self.text_value.setReadOnly(True)

        self.setGeometry(x, y, label_length + slider_length + text_length + 40, 40)
        self.slider.valueChanged.connect(SliderChangeEvent(self.text_value, self.resolution))

    def set_value(self, value):
        self.slider.setValue(value)

    def get_value(self):
        return float(self.slider.value()) / self.resolution


class SliderChangeEvent:
    def __init__(self, text_item, resolution):
        self.text_item = text_item
        self.resolution = resolution

    def __call__(self, value):
        text_to_show = str(float(value) / float(self.resolution))
        self.text_item.setText(text_to_show)