# -*- coding: utf-8 -*-
"""
@Date     : 2021/4/12 17:05:29
@Author   : milier00
@FileName : GraphWindow.py
"""
import sys
import imageio
sys.path.append("./ui/")
sys.path.append("./model/")
from PyQt5.QtWidgets import QApplication, QWidget, QMenu, QMessageBox, QButtonGroup, QAction, \
    QAbstractItemView, QGridLayout, QShortcut, QListWidget, QFileDialog, QInputDialog
from PyQt5.QtCore import pyqtSignal, Qt, QRectF
from PyQt5.QtGui import  QKeySequence
from pyqtgraph.Qt import QtGui, QtCore
from images import myImages
from GraphWindow_ui import Ui_Graph
from DataSlicing2D import myDataSlicing2D
from DataSlicing import myDataSlicing
from customROI import *
from Data import *
from func2D import *
import cv2 as cv
import numpy as np
import functools as ft
import pyqtgraph as pg
from scipy.ndimage import *
import ctypes
from skimage import exposure, img_as_float
import imageio
import copy
import os



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

class myGraphWindow(QWidget, Ui_Graph):
    # Common signal
    close_signal = pyqtSignal()
    list_changed_signal = pyqtSignal()
    update_display_signal = pyqtSignal()

    def __init__(self, data_list, data_paths):
        super().__init__()
        self.setupUi(self)
        self.init_UI(data_list, data_paths)
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("myappid")

    def init_UI(self, data_list, data_paths):
        self.move(850, 50)         # Init ui position
        self.resize(900, 700)
        self.setAttribute(Qt.WA_DeleteOnClose)  # make sure the window object is deleted after close

        self.parent_data_list = data_list
        self.parent_data_paths = data_paths

        self.plot_list = []         # expanded names displayed in plot list
        self.displayed_plot_list = []
        self.parent_name = []       # parent names in plot list
        self.data = []              # self.data(MappingData) <---> self.parent_name
        self.expanded_plot_list = [] # expanded names of data, for operation mode 3 only
        self.expanded_plot_data = [] # self.expanded_plot_list <---> self.expadned_plot_data (list of 2D array)
        self.processed_list = []    # parent names displayed in processed list
        self.processed_data = []    # self.processed_data(MappingResult) <---> self.processed_list
        self.expanded_pro_list = [] # expanded names of processed data, for operation mode 3 only
        self.expanded_pro_data = [] # self.expanded_pro_list <---> self.expanded_pro_data (list of 2D array)

        self.current_list = None
        self.energy_index = 0

        self.contrast = 200
        self.opacity = 100
        self.color_map_index = 83
        self.operating_mode_1 = 0       # 0: all map, 1: single map
        self.operating_mode_2 = 0       # 0: global, 1: roi
        self.ifft_mode = False
        self.part_type = 0              # 0: square, 1: circle
        self.linecut_width = 1          # default linecut width = 1
        self.rec_flag = False           # 0: no recording, 1: recording

        self.func2D = myFunc()
        self.myimg = myImages()

        # signals |
        QApplication.instance().focusObjectChanged.connect(self.focus_changed)
        # listWidget | Plot list
        self.listWidget = DropInList()
        self.listWidget.setObjectName('listWidget')
        self.listWidget.list_changed_signal.connect(self.pre_treat_list)
        self.listWidget.itemClicked.connect(ft.partial(self.update_graph, 0))
        self.listWidget.itemSelectionChanged.connect(self.edit_selection)
        self.listWidget.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.listWidget.setContextMenuPolicy(Qt.CustomContextMenu)
        self.listWidget.customContextMenuRequested[QtCore.QPoint].connect(lambda: self.rightMenuShow(0))
        grid = QGridLayout()
        grid.addWidget(self.listWidget, 1, 1)
        self.groupBox.setLayout(grid)

        # listWidget | Processed list
        self.listWidget_Processed.itemClicked.connect(ft.partial(self.update_graph, 1))
        # self.listWidget_Processed.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.listWidget_Processed.setContextMenuPolicy(Qt.CustomContextMenu)
        self.listWidget_Processed.customContextMenuRequested[QtCore.QPoint].connect(lambda: self.rightMenuShow(1))

        # scrollBar |
        self.scrollBar_Energy.valueChanged.connect(self.update_graph_)
        self.scrollBar_Opacity.valueChanged.connect(self.update_opacity)
        self.scrollBar_Contrast.valueChanged.connect(self.update_contrast)

        # graphicsView
        self.view_box = self.graphicsView.addViewBox()
        self.graphicsView.ci.layout.setContentsMargins(0, 0, 0, 0)     # eliminate the border
        self.graphicsView.ci.layout.setSpacing(0)                      # eliminate the border
        self.view_box.setRange(QRectF(-512, -512, 512, 512), padding=0)
        self.view_box.setLimits(xMin=-512, xMax=512, yMin=-512, yMax=512, \
                                minXRange=3, maxXRange=1024, minYRange=3, maxYRange=1024)
        self.view_box.setAspectLocked(True)
        self.view_box.setCursor(Qt.CrossCursor)
        self.view_box.setMouseMode(self.view_box.PanMode)

        self.img_display = pg.ImageItem()
        self.view_box.addItem(self.img_display, ignoreBounds=True)  # ignoreBounds is unclear, Flase by default, works same

        # ROI | image box
        self.roi = pg.ROI([0, 0], [10, 10], resizable=False, removable=True, handlePen=(255, 255, 255, 0))
        self.roi.hide()

        # ROI | define pens
        blue_pen = pg.mkPen((100, 200, 255, 255), width=1)
        green_pen = pg.mkPen((150, 220, 0, 255), width=1)
        yellow_pen = pg.mkPen((255, 234, 0, 255), width=2)
        purple_pen = pg.mkPen((220, 180, 255, 255), width=2)

        # ROI | Interest part / Point
        self.part_s = pg.ROI([0, 0], [200, 200], pen=blue_pen, scaleSnap=True)
        # self.part_s = CustomRectangularROI([0, 0], [200, 200], pen=blue_pen, scaleSnap=True)
        self.part_s.addScaleHandle([0, 0], [1, 1], index=0)
        self.part_s.addScaleHandle([1, 1], [0, 0], index=1)
        self.part_s.setZValue(11)
        self.view_box.addItem(self.part_s)
        self.part_s.hide()

        # ROI | Interest part / Circle
        self.part_c = pg.CircleROI([0, 0], [100, 100], pen=blue_pen, scaleSnap=True)
        self.part_c.setZValue(11)
        self.view_box.addItem(self.part_c)
        self.part_c.hide()

        # ROI | Q-point
        self.qpoint = CrossCenterROI2([100,100], [10,10], pen=yellow_pen)
        self.qpoint.setZValue(11)
        self.view_box.addItem(self.qpoint)
        self.qpoint.removeHandle(0)
        self.qpoint.addCustomHandle2(info={'type': 't', 'pos': [0.5, 0.5]}, index=3)
        self.qpoint.movePoint(self.qpoint.getHandles()[0], [100, 100])
        self.qpoint.getHandles()[0].setPen(yellow_pen)
        self.qpoint.hide()

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

        # pushButton | View Control
        self.pushButton_Rotate.clicked.connect(self.rotate)
        self.pushButton_FullView.clicked.connect(self.full_view)
        self.pushButton_copy.clicked.connect(lambda: self.clone_stamp(0))
        self.pushButton_paste.clicked.connect(lambda: self.clone_stamp(1))

        # radioButton | View Control
        self.pallet_group = QButtonGroup()
        self.pallet_group.addButton(self.radioButton_Color, 0)
        self.pallet_group.addButton(self.radioButton_Gray, 1)
        self.pallet_group.buttonToggled[int, bool].connect(self.pallet_changed)

        # checkBox | View Control
        self.filter_group = QButtonGroup()
        self.filter_group.addButton(self.checkBox_Reverse, 0)
        self.filter_group.addButton(self.checkBox_Illuminated, 1)
        self.filter_group.addButton(self.checkBox_PlaneFit, 2)
        self.filter_group.setExclusive(False)
        self.filter_group.buttonToggled[int, bool].connect(self.filter_changed)

        # toolButton | View Control
        self.init_colormap()
        # signals |
        self.update_display_signal.connect(self.update_display)

        # keyboard event |
        QShortcut(QtGui.QKeySequence('Up', ), self, lambda: self.select_file(0))
        QShortcut(QtGui.QKeySequence('Down', ), self, lambda: self.select_file(1))
        QShortcut(QtGui.QKeySequence('Left', ), self, lambda: self.select_file(0))
        QShortcut(QtGui.QKeySequence('Right', ), self, lambda: self.select_file(1))

        self.shortcut = QShortcut(QKeySequence('Delete'), self)
        self.shortcut.activated.connect(self.edit_delete)

        self.shortcut_copy = QShortcut(QKeySequence('Shift+C'), self)
        self.shortcut_copy.activated.connect(lambda: self.clone_stamp(0))
        self.shortcut_paste = QShortcut(QKeySequence('Shift+V'), self)
        self.shortcut_paste.activated.connect(lambda: self.clone_stamp(1))

        self.shortcut_align = QShortcut(QKeySequence('Space'), self)
        self.shortcut_align.activated.connect(self.align2pixel)

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
        
    # Plot List | Up/Down and Left/Right keyboard slot
    def select_file(self, index):
        if index == 0:  # previous
            if self.listWidget.currentRow() - 1 == -1:
                self.listWidget.setCurrentRow(len(self.plot_list) - 1)
            else:
                self.listWidget.setCurrentRow(self.listWidget.currentRow() - 1)
        elif index == 1:  # next
            if self.listWidget.currentRow() + 1 == len(self.plot_list):
                self.listWidget.setCurrentRow(0)
            else:
                self.listWidget.setCurrentRow(self.listWidget.currentRow() + 1)
        self.update_graph(0)

    # focus object changed
    def focus_changed(self, obj):
        if obj != None:
            if obj == self.listWidget or obj == self.listWidget_Processed:
                self.current_list = obj

    # Plot List(0) & Processed List(1) | right click menu, 0: Plot list; 1: Processed list
    def rightMenuShow(self, index):
        if index == 0:  # plot list
            rightMenu = QMenu(self.listWidget)
            deleteAction = QAction("Delete", self, triggered=lambda: self.delete(0))
            rightMenu.addAction(deleteAction)
            if self.listWidget.currentItem().text()[0] != '\t':
                rightMenu.exec_(QtGui.QCursor.pos())
        elif index == 1:  # processed list
            rightMenu = QMenu(self.listWidget_Processed)
            saveasAction = QAction("Save as", self, triggered=self.save_as)
            deleteAction = QAction("Delete", self, triggered=lambda: self.delete(1))
            renameAction = QAction("Rename", self, triggered=self.rename)
            rightMenu.addAction(saveasAction)
            rightMenu.addAction(deleteAction)
            rightMenu.addAction(renameAction)
            rightMenu.exec_(QtGui.QCursor.pos())

    # Processed List(1) | save as
    def save_as(self):
        # find selected data
        items = self.listWidget_Processed.selectedItems()
        for item in items:
            for plot in self.processed_list:
                if plot.find(item.text()) != -1:
                    file_name = item.text()
                    data2save = self.processed_data[self.processed_list.index(item.text())]
                    dir, file = os.path.split(data2save.parent_path)
                    default_name = self.get_save_name(dir, file_name)
                    fileName, ok = QFileDialog.getSaveFileName(self, "Save", default_name, "MAT(*.mat);; DAT(*.dat);; PNG(*.png);; JPEG(*.jpeg);; EPS(*.eps)")
                    if fileName[-4:] == '.mat':
                        self.func2D.save_mat(fileName, data2save)
                    elif fileName[-4:] == '.dat':
                        if data2save.result.shape[0] > 1:
                            for i in range(data2save.result.shape[0]):
                                np.savetxt(fileName[:-4]+'-No'+str(i).zfill(2)+'.dat', data2save.result[i])
                        else:
                            np.savetxt(fileName, data2save.result[0])
                    else:
                        if data2save.result.shape[0] > 1:
                            for i in range(data2save.result.shape[0]):
                                imageio.imwrite(fileName[:-4] + '-No'+str(i).zfill(2) + fileName[-4:], data2save.result[i])
                        else:
                            imageio.imwrite(fileName, data2save.result[0])

    # get default file name when save requested
    def get_save_name(self, path, name):
        for root, dirs, files in os.walk(path, topdown=False):
            exist_num = 0
            for file in files:
                if file.find(name) != -1:
                    exist_num += 1
        return name.replace('.nstm','') + '-' + str(exist_num).zfill(2)

    # Delete | keyboard slot, figure out which list to react
    def edit_delete(self):
        if self.current_list == self.listWidget:
            self.delete(0)
        elif self.current_list == self.listWidget_Processed:
            self.delete(1)

    # Plot List(0) & Processed List(1) | delete action slot
    def delete(self, index):
        if index == 0:  # plot list
            items = self.listWidget.selectedItems()

            for item in items:
                # get list of index to delete
                delete_items = []

                if item.text()[0] != '\t':
                    for plot in self.plot_list:
                        if plot.find(item.text()) != -1:
                            delete_items.append(plot)

                # delete from listWidget
                for i in range(len(self.plot_list) - 1, -1, -1):
                    if self.plot_list[i] in delete_items:
                        self.plot_list.pop(i)

                # make sure multi-channel file names doesn't exit alone
                multi_file_names = [plot for plot in self.plot_list if plot[0] != '\t']
                multi_file_num = [0] * len(multi_file_names)
                multi_file_left = [0] * len(multi_file_names)

                for i in range(len(multi_file_names)):
                    for plot in self.plot_list:
                        if plot.find(multi_file_names[i]) != -1:
                            multi_file_left[i] += 1

                for i in range(len(multi_file_names)):
                    for file in self.parent_data_list:
                        if file.find(multi_file_names[i]) != -1:
                            multi_file_num[i] += 1
                    if multi_file_num[i] > 1 and multi_file_left[i] == 1:
                        index = self.plot_list.index(multi_file_names[i])
                        self.plot_list.pop(index)

            self.listWidget.clear()
            self.listWidget.addItems(self.plot_list)
            self.refresh_list(0)

        elif index == 1:  # processed list
            items = self.listWidget_Processed.selectedItems()

            for item in items:
                # get list of index to delete
                delete_items = []
                for plot in self.processed_list:
                    if plot.find(item.text()) != -1 and len(plot) == len(item.text()):
                        delete_items.append(plot)

                # delete from listWidget
                for i in range(len(self.processed_list) - 1, -1, -1):
                    if self.processed_list[i] in delete_items:
                        self.processed_list.pop(i)
                        self.processed_data.pop(i)

            self.listWidget_Processed.clear()
            self.listWidget_Processed.addItems(self.processed_list)
            self.refresh_list(1)

    # Processed List | rename action slot
    def rename(self):
        item = self.listWidget_Processed.currentItem()
        text, okPressed = QInputDialog.getText(self, "New name", "New name:", text=item.text())
        if okPressed and text != '':
            item.setText(text)
        self.refresh_list(1)

    # Plot List | set selection by logic
    def edit_selection(self):
        items = self.listWidget.selectedItems()
        for item in items:
            if item.text()[0] != '\t':
                for i in range(len(self.plot_list)):
                    if self.plot_list[i].find(item.text()) != -1:
                        self.listWidget.item(i).setSelected(True)

    # Plot list | drop items signal slot
    def pre_treat_list(self):
        # deal with multi-channel data
        for row in range(self.listWidget.count()):
            for data in self.parent_data_list:
                if data.find(self.listWidget.item(row).text()) != -1 and data.find('_No') != -1:
                    self.listWidget.addItem(data)
        self.refresh_list(0)

    # Plot List(0) & Processed List(1) | pre_treat_list slot and menu add2win slot
    def refresh_list(self, index):

        if index == 0:  # Plot list
            # get current plot list from listWidget
            self.plot_list = []
            for row in range(self.listWidget.count()):
                if self.listWidget.item(row).text().find('.nstm') != -1:
                    self.plot_list.append(self.listWidget.item(row).text())

            # remove repeated items
            self.plot_list = list(set(self.plot_list))
            # sort plot list
            self.plot_list = sorted(self.plot_list, key=self.parent_data_list.index)
            # add items to listWidget
            self.listWidget.clear()
            self.listWidget.addItems(self.plot_list)
            self.listWidget.setCurrentRow(-1)
            self.displayed_plot_list.clear()
            self.displayed_plot_list = copy.deepcopy(self.plot_list)
            self.refresh_data()

        elif index == 1:  # Processed list

            self.processed_list = []
            for row in range(self.listWidget_Processed.count()):
                self.processed_list.append(self.listWidget_Processed.item(row).text())
            self.listWidget_Processed.clear()
            self.listWidget_Processed.addItems(self.processed_list)

            # refresh expanded name list and data list for operation mode 3
            self.expanded_pro_list = []
            self.expanded_pro_data = []
            for i in range(len(self.processed_data)):
                if self.processed_data[i].result.shape[0] == 1:
                    self.expanded_pro_data.append(self.processed_data[i].result[0])
                    self.expanded_pro_list.append(self.processed_list[i])
                elif self.processed_data[i].result.shape[0] > 1:
                    for j in range(self.processed_data[i].result.shape[0]):
                        self.expanded_pro_list.append(self.processed_list[i]+'_No'+str(j).zfill(2))
                        self.expanded_pro_data.append(self.processed_data[i].result[j])

    # Plot list | reload data after refresh_list
    def refresh_data(self):
        self.data.clear()
        self.parent_name.clear()
        # load all data in plot list (parent_name <--> self.data)
        for plot in self.plot_list:
            if plot[0] != '\t':
                self.parent_name.append(plot)
                data = MappingData(self.parent_data_paths[self.parent_data_list.index(plot)])
                self.data.append(data)

        # refresh expanded name list and data list for operation mode 3
        self.expanded_plot_list = []
        self.expanded_plot_data = []
        for i in range(len(self.parent_name)):
            if self.data[i].child_num == 1:
                self.expanded_plot_list.append(self.parent_name[i]+'_No00')
                self.expanded_plot_data.append(self.data[i].child_data[0])
            elif self.data[i].child_num > 1:
                for j in range(self.data[i].child_num):
                    self.expanded_plot_list.append(self.parent_name[i]+'_No'+str(j).zfill(2))
                    self.expanded_plot_data.append(self.data[i].child_data[j])

    # Plot list(0) & Processed list(1) | single click slot
    def update_graph(self, index):
        if index == 0:  # plot list single clicked
            # get current item
            if len(self.listWidget.selectedItems()) > 1:
                item = self.listWidget.selectedItems()[0]
            elif len(self.listWidget.selectedItems()) == 1:
                item = self.listWidget.currentItem()

            if item.text()[0] == '\t':
                self.energy_index = int(item.text()[-2:])
                parent_index = self.parent_name.index(item.text()[1:-5])
         
            elif item.text()[0] != '\t':
                self.energy_index = 0
                parent_index = self.parent_name.index(item.text())
                
            self.scrollBar_Energy.setMaximum(self.data[parent_index].child_num - 1)
            self.scrollBar_Energy.setValue(self.energy_index)

            bias, iset = (self.data[parent_index].energy[self.energy_index], self.data[parent_index].iset[self.energy_index])
            self.label_Energy.setText("<span style='font-size: 9pt'><b>%0.3fV %.3fnA</b></span>" % (bias, iset))
            self.label_Scale.setText(str(self.data[parent_index].scale))

            self.raw_img = self.data[parent_index].child_data[self.energy_index]
            self.current_img = self.myimg.prepare_data(self.myimg.partial_renormalize(self.data[parent_index].child_data_bit[self.energy_index]))
            self.current_img_tmp = copy.deepcopy(self.current_img)

            self.update_display_signal.emit()

        elif index == 1:    # processed list single click slot
            # get current item
            if len(self.listWidget_Processed.selectedItems()) > 1:
                item = self.listWidget_Processed.selectedItems()[0]
            elif len(self.listWidget_Processed.selectedItems()) == 1:
                item = self.listWidget_Processed.currentItem()

            data2view = self.processed_data[self.processed_list.index(item.text())]
            if data2view.result.shape[0] == 1:    # single parent (only 1 child is itself)
                self.energy_index = 0
                self.scrollBar_Energy.setValue(0)
                self.scrollBar_Energy.setMaximum(0)
            elif data2view.result.shape[0] > 1:    # normal parent
                self.energy_index = 0
                self.scrollBar_Energy.setValue(0)
                self.scrollBar_Energy.setMaximum(len(data2view.energy)-1)

            bias, iset = (data2view.energy[0], data2view.iset[0])
            self.label_Energy.setText("<span style='font-size: 9pt'><b>%0.3fV %.3fnA</b></span>" % (bias, iset))
            self.label_Scale.setText(str(data2view.scale))

            self.raw_img = data2view.result[0]
            self.current_img = self.myimg.prepare_data(self.myimg.partial_renormalize(self.raw_img))
            self.current_img_tmp = copy.deepcopy(self.current_img)

            self.update_display_signal.emit()

    # energy scrollBar | energy valueChanged slot
    def update_graph_(self):
        if self.current_list == self.listWidget:
            # get current item
            if len(self.listWidget.selectedItems()) > 1:
                item = self.listWidget.selectedItems()[0]
            elif len(self.listWidget.selectedItems()) == 1:
                item = self.listWidget.currentItem()

            self.energy_index = self.scrollBar_Energy.value()
            if item.text()[0] == '\t':
                parent_index = self.parent_name.index(item.text()[1:-5])
                self.listWidget.setCurrentRow(self.plot_list.index('\t'+item.text()[1:-5] + '_No' + str(self.energy_index).zfill(2)))
            elif item.text()[0] != '\t':
                parent_index = self.parent_name.index(item.text())
                self.listWidget.setCurrentRow(self.plot_list.index('\t'+item.text() + '_No' + str(self.energy_index).zfill(2)))

            bias, iset = (self.data[parent_index].energy[self.energy_index], self.data[parent_index].iset[self.energy_index])
            self.label_Energy.setText("<span style='font-size: 9pt'>%0.3fV %.3fnA</span>" % (bias, iset))
            self.label_Scale.setText(str(self.data[parent_index].scale))

            self.raw_img = self.data[parent_index].child_data[self.energy_index]
            self.current_img = self.myimg.prepare_data(self.myimg.partial_renormalize(self.data[parent_index].child_data_bit[self.energy_index]))
            self.current_img_tmp = copy.deepcopy(self.current_img)

            self.update_display_signal.emit()

        elif self.current_list == self.listWidget_Processed:
            # get current item
            if len(self.listWidget_Processed.selectedItems()) > 1:
                item = self.listWidget_Processed.selectedItems()[0]
            elif len(self.listWidget_Processed.selectedItems()) == 1:
                item = self.listWidget_Processed.currentItem()
            elif len(self.listWidget_Processed.selectedItems()) == 0:
                return

            self.energy_index = self.scrollBar_Energy.value()
            bias, iset = (self.processed_data[self.processed_list.index(item.text())].energy[self.energy_index],
                          self.processed_data[self.processed_list.index(item.text())].iset[self.energy_index])
            self.label_Energy.setText("<span style='font-size: 9pt'>%0.3fV %.3fnA</span>" % (bias, iset))
            self.label_Scale.setText(str(self.processed_data[self.processed_list.index(item.text())].scale))

            self.raw_img = self.processed_data[self.processed_list.index(item.text())].result[self.energy_index]
            self.current_img = self.myimg.prepare_data(self.myimg.partial_renormalize(self.raw_img))
            self.current_img_tmp = copy.deepcopy(self.current_img)

            self.update_display_signal.emit()

    # Opacity scrollBar slot |
    def update_opacity(self, opacity):
        ''' Change opacity of imageItem '''
        self.opacity = opacity
        self.update_display_signal.emit()

    # Contrast scrollBar slot |
    def update_contrast(self, contrast):
        ''' Change contrast of imageItem '''
        self.contrast = contrast
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

    # shortcut "Space" | align part_s to pixels
    def align2pixel(self):
        x1 = int(self.part_s.pos()[0])
        y1 = int(self.part_s.pos()[1])
        x3 = int(self.part_s.getHandles()[1].pos()[0])
        y3 = int(self.part_s.getHandles()[1].pos()[1])

        self.part_s.movePoint(self.part_s.getHandles()[0], [x1, y1], finish=False)
        self.part_s.movePoint(self.part_s.getHandles()[1], [x3 + x1, y3 + y1])
        self.part_s.setPos([x1, y1])

    # reset button slot | make image full view
    def full_view(self):
        '''Zoom in to whole image. '''
        self.img_display.setRect(QRectF(0, 0, self.img_display.width(), self.img_display.height()))
        self.view_box.setRange(QRectF(0, 0, self.img_display.width(), self.img_display.height()), padding=0)

    # rotate button slot | rotate
    def rotate(self):
        '''Rotate image 90° counterclockwise.'''
        self.roi.rotate(90, center=[0.5, 0.5])

    # pallet radioButton slot | gray, color
    def pallet_changed(self, status):
        '''Change color map for displayed image: afm-hot or gray.'''
        if status:
            self.update_display_signal.emit()

    # Color map slot | multiple colormap
    def color_map(self, index):
        self.color_map_index = index
        self.update_display_signal.emit()

    # filter checkBox slot | reverse, Illuminated and Plane fit
    def filter_changed(self, index, status):
        '''Process image based on checkBox signal: Reverse, Illuminated and Plane fit.'''
        # re-initialize current img
        # self.current_img = self.myimg.prepare_data(self.myimg.partial_renormalize(self.raw_img))
        self.current_img = copy.deepcopy(self.current_img_tmp)

        # Set mutual exclusion of Illuminated and Plane fit
        if self.checkBox_Illuminated.isChecked():
            if index == 2 and status:
                self.checkBox_Illuminated.setChecked(False)
                self.checkBox_PlaneFit.setChecked(True)
            else:
                self.checkBox_Illuminated.setChecked(True)
                self.checkBox_PlaneFit.setChecked(False)

        if self.checkBox_PlaneFit.isChecked():
            if index == 1 and status:
                self.checkBox_PlaneFit.setChecked(False)
                self.checkBox_Illuminated.setChecked(True)
            else:
                self.checkBox_PlaneFit.setChecked(True)
                self.checkBox_Illuminated.setChecked(False)

        # CheckBox status variable
        if_reverse = self.checkBox_Reverse.isChecked()
        if_illuminated = self.checkBox_Illuminated.isChecked()
        if_plane_fit = self.checkBox_PlaneFit.isChecked()

        # Get current selected display mode
        if if_reverse and (not if_plane_fit) and (not if_illuminated):
            reverse_gray_img = self.myimg.gray2reverse(self.current_img)
            self.current_img = reverse_gray_img
        elif if_illuminated and (not if_plane_fit) and (not if_reverse):
            illuminated_img = self.myimg.illuminated(self.current_img)
            self.current_img = illuminated_img
        elif if_plane_fit and (not if_illuminated) and (not if_reverse):
            planefit_img = self.myimg.plane_fit(self.current_img)
            self.current_img = planefit_img
        elif if_plane_fit and if_illuminated and (not if_reverse):
            planefit_img = self.myimg.plane_fit(self.current_img)
            illuminated_planefit_img = self.myimg.illuminated(planefit_img)
            self.current_img = illuminated_planefit_img
        elif if_reverse and if_plane_fit and (not if_illuminated):
            planefit_img = self.myimg.plane_fit(self.current_img)
            reverse_planefit_img = self.myimg.gray2reverse(planefit_img)
            self.current_img = reverse_planefit_img
        elif if_reverse and if_illuminated and (not if_plane_fit):
            illuminated_img = self.myimg.illuminated(self.current_img)
            revered_illuminated_img = self.myimg.gray2reverse(illuminated_img)
            self.current_img = revered_illuminated_img
        elif if_reverse and if_illuminated and if_plane_fit:
            planefit_img = self.myimg.plane_fit(self.current_img)
            illuminated_planefit_img = self.myimg.illuminated(planefit_img)
            revered_illuminated_planefit_img = self.myimg.gray2reverse(illuminated_planefit_img)
            self.current_img = revered_illuminated_planefit_img
        elif (not if_reverse) and (not if_illuminated) and (not if_plane_fit):
            self.current_img = copy.deepcopy(self.current_img)

        self.update_display_signal.emit()

    # update display image
    def update_display(self):
        '''Update image based on user selected filter and colormap.'''
        if self.radioButton_Gray.isChecked():
            psudo_gray_img = cv.cvtColor(self.current_img, cv.COLOR_GRAY2BGR)
            self.color_current_img = psudo_gray_img
        elif self.radioButton_Color.isChecked():
            color_img = self.myimg.color_map(self.current_img, self.color_map_index)
            self.color_current_img = color_img

        # set contrast
        img = img_as_float(self.color_current_img)
        self.color_current_img = exposure.adjust_gamma(img, self.contrast / 200)
        # set opacity
        self.img_display.setOpacity(self.opacity / 100)
        # set image
        self.img_display.setImage(self.color_current_img)
        self.view_box.setRange(QRectF(0, 0, self.img_display.width(), self.img_display.height()), padding=0)
        self.init_roi()

    # obtain target data for OP1 & OP2
    def get_target_data(self):
        if self.operating_mode_1 == 0:   # single parent global mode
            if self.current_list == self.listWidget:    # plot list
                if len(self.listWidget.selectedItems()) == 0:
                    QMessageBox.warning(None, "Data Selection", 'Please select only 1 data in plot list!', QMessageBox.Ok)
                    return
                else:
                    if self.listWidget.currentItem().text()[0] == '\t':
                        name = self.listWidget.currentItem().text()[1:-5]
                    else:
                        name = self.listWidget.currentItem().text()
                    data = MappingResult(self.data[self.parent_name.index(name)], -1)
            else:   # processed list
                name = self.listWidget_Processed.currentItem().text()
                pro_data = self.processed_data[self.processed_list.index(name)]
                if name.find('_No') != -1:  # single processed parent
                    index = int(name[-2:])
                    data = MappingResult(pro_data.parent_data, index)
                    data.target = [pro_data.result[0]]
                else:  # normal processed parent
                    data = MappingResult(pro_data.parent_data, -1)
                    data.target = []
                    for i in range(pro_data.result.shape[0]):
                        data.target.append(pro_data.result[i])
        elif self.operating_mode_1 == 1: # single energy global mode
            if self.current_list == self.listWidget:
                if self.listWidget.currentItem().text()[0] == '\t':
                    pname = self.listWidget.currentItem().text()[1:-5]
                    name = self.listWidget.currentItem().text()[1:]
                    index = int(self.listWidget.currentItem().text()[-2:])
                else:
                    pname = self.listWidget.currentItem().text()
                    name = self.listWidget.currentItem().text()+'No_00'
                    index = 0
                data = MappingResult(self.data[self.parent_name.index(pname)], index)
                data.get_energy(self.data[self.parent_name.index(pname)], index)
            else:   # make a new MappingResult data type and rewrite target
                name = self.listWidget_Processed.currentItem().text()
                pro_data = self.processed_data[self.processed_list.index(name)]
                if name.find('_No') != -1:  # single processed parent
                    index = int(name[-2:])
                    data = MappingResult(pro_data.parent_data, index)
                    data.target = [pro_data.result[0]]
                else:                       # normal processed parent
                    index = self.scrollBar_Energy.value()
                    data = MappingResult(pro_data.parent_data, index)
                    data.target = [pro_data.result[index]]
        return data, name

    # get non-repetitive name for new data in processed list
    def avoid_repeat_name(self, target_name):
        count = 0
        for name in self.processed_list:
            if name.find(target_name) != -1:
                count += 1
        if count != 0:
            final_name = target_name + '_' + str(count).zfill(2)
            return final_name
        else:
            return target_name

    # get indices of circle boudary within ret0
    def get_circle_boundary(self, ret0):
        indices = np.where(ret0.flatten() == 0)[0]
        coordinates = []
        for indice in indices:
            coordinates.append(np.unravel_index(indice, ret0.shape))
        return coordinates

    # add wider border to boundary, for convolution and smooth
    def get_circle_boundary_boundary(self, coordinates):
        # generate an ellipsoidal mask of oringinal size
        wo, ho = coordinates[-1][0], coordinates[-1][1]
        mask1 = np.fromfunction(lambda x, y: np.hypot(((x + 0.5) / (wo / 2.) - 1), ((y + 0.5) / (ho / 2.) - 1)) < 1,
                                (wo, ho))

        # get a even smaller mask
        wss, hss = copy.deepcopy(wo - 4), copy.deepcopy(ho - 4)
        mask3 = np.fromfunction(lambda x, y: np.hypot(((x + 0.5) / (wss / 2.) - 1), ((y + 0.5) / (hss / 2.) - 1)) > 1,
                                (wss, hss))
        mask3 = np.concatenate((mask3, np.ones((2, mask3.shape[1]), dtype=int)), axis=0)
        mask3 = np.concatenate((np.ones((2, mask3.shape[1]), dtype=int), mask3), axis=0)
        mask3 = np.concatenate((mask3, np.ones((mask3.shape[0], 2), dtype=int)), axis=1)
        mask3 = np.concatenate((np.ones((mask3.shape[0], 2), dtype=int), mask3), axis=1)
        coordinates += [np.unravel_index(indice, mask3.shape) for indice in np.where(mask3.flatten() == 1)[0]]

        # generate an ellipsoidal mask of smaller size
        ## right bottom
        ws, hs = copy.deepcopy(wo - 3), copy.deepcopy(ho - 3)
        mask2 = np.fromfunction(lambda x, y: np.hypot(((x + 0.5) / (ws / 2.) - 1), ((y + 0.5) / (hs / 2.) - 1)) < 1,
                                (ws, hs))
        mask2 = np.concatenate((mask2, np.zeros((2, mask2.shape[1]), dtype=int)), axis=0)
        mask2 = np.concatenate((np.zeros((1, mask2.shape[1]), dtype=int), mask2), axis=0)
        mask2 = np.concatenate((mask2, np.zeros((mask2.shape[0], 2), dtype=int)), axis=1)
        mask2 = np.concatenate((np.zeros((mask2.shape[0], 1), dtype=int), mask2), axis=1)
        mask = mask1.astype(int) + mask2.astype(int)
        coordinates += [np.unravel_index(indice, mask.shape) for indice in np.where(mask.flatten() == 1)[0]]

        ## left bottom
        mask2 = np.fromfunction(lambda x, y: np.hypot(((x + 0.5) / (ws / 2.) - 1), ((y + 0.5) / (hs / 2.) - 1)) < 1,
                                (ws, hs))
        mask2 = np.concatenate((mask2, np.zeros((1, mask2.shape[1]), dtype=int)), axis=0)
        mask2 = np.concatenate((np.zeros((2, mask2.shape[1]), dtype=int), mask2), axis=0)
        mask2 = np.concatenate((mask2, np.zeros((mask2.shape[0], 2), dtype=int)), axis=1)
        mask2 = np.concatenate((np.zeros((mask2.shape[0], 1), dtype=int), mask2), axis=1)
        mask = mask1.astype(int) + mask2.astype(int)
        coordinates += [np.unravel_index(indice, mask.shape) for indice in np.where(mask.flatten() == 1)[0]]

        ## right top
        mask2 = np.fromfunction(lambda x, y: np.hypot(((x + 0.5) / (ws / 2.) - 1), ((y + 0.5) / (hs / 2.) - 1)) < 1,
                                (ws, hs))
        mask2 = np.concatenate((mask2, np.zeros((2, mask2.shape[1]), dtype=int)), axis=0)
        mask2 = np.concatenate((np.zeros((1, mask2.shape[1]), dtype=int), mask2), axis=0)
        mask2 = np.concatenate((mask2, np.zeros((mask2.shape[0], 1), dtype=int)), axis=1)
        mask2 = np.concatenate((np.zeros((mask2.shape[0], 2), dtype=int), mask2), axis=1)
        mask = mask1.astype(int) + mask2.astype(int)
        coordinates += [np.unravel_index(indice, mask.shape) for indice in np.where(mask.flatten() == 1)[0]]

        ## left top
        mask2 = np.fromfunction(lambda x, y: np.hypot(((x + 0.5) / (ws / 2.) - 1), ((y + 0.5) / (hs / 2.) - 1)) < 1,
                                (ws, hs))
        mask2 = np.concatenate((mask2, np.zeros((1, mask2.shape[1]), dtype=int)), axis=0)
        mask2 = np.concatenate((np.zeros((2, mask2.shape[1]), dtype=int), mask2), axis=0)
        mask2 = np.concatenate((mask2, np.zeros((mask2.shape[0], 1), dtype=int)), axis=1)
        mask2 = np.concatenate((np.zeros((mask2.shape[0], 2), dtype=int), mask2), axis=1)
        mask = mask1.astype(int) + mask2.astype(int)
        coordinates += [np.unravel_index(indice, mask.shape) for indice in np.where(mask.flatten() == 1)[0]]

        # add the borders
        tt = np.linspace(0, wo, wo + 1).astype(int)
        coordinates += [(0, t) for t in tt]
        coordinates += [(wo, t) for t in tt]
        coordinates += [(t, 0) for t in tt]
        coordinates += [(t, ho) for t in tt]
        coordinates = list(set(coordinates))
        return coordinates

    def remove_center(self, data):
        pos = np.unravel_index(data.argmax(), data.shape)
        data[pos[0], pos[1]] = data[pos[0]+1, pos[1]+1]
        return data

    def fft(self):
        ''' Operation 1 '''
        if self.operating_mode_2 == 0:
            data, name = self.get_target_data()
            result = []
            for img in data.target:
                fft_img = np.abs(np.fft.fftshift(np.fft.fft2(img)))
                fft_img = self.remove_center(fft_img)
                result.append(fft_img)
            result = np.array(result)
            data.result = result
            self.processed_data.append(data)
            data.name = 'fft-' + name
            data.name = self.avoid_repeat_name(data.name)
            self.listWidget_Processed.addItem(data.name)
            self.refresh_list(1)
        elif self.operating_mode_2 == 1:
            data, name = self.get_target_data()
            result = []
            for img in data.target:
                tmp = copy.deepcopy(img)
                if self.part_type == 0:
                    ret = self.part_s.getArrayRegion(tmp, self.img_display, axes=(0, 1), returnMappedCoords=True)
                else:
                    ret = self.part_c.getArrayRegion(tmp, self.img_display, axes=(0, 1), returnMappedCoords=True)
                    boundary = self.get_circle_boundary(ret[0])
                start_row = int(ret[1][0][0][0])
                end_row = int(1 + ret[1][0][-1][0])
                start_column = int(ret[1][1][0][0])
                end_column = int(1 + ret[1][1][0][-1])
                part = np.abs(np.fft.fftshift(np.fft.fft2(ret[0])))
                part = self.remove_center(part)
                if self.part_type == 1:
                    for coordinate in boundary:
                        part[coordinate[0]][coordinate[1]] = copy.deepcopy(tmp[coordinate[0]+start_row][coordinate[1]+start_column])
                for row in range(start_row, end_row):
                    for col in range(start_column, end_column):
                        tmp[row][col] = copy.deepcopy(part[row - start_row][col - start_column])
                result.append(tmp)
            result = np.array(result)
            data.result = result
            self.processed_data.append(data)
            data.name = 'fft-part-' + name
            data.name = self.avoid_repeat_name(data.name)
            self.listWidget_Processed.addItem(data.name)
            self.refresh_list(1)

    def fft_i(self):
        ''' Operation 1 '''
        if self.operating_mode_2 == 0:
            data, name = self.get_target_data()
            result = []
            for img in data.target:
                fft_img = np.fft.fftshift(np.fft.fft2(img))
                fft_img_abs, fft_img_real, fft_img_imag = self.remove_center(np.abs(fft_img)), np.real(fft_img), np.imag(fft_img)
                result.append(fft_img_abs); result.append(fft_img_real); result.append(fft_img_imag)
            result = np.array(result)
            data.result = result
            data.energy = [0] * result.shape[0]
            self.processed_data.append(data)
            data.name = 'fft*-' + name
            data.name = self.avoid_repeat_name(data.name)
            self.listWidget_Processed.addItem(data.name)
            self.refresh_list(1)

    def ifft(self):
        ''' Operation 1 '''
        if self.operating_mode_2 == 0:
            data, name = self.get_target_data()
            result = []
            for index in range(len(data.target)):
                if index % 3 == 0:
                    fft_img = data.target[index+1] + data.target[index+2] * 1j
                    ifft_img = np.real(np.fft.ifft2(np.fft.ifftshift(fft_img)))
                    result.append(ifft_img)
            result = np.array(result)
            data.result = result
            data.energy = [0] * result.shape[0]
            self.processed_data.append(data)
            data.name = 'ifft-' + name
            data.name = self.avoid_repeat_name(data.name)
            self.listWidget_Processed.addItem(data.name)
            self.refresh_list(1)

    def smooth(self, method, area, order, val):
        '''
        Operation 1 & 2

        Filter functions from scipy.ndimage

            * gaussian_filter
                area: sigma
                    Standard deviation for Gaussian kernel.
                    The standard deviations of the Gaussian filter are given for each axis as a sequence, or as a single number, in which case it is equal for all axes.
                order: order
                    The order of the filter along each axis is given as a sequence of integers, or as a single number. An order of 0 corresponds to convolution with a Gaussian kernel.
                    A positive order corresponds to convolution with that derivative of a Gaussian.

            * uniform_filter
                area: size
                    The sizes of the uniform filter are given for each axis as a sequence, or as a single number, in which case the size is equal for all axes.

            * gaussian_laplace
                area: sigma
                    The standard deviations of the Gaussian filter are given for each axis as a sequence, or as a single number, in which case it is equal for all axes.
        '''
        if self.operating_mode_2 == 0:
            data, name = self.get_target_data()
            result = []
            for img in data.target:
                if method == 0:     # Guassian
                    smooth_img = gaussian_filter(img, sigma=area, order=order)
                    result.append(smooth_img)
                    data.name = 'gaussian-' + name
                elif method == 1:   # Uniform
                    smooth_img = uniform_filter(img, size=area)
                    result.append(smooth_img)
                    data.name = 'uniform-' + name
                elif method == 2:   # Gaussian-Laplace
                    smooth_img = gaussian_laplace(img, sigma=area)
                    result.append(smooth_img)
                    data.name = 'gaussian_laplace-' + name
                elif method == 3:   # Set to value
                    x = np.ones(img.shape)
                    smooth_img = x * val
                    result.append(smooth_img)
                    data.name = 'set2val-' + name
                elif method == 4:   # Symmetry
                    # smooth_img = np.array(eng.symmetry(matlab.double(img.tolist()), order))
                    smooth_img = self.func2D.symmetry(img, order)
                    result.append(smooth_img)
                    data.name = 'symmetry'+ str(order) +'-' + name
                elif method == 5:   # Delete bad point
                    # smooth_img = np.array(eng.smooth_sts_mapping(matlab.double(img.tolist()), val, area))
                    smooth_img = self.func2D.delete_bad_point(img, val, area)
                    result.append(smooth_img)
                    data.name = 'delbadpt-' + name
            result = np.array(result)
            data.result = result
            self.processed_data.append(data)
            data.name = self.avoid_repeat_name(data.name)
            self.listWidget_Processed.addItem(data.name)
            self.refresh_list(1)
        elif self.operating_mode_2 == 1:
            data, name = self.get_target_data()
            result = []
            for img in data.target:
                tmp = copy.deepcopy(img)
                if self.part_type == 0:
                    ret = self.part_s.getArrayRegion(tmp, self.img_display, axes=(0, 1), returnMappedCoords=True)
                else:
                    real_size = self.part_c.state['size']
                    fake_size = pg.Point(self.part_c.state['size'].x()+4, self.part_c.state['size'].y()+4)
                    self.part_c.setSize(fake_size, center=[0.5, 0.5])
                    ret = self.part_c.getArrayRegion(tmp, self.img_display, axes=(0, 1), returnMappedCoords=True)
                    self.part_c.setSize(real_size, center=[0.5, 0.5])
                    boundary = self.get_circle_boundary_boundary(self.get_circle_boundary(ret[0]))
                start_row = int(ret[1][0][0][0])
                end_row = int(1 + ret[1][0][-1][0])
                start_column = int(ret[1][1][0][0])
                end_column = int(1 + ret[1][1][0][-1])
                if method == 0:  # Guassian
                    part = gaussian_filter(ret[0], area, order)
                    data.name = 'gaussian-part-' + name
                elif method == 1:  # Uniform
                    part = uniform_filter(ret[0], area)
                    data.name = 'uniform-part-' + name
                elif method == 2:  # Gaussian-Laplace
                    part = gaussian_laplace(ret[0], area)
                    data.name = 'median-part-' + name
                elif method == 3:   # Set to value
                    x = np.ones(img.shape)
                    part = x * val
                    data.name = 'set2val-part-' + name
                elif method == 4:   # Symmetry
                    part = self.func2D.symmetry(ret[0], order)
                    data.name = 'symmetry-part-' + str(order) + '-' + name
                elif method == 5:   # Delete bad point
                    part = self.func2D.delete_bad_point(ret[0], val, area)
                    data.name = 'delbadpt-part-' + name
                if self.part_type == 1:
                    for coordinate in boundary:
                        part[coordinate[0]][coordinate[1]] = copy.deepcopy(tmp[coordinate[0]+start_row][coordinate[1]+start_column])
                for row in range(start_row, end_row):
                    for col in range(start_column, end_column):
                        tmp[row][col] = copy.deepcopy(part[row - start_row][col - start_column])
                result.append(tmp)
            result = np.array(result)
            if self.ifft_mode:
                data.energy = [0] * result.shape[0]
            data.result = result
            self.processed_data.append(data)
            data.name = self.avoid_repeat_name(data.name)
            self.listWidget_Processed.addItem(data.name)
            self.refresh_list(1)

    def algebra(self, operation, value):
        ''' Operation 1 & 2'''
        if self.operating_mode_2 == 0:
            data, name = self.get_target_data()
            result = []
            for img in data.target:
                if operation == 0:      # Plus
                    do_img = img + value
                    data.name = 'plus-' + name
                elif operation == 1:    # Minus
                    do_img = img - value
                    data.name = 'minus-' + name
                elif operation == 2:    # Multiply
                    do_img = img * value
                    data.name = 'multiply-' + name
                elif operation == 3:    # Devide
                    do_img = img / value
                    data.name ='devide-' + name
                elif operation == 4:     # Exp
                    do_img = np.exp(img)
                    data.name = 'exp-' + name
                elif operation == 5:    # Log
                    do_img = np.log(img)
                    data.name = 'log-' + name
                result.append(do_img)
            result = np.array(result)
            data.result = result
            self.processed_data.append(data)
            data.name = self.avoid_repeat_name(data.name)
            self.listWidget_Processed.addItem(data.name)
            self.refresh_list(1)
        elif self.operating_mode_2 == 1:
            data, name = self.get_target_data()
            result = []
            for img in data.target:
                tmp = copy.deepcopy(img)
                if self.part_type == 0: # square
                    ret = self.part_s.getArrayRegion(tmp, self.img_display, axes=(0, 1), returnMappedCoords=True)
                else:   # circle
                    ret = self.part_c.getArrayRegion(tmp, self.img_display, axes=(0, 1), returnMappedCoords=True)
                    boundary = self.get_circle_boundary(ret[0])
                start_row = int(ret[1][0][0][0])
                end_row = int(1 + ret[1][0][-1][0])
                start_column = int(ret[1][1][0][0])
                end_column = int(1 + ret[1][1][0][-1])
                # !!! need to be part = ret[0] + value
                # originally is part = img + value
                if operation == 0:  # Plus
                    part = ret[0] + value
                    data.name = 'plus-' + name
                elif operation == 1:  # Minus
                    part = ret[0] - value
                    data.name = 'minus-' + name
                elif operation == 2:  # Multiply
                    part = ret[0] * value
                    data.name = 'multiply-' + name
                elif operation == 3:  # Devide
                    part = ret[0] / value
                    data.name = 'devide-' + name
                elif operation == 4:  # Exp
                    part = np.exp(ret[0])
                    data.name = 'exp-' + name
                elif operation == 5:  # Log
                    part = np.log(ret[0])
                    data.name = 'log-' + name
                if self.part_type == 1:
                    for coordinate in boundary:
                        part[coordinate[0]][coordinate[1]] = copy.deepcopy(tmp[coordinate[0]+start_row][coordinate[1]+start_column])
                for row in range(start_row, end_row):
                    for col in range(start_column, end_column):
                        tmp[row][col] = copy.deepcopy(part[row - start_row][col - start_column])
                result.append(tmp)

            result = np.array(result)
            data.result = result
            self.processed_data.append(data)
            data.name = self.avoid_repeat_name(data.name)
            self.listWidget_Processed.addItem(data.name)
            self.refresh_list(1)

    def bulid_bold_line(self, width):
        line_bold = pg.LineROI([0, 0], [100, 100], width=width, pen=(1, 9))
        line_bold.setZValue(11)
        self.view_box.addItem(line_bold)
        line_bold.movePoint(line_bold.getHandles()[0], [self.linecut.getHandles()[0].pos().x()+self.linecut.pos().x(), \
                                                        self.linecut.getHandles()[0].pos().y()+self.linecut.pos().y()])
        line_bold.movePoint(line_bold.getHandles()[1], [self.linecut.getHandles()[1].pos().x()+self.linecut.pos().x(), \
                                                        self.linecut.getHandles()[1].pos().y()+self.linecut.pos().y()])
        # line_bold.hide()
        return line_bold

    def remove_bold_line(self, lineROI):
        self.view_box.removeItem(lineROI)

    def export_linecut(self, path, angle):
        # Operation 1
        if self.operating_mode_1 == 0:

            # Plot list
            if self.current_list == self.listWidget:
                if len(self.listWidget.selectedItems()) == 0:
                    QMessageBox.warning(None, "Data Selection", 'Please select only 1 data in plot list!', QMessageBox.Ok)
                    return
                else:
                    if self.listWidget.currentItem().text()[0] == '\t':
                        name = self.listWidget.currentItem().text()[1:-5]
                    else:
                        name = self.listWidget.currentItem().text()
                    data = self.data[self.parent_name.index(name)]  # MappingData
                for name in data.child_name:
                    img2do = data.child_data[data.child_name.index(name)]
                    if self.linecut_width == 1:
                        ret = self.linecut.getArrayRegion(img2do, self.img_display, axes=(0, 1), returnMappedCoords=True)
                        default_name = path + "linecut_angle" + str(int(angle)) + '_' + name[1:-9] + name[-5:] + '.dat'
                        np.savetxt(default_name, ret[0])
                    else:
                        line_bold = self.bulid_bold_line(self.linecut_width)
                        ret = line_bold.getArrayRegion(img2do, self.img_display, axes=(0, 1), returnMappedCoords=True)
                        avg = ret[0].mean(axis=1)
                        default_name = path + "linecut_angle" + str(int(angle)) + '_' + name[1:-9] + name[-5:] + '.dat'
                        np.savetxt(default_name, avg)
                        self.remove_bold_line(line_bold)

            # Processed list
            elif self.current_list == self.listWidget_Processed:
                if len(self.listWidget_Processed.selectedItems()) == 0:
                    QMessageBox.warning(None, "Data Selection", 'Please select only 1 data in plot list!', QMessageBox.Ok)
                    return
                else:
                    name = self.listWidget_Processed.currentItem().text()
                    data = self.processed_data[self.processed_list.index(name)]  # MappingResult
                for i in range(data.result.shape[0]):
                    img2do = data.result[i]
                    if self.linecut_width == 1:
                        ret = self.linecut.getArrayRegion(img2do, self.img_display, axes=(0, 1),returnMappedCoords=True)
                        default_name = path + "linecut_angle" + str(int(angle)) + '_' + name[:-4] + '-' + str(i).zfill(5) + '.dat'
                        np.savetxt(default_name, ret[0])
                    else:
                        line_bold = self.bulid_bold_line(self.linecut_width)
                        ret = line_bold.getArrayRegion(img2do, self.img_display, axes=(0, 1), returnMappedCoords=True)
                        avg = ret[0].mean(axis=1)
                        default_name = path + "linecut_angle" + str(int(angle)) + '_' + name[:-4] + '-' + str(i).zfill(5) + '.dat'
                        np.savetxt(default_name, avg)
                        self.remove_bold_line(line_bold)

        # Operation 2
        elif self.operating_mode_1 == 1:

            # Plot list
            if self.current_list == self.listWidget:
                if self.listWidget.currentItem().text()[0] == '\t':
                    pname = self.listWidget.currentItem().text()[1:-5]
                    name = self.listWidget.currentItem().text()
                    index = int(self.listWidget.currentItem().text()[-2:])
                else:
                    pname = self.listWidget.currentItem().text()
                    name = self.listWidget.currentItem().text() + 'No_00'
                    index = 0
                data = self.data[self.parent_name.index(pname)]
                # data.get_energy(self.data[self.parent_name.index(pname)], index)
                if self.linecut_width == 1:
                    ret = self.linecut.getArrayRegion(data.child_data[index], self.img_display, axes=(0, 1), returnMappedCoords=True)
                    default_name = path + "linecut_angle" + str(int(angle)) + '_' + name[1:-9] + name[-5:] + '.dat'
                    # fileName, ok = QFileDialog.getSaveFileName(self, "Save", default_name, "DAT Files(*.dat)")
                    np.savetxt(default_name, ret[0])
                else:
                    line_bold = self.bulid_bold_line(self.linecut_width)
                    ret = line_bold.getArrayRegion(data.child_data[index], self.img_display, axes=(0, 1), returnMappedCoords=True)
                    avg = ret[0].mean(axis=1)
                    default_name = path + "linecut_angle" + str(int(angle)) + '_' + name[1:-9] + name[-5:] + '.dat'
                    np.savetxt(default_name, avg)
                    self.remove_bold_line(line_bold)

            # Processed list
            elif self.current_list == self.listWidget_Processed:
                name = self.listWidget_Processed.currentItem().text()
                data = self.processed_data[self.processed_list.index(name)]
                energy = self.scrollBar_Energy.value()
                img2do = data.result[energy]
                if self.linecut_width == 1:
                    ret = self.linecut.getArrayRegion(img2do, self.img_display, axes=(0, 1), returnMappedCoords=True)
                    default_name = path + "linecut_angle" + str(int(angle)) + '_' + name[:-9] + name[-5:] + '-' + str(energy).zfill(5) + '.dat'
                    np.savetxt(default_name, ret[0])
                else:
                    line_bold = self.bulid_bold_line(self.linecut_width)
                    ret = line_bold.getArrayRegion(data.child_data[index], self.img_display, axes=(0, 1), returnMappedCoords=True)
                    avg = ret[0].mean(axis=1)
                    default_name = path + "linecut_angle" + str(int(angle)) + '_' + name[:-9] + name[-5:] + '-' + str(energy).zfill(5) + '.dat'
                    np.savetxt(default_name, avg)
                    self.remove_bold_line(line_bold)

    def adv_linecut(self, index, angle):

        # energy
        if index == 0:

            # Plot list
            if self.current_list == self.listWidget:
                if len(self.listWidget.selectedItems()) == 0:
                    QMessageBox.warning(None, "Data Selection", 'Please select only 1 data in plot list!',
                                        QMessageBox.Ok)
                    return
                else:
                    if self.listWidget.currentItem().text()[0] == '\t':
                        name = self.listWidget.currentItem().text()[1:-5]
                    else:
                        name = self.listWidget.currentItem().text()
                data = self.data[self.parent_name.index(name)]
                for name in data.child_name:
                    img2do = data.child_data[data.child_name.index(name)]
                    if self.linecut_width == 1:
                        ret = self.linecut.getArrayRegion(img2do, self.img_display, axes=(0, 1), returnMappedCoords=True)
                        avg = ret[0]
                    else:
                        line_bold = self.bulid_bold_line(self.linecut_width)
                        ret = line_bold.getArrayRegion(img2do, self.img_display, axes=(0, 1), returnMappedCoords=True)
                        avg = ret[0].mean(axis=1)
                        self.remove_bold_line(line_bold)
                    default_name = "linecut_angle" + str(int(angle)) + '_' + name[1:-9] + '.dat'
                    if data.child_name.index(name) == 0:
                        img = avg
                    else:
                        img = np.vstack((img, avg))  # patch into 2D array
                fake_data = MappingResult(data, -1)
                fake_data.target = [np.flipud(img)]
                fake_data.name = default_name
                return fake_data

            # Processed list
            elif self.current_list == self.listWidget_Processed:
                if len(self.listWidget_Processed.selectedItems()) == 0:
                    QMessageBox.warning(None, "Data Selection", 'Please select only 1 data in plot list!',
                                        QMessageBox.Ok)
                    return
                else:
                    name = self.listWidget_Processed.currentItem().text()
                    data = self.processed_data[self.processed_list.index(name)]  # MappingResult
                for i in range(data.result.shape[0]):
                    img2do = data.result[i]
                    if self.linecut_width == 1:
                        ret = self.linecut.getArrayRegion(img2do, self.img_display, axes=(0, 1), returnMappedCoords=True)
                        avg = ret[0]
                    else:
                        line_bold = self.bulid_bold_line(self.linecut_width)
                        ret = line_bold.getArrayRegion(img2do, self.img_display, axes=(0, 1), returnMappedCoords=True)
                        avg = ret[0].mean(axis=1)
                        self.remove_bold_line(line_bold)
                    default_name = "linecut_angle" + str(int(angle)) + '_' + name[:-4] + '-' + str(i).zfill(5) + '.dat'
                    if i == 0:
                        img = avg
                    else:
                        img = np.vstack((img, avg))  # patch into 2D array
                fake_data = copy.deepcopy(data)
                fake_data.target = [np.flipud(img)]
                fake_data.name = default_name
                return fake_data

        # angle
        elif index == 1:

            # Plot list
            if self.current_list == self.listWidget:
                if self.listWidget.currentItem().text()[0] == '\t':
                    pname = self.listWidget.currentItem().text()[1:-5]
                    name = self.listWidget.currentItem().text()
                    index = int(self.listWidget.currentItem().text()[-2:])
                else:
                    pname = self.listWidget.currentItem().text()
                    name = self.listWidget.currentItem().text() + 'No_00'
                    index = 0
                data = self.data[self.parent_name.index(pname)]
                if self.linecut_width == 1:
                    ret = self.linecut.getArrayRegion(data.child_data[index], self.img_display, axes=(0, 1),returnMappedCoords=True)
                    avg = ret[0]
                else:
                    line_bold = self.bulid_bold_line(self.linecut_width)
                    ret = line_bold.getArrayRegion(data.child_data[index], self.img_display, axes=(0, 1),returnMappedCoords=True)
                    avg = ret[0].mean(axis=1)
                    self.remove_bold_line(line_bold)
                default_name = "linecut_multi-angle" + str(int(angle)) + '_' + name[1:-9] + name[-5:] + '.dat'
                fake_data = MappingResult(self.data[self.parent_name.index(pname)], index)  # fake
                fake_data.name = default_name
                return avg, fake_data

            # Processed list
            elif self.current_list == self.listWidget_Processed:
                name = self.listWidget_Processed.currentItem().text()
                data = self.processed_data[self.processed_list.index(name)]
                energy = self.scrollBar_Energy.value()
                img2do = data.result[energy]
                if self.linecut_width == 1:
                    ret = self.linecut.getArrayRegion(img2do, self.img_display, axes=(0, 1), returnMappedCoords=True)
                    avg = ret[0]
                else:
                    line_bold = self.bulid_bold_line(self.linecut_width)
                    ret = line_bold.getArrayRegion(img2do, self.img_display, axes=(0, 1), returnMappedCoords=True)
                    avg = ret[0].mean(axis=1)
                    self.remove_bold_line(line_bold)
                default_name = "linecut_multi-angle" + str(int(angle)) + '_' + name[:-9] + name[-5:] + '-' + str(energy).zfill(5) + '.dat'
                fake_data = copy.deepcopy(data)
                fake_data.name = default_name
                return avg, fake_data

    def patch_linecut(self, index, path, data):
        row = data.target[0].shape[0]
        col = data.target[0].shape[1]

        result = copy.deepcopy(data.target[0])
        if col > row:
            for i in range(row - 1, -1, -1):
                for j in range(col // row - 1):
                    result = np.insert(result, i, result[i], axis=0)

        data.result = np.array([result.transpose()])

        if index == 0:
            self.processed_data.append(data)
            data.name = self.avoid_repeat_name(data.name)
            self.listWidget_Processed.addItem(data.name)
            self.refresh_list(1)
        elif index == 1:
            default_name = path + data.name
            np.savetxt(default_name, result.transpose())
            # dict = {'result': result.transpose()}
            # savemat(default_name, dict)

    def adv_conv(self, kernel):
        ''' Operation 1 & 2'''
        if self.operating_mode_2 == 0:
            data, name = self.get_target_data()
            result = []
            for img in data.target:
                filt_img = convolve(img, kernel)
                result.append(filt_img)
            result = np.array(result)
            data.result = result
            self.processed_data.append(data)
            data.name = 'conv-' + name
            data.name = self.avoid_repeat_name(data.name)
            self.listWidget_Processed.addItem(data.name)
            self.refresh_list(1)
        elif self.operating_mode_2 == 1:
            data, name = self.get_target_data()
            result = []
            for img in data.target:
                tmp = copy.deepcopy(self.myimg.prepare_data(img))   # to avoid big contrast
                if self.part_type == 0:
                    ret = self.part_s.getArrayRegion(tmp, self.img_display, axes=(0, 1), returnMappedCoords=True)
                else:
                    real_size = self.part_c.state['size']
                    fake_size = pg.Point(self.part_c.state['size'].x()+4, self.part_c.state['size'].y()+4)
                    self.part_c.setSize(fake_size, center=[0.5, 0.5])
                    ret = self.part_c.getArrayRegion(tmp, self.img_display, axes=(0, 1), returnMappedCoords=True)
                    self.part_c.setSize(real_size, center=[0.5, 0.5])
                    boundary = self.get_circle_boundary_boundary(self.get_circle_boundary(ret[0]))
                start_row = int(ret[1][0][0][0])
                end_row = int(1 + ret[1][0][-1][0])
                start_column = int(ret[1][1][0][0])
                end_column = int(1 + ret[1][1][0][-1])
                norm_factor = np.sum(np.array(kernel)) if np.sum(np.array(kernel)) > 1e-5 else 1
                part = convolve(ret[0], kernel) / norm_factor
                if self.part_type == 1:
                    for coordinate in boundary:
                        part[coordinate[0]][coordinate[1]] = copy.deepcopy(tmp[coordinate[0]+start_row][coordinate[1]+start_column])
                for row in range(start_row, end_row):
                    for col in range(start_column, end_column):
                        tmp[row][col] = copy.deepcopy(part[row - start_row][col - start_column])
                result.append(tmp)
            result = np.array(result)
            data.result = result
            self.processed_data.append(data)
            data.name = 'conv-part-' + name
            data.name = self.avoid_repeat_name(data.name)
            self.listWidget_Processed.addItem(data.name)
            self.refresh_list(1)

    def convolve(self, image, filt):
        ''' Operation 1 & 2'''
        height, width = image.shape
        h, w = filt.shape
        height_new = height - h + 1
        width_new = width - w + 1
        image_new = np.zeros((height_new, width_new), dtype=np.float)
        for i in range(height_new):
            for j in range(width_new):
                image_new[i, j] = np.sum(image[i:i + h, j:j + w] * filt)
        image_new = image_new.clip(0, 255)
        image_new = np.rint(image_new).astype('uint8')
        return image_new

    def get_current_parent(self):
        if self.current_list == self.listWidget:
            name = self.listWidget.currentItem().text()
            if name[0] == '\t':
                pname = name[1:-5]
            else:
                pname = name
            data = copy.deepcopy(self.data[self.parent_name.index(pname)].data_)
            """ ccpp1.3 """
            # data = data.swapaxes(0, 2)
            energy = copy.deepcopy(self.data[self.parent_name.index(pname)].energy)
            rscale = copy.deepcopy(self.data[self.parent_name.index(pname)].scale)
            return data, pname, energy, rscale
        elif self.current_list == self.listWidget_Processed:
            name = self.processed_data[self.processed_list.index(self.listWidget_Processed.currentItem().text())].name
            data = self.processed_data[self.processed_list.index(self.listWidget_Processed.currentItem().text())].result
            energy = self.processed_data[self.processed_list.index(self.listWidget_Processed.currentItem().text())].energy
            rscale = (200, 200)
            if data.shape[0] == 1:
                QMessageBox.warning(None, "Data Selection", 'The data you selected is 2D data. Please select a 3D data.', QMessageBox.Ok)
                return

            return data, name, energy, rscale

    def get_current_child(self):
        if self.current_list == self.listWidget and self.listWidget.currentItem() != None:
            name = self.listWidget.currentItem().text()
            if name[0] == '\t':
                pname = name[1:-5]
            else:
                pname = name
            index = self.scrollBar_Energy.value()
            data = copy.deepcopy(self.data[self.parent_name.index(pname)].data_[index, :, :])
            energy = self.data[self.parent_name.index(pname)].energy
            rscale = self.data[self.parent_name.index(pname)].scale
            return data, name, energy, rscale
        elif self.current_list == self.listWidget_Processed:
            index = self.scrollBar_Energy.value()
            if self.listWidget_Processed.currentItem() is not None:
                name = self.processed_data[self.processed_list.index(self.listWidget_Processed.currentItem().text())].name
                data = self.processed_data[self.processed_list.index(self.listWidget_Processed.currentItem().text())].result[index]
                energy = self.processed_data[self.processed_list.index(self.listWidget_Processed.currentItem().text())].energy
                rscale = self.processed_data[self.processed_list.index(self.listWidget_Processed.currentItem().text())].scale
                return data, name, energy, rscale

    def make_cube_data(self, data):
        depth = data.shape[0]
        row = data.shape[1]
        tmp = copy.deepcopy(data)
        if depth < row:
            for i in range(depth - 1, -1, -1):
                for j in range(row // depth - 1):
                    tmp = np.insert(tmp, i, tmp[i], axis=0)
        return tmp[:, :, ::-1]

    def data_slicing(self, index):
        if index == 0:  # 3D slicing
            data, name, energy, rscale = self.get_current_parent()
            data = self.make_cube_data(data)
            self.dataSlicing = myDataSlicing()
            self.dataSlicing.close_signal.connect(lambda: self.close_subwin(0))
            self.dataSlicing.init_data(data, name, energy, rscale)
            self.dataSlicing.line_changed(0, True)
            self.dataSlicing.show()
        elif index == 1:    # 2D slicing
            data, name, energy, rscale = self.get_current_child()
            self.dataSlicing2D = myDataSlicing2D()
            self.dataSlicing2D.close_signal.connect(lambda: self.close_subwin(1))
            self.dataSlicing2D.init_data(data, name, energy, rscale)
            self.dataSlicing2D.show()

    def close_subwin(self, index):
        if index == 0:  # 3D slicing
            self.dataSlicing.deleteLater()
        else:    # 2D slicing
            self.dataSlicing2D.deleteLater()

    def get_current_name(self):
        if self.current_list == self.listWidget:
            name = self.listWidget.currentItem().text()
        elif self.current_list == self.listWidget_Processed:
            name = self.processed_data[self.processed_list.index(self.listWidget_Processed.currentItem().text())].name
            name += 'No_' + str(self.scrollBar_Energy.value()).zfill(2)
        return name

    def roi_cut(self):
        ''' Operation 1 & 2'''
        data, name = self.get_target_data()
        result = []
        for img in data.target:
            tmp = copy.deepcopy(img)
            if self.part_type == 0:
                ret = self.part_s.getArrayRegion(tmp, self.img_display, axes=(0, 1), returnMappedCoords=True)
            else:
                ret = self.part_c.getArrayRegion(tmp, self.img_display, axes=(0, 1), returnMappedCoords=True)
                boundary = self.get_circle_boundary(ret[0])
            # replace the circle boundary with minimum value
            part = ret[0]; tmp = np.ones(img.shape) * np.min(img)
            start_row = int(ret[1][0][0][0]); start_column = int(ret[1][1][0][0])
            if self.part_type == 1:
                for coordinate in boundary:
                    part[coordinate[0]][coordinate[1]] = copy.deepcopy(
                        tmp[coordinate[0] + start_row][coordinate[1] + start_column])
            data.name = 'cut-part-' + name
            result.append(part)
        result = np.array(result)
        data.result = result
        self.processed_data.append(data)
        data.name = self.avoid_repeat_name(data.name)
        self.listWidget_Processed.addItem(data.name)
        self.refresh_list(1)

    def clone_stamp(self, index):
        # warning box if it's global mode
        if self.operating_mode_2 == 0:
            QMessageBox.warning(None, "Clone Stamp", 'Please select ROI mode!', QMessageBox.Ok)
            return
        ''' Operation 1 & 2'''
        data, name = self.get_target_data()
        if index == 0:  # copy
            self.stack_part = []
            for img in data.target:
                tmp = copy.deepcopy(img)
                if self.part_type == 0:
                    ret = self.part_s.getArrayRegion(tmp, self.img_display, axes=(0, 1), returnMappedCoords=True)
                else:
                    ret = self.part_c.getArrayRegion(tmp, self.img_display, axes=(0, 1), returnMappedCoords=True)
                self.stack_part.append(ret[0])
        elif index == 1:   # paste
            result = []
            for n, img in enumerate(data.target):
                tmp = copy.deepcopy(img)
                if self.part_type == 0:
                    ret = self.part_s.getArrayRegion(tmp, self.img_display, axes=(0, 1), returnMappedCoords=True)
                else:
                    ret = self.part_c.getArrayRegion(tmp, self.img_display, axes=(0, 1), returnMappedCoords=True)
                    boundary = self.get_circle_boundary(ret[0])
                start_row = int(ret[1][0][0][0])
                end_row = int(1 + ret[1][0][-1][0])
                start_column = int(ret[1][1][0][0])
                end_column = int(1 + ret[1][1][0][-1])
                part = self.stack_part[n]
                if self.part_type == 1:
                    for coordinate in boundary:
                        part[coordinate[0]][coordinate[1]] = copy.deepcopy(
                            tmp[coordinate[0] + start_row][coordinate[1] + start_column])
                for row in range(start_row, end_row):
                    for col in range(start_column, end_column):
                        tmp[row][col] = copy.deepcopy(part[row - start_row][col - start_column])
                result.append(tmp)
            result = np.array(result)
            data.result = result
            self.processed_data.append(data)
            data.name = 'clone-stamp-' + name
            data.name = self.avoid_repeat_name(data.name)
            self.listWidget_Processed.addItem(data.name)
            self.refresh_list(1)

    def roi_rec(self, status):
        if status:
            self.reccut_flag = False
            # warning box if it's global mode
            if self.operating_mode_2 == 0:
                QMessageBox.warning(None, "Clone Stamp", 'Please select ROI mode!', QMessageBox.Ok)
                return
            ''' Operation 1 & 2'''
            self.rectoi_target = self.get_target_data()
            # clear cutting map with minimum value, zero does n ot work when data is bit data
            self.map = np.ones(np.array(self.rectoi_target[0].target).shape) * np.min(np.array(self.rectoi_target[0].target))
        elif self.reccut_flag:
                data, name = self.rectoi_target
                data.result = copy.deepcopy(self.map)
                self.processed_data.append(data)
                data.name = 'rec-cut-' + name
                data.name = self.avoid_repeat_name(data.name)
                self.listWidget_Processed.addItem(data.name)
                self.refresh_list(1)

    def roi_reccut(self):
        data, name = self.rectoi_target
        # Cut part
        map_part = []
        for img in data.target:
            tmp = copy.deepcopy(img)
            if self.part_type == 0:
                ret = self.part_s.getArrayRegion(tmp, self.img_display, axes=(0, 1), returnMappedCoords=True)
            else:
                ret = self.part_c.getArrayRegion(tmp, self.img_display, axes=(0, 1), returnMappedCoords=True)
            map_part.append(ret[0])

        # Paste to map
        result = []
        for n, img in enumerate(data.target):
            tmp = copy.deepcopy(img)
            map = np.ones(img.shape) * np.min(img)
            if self.part_type == 0:
                ret = self.part_s.getArrayRegion(tmp, self.img_display, axes=(0, 1), returnMappedCoords=True)
            else:
                ret = self.part_c.getArrayRegion(tmp, self.img_display, axes=(0, 1), returnMappedCoords=True)
                boundary = self.get_circle_boundary(ret[0])
            start_row = int(ret[1][0][0][0])
            end_row = int(1 + ret[1][0][-1][0])
            start_column = int(ret[1][1][0][0])
            end_column = int(1 + ret[1][1][0][-1])
            part = map_part[n]
            if self.part_type == 1:
                for coordinate in boundary:
                    part[coordinate[0]][coordinate[1]] = np.min(img)
            for row in range(start_row, end_row):
                for col in range(start_column, end_column):
                    map[row][col] = copy.deepcopy(part[row - start_row][col - start_column])
            result.append(map)
        result = np.array(result)
        self.map += result

    def adv_plane_fit(self, fitted):
        data, name = self.get_target_data()
        result = []
        result.append(fitted)
        data.result = np.array(result)
        self.processed_data.append(data)
        data.name = 'plane-fit-' + name
        data.name = self.avoid_repeat_name(data.name)
        self.listWidget_Processed.addItem(data.name)
        self.refresh_list(1)

    def adv_illumination(self, illuminated):
        data, name = self.get_target_data()
        result = []
        result.append(illuminated)
        data.result = np.array(result)
        self.processed_data.append(data)
        data.name = 'illuminate-' + name
        data.name = self.avoid_repeat_name(data.name)
        self.listWidget_Processed.addItem(data.name)
        self.refresh_list(1)




if __name__ == "__main__":
    app = QApplication(sys.argv)
    names = ['20201207-BaTi2Sb2O-edge-002.3ds', '\t20201207-BaTi2Sb2O-edge-002.3ds_No00',
             '\t20201207-BaTi2Sb2O-edge-002.3ds_No01', '\t20201207-BaTi2Sb2O-edge-002.3ds_No02',
             '\t20201207-BaTi2Sb2O-edge-002.3ds_No03', '\t20201207-BaTi2Sb2O-edge-002.3ds_No04',
             '\t20201207-BaTi2Sb2O-edge-002.3ds_No05', '\t20201207-BaTi2Sb2O-edge-002.3ds_No06',
             '\t20201207-BaTi2Sb2O-edge-002.3ds_No07', '\t20201207-BaTi2Sb2O-edge-002.3ds_No08',
             '20201207-BaTi2Sb2O-edge-012.3ds', '\t20201207-BaTi2Sb2O-edge-012.3ds_No00',
             '\t20201207-BaTi2Sb2O-edge-012.3ds_No01', '\t20201207-BaTi2Sb2O-edge-012.3ds_No02',
             '\t20201207-BaTi2Sb2O-edge-012.3ds_No03', '\t20201207-BaTi2Sb2O-edge-012.3ds_No04',
             '\t20201207-BaTi2Sb2O-edge-012.3ds_No05', '\t20201207-BaTi2Sb2O-edge-012.3ds_No06',
             '\t20201207-BaTi2Sb2O-edge-012.3ds_No07', '\t20201207-BaTi2Sb2O-edge-012.3ds_No08',
             '\t20201207-BaTi2Sb2O-edge-012.3ds_No09', '\t20201207-BaTi2Sb2O-edge-012.3ds_No10',
             '\t20201207-BaTi2Sb2O-edge-012.3ds_No11', '\t20201207-BaTi2Sb2O-edge-012.3ds_No12',
             '\t20201207-BaTi2Sb2O-edge-012.3ds_No13', '\t20201207-BaTi2Sb2O-edge-012.3ds_No14',
             '\t20201207-BaTi2Sb2O-edge-012.3ds_No15', '\t20201207-BaTi2Sb2O-edge-012.3ds_No16',
             '\t20201207-BaTi2Sb2O-edge-012.3ds_No17', '\t20201207-BaTi2Sb2O-edge-012.3ds_No18']
    paths = ['C:/Users/DAN/Documents/MyCode/PythonScripts/ccpp1.0/test data\\20201207-BaTi2Sb2O-edge-002.3ds',
             'C:/Users/DAN/Documents/MyCode/PythonScripts/ccpp1.0/test data\\20201207-BaTi2Sb2O-edge-002.3ds',
             'C:/Users/DAN/Documents/MyCode/PythonScripts/ccpp1.0/test data\\20201207-BaTi2Sb2O-edge-002.3ds',
             'C:/Users/DAN/Documents/MyCode/PythonScripts/ccpp1.0/test data\\20201207-BaTi2Sb2O-edge-002.3ds',
             'C:/Users/DAN/Documents/MyCode/PythonScripts/ccpp1.0/test data\\20201207-BaTi2Sb2O-edge-002.3ds',
             'C:/Users/DAN/Documents/MyCode/PythonScripts/ccpp1.0/test data\\20201207-BaTi2Sb2O-edge-002.3ds',
             'C:/Users/DAN/Documents/MyCode/PythonScripts/ccpp1.0/test data\\20201207-BaTi2Sb2O-edge-002.3ds',
             'C:/Users/DAN/Documents/MyCode/PythonScripts/ccpp1.0/test data\\20201207-BaTi2Sb2O-edge-002.3ds',
             'C:/Users/DAN/Documents/MyCode/PythonScripts/ccpp1.0/test data\\20201207-BaTi2Sb2O-edge-002.3ds',
             'C:/Users/DAN/Documents/MyCode/PythonScripts/ccpp1.0/test data\\20201207-BaTi2Sb2O-edge-002.3ds',
             'C:/Users/DAN/Documents/MyCode/PythonScripts/ccpp1.0/test data\\20201207-BaTi2Sb2O-edge-012.3ds',
             'C:/Users/DAN/Documents/MyCode/PythonScripts/ccpp1.0/test data\\20201207-BaTi2Sb2O-edge-012.3ds',
             'C:/Users/DAN/Documents/MyCode/PythonScripts/ccpp1.0/test data\\20201207-BaTi2Sb2O-edge-012.3ds',
             'C:/Users/DAN/Documents/MyCode/PythonScripts/ccpp1.0/test data\\20201207-BaTi2Sb2O-edge-012.3ds',
             'C:/Users/DAN/Documents/MyCode/PythonScripts/ccpp1.0/test data\\20201207-BaTi2Sb2O-edge-012.3ds',
             'C:/Users/DAN/Documents/MyCode/PythonScripts/ccpp1.0/test data\\20201207-BaTi2Sb2O-edge-012.3ds',
             'C:/Users/DAN/Documents/MyCode/PythonScripts/ccpp1.0/test data\\20201207-BaTi2Sb2O-edge-012.3ds',
             'C:/Users/DAN/Documents/MyCode/PythonScripts/ccpp1.0/test data\\20201207-BaTi2Sb2O-edge-012.3ds',
             'C:/Users/DAN/Documents/MyCode/PythonScripts/ccpp1.0/test data\\20201207-BaTi2Sb2O-edge-012.3ds',
             'C:/Users/DAN/Documents/MyCode/PythonScripts/ccpp1.0/test data\\20201207-BaTi2Sb2O-edge-012.3ds',
             'C:/Users/DAN/Documents/MyCode/PythonScripts/ccpp1.0/test data\\20201207-BaTi2Sb2O-edge-012.3ds',
             'C:/Users/DAN/Documents/MyCode/PythonScripts/ccpp1.0/test data\\20201207-BaTi2Sb2O-edge-012.3ds',
             'C:/Users/DAN/Documents/MyCode/PythonScripts/ccpp1.0/test data\\20201207-BaTi2Sb2O-edge-012.3ds',
             'C:/Users/DAN/Documents/MyCode/PythonScripts/ccpp1.0/test data\\20201207-BaTi2Sb2O-edge-012.3ds',
             'C:/Users/DAN/Documents/MyCode/PythonScripts/ccpp1.0/test data\\20201207-BaTi2Sb2O-edge-012.3ds',
             'C:/Users/DAN/Documents/MyCode/PythonScripts/ccpp1.0/test data\\20201207-BaTi2Sb2O-edge-012.3ds',
             'C:/Users/DAN/Documents/MyCode/PythonScripts/ccpp1.0/test data\\20201207-BaTi2Sb2O-edge-012.3ds',
             'C:/Users/DAN/Documents/MyCode/PythonScripts/ccpp1.0/test data\\20201207-BaTi2Sb2O-edge-012.3ds',
             'C:/Users/DAN/Documents/MyCode/PythonScripts/ccpp1.0/test data\\20201207-BaTi2Sb2O-edge-012.3ds',
             'C:/Users/DAN/Documents/MyCode/PythonScripts/ccpp1.0/test data\\20201207-BaTi2Sb2O-edge-012.3ds']
    window = myGraphWindow(names, paths)
    window.listWidget.addItems(names)
    window.refresh_list(0)
    window.show()
    sys.exit(app.exec_())