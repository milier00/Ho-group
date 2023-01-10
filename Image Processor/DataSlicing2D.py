# -*- coding: utf-8 -*-
"""
@Date     : 2021/6/1 08:52:41
@Author   : milier00
@FileName : DataAnalysis.py
"""
import sys
sys.path.append("../ui/")
sys.path.append("../model/")
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QGridLayout
from PyQt5.QtCore import pyqtSignal, QRectF
from DataAnalysis_ui import Ui_DataAnalysis
from images import myImages
from Data import *
import numpy as np
import pyqtgraph as pg
import ctypes


class myDataSlicing2D(Ui_DataAnalysis, QWidget):
    close_signal = pyqtSignal()
    do_signal = pyqtSignal()
    export_signal = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.init_UI()
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("myappid")

    def init_UI(self):
        self.resize(1400, 420)
        self.myimg = myImages()

        l = QGridLayout()
        self.setLayout(l)
        l.setSpacing(0)

        l.addWidget(self.graphicsLayoutWidget, 0, 0, 4, 1)

        # A plot area (ViewBox + axes) for displaying the image
        self.p1 = self.graphicsLayoutWidget.addPlot(title="", colspan=1)
        self.p1.vb.setAspectLocked(True)
        # Item for displaying image data
        self.img = pg.ImageItem()
        self.p1.addItem(self.img)
        self.p1.setMaximumWidth(400)
        self.p1.setMinimumWidth(400)

        # Custom ROI for selecting an image region
        self.roi = pg.LineROI([0,0], [20, 20], width=5, pen=(1, 9))
        self.p1.addItem(self.roi)
        self.roi.setZValue(10)  # make sure ROI is drawn above image

        self.line = pg.LineSegmentROI([[0, 0], [20, 20]], pen='r')
        self.p1.addItem(self.line)
        self.line.setZValue(10)

        # Isocurve drawing
        self.iso = pg.IsocurveItem(level=0.8, pen='g')
        self.iso.setParentItem(self.img)
        self.iso.setZValue(5)

        # Contrast/color control
        self.hist = pg.HistogramLUTItem()
        self.hist.setImageItem(self.img)
        self.graphicsLayoutWidget.addItem(self.hist)

        # # set jet colormap
        # colors = [(0, 0, 128), (0, 0, 255), (0, 255, 255), (255, 255, 0), (255, 0, 0), (128, 0, 0)]
        # pos = np.array([0, 0.125, 0.375, 0.625, 0.875, 1])
        # cmap = pg.ColorMap(pos=pos, color=colors)
        # self.hist.gradient.setColorMap(cmap)

        # Draggable line for setting isocurve level
        self.isoLine = pg.InfiniteLine(angle=0, movable=True, pen='g')
        self.hist.vb.addItem(self.isoLine)
        self.hist.vb.setMouseEnabled(y=False)  # makes user interaction a little easier
        self.isoLine.setZValue(1000)  # bring iso line above contrast controls

        # Another plot area for displaying ROI data
        self.p3 = self.graphicsLayoutWidget.addPlot(colspan=1)
        self.p3.setMaximumHeight(400)
        self.p3.setMinimumWidth(400)
        self.p3.setMaximumWidth(400)

        self.p2 = self.graphicsLayoutWidget.addPlot(colspan=1)
        self.p2.setMaximumHeight(400)
        self.p2.setMinimumWidth(400)
        self.p2.setMaximumWidth(400)

        # Monkey-patch the image to use our custom hover function.
        # This is generally discouraged (you should subclass ImageItem instead),
        # but it works for a very simple use like this.
        self.img.hoverEvent = self.imageHoverEvent

        self.line.sigRegionChanged.connect(self.updateLinecut)
        self.roi.sigRegionChanged.connect(self.updatePlot)
        self.isoLine.sigDragged.connect(self.updateIsocurve)


    # thin line
    def updateLinecut(self):
        ret = self.line.getArrayRegion(self.raw_data, self.img)
        self.data1d = ret
        self.p3.clear()
        #cc.glasbey_light[random.randint(0, 255)
        self.p3.plot(ret, pen=pg.mkPen((255, 0, 0, 255), width=2))

    # bold line
    def updatePlot(self):
        selected = self.roi.getArrayRegion(self.raw_data, self.img)
        self.p2.plot(selected.mean(axis=1), clear=True, pen=pg.mkPen((0, 0, 0, 255), width=2))

    def updateIsocurve(self):
        self.iso.setLevel(self.isoLine.value())

    def imageHoverEvent(self, event):
        """Show the position, pixel, and value under the mouse cursor.
        """
        if event.isExit():
            self.p1.setTitle("")
            return
        pos = event.pos()
        i, j = pos.y(), pos.x()
        i = int(np.clip(i, 0, self.data.shape[0] - 1))
        j = int(np.clip(j, 0, self.data.shape[1] - 1))
        val = self.data[i, j]
        ppos = self.img.mapToParent(pos)
        x, y = ppos.x(), ppos.y()
        self.p1.setTitle("<span style='font-size: 8pt'>pos:(%0.1f,%0.1f) <br /> pixel:(%d,%d) <br /> value:%g</span>" % (x, y, i, j, val), justify='left')

    def init_data(self, data, name, energy, rscale):
        self.setWindowTitle('Data Analysis: ' + name)
        self.raw_data = data
        self.data = self.myimg.prepare_data(self.myimg.partial_renormalize(data))
        self.energy = energy
        self.rscale = rscale
        self.img.setImage(self.data)
        # print(self.data.min(), self.data.max())

        # zoom to fit image
        self.p1.autoRange()
        # self.img.vb.setRange(QRectF(0, 0, self.img.width(), self.img.height()), padding=0)
        self.hist.setLevels(self.data.min(), self.data.max())
        self.isoLine.setValue(np.median(self.data))

        # build isocurves from smoothed data
        self.iso.setData(pg.gaussianFilter(self.data, (2, 2)))
        self.updatePlot()
        self.updateLinecut()

    # Emit close signal
    def closeEvent(self, event):
        self.close_signal.emit()
        event.accept()




if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = myDataSlicing2D()

    # Generate image data
    # data = np.random.normal(size=(200, 100))
    # data[20:80, 20:80] += 2.
    # data = pg.gaussianFilter(data, (3, 3))
    # data += np.random.normal(size=(200, 100)) * 0.1

    data = np.loadtxt('C:/Users/DAN/Documents/MyCode/PythonScripts/stm2/test data/delay scan imaging 2/fft/freq_max.txt')

    window.init_data(data,'hhh', [200], (200,200))
    # set position and scale of image
    # window.img.scale(0.2, 0.2)
    # window.img.translate(-50, 0)

    window.show()
    sys.exit(app.exec_())