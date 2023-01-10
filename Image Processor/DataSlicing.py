# -*- coding: utf-8 -*-
"""
@Date     : 2021/6/1 09:32:02
@Author   : milier00
@FileName : DataSlicing.py
"""
import sys
sys.path.append("./ui/")
sys.path.append("./model/")
from PyQt5.QtWidgets import QToolButton, QMenu, QAction, QApplication, QPushButton, QSizePolicy, QSlider, QLabel, QFileDialog, QDoubleSpinBox, QMainWindow, QRadioButton, QButtonGroup
from PyQt5.QtCore import pyqtSignal, Qt, QRectF
from pyqtgraph.Qt import QtWidgets
from images import myImages
from DataSlicing_ui import Ui_DataSlicing
from Data import *
import numpy as np
from skimage import transform, io, color
import pyqtgraph as pg
import copy
import ctypes
import colorcet as cc


class myDataSlicing(Ui_DataSlicing, QMainWindow):
    close_signal = pyqtSignal()
    do_signal = pyqtSignal()
    export_signal = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.init_UI()
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("myappid")

    def init_UI(self):
        self.move(80, 440)       # Init ui position

        # Interpret image data as row-major instead of col-major
        # pg.setConfigOptions(imageAxisOrder='row-major')
        self.myimg = myImages()
        self.color_map_index = 3    # default magma

        self.resize(1200, 520)
        cw = QtWidgets.QWidget()
        self.setCentralWidget(cw)
        l = QtWidgets.QGridLayout()
        cw.setLayout(l)

        # center | curve plot
        self.glayout = pg.GraphicsLayoutWidget()
        self.glayout.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Preferred)
        self.glayout.setMaximumWidth(500)
        self.glayout.setMinimumWidth(500)
        self.plt = self.glayout.addPlot(row=1, col=0)
        # center | interval spinBox
        self.spinBox = QDoubleSpinBox()
        self.spinBox.setMaximum(10)
        self.spinBox.setDecimals(2)
        self.spinBox.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Fixed)
        self.spinBox.editingFinished.connect(self.spin2slider)
        # center | interval slideBar
        self.slideBar = QSlider()
        self.slideBar.setMaximum(1000)
        self.slideBar.setTickPosition(QSlider.TicksBothSides)
        self.slideBar.setTickInterval(50)
        self.slideBar.setOrientation(Qt.Horizontal)
        self.slideBar.setMaximumWidth(200)
        self.slideBar.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Fixed)
        self.slideBar.valueChanged.connect(self.slider2spin)
        self.slideBar.valueChanged.connect(self.update_interval)
        # center | interval label
        self.label = QLabel('Interval')
        self.label.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Fixed)
        # right | line cut option
        self.radio_0 = QRadioButton()
        self.radio_0.setText('fine line')
        self.radio_0.setMaximumWidth(100)
        self.radio_0.setChecked(True)
        self.radio_1 = QRadioButton()
        self.radio_1.setText('bold line')
        self.radio_1.setMaximumWidth(100)

        self.radio_group = QButtonGroup()
        self.radio_group.addButton(self.radio_0, 0)
        self.radio_group.addButton(self.radio_1, 1)
        self.radio_group.buttonToggled[int, bool].connect(self.line_changed)

        self.pushButton_export2d = QPushButton('Export2D')
        self.pushButton_export2d.clicked.connect(self.export)
        self.toolButton_ColorMap = QToolButton()
        self.toolButton_ColorMap.setArrowType(Qt.DownArrow)
        self.toolButton_ColorMap.setAutoRaise(True)
        self.toolButton_ColorMap.setPopupMode(QToolButton.InstantPopup)
        self.init_colormap()

        # image view | 1: right part (line cut), 2: left part (display)
        self.imv1 = pg.ImageView()
        # self.imv1.view.disableAutoRange()
        self.imv1.ui.roiBtn.setMaximumWidth(60)
        self.imv1.ui.menuBtn.setMaximumWidth(60)
        self.imv1.setMaximumWidth(500)
        self.imv1.setMinimumWidth(500)

        self.imv2 = pg.ImageView(view=pg.PlotItem())
        self.imv2.view.setAspectLocked(False)
        # self.imv2.ui.histogram.setMaximumWidth(160)
        self.imv2.ui.roiBtn.setMaximumWidth(60)
        self.imv2.ui.menuBtn.setMaximumWidth(60)
        self.imv2.setMaximumWidth(500)
        self.imv2.setMinimumWidth(500)

        # self.hist1 = self.imv1.getHistogramWidget()
        # self.hist1.setMaximumWidth(100)
        # self.hist2 = self.imv2.getHistogramWidget()
        # self.hist2.setMaximumWidth(100)

        ## add items
        # left part
        l.addWidget(self.imv2, 0, 0, 2, 1)
        # central part
        l.addWidget(self.glayout, 0, 1, 1, 3)
        l.addWidget(self.spinBox, 1, 2, 1, 1)
        l.addWidget(self.slideBar, 1, 3, 1, 1)
        l.addWidget(self.label, 1, 1, 1, 1)
        # right part
        l.addWidget(self.imv1, 0, 4, 1, 4)
        l.addWidget(self.radio_0, 1, 4, 1, 1)
        l.addWidget(self.radio_1, 1, 5, 1, 1)
        l.addWidget(self.pushButton_export2d, 1, 6, 1, 1)
        l.addWidget(self.toolButton_ColorMap, 1, 7, 1, 1)

        # ROI | right part line cut
        self.line_fine = pg.LineSegmentROI([[30, 100], [80, 5]], pen='r')
        self.imv1.addItem(self.line_fine)
        self.line_fine.sigRegionChanged.connect(self.update)

        self.line_bold = pg.LineROI([30, 100], [80, 5], width=5, pen=(1, 9))
        self.imv1.addItem(self.line_bold)
        self.line_bold.sigRegionChanged.connect(self.update)
        self.line_bold.hide()

        self.line_index = 0     # 0: fine line; 1: bold line

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

    # Color map slot | multiple colormap
    def color_map(self, index):
        self.color_map_index = index
        self.update()

    def line_changed(self, index, status):
        if status:
            self.line_index = index
            if index == 0:
                self.line_bold.hide()
                self.line_fine.show()
            else:
                self.line_bold.show()
                self.line_fine.hide()
        self.update()

    def init_data(self, data, name, energy, rscale):
        self.raw_data = copy.deepcopy(data); self.data = data;
        for i in range(data.shape[0]):
            self.data[i] = self.myimg.prepare_data(self.myimg.partial_renormalize(data[i]))
        self.energy = energy
        self.energy = np.linspace(0, data.shape[0], data.shape[0])
        self.rscale = rscale
        self.setWindowTitle('Data Slicing: ' + name)
        ## Display the data
        self.imv1.setImage(self.data)
        self.imv1.view.setRange(QRectF(0, 0, self.imv1.imageItem.width(), self.imv1.imageItem.height()), padding=0)
        ## set jet colormap
        # colors = [(0, 0, 128), (0, 0, 255), (0, 255, 255), (255, 255, 0), (255, 0, 0), (128, 0, 0)]
        # pos = np.array([0, 0.125, 0.375, 0.625, 0.875, 1])
        # cmap = pg.ColorMap(pos=pos, color=colors)
        ## set magma color
        cmap = pg.colormap.get('magma', source='matplotlib')
        self.imv1.setColorMap(cmap)
        self.update()

    def update(self):
        if self.line_index == 0:    # fine line
            d2 = self.line_fine.getArrayRegion(self.raw_data, self.imv1.imageItem, axes=(1, 2))   # get sliced data
        else:   # bold line
            selected = self.line_bold.getArrayRegion(self.raw_data, self.imv1.imageItem, axes=(1, 2))
            d2 = selected.mean(axis=2)

        # """ delay imaging """
        # (row, col) = d2.shape
        # for i in range(col - 1, -1, -1):
        #     for j in range(2):
        #         d2 = np.insert(d2, i, d2[:, i], axis=1)
        # """ ------------- """

        self.imv2.setImage(d2.transpose())
        # set y ticks and title
        energy_ticks = np.linspace(np.min(self.energy), np.max(self.energy), 5)
        self.energy_ticks = [round(energy, 1) for energy in energy_ticks]
        self.origin_ticks = np.linspace(0, d2.transpose().shape[1], 5)
        self.imv2.view.axes['left']['item'].setTicks([[(self.origin_ticks[0], str(self.energy_ticks[4])), (self.origin_ticks[1], str(self.energy_ticks[3])), \
                                                       (self.origin_ticks[2], str(self.energy_ticks[2])), (self.origin_ticks[3], str(self.energy_ticks[1])), \
                                                       (self.origin_ticks[4], str(self.energy_ticks[0]))]])
        ## set jet colormap
        # colors = [(0, 0, 128), (0, 0, 255), (0, 255, 255), (255, 255, 0), (255, 0, 0), (128, 0, 0)]
        # pos = np.array([0, 0.125, 0.375, 0.625, 0.875, 1])
        # cmap = pg.ColorMap(pos=pos, color=colors)
        ## set magma colormap
        # cmap = pg.colormap.get('magma', source='matplotlib')
        # self.imv2.setColorMap(cmap)
        ## set colormap by selection
        self.imv2.setColorMap(self.myimg.colormap_dict_cm[self.color_map_index])
        # delete redundant data
        self.data1d = np.unique(d2, axis=0)
        self.data1d = self.data1d
        # plot with interval
        self.update_interval()

    def update_interval(self):
        interval = self.spinBox.value()  # get current interval
        data1d = copy.deepcopy(self.data1d)  # make a copy
        # add interval
        mean_value = np.average(data1d)
        for i in range(data1d.shape[0]):
            data1d[i] += mean_value * i * (interval/5)
        # plot with interval
        self.plt.clear()
        for i in range(data1d.shape[0]):
            self.plt.plot(data1d[i], pen=cc.glasbey_dark[i])

    def spin2slider(self):
        val = int(self.spinBox.value()*100)
        self.slideBar.setValue(val)

    def slider2spin(self):
        val = round(self.slideBar.value()/100, 2)
        self.spinBox.setValue(val)

    def export(self):
        img2save = transform.rescale(self.imv2.imageItem.image.transpose(), (3, 3))     # up-scale 3 times
        fileName, ok = QFileDialog.getSaveFileName(self, "Save", 'linecut2d', "JPG(*.jpg);;PNG(*.png);;EPS(*.eps)")
        img2save = self.myimg.prepare_data(img2save)
        img2save = self.myimg.color_map(img2save, self.color_map_index)
        img2save = color.rgba2rgb(img2save)
        io.imsave(fileName, img2save)

    # Emit close signal
    def closeEvent(self, event):
        self.close_signal.emit()
        event.accept()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = myDataSlicing()
    ''' data in example'''
    # x1 = np.linspace(-30, 10, 128)[:, np.newaxis, np.newaxis]
    # x2 = np.linspace(-20, 20, 128)[:, np.newaxis, np.newaxis]
    # y = np.linspace(-30, 10, 128)[np.newaxis, :, np.newaxis]
    # z = np.linspace(-20, 20, 128)[np.newaxis, np.newaxis, :]
    # d1 = np.sqrt(x1 ** 2 + y ** 2 + z ** 2)
    # d2 = 2 * np.sqrt(x1[::-1] ** 2 + y ** 2 + z ** 2)
    # d3 = 4 * np.sqrt(x2 ** 2 + y[:, ::-1] ** 2 + z ** 2)
    # data = (np.sin(d1) / d1 ** 2) + (np.sin(d2) / d2 ** 2) + (np.sin(d3) / d3 ** 2)
    ''' self made data '''
    # a = np.array([1, 1, 1] * 30)
    # b = np.array([2, 2, 2] * 30)
    # c = np.array([3, 3, 3] * 30)
    # d = np.vstack((a, b, c))
    # f = []
    # f.append(d)
    # f = np.array(f)
    # for i in range(f.shape[1] - 1, -1, -1):
    #     for j in range(29):
    #         f = np.insert(f, i, f[:, i, :], axis=1)
    # depth = f.shape[0]
    # row = f.shape[2]
    # if depth < row:
    #     for i in range(depth - 1, -1, -1):
    #         for j in range(row // depth - 1):
    #             f = np.insert(f, i, f[i], axis=0)
    # for slice in f[30:31, :, :]:
    #     for i in range(30, 60):
    #         f[i, :, :] = slice * 2
    #     for j in range(60, 90):
    #         f[j, :, :] = slice * 3
    # data = f
    #
    # window.init_data(data, 'hhh', np.linspace(0,90,90), (200,200))

    """ delay imaging """
    import os
    dir_path = r"C:\Users\DAN\OneDrive\Document\myCode\pyinstaller\delay imaging\real-time delay imaging\raw"
    # get a file list for imgings
    file_list = []
    for root, dirs, files in os.walk(dir_path, topdown=False):
        for file in files:
            if file[:7] == "puzzle_" and file[-4:] == '.txt':
                data_path = os.path.join(root, file)
                file_list.append(data_path)
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
    # window.init_data(data, 'delay imaging', np.linspace(0, 125, 125), (105, 105))
    window.init_data(data[:30], 'delay imaging', np.linspace(0, 30, 30), (105, 105))
    window.show()
    sys.exit(app.exec_())