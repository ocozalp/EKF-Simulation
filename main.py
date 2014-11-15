import sys

import PyQt4.QtGui as gui

from ui.main_window import MainWindow


def main():
    app = gui.QApplication(sys.argv)
    mw = MainWindow()
    mw.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()