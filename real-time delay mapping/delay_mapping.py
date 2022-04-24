# -*- coding: utf-8 -*-
"""
@Date     : 2022/04/23 15:06:52
@Author   : milier00
@FileName : delay_mapping.py
"""
import numpy as np
from pyqtgraph.Qt import QtGui
import pyqtgraph as pg
from PyQt5.QtWidgets import QApplication, QMainWindow, QRadioButton, QButtonGroup
import ctypes
import sys
import copy

class myDelayMapping(QMainWindow):
    def __init__(self):
        super().__init__()
        self.init_UI()
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("myappid")

    def init_UI(self):
        ## Create window with two ImageView widgets
        self.resize(800, 800)
        self.setWindowTitle('Delay Mapping: 6 passes 11*11 pts')
        cw = QtGui.QWidget()
        self.setCentralWidget(cw)
        l = QtGui.QGridLayout()
        cw.setLayout(l)

        self.imv1 = pg.ImageView()
        self.imv2 = pg.ImageView()

        self.radio1 = QRadioButton('mapping1')
        self.radio2 = QRadioButton('mapping2')
        self.radio3 = QRadioButton('mapping3')

        self.radio_group = QButtonGroup()
        self.radio_group.addButton(self.radio1, 1)
        self.radio_group.addButton(self.radio2, 2)
        self.radio_group.addButton(self.radio3, 3)
        self.radio_group.buttonToggled[int, bool].connect(self.file_changed)

        l.addWidget(self.imv1, 0, 0, 1, 3)
        l.addWidget(self.imv2, 1, 0, 1, 3)
        l.addWidget(self.radio1, 2, 0, 1, 1)
        l.addWidget(self.radio2, 2, 1, 1, 1)
        l.addWidget(self.radio3, 2, 2, 1, 1)
        self.roi = pg.LineSegmentROI([[0, 0], [10, 10]], pen='r')
        self.imv1.addItem(self.roi)

    def file_changed(self, index, status):
        if status:
            if index == 3:
                file = './mapping3.txt'
            elif index == 2:
                file = './mapping2.txt'
            elif index == 1:
                file = './mapping1.txt'

            mapping = np.loadtxt(file)
            z = np.zeros((401, 11, 11))
            for i in range(1, mapping.shape[0]):
                for j in range(z.shape[2]):
                    z[i, :, j] = mapping[i, (j % 11) * 11 + 1: (j % 11) * 11 + 12]
            data = z

            self.roi.sigRegionChanged.connect(lambda: self.update(data))
            self.imv1.setImage(data)
            self.update(data)

    def update(self, data):
        d2 = self.roi.getArrayRegion(data, self.imv1.imageItem, axes=(1, 2))

        result = copy.deepcopy(np.fliplr(d2))
        row, col = result.shape[0], result.shape[1]

        '''to make the line cut looks like our real linecut data / delay imaging '''
        for i in range(col - 1, -1, -1):
            for j in range(25):
                result = np.insert(result, i, result[:, i], axis=1)

        '''to make the line cut looks like our real linecut data / delay imaging '''
        # for i in range(row - 1, -1, -1):
        #     for j in range(2):
        #         result = np.insert(result, i, result[i, :], axis=0)

        ''' save line cut '''
        # np.savetxt('./test data/mapping3/result3_rdiag.txt', result)

        self.imv2.setImage(result)



if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = myDelayMapping()
    window.show()
    sys.exit(app.exec_())