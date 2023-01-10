# -*- coding: utf-8 -*-
"""
@Date     : 12/31/2022 15:53:49
@Author   : milier00
@FileName : Illumination.py
"""
import sys
sys.path.append("./ui/")
sys.path.append("./model/")
from PyQt5.QtWidgets import QProxyStyle, QStyle, QStyleOptionSlider, QWidget, QApplication
from PyQt5.QtCore import QSize, Qt, pyqtSignal, QPoint, QRectF
from PyQt5.QtGui import QColor, QPainter, QPainterPath
import pyqtgraph as pg
from pyqtgraph.Qt import QtGui
from images import myImages
from Illumination_ui import Ui_Illumination
from Data import *
import numpy as np
import ctypes
import copy
import scipy


class HollowHandleStyle(QProxyStyle):
    """ 滑块中空样式 """

    def __init__(self, config: dict = None):
        """
        Parameters
        ----------
        config: dict
            样式配置
        """
        super().__init__()
        self.config = {
            "groove.height": 3,
            "sub-page.color": QColor(120, 120, 120),
            "add-page.color": QColor(240, 240, 240, 255),
            "handle.color": QColor(120, 120, 120),
            "handle.ring-width": 4,
            "handle.hollow-radius": 4,
            "handle.margin": 2
        }
        config = config if config else {}
        self.config.update(config)

        # 计算 handle 的大小
        w = self.config["handle.margin"]+self.config["handle.ring-width"] + \
            self.config["handle.hollow-radius"]
        self.config["handle.size"] = QSize(2*w, 2*w)

    def subControlRect(self, cc: QStyle.ComplexControl, opt: QStyleOptionSlider, sc: QStyle.SubControl, widget: QWidget):
        """ 返回子控件所占的矩形区域 """
        if cc != self.CC_Slider or opt.orientation != Qt.Horizontal or sc == self.SC_SliderTickmarks:
            return super().subControlRect(cc, opt, sc, widget)

        rect = opt.rect

        if sc == self.SC_SliderGroove:
            h = self.config["groove.height"]
            grooveRect = QRectF(0, (rect.height()-h)//2, rect.width(), h)
            return grooveRect.toRect()

        elif sc == self.SC_SliderHandle:
            size = self.config["handle.size"]
            x = self.sliderPositionFromValue(
                opt.minimum, opt.maximum, opt.sliderPosition, rect.width())
            # 解决滑块跑出滑动条的情况
            x *= (rect.width()-size.width())/rect.width()
            sliderRect = QRectF(x, 0, size.width(), size.height())
            return sliderRect.toRect()

    def drawComplexControl(self, cc: QStyle.ComplexControl, opt: QStyleOptionSlider, painter: QPainter, widget: QWidget):
        """ 绘制子控件 """
        if cc != self.CC_Slider or opt.orientation != Qt.Horizontal:
            return super().drawComplexControl(cc, opt, painter, widget)

        grooveRect = self.subControlRect(cc, opt, self.SC_SliderGroove, widget)
        handleRect = self.subControlRect(cc, opt, self.SC_SliderHandle, widget)
        painter.setRenderHints(QPainter.Antialiasing)
        painter.setPen(Qt.NoPen)

        # 绘制滑槽
        painter.save()
        painter.translate(grooveRect.topLeft())

        # 绘制划过的部分
        w = handleRect.x()-grooveRect.x()
        h = self.config['groove.height']
        painter.setBrush(self.config["sub-page.color"])
        painter.drawRect(0, 0, w, h)

        # 绘制未划过的部分
        x = w+self.config['handle.size'].width()
        painter.setBrush(self.config["add-page.color"])
        painter.drawRect(x, 0, grooveRect.width()-w, h)
        painter.restore()

        # 绘制滑块
        ringWidth = self.config["handle.ring-width"]
        hollowRadius = self.config["handle.hollow-radius"]
        radius = ringWidth + hollowRadius

        path = QPainterPath()
        path.moveTo(0, 0)
        center = handleRect.center() + QPoint(1, 1)
        path.addEllipse(center, radius, radius)
        path.addEllipse(center, hollowRadius, hollowRadius)

        handleColor = self.config["handle.color"]  # type:QColor
        handleColor.setAlpha(255 if opt.activeSubControls !=
                             self.SC_SliderHandle else 153)
        painter.setBrush(handleColor)
        painter.drawPath(path)

        # 滑块按下
        if widget.isSliderDown():
            handleColor.setAlpha(255)
            painter.setBrush(handleColor)
            painter.drawEllipse(handleRect)


class myIlluminationWin(QWidget, Ui_Illumination):
    # Common signal
    close_signal = pyqtSignal(object)

    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.init_UI()
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("myappid")
        self.kernel_dict = {0: np.array([[0,-1,0],[-1,5,-1],[0,-1,0]]), 1: np.array([[0,1,0],[1,-4,1],[0,1,0]]), \
                            2: np.array([[0.0625,0.125,0.0625],[0.125,0.25,0.125],[0.0625,0.125,0.125]]), \
                            3: np.array([[0,1,0],[1,9,1],[0,1,0]]),\
                            4: np.array([[-1,-2,-1],[0,0,0],[1,2,1]]), 5: np.array([[-2,-1,0],[-1,1,1],[0,1,2]]), \
                            6: np.array([[-1,-1,-1],[-1,8,-1],[-1,-1,-1]]), 7: np.array([[-1,-1,-1],[-1,9,-1],[-1,-1,-1]]), \
                            8: np.array([[1,1,1],[1,-7,1],[1,1,1]]), \
                            9: np.array([[-1,-1,-1,-1,-1],[-1,2,2,2,-1],[-1,2,8,2,-1],[-1,2,2,2,-1], [-1,-1,-1,-1,-1]])/8.0,
                            10: np.array([[1/3,0,-1/3],[1/3,0,-1/3],[1/3,0,-1/3]]),
                            11: np.array([[1/4,0,-1/4],[1/2,0,-1/2],[1/4,0,-1/4]])}

    def init_UI(self):
        self.phi = np.pi/2
        self.theta = np.pi/4

        # graphicsView
        self.graphicsView.ci.layout.setContentsMargins(0, 0, 0, 0)     # eliminate the border
        self.graphicsView.ci.layout.setSpacing(0)                      # eliminate the border
        self.view_box = self.graphicsView.addViewBox()
        self.view_box.setRange(QRectF(-512, -512, 512, 512), padding=0)
        self.view_box.setLimits(xMin=-512, xMax=512, yMin=-512, yMax=512, \
                                minXRange=3, maxXRange=1024, minYRange=3, maxYRange=1024)
        self.view_box.setAspectLocked(True)
        self.view_box.setCursor(Qt.CrossCursor)
        self.view_box.setMouseMode(self.view_box.PanMode)

        self.img_display = pg.ImageItem()
        self.view_box.addItem(self.img_display)

        self.myimg = myImages()

        self.spinBox_theta.editingFinished.connect(self.update_data)
        self.slider_theta.valueChanged.connect(self.spinBox_theta.setValue)
        self.slider_theta.valueChanged.connect(self.update_data)
        self.slider_theta.setStyle(HollowHandleStyle())

        self.spinBox_phi.editingFinished.connect(self.update_data)
        self.slider_phi.valueChanged.connect(self.spinBox_phi.setValue)
        self.slider_phi.valueChanged.connect(self.update_data)
        self.slider_phi.setStyle(HollowHandleStyle())

    def init_data(self, img):
        self.raw_img = img
        ''' for test only '''
        # with open(r"D:\Code\2022oct\11102207.nstm", 'rb') as input:
        #     data = pickle.load(input)
        # self.raw_img = data.data[0]

        self.current_img = copy.deepcopy(self.raw_img)
        self.update_data()

    def update_data(self):
        self.theta = self.spinBox_theta.value() * np.pi / 180
        self.phi = self.spinBox_phi.value() * np.pi / 180
        Prewitt_horizontal = self.kernel_dict[10]
        Prewitt_vertival = self.kernel_dict[10].transpose()
        Sobel_horizontal = self.kernel_dict[11]
        Sobel_vertival = self.kernel_dict[11].transpose()
        kernel = Prewitt_vertival * np.sin(self.phi) + Prewitt_horizontal * np.cos(self.phi)
        kernel = Sobel_vertival * np.sin(self.phi) + Sobel_horizontal * np.cos(self.phi)

        self.current_img = scipy.ndimage.convolve(self.raw_img, kernel)
        # self.current_img = scipy.ndimage.prewitt(self.raw_img, axis=-1)
        # self.current_img = scipy.ndimage.sobel(self.raw_img, axis=0)

        self.update_display()

    # !!! not used
    def convolve(self, image, filt):
        height, width = image.shape
        h, w = filt.shape
        height_new = height - h + 1
        width_new = width - w + 1
        image_new = np.zeros((height_new, width_new), dtype=float)
        for i in range(height_new):
            for j in range(width_new):
                image_new[i, j] = np.sum(image[i:i + h, j:j + w] * filt)
        image_new = image_new.clip(0, 255)
        image_new = np.rint(image_new).astype('uint8')
        return image_new

    def update_display(self):
        self.img_display.setImage(self.current_img, levels=[self.current_img.min() * np.sin(self.theta), self.current_img.max() * np.cos(self.theta)])
        self.view_box.setRange(QRectF(0, 0, self.img_display.width(), self.img_display.height()), padding=0)

    def closeEvent(self, a0: QtGui.QCloseEvent) -> None:
        self.close_signal.emit(self.img_display.image)
        a0.accept()

if __name__ == "__main__":
    # create the application and the main window
    app = QApplication(sys.argv)
    window = myIlluminationWin()
    window.init_data(0)
    window.show()
    sys.exit(app.exec_())