# -*- coding: utf-8 -*-
"""
@Date     : 2021/4/10 16:15:39
@Author   : milier00
@FileName : SimCurve.py
"""
import sys
sys.path.append("./ui/")
sys.path.append("./model/")
from PyQt5.QtWidgets import QApplication, QWidget
from PyQt5.QtCore import pyqtSignal
from SimCurve_ui import Ui_SimCurve
from Data import *
import ctypes

class mySimCurve(Ui_SimCurve, QWidget):
    close_signal = pyqtSignal()
    do_signal = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.init_UI()
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("myappid")

    def init_UI(self):
        self.pushButton_do_SC.clicked.connect(self.do_signal)
        self.pushButton_exit_SC.clicked.connect(self.close)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = mySimCurve()
    window.show()
    sys.exit(app.exec_())