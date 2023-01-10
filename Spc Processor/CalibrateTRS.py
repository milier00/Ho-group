# -*- coding: utf-8 -*-
"""
@Date     : 12/18/2022 12:55:58
@Author   : milier00
@FileName : CalibrateTRS.py
"""
import sys
sys.path.append("./ui/")
sys.path.append("./model/")
sys.path.append("./Plot2D3D/")
from PyQt5.QtWidgets import QApplication, QWidget, QSizePolicy,QInputDialog, QMessageBox, QAbstractItemView, QGridLayout, \
    QComboBox, QFileDialog, QShortcut, QListWidget, QMenu, QAction
from PyQt5.QtCore import pyqtSignal, Qt
from PyQt5.QtGui import QKeySequence, QColor
from pyqtgraph.Qt import QtGui, QtCore
from images import myImages
from SpcWin_ui import Ui_SpcWin
from CalibrateTRS_ui import Ui_CalibrateTRS
from Data import *
from func1D import myFunc
import numpy as np
import functools as ft
import pyqtgraph as pg
from sympy import *
import math
import copy
import ctypes
import os
from collections import defaultdict
import colorcet as cc
import random
class CustomViewBox(pg.ViewBox):
    def __init__(self, *args, **kwds):
        kwds['enableMenu'] = True
        pg.ViewBox.__init__(self, *args, **kwds)
        self.setMouseMode(self.RectMode)

    ## reimplement right-click to pop out window
    ## reimplement middle-click to pop out window
    def mouseClickEvent(self, ev):
        if ev.button() == QtCore.Qt.MouseButton.MiddleButton:
            self.autoRange()
        if ev.button() == QtCore.Qt.MouseButton.RightButton and self.menuEnabled():
            ev.accept()
            self.raiseContextMenu(ev)

    ## reimplement mouseDragEvent to disable continuous axis zoom
    def mouseDragEvent(self, ev, axis=None):
        if axis is not None and ev.button() == QtCore.Qt.MouseButton.RightButton:
            ev.ignore()
        else:
            pg.ViewBox.mouseDragEvent(self, ev, axis=axis)


class myCalTRSWindow(QWidget, Ui_CalibrateTRS):
    # Common signal
    close_signal = pyqtSignal()
    send_signal = pyqtSignal(list, list)
    # Consts
    SENSITIVITIES = [
        np.nan, 2.0e-9, 5.0e-9, 10.0e-9, 20.0e-9, 50.0e-9, 100.0e-9,
        200.0e-9, 500.0e-9, 1.0e-6, 2.0e-6, 5.0e-6, 10.0e-6,
        20.0e-6, 50.0e-6, 100.0e-6, 200.0e-6, 500.0e-6, 1.0e-3,
        2.0e-3, 5.0e-3, 10.0e-3, 20.0e-3, 50.0e-3, 100.0e-3,
        200.0e-3, 500.0e-3, 1.0
    ]

    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.init_UI()
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("myappid")

    def init_UI(self):
        self.sen1 = 1
        self.sen2 = 1
        self.offset1 = 0
        self.offset2 = 0
        self.angle1 = 0
        self.angle2 = 0
        self.result_names = []
        self.img = myImages()
        self.func1D = myFunc()


        """ Graphsic """
        # label | display scanner coordinates
        self.label = pg.LabelItem(justify='right')
        self.graphicsView.addItem(self.label, row=0, col=0)
        self.label.hide()

        # graphicsView |
        self.viewBox = CustomViewBox(enableMenu=False)

        # plotItem |
        self.plot = self.graphicsView.addPlot(viewBox=self.viewBox, row=1, col=0)
        self.proxy = pg.SignalProxy(self.plot.scene().sigMouseMoved, rateLimit=60, slot=self.mouseMoved)

        # legend |
        self.legend = self.plot.addLegend(labelTextSize='10pt')
        self.legend.setParentItem(self.plot)
        # self.legend.hide()

        # axis |
        self.x_axis = self.plot.axes['bottom']['item']
        self.y_axis = self.plot.axes['left']['item']

        # ROI | data scanner
        self.vLine = pg.InfiniteLine(angle=90, movable=False)
        self.hLine = pg.InfiniteLine(angle=0, movable=False)
        self.plot.addItem(self.vLine, ignoreBounds=True)
        self.plot.addItem(self.hLine, ignoreBounds=True)
        self.vLine.hide()
        self.hLine.hide()

        # colorBar |
        self.colorBar = pg.HistogramLUTItem(levelMode='mono')
        # self.colorBar.setImageItem(self.img_display)
        self.graphicsView.addItem(self.colorBar, 1, 1, 1, 1)
        self.colorBar.vb.setFixedWidth(1)  # zero gives error
        self.colorBar.hide()

        """ Controls """
        # pushButton |
        self.pushButton_xScale.clicked.connect(lambda: self.scale(0))
        self.pushButton_yScale.clicked.connect(lambda: self.scale(1))
        self.pushButton_Scanner.clicked.connect(self.show_scanner)
        self.pushButton_send.clicked.connect(self.send_result)
        # comboBox |
        self.comboBox_SenCH1.currentIndexChanged.connect(lambda: self.pars_changed(0))
        self.comboBox_SenCH2.currentIndexChanged.connect(lambda: self.pars_changed(1))
        # spinBox |
        self.spinBox_offsetCH1.editingFinished.connect(lambda: self.pars_changed(0))
        self.spinBox_offsetCH2.editingFinished.connect(lambda: self.pars_changed(1))
        self.spinBox_angle1.editingFinished.connect(lambda: self.pars_changed(0))
        self.spinBox_angle2.editingFinished.connect(lambda: self.pars_changed(1))
        self.spinBox_angle1.editingFinished.connect(self.spin2slider)
        self.spinBox_angle2.editingFinished.connect(self.spin2slider)
        self.spinBox_SenCH1 = pg.SpinBox(value=1, suffix='V', siPrefix=True)
        self.spinBox_SenCH2 = pg.SpinBox(value=1, suffix='V', siPrefix=True)
        self.groupBox_CH1.layout().addWidget(self.spinBox_SenCH1, 1, 2, 1, 1)
        self.groupBox_CH2.layout().addWidget(self.spinBox_SenCH2, 1, 2, 1, 1)
        self.spinBox_SenCH1.valueChanged.connect(lambda: self.pars_changed(0))
        self.spinBox_SenCH2.valueChanged.connect(lambda: self.pars_changed(1))
        # slider |
        self.slider_angle1.valueChanged.connect(self.slider2spin)
        self.slider_angle2.valueChanged.connect(self.slider2spin)
        self.slider_angle1.valueChanged.connect(lambda: self.pars_changed(0))
        self.slider_angle2.valueChanged.connect(lambda: self.pars_changed(1))

    def spin2slider(self):
        self.slider_angle1.setValue(int(self.spinBox_angle1.value() * 100))
        self.slider_angle2.setValue(int(self.spinBox_angle2.value() * 100))

    def slider2spin(self):
        self.spinBox_angle1.setValue(self.slider_angle1.value() / 100)
        self.spinBox_angle2.setValue(self.slider_angle2.value() / 100)

    # Graphics | scale by X/Y axis
    def scale(self, index):
        if index == 0:  # scale x
            self.plot.vb.enableAutoRange(axis='x', enable=True)
            self.plot.vb.updateAutoRange()
        elif index == 1:  # sacle y
            self.plot.vb.enableAutoRange(axis='y', enable=True)
            self.plot.vb.updateAutoRange()

    # Graphics | show crosshair data scanner
    def show_scanner(self):
        if self.pushButton_Scanner.isChecked():
            self.proxy = pg.SignalProxy(self.plot.scene().sigMouseMoved, rateLimit=60, slot=self.mouseMoved)
            self.plot.addItem(self.vLine, ignoreBounds=True)
            self.plot.addItem(self.hLine, ignoreBounds=True)
            self.vLine.show()
            self.hLine.show()
            self.label.show()
        else:
            self.plot.removeItem(self.vLine)
            self.plot.removeItem(self.hLine)
            self.label.hide()

    def mouseMoved(self, evt):
        pos = evt[0]  ## using signal proxy turns original arguments into a tuple
        if self.plot.sceneBoundingRect().contains(pos):
            mousePoint = self.plot.vb.mapSceneToView(pos)
            data_x = [] * len(self.plot.listDataItems())
            data_y = [] * len(self.plot.listDataItems())
            color = [] * len(self.plot.listDataItems())
            for curve in self.plot.listDataItems():
                near_x = min(curve.xData, key=lambda x: abs(x - mousePoint.x()))
                index = list(curve.xData).index(near_x)
                data_x += [near_x]
                data_y += [curve.yData[index]]
                color += [self.img.RGB_to_Hex(curve.curve.opts['pen'].brush().color().getRgb())]

            text = ''
            num = 0
            for i in range(len(data_x)):
                num += 1
                text += "<span style='font-size: 8pt'><span style='color: " + color[
                    i] + "'>(%.3e, %.3e)   </span>" % (data_x[i], data_y[i])
                if num % 5 == 0:
                    text += "<br />"
            self.label.setText(text)
            self.vLine.setPos(mousePoint.x())
            self.hLine.setPos(mousePoint.y())

    def fake(self, index):
        dir_path = 'D:/exp/'
        # get a file list for raw data
        file_list = []
        for root, dirs, files in os.walk(dir_path, topdown=False):
            for file in files:
                if file[:6] == "100422" and file[-4:] == '.txt':
                    data_path = os.path.join(root, file)
                    file_list.append(data_path)
        print('file number:', len(file_list))

        dir_path = 'D:/exp/'
        index = file_list.index(dir_path + "10042249.txt")
        file_name = os.path.split(file_list[index])[1][:-4]

        ivf = np.loadtxt(file_list[index], skiprows=1)
        didvf = np.loadtxt(file_list[index + 1], skiprows=1)
        ietsf = np.loadtxt(file_list[index + 2], skiprows=1)
        ivb = np.loadtxt(file_list[index + 3], skiprows=1)
        didvb = np.loadtxt(file_list[index + 4], skiprows=1)
        ietsb = np.loadtxt(file_list[index + 5], skiprows=1)

        avgiv = (ivf[:, 1] + ivb[:, 1]) / 2
        avgdidv = (didvf[:, 1] + didvb[:, 1]) / 2
        avgiets = (ietsf[:, 1] + ietsb[:, 1]) / 2

        iv = np.hstack((ivf, ivb[:, 1][:, np.newaxis]))
        iv = np.hstack((iv, avgiv[:, np.newaxis]))
        didv = np.hstack((didvf, didvb[:, 1][:, np.newaxis]))
        didv = np.hstack((didv, avgdidv[:, np.newaxis]))
        iets = np.hstack((ietsf, ietsb[:, 1][:, np.newaxis]))
        iets = np.hstack((iets, avgiets[:, np.newaxis]))

        bias = ivf[:, 0] * 1000 + 2.5  # divider off
        # bias = ivf[:,0]*100+1.2
        # # ####################################################
        index = file_list.index(dir_path + "10042255.txt")
        file_name2 = os.path.split(file_list[index])[1][:-4]

        ivf = np.loadtxt(file_list[index], skiprows=1)
        didvf = np.loadtxt(file_list[index + 1], skiprows=1)
        ietsf = np.loadtxt(file_list[index + 2], skiprows=1)
        ivb = np.loadtxt(file_list[index + 3], skiprows=1)
        didvb = np.loadtxt(file_list[index + 4], skiprows=1)
        ietsb = np.loadtxt(file_list[index + 5], skiprows=1)

        avgiv = (ivf[:, 1] + ivb[:, 1]) / 2
        avgdidv = (didvf[:, 1] + didvb[:, 1]) / 2
        avgiets = (ietsf[:, 1] + ietsb[:, 1]) / 2

        iv2 = np.hstack((ivf, ivb[:, 1][:, np.newaxis]))
        iv2 = np.hstack((iv2, avgiv[:, np.newaxis]))
        didv2 = np.hstack((didvf, didvb[:, 1][:, np.newaxis]))
        didv2 = np.hstack((didv2, avgdidv[:, np.newaxis]))
        iets2 = np.hstack((ietsf, ietsb[:, 1][:, np.newaxis]))
        iets2 = np.hstack((iets2, avgiets[:, np.newaxis]))

        ########################################################

        myiv = (iv[:, 3] * 100 + iv2[:, 3] * 100 ) / 200
        mych1 = (didv[:, 3] * 100 + didv2[:, 3] * 100 ) / 200
        mych2 = (iets[:, 3] * 100 + iets2[:, 3] * 100 ) / 200

        myiv = np.vstack((bias, myiv))
        mych1 = np.vstack((bias, mych1))
        mych2 = np.vstack((bias, mych2))
        print(bias.shape, myiv.shape, mych1.shape, mych2.shape)
        return [myiv, mych1, mych2]

    def pars_changed(self, index):

        # CH1 parameters changed
        if index == 0:
            self.sen1 = self.spinBox_SenCH1.value()
            self.offset1  = self.spinBox_offsetCH1.value()
            self.angle1 = self.spinBox_angle1.value()

        # CH2 parameters changed
        elif index == 1:
            self.sen2 = self.spinBox_SenCH2.value()
            self.offset2  = self.spinBox_offsetCH2.value()
            self.angle2 = self.spinBox_angle2.value()

        self.update_graph()

    def init_data(self, data):
        """ uncomment this line in test mode """
        # data = self.fake(0)

        self.data = data
        # data : [(x,ch0), (x,ch1), (x,ch2)]
        # data : [(x,ch0_fwd), (x,ch1_fwd), (x,ch2_fwd), (x,ch0_bwd), (x,ch1_bwd), (x,ch2_bwd)]
        self.xs = []
        self.ys = []
        self.visible_list = []
        for xy in data:
            self.xs.append(xy[0])
            self.ys.append(xy[1])
            self.visible_list.append(True)

        self.update_graph()

    def init_name(self, names):
        self.result_names = names

    def update_graph(self):
        ## clear all items in plotItem
        self.plot.clear()

        ## make a copy of raw data
        self.xx = copy.deepcopy(self.xs)
        self.yy = copy.deepcopy(self.ys)

        ## append calibrated data
        bias = self.data[0][0]

        if len(self.data) == 3:
            ch1 = self.data[1][1]
            cal_ch1 = (ch1 - self.offset1 / 100) * self.sen1
            _, self.rot_cal_ch1 = self.func1D.myrotate(bias, cal_ch1, self.angle1)
            self.xx.append(bias)
            self.yy.append(self.rot_cal_ch1)

            ch2 = self.data[2][1]
            cal_ch2 = (ch2 - self.offset2 / 100) * self.sen2
            _, self.rot_cal_ch2 = self.func1D.myrotate(bias, cal_ch2, self.angle2)
            self.xx.append(bias)
            self.yy.append(self.rot_cal_ch2)

            # Dedicated colors which look "good"
            names = ['IV', 'CH1', 'CH2', 'cal-rot CH1', 'cal-rot CH2']
            colors = ['#fe03cb', '#76bcfd', '#00c720', '#ffa530', '#ff97aa', '#00dfdf']
            colors = cc.glasbey_dark[:6]

        elif len(self.data) == 6:
            ch1_fwd = self.data[1][1]
            cal_ch1_fwd = (ch1_fwd - self.offset1 / 100) * self.sen1
            _, self.rot_cal_ch1_fwd = self.func1D.myrotate(bias, cal_ch1_fwd, self.angle1)
            self.xx.append(bias)
            self.yy.append(self.rot_cal_ch1_fwd)

            ch2_fwd = self.data[2][1]
            cal_ch2_fwd = (ch2_fwd - self.offset2 / 100) * self.sen2
            _, self.rot_cal_ch2_fwd = self.func1D.myrotate(bias, cal_ch2_fwd, self.angle2)
            self.xx.append(bias)
            self.yy.append(self.rot_cal_ch2_fwd)

            ch1_bwd = self.data[4][1]
            cal_ch1_bwd = (ch1_bwd - self.offset1 / 100) * self.sen1
            _, self.rot_cal_ch1_bwd = self.func1D.myrotate(bias, cal_ch1_bwd, self.angle1)
            self.xx.append(bias)
            self.yy.append(self.rot_cal_ch1_bwd)

            ch2_bwd = self.data[5][1]
            cal_ch2_bwd = (ch2_bwd - self.offset2 / 100) * self.sen2
            _, self.rot_cal_ch2_bwd = self.func1D.myrotate(bias, cal_ch2_bwd, self.angle2)
            self.xx.append(bias)
            self.yy.append(self.rot_cal_ch2_bwd)

            # Dedicated colors which look "good"
            names = ['IV_fwd', 'CH1_fwd', 'CH2_fwd', 'IV_bwd', 'CH1_bwd', 'CH2_bwd',
                     'cal-rot CH1_fwd', 'cal-rot CH2_fwd', 'cal-rot CH1_bwd', 'cal-rot CH2_bwd']
            colors = ['#fe03cb', '#76bcfd', '#00c720', '#ffa530', '#ff97aa', '#00dfdf',
                      '#c8c400', '#ff7166', '#00acc7', '#9a4700']
            colors = cc.glasbey_dark[:10]

        ## append visibility for new lines
        if len(self.visible_list) < len(self.xx):
            self.visible_list += [True] * (len(self.xx) - len(self.visible_list))

        ## plot
        for x, y, name, color in zip(self.xx, self.yy, names, colors):
            pen = pg.mkPen(color=color, width=2)
            if name.find('cal') != -1:
                pen.setDashPattern([4, 4, 4, 4])
            # cc.glasbey_light[random.randint(0, 255)]
            self.plot.addItem(pg.PlotDataItem(x, y, pen=pen, name=name))

        ## set visibility for each line
        for (item, _), visible in zip(self.legend.items, self.visible_list):
            item.sigVisibilityChanged.connect(self.visibility_changed)
            item.item.setVisible(visible)
            item.update()

    # ItemSample mouse clicked slot | update visibility variable
    def visibility_changed(self):
        self.visible_list.clear()
        for item, _ in self.legend.items:
            self.visible_list.append(item.item.isVisible())

    def send_result(self):
        bias = self.data[0][0]
        packed_data = []
        if len(self.data) == 3:
            packed_data.append(np.vstack((bias, self.rot_cal_ch1)))
            packed_data.append(np.vstack((bias, self.rot_cal_ch2)))
        elif len(self.data) == 6:
            packed_data.append(np.vstack((bias, self.rot_cal_ch1_fwd)))
            packed_data.append(np.vstack((bias, self.rot_cal_ch2_fwd)))
            packed_data.append(np.vstack((bias, self.rot_cal_ch1_bwd)))
            packed_data.append(np.vstack((bias, self.rot_cal_ch2_bwd)))
        self.send_signal.emit(packed_data, self.result_names)
        self.close()

    def closeEvent(self, a0: QtGui.QCloseEvent) -> None:
        self.result_names.clear()
        self.rot_cal_ch1 = None
        self.rot_cal_ch2 = None
        self.rot_cal_ch1_fwd = None
        self.rot_cal_ch2_fwd = None
        self.rot_cal_ch1_bwd = None
        self.rot_cal_ch2_bwd = None
        self.plot.clear()
        self.visible_list = []
        a0.accept()


if __name__ == "__main__":
    # create the application and the main window
    app = QApplication(sys.argv)
    window = myCalTRSWindow()
    window.init_data([0])
    window.show()
    sys.exit(app.exec_())