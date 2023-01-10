# -*- coding: utf-8 -*-
"""
@Date     : 2022/12/10 20:57:41
@Author   : milier00
@FileName : SpcWindow.py
"""
import sys
sys.path.append("./ui/")
sys.path.append("./model/")
sys.path.append("./Plot2D3D/")
from PyQt5.QtWidgets import QApplication, QWidget, QSizePolicy, QInputDialog, QMessageBox, \
    QAbstractItemView, QGridLayout, QFileDialog, QShortcut, QListWidget, QMenu, QAction
from PyQt5.QtCore import pyqtSignal, Qt
from PyQt5.QtGui import QKeySequence
from pyqtgraph.Qt import QtGui, QtCore
from images import myImages
from SpcWin_ui import Ui_SpcWin
from switch_button import SwitchButton
from SpcPassEditor import mySpcPassEditor
from message_dialog import MessageDialog
from SpectroscopyInfo import mySpectroscopyInfo
from CalibrateIETS import myCalIETSWindow
from CalibrateTRS import myCalTRSWindow
from AdvancedAlgebra import myAdvAlgebra
from SimCurve import mySimCurve
from PlotWindow import myPlotWindow
from DrawSpc import myDrawSpc
from WeightedAVG import myWeightedAVG
from Data import *
from func1D import *
from collections import defaultdict
import numpy as np
import functools as ft
import pyqtgraph as pg
import scipy
from sympy import *
import math
import copy
import ctypes
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

class mySpcWindow(QWidget, Ui_SpcWin):
    # Common signal
    close_signal = pyqtSignal()
    list_changed_signal = pyqtSignal()

    def __init__(self, data_list, data_paths):
        super().__init__()
        pg.setConfigOption('background', (240, 240, 240, 255))
        pg.setConfigOption('foreground', 'k')
        self.setupUi(self)
        self.init_UI(data_list, data_paths)
        self.setAttribute(Qt.WA_DeleteOnClose)  # make sure the window object is deleted after close
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("myappid")
        ''' Add these lines to DataWindow_ui.py '''
        # import pyqtgraph as pg
        # pg.setConfigOption('background', (240, 240, 240, 255))
        # pg.setConfigOption('foreground', 'k')

    def init_UI(self, data_list, data_paths):
        self.move(700, 100)         # Init ui position

        self.parent_data_list = copy.deepcopy(data_list)
        self.parent_data_paths = copy.deepcopy(data_paths)

        self.indentor = '      '
        self.plot_list = []
        self.data_list = []
        self.del_pass_dict = defaultdict(list)
        self.current_pt_dict = defaultdict(int)
        self.displayed_plot_list = []
        self.processed_list = []
        self.displayed_pro_list = []
        self.processed_data = []
        self.data = []
        self.current_list = None
        self.show_fb = True      # True: show forward and backward channels
        self.show_pt = False        # True: expand all pts

        self.img = myImages()
        self.func1D = myFunc()
        self.passEditor = mySpcPassEditor()
        self.spcInfo = mySpectroscopyInfo()
        self.calIETS = myCalIETSWindow()
        self.calTRS = myCalTRSWindow()
        self.advAGB = myAdvAlgebra()
        self.simCurve = mySimCurve()
        self.plotWin = myPlotWindow()
        self.drawWin = myDrawSpc()
        self.weightedAVG = myWeightedAVG()

        self.simCurve.do_signal.connect(self.do_simCurve)
        self.advAGB.do_signal.connect(self.do_advAGB)
        self.calIETS.send_signal.connect(self.calibrate_IETS)
        self.calTRS.send_signal.connect(self.calibrate_TRS)
        self.passEditor.close_signal.connect(self.update_del_pass)
        self.weightedAVG.close_signal.connect(self.weighted_avg)

        self.parent_data_colors = self.func1D.parent_data_colors
        self.processed_data_colors = self.func1D.processed_data_colors

        """ Controls """
        # signals |
        QApplication.instance().focusObjectChanged.connect(self.focus_changed)
        # pushButton |
        self.pushButton_xScale.clicked.connect(lambda: self.scale(0))
        self.pushButton_yScale.clicked.connect(lambda: self.scale(1))
        self.pushButton_Scanner.clicked.connect(self.show_scanner)
        self.pushButton_All1.clicked.connect(lambda: self.check_all(0))
        self.pushButton_All2.clicked.connect(lambda: self.check_all(1))
        # self.pushButton_Avg.clicked.connect(lambda: self.average_batch(0))
        # self.pushButton_Avg_Individual.clicked.connect(lambda: self.average_batch(1))
        self.pushButton_Saveas.clicked.connect(self.save_as_batch)

        # switchButton |
        self.switchButton_FB = SwitchButton(parent=self, text='Show FB')
        self.switchButton_FB.checkedChanged.connect(self.show_fb_changed)
        self.switchButton_FB.setChecked(True)
        self.switchButton_Pt = SwitchButton(parent=self, text='Hide Pts')
        self.switchButton_Pt.checkedChanged.connect(self.show_pt_changed)
        self.switchButton_Pt.setChecked(False)
        # scrollBar |
        self.scrollBar_ptnum.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.scrollBar_ptnum.valueChanged.connect(self.update_ptnum)
        self.scrollBar_ptnum.setMinimum(1)
        self.scrollBar_ptnum.setMaximum(1)
        # Plot control |
        layout = QGridLayout()
        layout.addWidget(self.label_ptnum, 1, 1)
        layout.addWidget(self.label_num, 1, 2)
        layout.addWidget(self.scrollBar_ptnum, 1, 3)
        layout.addWidget(self.switchButton_Pt, 1, 4)
        layout.addWidget(self.switchButton_FB, 1, 5)
        self.widget_plot.setLayout(layout)
        # listWidget | Plot list
        self.listWidget = DropInList()
        self.listWidget.list_changed_signal.connect(self.pre_treat_list)
        self.listWidget.itemClicked.connect(ft.partial(self.edit_check_state, 0))
        self.listWidget.itemSelectionChanged.connect(self.edit_selection)
        self.listWidget.itemSelectionChanged.connect(self.edit_ptnum)
        self.listWidget.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.listWidget.setContextMenuPolicy(Qt.CustomContextMenu)
        self.listWidget.customContextMenuRequested[QtCore.QPoint].connect(lambda: self.rightMenuShow(0))
        grid = QGridLayout()
        grid.addWidget(self.listWidget, 1, 1)
        self.groupBox.setLayout(grid)

        # listWidget | Processed list
        self.listWidget_Processed.itemClicked.connect(ft.partial(self.edit_check_state, 1))
        # self.listWidget_Processed.itemDoubleClicked.connect(self.rename)
        self.listWidget_Processed.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.listWidget_Processed.setContextMenuPolicy(Qt.CustomContextMenu)
        self.listWidget_Processed.customContextMenuRequested[QtCore.QPoint].connect(lambda: self.rightMenuShow(1))
        # keyBoard event | Delete
        self.shortcut = QShortcut(QKeySequence('Delete'), self)
        self.shortcut.activated.connect(self.edit_delete)

        """ Graphics """
        # label | display scanner coordinates
        self.label = pg.LabelItem(justify='right')
        self.graphicsView.addItem(self.label, row=0, col=0)
        # graphicsView |
        self.plot = self.graphicsView.addPlot(row=1, col=0)
        # self.plot.disableAutoRange()
        # ROI | data scanner
        gray_pen = pg.mkPen((150, 150, 150, 255), width=1)
        self.scanner_vLine = pg.InfiniteLine(angle=90, movable=False, pen=gray_pen)
        self.plot.addItem(self.scanner_vLine, ignoreBounds=True)

        # keyBoard event | Delete
        # self.shortcut = QShortcut(QKeySequence('Delete'), self)
        # self.shortcut.activated.connect(self.edit_delete)

    # switchButton slot | show/hide fb
    def show_fb_changed(self, isChecked: bool):
        self.show_fb = isChecked
        text = 'Show FB' if isChecked else 'Avg FB'
        self.switchButton_FB.setText(text)
        self.refresh_list(0)
        self.refresh_data(0)
        self.update_graph()

    # switchButton slot | show/hide pts
    def show_pt_changed(self, isChecked: bool):
        self.show_pt = isChecked
        text = 'Show Pts' if isChecked else 'Tab Pts'
        self.switchButton_Pt.setText(text)
        self.label_ptnum.setEnabled(not isChecked)
        self.label_num.setEnabled(not isChecked)
        self.scrollBar_ptnum.setEnabled(not isChecked)
        self.refresh_list(0)
        self.refresh_data(0)
        self.update_graph()

    # Graphics | scanner mouse moved signal slot
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
                text += "<span style='font-size: 9pt'><span style='color: " + color[
                    i] + "'>(%0.3e, %0.3e)   </span>" % (data_x[i], data_y[i])
                if num % 3 == 0:
                    text += "<br />"
            self.label.setText(text)

            self.scanner_vLine.setPos(mousePoint.x())

    # Plot List(0) & Processed List(1) | set all items in listWidget checked
    def set_list_checked(self, index):
        if index == 0:
            for row in range(self.listWidget.count()):
                self.listWidget.item(row).setCheckState(2)
        elif index == 1:
            for row in range(self.listWidget_Processed.count()):
                self.listWidget_Processed.item(row).setCheckState(2)
                self.listWidget_Processed.item(row).setFlags(
                    self.listWidget_Processed.item(
                        row).flags() | QtCore.Qt.ItemIsUserCheckable | QtCore.Qt.ItemIsEditable)

    # Plot List(0) & Processed List(1) | check all button slot
    def check_all(self, index):
        # set plots all checked in Plot list
        if index == 0:
            if self.pushButton_All1.isChecked():
                for row in range(self.listWidget.count()):
                    self.listWidget.item(row).setCheckState(2)
            else:
                for row in range(self.listWidget.count()):
                    self.listWidget.item(row).setCheckState(0)

            self.displayed_plot_list = []
            for row in range(self.listWidget.count()):
                if self.listWidget.item(row).checkState() != 0:
                    self.displayed_plot_list.append(self.listWidget.item(row).text())

            self.update_graph()

        # set plots all checked in Processed list
        elif index == 1:
            if self.pushButton_All2.isChecked():
                for row in range(self.listWidget_Processed.count()):
                    self.listWidget_Processed.item(row).setCheckState(2)
            else:
                for row in range(self.listWidget_Processed.count()):
                    self.listWidget_Processed.item(row).setCheckState(0)

            self.displayed_pro_list = []
            for row in range(self.listWidget_Processed.count()):
                if self.listWidget_Processed.item(row).checkState() == 2:
                    self.displayed_pro_list.append(self.listWidget_Processed.item(row).text())
            self.update_graph()

    # Plot List(0) & Processed List(1) | remember check state
    def remember_check_state(self, index):
        # remember check state in Plot list
        if index == 0:
            self.remember_plot_list = {}
            for row in range(self.listWidget.count()):
                self.remember_plot_list[self.listWidget.item(row).text()] = self.listWidget.item(row).checkState()

        # remember check state in Processed list
        elif index == 1:
            self.remember_pro_list = {}
            for row in range(self.listWidget_Processed.count()):
                self.remember_pro_list[self.listWidget_Processed.item(row).text()] = self.listWidget_Processed.item(row).checkState()

    # Plot List(0) & Processed List(1) | recover check state
    def recover_check_state(self, index):
        # recover check state in Plot list
        if index == 0:
            for row in range(self.listWidget.count()):
                if self.listWidget.item(row).text() in self.remember_plot_list.keys():
                    self.listWidget.item(row).setCheckState(self.remember_plot_list[self.listWidget.item(row).text()])

            self.displayed_plot_list = []
            for row in range(self.listWidget.count()):
                if self.listWidget.item(row).checkState() == 2:
                    self.displayed_plot_list.append(self.listWidget.item(row).text())
            self.update_graph()

        # recover check state in Processed list
        elif index == 1:
            for row in range(self.listWidget_Processed.count()):
                if self.listWidget_Processed.item(row).text() in self.remember_pro_list.keys():
                    self.listWidget_Processed.item(row).setCheckState(self.remember_pro_list[self.listWidget_Processed.item(row).text()])

            self.displayed_pro_list = []
            for row in range(self.listWidget_Processed.count()):
                if self.listWidget_Processed.item(row).checkState() == 2:
                    self.displayed_pro_list.append(self.listWidget_Processed.item(row).text())
            self.update_graph()

    # Plot List(0) & Processed List(1) | set check state by logic
    def edit_check_state(self, index, item):
        if index == 0:

            # collect multi-channel file names
            multi_file_names = [plot for plot in self.plot_list if plot[:6] != self.indentor]
            multi_file_left = [0] * len(multi_file_names)

            # count number of multi-channel file data left in current window
            # multi-channel file itself is not included
            for i in range(len(multi_file_names)):
                for plot in self.plot_list:
                    if plot.find(multi_file_names[i]) != -1 and plot.find(self.indentor) != -1:
                        multi_file_left[i] += 1

            if item.text()[:6] == self.indentor:
                child_states = []
                if self.show_pt:
                    if self.show_fb:
                        parent_text = multi_file_names[multi_file_names.index(item.text()[6:24])]
                    else:
                        parent_text = multi_file_names[multi_file_names.index(item.text()[6:28])]
                else:
                    parent_text = multi_file_names[multi_file_names.index(item.text()[6:18])]
                parent_index = self.plot_list.index(parent_text)

                for i in range(multi_file_left[multi_file_names.index(parent_text)]):
                    child_states.append(self.listWidget.item(parent_index + i + 1).checkState())
                if sum(child_states) == 0:  # All Unchecked
                    self.listWidget.item(parent_index).setCheckState(0)
                elif sum(child_states) == 2 * multi_file_left[multi_file_names.index(parent_text)]:  # All Checked
                    self.listWidget.item(parent_index).setCheckState(2)
                else:  # PartiallyChecked
                    self.listWidget.item(parent_index).setCheckState(1)

            elif item.text()[:6] != self.indentor:
                if (item.text() in multi_file_names) and (multi_file_left[multi_file_names.index(item.text())] > 0):
                    parent_index = self.plot_list.index(item.text())
                    if item.checkState() == 0:
                        for i in range(multi_file_left[multi_file_names.index(item.text())]):
                            self.listWidget.item(parent_index + i + 1).setCheckState(0)
                    elif item.checkState() == 2:
                        for i in range(multi_file_left[multi_file_names.index(item.text())]):
                            self.listWidget.item(parent_index + i + 1).setCheckState(2)

            if_all_check = 0
            for row in range(self.listWidget.count()):
                if_all_check += self.listWidget.item(row).checkState()
            if if_all_check == 2 * self.listWidget.count():
                self.pushButton_All1.setChecked(True)
            elif if_all_check == 0:
                self.pushButton_All1.setChecked(False)

            self.displayed_plot_list = []
            for row in range(self.listWidget.count()):
                if self.listWidget.item(row).checkState() != 0:
                    self.displayed_plot_list.append(self.listWidget.item(row).text())

            self.update_graph()

        elif index == 1:
            if_all_check = 0
            for row in range(self.listWidget_Processed.count()):
                if_all_check += self.listWidget_Processed.item(row).checkState()
            if if_all_check == 2 * self.listWidget_Processed.count():
                self.pushButton_All2.setChecked(True)
            elif if_all_check == 0:
                self.pushButton_All2.setChecked(False)

            self.displayed_pro_list = []
            for row in range(self.listWidget_Processed.count()):
                if self.listWidget_Processed.item(row).checkState() == 2:
                    self.displayed_pro_list.append(self.listWidget_Processed.item(row).text())

            self.update_graph()

    # Plot List | set selection by logic
    def edit_selection(self):
        items = self.listWidget.selectedItems()
        for item in items:
            if item.text()[:6] != self.indentor:
                for i in range(len(self.plot_list)):
                    if self.plot_list[i].find(item.text()) != -1:
                        self.listWidget.item(i).setSelected(True)

    # Plot List | set pt num scrollBar by selection
    def edit_ptnum(self):
        if not self.show_pt:
            items = self.listWidget.selectedItems()
            selected_parent = []
            for item in items:
                try:
                    if item.text().find(self.indentor) == -1:
                        selected_parent.append(item.text())
                except:
                    continue
            if len(selected_parent) != 0:
                name = selected_parent[0]
                index = self.parent_data_list.index(name)
                data = SpcData(self.parent_data_paths[index])
                self.scrollBar_ptnum.setMaximum(data.pt_num)
                self.scrollBar_ptnum.setValue(self.current_pt_dict[name]+1)

    def update_ptnum(self, value):
        if hasattr(self, "listWidget"):
            self.label_num.setText(str(value))
            self.current_pt = value - 1
            items = self.listWidget.selectedItems()
            selected_parent = []
            for item in items:
                try:
                    if item.text().find(self.indentor) == -1:
                        selected_parent.append(item.text())
                except:
                    continue
            if len(selected_parent) != 0:
                name = selected_parent[0]
                self.current_pt_dict[name] = self.current_pt

            self.refresh_data(0)
            self.update_graph()

    # Plot List(0) & Processed List(1) | right click menu, 0: Plot list; 1: Processed list
    def rightMenuShow(self, index):
        if index == 0:  # plot list
            rightMenu = QMenu(self.listWidget)
            saveasAction = QAction("Save as", self, triggered=lambda: self.save_as(0))  # parent or child
            deleteAction = QAction("Delete", self, triggered=lambda: self.delete(0))    # parent only
            infoAction = QAction("Info", self, triggered=self.info) # parent only
            editpassAction = QAction("Edit pass", self, triggered=self.edit_pass)   # parent only
            calIETSAction = QAction("Calibrate IETS", self, triggered=self.show_calIETS)    # parent only
            calTRSAction = QAction("Calibrate TRS", self, triggered=self.show_calTRS)   # parent only
            if self.listWidget.currentItem().text()[:6] == self.indentor:
                rightMenu.addAction(saveasAction)
                rightMenu.exec_(QtGui.QCursor.pos())
            else:
                rightMenu.addAction(saveasAction)
                rightMenu.addAction(deleteAction)
                rightMenu.addAction(infoAction)
                rightMenu.addAction(editpassAction)
                rightMenu.addAction(calIETSAction)
                rightMenu.addAction(calTRSAction)
                rightMenu.exec_(QtGui.QCursor.pos())
        elif index == 1:  # processed list
            rightMenu = QMenu(self.listWidget_Processed)
            saveasAction = QAction("Save as", self, triggered=lambda: self.save_as(1))
            renameAction = QAction("Rename", self, triggered=self.rename)
            deleteAction = QAction("Delete", self, triggered=lambda: self.delete(1))
            rightMenu.addAction(saveasAction)
            rightMenu.addAction(renameAction)
            rightMenu.addAction(deleteAction)
            rightMenu.exec_(QtGui.QCursor.pos())

    def get_target_data_basic(self, index):
        pass

    def show_calIETS(self):
        if self.calIETS.isVisible():
            self.calIETS.close()

        item = self.listWidget.currentItem()

        # parent data selected
        if item.text()[:6] != self.indentor:
            data_path = self.parent_data_paths[self.parent_data_list.index(item.text())]
            data = SpcData(data_path)
            parent_name = item.text()
            if not self.show_pt:
                target = data.avg_child_part(self.show_fb, self.del_pass_dict[item.text()])[self.current_pt_dict[item.text()]]
            else:
                pt_num = int(item.text()[item.text().find('Pt#') + 3:]) - 1
                target = data.avg_child_part(self.show_fb, self.del_pass_dict[item.text()[:12]])[pt_num]
            ### target : [(x,ch0), (x,ch1), (x,ch2)]
            ### target : [(x,ch0_fwd), (x,ch1_fwd), (x,ch2_fwd), (x,ch0_bwd), (x,ch1_bwd), (x,ch2_bwd)]
            self.calIETS.init_data(target)

        # child data selected
        else:
            # data = self.data_list[self.plot_list.index(item.text())]    # (2,xxx)
            data_path = self.parent_data_paths[self.parent_data_list.index(item.text())]
            parent_data = SpcData(data_path)
            parent_name = self.get_parent_name(item.text())
            if not self.show_pt:
                parent_index = self.plot_list.index(parent_name)
                ch_index = self.plot_list.index(item.text()) - parent_index - 1
                target_bundle = parent_data.avg_child_part(self.show_fb, self.del_pass_dict[parent_name])[self.current_pt_dict[parent_name]]
            else:
                parent_index = self.plot_list.index(parent_name)
                ch_index = self.plot_list.index(item.text()) - parent_index - 1
                pt_num = int(item.text()[item.text().find('Pt#') + 3: item.text().find('Pt#') + 5]) - 1
                target_bundle = parent_data.avg_child_part(self.show_fb, self.del_pass_dict[parent_name[:12]])[pt_num]
            ### target_bundle: (2, data_num)
            self.calIETS.init_data(target_bundle)

        self.calIETS.init_name(self.get_cal_result_name(1, parent_name))
        # open calibrate IETS window
        self.calIETS.setWindowTitle('Calibrate IETS:   ' + parent_name)
        self.calIETS.show()

    def calibrate_IETS(self, packed_data, result_names):
        ## paccked_data: [(bias, rot_cal_ch1), (bias, rot_cal_ch2)]
        if len(packed_data) == 2:
            pass
        ## paccked_data: [(bias, rot_cal_ch1_fwd), (bias, rot_cal_ch2_fwd), (bias, rot_cal_ch1_bwd), (bias, rot_cal_ch2_bwd)]
        elif len(packed_data) == 4:
            pass
        print('get calibration results!')
        self.processed_data += packed_data
        self.listWidget_Processed.addItems(result_names)
        self.refresh_list(1)

    def show_calTRS(self):
        if self.calTRS.isVisible():
            self.calTRS.close()

        item = self.listWidget.currentItem()

        # parent data selected
        if item.text()[:6] != self.indentor:
            data_path = self.parent_data_paths[self.parent_data_list.index(item.text())]
            data = SpcData(data_path)
            parent_name = item.text()
            if not self.show_pt:
                target = data.avg_child_part(self.show_fb, self.del_pass_dict[item.text()])[
                    self.current_pt_dict[item.text()]]
            else:
                pt_num = int(item.text()[item.text().find('Pt#') + 3:]) - 1
                target = data.avg_child_part(self.show_fb, self.del_pass_dict[item.text()[:12]])[pt_num]
            ### target : [(x,ch0), (x,ch1), (x,ch2)]
            ### target : [(x,ch0_fwd), (x,ch1_fwd), (x,ch2_fwd), (x,ch0_bwd), (x,ch1_bwd), (x,ch2_bwd)]
            self.calTRS.init_data(target)

        # child data selected
        else:
            # data = self.data_list[self.plot_list.index(item.text())]    # (2,xxx)
            data_path = self.parent_data_paths[self.parent_data_list.index(item.text())]
            parent_data = SpcData(data_path)
            parent_name = self.get_parent_name(item.text())
            if not self.show_pt:
                parent_index = self.plot_list.index(parent_name)
                ch_index = self.plot_list.index(item.text()) - parent_index - 1
                target_bundle = parent_data.avg_child_part(self.show_fb, self.del_pass_dict[parent_name])[
                    self.current_pt_dict[parent_name]]
            else:
                parent_index = self.plot_list.index(parent_name)
                ch_index = self.plot_list.index(item.text()) - parent_index - 1
                pt_num = int(item.text()[item.text().find('Pt#') + 3: item.text().find('Pt#') + 5]) - 1
                target_bundle = parent_data.avg_child_part(self.show_fb, self.del_pass_dict[parent_name[:12]])[pt_num]
            self.calTRS.init_data(target_bundle)

        self.calTRS.init_name(self.get_cal_result_name(0, parent_name))
        # open calibrate TRS window
        self.calTRS.setWindowTitle('Calibrate TRS:   ' + parent_name)
        self.calTRS.show()

    def calibrate_TRS(self, packed_data, result_names):
        ## paccked_data: [(bias, rot_cal_ch1), (bias, rot_cal_ch2)]
        if len(packed_data) == 2:
            pass
        ## paccked_data: [(bias, rot_cal_ch1_fwd), (bias, rot_cal_ch2_fwd), (bias, rot_cal_ch1_bwd), (bias, rot_cal_ch2_bwd)]
        elif len(packed_data) == 4:
            pass
        print('get calibration results!')
        self.processed_data += packed_data
        self.listWidget_Processed.addItems(result_names)
        self.refresh_list(1)

    def reform_data2save(self, target):
        ### target : [(x,ch0), (x,ch1), (x,ch2)]
        if len(target) == 3:
            x = target[0][0]
            ch0 = target[0][1]
            ch1 = target[1][1]
            ch2 = target[2][1]
            data2save = np.vstack((x, ch0))
            data2save = np.vstack((data2save, ch1))
            data2save = np.vstack((data2save, ch2))
            print('data2save:', data2save.shape)

        ### target : [(x,ch0_fwd), (x,ch1_fwd), (x,ch2_fwd), (x,ch0_bwd), (x,ch1_bwd), (x,ch2_bwd)]
        elif len(target) == 6:
            x = target[0][0]
            ch0_fwd = target[0][1]
            ch1_fwd = target[1][1]
            ch2_fwd = target[2][1]
            ch0_bwd = target[3][1]
            ch1_bwd = target[4][1]
            ch2_bwd = target[5][1]
            data2save = np.vstack((x, ch0_fwd))
            data2save = np.vstack((data2save, ch1_fwd))
            data2save = np.vstack((data2save, ch2_fwd))
            data2save = np.vstack((data2save, ch0_bwd))
            data2save = np.vstack((data2save, ch1_bwd))
            data2save = np.vstack((data2save, ch2_bwd))
            print('data2save:', data2save.shape)

        ### target : [(x,ch)]
        elif len(target) == 1:
            data2save = target[0]

        return data2save

    # get default file name when save requested
    def get_save_name(self, path, name):
        for root, dirs, files in os.walk(path, topdown=False):
            exist_num = 0
            for file in files:
                if file.find(name) != -1:
                    exist_num += 1
        return name+'-'+str(exist_num).zfill(3)

    def get_cal_result_name(self, mode, parent_name):
        # parent_name: xxxxxx.spc_Pt#01  or xxxxxx.spc

        if mode == 0:   # calibrate TRS
            if self.show_fb:
                result_names = ['rot-cal-ch1fwd-'+ parent_name, 'rot-cal-ch2fwd-'+ parent_name,
                         'rot-cal-ch1bwd-'+ parent_name, 'rot-cal-ch2bwd-'+ parent_name]
            else:
                result_names = ['rot-cal-ch1-' + parent_name, 'rot-cal-ch2-' + parent_name]

        elif mode == 1: # calibrate IETS
            if self.show_fb:
                result_names = ['cal-int-ch1fwd-'+ parent_name, 'cal-int-ch2fwd-'+ parent_name,
                         'cal-int-ch1bwd-'+ parent_name, 'cal-int-ch2bwd-'+ parent_name]
            else:
                result_names = ['cal-int-ch1-' + parent_name, 'cal-int-ch2-' + parent_name]

        return result_names

    # get parent name from a child name
    def get_parent_name(self, name):
        print('raw name:', name)
        if not self.show_pt:
            print('parent name:', name[6:18])
            return name[6:18]
        else:
            if self.show_fb:
                print('parent name:', name[6:24])
                return name[6:24]

            else:
                print('parent name:', name[6:28])
                return name[6:28]

    # Plot List(0) & Processed List(1) | save as action slot
    def save_as(self, index):

        if index == 0:  # Plot list
            item = self.listWidget.currentItem()

            # parent data selected
            if item.text()[:6] != self.indentor:
                data_path = self.parent_data_paths[self.parent_data_list.index(item.text())]
                data = SpcData(data_path)
                parent_name = item.text()
                if not self.show_pt:
                    target = data.avg_child_part(self.show_fb, self.del_pass_dict[item.text()])[
                        self.current_pt_dict[item.text()]]
                    ### target : [(x,ch0), (x,ch1), (x,ch2)]
                else:
                    pt_num = int(item.text()[item.text().find('Pt#') + 3:]) - 1
                    target = data.avg_child_part(self.show_fb, self.del_pass_dict[item.text()[:12]])[pt_num]
                    ### target : [(x,ch0_fwd), (x,ch1_fwd), (x,ch2_fwd), (x,ch0_bwd), (x,ch1_bwd), (x,ch2_bwd)]
                data2save = self.reform_data2save(target)
                name = self.get_save_name(data.dir, data.name[:-4])
                default_name = os.path.join(data.dir, name)

            # child data selected
            else:
                # data = self.data_list[self.plot_list.index(item.text())]    # (2,xxx)
                data_path = self.parent_data_paths[self.parent_data_list.index(item.text())]
                parent_data = SpcData(data_path)
                parent_name = self.get_parent_name(item.text())
                if not self.show_pt:
                    parent_index = self.plot_list.index(parent_name)
                    ch_index = self.plot_list.index(item.text()) - parent_index - 1
                    ch_name = self.get_ch_name(parent_name, ch_index)
                    target = parent_data.avg_child_part(self.show_fb, self.del_pass_dict[parent_name[:12]])[
                        self.current_pt_dict[parent_name]][ch_index]
                else:
                    parent_index = self.plot_list.index(parent_name)
                    ch_index = self.plot_list.index(item.text()) - parent_index - 1
                    ch_name = self.get_ch_name(parent_name, ch_index)
                    pt_num = int(item.text()[item.text().find('Pt#') + 3: item.text().find('Pt#') + 5]) - 1
                    target = parent_data.avg_child_part(self.show_fb, self.del_pass_dict[parent_name[:12]])[
                        pt_num][ch_index]
                    ### target: (2, data_num)
                data2save = self.reform_data2save([target])
                name = self.get_save_name(parent_data.dir, parent_name.replace('.spc', ''))
                default_name = os.path.join(parent_data.dir, name)

            # save data
            fileName, ok = QFileDialog.getSaveFileName(self, "Save", default_name, "TXT(*.txt)")
            self.func1D.save_txt(fileName, data2save)

        elif index == 1:  # Processed list
            file_name = self.listWidget_Processed.currentItem().text()
            data2save = self.processed_data[self.processed_list.index(file_name)]
            dir, file = os.path.split(self.parent_data_paths[0])
            default_name = self.get_save_name(dir, file_name).replace('.spc', '')
            fileName, ok = QFileDialog.getSaveFileName(self, "Save", default_name, "TXT(*.txt)")
            self.func1D.save_txt(fileName, data2save)

    # Processed List| save as all checked slot
    def save_as_batch(self):
        dir_path = os.path.split(self.parent_data_paths[0])[0]
        path = QFileDialog.getExistingDirectory(self, "Select folder", dir_path, QFileDialog.ShowDirsOnly) + '/'
        for file_name in self.displayed_pro_list:
            data2save = self.processed_data[self.processed_list.index(file_name)]
            dir, file = os.path.split(self.parent_data_paths[0])
            default_name = self.get_save_name(dir, file_name).replace('.spc', '')
            print(path)
            self.func1D.save_txt(path+default_name+'.dat', data2save)

    # delete keyboard event slot, to figure out target list
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
                if item.text()[:6] != self.indentor:
                    for plot in self.plot_list:
                        if plot.find(item.text()) != -1:
                            delete_items.append(plot)
                elif item.text()[:6] == self.indentor:
                    continue

                # delete from listWidget
                for i in range(len(self.plot_list) - 1, -1, -1):
                    if self.plot_list[i] in delete_items:
                        self.plot_list.pop(i)

            for item in delete_items:
                try:
                    del self.del_pass_dict[item]
                except:
                    continue
            self.remember_check_state(0)
            self.listWidget.clear()
            self.listWidget.addItems(self.plot_list)
            self.set_list_checked(0)
            self.refresh_list(0)
            self.refresh_data(0)
            self.recover_check_state(0)

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

            # do not call refresh_list(1) here, it's special case
            # lines below do similar things to refresh_list(1) in slightly different order
            # refresh_list(1) will mess check state up
            self.remember_check_state(1)
            self.listWidget_Processed.clear()
            self.listWidget_Processed.addItems(self.processed_list)
            self.set_list_checked(1)
            self.recover_check_state(1)
            for row in range(self.listWidget_Processed.count()):
                if self.listWidget_Processed.item(row).checkState() == 2:
                    self.displayed_pro_list.append(self.listWidget_Processed.item(row).text())
            self.update_graph()

    # Plot List | info action slot
    def info(self):
        data_path = self.parent_data_paths[self.parent_data_list.index(self.listWidget.currentItem().text())]
        with open(data_path, 'rb') as input:
            spc = pickle.load(input)
        self.spcInfo.init_spcInfo(spc)
        self.spcInfo.show()

    def edit_pass(self):
        index = self.parent_data_list.index(self.listWidget.currentItem().text())
        data_path = self.parent_data_paths[index]
        data = SpcData(data_path)
        if data.every:
            self.passEditor.init_list(data)
            self.passEditor.show()
        else:
            self.showDialog('No single pass data available!')

    # Processed List | rename action slot
    def rename(self):
        item = self.listWidget_Processed.currentItem()
        text, okPressed = QInputDialog.getText(self, "New name", "New name:", text=item.text())
        if okPressed and text != '':
            item.setText(text)

        # self.remember_check_state(1)
        # self.set_list_checked(1)
        self.refresh_list(1)
        # self.recover_check_state(1)

    def showDialog(self, content):
        w = MessageDialog('Warning', content, self)
        w.exec()

    # focus object changed
    def focus_changed(self, obj):
        if obj != None:
            if obj == self.listWidget or obj == self.listWidget_Processed:
                self.current_list = obj

    # Plot list | drop items signal slot
    def pre_treat_list(self):
        # deal with multi-channel data
        for row in range(self.listWidget.count()):
            for data in self.parent_data_list:
                if data.find(self.listWidget.item(row).text()) != -1:
                    self.listWidget.addItem(data)
        self.refresh_list(0)
        self.refresh_list(2)
        self.refresh_data(0)
        self.update_graph()

    # Plot List(0) & Processed List(1) |
    def refresh_list(self, index):

        if index == 0:  # Plot list
            # get current plot list from listWidget
            self.plot_list = []

            for row in range(self.listWidget.count()):
                if self.listWidget.item(row).text().find('.spc') != -1 and self.listWidget.item(row).text().find(self.indentor) == -1:
                    name = self.listWidget.item(row).text()[:12]    # Avoid point num name_Pt#xxx
                    data_path = self.parent_data_paths[self.parent_data_list.index(name)]
                    data = SpcData(data_path)

                    if self.show_fb:
                        if not self.show_pt:
                            self.plot_list.append(name)
                            self.plot_list += data.ch_names
                        else:
                            self.plot_list += data.pt_ch_names
                    else:
                        if not self.show_pt:
                            self.plot_list.append(name)
                            self.plot_list += data.ch_names_folded
                        else:
                            self.plot_list += data.pt_ch_names_folded

            # remove repeated items
            self.plot_list = list(set(self.plot_list))
            # sort plot list
            # print('-->', '      11111111.spc_avg_Pt#01_I_avgfb' in self.parent_data_list)
            # print('      1105220c.spc_Pt#01_X2_fwd' in self.parent_data_list)
            print(self.parent_data_list, sep='\n')
            self.plot_list = sorted(self.plot_list, key=self.parent_data_list.index)

            # add items to listWidget
            self.listWidget.clear()
            self.listWidget.addItems(self.plot_list)
            # set color
            # for row in range(self.listWidget.count()):
            #     # count child
            #     is_multi = 0
            #     for name in self.parent_data_list:
            #         if name.find(self.listWidget.item(row).text() + '_pass') != -1:
            #             is_multi += 1
            #     # multi-channel file has white background, others are colorful
            #     if self.listWidget.item(row).text()[-4:] == '.spc' and is_multi > 0:
            #         self.listWidget.item(row).setForeground(QColor('black'))
            #         # self.listWidget.item(row).setBackground(QColor('aliceblue'))
            #     else:
            #         color = self.parent_data_colors[self.parent_data_list.index(self.listWidget.item(row).text())]
            #         self.listWidget.item(row).setForeground(color)
            #         # self.listWidget.item(row).setBackground(QColor('aliceblue'))
            self.set_list_checked(0)
            self.listWidget.setCurrentRow(-1)
            self.displayed_plot_list.clear()
            self.displayed_plot_list = copy.deepcopy(self.plot_list)


        elif index == 1:  # Processed list
            self.remember_check_state(1)

            self.processed_list = []
            for row in range(self.listWidget_Processed.count()):
                self.processed_list.append(self.listWidget_Processed.item(row).text())
            self.listWidget_Processed.clear()
            self.listWidget_Processed.addItems(self.processed_list)
            # # set color
            # for row in range(self.listWidget_Processed.count()):
            #     color = self.processed_data_colors[
            #         self.processed_list.index(self.listWidget_Processed.item(row).text())]
            #     self.listWidget_Processed.item(row).setForeground(color)

            self.set_list_checked(1)
            self.recover_check_state(1)
            self.displayed_pro_list = []
            for row in range(self.listWidget_Processed.count()):
                if self.listWidget_Processed.item(row).checkState() == 2:
                    self.displayed_pro_list.append(self.listWidget_Processed.item(row).text())

            self.update_graph()

        # just to get keys of del_pass_dict and current_pt_dict
        # should only be called when data is added or deleted
        elif index == 2:
            parent_data_list = []
            for plot in self.plot_list:
                if plot.find('.spc') != -1 and plot.find(self.indentor) == -1:
                    if self.show_pt:
                        parent_data_list.append(plot[:-6])
                    else:
                        parent_data_list.append(plot)
            self.del_pass_dict = dict.fromkeys(parent_data_list)
            self.current_pt_dict = dict.fromkeys(parent_data_list, 0)

    # refresh data_list for plot
    # called whenever plot_list is changed
    def refresh_data(self, index):
        if index == 0:

            self.data_list = []

            for plot in self.plot_list:
                if plot.find('.spc') != -1 and plot.find(self.indentor) == -1:
                    self.data_list.append(None)
                    index = self.parent_data_list.index(plot)
                    data = SpcData(self.parent_data_paths[index])

                    if not self.show_pt:
                        for ch in data.avg_child_part(self.show_fb, self.del_pass_dict[plot])[self.current_pt_dict[plot]]:
                            self.data_list.append(ch)
                    else:
                        pt_num = int(plot[plot.find('Pt#')+3:])-1
                        print(self.del_pass_dict, plot[:12])
                        for ch in data.avg_child_part(self.show_fb, self.del_pass_dict[plot[:12]])[pt_num]:
                            self.data_list.append(ch)

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
            self.plot.addItem(self.scanner_vLine, ignoreBounds=True)
            self.proxy = pg.SignalProxy(self.plot.scene().sigMouseMoved, rateLimit=60, slot=self.mouseMoved)
            self.label.show()
        else:
            self.plot.removeItem(self.scanner_vLine)
            # self.plot.scene().sigMouseMoved.disconnect(self.mouseMoved)
            self.label.hide()

    # passEditor close signal slot | update multi-pass data with selected passes
    def update_del_pass(self, name, del_pass_list):
        self.del_pass_dict[name] = del_pass_list
        print('deleted passes:', del_pass_list)
        self.refresh_data(0)
        self.update_graph()

    # Graphics | update plot in current window
    def update_graph(self):

        self.plot.clear()
        self.lines = []
        for i, name in enumerate(self.displayed_plot_list):
            if name.find('.spc') != -1 and name.find(self.indentor) != -1:
                index = self.plot_list.index(name)
                data = self.data_list[index]
                pen = pg.mkPen(self.parent_data_colors[index], width=2)
                # cc.glasbey_light[random.randint(0, 255)]
                self.lines.append(
                        self.plot.plot(x=data[0], y=data[1], pen=pen))

        for i, name in enumerate(self.displayed_pro_list):
            ind = self.processed_list.index(name)
            data = self.processed_data[ind]
            pen = pg.mkPen(self.processed_data_colors[ind], width=2)
            # cc.glasbey_light[random.randint(0, 255)]
            self.lines.append(self.plot.plot(x=data[0], y=data[1], pen=pen))

    # Processing | get all checked plot
    def get_target_plot(self):
        self.target_plot_list = []
        for row in range(self.listWidget.count()):
            if self.listWidget.item(row).checkState() == 2 and self.listWidget.item(row).text()[:6] == self.indentor:
                self.target_plot_list.append(self.listWidget.item(row).text())

        self.target_pro_list = []
        for row in range(self.listWidget_Processed.count()):
            if self.listWidget_Processed.item(row).checkState() == 2:
                self.target_pro_list.append(self.listWidget_Processed.item(row).text())

        self.target_data = []
        for plot in self.target_plot_list:
            ind = self.plot_list.index(plot)
            data = copy.deepcopy(self.data_list[ind])
            self.target_data.append(data)

        for pro in self.target_pro_list:
            ind = self.processed_list.index(pro)
            data = copy.deepcopy(self.processed_data[ind])
            self.target_data.append(data)

    # Processing | get all selected plot
    def get_target_line(self):
        self.target_line = []
        self.target_line_name = []

        plot_items = self.listWidget.selectedItems()
        for plot in plot_items:
            if plot.text()[:6] == self.indentor:
                ind = self.plot_list.index(plot.text())
                data = copy.deepcopy(self.data_list[ind])
                self.target_line.append(data)
                self.target_line_name.append(plot.text())

        pro_items = self.listWidget_Processed.selectedItems()
        for pro in pro_items:
            ind = self.processed_list.index(pro.text())
            data = copy.deepcopy(self.processed_data[ind])
            self.target_line.append(data)
            self.target_line_name.append(pro.text())

    def weighted_avg(self, name_list, result_list):

        # append result data list
        for data in result_list:
            self.processed_data.append(data)

        # append result name list
        for i in range(len(name_list)):
            max_index_list = []
            for row in range(self.listWidget_Processed.count()):
                if self.listWidget_Processed.item(row).text().find('wAVG') != -1:
                    if self.listWidget_Processed.item(row).text()[-2] == '_':
                        max_index_list.append(int(self.listWidget_Processed.item(row).text()[-1]))
                    else:
                        max_index_list.append(int(self.listWidget_Processed.item(row).text()[-2:]))
            max_index = np.max(max_index_list) if len(max_index_list) > 0 else 0
            self.listWidget_Processed.addItem(name_list[i] + '_' + str(max_index + 1))

        self.refresh_list(1)

    # Processing | Algebra (0: Plus; 1: Multiply; 2: Log; 3: Exp;
    # 4: Norm(AVG); 5: Norm(1PT); 6: Multiply(x axis); 7: Plus(x axis))
    def algebra(self, mode, val):
        self.get_target_plot()

        for plot in self.target_data:
            if mode == 0:
                plot[1] = plot[1] + val
            elif mode == 1:
                plot[1] = plot[1] * val
            elif mode == 2:
                for i in range(len(plot[1])):
                    plot[1][i] = val * math.log(plot[1][i])
            elif mode == 3:
                for i in range(len(plot[1])):
                    plot[1][i] = val * math.exp(plot[1][i])
            elif mode == 4:
                avg = plot[1].mean()
                for i in range(len(plot[1])):
                    plot[1][i] = plot[1][i] / avg
            elif mode == 5:
                first = plot[1][0]
                for i in range(len(plot[1])):
                    plot[1][i] = plot[1][i] / first
            elif mode == 6:
                plot[0] = plot[0] * val
            elif mode == 7:
                plot[0] = plot[0] + val

            self.processed_data.append(plot)

        for i in range(len(self.target_data)):
            max_index_list = []
            for row in range(self.listWidget_Processed.count()):
                if self.listWidget_Processed.item(row).text().find('algebra') != -1:
                    if self.listWidget_Processed.item(row).text()[-2] == '_':
                        max_index_list.append(int(self.listWidget_Processed.item(row).text()[-1]))
                    else:
                        max_index_list.append(int(self.listWidget_Processed.item(row).text()[-2:]))
            max_index = np.max(max_index_list) if len(max_index_list) > 0 else 0
            self.listWidget_Processed.addItem('algebra_' + str(max_index + 1))

        self.refresh_list(1)

    # Processing | show Advanced algebra window
    def show_advAGB(self):
        self.get_target_line()
        if len(self.target_line) < 1 or len(self.target_line) > 4:
            QMessageBox.warning(None, "Select lines", 'Please select 1~4 lines!', QMessageBox.Ok)
            return
        else:
            length = self.target_line[0].shape[1]
            for line in self.target_line:
                if length != line.shape[1]:
                    QMessageBox.warning(None, "Select lines", 'Selected lines are different in shape!', QMessageBox.Ok)
                    return

            text = ''
            for i in range(len(self.target_line_name)):
                text += 'x_' + str(i) + ':' + self.target_line_name[i] + '\n'
            self.advAGB.label_lines.setText(text)
            self.advAGB.show()

    # Processing | Advanced algebra
    def do_advAGB(self):
        x = self.target_line[0][0]
        expr = self.advAGB.lineEdit_adv.text()
        x_0, x_1, x_2, x_3 = symbols('x_0 x_1 x_2 x_3')
        num = len(self.target_line)
        if num == 1:
            f = lambdify([x_0], expr, 'numpy')
            line = f(self.target_line[0][1])
        elif num == 2:
            f = lambdify([x_0, x_1], expr, 'numpy')
            line = f(self.target_line[0][1], self.target_line[1][1])
        elif num == 3:
            f = lambdify([x_0, x_1, x_2], expr, 'numpy')
            line = f(self.target_line[0][1], self.target_line[1][1], self.target_line[2][1])
        elif num == 4:
            f = lambdify([x_0, x_1, x_2, x_3], expr, 'numpy')
            line = f(self.target_line[0][1], self.target_line[1][1], self.target_line[2][1], self.target_line[3][1])
        self.processed_data.append(np.vstack((x, line)))

        max_index_list = []
        for row in range(self.listWidget_Processed.count()):
            if self.listWidget_Processed.item(row).text().find('adv_algebra') != -1:
                if self.listWidget_Processed.item(row).text()[-2] == '_':
                    max_index_list.append(int(self.listWidget_Processed.item(row).text()[-1]))
                else:
                    max_index_list.append(int(self.listWidget_Processed.item(row).text()[-2:]))
        max_index = np.max(max_index_list) if len(max_index_list) > 0 else 0
        self.listWidget_Processed.addItem('adv_algebra_' + str(max_index + 1))
        self.refresh_list(1)

    # Processing | show Sim curve window
    def show_simCurve(self):
        self.simCurve.show()

    # Processing | Sim curve
    def do_simCurve(self):
        if self.simCurve.lineEdit_expr_SC.text() != '':
            expr = self.simCurve.lineEdit_expr_SC.text()
        else:
            QMessageBox.warning(None, "Sim_curve", "You haven't completed it yet.\n\
            All the parameters must be defined.", QMessageBox.Ok)
            return
        if self.simCurve.lineEdit_xmin_SC.text() != '':
            xmin = float(self.simCurve.lineEdit_xmin_SC.text())
        else:
            QMessageBox.warning(None, "Sim_curve", "You haven't completed it yet.\n\
            All the parameters must be defined.", QMessageBox.Ok)
            return
        if self.simCurve.lineEdit_xmax_SC.text() != '':
            xmax = float(self.simCurve.lineEdit_xmax_SC.text())
        else:
            QMessageBox.warning(None, "Sim_curve", "You haven't completed it yet.\n\
            All the parameters must be defined.", QMessageBox.Ok)
            return
        if self.simCurve.lineEdit_pt_SC.text() != '':
            point = int(self.simCurve.lineEdit_pt_SC.text())
        else:
            QMessageBox.warning(None, "Sim_curve", "You haven't completed it yet.\n\
            All the parameters must be defined.", QMessageBox.Ok)
            return
        if self.simCurve.lineEdit_para_SC.text() != '':
            param_num = int(self.simCurve.lineEdit_para_SC.text())
        else:
            QMessageBox.warning(None, "Sim_curve", "You haven't completed it yet.\n\
            All the parameters must be defined.", QMessageBox.Ok)
            return
        if self.simCurve.lineEdit_a_SC.text() != '':
            param_a = float(self.simCurve.lineEdit_a_SC.text())
        else:
            QMessageBox.warning(None, "Sim_curve", "You haven't completed it yet.\n\
            All the parameters must be defined.", QMessageBox.Ok)
            return
        if self.simCurve.lineEdit_b_SC.text() != '':
            param_b = float(self.simCurve.lineEdit_b_SC.text())
        else:
            QMessageBox.warning(None, "Sim_curve", "You haven't completed it yet.\n\
            All the parameters must be defined.", QMessageBox.Ok)
            return
        if self.simCurve.lineEdit_c_SC.text() != '':
            param_c = float(self.simCurve.lineEdit_c_SC.text())
        else:
            QMessageBox.warning(None, "Sim_curve", "You haven't completed it yet.\n\
            All the parameters must be defined.", QMessageBox.Ok)
            return
        if self.simCurve.lineEdit_d_SC.text() != '':
            param_d = float(self.simCurve.lineEdit_d_SC.text())
        else:
            QMessageBox.warning(None, "Sim_curve", "You haven't completed it yet.\n\
            All the parameters must be defined.", QMessageBox.Ok)
            return

        data = np.linspace(xmin, xmax, point)
        if param_num == 0:
            x = symbols('x')
            f = lambdify(x, expr, 'numpy')
            line = f(data)
        elif param_num == 1:
            x, a = symbols('x a')
            f = lambdify([x, a], expr, 'numpy')
            line = f(data, param_a)
        elif param_num == 2:
            x, a, b = symbols('x a b')
            f = lambdify([x, a, b], expr, 'numpy')
            line = f(data, param_a, param_b)
        elif param_num == 3:
            x, a, b, c = symbols('x a b c')
            f = lambdify([x, a, b, c], expr, 'numpy')
            line = f(data, param_a, param_b, param_c)
        elif param_num == 4:
            x, a, b, c, d = symbols('x a b c d')
            f = lambdify([x, a, b, c, d], expr, 'numpy')
            line = f(data, param_a, param_b, param_c, param_d)

        self.processed_data.append(np.vstack((data, line)))

        max_index_list = []
        for row in range(self.listWidget_Processed.count()):
            if self.listWidget_Processed.item(row).text().find('sim_curve') != -1:
                if self.listWidget_Processed.item(row).text()[-2] == '_':
                    max_index_list.append(int(self.listWidget_Processed.item(row).text()[-1]))
                else:
                    max_index_list.append(int(self.listWidget_Processed.item(row).text()[-2:]))
        max_index = np.max(max_index_list) if len(max_index_list) > 0 else 0
        self.listWidget_Processed.addItem('sim_curve_' + str(max_index + 1))
        self.refresh_list(1)

    # Processing | FFT / IFFT
    def fft(self, index):
        self.get_target_plot()
        if index == 0:
            for plot in self.target_data:
                x = plot[0]
                y = plot[1]
                plot = [x] + [y]
                # tmp = [np.abs(np.fft.fftshift(np.fft.fft(plot[1])))]
                # plot[1] = tmp[0]
                freq = np.fft.fftshift(np.fft.fftfreq(x.shape[-1]))
                amp = np.abs(np.fft.fftshift(np.fft.fft(plot[1])))
                plot = np.vstack((freq, amp))
                self.processed_data.append(plot)

            for i in range(len(self.target_data)):
                max_index_list = []
                for row in range(self.listWidget_Processed.count()):
                    if self.listWidget_Processed.item(row).text().find('fft') != -1:
                        if self.listWidget_Processed.item(row).text()[-2] == '_':
                            max_index_list.append(int(self.listWidget_Processed.item(row).text()[-1]))
                        else:
                            max_index_list.append(int(self.listWidget_Processed.item(row).text()[-2:]))
                max_index = np.max(max_index_list) if len(max_index_list) > 0 else 0
                self.listWidget_Processed.addItem('fft_' + str(max_index + 1))

        elif index == 1:
            for plot in self.target_data:
                x = plot[0]
                y = plot[1]
                plot = [x] + [y]
                tmp = [np.fft.ifft(np.fft.ifftshift(plot[1]))]
                plot[1] = tmp[0].real
                self.processed_data.append(plot)

            for i in range(len(self.target_data)):
                max_index_list = []
                for row in range(self.listWidget_Processed.count()):
                    if self.listWidget_Processed.item(row).text().find('ifft') != -1:
                        if self.listWidget_Processed.item(row).text()[-2] == '_':
                            max_index_list.append(int(self.listWidget_Processed.item(row).text()[-1]))
                        else:
                            max_index_list.append(int(self.listWidget_Processed.item(row).text()[-2:]))
                max_index = np.max(max_index_list) if len(max_index_list) > 0 else 0
                self.listWidget_Processed.addItem('ifft_' + str(max_index + 1))

        self.refresh_list(1)

    # Processing | Filter
    def filter(self, method, lfreq, hfreq):
        self.get_target_plot()

        if method == 0:     # dy/dx
            for plot in self.target_data:
                tmp = np.gradient(plot[1])
                plot[1] = tmp
                self.processed_data.append(plot)
        elif method == 1:   # d2y/dx2
            for plot in self.target_data:
                tmp = np.gradient(plot[1])
                plot[1] = np.gradient(tmp)
                self.processed_data.append(plot)
        elif method == 2:   # cut off
            for plot in self.target_data:
                # re1 = int(len(plot[1]) * lfreq)
                # re2 = int(len(plot[1]) * hfreq)
                # for i in plot[1][re1-1:len(plot[1])-re2]:
                #     plot[1][plot[1].tolist().index(i)] = 0
                #     plot[1] = np.array(plot[1])
                """ band pass """
                b, a = scipy.signal.butter(3, [lfreq, hfreq], 'band')
                plot[1] = scipy.signal.lfilter(b, a, plot[1])
                """ adv band pass """
                # segment = plot[1][np.argpartition(abs(plot[1]), -plot[1].shape[0]//10)[-plot[1].shape[0]//10:]]
                # plot[1] = scipy.signal.filtfilt(b, a, segment, method="gust")
                """ lo and hi pass """
                # b, a = scipy.signal.butter(3, lfreq, 'lowpass')
                # plot[1] = scipy.signal.filtfilt(b, a, plot[1])
                # b, a = scipy.signal.butter(3, hfreq, 'highpass')
                # plot[1] = scipy.signal.filtfilt(b, a, plot[1])

                self.processed_data.append(plot)

        for i in range(len(self.target_data)):
            max_index_list = []
            for row in range(self.listWidget_Processed.count()):
                if self.listWidget_Processed.item(row).text().find('filter') != -1:
                    if self.listWidget_Processed.item(row).text()[-2] == '_':
                        max_index_list.append(int(self.listWidget_Processed.item(row).text()[-1]))
                    else:
                        max_index_list.append(int(self.listWidget_Processed.item(row).text()[-2:]))
            max_index = np.max(max_index_list) if len(max_index_list) > 0 else 0
            self.listWidget_Processed.addItem('filter_' + str(max_index + 1))

        self.refresh_list(1)

    # Processing | Smooth
    def smooth(self, method, factor):
        self.get_target_plot()
        for plot in self.target_data:
            if method == 'movmean':
                plot[1] = self.func1D.smoothdata_movmean(plot[1], factor)
            elif method == 'movmedian':
                plot[1] = self.func1D.smoothdata_movmedian(plot[1], factor)
            elif method == 'gaussian':
                plot[1] = self.func1D.smoothdata_gaussian(plot[1], factor)
            elif method == 'sgolay':
                plot[1] = self.func1D.smoothdata_sgolay(plot[1], factor)
            self.processed_data.append(plot)

        for i in range(len(self.target_data)):
            max_index_list = []
            for row in range(self.listWidget_Processed.count()):
                if self.listWidget_Processed.item(row).text().find('smooth') != -1:
                    if self.listWidget_Processed.item(row).text()[-2] == '_':
                        max_index_list.append(int(self.listWidget_Processed.item(row).text()[-1]))
                    else:
                        max_index_list.append(int(self.listWidget_Processed.item(row).text()[-2:]))
            max_index = np.max(max_index_list) if len(max_index_list) > 0 else 0
            self.listWidget_Processed.addItem('smooth_' + str(max_index + 1))

        self.refresh_list(1)

    def norm3Ddata(self, data3D):
        for data in data3D:
            first = data[0]
            for i in range(len(data)):
                data[i] = data[i] / first
        return data3D

    # Processing | Plot 2D/3D
    def plot2D3D(self):
        self.get_target_plot()
        target_y = []
        target_x = self.target_data[0][0]

        for plot in self.target_data:
            target_y.append(plot[1])
        col = self.target_data[0].shape[1]
        row = len(self.target_data)
        target_y = self.norm3Ddata(copy.deepcopy(target_y))
        data3D = np.array(target_y).reshape(row, col)

        self.plotWin.init_data(target_x, data3D)
        self.plotWin.iniFigure()
        self.plotWin.on_combo3D_type_currentIndexChanged(0)
        self.plotWin.on_combo2D_color_currentIndexChanged(0)
        self.plotWin.show()

    # Processing | Plot 2D/3D
    def draw2D3D(self):
        self.get_target_plot()
        target_y = []
        target_x = []
        for plot in self.target_data:
            target_x.append(plot[0])
            target_y.append(plot[1])
        names = self.target_plot_list + self.target_pro_list

        col = self.target_data[0].shape[1]
        row = len(self.target_data)
        ys = self.norm3Ddata(copy.deepcopy(target_y))
        data3D = np.array(ys).reshape(row, col)

        self.drawWin.init_data(target_x, target_y, names, data3D)
        self.drawWin.update_graph()
        self.drawWin.update_graph_2D()
        self.drawWin.update_graph_3D()
        self.drawWin.show()
        self.drawWin.raise_()



if __name__ == "__main__":
    app = QApplication(sys.argv)
    # names = ['1104220b.spc', '      1104220b.spc_I_fwd', '      1104220b.spc_X1_fwd', '      1104220b.spc_X2_fwd', '      1104220b.spc_I_bwd', '      1104220b.spc_X1_bwd', '      1104220b.spc_X2_bwd', '      1104220b.spc_I_avgfb', '      1104220b.spc_X1_avgfb', '      1104220b.spc_X2_avgfb', '1104220b_pass1.spc', '      1104220b_pass1.spc_I_fwd', '      1104220b_pass1.spc_X1_fwd', '      1104220b_pass1.spc_X2_fwd', '      1104220b_pass1.spc_I_bwd', '      1104220b_pass1.spc_X1_bwd', '      1104220b_pass1.spc_X2_bwd', '      1104220b_pass1.spc_I_avgfb', '      1104220b_pass1.spc_X1_avgfb', '      1104220b_pass1.spc_X2_avgfb', '1104220f.spc', '      1104220f.spc_I_fwd', '      1104220f.spc_X1_fwd', '      1104220f.spc_X2_fwd', '      1104220f.spc_I_bwd', '      1104220f.spc_X1_bwd', '      1104220f.spc_X2_bwd', '      1104220f.spc_I_avgfb', '      1104220f.spc_X1_avgfb', '      1104220f.spc_X2_avgfb', '1105220c_pass10.spc', '      1105220c_pass10.spc_I_fwd', '      1105220c_pass10.spc_X1_fwd', '      1105220c_pass10.spc_X2_fwd', '      1105220c_pass10.spc_I_bwd', '      1105220c_pass10.spc_X1_bwd', '      1105220c_pass10.spc_X2_bwd', '      1105220c_pass10.spc_I_avgfb', '      1105220c_pass10.spc_X1_avgfb', '      1105220c_pass10.spc_X2_avgfb', '1105220c.spc', '      1105220c.spc_I_fwd', '      1105220c.spc_X1_fwd', '      1105220c.spc_X2_fwd', '      1105220c.spc_I_bwd', '      1105220c.spc_X1_bwd', '      1105220c.spc_X2_bwd', '      1105220c.spc_I_avgfb', '      1105220c.spc_X1_avgfb', '      1105220c.spc_X2_avgfb', '1105220c_pass1.spc', '      1105220c_pass1.spc_I_fwd', '      1105220c_pass1.spc_X1_fwd', '      1105220c_pass1.spc_X2_fwd', '      1105220c_pass1.spc_I_bwd', '      1105220c_pass1.spc_X1_bwd', '      1105220c_pass1.spc_X2_bwd', '      1105220c_pass1.spc_I_avgfb', '      1105220c_pass1.spc_X1_avgfb', '      1105220c_pass1.spc_X2_avgfb', '1105220c_pass2.spc', '      1105220c_pass2.spc_I_fwd', '      1105220c_pass2.spc_X1_fwd', '      1105220c_pass2.spc_X2_fwd', '      1105220c_pass2.spc_I_bwd', '      1105220c_pass2.spc_X1_bwd', '      1105220c_pass2.spc_X2_bwd', '      1105220c_pass2.spc_I_avgfb', '      1105220c_pass2.spc_X1_avgfb', '      1105220c_pass2.spc_X2_avgfb', '1105220c_pass3.spc', '      1105220c_pass3.spc_I_fwd', '      1105220c_pass3.spc_X1_fwd', '      1105220c_pass3.spc_X2_fwd', '      1105220c_pass3.spc_I_bwd', '      1105220c_pass3.spc_X1_bwd', '      1105220c_pass3.spc_X2_bwd', '      1105220c_pass3.spc_I_avgfb', '      1105220c_pass3.spc_X1_avgfb', '      1105220c_pass3.spc_X2_avgfb', '1105220c_pass4.spc', '      1105220c_pass4.spc_I_fwd', '      1105220c_pass4.spc_X1_fwd', '      1105220c_pass4.spc_X2_fwd', '      1105220c_pass4.spc_I_bwd', '      1105220c_pass4.spc_X1_bwd', '      1105220c_pass4.spc_X2_bwd', '      1105220c_pass4.spc_I_avgfb', '      1105220c_pass4.spc_X1_avgfb', '      1105220c_pass4.spc_X2_avgfb', '1105220c_pass5.spc', '      1105220c_pass5.spc_I_fwd', '      1105220c_pass5.spc_X1_fwd', '      1105220c_pass5.spc_X2_fwd', '      1105220c_pass5.spc_I_bwd', '      1105220c_pass5.spc_X1_bwd', '      1105220c_pass5.spc_X2_bwd', '      1105220c_pass5.spc_I_avgfb', '      1105220c_pass5.spc_X1_avgfb', '      1105220c_pass5.spc_X2_avgfb', '1105220c_pass6.spc', '      1105220c_pass6.spc_I_fwd', '      1105220c_pass6.spc_X1_fwd', '      1105220c_pass6.spc_X2_fwd', '      1105220c_pass6.spc_I_bwd', '      1105220c_pass6.spc_X1_bwd', '      1105220c_pass6.spc_X2_bwd', '      1105220c_pass6.spc_I_avgfb', '      1105220c_pass6.spc_X1_avgfb', '      1105220c_pass6.spc_X2_avgfb', '1105220c_pass7.spc', '      1105220c_pass7.spc_I_fwd', '      1105220c_pass7.spc_X1_fwd', '      1105220c_pass7.spc_X2_fwd', '      1105220c_pass7.spc_I_bwd', '      1105220c_pass7.spc_X1_bwd', '      1105220c_pass7.spc_X2_bwd', '      1105220c_pass7.spc_I_avgfb', '      1105220c_pass7.spc_X1_avgfb', '      1105220c_pass7.spc_X2_avgfb', '1105220c_pass8.spc', '      1105220c_pass8.spc_I_fwd', '      1105220c_pass8.spc_X1_fwd', '      1105220c_pass8.spc_X2_fwd', '      1105220c_pass8.spc_I_bwd', '      1105220c_pass8.spc_X1_bwd', '      1105220c_pass8.spc_X2_bwd', '      1105220c_pass8.spc_I_avgfb', '      1105220c_pass8.spc_X1_avgfb', '      1105220c_pass8.spc_X2_avgfb', '1105220c_pass9.spc', '      1105220c_pass9.spc_I_fwd', '      1105220c_pass9.spc_X1_fwd', '      1105220c_pass9.spc_X2_fwd', '      1105220c_pass9.spc_I_bwd', '      1105220c_pass9.spc_X1_bwd', '      1105220c_pass9.spc_X2_bwd', '      1105220c_pass9.spc_I_avgfb', '      1105220c_pass9.spc_X1_avgfb', '      1105220c_pass9.spc_X2_avgfb', '1117220d.spc', '      1117220d.spc_I_fwd', '      1117220d.spc_X1_fwd', '      1117220d.spc_X2_fwd', '      1117220d.spc_I_avgfb', '      1117220d.spc_X1_avgfb', '      1117220d.spc_X2_avgfb', '1105220f.spc', '      1105220f.spc_I_fwd', '      1105220f.spc_X1_fwd', '      1105220f.spc_X2_fwd', '      1105220f.spc_I_bwd', '      1105220f.spc_X1_bwd', '      1105220f.spc_X2_bwd', '      1105220f.spc_I_avgfb', '      1105220f.spc_X1_avgfb', '      1105220f.spc_X2_avgfb', '1105220f_pass1.spc', '      1105220f_pass1.spc_I_fwd', '      1105220f_pass1.spc_X1_fwd', '      1105220f_pass1.spc_X2_fwd', '      1105220f_pass1.spc_I_bwd', '      1105220f_pass1.spc_X1_bwd', '      1105220f_pass1.spc_X2_bwd', '      1105220f_pass1.spc_I_avgfb', '      1105220f_pass1.spc_X1_avgfb', '      1105220f_pass1.spc_X2_avgfb', '1105220f_pass2.spc', '      1105220f_pass2.spc_I_fwd', '      1105220f_pass2.spc_X1_fwd', '      1105220f_pass2.spc_X2_fwd', '      1105220f_pass2.spc_I_bwd', '      1105220f_pass2.spc_X1_bwd', '      1105220f_pass2.spc_X2_bwd', '      1105220f_pass2.spc_I_avgfb', '      1105220f_pass2.spc_X1_avgfb', '      1105220f_pass2.spc_X2_avgfb', '1105220f_pass3.spc', '      1105220f_pass3.spc_I_fwd', '      1105220f_pass3.spc_X1_fwd', '      1105220f_pass3.spc_X2_fwd', '      1105220f_pass3.spc_I_bwd', '      1105220f_pass3.spc_X1_bwd', '      1105220f_pass3.spc_X2_bwd', '      1105220f_pass3.spc_I_avgfb', '      1105220f_pass3.spc_X1_avgfb', '      1105220f_pass3.spc_X2_avgfb', '1105220f_pass4.spc', '      1105220f_pass4.spc_I_fwd', '      1105220f_pass4.spc_X1_fwd', '      1105220f_pass4.spc_X2_fwd', '      1105220f_pass4.spc_I_bwd', '      1105220f_pass4.spc_X1_bwd', '      1105220f_pass4.spc_X2_bwd', '      1105220f_pass4.spc_I_avgfb', '      1105220f_pass4.spc_X1_avgfb', '      1105220f_pass4.spc_X2_avgfb', '1105220f_pass5.spc', '      1105220f_pass5.spc_I_fwd', '      1105220f_pass5.spc_X1_fwd', '      1105220f_pass5.spc_X2_fwd', '      1105220f_pass5.spc_I_bwd', '      1105220f_pass5.spc_X1_bwd', '      1105220f_pass5.spc_X2_bwd', '      1105220f_pass5.spc_I_avgfb', '      1105220f_pass5.spc_X1_avgfb', '      1105220f_pass5.spc_X2_avgfb', '1105220g.spc', '      1105220g.spc_I_fwd', '      1105220g.spc_X1_fwd', '      1105220g.spc_X2_fwd', '      1105220g.spc_I_bwd', '      1105220g.spc_X1_bwd', '      1105220g.spc_X2_bwd', '      1105220g.spc_I_avgfb', '      1105220g.spc_X1_avgfb', '      1105220g.spc_X2_avgfb', '1105220g_pass1.spc', '      1105220g_pass1.spc_I_fwd', '      1105220g_pass1.spc_X1_fwd', '      1105220g_pass1.spc_X2_fwd', '      1105220g_pass1.spc_I_bwd', '      1105220g_pass1.spc_X1_bwd', '      1105220g_pass1.spc_X2_bwd', '      1105220g_pass1.spc_I_avgfb', '      1105220g_pass1.spc_X1_avgfb', '      1105220g_pass1.spc_X2_avgfb', '1105220g_pass2.spc', '      1105220g_pass2.spc_I_fwd', '      1105220g_pass2.spc_X1_fwd', '      1105220g_pass2.spc_X2_fwd', '      1105220g_pass2.spc_I_bwd', '      1105220g_pass2.spc_X1_bwd', '      1105220g_pass2.spc_X2_bwd', '      1105220g_pass2.spc_I_avgfb', '      1105220g_pass2.spc_X1_avgfb', '      1105220g_pass2.spc_X2_avgfb', '1117220c.spc', '      1117220c.spc_I_fwd', '      1117220c.spc_X1_fwd', '      1117220c.spc_X2_fwd', '      1117220c.spc_I_avgfb', '      1117220c.spc_X1_avgfb', '      1117220c.spc_X2_avgfb']
    # paths = ['D:/Code/2022oct/spc/testttt\\1104220b.spc', 'D:/Code/2022oct/spc/testttt\\1104220b.spc', 'D:/Code/2022oct/spc/testttt\\1104220b.spc', 'D:/Code/2022oct/spc/testttt\\1104220b.spc', 'D:/Code/2022oct/spc/testttt\\1104220b.spc', 'D:/Code/2022oct/spc/testttt\\1104220b.spc', 'D:/Code/2022oct/spc/testttt\\1104220b.spc', 'D:/Code/2022oct/spc/testttt\\1104220b.spc', 'D:/Code/2022oct/spc/testttt\\1104220b.spc', 'D:/Code/2022oct/spc/testttt\\1104220b.spc', 'D:/Code/2022oct/spc/testttt\\1104220b_pass1.spc', 'D:/Code/2022oct/spc/testttt\\1104220b_pass1.spc', 'D:/Code/2022oct/spc/testttt\\1104220b_pass1.spc', 'D:/Code/2022oct/spc/testttt\\1104220b_pass1.spc', 'D:/Code/2022oct/spc/testttt\\1104220b_pass1.spc', 'D:/Code/2022oct/spc/testttt\\1104220b_pass1.spc', 'D:/Code/2022oct/spc/testttt\\1104220b_pass1.spc', 'D:/Code/2022oct/spc/testttt\\1104220b_pass1.spc', 'D:/Code/2022oct/spc/testttt\\1104220b_pass1.spc', 'D:/Code/2022oct/spc/testttt\\1104220b_pass1.spc', 'D:/Code/2022oct/spc/testttt\\1104220f.spc', 'D:/Code/2022oct/spc/testttt\\1104220f.spc', 'D:/Code/2022oct/spc/testttt\\1104220f.spc', 'D:/Code/2022oct/spc/testttt\\1104220f.spc', 'D:/Code/2022oct/spc/testttt\\1104220f.spc', 'D:/Code/2022oct/spc/testttt\\1104220f.spc', 'D:/Code/2022oct/spc/testttt\\1104220f.spc', 'D:/Code/2022oct/spc/testttt\\1104220f.spc', 'D:/Code/2022oct/spc/testttt\\1104220f.spc', 'D:/Code/2022oct/spc/testttt\\1104220f.spc', 'D:/Code/2022oct/spc/testttt\\1105220c_pass10.spc', 'D:/Code/2022oct/spc/testttt\\1105220c_pass10.spc', 'D:/Code/2022oct/spc/testttt\\1105220c_pass10.spc', 'D:/Code/2022oct/spc/testttt\\1105220c_pass10.spc', 'D:/Code/2022oct/spc/testttt\\1105220c_pass10.spc', 'D:/Code/2022oct/spc/testttt\\1105220c_pass10.spc', 'D:/Code/2022oct/spc/testttt\\1105220c_pass10.spc', 'D:/Code/2022oct/spc/testttt\\1105220c_pass10.spc', 'D:/Code/2022oct/spc/testttt\\1105220c_pass10.spc', 'D:/Code/2022oct/spc/testttt\\1105220c_pass10.spc', 'D:/Code/2022oct/spc/testttt\\1105220c.spc', 'D:/Code/2022oct/spc/testttt\\1105220c.spc', 'D:/Code/2022oct/spc/testttt\\1105220c.spc', 'D:/Code/2022oct/spc/testttt\\1105220c.spc', 'D:/Code/2022oct/spc/testttt\\1105220c.spc', 'D:/Code/2022oct/spc/testttt\\1105220c.spc', 'D:/Code/2022oct/spc/testttt\\1105220c.spc', 'D:/Code/2022oct/spc/testttt\\1105220c.spc', 'D:/Code/2022oct/spc/testttt\\1105220c.spc', 'D:/Code/2022oct/spc/testttt\\1105220c.spc', 'D:/Code/2022oct/spc/testttt\\1105220c_pass1.spc', 'D:/Code/2022oct/spc/testttt\\1105220c_pass1.spc', 'D:/Code/2022oct/spc/testttt\\1105220c_pass1.spc', 'D:/Code/2022oct/spc/testttt\\1105220c_pass1.spc', 'D:/Code/2022oct/spc/testttt\\1105220c_pass1.spc', 'D:/Code/2022oct/spc/testttt\\1105220c_pass1.spc', 'D:/Code/2022oct/spc/testttt\\1105220c_pass1.spc', 'D:/Code/2022oct/spc/testttt\\1105220c_pass1.spc', 'D:/Code/2022oct/spc/testttt\\1105220c_pass1.spc', 'D:/Code/2022oct/spc/testttt\\1105220c_pass1.spc', 'D:/Code/2022oct/spc/testttt\\1105220c_pass2.spc', 'D:/Code/2022oct/spc/testttt\\1105220c_pass2.spc', 'D:/Code/2022oct/spc/testttt\\1105220c_pass2.spc', 'D:/Code/2022oct/spc/testttt\\1105220c_pass2.spc', 'D:/Code/2022oct/spc/testttt\\1105220c_pass2.spc', 'D:/Code/2022oct/spc/testttt\\1105220c_pass2.spc', 'D:/Code/2022oct/spc/testttt\\1105220c_pass2.spc', 'D:/Code/2022oct/spc/testttt\\1105220c_pass2.spc', 'D:/Code/2022oct/spc/testttt\\1105220c_pass2.spc', 'D:/Code/2022oct/spc/testttt\\1105220c_pass2.spc', 'D:/Code/2022oct/spc/testttt\\1105220c_pass3.spc', 'D:/Code/2022oct/spc/testttt\\1105220c_pass3.spc', 'D:/Code/2022oct/spc/testttt\\1105220c_pass3.spc', 'D:/Code/2022oct/spc/testttt\\1105220c_pass3.spc', 'D:/Code/2022oct/spc/testttt\\1105220c_pass3.spc', 'D:/Code/2022oct/spc/testttt\\1105220c_pass3.spc', 'D:/Code/2022oct/spc/testttt\\1105220c_pass3.spc', 'D:/Code/2022oct/spc/testttt\\1105220c_pass3.spc', 'D:/Code/2022oct/spc/testttt\\1105220c_pass3.spc', 'D:/Code/2022oct/spc/testttt\\1105220c_pass3.spc', 'D:/Code/2022oct/spc/testttt\\1105220c_pass4.spc', 'D:/Code/2022oct/spc/testttt\\1105220c_pass4.spc', 'D:/Code/2022oct/spc/testttt\\1105220c_pass4.spc', 'D:/Code/2022oct/spc/testttt\\1105220c_pass4.spc', 'D:/Code/2022oct/spc/testttt\\1105220c_pass4.spc', 'D:/Code/2022oct/spc/testttt\\1105220c_pass4.spc', 'D:/Code/2022oct/spc/testttt\\1105220c_pass4.spc', 'D:/Code/2022oct/spc/testttt\\1105220c_pass4.spc', 'D:/Code/2022oct/spc/testttt\\1105220c_pass4.spc', 'D:/Code/2022oct/spc/testttt\\1105220c_pass4.spc', 'D:/Code/2022oct/spc/testttt\\1105220c_pass5.spc', 'D:/Code/2022oct/spc/testttt\\1105220c_pass5.spc', 'D:/Code/2022oct/spc/testttt\\1105220c_pass5.spc', 'D:/Code/2022oct/spc/testttt\\1105220c_pass5.spc', 'D:/Code/2022oct/spc/testttt\\1105220c_pass5.spc', 'D:/Code/2022oct/spc/testttt\\1105220c_pass5.spc', 'D:/Code/2022oct/spc/testttt\\1105220c_pass5.spc', 'D:/Code/2022oct/spc/testttt\\1105220c_pass5.spc', 'D:/Code/2022oct/spc/testttt\\1105220c_pass5.spc', 'D:/Code/2022oct/spc/testttt\\1105220c_pass5.spc', 'D:/Code/2022oct/spc/testttt\\1105220c_pass6.spc', 'D:/Code/2022oct/spc/testttt\\1105220c_pass6.spc', 'D:/Code/2022oct/spc/testttt\\1105220c_pass6.spc', 'D:/Code/2022oct/spc/testttt\\1105220c_pass6.spc', 'D:/Code/2022oct/spc/testttt\\1105220c_pass6.spc', 'D:/Code/2022oct/spc/testttt\\1105220c_pass6.spc', 'D:/Code/2022oct/spc/testttt\\1105220c_pass6.spc', 'D:/Code/2022oct/spc/testttt\\1105220c_pass6.spc', 'D:/Code/2022oct/spc/testttt\\1105220c_pass6.spc', 'D:/Code/2022oct/spc/testttt\\1105220c_pass6.spc', 'D:/Code/2022oct/spc/testttt\\1105220c_pass7.spc', 'D:/Code/2022oct/spc/testttt\\1105220c_pass7.spc', 'D:/Code/2022oct/spc/testttt\\1105220c_pass7.spc', 'D:/Code/2022oct/spc/testttt\\1105220c_pass7.spc', 'D:/Code/2022oct/spc/testttt\\1105220c_pass7.spc', 'D:/Code/2022oct/spc/testttt\\1105220c_pass7.spc', 'D:/Code/2022oct/spc/testttt\\1105220c_pass7.spc', 'D:/Code/2022oct/spc/testttt\\1105220c_pass7.spc', 'D:/Code/2022oct/spc/testttt\\1105220c_pass7.spc', 'D:/Code/2022oct/spc/testttt\\1105220c_pass7.spc', 'D:/Code/2022oct/spc/testttt\\1105220c_pass8.spc', 'D:/Code/2022oct/spc/testttt\\1105220c_pass8.spc', 'D:/Code/2022oct/spc/testttt\\1105220c_pass8.spc', 'D:/Code/2022oct/spc/testttt\\1105220c_pass8.spc', 'D:/Code/2022oct/spc/testttt\\1105220c_pass8.spc', 'D:/Code/2022oct/spc/testttt\\1105220c_pass8.spc', 'D:/Code/2022oct/spc/testttt\\1105220c_pass8.spc', 'D:/Code/2022oct/spc/testttt\\1105220c_pass8.spc', 'D:/Code/2022oct/spc/testttt\\1105220c_pass8.spc', 'D:/Code/2022oct/spc/testttt\\1105220c_pass8.spc', 'D:/Code/2022oct/spc/testttt\\1105220c_pass9.spc', 'D:/Code/2022oct/spc/testttt\\1105220c_pass9.spc', 'D:/Code/2022oct/spc/testttt\\1105220c_pass9.spc', 'D:/Code/2022oct/spc/testttt\\1105220c_pass9.spc', 'D:/Code/2022oct/spc/testttt\\1105220c_pass9.spc', 'D:/Code/2022oct/spc/testttt\\1105220c_pass9.spc', 'D:/Code/2022oct/spc/testttt\\1105220c_pass9.spc', 'D:/Code/2022oct/spc/testttt\\1105220c_pass9.spc', 'D:/Code/2022oct/spc/testttt\\1105220c_pass9.spc', 'D:/Code/2022oct/spc/testttt\\1105220c_pass9.spc', 'D:/Code/2022oct/spc/testttt\\1117220d.spc', 'D:/Code/2022oct/spc/testttt\\1117220d.spc', 'D:/Code/2022oct/spc/testttt\\1117220d.spc', 'D:/Code/2022oct/spc/testttt\\1117220d.spc', 'D:/Code/2022oct/spc/testttt\\1117220d.spc', 'D:/Code/2022oct/spc/testttt\\1117220d.spc', 'D:/Code/2022oct/spc/testttt\\1117220d.spc', 'D:/Code/2022oct/spc/testttt\\1105220f.spc', 'D:/Code/2022oct/spc/testttt\\1105220f.spc', 'D:/Code/2022oct/spc/testttt\\1105220f.spc', 'D:/Code/2022oct/spc/testttt\\1105220f.spc', 'D:/Code/2022oct/spc/testttt\\1105220f.spc', 'D:/Code/2022oct/spc/testttt\\1105220f.spc', 'D:/Code/2022oct/spc/testttt\\1105220f.spc', 'D:/Code/2022oct/spc/testttt\\1105220f.spc', 'D:/Code/2022oct/spc/testttt\\1105220f.spc', 'D:/Code/2022oct/spc/testttt\\1105220f.spc', 'D:/Code/2022oct/spc/testttt\\1105220f_pass1.spc', 'D:/Code/2022oct/spc/testttt\\1105220f_pass1.spc', 'D:/Code/2022oct/spc/testttt\\1105220f_pass1.spc', 'D:/Code/2022oct/spc/testttt\\1105220f_pass1.spc', 'D:/Code/2022oct/spc/testttt\\1105220f_pass1.spc', 'D:/Code/2022oct/spc/testttt\\1105220f_pass1.spc', 'D:/Code/2022oct/spc/testttt\\1105220f_pass1.spc', 'D:/Code/2022oct/spc/testttt\\1105220f_pass1.spc', 'D:/Code/2022oct/spc/testttt\\1105220f_pass1.spc', 'D:/Code/2022oct/spc/testttt\\1105220f_pass1.spc', 'D:/Code/2022oct/spc/testttt\\1105220f_pass2.spc', 'D:/Code/2022oct/spc/testttt\\1105220f_pass2.spc', 'D:/Code/2022oct/spc/testttt\\1105220f_pass2.spc', 'D:/Code/2022oct/spc/testttt\\1105220f_pass2.spc', 'D:/Code/2022oct/spc/testttt\\1105220f_pass2.spc', 'D:/Code/2022oct/spc/testttt\\1105220f_pass2.spc', 'D:/Code/2022oct/spc/testttt\\1105220f_pass2.spc', 'D:/Code/2022oct/spc/testttt\\1105220f_pass2.spc', 'D:/Code/2022oct/spc/testttt\\1105220f_pass2.spc', 'D:/Code/2022oct/spc/testttt\\1105220f_pass2.spc', 'D:/Code/2022oct/spc/testttt\\1105220f_pass3.spc', 'D:/Code/2022oct/spc/testttt\\1105220f_pass3.spc', 'D:/Code/2022oct/spc/testttt\\1105220f_pass3.spc', 'D:/Code/2022oct/spc/testttt\\1105220f_pass3.spc', 'D:/Code/2022oct/spc/testttt\\1105220f_pass3.spc', 'D:/Code/2022oct/spc/testttt\\1105220f_pass3.spc', 'D:/Code/2022oct/spc/testttt\\1105220f_pass3.spc', 'D:/Code/2022oct/spc/testttt\\1105220f_pass3.spc', 'D:/Code/2022oct/spc/testttt\\1105220f_pass3.spc', 'D:/Code/2022oct/spc/testttt\\1105220f_pass3.spc', 'D:/Code/2022oct/spc/testttt\\1105220f_pass4.spc', 'D:/Code/2022oct/spc/testttt\\1105220f_pass4.spc', 'D:/Code/2022oct/spc/testttt\\1105220f_pass4.spc', 'D:/Code/2022oct/spc/testttt\\1105220f_pass4.spc', 'D:/Code/2022oct/spc/testttt\\1105220f_pass4.spc', 'D:/Code/2022oct/spc/testttt\\1105220f_pass4.spc', 'D:/Code/2022oct/spc/testttt\\1105220f_pass4.spc', 'D:/Code/2022oct/spc/testttt\\1105220f_pass4.spc', 'D:/Code/2022oct/spc/testttt\\1105220f_pass4.spc', 'D:/Code/2022oct/spc/testttt\\1105220f_pass4.spc', 'D:/Code/2022oct/spc/testttt\\1105220f_pass5.spc', 'D:/Code/2022oct/spc/testttt\\1105220f_pass5.spc', 'D:/Code/2022oct/spc/testttt\\1105220f_pass5.spc', 'D:/Code/2022oct/spc/testttt\\1105220f_pass5.spc', 'D:/Code/2022oct/spc/testttt\\1105220f_pass5.spc', 'D:/Code/2022oct/spc/testttt\\1105220f_pass5.spc', 'D:/Code/2022oct/spc/testttt\\1105220f_pass5.spc', 'D:/Code/2022oct/spc/testttt\\1105220f_pass5.spc', 'D:/Code/2022oct/spc/testttt\\1105220f_pass5.spc', 'D:/Code/2022oct/spc/testttt\\1105220f_pass5.spc', 'D:/Code/2022oct/spc/testttt\\1105220g.spc', 'D:/Code/2022oct/spc/testttt\\1105220g.spc', 'D:/Code/2022oct/spc/testttt\\1105220g.spc', 'D:/Code/2022oct/spc/testttt\\1105220g.spc', 'D:/Code/2022oct/spc/testttt\\1105220g.spc', 'D:/Code/2022oct/spc/testttt\\1105220g.spc', 'D:/Code/2022oct/spc/testttt\\1105220g.spc', 'D:/Code/2022oct/spc/testttt\\1105220g.spc', 'D:/Code/2022oct/spc/testttt\\1105220g.spc', 'D:/Code/2022oct/spc/testttt\\1105220g.spc', 'D:/Code/2022oct/spc/testttt\\1105220g_pass1.spc', 'D:/Code/2022oct/spc/testttt\\1105220g_pass1.spc', 'D:/Code/2022oct/spc/testttt\\1105220g_pass1.spc', 'D:/Code/2022oct/spc/testttt\\1105220g_pass1.spc', 'D:/Code/2022oct/spc/testttt\\1105220g_pass1.spc', 'D:/Code/2022oct/spc/testttt\\1105220g_pass1.spc', 'D:/Code/2022oct/spc/testttt\\1105220g_pass1.spc', 'D:/Code/2022oct/spc/testttt\\1105220g_pass1.spc', 'D:/Code/2022oct/spc/testttt\\1105220g_pass1.spc', 'D:/Code/2022oct/spc/testttt\\1105220g_pass1.spc', 'D:/Code/2022oct/spc/testttt\\1105220g_pass2.spc', 'D:/Code/2022oct/spc/testttt\\1105220g_pass2.spc', 'D:/Code/2022oct/spc/testttt\\1105220g_pass2.spc', 'D:/Code/2022oct/spc/testttt\\1105220g_pass2.spc', 'D:/Code/2022oct/spc/testttt\\1105220g_pass2.spc', 'D:/Code/2022oct/spc/testttt\\1105220g_pass2.spc', 'D:/Code/2022oct/spc/testttt\\1105220g_pass2.spc', 'D:/Code/2022oct/spc/testttt\\1105220g_pass2.spc', 'D:/Code/2022oct/spc/testttt\\1105220g_pass2.spc', 'D:/Code/2022oct/spc/testttt\\1105220g_pass2.spc', 'D:/Code/2022oct/spc/testttt\\1117220c.spc', 'D:/Code/2022oct/spc/testttt\\1117220c.spc', 'D:/Code/2022oct/spc/testttt\\1117220c.spc', 'D:/Code/2022oct/spc/testttt\\1117220c.spc', 'D:/Code/2022oct/spc/testttt\\1117220c.spc', 'D:/Code/2022oct/spc/testttt\\1117220c.spc', 'D:/Code/2022oct/spc/testttt\\1117220c.spc']
    import pickle
    with open('./filenames.fname', 'rb') as input:
        names = pickle.load(input)
    with open('./filepaths.fpath', 'rb') as input:
        paths = pickle.load(input)
    window = mySpcWindow(data_list=names, data_paths=paths)
    add_names = ['1104220b.spc', '1104220f.spc', '1105220c.spc', '1117220d.spc', '1105220f.spc', '1105220g.spc', '1117220c.spc']
    window.listWidget.addItems(add_names)
    window.refresh_list(0)
    window.refresh_list(2)
    window.del_pass_dict['1105220c.spc'] = [[1], [1,2,3,4,5,6,7], [], [1,2,3,4,5,6,7,8,10]]
    window.refresh_data(0)
    window.update_graph()
    window.show()
    sys.exit(app.exec_())