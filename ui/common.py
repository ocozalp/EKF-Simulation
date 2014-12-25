import PyQt4.QtGui as gui


robot_colors = ['b', 'y', 'r']

def show_message_box(parent_widget, title, message):
    message_box = gui.QMessageBox()
    message_box.about(parent_widget, title, message)


def show_error_box(parent_widget, message):
    show_message_box(parent_widget, 'Hata', message)

