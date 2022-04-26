# -*- coding: utf-8 -*-
"""
@Date     : 2022/4/25 15:24:57
@Author   : milier00
@FileName : delay_imaging.py
"""
import numpy as np
from pyqtgraph import QtWidgets
import pyqtgraph as pg
from PyQt5.QtWidgets import QApplication, QMainWindow, QRadioButton, QButtonGroup, QLabel, QWidget, QGridLayout
import ctypes
import sys
import os
import copy

class myDelayImaging(QMainWindow):
    def __init__(self):
        super().__init__()
        self.init_UI()
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("myappid")

    def init_UI(self):
        self.raw_data = []
        self.axes = (1,2)

        ## Create window with two ImageView widgets
        self.resize(800, 800)
        self.setWindowTitle('Delay Imaging: ')
        cw = QWidget()
        self.setCentralWidget(cw)
        l = QGridLayout()
        cw.setLayout(l)

        self.imv1 = pg.ImageView()
        self.imv2 = pg.ImageView()
        self.label = QLabel('Dimension options:')
        self.radio_t = QRadioButton('t/f+(x,y)')
        self.radio_x = QRadioButton('x+(y,t/f)')
        self.radio_y = QRadioButton('y+(x,t/f)')
        self.radio_t.setChecked(True)

        self.label_ = QLabel('Data options:')
        self.radio1 = QRadioButton('(t,x,y)')
        self.radio2 = QRadioButton('(f,x,y)')
        self.radio3 = QRadioButton('(amp,x,y)')
        self.radio3.setEnabled(False)

        self.group = QButtonGroup()
        self.group.addButton(self.radio_t, 0)
        self.group.addButton(self.radio_x, 1)
        self.group.addButton(self.radio_y, 2)
        self.group.buttonToggled[int, bool].connect(self.axis_changed)

        self.radio_group = QButtonGroup()
        self.radio_group.addButton(self.radio1, 1)
        self.radio_group.addButton(self.radio2, 2)
        self.radio_group.addButton(self.radio3, 3)
        self.radio_group.buttonToggled[int, bool].connect(self.file_changed)

        l.addWidget(self.imv1, 0, 0, 1, 4)
        l.addWidget(self.imv2, 1, 0, 1, 4)
        l.addWidget(self.label_, 2, 0, 1, 1)
        l.addWidget(self.radio1, 2, 1, 1, 1)
        l.addWidget(self.radio2, 2, 2, 1, 1)
        l.addWidget(self.radio3, 2, 3, 1, 1)
        l.addWidget(self.label, 3, 0, 1, 1)
        l.addWidget(self.radio_t, 3, 1, 1, 1)
        l.addWidget(self.radio_x, 3, 2, 1, 1)
        l.addWidget(self.radio_y, 3, 3, 1, 1)

        self.roi = pg.LineSegmentROI([[0, 0], [50, 50]], pen='r')
        self.imv1.addItem(self.roi)

        # Isocurve drawing
        self.iso = pg.IsocurveItem(level=0.8, pen='g')
        self.iso.setParentItem(self.imv1.imageItem)
        self.iso.setZValue(5)

        # Draggable line for setting isocurve level
        self.isoLine = pg.InfiniteLine(angle=0, movable=True, pen='g')
        self.isoLine.sigDragged.connect(self.updateIsocurve)
        self.imv1.ui.histogram.vb.addItem(self.isoLine)
        self.imv1.ui.histogram.vb.setMouseEnabled(y=False)  # makes user interaction a little easier
        self.isoLine.setValue(0.8)
        self.isoLine.setZValue(1000)  # bring iso line above contrast controls

    def axis_changed(self, index, status):
        if status:
            if index == 0:
                self.imv1.setImage(self.data, axes={'t': 0, 'x': 1, 'y': 2})
                self.axes = (1, 2)
                self.update(self.data, self.axes)
            elif index == 1:
                self.imv1.setImage(self.data, axes={'t':1, 'x':2, 'y':0})
                self.axes = (2, 0)
                self.update(self.data, self.axes)
            elif index == 2:
                self.imv1.setImage(self.data, axes={'t':2, 'x': 1, 'y': 0})
                self.axes = (1, 0)
                self.update(self.data, self.axes)

    def update(self, data, axes):
        d2 = self.roi.getArrayRegion(data, self.imv1.imageItem, axes=axes)

        result = copy.deepcopy(np.fliplr(d2))
        row, col = result.shape[0], result.shape[1]

        '''to make the line cut looks like our real linecut data / delay imaging '''
        if self.radio1.isChecked():
            for i in range(col - 1, -1, -1):
                for j in range(2):
                    result = np.insert(result, i, result[:, i], axis=1)

        '''to make the line cut looks like our real linecut data / delay imaging '''
        if self.radio2.isChecked():
            for i in range(row - 1, -1, -1):
                for j in range(2):
                    result = np.insert(result, i, result[i, :], axis=0)

        self.imv2.setImage(result)
        self.setWindowTitle('Delay Imaging: ' + str(d2.shape[1]) + ' pts selected')

    def updateIsocurve(self):
        self.iso.setData(pg.gaussianFilter(self.imv1.imageItem.image, (3, 3)))
        self.iso.setLevel(self.isoLine.value())
        
    def init_data(self, data):
        self.raw_data = data
        self.data = copy.deepcopy(self.raw_data)
        self.roi.sigRegionChanged.connect(lambda: self.update(data, self.axes))
        self.imv1.setImage(data)
        self.update(data, (1, 2))

    def file_changed(self, index, status):
        if status:
            if index == 1:
                ''' delay imaging '''
                dir_path = './raw/'
                # get a file list for imgings
                file_list = []
                for root, dirs, files in os.walk(dir_path, topdown=False):
                    for file in files:
                        if file[:7] == "puzzle_" and file[-4:] == '.txt':
                            data_path = os.path.join(root, file)
                            file_list.append(data_path)
            elif index == 2:
                ''' fft - (f,x,y) '''
                dir_path = './fft/'
                # get a file list for imgings
                file_list = []
                for root, dirs, files in os.walk(dir_path, topdown=False):
                    for file in files:
                        if file[:5] == 'freq-' and file[-4:] == '.txt':
                            data_path = os.path.join(root, file)
                            file_list.append(data_path)
            # elif index == 3:
            #     ''' fft - (amp,x,y) '''
            #     dir_path = './test data/delay scan imaging 2/fft/'
            #     # get a file list for imgings
            #     file_list = []
            #     for root, dirs, files in os.walk(dir_path, topdown=False):
            #         for file in files:
            #             if file[:4] == 'amp-' and file[-4:] == '.txt':
            #                 data_path = os.path.join(root, file)
            #                 file_list.append(data_path)
            #     print('file number:', len(file_list))

            # get a 3D array, also save each image as png
            img_list = []
            for file in file_list:
                img = np.loadtxt(file)
                img = np.transpose(img)
                if file_list.index(file) == 0:
                    img_list.append(img)
                    img_list = np.array(img_list)
                else:
                    img_list = np.vstack((img_list, img.reshape(1, img.shape[0], img.shape[1])))

            data = np.array(img_list)
            self.init_data(data)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = myDelayImaging()
    window.show()
    sys.exit(app.exec_())