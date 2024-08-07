# -*- coding: utf-8 -*-
"""
@Date     : 2021/4/8 16:32:36
@Author   : milier00
@FileName : AdvancedAlgebra.py
"""
import sys
sys.path.append("./ui/")
sys.path.append("./model/")
from PyQt5.QtWidgets import QApplication, QWidget
from PyQt5.QtCore import pyqtSignal
from AdvancedAlgebra_ui import Ui_AdvancedAlgebra
from Data import *
import ctypes

class myAdvAlgebra(Ui_AdvancedAlgebra, QWidget):
    close_signal = pyqtSignal()
    do_signal = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.init_UI()
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("myappid")

    def init_UI(self):
        self.pushButton_do_adv.clicked.connect(self.do_signal)
        self.pushButton_cancel_adv.clicked.connect(self.close)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = myAdvAlgebra()
    window.show()
    sys.exit(app.exec_())