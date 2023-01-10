# -*- coding: utf-8 -*-
"""
@Date     : 2021/5/21 18:06:13
@Author   : milier00
@FileName : ImageProcessing.py
"""
import sys
sys.path.append("./ui/")
sys.path.append("./data/")
sys.path.append("./model/")
from PyQt5.QtWidgets import QMessageBox, QApplication, QMenu, QAction, QMainWindow, QAbstractItemView, QFileDialog, QShortcut
from PyQt5.QtCore import pyqtSignal, Qt
from PyQt5.QtCore import QSettings
from pyqtgraph.Qt import QtGui
from PyQt5 import QtCore
import pyqtgraph as pg
from ImageProcessing_ui import Ui_ImageProcessing
from GraphWindow import myGraphWindow
from DataSelection import myDataSelection
from AdvAGB import myAdvAlgebra
from AdvLC import myAdvLinecut
from AdvCONV import myAdvConv
from ScanInfo import myScanInfo
from PlaneFit import myPlaneFitWin
from Illumination import myIlluminationWin
from Data import *
from func2D import *
import functools as ft
import numpy as np
from sympy import *
import os
import ctypes
import copy
import pickle



class myImageProcessing(QMainWindow, Ui_ImageProcessing):
    # Common signal
    close_signal = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.init_UI()
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("myappid")

    def init_UI(self):
        self.move(50, 50)               # Init ui position

        self.dir_path = ''
        # self.file_type = 0            # file visibility in dir, 0: (.spc); 1: (.dep)
        self.file_index = 0
        self.file_names = []            # expanded file names for internal use
        self.file_paths = []            # file paths according to file_names
        self.displayed_file_names = []  # folded file names in Data listWidget
        self.displayed_file_paths = []  # folded file paths in Data listWidget
        self.entire_file_names = []     # expanded file names in all windows, include plot list and processed list
        self.entire_file_data = []      # self.entire_file_data (2D array) <---> self.entire_file_names
        self.target_list = []           # selected data list from entire_file_name
        self.target_data = []           # self.target_data (2D array) <---> self.target_list
        self.windows = []               # window object list
        self.window_names = []          # window names
        self.linecut_option = 1         # 0: option1, 1: option2
        self.operating_mode_1 = 0       # 0: all map, 1: single map
        self.operating_mode_2 = 0       # 0: global, 1: roi
        self.part_type = 0              # 0: square, 1: circle
        self.linecut_mode = 0           # 0: single angle, 1: multi-angle
        self.linecut_width = 1          # default linecut width is 1

        self.kernel_dict = {0: np.array([[0,-1,0],[-1,5,-1],[0,-1,0]]), 1: np.array([[0,1,0],[1,-4,1],[0,1,0]]), \
                            2: np.array([[0.0625,0.125,0.0625],[0.125,0.25,0.125],[0.0625,0.125,0.125]]), \
                            3: np.array([[0,1,0],[1,9,1],[0,1,0]]),\
                            4: np.array([[-1,-2,-1],[0,0,0],[1,2,1]]), 5: np.array([[-2,-1,0],[-1,1,1],[0,1,2]]), \
                            6: np.array([[-1,-1,-1],[-1,8,-1],[-1,-1,-1]]), 7: np.array([[-1,-1,-1],[-1,9,-1],[-1,-1,-1]]), \
                            8: np.array([[1,1,1],[1,-7,1],[1,1,1]]), \
                            9: np.array([[-1,-1,-1,-1,-1],[-1,2,2,2,-1],[-1,2,8,2,-1],[-1,2,2,2,-1], [-1,-1,-1,-1,-1]])/8.0
                            }

        self.current_window = None
        self.previous_window = None

        self.func2D = myFunc()
        self.map_info = myScanInfo()
        self.data_selection = myDataSelection()
        self.advAGB = myAdvAlgebra()
        self.advLC = myAdvLinecut()
        self.advCONV = myAdvConv()
        self.advPF = myPlaneFitWin()
        self.advIll = myIlluminationWin()
        self.cnfg = QSettings("config.ini", QSettings.IniFormat)  # Basic configuration module

        # signals |
        QApplication.instance().focusChanged.connect(self.focus_window_changed)
        self.data_selection.close_signal.connect(self.show_advAGB)
        self.advAGB.do_signal.connect(self.do_advAGB)
        self.advLC.do_signal.connect(lambda: self.do_advLC(0))
        self.advLC.export_signal.connect(lambda: self.do_advLC(1))
        self.advCONV.close_signal.connect(self.get_user_kernel)
        self.advPF.close_signal.connect(self.get_adv_planefit)
        self.advIll.close_signal.connect(self.get_adv_illuminate)

        # comboBox |
        self.comboBox_conv.currentIndexChanged.connect(self.enable_conv)
        self.comboBox_Smooth.currentIndexChanged.connect(self.smooth_method_changed)

        # pushButton |
        self.pushButton_Open.clicked.connect(self.open_file)
        self.pushButton_Previous.clicked.connect(lambda: self.select_file(0))
        self.pushButton_Next.clicked.connect(lambda: self.select_file(1))
        self.pushButton_Refresh.clicked.connect(self.refresh_list)
        self.pushButton_ShowInfo.clicked.connect(self.show_info)
        self.pushButton_fft.clicked.connect(self.do_fft)
        self.pushButton_do_Smooth.clicked.connect(self.do_smooth)
        self.pushButton_do_Algebra.clicked.connect(self.do_algebra)
        self.pushButton_adv_Algebra.clicked.connect(self.pre_operation_mode3)
        self.pushButton_Export.clicked.connect(self.export_linecut)
        self.pushButton_advLC.clicked.connect(self.show_advLC)
        self.pushButton_do_ConvCore.clicked.connect(self.do_conv)
        self.pushButton_adv_ConvCore.clicked.connect(self.show_advCONV)
        self.pushButton_show_slicing3d.clicked.connect(lambda: self.show_slicing(0))
        self.pushButton_show_slicing2d.clicked.connect(lambda: self.show_slicing(1))
        self.pushButton_cut_Point.clicked.connect(self.cut_roi)
        self.pushButton_cut_Circle.clicked.connect(self.cut_roi)
        self.pushButton_rec_Circle.toggled.connect(self.rec_setup)
        self.pushButton_rec_Circle.setShortcut(QtGui.QKeySequence('R', ))
        self.pushButton_rec_Point.toggled.connect(self.rec_setup)
        self.pushButton_rec_Point.setShortcut(QtGui.QKeySequence('R', ))
        self.pushButton_reccut_Circle.clicked.connect(self.reccut_roi)
        self.pushButton_reccut_Circle.setShortcut(QtGui.QKeySequence('T', ))
        self.pushButton_reccut_Point.clicked.connect(self.reccut_roi)
        self.pushButton_reccut_Point.setShortcut(QtGui.QKeySequence('T', ))
        self.pushButton_avg_export.clicked.connect(self.export_part_avg)
        self.pushButton_FFT_IFFT.clicked.connect(lambda: self.ifft(0))
        self.pushButton_IFFT_IFFT.clicked.connect(lambda: self.ifft(1))
        self.pushButton_advPF_do.clicked.connect(self.adv_planefit)
        self.pushButton_advIll_do.clicked.connect(self.adv_illuminate)

        # radioButton |
        self.radioButton_AllMap.toggled.connect(self.operating_mode_changed)
        self.radioButton_SingleMap.toggled.connect(self.operating_mode_changed)
        self.radioButton_Global.toggled.connect(self.operating_mode_changed)
        self.radioButton_ROI.toggled.connect(self.operating_mode_changed)

        self.radioButton_multi_angle.toggled.connect(self.linecut_mode_changed)
        self.radioButton_single_angle.toggled.connect(self.linecut_mode_changed)

        # groupBox |
        self.groupBox_LineCut.toggled.connect(self.linecut_checked)
        self.groupBox_Option1.toggled.connect(ft.partial(self.linecut_option_changed, 0))
        self.groupBox_Option2.toggled.connect(ft.partial(self.linecut_option_changed, 1))
        self.groupBox_QPoint_Mapping.toggled.connect(self.qpoint_checked)

        self.groupBox_Point_Mapping.toggled.connect(ft.partial(self.part_type_changed, 0))
        self.groupBox_Circle_Mapping.toggled.connect(ft.partial(self.part_type_changed, 1))
        self.groupBox_Point_Mapping.toggled.connect(self.point_checked)
        self.groupBox_Circle_Mapping.toggled.connect(self.circle_checked)

        self.groupBox_IFFT.toggled.connect(self.prepare_ifft)

        # spinBox and slider |
        self.spinBox_Angle_Linecut.editingFinished.connect(lambda: self.spin2slider(2))
        self.slider_Angle_Linecut.valueChanged.connect(ft.partial(self.slider2spin, 2))

        self.spinBox_x_Linecut.editingFinished.connect(lambda: self.linecut_changed(0))
        self.spinBox_y_Linecut.editingFinished.connect(lambda: self.linecut_changed(0))
        self.spinBox_Angle_Linecut.editingFinished.connect(lambda: self.linecut_changed(0))
        self.slider_Angle_Linecut.valueChanged.connect(lambda: self.linecut_changed(0))

        self.spinBox_x1_Linecut.editingFinished.connect(lambda: self.linecut_changed(1))
        self.spinBox_y1_Linecut.editingFinished.connect(lambda: self.linecut_changed(1))
        self.spinBox_x2_Linecut.editingFinished.connect(lambda: self.linecut_changed(1))
        self.spinBox_y2_Linecut.editingFinished.connect(lambda: self.linecut_changed(1))

        self.spinBox_x1_Point.editingFinished.connect(lambda: self.part_changed(0))
        self.spinBox_y1_Point.editingFinished.connect(lambda: self.part_changed(0))
        self.spinBox_x3_Point.editingFinished.connect(lambda: self.part_changed(0))
        self.spinBox_y3_Point.editingFinished.connect(lambda: self.part_changed(0))

        self.spinBox_x0_Circle.editingFinished.connect(lambda: self.circle_changed(0))
        self.spinBox_y0_Circle.editingFinished.connect(lambda: self.circle_changed(0))
        # self.spinBox_x1_Circle.editingFinished.connect(lambda: self.circle_changed(0))
        # self.spinBox_y1_Circle.editingFinished.connect(lambda: self.circle_changed(0))

        self.spinBox_width_Linecut.editingFinished.connect(self.linecut_width_changed)

        # listWidget |
        self.listWidget.setDragEnabled(True)
        self.listWidget.setDragDropOverwriteMode(False)
        self.listWidget.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.listWidget.setDefaultDropAction(Qt.MoveAction)

        self.listWidget.setContextMenuPolicy(Qt.CustomContextMenu)
        self.listWidget.customContextMenuRequested[QtCore.QPoint].connect(self.rightMenuShow)

        self.listWidget.itemDoubleClicked.connect(lambda: self.file_changed(0))
        self.listWidget.itemClicked.connect(lambda: self.file_changed(1))

        # mainMenu |
        self.menu = self.menuBar()
        self.menu.addAction(self.dockWidget_basic.toggleViewAction())
        self.menu.addAction(self.dockWidget_adv.toggleViewAction())
        # self.menu.addAction(self.dockWidget_agb.toggleViewAction())
        self.menu.addAction(self.dockWidget_roi.toggleViewAction())

        # keyboard event |
        QShortcut(QtGui.QKeySequence('Up', ), self, lambda: self.select_file(0))
        QShortcut(QtGui.QKeySequence('Down', ), self, lambda: self.select_file(1))
        QShortcut(QtGui.QKeySequence('Left', ), self, lambda: self.select_file(0))
        QShortcut(QtGui.QKeySequence('Right', ), self, lambda: self.select_file(1))

    # operation mode radio button slot
    def operating_mode_changed(self):
        # update flag
        self.operating_mode_1 = 0 if self.radioButton_AllMap.isChecked() else 1
        self.operating_mode_2 = 0 if self.radioButton_Global.isChecked() else 1
        if self.previous_window != (None or self.map_info):
            self.previous_window.operating_mode_1 = self.operating_mode_1
            self.previous_window.operating_mode_2 = self.operating_mode_2
            self.previous_window.part_type = self.part_type
        # enable/disable part roi if ROI mode is turned on/off
        if self.part_type == 0:
            self.groupBox_Point_Mapping.setChecked(self.operating_mode_2)
        else:
            self.groupBox_Circle_Mapping.setChecked(self.operating_mode_2)

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

    # Data List | file selection changed / single click / double click slot
    def file_changed(self, index):
        ''' Double click to open file in a new window.
            Single click / change selection to change selected data in top level window. '''
        if index == 0:    # double click slot
            if self.listWidget.count() > 0:
                self.file_index = self.listWidget.currentRow()

                # build a new data window
                data_window = myGraphWindow(self.file_names, self.file_paths)
                data_window.operating_mode_1 = self.operating_mode_1
                data_window.operating_mode_2 = self.operating_mode_2
                data_window.part_type = self.part_type
                self.windows.append(data_window)
                self.windows[-1].listWidget.list_changed_signal.connect(self.refresh_list)
                self.windows[-1].destroyed.connect(lambda: self.windows.remove(self.windows[-1]))

                # get selected file
                item = self.listWidget.currentItem()
                add_name = [item.text()]
                data = MappingData(self.file_paths[self.file_names.index(item.text())])
                for i in range(data.child_num):
                    add_name.append(data.child_name[i])

                # add files to new window
                self.windows[-1].listWidget.addItems(add_name)
                self.windows[-1].refresh_list(0)
                self.windows[-1].show()

        elif index == 1:  # file selection changed / single click slot
            if self.listWidget.count() > 0:
                self.file_index = self.listWidget.currentRow()

                # update plot list in window
                if self.previous_window != None:
                    if self.previous_window.listWidget.currentItem() != None:
                        if len(self.previous_window.listWidget.selectedItems()) != 0:
                            self.previous_window.delete(0)
                            self.add2window()
                            self.previous_window.listWidget.setCurrentRow(0)

    # Data List | right click menu
    def rightMenuShow(self):
        rightMenu = QMenu(self.listWidget)
        add2winAction = QAction("Add to current window", self, triggered=self.add2window)
        rightMenu.addAction(add2winAction)
        open2winAction = QAction("Open in new window", self, triggered=self.open2window)
        rightMenu.addAction(open2winAction)
        rightMenu.exec_(QtGui.QCursor.pos())

    # Menu | add to current window action slot
    def add2window(self):
        # get selected file index
        items = self.listWidget.selectedItems()
        add_index = []
        add_name = []
        for item in items:
            add_index.append(self.file_names.index(item.text()))
            add_name.append(item.text())

        for item in items:
            data = MappingData(self.file_paths[self.file_names.index(item.text())])
            for i in range(data.child_num):
                add_name.append(data.child_name[i])

        self.previous_window.listWidget.addItems(add_name)
        self.previous_window.refresh_list(0)

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
        self.windows[-1].destroyed.connect(lambda: self.windows.remove(self.windows[-1]))
        self.windows[-1].listWidget.addItems(add_name)
        # self.windows[-1].set_list_checked(0)
        self.windows[-1].refresh_list(0)
        self.windows[-1].show()

    # !!! not used | copy to new window button slot
    def copy2window(self):
        data_window = myGraphWindow(self.file_names, self.file_paths)
        data_window.operating_mode_1 = self.operating_mode_1
        data_window.operating_mode_2 = self.operating_mode_2
        data_window.part_type = self.part_type
        self.windows.append(data_window)
        self.windows[-1].listWidget.list_changed_signal.connect(self.refresh_list)
        self.windows[-1].destroyed.connect(lambda: self.windows.remove(self.windows[-1]))
        self.windows[-1].file_type = copy.deepcopy(self.previous_window.file_type)
        self.windows[-1].comboBox.setCurrentIndex(self.windows[-1].file_type)
        self.windows[-1].listWidget.addItems(self.previous_window.plot_list)
        # self.windows[-1].set_list_checked(0)
        self.windows[-1].refresh_list(0)
        self.windows[-1].listWidget_Processed.addItems(self.previous_window.processed_list)
        self.windows[-1].processed_data = copy.deepcopy(self.previous_window.processed_data)
        # self.windows[-1].set_list_checked(1)
        self.windows[-1].refresh_list(1)
        self.windows[-1].show()

    # Data List | open folder button slot
    def open_file(self):
        self.dir_path = self.cnfg.value("CNFG/FILE_PATH", type=str)
        if os.path.exists(self.dir_path):
            aFile, filt = QFileDialog.getOpenFileName(self, "Open file", self.dir_path, "NSTM(*.nstm)")
        else:
            curDir = "E:/Code/2022oct/"
            # curDir = QDir.currentPath()
            # curDir = "../test data/"
            aFile, filt = QFileDialog.getOpenFileName(self, "Open file", curDir, "NSTM(*.nstm)")

        dir, file = os.path.split(aFile)
        self.dir_path = dir
        # self.name_prefic = file[:-10]
        # self.prefix_len = len(file) - 10
        # self.get_overall_list()

        self.file_paths.clear()
        self.file_names.clear()
        self.displayed_file_names.clear()
        self.displayed_file_paths.clear()
        self.listWidget.clear()

        for root, dirs, files in os.walk(self.dir_path, topdown=False):
            for file in files:
                if file[-5:] == ".nstm":
                    data_path = os.path.join(root, file)
                    self.displayed_file_names.append(file)
                    self.displayed_file_paths.append(data_path)
                    data = MappingData(data_path)
                    self.file_paths.append(data.path)
                    self.file_names.append(data.name)
                    for i in range(data.child_num):
                        self.file_paths.append(data.path)
                        self.file_names.append(data.child_name[i])

        if len(self.file_paths) <= 0:
            return

        self.lineEdit.setText(self.dir_path)
        self.listWidget.addItems(self.displayed_file_names)
        print(self.file_names)
        print(self.file_paths)
        # refresh file list every second
        # self.timer.start(5000)
        # self.workThread.start()
        # self.workThread.trigger.connect(self.timer.stop)
        # self.timer.timeout.connect(self.refresh_file)

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
                    self.displayed_file_names.append(file)
                    self.displayed_file_paths.append(data_path)
                    data = MappingData(data_path)
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

    # Info | open info button slot
    def show_info(self):
        data_path = self.file_paths[self.file_names.index(self.listWidget.currentItem().text())]
        with open(data_path, 'rb') as input:
            data = pickle.load(input)
        self.map_info.init_scanInfo(data)
        self.map_info.setWindowTitle('Info: '+ self.listWidget.currentItem().text())
        self.map_info.setWindowModality(2)
        self.map_info.show()

    # Windows | update previous/current window
    def focus_window_changed(self, old, new):
        ''' Note that current window and previous window are myGraphWindow() '''
        if new != None and isinstance(new.window(), myGraphWindow):
            self.current_window = new.window()
            if hasattr(self.current_window, 'linecut'):
                self.current_window.linecut.sigRegionChanged.connect(lambda: self.linecut_changed(2))
            if hasattr(self.current_window, 'update_display_signal'):
                self.current_window.update_display_signal.connect(self.setup_range)
                self.current_window.update_display_signal.connect(self.edit_update_info)
            if hasattr(self.current_window, 'part_s'):
                self.current_window.part_s.sigRegionChanged.connect(lambda: self.part_changed(1))
                self.current_window.part_s.sigRegionChanged.connect(self.update_part_info)
            if hasattr(self.current_window, 'part_c'):
                self.current_window.part_c.sigRegionChanged.connect(lambda: self.circle_changed(1))
                self.current_window.part_c.sigRegionChanged.connect(self.update_circle_info)
            if hasattr(self.current_window, 'qpoint'):
                self.current_window.qpoint.sigRegionChanged.connect(self.update_qpoint_info)

        if old != None and isinstance(old.window(), myGraphWindow):
            self.previous_window = old.window()

    # ROI | Point & Circle groupBox slot
    def part_type_changed(self, index, status):
        if status:
            # self.previous_window.linecut.setPos([0, 0])
            if index == 0:
                self.groupBox_Circle_Mapping.setChecked(False)
                self.part_type = 0
            elif index == 1:
                self.groupBox_Point_Mapping.setChecked(False)
                self.part_type = 1
            if hasattr(self.previous_window, "part_type"):
                self.previous_window.part_type = self.part_type

    # Point | Point group box slot
    def point_checked(self, status):
        if hasattr(self.previous_window, "part_s") and hasattr(self.previous_window, "img_display"):
            if status:
                self.previous_window.part_s.movePoint(self.previous_window.part_s.getHandles()[1],
                                                       [self.previous_window.img_display.width() / 2,
                                                        self.previous_window.img_display.height() / 2])
                self.previous_window.part_s.show()
            else:
                self.previous_window.part_s.hide()

    # Circle | Circle group box slot
    def circle_checked(self, status):
        if hasattr(self.previous_window, "part_c") and hasattr(self.previous_window, "img_display"):
            if status:
                self.previous_window.part_c.movePoint(self.previous_window.part_c.getHandles()[0],
                                                       [self.previous_window.img_display.width() / 2,
                                                        self.previous_window.img_display.height() / 2])
                self.previous_window.part_c.show()
            else:
                self.previous_window.part_c.hide()

    # Point | input changed (0), roi changed (1)
    def part_changed(self, index):
        if index == 0:
            x1 = self.spinBox_x1_Point.value()
            y1 = self.spinBox_y1_Point.value()
            x3 = self.spinBox_x3_Point.value()
            y3 = self.spinBox_y3_Point.value()
            self.previous_window.part_s.movePoint(self.previous_window.part_s.getHandles()[0], [x1, y1], finish=False)
            self.previous_window.part_s.movePoint(self.previous_window.part_s.getHandles()[1], [x3 + x1, y3 + y1])
            self.previous_window.part_s.setPos([x1, y1])
        elif index == 1:
            x1 = int(self.previous_window.part_s.pos()[0])
            y1 = int(self.previous_window.part_s.pos()[1])
            x3 = int(self.previous_window.part_s.getHandles()[1].pos()[0])
            y3 = int(self.previous_window.part_s.getHandles()[1].pos()[1])
            self.spinBox_x1_Point.setValue(x1)
            self.spinBox_y1_Point.setValue(y1)
            self.spinBox_x3_Point.setValue(x3)
            self.spinBox_y3_Point.setValue(y3)

    # !!! not used | part_s sig region chenge finished
    def align2pixel(self, _):
        print('Finished!!!')
        ## disconnect signals to avoid recursion
        # self.previous_window.part_s.mysigRegionChanged.disconnect(lambda: self.part_changed(1))
        # self.previous_window.part_s.mysigRegionChanged.disconnect(self.update_part_info)
        # self.previous_window.part_s.blockSignals(True)
        # self.previous_window.part_s.mysigRegionChanged.disconnect()
        ## move points to slign with pixel
        x1 = self.spinBox_x1_Point.value()
        y1 = self.spinBox_y1_Point.value()
        x3 = self.spinBox_x3_Point.value()
        y3 = self.spinBox_y3_Point.value()
        self.previous_window.part_s.movePoint(self.previous_window.part_s.getHandles()[0], [x1, y1], finish=False)
        self.previous_window.part_s.movePoint(self.previous_window.part_s.getHandles()[1], [x3 + x1, y3 + y1])
        self.previous_window.part_s.setPos([x1, y1])
        ## reconnect signals
        # self.previous_window.part_s.blockSignals(False)
        # self.previous_window.part_s.mysigRegionChanged.connect(lambda: self.part_changed(1))
        # self.previous_window.part_s.mysigRegionChanged.connect(self.update_part_info)

    # !!! not used
    def disconnect(self, signal, handler=None):
        try:
            if handler is not None:
                while True:
                    signal.disconnect(handler)
            else:
                signal.disconnect()
        except TypeError:
            pass

    # Circle | input changed (0), roi changed (1)
    def circle_changed(self, index):
        if index == 0:
            x0 = self.spinBox_x0_Circle.value()
            y0 = self.spinBox_y0_Circle.value()
            # x1 = self.spinBox_x1_Circle.value()
            # y1 = self.spinBox_y1_Circle.value()
            # self.previous_window.part_c.movePoint(self.previous_window.part_c.getHandles()[0], [x0+x1, y0+y1], finish=False)
            self.previous_window.part_c.setPos([x0, y0])
        elif index == 1:
            x0 = int(self.previous_window.part_c.pos()[0])
            y0 = int(self.previous_window.part_c.pos()[1])
            # x1 = int(self.previous_window.part_c.getHandles()[0].pos()[0])
            # y1 = int(self.previous_window.part_c.getHandles()[0].pos()[1])
            self.spinBox_x0_Circle.setValue(x0)
            self.spinBox_y0_Circle.setValue(y0)
            # self.spinBox_x1_Point.setValue(x1)
            # self.spinBox_y1_Point.setValue(y1)

    # Point & Circle | update display signal slot
    def edit_update_info(self):
        if self.part_type == 0:
            self.update_part_info()
        else:
            self.update_circle_info()

    # Point | update info
    def update_part_info(self):
        if self.previous_window != None:
            try:
                data, name, energy, rscale = self.previous_window.get_current_child()
                ret = self.previous_window.part_s.getArrayRegion(data, self.previous_window.img_display, axes=(0, 1), returnMappedCoords=True)
                if np.abs(np.average(ret[0])) < 1e-5:
                    self.lineEdit_avg.setText(str(round(np.average(ret[0])*1e12, 5))+' *1e-12')
                    self.lineEdit_sum.setText(str(round(np.sum(ret[0])*1e12, 5))+' *1e-12')
                else:
                    self.lineEdit_avg.setText(str(round(np.average(ret[0]), 5)))
                    self.lineEdit_sum.setText(str(round(np.sum(ret[0]), 5)))
            except:
                pass

    # Circle | update info
    def update_circle_info(self):
        data, name, energy, rscale = self.previous_window.get_current_child()
        ret = self.previous_window.part_c.getArrayRegion(data, self.previous_window.img_display, axes=(0, 1), returnMappedCoords=True)
        if np.abs(np.average(ret[0])) < 1e-5:
            self.lineEdit_avg.setText(str(round(np.average(ret[0])*1e12, 5))+' *1e-12')
            self.lineEdit_sum.setText(str(round(np.sum(ret[0])*1e12, 5))+' *1e-12')
        else:
            self.lineEdit_avg.setText(str(round(np.average(ret[0]), 5)))
            self.lineEdit_sum.setText(str(round(np.sum(ret[0]), 5)))

    # Point & Circle | export avg value to dat
    def export_part_avg(self):
        data, name, energy, rscale = self.previous_window.get_current_parent()
        avg_values = []
        for i in range(data.shape[0]):
            if self.part_type == 0:
                ret = self.previous_window.part_s.getArrayRegion(data[i], self.previous_window.img_display, axes=(0, 1), returnMappedCoords=True)
            else:
                ret = self.previous_window.part_c.getArrayRegion(data[i], self.previous_window.img_display, axes=(0, 1), returnMappedCoords=True)
            avg = np.average(ret[0])
            avg_values.append(avg)
        avg_values = np.array(avg_values)
        default_name = self.dir_path + '/' + 'roi_avg_' + name[:-4]
        fileName, ok = QFileDialog.getSaveFileName(self, "Save", default_name, "DAT(*.dat)")
        np.savetxt(fileName, avg_values, delimiter='\t', comments='')

    # QPoint | QPoint group box slot
    def qpoint_checked(self, status):
        if status:
            self.previous_window.qpoint.movePoint(self.previous_window.qpoint.getHandles()[0],\
                                                  [self.previous_window.img_display.width() / 2, \
                                                   self.previous_window.img_display.height() / 2])
            self.previous_window.qpoint.setSize([self.previous_window.img_display.width() / 20, \
                                                   self.previous_window.img_display.height() / 20])
            self.previous_window.qpoint.show()
        else:
            self.previous_window.qpoint.hide()

    # QPoint | update info
    def update_qpoint_info(self):
        """ ccpp 1.3 """
        # pos = (self.previous_window.qpoint.getHandles()[0].pos()[0] + self.previous_window.qpoint.pos()[0],
        #        self.previous_window.qpoint.getHandles()[0].pos()[1] + self.previous_window.qpoint.pos()[1])
        # pos_center = (pos[0]-self.previous_window.img_display.width()/2, pos[1] - self.previous_window.img_display.height()/2)
        # pos_ratio = (pos_center[0]/(self.previous_window.img_display.width()/2), pos_center[1]/(self.previous_window.img_display.height()/2))
        # xscale = int(self.lineEdit_x_QPoint.text())*10 if self.lineEdit_x_QPoint.text() !='' else None
        # yscale = int(self.lineEdit_y_QPoint.text())*10 if self.lineEdit_y_QPoint.text() !='' else None
        # if xscale != None and yscale!= None:
        #     bounds = (np.pi/(xscale/self.previous_window.img_display.width()), np.pi/(yscale/self.previous_window.img_display.height()))
        #     pos_q = (pos_ratio[0]* bounds[0], pos_ratio[1] * bounds[1])
        #     pos_str = str(round(pos_q[0],3)) + ', ' + str(round(pos_q[1],3))
        #     self.lineEdit_qpoint.setText(pos_str)
        # else:
        #     self.lineEdit_qpoint.setText('Input xy!')
        """ STM data pro """
        pos = (self.previous_window.qpoint.getHandles()[0].pos()[0] + self.previous_window.qpoint.pos()[0],
               self.previous_window.qpoint.getHandles()[0].pos()[1] + self.previous_window.qpoint.pos()[1])
        value = self.previous_window.raw_img[int(np.trunc(pos[0])), int(np.trunc(pos[1]))]
        self.lineEdit_qpoint.setText(str(round(value,6)))

    # FFT (OP1) | do it button slot
    def do_fft(self):
        self.radioButton_AllMap.setChecked(True)
        self.previous_window.fft()

    # Smooth | comboBox slot, enable/disable and change params name
    def smooth_method_changed(self, index):
        if index == 1 or 2:   # Uniform, Gaussian-Laplace
            self.spinBox_degree_Smooth.setEnabled(False)
            self.label_20.setEnabled(False)
            self.label_20.setText('order')
            self.lineEdit_area_Smooth.setEnabled(True)
            self.label_19.setEnabled(True)
            self.label_19.setText('area')
            self.lineEdit_val_Smooth.setEnabled(False)
            self.label_17.setEnabled(False)
            self.label_17.setText('value')
        if index == 3:   # Set to value
            self.spinBox_degree_Smooth.setEnabled(False)
            self.label_20.setEnabled(False)
            self.label_20.setText('order')
            self.lineEdit_area_Smooth.setEnabled(False)
            self.label_19.setEnabled(False)
            self.label_19.setText('area')
            self.lineEdit_val_Smooth.setEnabled(True)
            self.label_17.setEnabled(True)
            self.label_17.setText('value')
        if index == 4:  # Symmetry
            self.spinBox_degree_Smooth.setEnabled(True)
            self.label_20.setEnabled(True)
            self.label_20.setText('order')
            self.lineEdit_area_Smooth.setEnabled(False)
            self.label_19.setEnabled(False)
            self.label_19.setText('area')
            self.lineEdit_val_Smooth.setEnabled(False)
            self.label_17.setEnabled(False)
            self.label_17.setText('value')
        if index == 5:    # Delete bad point
            self.spinBox_degree_Smooth.setEnabled(False)
            self.label_20.setEnabled(False)
            self.label_20.setText('order')
            self.lineEdit_area_Smooth.setEnabled(True)
            self.label_19.setEnabled(True)
            self.label_19.setText('min')
            self.lineEdit_val_Smooth.setEnabled(True)
            self.label_17.setEnabled(True)
            self.label_17.setText('max')
        if index == 0:  # Gaussian
            self.spinBox_degree_Smooth.setEnabled(True)
            self.label_20.setEnabled(True)
            self.label_20.setText('order')
            self.lineEdit_area_Smooth.setEnabled(True)
            self.label_19.setEnabled(True)
            self.label_19.setText('area')
            self.lineEdit_val_Smooth.setEnabled(False)
            self.label_17.setEnabled(False)
            self.label_17.setText('value')

    # Smooth (OP1 & OP2) | do it button slot
    def do_smooth(self):
        method = self.comboBox_Smooth.currentIndex()
        val = float(self.lineEdit_val_Smooth.text()) if self.lineEdit_val_Smooth.text() != '' else 0
        area = float(self.lineEdit_area_Smooth.text()) if self.lineEdit_area_Smooth.text() != '' else 0
        order = self.spinBox_degree_Smooth.value()
        self.previous_window.smooth(method, area, order, val)

    # Algebra (OP1 & OP2) | do it button slot
    def do_algebra(self):
        operation = self.comboBox_Algebra.currentIndex()
        value = float(self.lineEdit_Algebra.text())
        self.previous_window.algebra(operation, value)

    # preparation for operation mode 3
    def pre_operation_mode3(self):
        # collect all open windows' plot list and processed list (expanded and only child)
        self.entire_file_names = []
        self.entire_file_data = []
        print(len(self.windows))
        for window in self.windows:
            self.entire_file_names += window.expanded_plot_list
            self.entire_file_names += window.expanded_pro_list
            self.entire_file_data += window.expanded_plot_data
            self.entire_file_data += window.expanded_pro_data

        # list them in pop up window
        self.data_selection.init_list(self.entire_file_names)
        self.data_selection.show()

    # Advanced Algebra (OP3) | show Advanced algebra window
    def show_advAGB(self, data_list):
        # find corresponding data and do the algebra
        self.target_data = []
        self.target_list = []

        for data in data_list:
            self.target_data.append(self.entire_file_data[self.entire_file_names.index(data)])
        self.target_list = copy.deepcopy(data_list)

        size = self.target_data[0].shape
        for data in self.target_data:
            if data.shape == size:
                continue
            else:
                QMessageBox.warning(None, "Adv algebra", 'Data have different sizes!', QMessageBox.Ok)
                return

        text = ''
        for i in range(len(data_list)):
            text += 'x_' + str(i) + ':' + data_list[i] + '\n'
        self.advAGB.label_data.setText(text)
        self.advAGB.show()

    # Advanced Algebra (OP3) | do calculation for selected data
    def do_advAGB(self):
        # make a fake MappingResult data
        fake_result = MappingResult(self.previous_window.data[0], 0)

        # do adv algebra
        expr = self.advAGB.lineEdit.text()
        x_0, x_1, x_2, x_3 = symbols('x_0 x_1 x_2 x_3')
        num = len(self.target_data)
        if num == 1:
            f = lambdify([x_0], expr, 'numpy')
            img = f(self.target_data[0])
            fake_result.name = 'AdvAlgebra-' + self.target_list[0][-4:]
        elif num == 2:
            f = lambdify([x_0, x_1], expr, 'numpy')
            img = f(self.target_data[0], self.target_data[1])
            fake_result.name = 'AdvAlgebra-' + self.target_list[0][-4:] + '-' + self.target_list[1][-4:]
        elif num == 3:
            f = lambdify([x_0, x_1, x_2], expr, 'numpy')
            img = f(self.target_data[0], self.target_data[1], self.target_data[2])
            fake_result.name = 'AdvAlgebra-' + self.target_list[0][-4:] + '-' + self.target_list[1][-4:] + '-' + self.target_list[2][-4:]
        elif num == 4:
            f = lambdify([x_0, x_1, x_2, x_3], expr, 'numpy')
            img = f(self.target_data[0], self.target_data[1], self.target_data[2], self.target_data[3])
            fake_result.name = 'AdvAlgebra-' + self.target_list[0][-4:] + '-' + self.target_list[1][-4:] + '-' + self.target_list[2][-4:] + '-' + self.target_list[3][-4:]

        # append result in a previous window
        img = np.reshape(img, (1, img.shape[0], img.shape[1]))
        fake_result.result = img
        fake_result.energy = [-1]     # energy and scale are meaningless
        fake_result.scale = [(-1, -1)]
        self.previous_window.processed_data.append(fake_result)
        fake_result.name = self.previous_window.avoid_repeat_name(fake_result.name)
        self.previous_window.listWidget_Processed.addItem(fake_result.name)
        self.previous_window.refresh_list(1)

    # Line cut  (OP1 & OP2) | set up line cut and part range
    def setup_range(self):
        if (self.current_window != None) and (self.current_window != self.window()):
            width = self.current_window.img_display.width()
            height = self.current_window.img_display.height()
            self.spinBox_x1_Linecut.setMaximum(width)
            self.spinBox_y1_Linecut.setMaximum(height)
            self.spinBox_x2_Linecut.setMaximum(width)
            self.spinBox_y2_Linecut.setMaximum(height)
            self.spinBox_x_Linecut.setMaximum(width)
            self.spinBox_y_Linecut.setMaximum(height)

            self.spinBox_x1_Point.setMaximum(width)
            self.spinBox_y1_Point.setMaximum(height)
            self.spinBox_x3_Point.setMaximum(width)
            self.spinBox_y3_Point.setMaximum(height)

            self.spinBox_x0_Circle.setMaximum(width)
            self.spinBox_y0_Circle.setMaximum(height)
            # self.spinBox_x1_Circle.setMaximum(width)
            # self.spinBox_y1_Circle.setMaximum(height)

    # Line cut | Line cut groupBox slot
    def linecut_checked(self, status):
        if hasattr(self.previous_window, "linecut") and hasattr(self.previous_window, "img_display"):
            if status:
                self.previous_window.linecut.movePoint(self.previous_window.linecut.getHandles()[1], [self.previous_window.img_display.width()/2, self.previous_window.img_display.height()/2])
                self.previous_window.linecut.show()
            else:
                self.previous_window.linecut.hide()
            self.enable_linecut(status)

    # Line cut | enable items in other 3ds after linecut_changed
    def enable_linecut(self, enable):
        self.pushButton_advLC.setEnabled(enable)
        self.pushButton_Export.setEnabled(enable)
        self.radioButton_multi_angle.setEnabled(enable)
        self.radioButton_single_angle.setEnabled(enable)
        if enable:
            self.linecut_mode_changed()
        else:
            self.spinBox_delta_theta.setEnabled(False)
            self.spinBox_angle_num.setEnabled(False)

    # Line cut | Line cut option slot
    def linecut_option_changed(self, index, status):
        if hasattr(self.previous_window, "linecut"):
            if status:
                self.previous_window.linecut.setPos([0, 0])
                if index == 0:
                    self.previous_window.linecut.removeHandle(0)
                    pos = [self.previous_window.linecut.pos()[0], self.previous_window.linecut.pos()[1]]
                    self.previous_window.linecut_rot_handle1 = self.previous_window.linecut.addRotateHandle(pos=pos, center=pos, index=0)
                    self.groupBox_Option2.setChecked(False)
                    self.linecut_option = 0
                elif index == 1:
                    self.previous_window.linecut.removeHandle(0)
                    pos = [self.previous_window.linecut.pos()[0], self.previous_window.linecut.pos()[1]]
                    self.previous_window.linecut_free_handle1 = self.previous_window.linecut.addTranslateHandle(pos=pos, index=0)
                    purple_pen = pg.mkPen((220, 180, 255, 255), width=2)
                    self.previous_window.linecut.getHandles()[0].pen = purple_pen
                    self.previous_window.linecut.getHandles()[0].radius = 10
                    self.groupBox_Option1.setChecked(False)
                    self.linecut_option = 1

    # Line cut | Line cut
    def linecut_changed(self, index):
        if index == 0:      # line-cut operation 1
            x = self.spinBox_x_Linecut.value()
            y = self.spinBox_y_Linecut.value()
            angle = self.spinBox_Angle_Linecut.value()
            self.previous_window.linecut.setPos([x, y])
            self.previous_window.linecut.movePoint(self.previous_window.linecut.getHandles()[0], [x, y])
            self.previous_window.linecut.setAngle(angle, snap=True)
        elif index == 1:    # line-cut operation 2
            x1 = self.spinBox_x1_Linecut.value()
            y1 = self.spinBox_y1_Linecut.value()
            x2 = self.spinBox_x2_Linecut.value()
            y2 = self.spinBox_y2_Linecut.value()
            self.previous_window.linecut.movePoint(self.previous_window.linecut.getHandles()[0], [x1, y1], finish=False)
            self.previous_window.linecut.movePoint(self.previous_window.linecut.getHandles()[1], [x2 + x1, y2 + y1])
            self.previous_window.linecut.setPos([x1, y1])
        elif index == 2:    # sigRegionChanged
            if self.linecut_option == 0:
                x = int(self.previous_window.linecut.pos()[0])
                y = int(self.previous_window.linecut.pos()[1])
                angle = self.previous_window.linecut.angle()
                self.spinBox_x_Linecut.setValue(x)
                self.spinBox_y_Linecut.setValue(y)
                self.spinBox_Angle_Linecut.setValue(angle)
            elif self.linecut_option == 1:
                x = int(self.previous_window.linecut.pos()[0])
                y = int(self.previous_window.linecut.pos()[1])
                x1 = int(self.previous_window.linecut.getHandles()[0].pos()[0])
                y1 = int(self.previous_window.linecut.getHandles()[0].pos()[1])
                if len(self.previous_window.linecut.handles) > 1:
                    x2 = int(self.previous_window.linecut.getHandles()[1].pos()[0])
                    y2 = int(self.previous_window.linecut.getHandles()[1].pos()[1])
                    self.spinBox_x1_Linecut.setValue(x)
                    self.spinBox_y1_Linecut.setValue(y)
                    self.spinBox_x2_Linecut.setValue(x2)
                    self.spinBox_y2_Linecut.setValue(y2)

    # Line cut | connect spinBox and slider
    def slider2spin(self, index, bits):
        if index == 2:  # line cut angle
            self.spinBox_Angle_Linecut.setValue(round(bits / 100, 2))

    # Line cut | connect spinBox and slider
    def spin2slider(self, index):
        if index == 2:  # line cut angle
            value = int(self.spinBox_Angle_Linecut.value() * 100)
            self.slider_Angle_Linecut.setValue(value)

    # Line cut | linecut width changed slot
    def linecut_width_changed(self):
        self.linecut_width = self.spinBox_width_Linecut.value()
        self.previous_window.linecut_width = self.spinBox_width_Linecut.value()
        self.previous_window.linecut.pen.setWidth(self.previous_window.linecut_width)
        self.previous_window.linecut.update()

    # Line cut | line cut export mode radioButton slot
    def linecut_mode_changed(self):
        self.linecut_mode = 0 if self.radioButton_single_angle.isChecked() else 1
        if self.linecut_mode == 0:      # single angle
            self.spinBox_delta_theta.setEnabled(False)
            self.spinBox_angle_num.setEnabled(False)
        elif self.linecut_mode == 1:    # multi-angle
            self.spinBox_delta_theta.setEnabled(True)
            self.spinBox_angle_num.setEnabled(True)
            self.groupBox_Option1.setChecked(True)  # set line cut operation 1
        if self.previous_window != (None or self.map_info):
            self.previous_window.linecut_mode = self.linecut_mode

    # Line cut | export line cut data
    def export_linecut(self):
        if self.linecut_mode == 0:
            angle = self.spinBox_Angle_Linecut.value()
            self.previous_window.export_linecut(self.dir_path, angle)
        elif self.linecut_mode == 1:
            angle = self.spinBox_Angle_Linecut.value()
            delta = self.spinBox_delta_theta.value()
            num = self.spinBox_angle_num.value()
            self.previous_window.export_linecut(self.dir_path, angle)
            new_angle = copy.deepcopy(angle)
            for i in range(1, num):
                new_angle = int(new_angle+delta) if (new_angle+delta) <= 360 else int(new_angle+delta) % 360
                self.slider_Angle_Linecut.setValue(new_angle*100)
                self.previous_window.export_linecut(self.dir_path, new_angle)

    # Line cut | advanced line cut button slot
    def show_advLC(self):
        self.advLC.show()

    # Line cut | advLC window Do(index = 0) and Export(index = 1) button slot
    def do_advLC(self, index):
        if self.advLC.mode == 0:    # energy
            angle = self.spinBox_Angle_Linecut.value()
            data = self.previous_window.adv_linecut(0, angle)
        elif self.advLC.mode == 1:    # angle
            angle = self.spinBox_Angle_Linecut.value()
            delta = self.advLC.spinBox_delta.value()
            num = self.advLC.spinBox_num.value()
            new_angle = copy.deepcopy(angle)
            cut, data = self.previous_window.adv_linecut(1, angle)
            for i in range(1, num):
                new_angle = int(new_angle + delta) if (new_angle + delta) <= 360 else int(new_angle + delta) % 360
                self.slider_Angle_Linecut.setValue(new_angle * 100)
                new_cut, y = self.previous_window.adv_linecut(1, new_angle)
                cut = np.vstack((cut, new_cut))
            data.target = [cut]
        self.previous_window.patch_linecut(index, self.dir_path, data)

    def show_advCONV(self):
        self.advCONV.show()

    def enable_conv(self, index):
        if index != 10:      # default kernel selected
            self.pushButton_adv_ConvCore.setEnabled(False)
        elif index == 10:    # user defined kernel selected
            self.pushButton_adv_ConvCore.setEnabled(True)

    def get_user_kernel(self, kernel):
        self.user_kernel = kernel

    def do_conv(self):
        kernel_index = self.comboBox_conv.currentIndex()
        if kernel_index != 10:   # default kernel selected
            kernel = self.kernel_dict[kernel_index]
            self.previous_window.adv_conv(kernel)

        elif kernel_index == 10: # user defined kernel selected
            self.previous_window.adv_conv(self.user_kernel)

    def show_slicing(self, index):
        self.previous_window.data_slicing(index)

    def cut_roi(self):
        self.previous_window.roi_cut()

    def rec_setup(self, status):
        self.previous_window.roi_rec(status)
        if self.previous_window.part_type == 1:
            self.pushButton_cut_Circle.setEnabled(not status)
            self.pushButton_reccut_Circle.setEnabled(status)
        else:
            self.pushButton_cut_Point.setEnabled(not status)
            self.pushButton_reccut_Point.setEnabled(status)

    def reccut_roi(self):
        self.previous_window.reccut_flag = True
        self.previous_window.roi_reccut()

    def write_cnfg(self):
        self.cnfg.clear()
        self.cnfg.setValue("CNFG/FILE_PATH", self.dir_path)

    def prepare_ifft(self, status):
        if status:
            self.radioButton_AllMap.setChecked(True)
        self.previous_window.ifft_mode = status
        self.groupBox_LineCut.setEnabled(not status)
        self.groupBox_QPoint_Mapping.setEnabled(not status)
        self.dockWidget_basic.setEnabled(not status)
        self.dockWidget_other.setEnabled(not status)
        self.groupBox_fitting.setEnabled(not status)
        self.groupBox_conv.setEnabled(not status)
        self.groupBox_slicing.setEnabled(not status)
        self.radioButton_SingleMap.setEnabled(not status)

    def ifft(self, index):
        if index == 0:
            self.previous_window.fft_i()
        elif index == 1:
            self.previous_window.ifft()

    def adv_planefit(self):
        self.advPF.init_data(self.previous_window.raw_img)
        self.advPF.show()
        self.advPF.raise_()

    def get_adv_planefit(self, fitted):
        self.previous_window.adv_plane_fit(fitted)

    def adv_illuminate(self):
        self.advIll.init_data(self.previous_window.raw_img)
        self.advIll.show()
        self.advIll.raise_()

    def get_adv_illuminate(self, illuminated):
        self.previous_window.adv_illumination(illuminated)

    def closeEvent(self, event):
        self.write_cnfg()  # Write configuration file
        sys.exit(0)     # Close all aub windows




if __name__ == "__main__":
    # QtCore.QCoreApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling)
    # enable dpi scale
    # QApplication.setHighDpiScaleFactorRoundingPolicy(
    # Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)
    # QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
    # QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps)
    app = QApplication(sys.argv)
    window = myImageProcessing()
    app.setStyle("Fusion")
    window.show()
    sys.exit(app.exec_())

'''   
2022/12/3
pyqtgraph 0.12.4 pypi_0 pypi  --->   pyqtgraph 0.13.1 pypi_0 pypi 
'''