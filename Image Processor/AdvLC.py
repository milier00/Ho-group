# -*- coding: utf-8 -*-
"""
@Date     : 2021/5/29 20:59:30
@Author   : milier00
@FileName : AdvLC.py
"""
import sys
sys.path.append("../ui/")
sys.path.append("../data/")
sys.path.append("../Matlab/")
sys.path.append("../model/")
from PyQt5.QtWidgets import QApplication, QWidget
from PyQt5.QtCore import pyqtSignal
from AdvancedLinecut_ui import Ui_AdvancedLinecut
from Data import *
import functools as ft
import ctypes

class myAdvLinecut(Ui_AdvancedLinecut, QWidget):
    close_signal = pyqtSignal()
    do_signal = pyqtSignal()
    export_signal = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.init_UI()
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("myappid")

    def init_UI(self):
        self.mode = 0   # 0: energy, 1: angle

        self.pushButton_do_energy.clicked.connect(self.do_signal)
        self.pushButton_do_angle.clicked.connect(self.do_signal)
        self.pushButton_export_energy.clicked.connect(self.export_signal)
        self.pushButton_export_angle.clicked.connect(self.export_signal)

        self.groupBox_energy.toggled.connect(ft.partial(self.mode_changed, 0))
        self.groupBox_angle.toggled.connect(ft.partial(self.mode_changed, 1))

    def mode_changed(self, index, status):
        if status:
            self.mode = index
            if index == 0:
                self.groupBox_angle.setChecked(False)
            elif index == 1:
                self.groupBox_energy.setChecked(False)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = myAdvLinecut()
    window.show()
    sys.exit(app.exec_())