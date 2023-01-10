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
from PyQt5.QtWidgets import QApplication, QWidget, QSizePolicy,QInputDialog, QMessageBox, QAbstractItemView, QGridLayout, \
    QComboBox, QFileDialog, QShortcut, QListWidget, QMenu, QAction
from PyQt5.QtCore import pyqtSignal, Qt
from PyQt5.QtGui import QKeySequence, QColor
from pyqtgraph.Qt import QtGui, QtCore
from images import myImages
from SpcPassEditor_ui import Ui_SpcPassEditor
from switch_button import SwitchButton_PE
from message_dialog import MessageDialog
from Data import *
from func1D import *
import numpy as np
import functools as ft
import pyqtgraph as pg
from sympy import *
import math
import copy
import ctypes
import os
import colorcet as cc
import random

class mySpcPassEditor(QWidget, Ui_SpcPassEditor):
    # Common signal
    close_signal = pyqtSignal(str, list)
    list_changed_signal = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.init_UI()
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("myappid")

    def init_UI(self):
        self.data = None
        self.current_pt = 0
        self.show_fb = False
        self.show_avg = False
        self.plot_list = []
        self.data_list = []
        self.displayed_plot_list = []
        self.del_pass_list = []
        self.img = myImages()
        self.func1D = myFunc()
        self.parent_data_colors = self.func1D.parent_data_colors

        # pushButton |
        self.pushButton_xScale.clicked.connect(lambda: self.scale(0))
        self.pushButton_yScale.clicked.connect(lambda: self.scale(1))
        self.pushButton_Scanner.clicked.connect(self.show_scanner)
        self.pushButton_All1.clicked.connect(self.check_all)
        self.pushButton_Avg.toggled.connect(self.avg)
        self.pushButton_check.clicked.connect(lambda: self.see(1))
        self.pushButton_uncheck.clicked.connect(lambda: self.see(0))

        # switchButton |
        self.switchButton_FB = SwitchButton_PE(parent=self)
        self.switchButton_FB.checkedChanged.connect(self.show_fb_changed)
        self.switchButton_FB.setChecked(False)

        # scrollBar |
        self.scrollBar_ptnum.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.scrollBar_ptnum.valueChanged.connect(self.update_ptnum)
        self.scrollBar_ptnum.setMinimum(1)

        # Plot control |
        layout = QGridLayout()
        layout.addWidget(self.label_ptnum, 1, 1)
        layout.addWidget(self.label_num, 1, 2)
        layout.addWidget(self.scrollBar_ptnum, 1, 3)
        layout.addWidget(self.switchButton_FB, 1, 4)
        self.widget_plot.setLayout(layout)

        # listWidget |
        self.listWidget.setDragEnabled(False)
        self.listWidget.setDragDropOverwriteMode(False)
        self.listWidget.setSelectionMode(QAbstractItemView.ExtendedSelection)

        self.listWidget.setContextMenuPolicy(Qt.CustomContextMenu)
        self.listWidget.customContextMenuRequested[QtCore.QPoint].connect(self.rightMenuShow)
        self.listWidget.itemClicked.connect(self.edit_check_state)

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
        # keyBoard event | Delete
        self.shortcut = QShortcut(QKeySequence('V'), self)
        self.shortcut.activated.connect(self.press_see)

    def init_list(self, data):
        self.data = data

        self.plot_list = [] # each element is a list for single point, pass is expanded, length = pt_num
        self.data_list = [] # each element is a list for a single point, pass is expanded, length = pt_num
        self.del_pass_list = [[] for _ in range(data.pt_num)]
        self.remember_plot_list = [{} for _ in range(data.pt_num)]

        # show AVG
        if not self.show_fb:
            for i in range(data.pt_num):
                pt_name_list = []
                pt_data_list = []
                for j in range(data.pass_num):
                    name = 'Point# ' + str(i+1).zfill(2) + '_pass ' + str(j+1).zfill(3)
                    for suffix in data.ch_suffix_folded:
                        pt_name_list.append(name + suffix)
                    single_pt_data = Spc_SinglePt(self.data.child[j].data[i], self.data.scan_dir, self.data.data_num)
                    pt_data_list += single_pt_data.pack_data(False)

                self.plot_list.append(pt_name_list)
                self.data_list.append(pt_data_list)

        # show forward and backward
        else:
            for i in range(data.pt_num):
                pt_name_list = []
                pt_data_list = []
                for j in range(data.pass_num):
                    name = 'Point# ' + str(i+1).zfill(2) + '_pass ' + str(j+1).zfill(3)
                    for suffix in data.ch_suffix:
                        pt_name_list.append(name + suffix)
                    single_pt_data = Spc_SinglePt(self.data.child[j].data[i], self.data.scan_dir, self.data.data_num)
                    pt_data_list += single_pt_data.pack_data(True)
                self.plot_list.append(pt_name_list)
                self.data_list.append(pt_data_list)

        self.current_pt = 0
        self.scrollBar_ptnum.setMaximum(data.pt_num)
        self.scrollBar_ptnum.setValue(0)
        self.groupBox.setTitle(data.name)
        self.listWidget.clear()
        self.listWidget.addItems(self.plot_list[0])
        self.displayed_plot_list.clear()
        self.displayed_plot_list = copy.deepcopy(self.plot_list)
        self.refresh_list(0)

    def init_data(self):
        pass
        # (point_index, pass_num, channel=fb/avg)
        # for i in range(self.data.pt_num)
        # self.data_list = []

    # Plot list | index=0: init_list(), update_ptnum; index=1: show_fb_changed()
    def refresh_list(self, index):
        if self.data != None:
            # get current plot list from listWidget
            self.plot_list = []  # each element is a list for single point, pass is expanded
            self.data_list = []  # each element is a list for a single point, pass is expanded

            # show AVG
            if not self.show_fb:
                for i in range(self.data.pt_num):
                    pt_name_list = []
                    pt_data_list = []
                    for j in range(self.data.pass_num):
                        name = 'Point# ' + str(i + 1).zfill(2) + '_pass ' + str(j + 1).zfill(3)
                        for suffix in self.data.ch_suffix_folded:
                            pt_name_list.append(name + suffix)
                        single_pt_data = Spc_SinglePt(self.data.child[j].data[i], self.data.scan_dir,
                                                      self.data.data_num)
                        pt_data_list += single_pt_data.pack_data(False)
                    self.plot_list.append(pt_name_list)
                    self.data_list.append(pt_data_list)

            # show forward and backward
            else:
                for i in range(self.data.pt_num):
                    pt_name_list = []
                    pt_data_list = []
                    for j in range(self.data.pass_num):
                        name = 'Point# ' + str(i + 1).zfill(2) + '_pass ' + str(j + 1).zfill(3)
                        for suffix in self.data.ch_suffix:
                            pt_name_list.append(name + suffix)
                        single_pt_data = Spc_SinglePt(self.data.child[j].data[i], self.data.scan_dir,
                                                      self.data.data_num)
                        pt_data_list += single_pt_data.pack_data(True)
                    self.plot_list.append(pt_name_list)
                    self.data_list.append(pt_data_list)

            self.listWidget.clear()
            self.listWidget.addItems(self.plot_list[self.current_pt])
            self.set_list_checked()
            if index == 0:
                self.recover_check_state()
            else:
                self.displayed_plot_list.clear()
                self.displayed_plot_list = copy.deepcopy(self.plot_list)
                for i in range(self.data.pt_num):
                    self.del_pass_list[i] = []
            self.listWidget.setCurrentRow(-1)
            self.update_del_pass()
            self.update_graph(0)

    # Plot List | remember check state
    def remember_check_state(self):
        # remember check state in Plot list
        self.remember_plot_list[self.current_pt] = {}
        for row in range(self.listWidget.count()):
            self.remember_plot_list[self.current_pt][self.listWidget.item(row).text()] = self.listWidget.item(row).checkState()

    # Plot List | recover check state
    def recover_check_state(self):
        # recover check state in Plot list
        for row in range(self.listWidget.count()):
            if self.listWidget.item(row).text() in self.remember_plot_list[self.current_pt].keys():
                self.listWidget.item(row).setCheckState(self.remember_plot_list[self.current_pt][self.listWidget.item(row).text()])

        self.displayed_plot_list[self.current_pt] = []
        for row in range(self.listWidget.count()):
            if self.listWidget.item(row).checkState() != 0:
                self.displayed_plot_list[self.current_pt].append(self.listWidget.item(row).text())
        self.update_graph(0)

    def edit_check_state(self):
        self.displayed_plot_list[self.current_pt].clear()
        self.del_pass_list[self.current_pt].clear()
        for row in range(self.listWidget.count()):
            if self.listWidget.item(row).checkState() != 0:
                self.displayed_plot_list[self.current_pt].append(self.listWidget.item(row).text())
            else:
                i = self.listWidget.item(row).text().find('_pass')
                f = i+6
                pnum = int(self.listWidget.item(row).text()[f:f+3])-1
                self.del_pass_list[self.current_pt].append(pnum)
        self.update_del_pass()
        self.remember_check_state()
        self.update_graph(0)

    def update_del_pass(self):
        text = ''
        self.del_pass_list[self.current_pt] = list(set(self.del_pass_list[self.current_pt]))
        for i in self.del_pass_list[self.current_pt]:
            text += str(i+1)+';'
        self.label_delPass.setText(text)

    def update_ptnum(self, value):
        self.label_num.setText(str(value))
        self.current_pt = value - 1
        if not self.show_avg:
            self.refresh_list(0)
        else:
            self.update_del_pass()
            self.avg(True)

    # Plot List | set all items in listWidget checked
    def set_list_checked(self):
        for row in range(self.listWidget.count()):
            self.listWidget.item(row).setCheckState(2)

    def rightMenuShow(self):
        pass

    def press_see(self):
        items = self.listWidget.selectedItems()
        check_state = 0
        for item in items:
            check_state += item.checkState()
        if check_state == 0:
            for item in items:
                item.setCheckState(2)
        else:
            for item in items:
                item.setCheckState(0)

    def see(self, index):
        items = self.listWidget.selectedItems()
        for item in items:
            if index == 0:
                item.setCheckState(0)
            elif index == 1:
                item.setCheckState(2)

    # Graphics | scale by X/Y axis
    def scale(self, index):
        if index == 0:  # scale x
            self.plot.vb.enableAutoRange(axis='x', enable=True)
            self.plot.vb.updateAutoRange()
        elif index == 1:  # sacle y
            self.plot.vb.enableAutoRange(axis='y', enable=True)
            self.plot.vb.updateAutoRange()

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
                    i] + "'>(%0.2f, %0.2f)   </span>" % (data_x[i], data_y[i])
                if num % 5 == 0:
                    text += "<br />"
            self.label.setText(text)

            self.scanner_vLine.setPos(mousePoint.x())

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

    # switchButton slot | show/hide fb
    def show_fb_changed(self, isChecked: bool):
        self.show_fb = isChecked
        text = 'Show FB' if isChecked else 'Show AVG'
        self.switchButton_FB.setText(text)
        if not self.show_avg:
            self.refresh_list(1)
        else:
            self.avg(True)

    # Plot List | check all button slot
    def check_all(self):
        # set plots all checked in Plot list
        if self.pushButton_All1.isChecked():
            for row in range(self.listWidget.count()):
                self.listWidget.item(row).setCheckState(2)
        else:
            for row in range(self.listWidget.count()):
                self.listWidget.item(row).setCheckState(0)

        # self.displayed_plot_list[self.current_pt].clear()
        # for row in range(self.listWidget.count()):
        #     if self.listWidget.item(row).checkState() != 0:
        #         self.displayed_plot_list[self.current_pt].append(self.listWidget.item(row).text())
        self.edit_check_state()
        self.update_graph(0)

    def avg(self, status):
        self.show_avg = status
        if status:
            # each element is a list for a single point, length = self.data.pt_num
            # [[(x,I),(x,X1),(x,X2)], [(x,I),(x,X1),(x,X2)], [(x,I),(x,X1),(x,X2)], [(x,I),(x,X1),(x,X2)]]
            self.avg_data_list = self.data.avg_child_part(self.show_fb, self.del_pass_list)
            self.enable_avg(not status)
            self.update_graph(1)
        else:
            self.enable_avg(not status)
            self.refresh_list(0)
            self.update_graph(0)

    def enable_avg(self, enable):
        self.listWidget.setEnabled(enable)

    # Graphics | update plot in current window
    # index=0: normal mode, plot from displayed_plot_list and data_list
    # index=1: avg mode, plot pass-aveaged data
    def update_graph(self, index):
        # plot in graphicsView
        self.plot.clear()
        self.lines = []
        if index == 0:
            for i, name in enumerate(self.displayed_plot_list[self.current_pt]):

                ind = self.plot_list[self.current_pt].index(name)
                data = self.data_list[self.current_pt][ind]

                # color = self.parent_data_colors[i]
                # pen = cc.glasbey_light[random.randint(0, 255)]
                pen = pg.mkPen(cc.glasbey_dark[i], width=2)
                self.lines.append(self.plot.plot(x=data[0], y=data[1], name=name, pen=pen))
                # self.lines.append(self.plot.plot(x=data[0], y=data[1], name=name, pen=QColor(255,255,255,255)))
            # self.lines[2].setPen(pg.mkPen((255,0,0,255)))
        else:
            for i in range(len(self.avg_data_list[self.current_pt])):
                data = self.avg_data_list[self.current_pt][i]
                pen = pg.mkPen(cc.glasbey_dark[i], width=2)
                self.lines.append(self.plot.plot(x=data[0], y=data[1], pen=pen))

    def del_list_empty(self) -> bool:
        if_empty = 1
        for i in range(self.data.pt_num):
            if_empty *= int(self.del_pass_list[i] == [])
        return bool(if_empty)

    def get_del_text(self) -> str:
        if not self.del_list_empty():
            text = 'These passes are deleted:\n'
            for i in range(self.data.pt_num):
                text += 'Point#'; text += str(i+1); text += ": ";
                for p in self.del_pass_list[i]:
                    text += str(p+1); text += ',';
                text += '\n'
        else:
            text = 'No pass deleted.'
        return text

    def showDialog(self, content):
        w = MessageDialog('Warning', content, self)
        w.exec()

    def closeEvent(self, a0: QtGui.QCloseEvent) -> None:
        self.showDialog(self.get_del_text())
        self.close_signal.emit(self.data.name, self.del_pass_list)
        a0.accept()



if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = mySpcPassEditor()
    spc = SpcData('D:/Code/2022oct/spc/testttt\\1105220c.spc')
    window.init_list(spc)
    window.show()
    sys.exit(app.exec_())