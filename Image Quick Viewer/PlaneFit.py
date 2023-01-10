# -*- coding: utf-8 -*-
"""
@Date     : 12/6/2022 17:49:21
@Author   : milier00
@FileName : QuickView.py
"""
import sys
sys.path.append("./ui/")
sys.path.append("./model/")

from PyQt5.QtWidgets import QApplication
from pyqtgraph.Qt import QtGui
from images import myImages
from PlaneFitWindow_ui import Ui_PlaneFitWindow
from customROI import *
from Data import *
import numpy as np
import ctypes
import copy
from PyQt5.QtWidgets import QLabel
from PyQt5.QtCore import  Qt, pyqtSignal, QRectF
import pyqtgraph as pg
from pyqtgraph.Qt import QtCore
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.figure import Figure
import matplotlib
matplotlib.use('Qt5Agg')
from qframelesswindow import FramelessWindow, TitleBar



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
                "color": (255, 255, 255, 20),
                'background': (0, 0, 0, 0)
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

class MplCanvas(FigureCanvasQTAgg):

    def __init__(self, parent=None, width=5, height=4, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)
        # fig.patch.set_facecolor("None")
        self.axes = fig.add_subplot(111, projection='3d')
        super(MplCanvas, self).__init__(fig)


class myPlaneFitWin(FramelessWindow, Ui_PlaneFitWindow):
    # Common signal
    close_signal = pyqtSignal(object)

    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.init_UI()
        self.setTitleBar(CustomTitleBar(self))
        self.titleBar.raise_()
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("myappid")

    def init_UI(self):
        # self.move(1350, 50)         # Init ui position
        self.resize(1200, 500)
        self.setStyleSheet("background-color: black; color: white;")

        self.myimg = myImages()

        # graphicsView | left
        self.view_box_left = self.graphicsView_left.addViewBox()
        self.view_box_left.setAspectLocked(True)
        self.view_box_left.setCursor(Qt.CrossCursor)
        self.view_box_left.setMouseMode(self.view_box_left.PanMode)
        self.img_display_left = pg.ImageItem()
        self.view_box_left.addItem(self.img_display_left)

        # graphicsView | middle
        self.view_box_mid = self.graphicsView_mid.addViewBox()
        self.view_box_mid.setAspectLocked(True)
        self.view_box_mid.setCursor(Qt.CrossCursor)
        self.view_box_mid.setMouseMode(self.view_box_mid.PanMode)
        self.img_display_mid = pg.ImageItem()
        self.view_box_mid.addItem(self.img_display_mid)

        # graphicsView | middle
        self.view_box_right = self.graphicsView_right.addViewBox()
        self.view_box_right.setAspectLocked(True)
        self.view_box_right.setCursor(Qt.CrossCursor)
        self.view_box_right.setMouseMode(self.view_box_right.PanMode)
        self.img_display_right = pg.ImageItem()
        self.view_box_right.addItem(self.img_display_right)

        # pushButton |
        self.pushButton_full_left.clicked.connect(lambda: self.full_view(0))
        self.pushButton_full_mid.clicked.connect(lambda: self.full_view(1))
        self.pushButton_full_right.clicked.connect(lambda: self.full_view(2))

        # ROI | define pens
        blue_pen = pg.mkPen((100, 200, 255, 255), width=1)
        green_pen = pg.mkPen((150, 220, 0, 255), width=1)
        yellow_pen = pg.mkPen((255, 234, 0, 255), width=2)
        purple_pen = pg.mkPen((220, 180, 255, 255), width=2)

        self.pts = pg.PolyLineROI([[0, 0]], closed=False, pen=yellow_pen)
        # self.pts.removeHandle(self.pts.getHandles()[0])
        self.pts.clearPoints()
        self.pts.update()
        self.pts.handleSize = 10
        handlePen = pg.mkPen((150, 255, 255), width=5)
        self.pts.handlePen = pg.mkPen(handlePen)
        handleHoverPen = pg.mkPen((255, 255, 0), width=5)
        self.pts.handleHoverPen = handleHoverPen
        self.pts.addHandle({'type': 'f', 'pos':[5, 5]})
        self.pts.addHandle({'type': 'f', 'pos':[10, 10]})
        self.pts.addHandle({'type': 'f','pos':[5, 10]})
        self.pts.addHandle({'type': 'f', 'pos':[10, 5]})
        self.view_box_left.addItem(self.pts)
        self.pts.sigRegionChanged.connect(self.get_pts_pos)
        self.pts.update()

        self.layout = self.widget.layout()
        """ pyatgraph """
        ## Create a GL View widget to display data
        # self.w3d = gl.GLViewWidget()
        # self.layout.addWidget(self.w3d, 0, 2, 1, 1)
        # self.w3d.setCameraPosition(distance=50)
        """ pyplot """
        # self.fig = Figure()
        # self.canvas = FigureCanvas(self.fig)
        # self.axes = self.fig.add_subplot(111, projection='3d')
        # self.layout.addWidget(self.canvas, 0, 2, 1, 1)
        """ matplotlib """
        # Create the maptlotlib FigureCanvas object,
        # which defines a single set of axes as self.axes.
        self.canvas = MplCanvas(self, width=5, height=4, dpi=100)
        self.canvas.setStyleSheet("background-color:transparent;")
        self.canvas.axes.patch.set_alpha(0)
        self.layout.addWidget(self.canvas, 1, 6, 1, 1)
        self._setLastLabel()


    def _setLastLabel(self):
        self.label_4 = QtWidgets.QLabel(self.widget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_4.sizePolicy().hasHeightForWidth())
        self.label_4.setSizePolicy(sizePolicy)
        self.label_4.setMaximumSize(QtCore.QSize(16777215, 16777215))
        font = QtGui.QFont()
        font.setFamily("Yu Gothic UI")
        font.setPointSize(10)
        font.setBold(True)
        font.setItalic(False)
        font.setUnderline(False)
        font.setWeight(75)
        font.setStrikeOut(False)
        font.setKerning(True)
        self.label_4.setFont(font)
        self.label_4.setAlignment(QtCore.Qt.AlignCenter)
        self.label_4.setObjectName("label_4")
        self.gridLayout_2.addWidget(self.label_4, 0, 6, 1, 1)
        _translate = QtCore.QCoreApplication.translate
        self.label_4.setText(_translate("PlaneFitWindow", "Fitting"))

    # reset button slot | make image full view
    def full_view(self, index):
        '''Zoom in to whole image. '''
        if index == 0:
            self.view_box_left.setRange(QRectF(0, 0, self.img_display_left.width(), self.img_display_left.height()), padding=0)
        elif index == 1:
            self.view_box_mid.setRange(QRectF(0, 0, self.img_display_mid.width(), self.img_display_mid.height()), padding=0)
        elif index == 2:
            self.view_box_right.setRange(QRectF(0, 0, self.img_display_right.width(), self.img_display_right.height()), padding=0)

    # pts | update info
    def get_pts_pos(self):
        pos_x = []; pos_y = []; z=[];
        for handle in self.pts.getHandles():
            pos_x.append(int(np.trunc(handle.pos()[0] + self.pts.pos()[0])))
            pos_y.append(int(np.trunc(handle.pos()[1] + self.pts.pos()[1])))
            z.append(self.raw_img[pos_x[-1]][pos_y[-1]])
        x_p, y_p, z_p, new_z = self.get_plane_fit(pos_x, pos_y, z)
        self.update_plot(x_p, y_p, z_p, pos_x, pos_y, z, new_z)

    def get_plane_fit(self, x, y, z):

        A = np.zeros((3, 3))
        for i in range(0, len(x)):
            A[0, 0] = A[0, 0] + x[i] ** 2
            A[0, 1] = A[0, 1] + x[i] * y[i]
            A[0, 2] = A[0, 2] + x[i]
            A[1, 0] = A[0, 1]
            A[1, 1] = A[1, 1] + y[i] ** 2
            A[1, 2] = A[1, 2] + y[i]
            A[2, 0] = A[0, 2]
            A[2, 1] = A[1, 2]
            A[2, 2] = len(x)

        b = np.zeros((3, 1))
        for i in range(0, len(x)):
            b[0, 0] = b[0, 0] + x[i] * z[i]
            b[1, 0] = b[1, 0] + y[i] * z[i]
            b[2, 0] = b[2, 0] + z[i]

        A_inv = np.linalg.inv(A)
        X = np.dot(A_inv, b)
        # print('平面拟合结果为：z = %.3f * x + %.3f * y + %.3f' % (X[0, 0], X[1, 0], X[2, 0]))

        x_p = np.array([i for i in range(0, self.raw_img.shape[0])])
        y_p = np.array([i for i in range(0, self.raw_img.shape[1])])
        x_p, y_p = np.meshgrid(x_p, y_p)
        z_p = X[0, 0] * x_p + X[1, 0] * y_p + X[2, 0]

        new_z = X[0, 0] * self.raw_x + X[1, 0] * self.raw_y + X[2, 0] + np.min(self.raw_img)
        new_z = self.raw_z - new_z
        new_z = np.reshape(new_z, (self.raw_img.shape[0], self.raw_img.shape[1])).astype(np.float32)

        # from matplotlib import pyplot as plt
        # fig1 = plt.figure()
        # ax1 = plt.axes(projection='3d')
        # ax1.set_xlabel("x")
        # ax1.set_ylabel("y")
        # ax1.set_zlabel("z")
        # ax1.scatter(x, y, z, c='r', marker='o')
        # ax1.plot_wireframe(x_p, y_p, z_p, rstride=10, cstride=10)
        # ax1.scatter(self.raw_x, self.raw_y, self.raw_z, c='g', marker='.', alpha=0.05)
        # plt.show()

        return x_p, y_p, z_p, new_z

    def update_plot(self, x_p, y_p, z_p, pos_x, pos_y, z, new_z):
        """ pyqtgraph """
        # ## Add a grid to the view
        # self.grid = gl.GLGridItem()
        # self.grid.scale(self.raw_img.shape[0], self.raw_img.shape[1], 1)
        # self.grid.setDepthValue(10)  # draw grid after surfaces since they may be translucent
        # # self.w3d.addItem(self.grid)
        # ## Saddle example with x and y specified
        # x = np.linspace(0, self.raw_img.shape[0], self.raw_img.shape[0])
        # y = np.linspace(0, self.raw_img.shape[1], self.raw_img.shape[1])
        # z = 0.1 * ((x.reshape(129, 1) ** 2) - (y.reshape(1, 129) ** 2))
        # print(x.shape, y.shape, z.shape)
        # print(x_p.shape, y_p.shape, z_p.shape)
        # self.p3d = gl.GLSurfacePlotItem(x=x, y=y, z=z_p, shader='normalColor')
        # self.p3d_raw = gl.GLSurfacePlotItem(x=x, y=y, z=self.raw_img,  shader='shaded', color=(0.5, 0.5, 1, 1))
        # self.w3d.addItem(self.p3d)
        # self.w3d.addItem(self.p3d_raw)
        """ pyplot """
        # self.axes.clear()
        # self.axes.plot_wireframe(x_p, y_p, z_p, rstride=10, cstride=10)
        # self.axes.scatter(self.raw_x, self.raw_y, self.raw_z, c='g', marker='.', alpha=0.05)
        """ matplotlib """
        self.canvas.axes.cla()
        self.canvas.axes.plot_wireframe(x_p, y_p, z_p, rstride=10, cstride=10)
        self.canvas.axes.scatter(self.raw_x, self.raw_y, self.raw_z, c='g', marker='.', alpha=0.05)
        self.canvas.axes.scatter(pos_x, pos_y, z, c='r', marker='o')
        self.img_display_mid.setImage(new_z)
        self.result = copy.deepcopy(new_z)
        self.view_box_mid.setRange(QRectF(0, 0, self.img_display_mid.width(), self.img_display_mid.height()), padding=0)

    def init_data(self, data):
        self.data = data
        self.raw_img = self.myimg.prepare_data(self.myimg.partial_renormalize(self.data))
        """ Uncomment this 4 lines in test mode """
        # file = 'D:/Code\\2022oct/11012207.nstm'
        # self.data = MappingData(file)
        # child_index = 0
        # self.raw_img = self.myimg.prepare_data(self.myimg.partial_renormalize(self.data.data[child_index]))


        self.raw_x = np.array([[i + 1] * self.raw_img.shape[0] for i in range(self.raw_img.shape[0])]).flatten()
        self.raw_y = np.array(list(np.arange(self.raw_img.shape[1]) + 1) * self.raw_img.shape[1])
        self.raw_z = self.raw_img.flatten()

        self.img_display_left.setImage(self.raw_img)
        self.view_box_left.setRange(QRectF(0, 0, self.img_display_left.width(), self.img_display_left.height()),
                                      padding=0)

        planefit_img = self.myimg.plane_fit(self.raw_img)
        self.img_display_right.setImage(planefit_img)
        self.view_box_right.setRange(QRectF(0, 0, self.img_display_right.width(), self.img_display_right.height()),
                                     padding=0)
        self.get_pts_pos()

    def closeEvent(self, a0: QtGui.QCloseEvent) -> None:
        self.close_signal.emit(self.result)
        a0.accept()


if __name__ == "__main__":

    # enable dpi scale
    # QApplication.setHighDpiScaleFactorRoundingPolicy(
    # Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)
    # QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
    # QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps)

    app = QApplication(sys.argv)
    window = myPlaneFitWin()
    window.init_data(0)
    window.show()
    sys.exit(app.exec_())