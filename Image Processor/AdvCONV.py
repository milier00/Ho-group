# -*- coding: utf-8 -*-
"""
@Date     : 2021/5/31 10:48:13
@Author   : milier00
@FileName : AdvCONV.py
"""
import sys
sys.path.append("../ui/")
sys.path.append("../data/")
sys.path.append("../Matlab/")
sys.path.append("../model/")
from PyQt5.QtWidgets import QApplication, QWidget
from PyQt5.QtCore import pyqtSignal
from AdvancedConv_ui import Ui_AdvancedConv
from Data import *
import numpy as np
import functools as ft
import ctypes

class myAdvConv(Ui_AdvancedConv, QWidget):
    close_signal = pyqtSignal(np.ndarray)

    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.init_UI()
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("myappid")

    def init_UI(self):
        self.mode = 0   # 0: 3*3 kernel, 1: 5*5 kernel
        self.kernel3 = np.zeros((3, 3))
        self.kernel5 = np.zeros((5, 5))

        self.groupBox_33.toggled.connect(ft.partial(self.mode_changed, 0))
        self.groupBox_55.toggled.connect(ft.partial(self.mode_changed, 1))

        self.spinBox_00_33.editingFinished.connect(lambda: self.update_kernel(0))
        self.spinBox_01_33.editingFinished.connect(lambda: self.update_kernel(0))
        self.spinBox_02_33.editingFinished.connect(lambda: self.update_kernel(0))
        self.spinBox_10_33.editingFinished.connect(lambda: self.update_kernel(0))
        self.spinBox_11_33.editingFinished.connect(lambda: self.update_kernel(0))
        self.spinBox_12_33.editingFinished.connect(lambda: self.update_kernel(0))
        self.spinBox_20_33.editingFinished.connect(lambda: self.update_kernel(0))
        self.spinBox_21_33.editingFinished.connect(lambda: self.update_kernel(0))
        self.spinBox_22_33.editingFinished.connect(lambda: self.update_kernel(0))

        self.spinBox_00_55.editingFinished.connect(lambda: self.update_kernel(1))
        self.spinBox_01_55.editingFinished.connect(lambda: self.update_kernel(1))
        self.spinBox_02_55.editingFinished.connect(lambda: self.update_kernel(1))
        self.spinBox_03_55.editingFinished.connect(lambda: self.update_kernel(1))
        self.spinBox_04_55.editingFinished.connect(lambda: self.update_kernel(1))
        self.spinBox_10_55.editingFinished.connect(lambda: self.update_kernel(1))
        self.spinBox_11_55.editingFinished.connect(lambda: self.update_kernel(1))
        self.spinBox_12_55.editingFinished.connect(lambda: self.update_kernel(1))
        self.spinBox_13_55.editingFinished.connect(lambda: self.update_kernel(1))
        self.spinBox_14_55.editingFinished.connect(lambda: self.update_kernel(1))
        self.spinBox_20_55.editingFinished.connect(lambda: self.update_kernel(1))
        self.spinBox_21_55.editingFinished.connect(lambda: self.update_kernel(1))
        self.spinBox_22_55.editingFinished.connect(lambda: self.update_kernel(1))
        self.spinBox_23_55.editingFinished.connect(lambda: self.update_kernel(1))
        self.spinBox_24_55.editingFinished.connect(lambda: self.update_kernel(1))
        self.spinBox_30_55.editingFinished.connect(lambda: self.update_kernel(1))
        self.spinBox_31_55.editingFinished.connect(lambda: self.update_kernel(1))
        self.spinBox_32_55.editingFinished.connect(lambda: self.update_kernel(1))
        self.spinBox_33_55.editingFinished.connect(lambda: self.update_kernel(1))
        self.spinBox_34_55.editingFinished.connect(lambda: self.update_kernel(1))
        self.spinBox_40_55.editingFinished.connect(lambda: self.update_kernel(1))
        self.spinBox_41_55.editingFinished.connect(lambda: self.update_kernel(1))
        self.spinBox_42_55.editingFinished.connect(lambda: self.update_kernel(1))
        self.spinBox_43_55.editingFinished.connect(lambda: self.update_kernel(1))
        self.spinBox_44_55.editingFinished.connect(lambda: self.update_kernel(1))



    def mode_changed(self, index, status):
        if status:
            self.mode = index
            if index == 0:
                self.groupBox_55.setChecked(False)
            elif index == 1:
                self.groupBox_33.setChecked(False)

    def update_kernel(self, index):
        if index == 0:
            self.kernel3[0, 0] = self.spinBox_00_33.value()
            self.kernel3[0, 1] = self.spinBox_01_33.value()
            self.kernel3[0, 2] = self.spinBox_02_33.value()

            self.kernel3[1, 0] = self.spinBox_10_33.value()
            self.kernel3[1, 1] = self.spinBox_11_33.value()
            self.kernel3[1, 2] = self.spinBox_12_33.value()

            self.kernel3[2, 0] = self.spinBox_20_33.value()
            self.kernel3[2, 1] = self.spinBox_21_33.value()
            self.kernel3[2, 2] = self.spinBox_22_33.value()
        elif index == 1:
            self.kernel5[0, 0] = self.spinBox_00_55.value()
            self.kernel5[0, 1] = self.spinBox_01_55.value()
            self.kernel5[0, 2] = self.spinBox_02_55.value()
            self.kernel5[0, 3] = self.spinBox_03_55.value()
            self.kernel5[0, 4] = self.spinBox_04_55.value()

            self.kernel5[1, 0] = self.spinBox_10_55.value()
            self.kernel5[1, 1] = self.spinBox_11_55.value()
            self.kernel5[1, 2] = self.spinBox_12_55.value()
            self.kernel5[1, 3] = self.spinBox_13_55.value()
            self.kernel5[1, 4] = self.spinBox_14_55.value()

            self.kernel5[2, 0] = self.spinBox_20_55.value()
            self.kernel5[2, 1] = self.spinBox_21_55.value()
            self.kernel5[2, 2] = self.spinBox_22_55.value()
            self.kernel5[2, 3] = self.spinBox_23_55.value()
            self.kernel5[2, 4] = self.spinBox_24_55.value()

            self.kernel5[3, 0] = self.spinBox_30_55.value()
            self.kernel5[3, 1] = self.spinBox_31_55.value()
            self.kernel5[3, 2] = self.spinBox_32_55.value()
            self.kernel5[3, 3] = self.spinBox_33_55.value()
            self.kernel5[3, 4] = self.spinBox_34_55.value()

            self.kernel5[4, 0] = self.spinBox_40_55.value()
            self.kernel5[4, 1] = self.spinBox_41_55.value()
            self.kernel5[4, 2] = self.spinBox_42_55.value()
            self.kernel5[4, 3] = self.spinBox_43_55.value()
            self.kernel5[4, 4] = self.spinBox_44_55.value()

    # Emit close signal
    def closeEvent(self, event):
        if self.mode == 0:
            self.close_signal.emit(self.kernel3)
        elif self.mode == 1:
            self.close_signal.emit(self.kernel5)
        event.accept()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = myAdvConv()
    window.show()
    sys.exit(app.exec_())