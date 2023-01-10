# -*- coding: utf-8 -*-
"""
@Date     : 1/7/2022 2:03:21
@Author   : milier00
@FileName : MapWindow.py
"""
import sys
sys.path.append("./ui/")
sys.path.append("./model/")
from PyQt5.QtWidgets import QLabel, QApplication
from PyQt5.QtCore import Qt, pyqtSignal
import pyqtgraph as pg
from qframelesswindow import FramelessWindow, TitleBar
from images import myImages
from MapWin_ui import Ui_MapWin
from Data import *
import ctypes
import os

class CustomTitleBar(TitleBar):
    """ Custom title bar """

    def __init__(self, parent):
        super().__init__(parent)
        self.label = QLabel('', self)   # Advanced plane fit
        self.label.setStyleSheet("QLabel{font: 13px 'Segoe UI'; margin: 10px; "
                                 "color: white; background-color: transparent}")
        self.label.adjustSize()
        self.label.setScaledContents(True)

        self._style = {
            "normal": {
                "color": (240, 240, 240, 200),
                'background': (40, 40, 40, 200)
            },
            "hover": {
                "color": (255, 255, 255),
                'background': (0, 100, 182)
            },
            "pressed": {
                "color": (255, 255, 255),
                'background': (54, 57, 65)
            },
        }

        self.minBtn.updateStyle(self._style)
        self.maxBtn.updateStyle(self._style)
        self.closeBtn.updateStyle(self._style)

class myMapWin(FramelessWindow, Ui_MapWin):
    # Common signal
    close_signal = pyqtSignal(object)

    def __init__(self):
        super().__init__()
        # pg.setConfigOption('background', (240, 240, 240, 0))
        # pg.setConfigOption('foreground', 'k')
        self.setupUi(self)
        self.init_UI()
        self.setTitleBar(CustomTitleBar(self))
        self.titleBar.raise_()
        self.setStyleSheet("background-color: black; color: black;")
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("myappid")

    def init_UI(self):

        # graphicsView
        self.graphicsView.ci.layout.setContentsMargins(0, 0, 0, 0)     # eliminate the border
        self.graphicsView.ci.layout.setSpacing(0)                      # eliminate the border
        self.view_box = self.graphicsView.addViewBox()
        self.view_box.setAspectLocked(True)
        self.view_box.setCursor(Qt.CrossCursor)
        self.view_box.setMouseMode(self.view_box.PanMode)

        self.myimg = myImages()
        self.imgList = []

    def init_data(self, data_list):
        self.imgList = []
        # (x offset, y offset, step num, step size, xy-gain)
        for data in data_list:
            try:
                img = self.myimg.prepare_data(self.myimg.partial_renormalize(data.data[0]))
            except:
                continue
            # print('-----------------')
            # print(data.name, img.shape)
            # 0 -> gain 10.0, 1 -> gain 1.0, 3 -> gain 0.1
            xygain = 10 * (data.grid.lastgain[0] == 0) + 1 * (data.grid.lastgain[0] == 1) + 0.1 * (
                    data.grid.lastgain[0] == 3)
            # (x offset, y offset, step num, step size, xy-gain)
            xoff, yoff, stepnum, stepsize = (data.grid.lastdac[1], data.grid.lastdac[14],
                             data.grid.step_num, data.grid.step_size)
            # step_num * step_size * xy-gain
            size = stepnum * stepsize * xygain//10
            # print(stepnum, stepsize, xygain, size)
            x_start = xoff - (size//2-1)
            x_end = x_start + size
            y_start = yoff - (size//2-1)
            y_end = y_start + size
            # print(x_start, y_start, x_end, y_end)
            # print('size:', x_end-x_start, y_end-y_start)

            # resized = scipy.ndimage.zoom(img, size/img.shape[0], order=0)
            self.imgList.append(pg.ImageItem(img, rect=(x_start,y_start,size,size)))
            self.view_box.addItem(self.imgList[-1])

        self.view_box.autoRange()
        print(len(self.imgList))

if __name__ == "__main__":
    # create the application and the main window
    app = QApplication(sys.argv)
    window = myMapWin()
    dir_path = 'D:/Code/2022oct/'
    file_list = []
    for root, dirs, files in os.walk(dir_path, topdown=False):
        for file in files:
            if file[-5:] == '.nstm':
                data_path = os.path.join(root, file)
                file_list.append(data_path)
    data_list = []
    for file in file_list[:50]:
        data_list.append(MappingData(file))
    window.init_data(data_list)
    window.show()
    sys.exit(app.exec_())

