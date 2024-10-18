import sys

import PyQt5.QtGui as gui
import PyQt5.QtWidgets as widgets
from PyQt5.QtCore import Qt
import platform

from ui.main_window import MainWindow
import os


if platform.system() == 'Darwin':  # macOS-specific setup
    os.environ['QT_MAC_WANTS_LAYER'] = '1'
    widgets.QApplication.setAttribute(Qt.AA_MacDontSwapCtrlAndMeta)


def main():
    app = widgets.QApplication(sys.argv)
    mw = MainWindow()

    mw.show()
    app.exec()


if __name__ == '__main__':
    main()