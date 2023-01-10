# -*- coding: utf-8 -*-
"""
@Date     : 2021/4/10 20:45:54
@Author   : milier00
@FileName : AdvancedFitting.py
"""
import sys
sys.path.append("./ui/")
sys.path.append("./model/")
from PyQt5.QtWidgets import QApplication, QWidget
from PyQt5.QtCore import pyqtSignal
from AdvancedFitting_ui import Ui_AdvancedFitting
from Data import *
import functools as ft
import ctypes

class myAdvFitting(Ui_AdvancedFitting, QWidget):
    close_signal = pyqtSignal()
    do_signal = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.init_UI()
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("myappid")

    def init_UI(self):
        self.mode = 0

        self.pushButton_do_advF.clicked.connect(self.do_signal)
        self.pushButton_exit_advF.clicked.connect(self.close)

        self.groupBox_buildin_advF.toggled['bool'].connect(ft.partial(self.edit_mode, 0))
        self.groupBox_user_advF.toggled['bool'].connect(ft.partial(self.edit_mode, 1))

        self.comboBox_advF.currentIndexChanged['int'].connect(self.edit_range)

    def edit_mode(self, index, status):
        if status:
            self.mode = index
            if index == 0:
                self.groupBox_user_advF.setChecked(False)
            elif index == 1:
                self.groupBox_buildin_advF.setChecked(False)

    def edit_range(self, index):
        if index == 0 or index == 1:  # Gaussian(0) or Lorentzian(1)
            self.spinBox_peaknum_advF.setMaximum(5)
        elif index == 2 or index == 3:    # Moffat(2) or BreitWigner(3)
            self.spinBox_peaknum_advF.setMaximum(1)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = myAdvFitting()
    window.show()
    sys.exit(app.exec_())