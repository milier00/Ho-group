import sys

sys.path.append("./ui/")
sys.path.append("./model/")

from PyQt5.QtWidgets import QLabel, QSpinBox, QWidget, QGridLayout, QApplication, QMainWindow, QAbstractItemView, \
    QFileDialog, QShortcut, QMenu, QAction
from PyQt5.QtWidgets import QApplication, QLabel, QProxyStyle, QToolButton, QWidget, QMenu,  QButtonGroup, QAction, QAbstractItemView, QShortcut, QListWidget
from PyQt5.QtWidgets import QMainWindow,  QFileDialog
from PyQt5.QtWidgets import QMdiSubWindow
from PyQt5.QtWidgets import QStyle, QStyleOptionSlider
from PyQt5.QtCore import QSettings, QEasingCurve, QPropertyAnimation, QTimer
from PyQt5.QtCore import pyqtSignal, Qt, QDir
from PyQt5.QtGui import QColor, QPainter, QPainterPath
from PyQt5.QtCore import QSize, Qt, pyqtSignal, QPoint, QRectF
from PyQt5.QtCore import  pyqtSlot, QRectF
from pyqtgraph.Qt import QtGui
from PyQt5 import QtCore
from DrawSpc_ui import Ui_DrawSpc
from CustomHistogramLUTItem import CustomHistogramLUTItem
from Data import *
from images import myImages
import functools as ft
import numpy as np
import os
import ctypes
import copy
import pyqtgraph as pg
from pyqtgraph.Qt import QtWidgets
import pyqtgraph.parametertree.parameterTypes as pTypes
from pyqtgraph.parametertree import Parameter, ParameterTree
from switch_button import SwitchButton
import colorcet as cc
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.figure import Figure
import matplotlib
matplotlib.use('Qt5Agg')
import matplotlib as mpl

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

class MplCanvas(FigureCanvasQTAgg):

    def __init__(self, parent=None, width=5, height=4, dpi=100):
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        # fig.patch.set_facecolor("None")
        self.ax3D = self.fig.add_subplot(111, projection='3d')
        super(MplCanvas, self).__init__(self.fig)

    def redraw(self):  # 重绘曲线
        self.fig.canvas.draw()

class myDrawSpc(QWidget, Ui_DrawSpc):
    # Common signal
    close_signal = pyqtSignal()

    def __init__(self):
        super().__init__()
        pg.setConfigOption('background', (255, 255, 255, 255))
        pg.setConfigOption('foreground', 'k')
        self.setupUi(self)
        self.init_UI_LC()
        self.init_UI_2D()
        self.init_UI_3D()
        self.resize(2400, 1200)     # 4K
        self.resize(1200, 600)      # 2K
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("myappid")

    """ Common functions """

    def color_changed(self, type, index):
        if type == 0:   # Built-in colors
            self.colors = self.cmDictBuiltin[index]
            self.update_graph()
        elif type == 1: # From color map
            ''' add ticks by curve number '''
            cmap = self.cmDictCmap[self.comboBox_FromCmap.currentText()][self.comboBox_FromCmap_2.currentIndex()]
            self.colorBar.gradient.setColorMap(cmap, len(self.xs))
            self.colors = [tick[0].color.getRgb() for tick in self.colorBar.gradient.listTicks()]
            self.update_graph()
        elif type == -1:    # From color map AUX
            ''' add 5 ticks and determine colors uniformly '''
            cmap = self.cmDictCmap[self.comboBox_FromCmap.currentText()][self.comboBox_FromCmap_2.currentIndex()]
            self.colorBar.gradient.setColorMap(cmap, 5)
            pos = np.linspace(0, 255, len(self.xs), dtype=int)
            self.colors = [cmap.getColors()[p] for p in pos]
            self.update_graph()
        elif type == 2: # Gradient Color
            cmap = self.cmDictCmap[self.comboBox_GradientColor.currentText()][self.comboBox_GradientColor_2.currentIndex()]
            self.colors = [cmap] * len(self.xs)
            self.update_graph()
        elif type == 3: # 3D plot
            try:
                self.__colormap3D = mpl.cm.get_cmap(self.comboBox_cmap3D_2.currentText())
            except:
                return
            self.update_graph_3D()
        elif type == 4: # 2D plot
            self.__colormap2D = self.cmDictCmap[self.comboBox_cmap2D.currentText()][self.comboBox_cmap2D_2.currentIndex()]
            self.update_graph_2D()

    def load_cmap(self, type, index):
        if type == 1:
            self.comboBox_FromCmap_2.clear()
            if index == 0:
                cmListCmap = ['viridis', 'plasma', 'inferno', 'magma', 'cividis']
            elif index == 1:
                cmListCmap = [
                'Greys', 'Purples', 'Blues', 'Greens', 'Oranges', 'Reds',
                'YlOrBr', 'YlOrRd', 'OrRd', 'PuRd', 'RdPu', 'BuPu',
                'GnBu', 'PuBu', 'YlGnBu', 'PuBuGn', 'BuGn', 'YlGn']
            elif index == 2:
                cmListCmap = [
                    'binary', 'gist_yarg', 'gist_gray', 'gray', 'bone', 'pink',
                    'spring', 'summer', 'autumn', 'winter', 'cool', 'Wistia',
                    'hot', 'afmhot', 'gist_heat', 'copper']
            elif index == 3:
                cmListCmap = [
                    'PiYG', 'PRGn', 'BrBG', 'PuOr', 'RdGy', 'RdBu',
                    'RdYlBu', 'RdYlGn', 'Spectral', 'coolwarm', 'bwr', 'seismic']
            elif index == 4:
                cmListCmap = ['twilight', 'twilight_shifted', 'hsv']
            elif index == 5:
                cmListCmap = [
                'Pastel1', 'Pastel2', 'Paired', 'Accent',
                'Dark2', 'Set1', 'Set2', 'Set3',
                'tab10', 'tab20', 'tab20b', 'tab20c']
            elif index == 6:
                cmListCmap = [
                    'flag', 'prism', 'ocean', 'gist_earth', 'terrain', 'gist_stern',
                    'gnuplot', 'gnuplot2', 'CMRmap', 'cubehelix', 'brg',
                    'gist_rainbow', 'rainbow', 'jet', 'turbo', 'nipy_spectral',
                    'gist_ncar']
            self.comboBox_FromCmap_2.addItems(cmListCmap)
        elif type == -1:
            self.comboBox_FromCmapAUX_2.clear()
            if index == 0:
                cmListCmap = ['viridis', 'plasma', 'inferno', 'magma', 'cividis']
            elif index == 1:
                cmListCmap = [
                    'Greys', 'Purples', 'Blues', 'Greens', 'Oranges', 'Reds',
                    'YlOrBr', 'YlOrRd', 'OrRd', 'PuRd', 'RdPu', 'BuPu',
                    'GnBu', 'PuBu', 'YlGnBu', 'PuBuGn', 'BuGn', 'YlGn']
            elif index == 2:
                cmListCmap = [
                    'binary', 'gist_yarg', 'gist_gray', 'gray', 'bone', 'pink',
                    'spring', 'summer', 'autumn', 'winter', 'cool', 'Wistia',
                    'hot', 'afmhot', 'gist_heat', 'copper']
            elif index == 3:
                cmListCmap = [
                    'PiYG', 'PRGn', 'BrBG', 'PuOr', 'RdGy', 'RdBu',
                    'RdYlBu', 'RdYlGn', 'Spectral', 'coolwarm', 'bwr', 'seismic']
            elif index == 4:
                cmListCmap = ['twilight', 'twilight_shifted', 'hsv']
            elif index == 5:
                cmListCmap = [
                    'Pastel1', 'Pastel2', 'Paired', 'Accent',
                    'Dark2', 'Set1', 'Set2', 'Set3',
                    'tab10', 'tab20', 'tab20b', 'tab20c']
            elif index == 6:
                cmListCmap = [
                    'flag', 'prism', 'ocean', 'gist_earth', 'terrain', 'gist_stern',
                    'gnuplot', 'gnuplot2', 'CMRmap', 'cubehelix', 'brg',
                    'gist_rainbow', 'rainbow', 'jet', 'turbo', 'nipy_spectral',
                    'gist_ncar']
            self.comboBox_FromCmapAUX_2.addItems(cmListCmap)
        elif type == 2:
            self.comboBox_GradientColor_2.clear()
            if index == 0:
                cmListCmap = ['viridis', 'plasma', 'inferno', 'magma', 'cividis']
            elif index == 1:
                cmListCmap = [
                'Greys', 'Purples', 'Blues', 'Greens', 'Oranges', 'Reds',
                'YlOrBr', 'YlOrRd', 'OrRd', 'PuRd', 'RdPu', 'BuPu',
                'GnBu', 'PuBu', 'YlGnBu', 'PuBuGn', 'BuGn', 'YlGn']
            elif index == 2:
                cmListCmap = [
                    'binary', 'gist_yarg', 'gist_gray', 'gray', 'bone', 'pink',
                    'spring', 'summer', 'autumn', 'winter', 'cool', 'Wistia',
                    'hot', 'afmhot', 'gist_heat', 'copper']
            elif index == 3:
                cmListCmap = [
                    'PiYG', 'PRGn', 'BrBG', 'PuOr', 'RdGy', 'RdBu',
                    'RdYlBu', 'RdYlGn', 'Spectral', 'coolwarm', 'bwr', 'seismic']
            elif index == 4:
                cmListCmap = ['twilight', 'twilight_shifted', 'hsv']
            elif index == 5:
                cmListCmap = [
                'Pastel1', 'Pastel2', 'Paired', 'Accent',
                'Dark2', 'Set1', 'Set2', 'Set3',
                'tab10', 'tab20', 'tab20b', 'tab20c']
            elif index == 6:
                cmListCmap = [
                    'flag', 'prism', 'ocean', 'gist_earth', 'terrain', 'gist_stern',
                    'gnuplot', 'gnuplot2', 'CMRmap', 'cubehelix', 'brg',
                    'gist_rainbow', 'rainbow', 'jet', 'turbo', 'nipy_spectral',
                    'gist_ncar']
            self.comboBox_GradientColor_2.addItems(cmListCmap)
        elif type == 3: #3D
            self.comboBox_cmap3D_2.clear()
            if index == 0:
                cmListCmap = ['viridis', 'plasma', 'inferno', 'magma', 'cividis']
            elif index == 1:
                cmListCmap = [
                    'Greys', 'Purples', 'Blues', 'Greens', 'Oranges', 'Reds',
                    'YlOrBr', 'YlOrRd', 'OrRd', 'PuRd', 'RdPu', 'BuPu',
                    'GnBu', 'PuBu', 'YlGnBu', 'PuBuGn', 'BuGn', 'YlGn']
            elif index == 2:
                cmListCmap = [
                    'binary', 'gist_yarg', 'gist_gray', 'gray', 'bone', 'pink',
                    'spring', 'summer', 'autumn', 'winter', 'cool', 'Wistia',
                    'hot', 'afmhot', 'gist_heat', 'copper']
            elif index == 3:
                cmListCmap = [
                    'PiYG', 'PRGn', 'BrBG', 'PuOr', 'RdGy', 'RdBu',
                    'RdYlBu', 'RdYlGn', 'Spectral', 'coolwarm', 'bwr', 'seismic']
            elif index == 4:
                cmListCmap = ['twilight', 'twilight_shifted', 'hsv']
            elif index == 5:
                cmListCmap = [
                    'Pastel1', 'Pastel2', 'Paired', 'Accent',
                    'Dark2', 'Set1', 'Set2', 'Set3',
                    'tab10', 'tab20', 'tab20b', 'tab20c']
            elif index == 6:
                cmListCmap = [
                    'flag', 'prism', 'ocean', 'gist_earth', 'terrain', 'gist_stern',
                    'gnuplot', 'gnuplot2', 'CMRmap', 'cubehelix', 'brg',
                    'gist_rainbow', 'rainbow', 'jet', 'turbo', 'nipy_spectral',
                    'gist_ncar']
            self.comboBox_cmap3D_2.addItems(cmListCmap)
        elif type == 4: # 2D plot
            self.comboBox_cmap2D_2.clear()
            if index == 0:
                cmListCmap = ['viridis', 'plasma', 'inferno', 'magma', 'cividis']
            elif index == 1:
                cmListCmap = [
                    'Greys', 'Purples', 'Blues', 'Greens', 'Oranges', 'Reds',
                    'YlOrBr', 'YlOrRd', 'OrRd', 'PuRd', 'RdPu', 'BuPu',
                    'GnBu', 'PuBu', 'YlGnBu', 'PuBuGn', 'BuGn', 'YlGn']
            elif index == 2:
                cmListCmap = [
                    'binary', 'gist_yarg', 'gist_gray', 'gray', 'bone', 'pink',
                    'spring', 'summer', 'autumn', 'winter', 'cool', 'Wistia',
                    'hot', 'afmhot', 'gist_heat', 'copper']
            elif index == 3:
                cmListCmap = [
                    'PiYG', 'PRGn', 'BrBG', 'PuOr', 'RdGy', 'RdBu',
                    'RdYlBu', 'RdYlGn', 'Spectral', 'coolwarm', 'bwr', 'seismic']
            elif index == 4:
                cmListCmap = ['twilight', 'twilight_shifted', 'hsv']
            elif index == 5:
                cmListCmap = [
                    'Pastel1', 'Pastel2', 'Paired', 'Accent',
                    'Dark2', 'Set1', 'Set2', 'Set3',
                    'tab10', 'tab20', 'tab20b', 'tab20c']
            elif index == 6:
                cmListCmap = [
                    'flag', 'prism', 'ocean', 'gist_earth', 'terrain', 'gist_stern',
                    'gnuplot', 'gnuplot2', 'CMRmap', 'cubehelix', 'brg',
                    'gist_rainbow', 'rainbow', 'jet', 'turbo', 'nipy_spectral',
                    'gist_ncar']
            self.comboBox_cmap2D_2.addItems(cmListCmap)

    def init_data(self, xs, ys, names, data3D):
        ## init linecut data
        self.xs = copy.deepcopy(xs)
        self.ys = copy.deepcopy(ys)
        self.names = copy.deepcopy(names)

        """ for test only """
        # # Add some noise on the curves
        # noise = 0.1
        # noises: list = np.random.rand(25, 100) * noise
        # self.xs = []
        # self.ys = []
        # self.nb_lines = 25
        # for i in range(self.nb_lines):
        #     self.xs.append(np.linspace(0, 2 * np.pi, 100) - i)
        #     self.ys.append(np.sin(self.xs[-1]) * self.xs[-1] - i / 3 + noises[i])
        # self.names = []
        # for i in range(self.nb_lines):
        #     self.names.append('line#'+str(i))
        #
        # col = self.xs[0].shape[0]
        # row = len(self.xs)
        # target_y = self.norm3Ddata(self.ys)
        # data3D = np.array(target_y).reshape(row, col)
        """ End of test """

        ## create plot data items
        for name in self.names:
            self.plot.addItem(pg.PlotDataItem(x=[0], y=[0], name=name))

        ## init 2D Plot data
        self.data2D = np.array(self.ys)
        (row, col) = self.data2D.shape

        for i in range(row - 1, -1, -1):
            for j in range(col//row-1):
                self.data2D = np.insert(self.data2D, i, self.data2D[i, :], axis=0)
        self.data2D = self.data2D.transpose()

        ## init 3D Plot data
        self.data3D = copy.deepcopy(data3D)
        self.xyz = copy.deepcopy(data3D)
        y = np.linspace(0, data3D.shape[0] - 1, data3D.shape[0], endpoint=True)
        x = np.linspace(0, data3D.shape[1] - 1, data3D.shape[1], endpoint=True)
        x, y = np.meshgrid(x, y)  # 二维网格化数组
        z = data3D
        self._X = x
        self._Y = y
        self._Z = z

        self.init_line_style()
        self.init_colorBar()
        self.init_interval()

    def init_interval(self):
        # max = (np.max(self.data3D) - np.min(self.data3D)) * 1
        # self.spinBox_interval.setMinimum(0)
        # self.spinBox_interval.setMaximum(max)
        # self.slider_interval.setMinimum(0)
        # self.slider_interval.setMaximum(int(max*10))
        self.spinBox_interval.setMinimum(-1)
        self.spinBox_interval.setMaximum(1)
        self.slider_interval.setMinimum(-100)
        self.slider_interval.setMaximum(100)

    def norm3Ddata(self, data3D):
        for data in data3D:
            first = data[0]
            for i in range(len(data)):
                data[i] = data[i] / first
        return data3D

    def init_colorBar(self):
        cmap = self.cmDictCmap[self.comboBox_FromCmap.currentText()][self.comboBox_FromCmap_2.currentIndex()]
        self.colorBar.gradient.setColorMap(cmap, len(self.xs))
        self.colorBar_2D.gradient.setColorMap(self.__colormap2D)

    """ Line cut Tab """

    def init_UI_LC(self):
        self.move(500, 400)

        self.img = myImages()
        self.lines = []
        self.interval = 0
        self.line_index = 0
        self.all_line = False
        self.color_type = 0

        """ Graphsic """
        # label | display scanner coordinates
        self.label = pg.LabelItem(justify='right')
        self.graphicsView.addItem(self.label, row=0, col=0)
        self.label.hide()

        # graphicsView |
        self.viewBox = CustomViewBox(enableMenu=False)
        self.viewBox.sigRangeChanged.connect(self.range_changed)

        # plotItem |
        self.plot = self.graphicsView.addPlot(viewBox=self.viewBox, row=1, col=0)
        # self.proxy = pg.SignalProxy(self.plot.scene().sigMouseMoved, rateLimit=60, slot=self.mouseMoved)
        self.plot.showAxes('right')
        self.plot.showAxes('top')

        """ only show/hide legend item each time """
        # # legend |
        # self.legend = self.plot.addLegend(labelTextSize='10pt')
        # self.legend.setParentItem(self.plot)
        # self.legend.hide()
        """ delete/create legend item each time """
        # do nothing here

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
        self.colorBar = CustomHistogramLUTItem(levelMode='mono')
        self.graphicsView.addItem(self.colorBar, 1, 1, 1, 1)
        self.colorBar.hide()
        self.colorBar.gradient.sigTicksChanged.connect(self.tick_changed)
        self.colorBar.gradient.sigTicksChangeFinished.connect(self.tick_changed)
        self.colorBar.gradient.sigGradientChangeFinished.connect(self.tick_changed)

        # hist |
        self.hist = pg.ColorBarItem(values=(0, 255))
        self.graphicsView.addItem(self.hist, 1, 2, 1, 1)
        self.hist.hide()

        """ Contrls """
        # pushButton |
        self.pushButton_xScale.clicked.connect(lambda: self.scale(0))
        self.pushButton_yScale.clicked.connect(lambda: self.scale(1))
        self.pushButton_Scanner.clicked.connect(self.show_scanner)
        self.pushButton_CBar_LC.toggled.connect(self.show_colorbar)
        self.pushButton_CBarAUX_LC.toggled.connect(self.show_hist)

        # colorButton |
        self.colorButton = pg.ColorButton()
        self.colorButton.sigColorChanging.connect(self.line_style_changed)
        self.colorButton.sigColorChanged.connect(self.line_style_changed)
        self.toolBox.widget(3).layout().addWidget(self.colorButton, 3, 1, 1, 1)

        # switchButton |
        self.switchButton_allLine = SwitchButton(parent=self, text='Single')
        self.switchButton_allLine.checkedChanged.connect(self.line_option_changed)
        self.switchButton_allLine.setChecked(False)
        self.toolBox.widget(3).layout().addWidget(self.switchButton_allLine, 0, 1, 1, 1)

        # spinBox |
        self.spinBox_interval.editingFinished.connect(lambda: self.interval_changed(0))
        self.spinBox_xmin.editingFinished.connect(lambda: self.axis_changed(0))
        self.spinBox_xmax.editingFinished.connect(lambda: self.axis_changed(0))
        self.spinBox_ymin.editingFinished.connect(lambda: self.axis_changed(1))
        self.spinBox_ymax.editingFinished.connect(lambda: self.axis_changed(1))
        self.spinBox_lineWidth.editingFinished.connect(self.line_style_changed)
        self.spinBox_fontSize.editingFinished.connect(lambda: self.axis_changed(2))
        self.spinBox_fontSize.editingFinished.connect(self.legend_changed)
        self.spinBox_legendHspacing.editingFinished.connect(self.legend_changed)
        self.spinBox_legendVspacing.editingFinished.connect(self.legend_changed)
        self.spinBox_legendCols.editingFinished.connect(self.legend_changed)
        self.spinBox_titleSize.editingFinished.connect(self.title_changed)

        # slider |
        self.slider_minAUX.valueChanged.connect(lambda: self.tick_changed(None))
        self.slider_maxAUX.valueChanged.connect(lambda: self.tick_changed(None))
        self.slider_minAUX.setStyle(HollowHandleStyle())
        self.slider_maxAUX.setStyle(HollowHandleStyle())

        # comboBox |
        self.comboBox_lineIndex.setPlaceholderText('Select line')
        self.comboBox_lineIndex.setCurrentIndex(0)
        self.comboBox_lineIndex.setCurrentText('Select line')
        self.comboBox_lineType.currentIndexChanged.connect(self.line_style_changed)
        self.comboBox_lineIndex.currentIndexChanged.connect(self.line_changed)
        self.fontComboBox_font.setCurrentFont(QtGui.QFont("Times New Roman"))
        self.fontComboBox_title.setCurrentFont(QtGui.QFont("Times New Roman"))
        self.fontComboBox_font.currentFontChanged.connect(lambda: self.axis_changed(2))
        self.fontComboBox_font.currentFontChanged.connect(self.legend_changed)
        self.fontComboBox_title.currentFontChanged.connect(self.title_changed)

        # comboBoc | color
        cmListBuiltin = ('cc.glasbey', 'cc.glasbey_hv', 'cc.glasbey_cool', 'cc.glasbey_warm', 'cc.glasbey_dark', \
                    'cc.glasbey_light', 'blue', 'green', 'red', 'orange', \
                    'purple', 'black')
        glasbey_hv = [self.img.rgb2hex(c) for c in cc.glasbey_hv]
        self.cmDictBuiltin = {0: cc.glasbey, 1: glasbey_hv, 2: cc.glasbey_cool, 3: cc.glasbey_warm, 4: cc.glasbey_dark, \
                         5: cc.glasbey_light, 6: ['#038add'] * 256, 7: ['#2CA02C'] * 256, 8: ['#d60000'] * 256,
                         9: ['#FF7F0E'] * 256, \
                         10: ['#ba6efd'] * 256, 11: ['#1E1E1E'] * 256}
        self.comboBox_BuiltinColor.addItems(cmListBuiltin)
        self.comboBox_BuiltinColor.currentIndexChanged[int].connect(ft.partial(self.color_changed, 0))
        cmListCmap = ['viridis', 'plasma', 'inferno', 'magma', 'cividis']
        cmListCmapType = ['Perceptually Uniform Sequential', 'Sequential', 'Sequential (2)', 'Diverging', 'Cyclic', 'Qualitative', 'Miscellaneous']
        self.cmDictCmap = self.img.cmDictCmap
        self.comboBox_FromCmap.addItems(cmListCmapType)
        self.comboBox_FromCmap_2.addItems(cmListCmap)
        self.comboBox_FromCmap.currentIndexChanged[int].connect(ft.partial(self.load_cmap, 1))
        self.comboBox_FromCmap.currentIndexChanged[int].connect(ft.partial(self.color_changed, 1))
        self.comboBox_FromCmap_2.currentIndexChanged[int].connect(ft.partial(self.color_changed, 1))
        self.comboBox_FromCmapAUX.addItems(cmListCmapType)
        self.comboBox_FromCmapAUX_2.addItems(cmListCmap)
        self.comboBox_FromCmapAUX.currentIndexChanged[int].connect(ft.partial(self.load_cmap, -1))
        self.comboBox_FromCmapAUX.currentIndexChanged[int].connect(ft.partial(self.color_changed, -1))
        self.comboBox_FromCmapAUX_2.currentIndexChanged[int].connect(ft.partial(self.color_changed, -1))
        self.comboBox_GradientColor.addItems(cmListCmapType)
        self.comboBox_GradientColor_2.addItems(cmListCmap)
        self.comboBox_GradientColor.currentIndexChanged[int].connect(ft.partial(self.load_cmap, 2))
        self.comboBox_GradientColor.currentIndexChanged[int].connect(ft.partial(self.color_changed, 2))
        self.comboBox_GradientColor_2.currentIndexChanged[int].connect(ft.partial(self.color_changed, 2))
        self.colors = self.cmDictBuiltin[0]

        # lineEdit |
        self.lineEdit_customType.editingFinished.connect(self.line_style_changed)
        self.lineEdit_customType.setEnabled(False)
        self.label_customType.setEnabled(False)
        self.lineEdit_legendOffset.editingFinished.connect(lambda: self.axis_changed(2))
        self.lineEdit_titleContent.editingFinished.connect(self.title_changed)
        self.lineEdit_xtitle.editingFinished.connect(lambda: self.axis_changed(2))
        self.lineEdit_xunit.editingFinished.connect(lambda: self.axis_changed(2))
        self.lineEdit_ytitle.editingFinished.connect(lambda: self.axis_changed(2))
        self.lineEdit_yunit.editingFinished.connect(lambda: self.axis_changed(2))

        # slider |
        self.slider_interval.valueChanged.connect(lambda: self.interval_changed(1))

        # groupBox |
        self.groupBox_title.toggled.connect(self.show_title)
        self.groupBox_legend.toggled.connect(self.show_legend)
        self.groupBox_BuiltinColor.toggled[bool].connect(ft.partial(self.manual_exclusive, 0))
        self.groupBox_FromCmap.toggled[bool].connect(ft.partial(self.manual_exclusive, 1))
        self.groupBox_GradientColor.toggled[bool].connect(ft.partial(self.manual_exclusive, 2))
        self.groupBox_FromCmapAUX.toggled[bool].connect(ft.partial(self.manual_exclusive, -1))
        # """ set axis title """
        # self.plot.setLabel('bottom', 'Bias', 'mV')
        # self.plot.setLabel('left', 'dI/dV', 'arb.units')
        # """ set axis tick """
        # self.plot.axes['bottom']['item'].setTickFont(QtGui.QFont('Arial Black', pointSize=12))#, pointSize=-1[, weight=-1[, italic=false]]]))
        # """ set axis range """
        # self.plot.setXRange(0, 5)
        # self.plot.setYRange(0, 5)
        # """ set log mode """
        # self.plot.setLogMode(x=False, y=False)
        # """ set line style """
        # self.pen = pg.mkPen(color='#FF0', width=2, style=Qt.DashDotDotLine, dash=[2,4,2,4], cosmetic=True, hsv=None)
        # self.plot.listDataItems()[0].setPen(self.pen)
        # """ set color map """
        # cm = pg.colormap.get('CET-L17')
        # cm.reverse()
        # pen0 = cm.getPen(span=(-5, 2), width=10)
        # self.plot.listDataItems()[0].setPen(pen=pen0)
        # self.plot.listDataItems()[0].updateItems(styleUpdate=True)

        # """ parameter tree """
        # params = [pTypes.PenParameter(name="my Pen")]
        # ## Create tree of Parameter objects
        # p = Parameter.create(name='params', type='group', children=params)
        # ## Create two ParameterTree widgets, both accessing the same data
        # t = ParameterTree()
        # t.setParameters(p, showTop=False)
        # t.setWindowTitle('pyqtgraph example: Parameter Tree')
        #
        # layout = QtWidgets.QGridLayout()
        # layout.addWidget(t)
        # self.toolBox.widget(3).setLayout(layout)

    def tick_changed(self, obj):
        if self.color_type == 1:    # Line cut from color map
            self.colors = [tick[0].color.getRgb() for tick in obj.listTicks()]
            self.update_graph()
        elif self.color_type == -1:  # Line cut from color map AUX
            min = self.slider_minAUX.value()
            max = self.slider_maxAUX.value()
            # set pos of lines
            self.hist.region.setRegion((min, max))
            # set colorap
            cmap = self.cmDictCmap[self.comboBox_FromCmapAUX.currentText()][self.comboBox_FromCmapAUX_2.currentIndex()]
            self.hist.setColorMap(cmap)
            colors = cmap.getColors()[min:max]
            posx = np.linspace(0, 1, len(colors))
            cmap = pg.ColorMap(posx, colors)
            pos = np.linspace(0, len(cmap.getColors())-1, len(self.xs), dtype=int)
            self.colors = [cmap.getColors()[p] for p in pos]
            self.update_graph()

    def manual_exclusive(self, index: int, isChecked: bool):
        if isChecked:
            self.color_type = index
            self.color_changed(self.color_type, 0)
            if index == 0:
                self.groupBox_FromCmap.setChecked(False)
                self.groupBox_GradientColor.setChecked(False)
                self.groupBox_FromCmapAUX.setChecked(False)
                self.show_colorbar(False)
                self.show_hist(False)
            elif index ==1:
                self.groupBox_BuiltinColor.setChecked(False)
                self.groupBox_GradientColor.setChecked(False)
                self.groupBox_FromCmapAUX.setChecked(False)
                self.show_colorbar(True)
                self.show_hist(False)
            elif index == 2:
                self.groupBox_BuiltinColor.setChecked(False)
                self.groupBox_FromCmap.setChecked(False)
                self.groupBox_FromCmapAUX.setChecked(False)
                self.show_colorbar(False)
                self.show_hist(False)
            elif index == -1:
                self.groupBox_BuiltinColor.setChecked(False)
                self.groupBox_FromCmap.setChecked(False)
                self.groupBox_GradientColor.setChecked(False)
                self.show_colorbar(False)
                self.show_hist(True)

    def show_title(self, show):
        if show:
            self.plot.titleLabel.show()
        else:
            self.plot.setTitle(None)

    def show_legend(self, show):
        """ delete/create legend item each time """
        if show:
            self.legend = self.plot.addLegend(labelTextSize='10pt')
            self.legend.setParentItem(self.plot)
            for item in self.plot.listDataItems():
                self.legend.addItem(item, item.name())
            self.legend.show()
        else:
            self.legend.clear()
            self.plot.removeItem(self.legend)
            self.legend = None
        """ only show/hide legend item each time """
        # if show:
        #     self.legend.show()
        # else:
        #     self.legend.hide()

    # switchButton slot | show/hide fb
    def line_option_changed(self, isChecked: bool):
        self.all_line = isChecked
        text = 'All' if isChecked else 'Single'
        self.switchButton_allLine.setText(text)
        self.comboBox_lineIndex.setEnabled(not isChecked)

    def line_changed(self, index):
        self.line_index = index
        self.load_line_style()

    def load_line_style(self):
        self.spinBox_lineWidth.setValue(self.line_style_dict[self.line_index]['width'])
        self.comboBox_lineType.setCurrentIndex(self.line_style_dict[self.line_index]['dash'])
        if self.comboBox_lineType.currentIndex() == 5:
            self.lineEdit_customType.setText(self.line_style_dict[self.line_index]['custom dash'])
        else:
            self.lineEdit_customType.setText('')
        self.colorButton.setColor(self.line_style_dict[self.line_index]['color'])

    def update_line_style(self):
        self.line_style_dict[self.line_index]['width'] = self.spinBox_lineWidth.value()
        self.line_style_dict[self.line_index]['dash'] = self.comboBox_lineType.currentIndex()
        if self.comboBox_lineType.currentIndex() == 5:
            custom_type = self.lineEdit_customType.text().replace(',', '')
            custom_type = [int(x) for x in custom_type]
            self.line_style_dict[self.line_index]['custom dash'] = custom_type
        else:
            self.line_style_dict[self.line_index]['custom dash'] = None
        self.line_style_dict[self.line_index]['color'] = self.colorButton.color()

    def line_style_changed(self):
        self.update_line_style()

        if self.all_line:  # set all line style
            # line width changed
            width = self.spinBox_lineWidth.value()
            for line in self.plot.listDataItems():
                pen = line.opts['pen']
                pen.setWidth(width)
                line.updateItems(styleUpdate=True)

            # line type changed
            ind = self.comboBox_lineType.currentIndex()
            pen_style_dict = {0: Qt.SolidLine, 1: Qt.DashLine, 2: Qt.DotLine, 3: Qt.DashDotLine,
                              4: Qt.DashDotDotLine, 5: Qt.CustomDashLine}
            if ind == 5:
                self.lineEdit_customType.setEnabled(True)
                self.label_customType.setEnabled(True)
                custom_type = self.lineEdit_customType.text().replace(',', '')
                custom_type = [int(x) for x in custom_type]
            else:
                self.lineEdit_customType.setEnabled(False)
                self.label_customType.setEnabled(False)
            for line in self.plot.listDataItems():
                pen = line.opts['pen']
                pen.setStyle(pen_style_dict[ind])
                if ind == 5:
                    pen.setDashPattern(custom_type)
                line.updateItems(styleUpdate=True)
                # setBrush()
                # setCapStyle()
                # setJoinStyle()

            # line color changed
            color = self.colorButton.color()
            for line in self.plot.listDataItems():
                pen = line.opts['pen']
                pen.setColor(color)
                line.updateItems(styleUpdate=True)

        # set single line style
        else:
            # line width changed
            width = self.spinBox_lineWidth.value()
            line = self.plot.listDataItems()[self.line_index]
            pen = line.opts['pen']
            pen.setWidth(width)
            line.updateItems(styleUpdate=True)

            # line type changed
            ind = self.comboBox_lineType.currentIndex()
            pen_style_dict = {0: Qt.SolidLine, 1: Qt.DashLine, 2: Qt.DotLine, 3: Qt.DashDotLine,
                              4: Qt.DashDotDotLine, 5: Qt.CustomDashLine}
            if ind == 5:
                self.lineEdit_customType.setEnabled(True)
                self.label_customType.setEnabled(True)
                custom_type = self.lineEdit_customType.text().replace(',', '')
                custom_type = [int(x) for x in custom_type]
            else:
                self.lineEdit_customType.setEnabled(False)
                self.label_customType.setEnabled(False)
            line = self.plot.listDataItems()[self.line_index]
            pen = line.opts['pen']
            pen.setStyle(pen_style_dict[ind])
            if ind == 5:
                pen.setDashPattern(custom_type)
            line.updateItems(styleUpdate=True)
            # setBrush()
            # setCapStyle()
            # setJoinStyle()

            # line color changed
            color = self.colorButton.color()
            line = self.plot.listDataItems()[self.line_index]
            pen = line.opts['pen']
            pen.setColor(color)
            line.updateItems(styleUpdate=True)

    def range_changed(self, _, range, status):
        if status[0]:
            self.spinBox_xmin.setValue(range[0][0])
            self.spinBox_xmax.setValue(range[0][1])
        if status[1]:
            self.spinBox_ymin.setValue(range[1][0])
            self.spinBox_ymax.setValue(range[1][1])
        # sigRangeChanged: <__main__.CustomViewBox object at 0x000002844222F700> [[-0.5, 5.5], [-0.1, 5.1]] [False, True]

    def interval_changed(self, index):
        if index == 0:
            value = self.spinBox_interval.value()
            self.slider_interval.setValue(int(100*value))
        elif index == 1:
            value = self.slider_interval.value()
            self.spinBox_interval.setValue(round(value/100, 2))
        self.interval = value
        self.update_graph()

    def title_changed(self):
        """ set title font and size """
        text = self.lineEdit_titleContent.text()
        size = self.spinBox_titleSize.value()
        font = self.fontComboBox_title.currentFont()
        titleStyle = {'color': '#000000', 'font-family': font.family(), 'size': str(size) + 'pt'}
        self.plot.setTitle(text, **titleStyle)

    def legend_changed(self):
        """ set legend font, size, column, offset and spacing """
        if hasattr(self, "legend"):
            if self.legend is not None:
                font = self.fontComboBox_font.currentFont()
                size = self.spinBox_fontSize.value()
                # CHANGE THE FONT SIZE AND COLOR OF ALL LEGENDS LABEL
                legendLabelStyle = {'color': '#000000', 'font-family': font.family(), 'size': str(size) + 'pt',
                                    'bold': False,
                                    'italic': False}
                for item in self.legend.items:
                    for single_item in item:
                        if isinstance(single_item, pg.graphicsItems.LabelItem.LabelItem):
                            single_item.setText(single_item.text, **legendLabelStyle)
                # change layout spacing
                hspacing = self.spinBox_legendHspacing.value()
                vspacing = self.spinBox_legendVspacing.value()
                self.legend.layout.setHorizontalSpacing(hspacing)
                self.legend.layout.setVerticalSpacing(vspacing)
                # change columns
                cols = self.spinBox_legendCols.value()
                self.legend.setColumnCount(cols)
                # change offset
                # offset = self.lineEdit_legendOffset.text().replace(',', '')
                # offset = [int(x) for x in offset]
                # self.legend.setOffset(offset)
                # update legend
                self.legend.updateSize()
                self.legend.update()

    def axis_changed(self, index):
        if index == 0:
            min = self.spinBox_xmin.value()
            max = self.spinBox_xmax.value()
            self.plot.setXRange(min, max, padding=0)
        elif index == 1:
            min = self.spinBox_ymin.value()
            max = self.spinBox_ymax.value()
            self.plot.setYRange(min, max, padding=0)
        elif index == 2:
            font = self.fontComboBox_font.currentFont()
            size = self.spinBox_fontSize.value()
            font.setPointSize(size)
            """ set tick font and size """
            self.x_axis.setTickFont(font)
            self.y_axis.setTickFont(font)
            """ set label font and size """
            x_title = self.lineEdit_xtitle.text()
            x_unit = self.lineEdit_xunit.text()
            y_title = self.lineEdit_ytitle.text()
            y_unit = self.lineEdit_yunit.text()
            labelStyle = {'color': '#000000', 'font-family': font.family(), 'font-size': str(size) + 'pt'}
            self.plot.setLabel('bottom', x_title, x_unit, **labelStyle)
            self.plot.setLabel('left', y_title, y_unit, **labelStyle)

            # SET AND CHANGE THE FONT SIZE AND COLOR OF THE PLOT TITLE
            # titleStyle = {'color': '#000000', 'size': '26pt'}
            # p1.setTitle('Active Power', **titleStyle)

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
            self.label.setText(None)    # to make sure plot can be scaled by window size
            self.proxy.disconnect()     # to make sure plot can be scaled by window size
            self.plot.removeItem(self.vLine)
            self.plot.removeItem(self.hLine)
            self.label.hide()

    # CBar pushButton slot | show/hide current subwin colorbar
    def show_colorbar(self, show):
        self.colorbar_visible = show
        if show:
            self.colorBar.show()
            self.colorBar.gradient.setMaxDim(30)
        else:
            self.colorBar.hide()
            self.colorBar.gradient.setMaxDim(0)  # zero gives error

    def show_hist(self, show):
        self.hist_visible = show
        if show:
            self.hist.show()
        else:
            self.hist.hide()

    def update_graph(self):
        # self.plot.clear()

        # Add interval
        self.xx = copy.deepcopy(self.xs)
        self.yy = copy.deepcopy(self.ys)

        mean_value = np.average(self.ys)
        for i in range(len(self.xs)):
            self.yy[i] += mean_value * i * (self.interval / 50)
        """ for test only """
        # colors = ['#08F7FE', '#FE53BB', '#F5D300', '#00ff41', '#FF0000', '#9467bd']
        # names = ['cc1', 'cc2', 'cc3', 'cc4', 'cc5']

        for color, x, y, name, item in zip(self.colors, self.xx, self.yy, self.names, self.plot.listDataItems()):
            if self.color_type != 2:
                pen = pg.mkPen(color=color, width=2)
            else:
                pen = color.getPen(span=(np.min(y), np.max(y)), width=5)
                print(color)
            # self.plot.addItem(pg.PlotDataItem(x, y, pen=pen, name=name))
            item.setData(x, y, pen=pen, name=name)
        self.update_range()

    def update_range(self):
        self.spinBox_xmin.setValue(self.x_axis.range[0])
        self.spinBox_xmax.setValue(self.x_axis.range[1])

        self.spinBox_ymin.setValue(self.y_axis.range[0])
        self.spinBox_ymax.setValue(self.y_axis.range[1])

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

    def init_line_style(self):
        """ for test only """
        # colors = ['#08F7FE', '#FE53BB', '#F5D300', '#00ff41', '#FF0000', '#9467bd', ]
        self.line_style_dict = []
        for i in range(len(self.xs)):
            self.comboBox_lineIndex.addItem(str(i + 1))
            self.line_style_dict.append({'width': 1, 'dash': 0, 'custom dash': None, 'color': QtGui.QColor(self.colors[i])})

    """ 2D Tab """

    def init_UI_2D(self):
        self.__colormap2D = self.cmDictCmap['Perceptually Uniform Sequential'][0]

        """ Controls """
        # colormap |
        cmListCmap = ['viridis', 'plasma', 'inferno', 'magma', 'cividis']
        cmListCmapType = ['Perceptually Uniform Sequential', 'Sequential', 'Sequential (2)', 'Diverging', 'Cyclic', 'Qualitative', 'Miscellaneous']
        self.comboBox_cmap2D.addItems(cmListCmapType)
        self.comboBox_cmap2D_2.addItems(cmListCmap)
        self.comboBox_cmap2D.currentIndexChanged[int].connect(ft.partial(self.load_cmap, 4))
        self.comboBox_cmap2D.currentIndexChanged[int].connect(ft.partial(self.color_changed, 4))
        self.comboBox_cmap2D_2.currentIndexChanged[int].connect(ft.partial(self.color_changed, 4))

        # title |
        self.fontComboBox_title_2D.currentFontChanged.connect(self.title_changed_2D)
        self.groupBox_title_2D.toggled.connect(self.show_title_2D)
        self.spinBox_titleSize_2D.editingFinished.connect(self.title_changed_2D)
        self.lineEdit_titleContent_2D.editingFinished.connect(self.title_changed_2D)
        # axis | visibility
        self.groupBox_x2D.toggled[bool].connect(ft.partial(self.show_axis_2D, 'x'))
        self.groupBox_y2D.toggled[bool].connect(ft.partial(self.show_axis_2D, 'y'))
        # axis | font
        self.fontComboBox_font_2D.setCurrentFont(QtGui.QFont("Times New Roman"))
        self.fontComboBox_font_2D.currentFontChanged.connect(lambda: self.axis_changed_2D(2))
        self.spinBox_fontSize_2D.editingFinished.connect(lambda: self.axis_changed_2D(2))
        # axis | range
        self.spinBox_xmin_2D.editingFinished.connect(lambda: self.axis_changed_2D(0))
        self.spinBox_xmax_2D.editingFinished.connect(lambda: self.axis_changed_2D(0))
        self.spinBox_ymin_2D.editingFinished.connect(lambda: self.axis_changed_2D(1))
        self.spinBox_ymax_2D.editingFinished.connect(lambda: self.axis_changed_2D(1))
        # axis | label
        self.lineEdit_xtitle_2D.editingFinished.connect(lambda: self.axis_changed_2D(2))
        self.lineEdit_xunit_2D.editingFinished.connect(lambda: self.axis_changed_2D(2))
        self.lineEdit_ytitle_2D.editingFinished.connect(lambda: self.axis_changed_2D(2))
        self.lineEdit_yunit_2D.editingFinished.connect(lambda: self.axis_changed_2D(2))
        # colorBar |
        self.pushButton_CBar_2D.toggled.connect(self.show_colorbar_2D)

        """ Graphsic """
        # label | display scanner coordinates
        self.label_2D = pg.LabelItem(justify='right')
        self.graphicsView_2D.addItem(self.label_2D, row=0, col=0)
        self.label_2D.hide()

        # graphicsView |
        self.plot_2D = self.graphicsView_2D.addPlot(row=0, col=0)
        self.x_axis_2D = self.plot_2D.axes['bottom']['item']
        self.y_axis_2D = self.plot_2D.axes['left']['item']
        self.plot_2D.showAxes((True, True, True, True))

        # viewBox |
        # self.view_box.setRange(QRectF(-512, -512, 512, 512), padding=0)
        # self.view_box.setLimits(xMin=-512, xMax=512, yMin=-512, yMax=512, \
        #                         minXRange=3, maxXRange=1024, minYRange=3, maxYRange=1024)
        #
        # self.view_box.setCursor(Qt.CrossCursor)
        # self.view_box.setMouseMode(self.view_box.PanMode)
        self.viewBox_2D = self.plot_2D.vb
        # self.viewBox_2D.setAspectLocked(True)
        self.viewBox_2D.setMouseEnabled(x=True, y=True)
        self.viewBox_2D.setRange(xRange=(0, 100), yRange=(0, 100), padding=0)
        self.viewBox_2D.sigRangeChanged.connect(self.range_changed_2D)
        self.viewBox_2D.disableAutoRange()

        # imageDisplay |
        self.img_display = pg.ImageItem()
        self.viewBox_2D.addItem(self.img_display)
        # colorBar |
        self.colorBar_2D = pg.HistogramLUTItem(levelMode='mono')
        self.colorBar_2D.setImageItem(self.img_display)
        self.graphicsView_2D.addItem(self.colorBar_2D)

        """ set axis title """
        self.plot_2D.setLabel('bottom', 'Bias', 'mV')
        self.plot_2D.setLabel('left', 'dI/dV', 'arb.units')

    def show_colorbar_2D(self, show):
        if show:
            self.colorBar_2D.vb.setFixedWidth(18)
            self.colorBar_2D.show()
        else:
            self.colorBar_2D.vb.setFixedWidth(1)  # zero gives error
            self.colorBar_2D.hide()

    def show_axis_2D(self, axis, show):
        """ select axis visibility by x and y """
        # if axis == 'x':
        #     if show:
        #         self.x_axis_2D.show()
        #     else:
        #         self.x_axis_2D.hide()
        # elif axis == 'y':
        #     if show:
        #         self.y_axis_2D.show()
        #     else:
        #         self.y_axis_2D.hide()
        """ show/hide all 4 axes """
        self.plot_2D.showAxes((show, show, show, show))

    def show_title_2D(self, show):
        if show:
            self.plot_2D.titleLabel.show()
        else:
            self.plot_2D.setTitle(None)

    def title_changed_2D(self):
        """ set title font and size """
        text = self.lineEdit_titleContent_2D.text()
        size = self.spinBox_titleSize_2D.value()
        font = self.fontComboBox_title_2D.currentFont()
        titleStyle = {'color': '#000000', 'font-family': font.family(), 'size': str(size) + 'pt'}
        self.plot_2D.setTitle(text, **titleStyle)

    def axis_changed_2D(self, index):
        if index == 0:
            min = self.spinBox_xmin_2D.value()
            max = self.spinBox_xmax_2D.value()
            self.plot_2D.setXRange(min, max, padding=0)
        elif index == 1:
            min = self.spinBox_ymin_2D.value()
            max = self.spinBox_ymax_2D.value()
            self.plot_2D.setYRange(min, max, padding=0)
        elif index == 2:
            font = self.fontComboBox_font_2D.currentFont()
            size = self.spinBox_fontSize_2D.value()
            font.setPointSize(size)
            """ set tick font and size """
            self.x_axis_2D.setTickFont(font)
            self.y_axis_2D.setTickFont(font)
            """ set label font and size """
            x_title = self.lineEdit_xtitle_2D.text()
            x_unit = self.lineEdit_xunit_2D.text()
            y_title = self.lineEdit_ytitle_2D.text()
            y_unit = self.lineEdit_yunit_2D.text()
            labelStyle = {'color': '#000000', 'font-family': font.family(), 'font-size': str(size) + 'pt'}
            self.plot_2D.setLabel('bottom', x_title, x_unit, **labelStyle)
            self.plot_2D.setLabel('left', y_title, y_unit, **labelStyle)

    def range_changed_2D(self, _, range, status):
        if status[0]:
            self.spinBox_xmin_2D.setValue(range[0][0])
            self.spinBox_xmax_2D.setValue(range[0][1])
        if status[1]:
            self.spinBox_ymin_2D.setValue(range[1][0])
            self.spinBox_ymax_2D.setValue(range[1][1])

    def update_graph_2D(self):
        self.colorBar_2D.gradient.setColorMap(self.__colormap2D)
        self.img_display.setImage(self.data2D)
        self.colorBar_2D.setLevels(self.data2D.min(), self.data2D.max())
        self.viewBox_2D.setRange(QRectF(0, 0, self.img_display.width(), self.img_display.height()), padding=0)

    """ 3D Tab """
    def init_UI_3D(self):
        self.type3D = 0
        self.__colormap3D = mpl.cm.seismic

        # comboBox |
        self.comboBox_3dtype.currentIndexChanged[int].connect(self.type3d_changed)
        cmListCmap = ['viridis', 'plasma', 'inferno', 'magma', 'cividis']
        cmListCmapType = ['Perceptually Uniform Sequential', 'Sequential', 'Sequential (2)', 'Diverging', 'Cyclic', 'Qualitative', 'Miscellaneous']
        self.comboBox_cmap3D.addItems(cmListCmapType)
        self.comboBox_cmap3D_2.addItems(cmListCmap)
        self.comboBox_cmap3D.currentIndexChanged[int].connect(ft.partial(self.load_cmap, 3))
        self.comboBox_cmap3D.currentIndexChanged[int].connect(ft.partial(self.color_changed, 3))
        self.comboBox_cmap3D_2.currentIndexChanged[int].connect(ft.partial(self.color_changed, 3))

        """ canvas """
        self.lay3d = QGridLayout()
        self.dockWidget_3.widget().setLayout(self.lay3d)

        self.canvas3D = MplCanvas(self, width=5, height=4, dpi=100)
        # self.canvas3D.setStyleSheet("background-color:transparent;")
        # self.canvas3D.ax3D.patch.set_alpha(0)
        self.lay3d.addWidget(self.canvas3D, 0, 0, 1, 1)

    def type3d_changed(self, index):
        self.type3D = index
        self.update_graph_3D()

    def update_graph_3D(self):
        y = np.linspace(0, self.xyz.shape[0] * (int(self.interval) + 1) - 1, self.xyz.shape[0] * (int(self.interval) + 1), endpoint=True)
        x = np.linspace(0, self.xyz.shape[1], self.xyz.shape[1], endpoint=True)
        x, y = np.meshgrid(x, y)

        for i in range(self.xyz.shape[0] - 1, -1, -1):
            b = np.array(self.xyz[i, :].tolist() * int(self.interval)).reshape(int(self.interval), self.xyz.shape[1])
            self.xyz = np.insert(self.xyz, i, values=b, axis=0)

        self._X = x
        self._Y = y
        self._Z = copy.deepcopy(self.xyz)

        self.canvas3D.ax3D.clear()
        if self.type3D == 0:  # 3D surface
            normDef = mpl.colors.Normalize(vmin=self._Z.min(), vmax=self._Z.max())
            series3D = self.canvas3D.ax3D.plot_surface(self._X, self._Y, self._Z,
                                              cmap=self.__colormap3D, linewidth=1, picker=True,
                                             norm=normDef, antialiased=False)   # set antialiased=False to avoid grids
            self.canvas3D.ax3D.set_title("3D surface")
        elif self.type3D == 1:  # 3D wireframe
            series3D = self.canvas3D.ax3D.plot_wireframe(self._X, self._Y, self._Z,
                                                cmap=self.__colormap3D, linewidth=1, picker=True)
            self.canvas3D.ax3D.set_title("3D wireframe")
        elif self.type3D == 2:  # 3D scatter
            series3D = self.canvas3D.ax3D.scatter(self._X, self._Y, self._Z,
                                         s=15, c='r', picker=True)
            self.canvas3D.ax3D.set_title("3D scatter")

        self.canvas3D.ax3D.set_xlabel("axis-X")
        self.canvas3D.ax3D.set_ylabel("axis-Y")
        self.canvas3D.ax3D.set_zlabel("axis-Z")
        self.canvas3D.redraw()

    @pyqtSlot(bool)
    def on_checkBox_flipZ_clicked(self, checked):
        self.canvas3D.ax3D.invert_zaxis()  # toggle
        self.canvas3D.redraw()

    @pyqtSlot(bool)
    def on_checkBox_grid_clicked(self, checked):
        self.canvas3D.ax3D.grid(checked)
        self.canvas3D.redraw()

    @pyqtSlot(bool)
    def on_checkBox_axes_clicked(self, checked):
        if checked:
            self.canvas3D.ax3D.set_axis_on()
        else:
            self.canvas3D.ax3D.set_axis_off()
        self.canvas3D.redraw()

    def close(self) -> bool:
        self.plot.clear()
        self.plot_2D.clear()



if __name__ == "__main__":
    # QtCore.QCoreApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling)
    app = QApplication(sys.argv)
    window = myDrawSpc()
    """ for test only """
    window.init_data(0,0,0,0)
    window.update_graph()
    window.update_graph_2D()
    window.update_graph_3D()

    window.show()
    sys.exit(app.exec_())
