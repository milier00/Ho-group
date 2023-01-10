# -*- coding: utf-8 -*-
"""
@Date     : 12/17/2022 18:56:58
@Author   : milier00
@FileName : CalibrateIETS.py
"""
import sys
sys.path.append("./ui/")
sys.path.append("./model/")
sys.path.append("./Plot2D3D/")
from PyQt5.QtWidgets import QApplication, QWidget
from PyQt5.QtCore import pyqtSignal
from pyqtgraph.Qt import QtGui, QtCore
from images import myImages
from CalibrateIETS_ui import Ui_CalibrateIETS
from Data import *
from func1D import myFunc
import numpy as np
import pyqtgraph as pg
import colorcet as cc
import copy
import ctypes
import os





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


class myCalIETSWindow(QWidget, Ui_CalibrateIETS):
    # Common signal
    close_signal = pyqtSignal()
    send_signal = pyqtSignal(list, list)

    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.init_UI()
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("myappid")

    def init_UI(self):
        self.slope_didv = 0
        self.offset_didv = 0
        self.slope_iets = 0
        self.offset_iets = 0
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
        # spinBox |
        self.spinBox_slope_didv.editingFinished.connect(lambda: self.pars_changed(0))
        self.spinBox_offset_didv.editingFinished.connect(lambda: self.pars_changed(0))
        self.spinBox_slope_iets.editingFinished.connect(lambda: self.pars_changed(0))
        self.spinBox_offset_iets.editingFinished.connect(lambda: self.pars_changed(0))
        self.spinBox_slopeMin_didv.editingFinished.connect(lambda: self.set_range(0))
        self.spinBox_slopeMax_didv.editingFinished.connect(lambda: self.set_range(0))
        self.spinBox_offsetMin_didv.editingFinished.connect(lambda: self.set_range(1))
        self.spinBox_offsetMax_didv.editingFinished.connect(lambda: self.set_range(1))
        self.spinBox_slopeMin_IETS.editingFinished.connect(lambda: self.set_range(2))
        self.spinBox_slopeMax_IETS.editingFinished.connect(lambda: self.set_range(2))
        self.spinBox_offsetMin_IETS.editingFinished.connect(lambda: self.set_range(3))
        self.spinBox_offsetMax_IETS.editingFinished.connect(lambda: self.set_range(3))

        # sliderBar |
        self.slider_slope_didv.valueChanged.connect(lambda: self.pars_changed(1))
        self.slider_offset_didv.valueChanged.connect(lambda: self.pars_changed(1))
        self.slider_slope_iets.valueChanged.connect(lambda: self.pars_changed(1))
        self.slider_offset_iets.valueChanged.connect(lambda: self.pars_changed(1))

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

    def fake(self, index=0):
        dir_path = 'C:/Users/DAN/Downloads/exp/'
        # get a file list for raw data
        file_list = []
        for root, dirs, files in os.walk(dir_path, topdown=False):
            for file in files:
                if file[:6] == "081122" and file[-4:] == '.txt':
                    data_path = os.path.join(root, file)
                    file_list.append(data_path)
        print('file number:', len(file_list))

        dir_path = 'C:/Users/DAN/Downloads/exp/'
        index = file_list.index(dir_path + "081122g9.txt")
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
        bias = ivf[:, 0]
        print('bias shape:', bias.shape, 'IV shape:', iv.shape, 'dIdV shape:', didv.shape, 'IETS shape:', iets.shape)

        if index == 0:
            return [(bias, iv[:, 3]),(bias, didv[:,3]),(bias, iets[:,3])]
        elif index == 1:
            return [(bias, iv[:, 1]), (bias, didv[:, 1]), (bias, iets[:, 1]),
                    (bias, iv[:, 2]), (bias, didv[:, 2]), (bias, iets[:, 2])]

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
        # self.init_offset()

    def init_offset(self):
        self.spinBox_offset_didv.setMaximum(np.max(np.abs(self.data[1][1])))
        self.spinBox_offset_didv.setMinimum(-np.max(np.abs(self.data[1][1])))
        self.slider_offset_didv.setMaximum(int(np.max(np.abs(self.data[1][1])) * 10000))
        self.slider_offset_didv.setMinimum(int(np.max(-np.abs(self.data[1][1])) * 10000))
        self.spinBox_offset_didv.setValue(np.average(self.data[1][1]))

        self.spinBox_offset_iets.setMaximum(np.max(np.abs(self.data[2][1])))
        self.spinBox_offset_iets.setMinimum(-np.max(np.abs(self.data[2][1])))
        self.slider_offset_iets.setMaximum(int(np.max(np.abs(self.data[2][1])) * 10000))
        self.slider_offset_iets.setMinimum(int(np.max(-np.abs(self.data[2][1])) * 10000))
        self.spinBox_offset_iets.setValue(np.average(self.data[2][1]))

    def set_range(self, index):
        if index == 0:
            self.slider_slope_didv.setMinimum(self.spinBox_slopeMin_didv.value())
            self.slider_slope_didv.setMaximum(self.spinBox_slopeMax_didv.value())
            ran = self.spinBox_slopeMax_didv.value() - self.spinBox_slopeMin_didv.value()
            self.slider_slope_didv.setSingleStep(ran//1000)
            self.slider_slope_didv.setPageStep(ran//100)
            self.spinBox_slope_didv.setMinimum(self.spinBox_slopeMin_didv.value()/10000)
            self.spinBox_slope_didv.setMaximum(self.spinBox_slopeMax_didv.value()/10000)
        elif index == 1:
            self.slider_offset_didv.setMinimum(self.spinBox_offsetMin_didv.value())
            self.slider_offset_didv.setMaximum(self.spinBox_offsetMax_didv.value())
            ran = self.spinBox_offsetMax_didv.value() - self.spinBox_offsetMin_didv.value()
            self.slider_offset_didv.setSingleStep(ran//1000)
            self.slider_offset_didv.setPageStep(ran//100)
            self.spinBox_offset_didv.setMinimum(self.spinBox_offsetMin_didv.value()/10000)
            self.spinBox_offset_didv.setMaximum(self.spinBox_offsetMax_didv.value()/10000)
        elif index == 2:
            self.slider_slope_iets.setMinimum(self.spinBox_slopeMin_IETS.value())
            self.slider_slope_iets.setMaximum(self.spinBox_slopeMax_IETS.value())
            ran = self.spinBox_slopeMax_IETS.value() - self.spinBox_slopeMin_IETS.value()
            self.slider_slope_iets.setSingleStep(ran//1000)
            self.slider_slope_iets.setPageStep(ran//100)
            self.spinBox_slope_iets.setMinimum(self.spinBox_slopeMin_IETS.value()/10000)
            self.spinBox_slope_iets.setMaximum(self.spinBox_slopeMax_IETS.value()/10000)
        elif index == 3:
            self.slider_offset_iets.setMinimum(self.spinBox_offsetMin_IETS.value())
            self.slider_offset_iets.setMaximum(self.spinBox_offsetMax_IETS.value())
            ran = self.spinBox_offsetMax_IETS.value() - self.spinBox_offsetMin_IETS.value()
            self.slider_offset_iets.setSingleStep(ran//1000)
            self.slider_offset_iets.setPageStep(ran//100)
            self.spinBox_offset_iets.setMinimum(self.spinBox_offsetMin_IETS.value()/10000)
            self.spinBox_offset_iets.setMaximum(self.spinBox_offsetMax_IETS.value()/10000)

    def init_name(self, names):
        self.result_names = names

    def pars_changed(self, index):
        if index == 0:
            self.slider_slope_didv.setValue(int(self.spinBox_slope_didv.value()*10000))
            self.slider_offset_didv.setValue(int(self.spinBox_offset_didv.value()*10000))
            self.slider_slope_iets.setValue(int(self.spinBox_slope_iets.value()*10000))
            self.slider_offset_iets.setValue(int(self.spinBox_offset_iets.value()*10000))

        elif index == 1:
            self.spinBox_slope_didv.setValue(self.slider_slope_didv.value()/10000)
            self.spinBox_offset_didv.setValue(self.slider_offset_didv.value()/10000)
            self.spinBox_slope_iets.setValue(self.slider_slope_iets.value()/10000)
            self.spinBox_offset_iets.setValue(self.slider_offset_iets.value()/10000)

        self.slope_didv = self.spinBox_slope_didv.value()
        self.offset_didv = self.spinBox_offset_didv.value()
        self.slope_iets = self.spinBox_slope_iets.value()
        self.offset_iets = self.spinBox_offset_iets.value()

        self.update_graph()

    def update_graph(self):
        ## clear all items in plotItem
        self.plot.clear()

        # Add interval
        self.xx = copy.deepcopy(self.xs)
        self.yy = copy.deepcopy(self.ys)

        bias = self.data[0][0]

        # forward and backward averaged
        if len(self.data) == 3:
            didv = self.data[1][1]
            int_didv = self.func1D.do_int(bias, didv)
            self.cal_int_didv = self.slope_didv * int_didv + self.offset_didv
            self.cal_didv = self.slope_didv * didv + self.offset_didv
            self.xx.append(bias[1:])
            self.yy.append(self.cal_int_didv[1:])

            iets = self.data[2][1]
            int_iets = self.func1D.do_int(bias, iets)
            self.cal_int_iets = self.slope_iets * int_iets + self.offset_iets
            self.cal_iets = self.slope_iets * iets + self.offset_iets
            self.xx.append(bias[1:])
            self.yy.append(self.cal_int_iets[1:])

            # Names
            names = ['IV', 'dIdV', 'IETS', 'cal-int dIdV', 'cal-int IETS']
            # Dedicated colors which look "good"
            colors = ['#08F7FE', '#FE53BB', '#F5D300', '#00ff41', '#FF0000', '#9467bd']
            colors = cc.glasbey_dark[:6]

        # show forward and backward
        elif len(self.data) == 6:
            didv_fwd = self.data[1][1]
            int_didv_fwd = self.func1D.do_int(bias, didv_fwd)
            self.cal_int_didv_fwd = self.slope_didv * int_didv_fwd + self.offset_didv
            self.cal_didv_fwd = self.slope_didv * didv_fwd + self.offset_didv
            self.xx.append(bias[1:])
            self.yy.append(self.cal_int_didv_fwd[1:])

            iets_fwd = self.data[2][1]
            int_iets_fwd = self.func1D.do_int(bias, iets_fwd)
            self.cal_int_iets_fwd = self.slope_iets * int_iets_fwd + self.offset_iets
            self.cal_iets_fwd = self.slope_iets * iets_fwd + self.offset_iets
            self.xx.append(bias[1:])
            self.yy.append(self.cal_int_iets_fwd[1:])

            didv_bwd = self.data[4][1]
            int_didv_bwd = self.func1D.do_int(bias, didv_bwd)
            self.cal_int_didv_bwd = self.slope_didv * int_didv_bwd + self.offset_didv
            self.cal_didv_bwd = self.slope_didv * didv_bwd + self.offset_didv
            self.xx.append(bias[1:])
            self.yy.append(self.cal_int_didv_bwd[1:])

            iets_bwd = self.data[5][1]
            int_iets_bwd = self.func1D.do_int(bias, iets_bwd)
            self.cal_int_iets_bwd = self.slope_iets * int_iets_bwd + self.offset_iets
            self.cal_iets_bwd = self.slope_iets * iets_bwd + self.offset_iets
            self.xx.append(bias[1:])
            self.yy.append(self.cal_int_iets_bwd[1:])

            # Names
            names = ['IV_fwd', 'dIdV_fwd', 'IETS_fwd', 'IV_bwd', 'dIdV_bwd', 'IETS_bwd',
                     'cal-int dIdV_fwd', 'cal-int IETS_fwd', 'cal-int dIdV_bwd', 'cal-int IETS_bwd']
            # Dedicated colors which look "good"
            colors = ['#08F7FE', '#FE53BB', '#F5D300', '#00ff41', '#FF0000', '#9467bd',
                      '#08F7FE', '#FE53BB', '#F5D300', '#00ff41', '#FF0000', '#9467bd']
            colors = cc.glasbey_dark[:10]

        ## append visibility for new lines
        if len(self.visible_list) < len(self.xx):
            self.visible_list += [True] * (len(self.xx) - len(self.visible_list))

        # plot
        for x, y, name, color in zip(self.xx, self.yy, names, colors):
            pen = pg.mkPen(color=color, width=2)
            if name.find('cal') != -1:
                pen.setDashPattern([4, 4, 4, 4])
            #cc.glasbey_light[random.randint(0, 255)]
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
            packed_data.append(np.vstack((bias[1:], self.cal_didv[1:])))
            packed_data.append(np.vstack((bias[1:], self.cal_iets[1:])))
        elif len(self.data) == 6:
            packed_data.append(np.vstack((bias[1:], self.cal_didv_fwd[1:])))
            packed_data.append(np.vstack((bias[1:], self.cal_iets_fwd[1:])))
            packed_data.append(np.vstack((bias[1:], self.cal_didv_bwd[1:])))
            packed_data.append(np.vstack((bias[1:], self.cal_iets_bwd[1:])))
        self.send_signal.emit(packed_data, self.result_names)
        self.close()

    def closeEvent(self, a0: QtGui.QCloseEvent) -> None:
        self.result_names.clear()
        self.cal_int_didv = None
        self.cal_int_iets = None
        self.cal_int_didv_fwd = None
        self.cal_int_iets_fwd = None
        self.cal_int_didv_bwd = None
        self.cal_int_iets_bwd = None
        self.plot.clear()
        self.visible_list = []
        a0.accept()



if __name__ == "__main__":
    # create the application and the main window
    app = QApplication(sys.argv)
    window = myCalIETSWindow()
    window.init_data([0])
    # print(len(window.fake()))
    window.show()
    sys.exit(app.exec_())