# -*- coding: utf-8 -*-
"""
@Date     : 12/6/2022 17:49:21
@Author   : milier00
@FileName : QuickView.py
"""
import sys
sys.path.append("./ui/")
sys.path.append("./model/")
from PyQt5.QtWidgets import QMainWindow, QMdiSubWindow, QLabel, QMenu, QToolButton, QProxyStyle, QStyle, \
    QStyleOptionSlider, QWidget, QApplication, QButtonGroup, QAction, QAbstractItemView, QShortcut, QListWidget, QFileDialog
from PyQt5.QtCore import QEasingCurve, QSettings, QPropertyAnimation, QTimer, QSize, Qt, pyqtSignal, QPoint, QRectF
from PyQt5.QtGui import QPixmap, QColor, QPainter, QPainterPath
from PyQt5 import QtWidgets, QtCore
import pyqtgraph as pg
from pyqtgraph.Qt import QtGui
from images import myImages
from QuickView_ui import Ui_QuickView
from DataAnalysis import myDataAnalysis
from PlaneFit import myPlaneFitWin
from Illumination import myIlluminationWin
from MapWindow import myMapWin
from Data import *
import cv2 as cv
import numpy as np
import ctypes
from skimage import exposure, img_as_float
import functools as ft
import copy
import os
from matplotlib import pyplot as plt
from matplotlib.colors import LinearSegmentedColormap

"""============= Fluent status bar  ========================"""
class StateTooltip(QWidget):
    """ State tooltip """

    closedSignal = pyqtSignal()

    def __init__(self, title, content, parent=None):
        """
        Parameters
        ----------
        title: str
            title of tooltip

        content: str
            content of tooltip

        parant:
            parent window
        """
        super().__init__(parent)
        self.title = title
        self.content = content

        self.titleLabel = QLabel(self.title, self)
        self.contentLabel = QLabel(self.content, self)
        self.rotateTimer = QTimer(self)
        self.closeTimer = QTimer(self)
        self.animation = QPropertyAnimation(self, b"windowOpacity")
        self.busyImage = QPixmap("resource/images/running.png")
        self.doneImage = QPixmap("resource/images/completed.png")
        self.closeButton = QToolButton(self)

        self.isDone = False
        self.rotateAngle = 0
        self.deltaAngle = 20

        self.__initWidget()

    def __initWidget(self):
        """ initialize widgets """
        self.setAttribute(Qt.WA_StyledBackground)
        self.rotateTimer.setInterval(50)
        self.closeTimer.setInterval(1000)
        self.contentLabel.setMinimumWidth(200)

        # connect signal to slot
        self.closeButton.clicked.connect(self.__onCloseButtonClicked)
        self.rotateTimer.timeout.connect(self.__rotateTimerFlowSlot)
        self.closeTimer.timeout.connect(self.__slowlyClose)

        self.__setQss()
        self.__initLayout()

        self.rotateTimer.start()

    def __initLayout(self):
        """ initialize layout """
        self.setFixedSize(max(self.titleLabel.width(),
                          self.contentLabel.width()) + 70, 64)
        self.titleLabel.move(40, 11)
        self.contentLabel.move(15, 34)
        self.closeButton.move(self.width() - 30, 23)

    def __setQss(self):
        """ set style sheet """
        self.titleLabel.setObjectName("titleLabel")
        self.contentLabel.setObjectName("contentLabel")

        with open("./resource/style/state_tooltip.qss", encoding="utf-8") as f:
            self.setStyleSheet(f.read())

        self.titleLabel.adjustSize()
        self.contentLabel.adjustSize()

    def setTitle(self, title: str):
        """ set the title of tooltip """
        self.title = title
        self.titleLabel.setText(title)
        self.titleLabel.adjustSize()

    def setContent(self, content: str):
        """ set the content of tooltip """
        self.content = content
        self.contentLabel.setText(content)

        # adjustSize() will mask spinner get stuck
        self.contentLabel.adjustSize()

    def setState(self, isDone=False):
        """ set the state of tooltip """
        self.isDone = isDone
        self.update()
        if self.isDone:
            self.closeTimer.start()

    def __onCloseButtonClicked(self):
        """ close button clicked slot """
        self.closedSignal.emit()
        self.hide()

    def __slowlyClose(self):
        """ fade out """
        self.rotateTimer.stop()
        self.animation.setEasingCurve(QEasingCurve.Linear)
        self.animation.setDuration(500)
        self.animation.setStartValue(1)
        self.animation.setEndValue(0)
        self.animation.finished.connect(self.deleteLater)
        self.animation.start()

    def __rotateTimerFlowSlot(self):
        """ rotate timer time out slot """
        self.rotateAngle = (self.rotateAngle + self.deltaAngle) % 360
        self.update()

    def paintEvent(self, e):
        """ paint state tooltip """
        super().paintEvent(e)
        painter = QPainter(self)
        painter.setRenderHints(QPainter.SmoothPixmapTransform)
        painter.setPen(Qt.NoPen)
        if not self.isDone:
            painter.translate(24, 23)
            painter.rotate(self.rotateAngle)
            painter.drawPixmap(
                -int(self.busyImage.width() / 2),
                -int(self.busyImage.height() / 2),
                self.busyImage,
            )
        else:
            painter.drawPixmap(14, 13, self.doneImage.width(),
                               self.doneImage.height(), self.doneImage)

"""============= Fluent slide bar  ========================"""
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

"""============= Drop in List Widget  ========================"""
class DropInList(QListWidget):
    list_changed_signal = pyqtSignal()

    def __init__(self):
        super(DropInList, self).__init__()
        self.setAcceptDrops(True)

    def dropEvent(self, QDropEvent):
        source_Widget = QDropEvent.source()
        items = source_Widget.selectedItems()

        for i in items:
            source_Widget.takeItem(source_Widget.indexFromItem(i).row())
            self.addItem(i)

        self.list_changed_signal.emit()  # only used for drop event

def create_icon_by_color(color):
    pixmap = QtGui.QPixmap(512, 512)
    pixmap.fill(color)
    return QtGui.QIcon(pixmap)

'''########## 1. My original sub window ##############'''
# class mySubWin(QMdiSubWindow):
#     update_display_signal = pyqtSignal()
#
#     def __init__(self):
#         super().__init__()
#         self.init_UI()
#         self.setAttribute(Qt.WA_DeleteOnClose)
#         ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("myappid")
#
#     def init_UI(self):
#         self.setOption(True, QMdiSubWindow.RubberBandResize)
#         self.setWindowIcon(create_icon_by_color(QtGui.QColor("transparent")))
#         # self.showSystemMenu()
#         self.resize(400, 400)
#
#         self.contrast = 200
#         self.opacity = 100
#         self.pallet = 0
#         self.filter = [False, False, True]
#         self.color_map_index = 51
#
#         self.myimg = myImages()
#
#         # Plot widgets |
#         self.graphicsView = pg.GraphicsLayoutWidget(self)
#         self.setWidget(self.graphicsView)
#         self.plot = self.graphicsView.addPlot(row=0, col=0)
#
#         # self.view_box.setRange(QRectF(-512, -512, 512, 512), padding=0)
#         # self.view_box.setLimits(xMin=-512, xMax=512, yMin=-512, yMax=512, \
#         #                         minXRange=3, maxXRange=1024, minYRange=3, maxYRange=1024)
#         #
#         # self.view_box.setCursor(Qt.CrossCursor)
#         # self.view_box.setMouseMode(self.view_box.PanMode)
#         self.view_box = self.plot.vb
#         self.view_box.setAspectLocked(True)
#         self.view_box.setMouseEnabled(x=True, y=True)
#         # self.viewbox.disableAutoRange()
#         # self.viewbox.hideButtons()
#         self.view_box.setRange(xRange=(0, 100), yRange=(0, 100), padding=0)
#
#         self.img_display = pg.ImageItem()
#         self.view_box.addItem(self.img_display)
#         self.plot.showAxes(False, showValues=(True, False, False, True))
#
#         ''' ColorBar '''
#         self.colorBar = self.plot.addColorBar(self.img_display, width=18, label=None, colorMap='CET-L9', values=(0, 30_000), interactive=False)
#
#         # bar = pg.ColorBarItem(
#         #     values = (0, 30_000),
#         #     colorMap='CET-L4',
#         #     label='horizontal color bar',
#         #     limits = (0, None),
#         #     rounding=1000,
#         #     orientation = 'h',
#         #     pen='#8888FF', hoverPen='#EEEEFF', hoverBrush='#EEEEFF80'
#         # )
#         ''' pgcolorbar '''
#         # showHistogram = True
#         # self.colorBar = ColorLegendItem(
#         #     imageItem=self.img_display,
#         #     showHistogram=showHistogram,
#         #     histHeightPercentile=99.0, # Uncomment to discard the outliers in the histogram height
#         #     label='Random data')
#         # self.colorBar.setMinimumHeight(60)
#         # self.graphicsView.addItem(self.colorBar, 0, 1)
#
#         # ROI | define pens
#         blue_pen = pg.mkPen((100, 200, 255, 255), width=1)
#         green_pen = pg.mkPen((150, 220, 0, 255), width=1)
#         yellow_pen = pg.mkPen((255, 234, 0, 255), width=2)
#         purple_pen = pg.mkPen((220, 180, 255, 255), width=2)
#
#         # ROI | image box
#         self.roi = pg.ROI([0, 0], [10, 10], resizable=False, removable=True, handlePen=(255, 255, 255, 0))
#         self.roi.hide()
#
#         # ROI | Line Cut
#         self.linecut = pg.LineSegmentROI([[0, 0], [100, 100]], pen=green_pen)
#         self.linecut.rotateSnapAngle = 0.01
#         self.linecut.setZValue(11)
#         self.view_box.addItem(self.linecut)
#         self.linecut.removeHandle(0)
#         self.linecut.addTranslateHandle(pos=[0, 0], index=0)
#         self.linecut.getHandles()[0].pen = purple_pen
#         self.linecut.getHandles()[0].radius = 10
#         # self.linecut.getHandles()[1].pen = blue_pen
#         # self.linecut.getHandles()[1].radius = 10
#         self.linecut.hide()
#
#     def init_data(self, data, child_index):
#         self.data = data
#         # self.raw_img = self.myimg.prepare_data(
#         #     self.myimg.partial_renormalize(self.data[parent_index].child_data[self.energy_index]))
#         self.raw_img = self.myimg.prepare_data(self.myimg.partial_renormalize(self.data.data[child_index]))
#         self.current_img = copy.deepcopy(self.raw_img)
#         self.update_display_signal.emit()
#
#     # ROI | image box
#     def init_roi(self):
#         ''' ROI needed for rotate option '''
#         self.img_display.setParentItem(self.view_box)
#         self.view_box.removeItem(self.roi)
#         self.roi = pg.ROI([0, 0], [self.img_display.width(), self.img_display.height()], resizable=False,
#                           removable=True, handlePen=(255, 255, 255, 0))
#         self.roi.addRotateHandle([1, 0], [0.5, 0.5])
#         self.roi.addRotateHandle([0, 1], [0.5, 0.5])
#         self.view_box.addItem(self.roi)
#         self.img_display.setParentItem(self.roi)
#
#     # update display image
#     def update_display(self):
#         '''Update image based on user selected filter and colormap.'''
#         if self.pallet == 0:
#             psudo_gray_img = cv.cvtColor(self.current_img, cv.COLOR_GRAY2BGR)
#             self.color_current_img = psudo_gray_img
#             if self.filter[0]:
#                 cmap = self.myimg.reverse_colormap('gray')
#             else:
#                 cmap = 'gray'
#             self.colorBar.setColorMap(cmap)
#             # self.colorBar.autoScaleFromImage()
#         elif self.pallet == 1:
#             color_img = self.myimg.color_map(self.current_img, self.color_map_index)
#             self.color_current_img = color_img
#             # self.colorBar.setLevels(low=color_img.min(), high=color_img.min())
#             if self.filter[0]:
#                 cmap = self.myimg.colormap_dict_cm[self.color_map_index]
#                 cmap = self.myimg.reverse_colormap(cmap)
#             else:
#                 cmap = self.myimg.colormap_dict_cm[self.color_map_index]
#             self.colorBar.setColorMap(cmap)
#
#         # set contrast
#         img = img_as_float(self.color_current_img)
#         self.color_current_img = exposure.adjust_gamma(img, self.contrast / 200)
#         # set opacity
#         self.img_display.setOpacity(self.opacity / 100)
#         # set image
#         self.img_display.setImage(self.color_current_img)
#         self.view_box.setRange(QRectF(0, 0, self.img_display.width(), self.img_display.height()), padding=0)
#         self.init_roi()

'''########## 2. QPoxyStyle #############'''
def create_icon_by_color(color):
    pixmap = QtGui.QPixmap(256, 256)
    pixmap.fill(color)
    return QtGui.QIcon(pixmap)

class TitleProxyStyle(QtWidgets.QProxyStyle):
    def drawComplexControl(self, control, option, painter, widget=None):
        if control == QtWidgets.QStyle.CC_TitleBar:
            if hasattr(widget, "titleColor"):
                color = widget.titleColor
                if color.isValid():
                    option.palette.setBrush(
                        QtGui.QPalette.Highlight, QtGui.QColor(color)
                    )
            option.icon = create_icon_by_color(QtGui.QColor("transparent"))
        super(TitleProxyStyle, self).drawComplexControl(
            control, option, painter, widget
        )

class mySubWin(QtWidgets.QMdiSubWindow):
    update_display_signal = pyqtSignal()

    def __init__(self, parent=None, flags=QtCore.Qt.Widget):
        super(mySubWin, self).__init__(parent, flags)
        style = TitleProxyStyle(self.style())
        self.setStyle(style)
        self._titleColor = QtGui.QColor()

        """ transparent window """
        # pg.setConfigOption('background', (0, 0, 0, 0))
        # pg.setConfigOption('foreground', 'w')
        # self.setStyleSheet("background-color: transparent; color: white;")
        # self._titleColor = QtGui.QColor("transparent")
        """ black window """
        pg.setConfigOption('background', (0, 0, 0, 255))
        pg.setConfigOption('foreground', 'w')
        self.setStyleSheet("background-color: black; color: white;")
        self.titleColor = QtGui.QColor("darkgray")
        self._titleColor = QtGui.QColor('#2F3337')

        self.init_UI()
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("myappid")

    def init_UI(self):
        self.setOption(True, QMdiSubWindow.RubberBandResize)
        self.resize(400, 400)

        self.name = ''
        self.contrast = 200
        self.opacity = 100
        self.pallet = 0                       # pallet option (0: Gray; 1: Color)
        self.filter = [False, False, False]   # filter option (0: Reverse; 1: PlaneFit)
        self.color_map_index = 83             # ho rainbow

        self.myimg = myImages()

        # Plot widgets |
        self.graphicsView = pg.GraphicsLayoutWidget(self)
        self.graphicsView.ci.layout.setContentsMargins(0, 0, 0, 0)     # eliminate the border
        self.graphicsView.ci.layout.setSpacing(0)                      # eliminate the border
        # self.graphicsView.ci.setBorder((255,0,0,255))
        self.setWidget(self.graphicsView)
        self.plot = self.graphicsView.addPlot(row=0, col=0)

        # self.view_box.setRange(QRectF(-512, -512, 512, 512), padding=0)
        # self.view_box.setLimits(xMin=-512, xMax=512, yMin=-512, yMax=512, \
        #                         minXRange=3, maxXRange=1024, minYRange=3, maxYRange=1024)
        #
        # self.view_box.setCursor(Qt.CrossCursor)
        # self.view_box.setMouseMode(self.view_box.PanMode)
        self.view_box = self.plot.vb
        self.view_box.setAspectLocked(True)
        self.view_box.setMouseEnabled(x=True, y=True)
        # self.viewbox.disableAutoRange()
        # self.viewbox.hideButtons()
        self.view_box.setRange(xRange=(0, 100), yRange=(0, 100), padding=0)

        self.img_display = pg.ImageItem()
        self.view_box.addItem(self.img_display)
        self.plot.showAxes(False, showValues=(True, False, False, True))

        ''' ColorBar '''
        self.colorBar = self.plot.addColorBar(self.img_display, width=18, label=None, colorMap='CET-L9',
                                              values=(0, 30_000), interactive=False)

        # bar = pg.ColorBarItem(
        #     values = (0, 30_000),
        #     colorMap='CET-L4',
        #     label='horizontal color bar',
        #     limits = (0, None),
        #     rounding=1000,
        #     orientation = 'h',
        #     pen='#8888FF', hoverPen='#EEEEFF', hoverBrush='#EEEEFF80'
        # )
        ''' pgcolorbar '''
        # showHistogram = True
        # self.colorBar = ColorLegendItem(
        #     imageItem=self.img_display,
        #     showHistogram=showHistogram,
        #     histHeightPercentile=99.0, # Uncomment to discard the outliers in the histogram height
        #     label='Random data')
        # self.colorBar.setMinimumHeight(60)
        # self.graphicsView.addItem(self.colorBar, 0, 1)

        # ROI | define pens
        blue_pen = pg.mkPen((100, 200, 255, 255), width=1)
        green_pen = pg.mkPen((150, 220, 0, 255), width=1)
        yellow_pen = pg.mkPen((255, 234, 0, 255), width=2)
        purple_pen = pg.mkPen((220, 180, 255, 255), width=2)

        # ROI | image box
        self.roi = pg.ROI([0, 0], [10, 10], resizable=False, removable=True, handlePen=(255, 255, 255, 0))
        self.roi.hide()

        # ROI | Line Cut
        self.linecut = pg.LineSegmentROI([[0, 0], [100, 100]], pen=green_pen)
        self.linecut.rotateSnapAngle = 0.01
        self.linecut.setZValue(11)
        self.view_box.addItem(self.linecut)
        self.linecut.removeHandle(0)
        self.linecut.addTranslateHandle(pos=[0, 0], index=0)
        self.linecut.getHandles()[0].pen = purple_pen
        self.linecut.getHandles()[0].radius = 10
        # self.linecut.getHandles()[1].pen = blue_pen
        # self.linecut.getHandles()[1].radius = 10
        self.linecut.hide()

    def init_data(self, data, child_index):
        self.data = data
        # self.raw_img = self.myimg.prepare_data(
        #     self.myimg.partial_renormalize(self.data[parent_index].child_data[self.energy_index]))
        self.raw_img = self.myimg.prepare_data(self.myimg.partial_renormalize(self.data.data[child_index]))
        self.current_img = copy.deepcopy(self.raw_img)
        self.update_display_signal.emit()

    # ROI | image box
    def init_roi(self):
        ''' ROI needed for rotate option '''
        self.img_display.setParentItem(self.view_box)
        self.view_box.removeItem(self.roi)
        self.roi = pg.ROI([0, 0], [self.img_display.width(), self.img_display.height()], resizable=False,
                          removable=True, handlePen=(255, 255, 255, 0))
        self.roi.addRotateHandle([1, 0], [0.5, 0.5])
        self.roi.addRotateHandle([0, 1], [0.5, 0.5])
        self.view_box.addItem(self.roi)
        self.img_display.setParentItem(self.roi)

    @property
    def titleColor(self):
        return self._titleColor

    @titleColor.setter
    def titleColor(self, color):
        self._titleColor = color
        self.update()

    # CBar all the same button slot | update display image
    def update_display(self):
        '''Update image based on user selected filter and colormap.'''
        if self.pallet == 0:
            psudo_gray_img = cv.cvtColor(self.current_img, cv.COLOR_GRAY2BGR)
            self.color_current_img = psudo_gray_img
            if self.filter[0]:
                cmap = self.myimg.reverse_colormap('gray')
            else:
                cmap = 'gray'
            self.colorBar.setColorMap(cmap)
            # self.colorBar.autoScaleFromImage()
        elif self.pallet == 1:
            color_img = self.myimg.color_map(self.current_img, self.color_map_index)
            self.color_current_img = color_img
            # self.colorBar.setLevels(low=color_img.min(), high=color_img.min())
            if self.filter[0]:
                cmap = self.myimg.colormap_dict_cm[self.color_map_index]
                cmap = self.myimg.reverse_colormap(cmap)
            else:
                cmap = self.myimg.colormap_dict_cm[self.color_map_index]
            self.colorBar.setColorMap(cmap)

        # set contrast
        img = img_as_float(self.color_current_img)
        self.color_current_img = exposure.adjust_gamma(img, self.contrast / 200)
        # set opacity
        self.img_display.setOpacity(self.opacity / 100)
        # set image
        self.img_display.setImage(self.color_current_img)
        self.view_box.setRange(QRectF(0, 0, self.img_display.width(), self.img_display.height()), padding=0)
        self.init_roi()

'''########## 3. Customize title bar #############'''
# class MyBar(QWidget):
#
#     def __init__(self, parent):
#         super(MyBar, self).__init__()
#         self.parent = parent
#         print(self.parent.width())
#         self.layout = QHBoxLayout()
#         self.layout.setContentsMargins(0,0,0,0)
#         self.title = QLabel("My Own Bar")
#
#         btn_size = 35
#
#         self.btn_close = QPushButton("x")
#         self.btn_close.clicked.connect(self.btn_close_clicked)
#         self.btn_close.setFixedSize(btn_size,btn_size)
#         self.btn_close.setStyleSheet("background-color: red;")
#
#         self.btn_min = QPushButton("-")
#         self.btn_min.clicked.connect(self.btn_min_clicked)
#         self.btn_min.setFixedSize(btn_size, btn_size)
#         self.btn_min.setStyleSheet("background-color: gray;")
#
#         self.btn_max = QPushButton("+")
#         self.btn_max.clicked.connect(self.btn_max_clicked)
#         self.btn_max.setFixedSize(btn_size, btn_size)
#         self.btn_max.setStyleSheet("background-color: gray;")
#
#         self.title.setFixedHeight(35)
#         # self.title.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
#         self.title.setAlignment(Qt.AlignLeft)
#         self.title.setIndent(10)
#         self.layout.addWidget(self.title)
#         self.layout.addWidget(self.btn_min)
#         self.layout.addWidget(self.btn_max)
#         self.layout.addWidget(self.btn_close)
#
#         self.title.setStyleSheet("""
#             background-color: black;
#             color: white;
#         """)
#         self.setLayout(self.layout)
#
#         self.start = QPoint(0, 0)
#         self.pressing = False
#
#     def resizeEvent(self, QResizeEvent):
#         super(MyBar, self).resizeEvent(QResizeEvent)
#         self.title.setFixedWidth(self.parent.width())
#
#     def mousePressEvent(self, event):
#         self.start = self.mapToGlobal(event.pos())
#         self.pressing = True
#
#     def mouseMoveEvent(self, event):
#         if self.pressing:
#             self.end = self.mapToGlobal(event.pos())
#             self.movement = self.end-self.start
#             self.parent.setGeometry(self.mapToGlobal(self.movement).x(),
#                                 self.mapToGlobal(self.movement).y(),
#                                 self.parent.width(),
#                                 self.parent.height())
#             self.start = self.end
#
#     def mouseReleaseEvent(self, QMouseEvent):
#         self.pressing = False
#
#     def btn_close_clicked(self):
#         self.parent.close()
#
#     def btn_max_clicked(self):
#         self.parent.showMaximized()
#
#     def btn_min_clicked(self):
#         self.parent.showMinimized()
#
# class mySubWin(QMdiSubWindow):
#     update_display_signal = pyqtSignal()
#
#     def __init__(self):
#         super(mySubWin, self).__init__()
#         self.init_UI()
#         ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("myappid")
#
#     def init_titlebar(self):
#         self.layout = QVBoxLayout()
#         self.setLayout(self.layout)
#         self.titlebar = MyBar(self)
#         self.layout.addWidget(self.titlebar)
#         self.layout.setContentsMargins(0, 0, 0, 0)
#         self.layout.addStretch(-1)
#         self.setWindowFlags(Qt.FramelessWindowHint)
#         self.setMinimumSize(400, 400)
#         self.pressing = False
#
#     def init_UI(self):
#         self.resize(800, 800)
#         self.init_titlebar()
#         # self.setOption(True, QMdiSubWindow.RubberBandResize)
#         # self.showSystemMenu()
#
#
#         self.contrast = 200
#         self.opacity = 100
#         self.pallet = 0
#         self.filter = [False, False, True]
#         self.color_map_index = 51
#
#         self.myimg = myImages()
#
#         # Plot widgets |
#         self.graphicsView = pg.GraphicsLayoutWidget(self)
#         self.graphicsView.setMinimumSize(400, 400)
#         self.layout.addWidget(self.graphicsView)
#         self.plot = self.graphicsView.addPlot(row=0, col=0)
#
#         # self.view_box.setRange(QRectF(-512, -512, 512, 512), padding=0)
#         # self.view_box.setLimits(xMin=-512, xMax=512, yMin=-512, yMax=512, \
#         #                         minXRange=3, maxXRange=1024, minYRange=3, maxYRange=1024)
#         #
#         # self.view_box.setCursor(Qt.CrossCursor)
#         # self.view_box.setMouseMode(self.view_box.PanMode)
#         self.view_box = self.plot.vb
#         self.view_box.setAspectLocked(True)
#         self.view_box.setMouseEnabled(x=True, y=True)
#         # self.viewbox.disableAutoRange()
#         # self.viewbox.hideButtons()
#         self.view_box.setRange(xRange=(0, 100), yRange=(0, 100), padding=0)
#
#         self.img_display = pg.ImageItem()
#         self.view_box.addItem(self.img_display)
#         self.plot.showAxes(False, showValues=(True, False, False, True))
#
#         ''' ColorBar '''
#         self.colorBar = self.plot.addColorBar(self.img_display, width=18, label=None, colorMap='CET-L9', values=(0, 30_000), interactive=False)
#
#         # bar = pg.ColorBarItem(
#         #     values = (0, 30_000),
#         #     colorMap='CET-L4',
#         #     label='horizontal color bar',
#         #     limits = (0, None),
#         #     rounding=1000,
#         #     orientation = 'h',
#         #     pen='#8888FF', hoverPen='#EEEEFF', hoverBrush='#EEEEFF80'
#         # )
#         ''' pgcolorbar '''
#         # showHistogram = True
#         # self.colorBar = ColorLegendItem(
#         #     imageItem=self.img_display,
#         #     showHistogram=showHistogram,
#         #     histHeightPercentile=99.0, # Uncomment to discard the outliers in the histogram height
#         #     label='Random data')
#         # self.colorBar.setMinimumHeight(60)
#         # self.graphicsView.addItem(self.colorBar, 0, 1)
#
#         # ROI | define pens
#         blue_pen = pg.mkPen((100, 200, 255, 255), width=1)
#         green_pen = pg.mkPen((150, 220, 0, 255), width=1)
#         yellow_pen = pg.mkPen((255, 234, 0, 255), width=2)
#         purple_pen = pg.mkPen((220, 180, 255, 255), width=2)
#
#         # ROI | image box
#         self.roi = pg.ROI([0, 0], [10, 10], resizable=False, removable=True, handlePen=(255, 255, 255, 0))
#         self.roi.hide()
#
#         # ROI | Line Cut
#         self.linecut = pg.LineSegmentROI([[0, 0], [100, 100]], pen=green_pen)
#         self.linecut.rotateSnapAngle = 0.01
#         self.linecut.setZValue(11)
#         self.view_box.addItem(self.linecut)
#         self.linecut.removeHandle(0)
#         self.linecut.addTranslateHandle(pos=[0, 0], index=0)
#         self.linecut.getHandles()[0].pen = purple_pen
#         self.linecut.getHandles()[0].radius = 10
#         # self.linecut.getHandles()[1].pen = blue_pen
#         # self.linecut.getHandles()[1].radius = 10
#         self.linecut.hide()
#
#     def init_data(self, data, child_index):
#         self.data = data
#         # self.raw_img = self.myimg.prepare_data(
#         #     self.myimg.partial_renormalize(self.data[parent_index].child_data[self.energy_index]))
#         self.raw_img = self.myimg.prepare_data(self.myimg.partial_renormalize(self.data.data[child_index]))
#         self.current_img = copy.deepcopy(self.raw_img)
#         self.update_display_signal.emit()
#
#     # ROI | image box
#     def init_roi(self):
#         ''' ROI needed for rotate option '''
#         self.img_display.setParentItem(self.view_box)
#         self.view_box.removeItem(self.roi)
#         self.roi = pg.ROI([0, 0], [self.img_display.width(), self.img_display.height()], resizable=False,
#                           removable=True, handlePen=(255, 255, 255, 0))
#         self.roi.addRotateHandle([1, 0], [0.5, 0.5])
#         self.roi.addRotateHandle([0, 1], [0.5, 0.5])
#         self.view_box.addItem(self.roi)
#         self.img_display.setParentItem(self.roi)

"""============= Quick View window ========================"""
class myQuickViewWindow(QMainWindow, Ui_QuickView):
    # Common signal
    close_signal = pyqtSignal()
    list_changed_signal = pyqtSignal()
    update_display_signal = pyqtSignal()

    count = 0

    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.init_UI()
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("myappid")

    def init_UI(self):
        # self.move(850, 50)         # Init ui position
        self.showMaximized()

        # 设置窗体无边框
        # self.setWindowFlags(Qt.FramelessWindowHint)
        # self.setWindowFlags(Qt.WindowSystemMenuHint)
        # 设置背景透明
        # self.setAttribute(Qt.WA_TranslucentBackground)
        # self.my_Qss()

        self.dir_path = ''
        # self.file_type = 0            # file visibility in dir, 0: (.spc); 1: (.dep)
        self.file_index = 0
        self.file_names = []            # expanded file names for internal use
        self.file_paths = []            # file paths according to file_names
        self.displayed_file_names = []  # folded file names in Data listWidget
        self.displayed_file_paths = []  # folded file paths in Data listWidget
        self.subwin_cmap_list = []  # list to  record all sub-windows' colormap index
        self.subwin_pallet_list = []  # list to record all sub-windows' pallet option

        self.cnfg = QSettings("config.ini", QSettings.IniFormat)  # Basic configuration module
        self.myimg = myImages()
        self.advPF = myPlaneFitWin()
        self.advIll = myIlluminationWin()
        self.makeMap = myMapWin()

        # toolButton | View Control
        self.init_colormap()

        # stateBar |
        self.stateTooltip = None
        # with open('resource/style/demo.qss', encoding='utf-8') as f:
        #     self.setStyleSheet(f.read())

        # menuBar |
        self.menu = self.menuBar()
        self.menu.addAction("New")
        self.menu.addAction("Cascade")
        self.menu.addAction("Tile")
        self.menu.addAction("Close all")
        self.menu.addAction("Close active")
        self.menu.addAction("Adv Plane fit")
        self.menu.addAction("Adv Illumination")
        self.menu.addAction("Make a map")
        self.menu.addAction("Make a fig")
        self.menu.triggered[QAction].connect(self.windowAction)

        # pushButton | File list
        self.pushButton_Open.clicked.connect(self.open_file)
        self.pushButton_Refresh.clicked.connect(self.refresh_list)
        self.pushButton_Previous.clicked.connect(lambda: self.select_file(0))
        self.pushButton_Next.clicked.connect(lambda: self.select_file(1))
        self.pushButton_ResetContrast.clicked.connect(lambda: self.reset_pallet(0))
        self.pushButton_ResetOpacity.clicked.connect(lambda: self.reset_pallet(1))
        self.pushButton_LineCut.toggled.connect(self.open_linecut)
        self.pushButton_CBarAll.toggled.connect(self.show_all_colorbar)
        self.pushButton_sameCBar.toggled.connect(self.same_colorbar)
        self.pushButton_ResetSize.clicked.connect(lambda: self.resize_all(0, 400))

        # scrollBar |
        self.scrollBar_Opacity.valueChanged.connect(self.update_opacity)
        self.scrollBar_Contrast.valueChanged.connect(self.update_contrast)
        self.scrollBar_Size.valueChanged[int].connect(ft.partial(self.resize_all, 1))
        self.scrollBar_Opacity.setStyle(HollowHandleStyle())
        self.scrollBar_Contrast.setStyle(HollowHandleStyle())
        self.scrollBar_Size.setStyle(HollowHandleStyle())

        # pushButton | View Control
        self.pushButton_Rotate.clicked.connect(self.rotate)
        self.pushButton_FullView.clicked.connect(self.full_view)
        self.pushButton_Colorbar.toggled.connect(self.show_colorbar)

        # radioButton | View Control
        self.pallet_group = QButtonGroup()
        self.pallet_group.addButton(self.radioButton_Color, 0)
        self.pallet_group.addButton(self.radioButton_Gray, 1)
        self.pallet_group.buttonToggled[int, bool].connect(self.pallet_changed)

        ''' checkBox setup '''
        # checkBox | View Control
        # self.filter_group = QButtonGroup()
        # self.filter_group.addButton(self.checkBox_Reverse, 0)
        # self.filter_group.addButton(self.checkBox_Illuminated, 1)
        # self.filter_group.addButton(self.checkBox_PlaneFit, 2)
        # self.filter_group.setExclusive(False)
        # self.filter_group.buttonToggled[int, bool].connect(self.filter_changed)

        ''' pushButton setup '''
        # pushButton | View Control
        self.filter_group = QButtonGroup()
        self.filter_group.addButton(self.pushButton_Reverse, 0)
        self.filter_group.addButton(self.pushButton_Illuminated, 1)
        self.filter_group.addButton(self.pushButton_PlaneFit, 2)
        self.filter_group.setExclusive(False)
        self.filter_group.buttonToggled[int, bool].connect(self.filter_changed)

        # toolButton | View Control
        self.init_colormap()

        # signals |
        self.mdiArea.subWindowActivated.connect(self.focus_changed)

        # self.toolBar = QToolBar()
        # self.addToolBar(self.toolBar)
        # self.toolBar.addAction("新建")
        # self.toolBar.addAction("级联")
        # self.toolBar.addAction("平铺")
        # self.toolBar.addAction("关闭全部")
        # self.toolBar.addAction("关闭活动窗口")
        # self.toolBar.addAction("测试")
        # self.toolBar.actionTriggered[QAction].connect(self.windowAction)

        # listWidget |
        self.listWidget.setDragEnabled(True)
        self.listWidget.setDragDropOverwriteMode(False)
        self.listWidget.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.listWidget.setDefaultDropAction(Qt.MoveAction)

        self.listWidget.setContextMenuPolicy(Qt.CustomContextMenu)
        self.listWidget.customContextMenuRequested[QtCore.QPoint].connect(self.rightMenuShow)

        self.listWidget.itemDoubleClicked.connect(lambda: self.file_changed(0))
        # self.listWidget.itemClicked.connect(lambda: self.file_changed(1))

        # keyboard event |
        QShortcut(QtGui.QKeySequence('Up', ), self, lambda: self.select_file(0))
        QShortcut(QtGui.QKeySequence('Down', ), self, lambda: self.select_file(1))
        QShortcut(QtGui.QKeySequence('Left', ), self, lambda: self.select_file(0))
        QShortcut(QtGui.QKeySequence('Right', ), self, lambda: self.select_file(1))

    # Update current sub-window variable
    def focus_changed(self, subwin):
        self.subwin = subwin
        if isinstance(subwin, mySubWin):
            self.load_subwin_status()

    # Load subwin palatte status when activated
    def load_subwin_status(self):
        self.scrollBar_Contrast.setValue(self.subwin.contrast)
        self.scrollBar_Opacity.setValue(self.subwin.opacity)
        self.radioButton_Color.setChecked(self.subwin.pallet)
        self.radioButton_Gray.setChecked(not self.subwin.pallet)

        ''' checkBox setup '''
        # self.filter_group.buttonToggled[int, bool].disconnect(self.filter_changed)
        # if self.subwin.filter[0]:
        #     self.checkBox_Reverse.setChecked(2)
        # elif not self.subwin.filter[0]:
        #     self.checkBox_Reverse.setChecked(0)
        # if self.subwin.filter[1] and (not self.subwin.filter[2]):
        #     self.checkBox_PlaneFit.setChecked(0)
        #     self.checkBox_Illuminated.setChecked(2)
        # elif (not self.subwin.filter[1]) and self.subwin.filter[2]:
        #     self.checkBox_Illuminated.setChecked(0)
        #     self.checkBox_PlaneFit.setChecked(2)
        # elif (not self.subwin.filter[1]) and (not self.subwin.filter[2]):
        #     self.checkBox_Illuminated.setChecked(0)
        #     self.checkBox_PlaneFit.setChecked(0)
        # self.filter_group.buttonToggled[int, bool].connect(self.filter_changed)

        ''' pushButton setup '''
        self.filter_group.buttonToggled[int, bool].disconnect(self.filter_changed)
        if self.subwin.filter[0]:
            self.pushButton_Reverse.setChecked(2)
        elif not self.subwin.filter[0]:
            self.pushButton_Reverse.setChecked(0)
        if self.subwin.filter[1] and (not self.subwin.filter[2]):
            self.pushButton_PlaneFit.setChecked(0)
            self.pushButton_Illuminated.setChecked(2)
        elif (not self.subwin.filter[1]) and self.subwin.filter[2]:
            self.pushButton_Illuminated.setChecked(0)
            self.pushButton_PlaneFit.setChecked(2)
        elif (not self.subwin.filter[1]) and (not self.subwin.filter[2]):
            self.pushButton_Illuminated.setChecked(0)
            self.pushButton_PlaneFit.setChecked(0)
        self.filter_group.buttonToggled[int, bool].connect(self.filter_changed)

    # Menu bar slot |
    def windowAction(self, q):
        # sub-window are never deleted in this version
        type = q.text()
        print("Triggered : %s" % type)
        if type == "New":
            subwin = self.new_subwin()
            subwin.show()
        elif type == "Cascade":
            self.mdiArea.cascadeSubWindows()
        elif type == "Tile":
            self.mdiArea.tileSubWindows()
            for win in self.mdiArea.subWindowList():
                win.view_box.setRange(
                    QRectF(0, 0, self.subwin.img_display.width(), self.subwin.img_display.height()), padding=0)
                win.resize(self.scrollBar_Size.value() - 30, self.scrollBar_Size.value())
        elif type == "Close all":
            self.mdiArea.closeAllSubWindows()
        elif type == "Close active":
            self.mdiArea.closeActiveSubWindow()
        elif type == "Adv Plane fit":
            self.advPF.init_data(self.subwin.raw_img)
            self.advPF.show()
            self.advPF.raise_()
        elif type == "Adv Illumination":
            self.advIll.init_data(self.subwin.raw_img)
            self.advIll.show()
            self.advIll.raise_()
        elif type == "Make a map":
            self.make_a_map()
        elif type == "Make a fig":
            self.make_a_fig()

    # plot all subwindow to a matplotlib sytle
    def make_a_fig(self):
        # get all images, names and colormaps
        img_list = [];
        name_list = [];
        cmap_list = [];
        for win in self.mdiArea.subWindowList():
            # print(win.windowTitle(), win.window().isVisible(), win.isShaded())
            img_list.append(self.dummy_plt(win.img_display.image))
            name_list.append(win.windowTitle().replace('\t','')) if win.windowTitle().find('\t') == 0 else name_list.append(win.windowTitle())
            if win.color_map_index != 83:
                cmap_list.append(self.myimg.colormap_dict_name[win.color_map_index])
            elif win.color_map_index == 83:
                cmap_list.append(self.get_ho_rrainbow())

        # determine the row and col of the fig
        row = int(np.sqrt(len(self.mdiArea.subWindowList())))
        col = len(self.mdiArea.subWindowList()) // row if len(self.mdiArea.subWindowList()) % row == 0 else len(
            self.mdiArea.subWindowList()) // row + 1

        # build a fig
        fig, axs = plt.subplots(nrows=row, ncols=col, figsize=(9, 6),
                                subplot_kw={'xticks': [], 'yticks': []})

        # plot images and hide border
        for ax, img, name, cmap in zip(axs.flat, img_list, name_list, cmap_list):
            ax.imshow(img, cmap=cmap)
            ax.set_title(name)
            ax.spines['top'].set_visible(False)
            ax.spines['right'].set_visible(False)
            ax.spines['bottom'].set_visible(False)
            ax.spines['left'].set_visible(False)

        # delete border of spare axes
        if len(img_list) < row * col:
            dummy = row * col - len(img_list)
            for i in range(dummy):
                ax = axs.flat[::-1][i]
                ax.spines['top'].set_visible(False)
                ax.spines['right'].set_visible(False)
                ax.spines['bottom'].set_visible(False)
                ax.spines['left'].set_visible(False)

        # show figure window
        plt.tight_layout()
        plt.show()

    # get ho-group rainbow colormap
    def get_ho_rrainbow(self):
        color_list = np.loadtxt(r".\model\RAINBOW.PAL")
        colors = []
        for i, color in enumerate(color_list):
            colors.append((color[0], color[1], color[2]))
        rrainbow = LinearSegmentedColormap.from_list('cmap', colors[::-1], 256)
        return rrainbow

    # find correct direction for plotting in plt window
    def dummy_plt(self, img):
        if img.ndim == 3:
            for i in range(img.shape[2]):
                img[:, :, i] = np.flipud(img[:, :, i].T)
        if img.ndim == 2:
            img = np.flipud(img.T)
        return img

    def init_subwin(self, subwin):
        subwin.setWindowTitle("subWindow %d" % self.count)
        subwin.resize(370, 400)
        # subwin.setOption(QMdiSubWindow.RubberBandResize) # make sub-window transparent when resizing
        subwin.setOption(QMdiSubWindow.RubberBandMove)     # make sub-window traparent when moving

        ## Create image items
        data = np.fromfunction(lambda i, j: (1+0.3*np.sin(i)) * (i)**2 + (j)**2, (100, 100))
        noisy_data = data * (1 + 0.2 * np.random.random(data.shape) )
        noisy_transposed = noisy_data.transpose()

        subwin.img_display.setImage(data)
        ''' pgcolorbar '''
        # subwin.colorBar.autoScaleFromImage()

        self.mdiArea.addSubWindow(subwin)

    # Build a new sub-window (internal use for double click)
    def new_subwin(self):
        self.count = self.count + 1
        sub = mySubWin()
        self.init_subwin(sub)
        sub.init_roi()
        sub.update_display_signal.connect(self.update_display)
        return sub

    def show_statusbar(self):
        if self.stateTooltip == None:
            self.stateTooltip = StateTooltip('Loading data', 'Please wait...', self)
            self.stateTooltip.move(810, 320)
            self.stateTooltip.show()

    def hide_statusbar(self):
        if self.stateTooltip:
            self.stateTooltip.setContent('Data ready 😆')
            self.stateTooltip.setState(True)
            self.stateTooltip = None

    # Data List | open folder button slot
    def open_file(self):
        self.show_statusbar()
        self.dir_path = self.cnfg.value("CNFG/FILE_PATH", type=str)
        if os.path.exists(self.dir_path):
            aFile, filt = QFileDialog.getOpenFileName(self, "Open file", self.dir_path, "NSTM(*.nstm)")
        else:
            curDir = "E:/Code/2022oct/"
            # curDir = QDir.currentPath()
            aFile, filt = QFileDialog.getOpenFileName(self, "Open file", curDir, "NSTM(*.nstm)")

        dir, file = os.path.split(aFile)
        self.dir_path = dir

        self.file_paths.clear()
        self.file_names.clear()
        self.displayed_file_names.clear()
        self.displayed_file_paths.clear()
        self.listWidget.clear()

        for root, dirs, files in os.walk(self.dir_path, topdown=False):
            for file in files:
                if file[-5:] == ".nstm":
                    data_path = os.path.join(root, file)
                    data = MappingData(data_path)
                    self.displayed_file_names.append(file)
                    self.displayed_file_paths.append(data_path)
                    if data.child_num != 1:
                        for i in range(data.child_num):
                            self.displayed_file_paths.append(data.path)
                            self.displayed_file_names.append(data.child_name[i])
                    self.file_paths.append(data.path)
                    self.file_names.append(data.name)
                    for i in range(data.child_num):
                        self.file_paths.append(data.path)
                        self.file_names.append(data.child_name[i])

        if len(self.file_paths) <= 0:
            return

        self.lineEdit.setText(self.dir_path)
        self.listWidget.addItems(self.displayed_file_names)
        self.hide_statusbar()

    # Data List | data window list changed signal slot
    def refresh_list(self):
        # print("refresh!!!")
        self.file_paths.clear()
        self.file_names.clear()
        self.displayed_file_names.clear()
        self.displayed_file_paths.clear()

        for root, dirs, files in os.walk(self.dir_path, topdown=False):
            for file in files:
                if file[-5:] == ".nstm":
                    data_path = os.path.join(root, file)
                    data = MappingData(data_path)
                    self.displayed_file_names.append(file)
                    self.displayed_file_paths.append(data_path)
                    if data.child_num != 1:
                        for i in range(data.child_num):
                            self.displayed_file_paths.append(data.path)
                            self.displayed_file_names.append(data.child_name[i])
                    self.file_paths.append(data.path)
                    self.file_names.append(data.name)
                    for i in range(data.child_num):
                        self.file_paths.append(data.path)
                        self.file_names.append(data.child_name[i])

        if len(self.file_paths) <= 0:
            return

        self.listWidget.clear()
        self.listWidget.addItems(self.displayed_file_names)
        self.listWidget.setCurrentRow(self.file_index)

    # Data List | file selection changed / single click / double click slot / right click
    def file_changed(self, index):
        ''' Double click to open file in a new window.
            Single click / change selection to change selected data in top level window. '''
        if index == 0:    # double click slot

            if self.listWidget.count() > 0:
                self.file_index = self.listWidget.currentRow()

                # build a new data window
                data_window = self.new_subwin()
                self.mdiArea.setActiveSubWindow(data_window)
                self.subwin = data_window
                data_window.update_display_signal.connect(self.update_display)

                # get selected file
                item = self.listWidget.currentItem()
                name = item.text()
                data = MappingData(self.file_paths[self.file_names.index(item.text())])
                if name.find('_No') != -1 and data.child_num > 1:
                    child_index = self.get_child_index(name)
                else:
                    child_index = 0
                data_window.init_data(data, child_index)

                # add file to new window
                data_window.setWindowTitle(name)
                data_window.name = name
                data_window.show()

        elif index == 1:  # file selection changed / single click slot

            # get selected file
            item = self.listWidget.currentItem()
            name = item.text()
            data = MappingData(self.file_paths[self.file_names.index(item.text())])
            if name.find('_No') != -1 and data.child_num > 1:
                child_index = self.get_child_index(name)
            else:
                child_index = 0
            self.subwin.init_data(data, child_index)

            # add file to new window
            self.subwin.setWindowTitle(name)
            self.subwin.name = name
            self.mdiArea.setActiveSubWindow(self.subwin)

        elif index == 2:    # batch open

            if self.listWidget.count() > 0:

                self.file_index = self.listWidget.currentRow()

                items = self.listWidget.selectedItems()
                for item in items:
                    # get item name
                    name = item.text()

                    # build a new data window
                    data_window = self.new_subwin()
                    self.mdiArea.setActiveSubWindow(data_window)
                    self.subwin = data_window
                    data_window.update_display_signal.connect(self.update_display)

                    # get data
                    data = MappingData(self.file_paths[self.file_names.index(item.text())])
                    if name.find('_No') != -1 and data.child_num > 1:
                        child_index = self.get_child_index(name)
                    else:
                        child_index = 0
                    data_window.init_data(data, child_index)

                    # add file to new window
                    data_window.setWindowTitle(name)
                    data_window.name = name
                    data_window.show()

    # Data list | get selected data child index
    def get_child_index(self, name):
        if name.find('_No') != -1:
            child_index = int(name[-2:])
        return child_index

    # Data list | subwin data
    def get_current_child(self):
        name = self.subwin.windowTitle()
        data = self.subwin.data
        if name.find('_No') != -1 and data.child_num > 1:
            child_index = self.get_child_index(name)
        else:
            child_index = 0
        return data, child_index

    # Data List | file type in comboBox changed slot
    def select_file(self, index):
        if index == 0:  # previous
            if self.listWidget.currentRow() - 1 == -1:
                self.listWidget.setCurrentRow(len(self.displayed_file_names) - 1)
            else:
                self.listWidget.setCurrentRow(self.listWidget.currentRow() - 1)
        elif index == 1:  # next
            if self.listWidget.currentRow() + 1 == len(self.displayed_file_names):
                self.listWidget.setCurrentRow(0)
            else:
                self.listWidget.setCurrentRow(self.listWidget.currentRow() + 1)
        self.file_index = self.listWidget.currentRow()
        self.file_changed(1)

    # Data List | right click menu
    def rightMenuShow(self):
        rightMenu = QMenu(self.listWidget)
        openBatchAction = QAction("Open", self, triggered=self.file_changed(2))
        rightMenu.addAction(openBatchAction)
        rightMenu.exec_(QtGui.QCursor.pos())

    # !!! not used
    # Menu | add to current window action slot
    def add2window(self):
        # get selected file index
        items = self.listWidget.selectedItems()
        add_index = []
        add_name = []
        for item in items:
            add_index.append(self.file_names.index(item.text()))
            add_name.append(item.text())
        # self.file_index = add_index[-1]

        for item in self.listWidget.selectedItems():
            data = MappingData(self.file_paths[self.file_names.index(item.text())])
            for i in range(data.child_num):
                add_name.append(data.child_name[i])

        self.previous_window.listWidget.addItems(add_name)
        self.previous_window.refresh_list(0)

    # !!! not used
    # Menu | open  to another window action slot
    def open2window(self):
        # get selected file index
        items = self.listWidget.selectedItems()
        add_index = []
        add_name = []
        for item in items:
            add_index.append(self.file_names.index(item.text()))
            add_name.append(item.text())
        # self.file_index = add_index[-1]

        for item in self.listWidget.selectedItems():
            data = MappingData(self.file_paths[self.file_names.index(item.text())])
            for i in range(data.child_num):
                add_name.append(data.child_name[i])

        # open files in new data window
        data_window = myGraphWindow(self.file_names, self.file_paths)
        data_window.operating_mode_1 = self.operating_mode_1
        data_window.operating_mode_2 = self.operating_mode_2
        data_window.part_type = self.part_type
        self.windows.append(data_window)
        self.windows[-1].listWidget.list_changed_signal.connect(self.refresh_list)
        self.windows[-1].listWidget.addItems(add_name)
        self.windows[-1].set_list_checked(0)
        self.windows[-1].refresh_list(0)
        self.windows[-1].show()

    # Opacity scrollBar slot |
    def update_opacity(self, opacity):
        ''' Change opacity of imageItem '''
        self.subwin.opacity = opacity
        self.subwin.update_display_signal.emit()

    # Contrast scrollBar slot |
    def update_contrast(self, contrast):
        ''' Change contrast of imageItem '''
        self.subwin.contrast = contrast
        self.subwin.update_display_signal.emit()

    # Resize all button and scrollBar slot |
    def resize_all(self, index, size):
        if index == 0:  # reset
            for win in self.mdiArea.subWindowList():
                win.resize(370, 400)
            self.scrollBar_Size.setValue(400)
        elif index == 1: # resize
            for win in self.mdiArea.subWindowList():
                win.resize(size-30, size)

    # Reset button slot | 0: contrast; 1: opacity
    def reset_pallet(self, index):
        if index == 0:
            self.scrollBar_Contrast.setValue(200)
        else:
            self.scrollBar_Opacity.setValue(100)

    # reset button slot | make image full view
    def full_view(self):
        '''Zoom in to whole image. '''
        self.subwin.view_box.setRange(QRectF(0, 0, self.subwin.img_display.width(), self.subwin.img_display.height()), padding=0)

    # rotate button slot | rotate
    def rotate(self):
        '''Rotate image 90° counterclockwise.'''
        self.subwin.roi.rotate(90, center=[0.5, 0.5])

    # pallet radioButton slot | gray, color
    def pallet_changed(self, status):
        '''Change color map for displayed image: afm-hot or gray.'''
        if status:
            if self.radioButton_Gray.isChecked():
                pallet = 0
            elif self.radioButton_Color.isChecked():
                pallet = 1
            self.subwin.pallet = pallet
            self.subwin.update_display_signal.emit()

    # Color map slot | multiple colormap
    def color_map(self, index):
        self.subwin.color_map_index = index
        self.subwin.update_display_signal.emit()

    # CBar pushButton slot | show/hide current subwin colorbar
    def show_colorbar(self, show):
        self.subwin.colorbar_visible = show
        if show:
            self.subwin.colorBar.vb.setFixedWidth(18)
            self.subwin.colorBar.show()
        else:
            self.subwin.colorBar.vb.setFixedWidth(1)  # zero gives error
            self.subwin.colorBar.hide()

    # CBarAll pushButton slot | show/hide all subwins' colorbar
    def show_all_colorbar(self, show):
        for win in self.mdiArea.subWindowList():
            win.colorbar_visible = show
            if show:
                win.colorBar.vb.setFixedWidth(24)
                win.colorBar.show()
            else:
                win.colorBar.vb.setFixedWidth(1)  # zero gives error
                win.colorBar.hide()

    # CBarAllTheSame pushbutton slot | keep all subwins' cbar the same
    def same_colorbar(self, ifsame):
        if ifsame:
            self.subwin_cmap_list.clear()
            self.subwin_pallet_list.clear()
            for win in self.mdiArea.subWindowList():
                self.subwin_cmap_list.append(win.color_map_index)
                self.subwin_pallet_list.append(win.pallet)
                win.color_map_index = self.subwin.color_map_index
                win.pallet = self.subwin.pallet
                win.update_display()
        else:
            for ind, win in enumerate(self.mdiArea.subWindowList()):
                win.color_map_index = self.subwin_cmap_list[ind]
                win.pallet = self.subwin_pallet_list[ind]
                win.update_display()

    # filter checkBox slot | reverse, Illuminated and Plane fit
    def filter_changed(self, index, status):
        '''Process image based on checkBox signal: Reverse, Illuminated and Plane fit.'''
        ''' checkBox setup '''
        # # Set mutual exclusion of Illuminated and Plane fit
        # if self.checkBox_Illuminated.isChecked():
        #     if index == 2 and status:
        #         self.checkBox_Illuminated.setChecked(False)
        #         self.checkBox_PlaneFit.setChecked(True)
        #     else:
        #         self.checkBox_Illuminated.setChecked(True)
        #         self.checkBox_PlaneFit.setChecked(False)
        # 
        # if self.checkBox_PlaneFit.isChecked():
        #     if index == 1 and status:
        #         self.checkBox_PlaneFit.setChecked(False)
        #         self.checkBox_Illuminated.setChecked(True)
        #     else:
        #         self.checkBox_PlaneFit.setChecked(True)
        #         self.checkBox_Illuminated.setChecked(False)
        # 
        # # CheckBox status variable
        # if_reverse = self.checkBox_Reverse.isChecked()
        # if_illuminated = self.checkBox_Illuminated.isChecked()
        # if_plane_fit = self.checkBox_PlaneFit.isChecked()
        # self.subwin.filter = [if_reverse, if_illuminated, if_plane_fit]

        ''' pushButton setup '''
        # Set mutual exclusion of Illuminated and Plane fit
        if self.pushButton_Illuminated.isChecked():
            if index == 2 and status:
                self.pushButton_Illuminated.setChecked(False)
                self.pushButton_PlaneFit.setChecked(True)
            else:
                self.pushButton_Illuminated.setChecked(True)
                self.pushButton_PlaneFit.setChecked(False)

        if self.pushButton_PlaneFit.isChecked():
            if index == 1 and status:
                self.pushButton_PlaneFit.setChecked(False)
                self.pushButton_Illuminated.setChecked(True)
            else:
                self.pushButton_PlaneFit.setChecked(True)
                self.pushButton_Illuminated.setChecked(False)

        # pushButton status variable
        if_reverse = self.pushButton_Reverse.isChecked()
        if_illuminated = self.pushButton_Illuminated.isChecked()
        if_plane_fit = self.pushButton_PlaneFit.isChecked()
        self.subwin.filter = [if_reverse, if_illuminated, if_plane_fit]

        # Get current selected display mode
        if if_reverse and (not if_plane_fit) and (not if_illuminated):
            reverse_gray_img = self.myimg.gray2reverse(self.subwin.raw_img)
            self.subwin.current_img = reverse_gray_img
        elif if_illuminated and (not if_plane_fit) and (not if_reverse):
            illuminated_img = self.myimg.illuminated(self.subwin.raw_img)
            self.subwin.current_img = illuminated_img
        elif if_plane_fit and (not if_illuminated) and (not if_reverse):
            planefit_img = self.myimg.plane_fit(self.subwin.raw_img)
            self.subwin.current_img = planefit_img
        elif if_plane_fit and if_illuminated and (not if_reverse):
            planefit_img = self.myimg.plane_fit(self.subwin.raw_img)
            illuminated_planefit_img = self.myimg.illuminated(planefit_img)
            self.subwin.current_img = illuminated_planefit_img
        elif if_reverse and if_plane_fit and (not if_illuminated):
            planefit_img = self.myimg.plane_fit(self.subwin.raw_img)
            reverse_planefit_img = self.myimg.gray2reverse(planefit_img)
            self.subwin.current_img = reverse_planefit_img
        elif if_reverse and if_illuminated and (not if_plane_fit):
            illuminated_img = self.myimg.illuminated(self.subwin.raw_img)
            revered_illuminated_img = self.myimg.gray2reverse(illuminated_img)
            self.subwin.current_img = revered_illuminated_img
        elif if_reverse and if_illuminated and if_plane_fit:
            planefit_img = self.myimg.plane_fit(self.subwin.raw_img)
            illuminated_planefit_img = self.myimg.illuminated(planefit_img)
            revered_illuminated_planefit_img = self.myimg.gray2reverse(illuminated_planefit_img)
            self.subwin.current_img = revered_illuminated_planefit_img
        elif (not if_reverse) and (not if_illuminated) and (not if_plane_fit):
            self.subwin.current_img = copy.deepcopy(self.subwin.raw_img)

        self.subwin.update_display_signal.emit()

    # update display image
    def update_display(self):
        '''Update image based on user selected filter and colormap.'''
        if self.subwin.pallet == 0:
            psudo_gray_img = cv.cvtColor(self.subwin.current_img, cv.COLOR_GRAY2BGR)
            self.subwin.color_current_img = psudo_gray_img
            if self.subwin.filter[0]:
                cmap = self.myimg.reverse_colormap(self.myimg.colormap_dict_cm[26])
            else:
                cmap = self.myimg.colormap_dict_cm[26]
            self.subwin.colorBar.setColorMap(cmap)
            # self.subwin.colorBar.autoScaleFromImage()
        elif self.subwin.pallet == 1:
            color_img = self.myimg.color_map(self.subwin.current_img, self.subwin.color_map_index)
            self.subwin.color_current_img = color_img
            # self.subwin.colorBar.setLevels(low=color_img.min(), high=color_img.min())
            if self.subwin.filter[0]:
                cmap = self.myimg.colormap_dict_cm[self.subwin.color_map_index]
                cmap = self.myimg.reverse_colormap(cmap)
            else:
                cmap = self.myimg.colormap_dict_cm[self.subwin.color_map_index]
            self.subwin.colorBar.setColorMap(cmap)

        # set contrast
        img = img_as_float(self.subwin.color_current_img)
        self.subwin.color_current_img = exposure.adjust_gamma(img, self.subwin.contrast / 200)
        # set opacity
        self.subwin.img_display.setOpacity(self.subwin.opacity / 100)
        # set image
        self.subwin.img_display.setImage(self.subwin.color_current_img)
        self.subwin.view_box.setRange(QRectF(0, 0, self.subwin.img_display.width(), self.subwin.img_display.height()), padding=0)
        self.subwin.init_roi()

    # toolButton | init colormap
    def init_colormap(self):
        self.colormap_menu = QMenu()

        self.User_No1 = self.colormap_menu.addMenu('User Dan.B')
        self.PU_Sequential = self.colormap_menu.addMenu('PU Sequential')
        self.Sequential_1 = self.colormap_menu.addMenu('Sequential(1)')
        self.Sequential_2 = self.colormap_menu.addMenu('Sequential(2)')
        self.Diverging = self.colormap_menu.addMenu('Diverging')
        self.Cyclic = self.colormap_menu.addMenu('Cyclic')
        self.Qualitative = self.colormap_menu.addMenu('Qualitative')
        self.Miscellaneous = self.colormap_menu.addMenu('Miscellaneous')

        self.viridis = QAction("Viridis", self.PU_Sequential)
        self.plasma = QAction("Plasma", self.PU_Sequential)
        self.inferno = QAction("Inferno", self.PU_Sequential)
        self.magma = QAction("Magma", self.PU_Sequential)
        self.cividis = QAction("Cividis", self.PU_Sequential)

        self.PU_Sequential.addAction(self.viridis)
        self.PU_Sequential.addAction(self.plasma)
        self.PU_Sequential.addAction(self.inferno)
        self.PU_Sequential.addAction(self.magma)
        self.PU_Sequential.addAction(self.cividis)

        self.Greys = QAction("Greys", self.Sequential_1)
        self.Purples = QAction("Purples", self.Sequential_1)
        self.Blues = QAction("Blues", self.Sequential_1)
        self.Greens = QAction("Greens", self.Sequential_1)
        self.Oranges = QAction("Oranges", self.Sequential_1)
        self.Reds = QAction("Reds", self.Sequential_1)
        self.YlOrBr = QAction("YlOrBr", self.Sequential_1)
        self.YlOrRd = QAction("YlOrRd", self.Sequential_1)
        self.OrRd = QAction("OrRd", self.Sequential_1)
        self.PuRd = QAction("PuRd", self.Sequential_1)
        self.BuPu = QAction("BuPu", self.Sequential_1)
        self.GnBu = QAction("GnBu", self.Sequential_1)
        self.PuBu = QAction("PuBu", self.Sequential_1)
        self.YlGnBu = QAction("YlGnBu", self.Sequential_1)
        self.PuBuGn = QAction("PuBuGn", self.Sequential_1)
        self.BuGn = QAction("BuGn", self.Sequential_1)
        self.YlGn = QAction("YlGn", self.Sequential_1)

        self.Sequential_1.addAction(self.Greys)
        self.Sequential_1.addAction(self.Purples)
        self.Sequential_1.addAction(self.Blues)
        self.Sequential_1.addAction(self.Greens)
        self.Sequential_1.addAction(self.Oranges)
        self.Sequential_1.addAction(self.Reds)
        self.Sequential_1.addAction(self.YlOrBr)
        self.Sequential_1.addAction(self.YlOrRd)
        self.Sequential_1.addAction(self.OrRd)
        self.Sequential_1.addAction(self.PuRd)
        self.Sequential_1.addAction(self.BuPu)
        self.Sequential_1.addAction(self.GnBu)
        self.Sequential_1.addAction(self.PuBu)
        self.Sequential_1.addAction(self.YlGnBu)
        self.Sequential_1.addAction(self.PuBuGn)
        self.Sequential_1.addAction(self.BuGn)
        self.Sequential_1.addAction(self.YlGn)

        self.binary = QAction("binary", self.Sequential_2)
        self.gist_yarg = QAction("gist_yarg", self.Sequential_2)
        self.gist_gray = QAction("gist_gray", self.Sequential_2)
        self.gray = QAction("gray", self.Sequential_2)
        self.bone = QAction("bone", self.Sequential_2)
        self.pink = QAction("pink", self.Sequential_2)
        self.spring = QAction("spring", self.Sequential_2)
        self.summer = QAction("summer", self.Sequential_2)
        self.autumn = QAction("autumn", self.Sequential_2)
        self.winter = QAction("winter", self.Sequential_2)
        self.cool = QAction("cool", self.Sequential_2)
        self.Wistia = QAction("Wistia", self.Sequential_2)
        self.hot = QAction("hot", self.Sequential_2)
        self.afmhot = QAction("afmhot", self.Sequential_2)
        self.gist_heat = QAction("gist_heat", self.Sequential_2)
        self.copper = QAction("copper", self.Sequential_2)

        self.Sequential_2.addAction(self.binary)
        self.Sequential_2.addAction(self.gist_yarg)
        self.Sequential_2.addAction(self.gist_gray)
        self.Sequential_2.addAction(self.gray)
        self.Sequential_2.addAction(self.bone)
        self.Sequential_2.addAction(self.pink)
        self.Sequential_2.addAction(self.spring)
        self.Sequential_2.addAction(self.summer)
        self.Sequential_2.addAction(self.autumn)
        self.Sequential_2.addAction(self.winter)
        self.Sequential_2.addAction(self.cool)
        self.Sequential_2.addAction(self.Wistia)
        self.Sequential_2.addAction(self.hot)
        self.Sequential_2.addAction(self.afmhot)
        self.Sequential_2.addAction(self.gist_heat)
        self.Sequential_2.addAction(self.copper)

        self.PiYG = QAction("PiYG", self.Diverging)
        self.PRGn = QAction("PRGn", self.Diverging)
        self.BrBG = QAction("BrBG", self.Diverging)
        self.PuOr = QAction("PuOr", self.Diverging)
        self.RdGy = QAction("RdGy", self.Diverging)
        self.RdBu = QAction("RdBu", self.Diverging)
        self.RdYlBu = QAction("RdYlBu", self.Diverging)
        self.RdYlGn = QAction("RdYlGn", self.Diverging)
        self.Spectral = QAction("Spectral", self.Diverging)
        self.coolwarm = QAction("coolwarm", self.Diverging)
        self.bwr = QAction("bwr", self.Diverging)
        self.seismic = QAction("seismic", self.Diverging)

        self.Diverging.addAction(self.PiYG)
        self.Diverging.addAction(self.PRGn)
        self.Diverging.addAction(self.BrBG)
        self.Diverging.addAction(self.PuOr)
        self.Diverging.addAction(self.RdGy)
        self.Diverging.addAction(self.RdBu)
        self.Diverging.addAction(self.RdYlBu)
        self.Diverging.addAction(self.RdYlGn)
        self.Diverging.addAction(self.Spectral)
        self.Diverging.addAction(self.coolwarm)
        self.Diverging.addAction(self.bwr)
        self.Diverging.addAction(self.seismic)

        self.twilight = QAction("twilight", self.Cyclic)
        self.twilight_shifted = QAction("twilight_shifted", self.Cyclic)
        # self.hsv = QAction("hsv", self.Cyclic)

        self.Cyclic.addAction(self.twilight)
        self.Cyclic.addAction(self.twilight_shifted)
        # self.Cyclic.addAction(self.hsv)

        self.Pastel1 = QAction("Pastel1", self.Qualitative)
        self.Pastel2 = QAction("Pastel2", self.Qualitative)
        self.Paired = QAction("Paired", self.Qualitative)
        self.Accent = QAction("Accent", self.Qualitative)
        self.Dark2 = QAction("Dark2", self.Qualitative)
        self.Set1 = QAction("Set1", self.Qualitative)
        self.Set2 = QAction("Set2", self.Qualitative)
        self.Set3 = QAction("Set3", self.Qualitative)
        self.tab10 = QAction("tab10", self.Qualitative)
        self.tab20 = QAction("tab20", self.Qualitative)
        self.tab20b = QAction("tab20b", self.Qualitative)
        self.tab20c = QAction("tab20c", self.Qualitative)

        self.Qualitative.addAction(self.Pastel1)
        self.Qualitative.addAction(self.Pastel2)
        self.Qualitative.addAction(self.Paired)
        self.Qualitative.addAction(self.Accent)
        self.Qualitative.addAction(self.Dark2)
        self.Qualitative.addAction(self.Set1)
        self.Qualitative.addAction(self.Set2)
        self.Qualitative.addAction(self.Set3)
        self.Qualitative.addAction(self.tab10)
        self.Qualitative.addAction(self.tab20)
        self.Qualitative.addAction(self.tab20b)
        self.Qualitative.addAction(self.tab20c)

        self.flag = QAction("flag", self.Miscellaneous)
        self.prism = QAction("prism", self.Miscellaneous)
        self.gist_earth = QAction("gist_earth", self.Miscellaneous)
        self.terrain = QAction("terrain", self.Miscellaneous)
        self.gist_stern = QAction("gist_stern", self.Miscellaneous)
        self.gnuplot = QAction("gnuplot", self.Miscellaneous)
        self.gnuplot2 = QAction("gnuplot2", self.Miscellaneous)
        self.CMRmap = QAction("CMRmap", self.Miscellaneous)
        self.cubehelix = QAction("cubehelix", self.Miscellaneous)
        self.brg = QAction("brg", self.Miscellaneous)
        self.gist_rainbow = QAction("gist_rainbow", self.Miscellaneous)
        self.rainbow = QAction("rainbow", self.Miscellaneous)
        # self.jet = QAction("jet", self.Miscellaneous)
        self.turbo = QAction("turbo", self.Miscellaneous)
        self.nipy_spectral = QAction("nipy_spectral", self.Miscellaneous)
        self.gist_ncar = QAction("gist_ncar", self.Miscellaneous)

        self.Miscellaneous.addAction(self.flag)
        self.Miscellaneous.addAction(self.prism)
        self.Miscellaneous.addAction(self.gist_earth)
        self.Miscellaneous.addAction(self.terrain)
        self.Miscellaneous.addAction(self.gist_stern)
        self.Miscellaneous.addAction(self.gnuplot)
        self.Miscellaneous.addAction(self.gnuplot2)
        self.Miscellaneous.addAction(self.CMRmap)
        self.Miscellaneous.addAction(self.cubehelix)
        self.Miscellaneous.addAction(self.brg)
        self.Miscellaneous.addAction(self.gist_rainbow)
        self.Miscellaneous.addAction(self.rainbow)
        # self.Miscellaneous.addAction(self.jet)
        self.Miscellaneous.addAction(self.turbo)
        self.Miscellaneous.addAction(self.nipy_spectral)
        self.Miscellaneous.addAction(self.gist_ncar)

        self.hsv = QAction("hsv", self.User_No1)
        self.jet = QAction("jet", self.User_No1)
        self.ho_rainbow = QAction("Ho rainbow", self.User_No1)

        self.User_No1.addAction(self.hsv)
        self.User_No1.addAction(self.jet)
        self.User_No1.addAction(self.twilight_shifted)
        self.User_No1.addAction(self.ho_rainbow)


        self.viridis.triggered.connect(lambda: self.color_map(0))
        self.plasma.triggered.connect(lambda: self.color_map(1))
        self.inferno.triggered.connect(lambda: self.color_map(2))
        self.magma.triggered.connect(lambda: self.color_map(3))
        self.cividis.triggered.connect(lambda: self.color_map(4))

        self.Greys.triggered.connect(lambda: self.color_map(5))
        self.Purples.triggered.connect(lambda: self.color_map(6))
        self.Blues.triggered.connect(lambda: self.color_map(7))
        self.Greens.triggered.connect(lambda: self.color_map(8))
        self.Oranges.triggered.connect(lambda: self.color_map(9))
        self.Reds.triggered.connect(lambda: self.color_map(10))
        self.YlOrBr.triggered.connect(lambda: self.color_map(11))
        self.YlOrRd.triggered.connect(lambda: self.color_map(12))
        self.OrRd.triggered.connect(lambda: self.color_map(13))
        self.PuRd.triggered.connect(lambda: self.color_map(14))
        self.BuPu.triggered.connect(lambda: self.color_map(15))
        self.GnBu.triggered.connect(lambda: self.color_map(16))
        self.PuBu.triggered.connect(lambda: self.color_map(17))
        self.YlGnBu.triggered.connect(lambda: self.color_map(18))
        self.PuBuGn.triggered.connect(lambda: self.color_map(19))
        self.BuGn.triggered.connect(lambda: self.color_map(20))
        self.YlGn.triggered.connect(lambda: self.color_map(21))

        self.binary.triggered.connect(lambda: self.color_map(22))
        self.gist_yarg.triggered.connect(lambda: self.color_map(23))
        self.gist_gray.triggered.connect(lambda: self.color_map(24))
        self.gray.triggered.connect(lambda: self.color_map(25))
        self.bone.triggered.connect(lambda: self.color_map(26))
        self.pink.triggered.connect(lambda: self.color_map(27))
        self.spring.triggered.connect(lambda: self.color_map(28))
        self.summer.triggered.connect(lambda: self.color_map(29))
        self.autumn.triggered.connect(lambda: self.color_map(30))
        self.winter.triggered.connect(lambda: self.color_map(31))
        self.cool.triggered.connect(lambda: self.color_map(32))
        self.Wistia.triggered.connect(lambda: self.color_map(33))
        self.hot.triggered.connect(lambda: self.color_map(34))
        self.afmhot.triggered.connect(lambda: self.color_map(35))
        self.gist_heat.triggered.connect(lambda: self.color_map(36))
        self.copper.triggered.connect(lambda: self.color_map(37))

        self.PiYG.triggered.connect(lambda: self.color_map(38))
        self.PRGn.triggered.connect(lambda: self.color_map(39))
        self.BrBG.triggered.connect(lambda: self.color_map(40))
        self.PuOr.triggered.connect(lambda: self.color_map(41))
        self.RdGy.triggered.connect(lambda: self.color_map(42))
        self.RdBu.triggered.connect(lambda: self.color_map(43))
        self.RdYlBu.triggered.connect(lambda: self.color_map(44))
        self.RdYlGn.triggered.connect(lambda: self.color_map(45))
        self.Spectral.triggered.connect(lambda: self.color_map(46))
        self.coolwarm.triggered.connect(lambda: self.color_map(47))
        self.bwr.triggered.connect(lambda: self.color_map(48))
        self.seismic.triggered.connect(lambda: self.color_map(49))

        self.twilight.triggered.connect(lambda: self.color_map(50))
        self.twilight_shifted.triggered.connect(lambda: self.color_map(51))
        self.hsv.triggered.connect(lambda: self.color_map(52))

        self.Pastel1.triggered.connect(lambda: self.color_map(53))
        self.Pastel2.triggered.connect(lambda: self.color_map(54))
        self.Paired.triggered.connect(lambda: self.color_map(55))
        self.Accent.triggered.connect(lambda: self.color_map(56))
        self.Dark2.triggered.connect(lambda: self.color_map(57))
        self.Set1.triggered.connect(lambda: self.color_map(58))
        self.Set2.triggered.connect(lambda: self.color_map(59))
        self.Set3.triggered.connect(lambda: self.color_map(60))
        self.tab10.triggered.connect(lambda: self.color_map(61))
        self.tab20.triggered.connect(lambda: self.color_map(62))
        self.tab20b.triggered.connect(lambda: self.color_map(63))
        self.tab20c.triggered.connect(lambda: self.color_map(64))

        self.flag.triggered.connect(lambda: self.color_map(65))
        self.prism.triggered.connect(lambda: self.color_map(66))
        self.gist_earth.triggered.connect(lambda: self.color_map(67))
        self.terrain.triggered.connect(lambda: self.color_map(68))
        self.gist_stern.triggered.connect(lambda: self.color_map(69))
        self.gnuplot.triggered.connect(lambda: self.color_map(70))
        self.gnuplot2.triggered.connect(lambda: self.color_map(71))
        self.CMRmap.triggered.connect(lambda: self.color_map(72))
        self.cubehelix.triggered.connect(lambda: self.color_map(73))
        self.brg.triggered.connect(lambda: self.color_map(74))
        self.gist_rainbow.triggered.connect(lambda: self.color_map(75))
        self.rainbow.triggered.connect(lambda: self.color_map(76))
        self.jet.triggered.connect(lambda: self.color_map(77))
        self.turbo.triggered.connect(lambda: self.color_map(78))
        self.nipy_spectral.triggered.connect(lambda: self.color_map(79))
        self.gist_ncar.triggered.connect(lambda: self.color_map(80))
        self.ho_rainbow.triggered.connect(lambda: self.color_map(83))

        self.toolButton_ColorMap.setMenu(self.colormap_menu)

    # pushButton | setup roi and open line cut
    def open_linecut(self, status):
        if status:
            data, child_index = self.get_current_child()
            self.dataAnalysis = myDataAnalysis()
            self.dataAnalysis.close_signal.connect(lambda: self.close_subwin(0))
            self.dataAnalysis.init_data(data, child_index, 26)
            self.dataAnalysis.show()
        elif isinstance(self.dataAnalysis, QWidget):
            self.dataAnalysis.close()

    def close_subwin(self, index):
        if index == 0:    # 2D slicing
            self.dataAnalysis.deleteLater()

    def my_Qss(self):
        qssStyle = '''

                   QWidget#widget{
                   background-color:#eef0f6;
                   border-left:0.5px solid lightgray;
                   border-right:0.5px solid lightgray;
                   border-top:0.5px solid lightgray;
                   border-bottom:0.5px solid #e5e5e5;
                   border-top-left-radius: 5px;
                   border-top-right-radius: 5px;
                   }

                   QWidget#widget_2{
                   background-color:#ffffff;
                   border-left:0.5px solid lightgray;
                    border-right:0.5px solid lightgray;
                   border-bottom:0.5px solid #e5e5e5;
                   border-bottom-left-radius: 5px;
                   border-bottom-right-radius: 5px;
                   padding:5px 5px 5px 5px
                   }

                   QPushButton#pushButton
                   {
                   font-family:"Webdings";
                   text-align:top;
                   background:#6DDF6D;border-radius:5px;
                   border:none;
                   font-size:13px;
                   }
                   QPushButton#pushButton:hover{background:green;}

                   QPushButton#pushButton_2
                   {
                   font-family:"Webdings";
                   background:#F7D674;border-radius:5px;
                   border:none;
                   font-size:13px;
                   }
                   QPushButton#pushButton_2:hover{background:yellow;}

                   QPushButton#pushButton_3
                   {
                   font-family:"Webdings";
                   background:#F76677;border-radius:5px;
                   border:none;
                   font-size:13px;
                   }
                   QPushButton#pushButton_3:hover{background:red;}
                   '''
        self.setStyleSheet(qssStyle)

    # def make_a_mapp(self):
    #     data_list = [];
    #     par_list = [];
    #     size_list = []
    #     for path in self.displayed_file_paths:
    #         data = MappingData(path)
    #         data_list.append(data)
    #         # 0 -> gain 10.0, 1 -> gain 1.0, 3 -> gain 0.1
    #         xygain = 10 * (data.grid.lastgain[0] == 0) + 1 * (data.grid.lastgain[0] == 1) + 0.1 * (
    #                     data.grid.lastgain[0] == 3)
    #         # (x offset, y offset, step num, step size)
    #         par_list.append((data.grid.lastdac[1], data.grid.lastdac[14],
    #                          data.grid.step_num, data.grid.step_size, xygain))
    #         size_list.append(data.grid.step_num * data.grid.step_size * xygain)
    #     par = np.array(par_list)
    #     size = np.array(size_list)
    #     print(par_list)
    #
    #     small_ind = np.argmin(par[:, 3])
    #     small_size = size_list[small_ind]
    #     small_size = 1
    #     img_list = []
    #     for ind, data in enumerate(data_list):
    #         # resized = scipy.ndimage.zoom(data.data[0], size_list[ind]/small_size, order=0)
    #         resized = scipy.ndimage.zoom(data.data[0], par_list[ind][3] * par_list[ind][4] / small_size, order=0)
    #         img_list.append(resized)
    #     small_val = np.min(np.array(img_list))
    #
    #     left_ind = np.argmin(par[:, 0] - par[:, 2] * par[:, 3] * par[:, 4] // 2 - 1)
    #     right_ind = np.argmax(par[:, 0] + par[:, 2] * par[:, 3] * par[:, 4] // 2 + 1)
    #     lower_ind = np.argmin(par[:, 1] - par[:, 2] * par[:, 3] * par[:, 4] // 2 - 1)
    #     upper_ind = np.argmax(par[:, 1] + par[:, 2] * par[:, 3] * par[:, 4] // 2 + 1)
    #
    #     left_border = par_list[left_ind][0] - img_list[left_ind].shape[0] // 2 - 1
    #     right_border = par_list[right_ind][0] + img_list[right_ind].shape[0] // 2 + 1
    #     lower_border = par_list[lower_ind][1] - img_list[lower_ind].shape[1] // 2 - 1
    #     upper_border = par_list[upper_ind][1] + img_list[upper_ind].shape[1] // 2 + 1
    #     print('--->', left_border, right_border, lower_border, upper_border)
    #     map = np.ones((right_border - left_border,
    #                    upper_border - lower_border)) * small_val  # (35594, 41534) 11957 12086 41532 41661
    #
    #     print('map shape:', map.shape)
    #     for ind, img in enumerate(img_list):
    #         print(ind, '->', img.shape)
    #         print(map[
    #               par_list[ind][0] - left_border - img.shape[0] // 2 - 1: par_list[ind][0] - left_border - img.shape[
    #                   0] // 2 - 1 + img.shape[0],
    #               par_list[ind][1] - lower_border - img.shape[1] // 2 - 1: par_list[ind][1] - lower_border - img.shape[
    #                   1] // 2 - 1 + img.shape[1]].shape)
    #         print(par_list[ind][0] - left_border - img.shape[0] // 2 - 1,
    #               par_list[ind][0] - left_border - img.shape[0] // 2 - 1 + img.shape[0], \
    #               par_list[ind][1] - lower_border - img.shape[1] // 2 - 1,
    #               par_list[ind][1] - lower_border - img.shape[1] // 2 - 1 + img.shape[1])
    #         map[par_list[ind][0] - left_border - img.shape[0] // 2 - 1: par_list[ind][0] - left_border - img.shape[
    #             0] // 2 - 1 + img.shape[0],
    #         par_list[ind][1] - lower_border - img.shape[1] // 2 - 1: par_list[ind][1] - lower_border - img.shape[
    #             1] // 2 - 1 + img.shape[1]] = img
    #         # map[par_list[ind][0]-img.shape[0]//2 -1: par_list[ind][0] - img.shape[0]//2-1+img.shape[0],
    #         #     par_list[ind][1]-img.shape[1]//2-1: par_list[ind][1]-img.shape[1]//2-1+img.shape[1]]=img
    #     map = scipy.ndimage.zoom(map, 1 / 3, order=0)
    #     imageio.imsave('./map.png', map)

    def make_a_map(self):
        data_list = []
        for path in self.displayed_file_paths:
            data = MappingData(path)
            data_list.append(data)

        self.makeMap.init_data(data_list)
        self.makeMap.show()
        self.makeMap.raise_()

    def write_cnfg(self):
        self.cnfg.clear()
        self.cnfg.setValue("CNFG/FILE_PATH", self.dir_path)

    def closeEvent(self, event):
        self.close_signal.emit()
        self.mdiArea.closeAllSubWindows()
        self.write_cnfg()  # Write configuration file
        # sys.exit(0)  # Close all aub windows, but doesn't work for matplotlib window
        event.accept()


if __name__ == "__main__":
    # create the application and the main window
    app = QApplication(sys.argv)
    window = myQuickViewWindow()
    ''' qdarkstyle '''
    ### setup stylesheet
    # os.environ['PYQTGRAPH_QT_LIB'] = 'PyQt5
    # app.setStyleSheet(qdarkstyle.load_stylesheet(qt_api=os.environ['PYQTGRAPH_QT_LIB'], palette=LightPalette))
    # run
    ''' 2. subwin '''
    # ## setup custimize subwin
    app.setStyle("Fusion")
    window.show()
    sys.exit(app.exec_())

'''
http://www.jiuaitu.com/python/380.html
'''