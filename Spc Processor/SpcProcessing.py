# -*- coding: utf-8 -*-
"""
@Date     : 2022/12/10 20:57:41
@Author   : milier00
@FileName : SpcProcessing.py
"""
import sys
sys.path.append("./ui/")
sys.path.append("./model/")
from PyQt5.QtWidgets import QApplication, QMainWindow, QAbstractItemView, QFileDialog, QShortcut, QMenu, QAction
from PyQt5.QtCore import pyqtSignal, Qt
from pyqtgraph.Qt import QtGui
from PyQt5 import QtCore
from PyQt5.QtCore import QSettings
from SpcPro_ui import Ui_SpcPro
from SpcWindow import mySpcWindow
from Data import *
import os
import ctypes
import copy


class mySpcProcessing(QMainWindow, Ui_SpcPro):
    # Common signal
    close_signal = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.init_UI()
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("myappid")

    def init_UI(self):
        self.move(50, 100)  # Init ui position

        self.dir_path = ''
        self.file_type = 0  # file visibility in dir, 0: (.spc); 1: (.dep)
        self.file_index = 0
        self.file_names = []  # expanded file names for internal use
        self.file_paths = []  # file paths according to file_names
        self.displayed_file_names = []  # folded file names in Data listWidget
        self.displayed_file_paths = []  # folded file paths in Data listWidget
        self.overall_names = []  # all expanded names (.spc) and (.dep) in the folder
        self.overall_paths = []  # paths according to overall_names
        self.windows = []  # window object list
        self.window_names = []  # window names
        self.linecut_option = 1  # 0: option1, 1: option2

        self.current_window = None
        self.previous_window = None

        self.cnfg = QSettings("config.ini", QSettings.IniFormat)  # Basic configuration module

        # signals |
        QApplication.instance().focusChanged.connect(self.focus_window_changed)

        # pushButton |
        self.pushButton_Open.clicked.connect(self.open_file)
        self.pushButton_Previous.clicked.connect(lambda: self.select_file(0))
        self.pushButton_Next.clicked.connect(lambda: self.select_file(1))
        self.pushButton_Refresh.clicked.connect(self.refresh_list)
        self.pushButton_do_algebra.clicked.connect(self.do_algebra)
        self.pushButton_Adv_algebra.clicked.connect(self.do_adv_algebra)
        self.pushButton_weightedAVG.clicked.connect(self.do_weighted_avg)
        self.pushButton_fft.clicked.connect(lambda: self.do_fft(0))
        self.pushButton_ifft.clicked.connect(lambda: self.do_fft(1))
        self.pushButton_do_SC.clicked.connect(self.do_simcurve)
        self.pushButton_Copy.clicked.connect(self.copy2window)
        self.pushButton_do_smooth.clicked.connect(self.do_smooth)
        self.pushButton_do_filter.clicked.connect(self.do_filter)
        self.pushButton_do_plot.clicked.connect(self.do_plot)
        self.pushButton_do_draw.clicked.connect(self.do_draw)

        # listWidget |
        self.listWidget.setDragEnabled(True)
        self.listWidget.setDragDropOverwriteMode(False)
        self.listWidget.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.listWidget.setDefaultDropAction(Qt.MoveAction)

        self.listWidget.setContextMenuPolicy(Qt.CustomContextMenu)
        self.listWidget.customContextMenuRequested[QtCore.QPoint].connect(self.rightMenuShow)

        self.listWidget.itemDoubleClicked.connect(lambda: self.file_changed(0))
        self.listWidget.itemClicked.connect(lambda: self.file_changed(1))

        # keyboard event |
        QShortcut(QtGui.QKeySequence('Up', ), self, lambda: self.select_file(0))
        QShortcut(QtGui.QKeySequence('Down', ), self, lambda: self.select_file(1))
        QShortcut(QtGui.QKeySequence('Left', ), self, lambda: self.select_file(0))
        QShortcut(QtGui.QKeySequence('Right', ), self, lambda: self.select_file(1))

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

    # Data List | open folder button slot
    def open_file(self):

        self.dir_path = self.cnfg.value("CNFG/FILE_PATH", type=str)
        if os.path.exists(self.dir_path):
            aFile, filt = QFileDialog.getOpenFileName(self, "Open file", self.dir_path, "SPC(*.spc)")
        else:
            curDir = "E:/Code/2022oct/spc/"
            aFile, filt = QFileDialog.getOpenFileName(self, "Open file", curDir, "SPC(*.spc)")

        dir, file = os.path.split(aFile)
        self.dir_path = dir

        self.file_paths.clear()
        self.file_names.clear()
        self.displayed_file_names.clear()
        self.displayed_file_paths.clear()
        self.listWidget.clear()

        for root, dirs, files in os.walk(self.dir_path, topdown=False):
            for file in files:
                if file[-4:] == ".spc":
                    data_path = os.path.join(root, file)
                    try:
                        data = SpcData(data_path)
                        self.file_paths.append(data.path)
                        self.file_names.append(data.name)
                        for name in data.ch_names:
                            self.file_paths.append(data.path)
                            self.file_names.append(name)
                        for name in data.ch_names_folded:
                            self.file_paths.append(data.path)
                            self.file_names.append(name)
                        for name in data.pt_ch_names:
                            self.file_paths.append(data.path)
                            self.file_names.append(name)
                        for name in data.pt_ch_names_folded:
                            self.file_paths.append(data.path)
                            self.file_names.append(name)
                        if file.find('_pass') == -1:
                            self.displayed_file_names.append(file)
                            self.displayed_file_paths.append(data_path)
                    except:
                        continue

        if len(self.file_paths) <= 0:
            return

        self.lineEdit.setText(self.dir_path)
        self.listWidget.addItems(self.displayed_file_names)

        import pickle
        with open('./filenames.fname', 'wb') as output:
            pickle.dump(self.file_names, output, pickle.HIGHEST_PROTOCOL)  # Save data
        with open('./filepaths.fpath', 'wb') as output:
            pickle.dump(self.file_paths, output, pickle.HIGHEST_PROTOCOL)  # Save data
        with open('./dspfilenames.fname', 'wb') as output:
            pickle.dump(self.displayed_file_names, output, pickle.HIGHEST_PROTOCOL)  # Save data
        with open('./dspfilepaths.fpath', 'wb') as output:
            pickle.dump(self.displayed_file_paths, output, pickle.HIGHEST_PROTOCOL)  # Save data
        print(self.file_names, self.file_paths)

    # Data List | data window list changed signal slot
    def refresh_list(self):
        self.file_paths.clear()
        self.file_names.clear()
        self.displayed_file_names.clear()
        self.displayed_file_paths.clear()
        self.listWidget.clear()

        for root, dirs, files in os.walk(self.dir_path, topdown=False):
            for file in files:
                if file[-4:] == ".spc":
                    data_path = os.path.join(root, file)
                    try:
                        data = SpcData(data_path)
                        self.file_paths.append(data.path)
                        self.file_names.append(data.name)
                        for name in data.ch_names:
                            self.file_paths.append(data.path)
                            self.file_names.append(name)
                        for name in data.ch_names_folded:
                            self.file_paths.append(data.path)
                            self.file_names.append(name)
                        if file.find('_pass') == -1:
                            self.displayed_file_names.append(file)
                            self.displayed_file_paths.append(data_path)
                    except:
                        continue

        if len(self.file_paths) <= 0:
            return

        self.lineEdit.setText(self.dir_path)
        self.listWidget.addItems(self.displayed_file_names)

    # Data List | file selection changed / single click / double click slot
    def file_changed(self, index):
        ''' Double click to open file in a new window.
            Single click / change selection to change selected data in top level window. '''
        if index == 0:    # double click slot
            if self.listWidget.count() > 0:
                self.file_index = self.listWidget.currentRow()

                # build a new data window
                data_window = mySpcWindow(self.file_names, self.file_paths)
                self.windows.append(data_window)
                self.windows[-1].listWidget.list_changed_signal.connect(self.refresh_list)

                # get selected file
                item = self.listWidget.currentItem()
                add_name = []
                if item.text().find('.spc') != -1 and item.text().find('_pass') == -1:
                    add_name.append(item.text())

                # add files to new window
                self.windows[-1].listWidget.addItems(add_name)
                self.windows[-1].set_list_checked(0)
                self.windows[-1].refresh_list(0)
                self.windows[-1].refresh_list(2)
                self.windows[-1].refresh_data(0)
                self.windows[-1].update_graph()
                self.windows[-1].show()

        elif index == 1:  # file selection changed / single click slot
            pass
            # if self.listWidget.count() > 0:
            #     self.file_index = self.listWidget.currentRow()
            #
            #     # update plot list in window
            #     if self.previous_window != (None or self.dat_info) and self.previous_window.listWidget.currentItem() != None:
            #     # if self.previous_window != None and self.previous_window.listWidget.currentItem() != None:
            #         if len(self.previous_window.listWidget.selectedItems()) != 0:
            #             self.previous_window.delete(0)
            #             self.add2window()
            #             self.previous_window.listWidget.setCurrentRow(0)

    # Windows | update previous/current window
    def focus_window_changed(self, old, new):
        ''' Note that current window is the window under focus, previous window is the last focused DataWindow '''
        if new != None and isinstance(new.window(), mySpcWindow):
            self.current_window = new.window()
        if old != None and isinstance(old.window(), mySpcWindow):
            self.previous_window = old.window()

    # Data List | right click menu
    def rightMenuShow(self):
        rightMenu = QMenu(self.listWidget)
        add2winAction = QAction("Add to current window", self, triggered=self.add2window)
        rightMenu.addAction(add2winAction)
        open2winAction = QAction("Open in new window", self, triggered=self.open2window)
        rightMenu.addAction(open2winAction)
        rightMenu.exec_(QtGui.QCursor.pos())

    def add2window(self):
        if self.listWidget.count() > 0:
            self.file_index = self.listWidget.currentRow()

            # get selected file
            item = self.listWidget.currentItem()
            add_name = [item.text()]
            if item.text().find('.spc') != -1 and item.text().find('_pass') == -1:
                add_name.append(item.text())

            # add files to previous window
            self.previous_window.listWidget.addItems(add_name)
            self.previous_window.set_list_checked(0)
            self.previous_window.refresh_list(0)
            self.previous_window.refresh_list(2)
            self.previous_window.refresh_data(0)
            self.previous_window.update_graph()
            self.previous_window.show()

    def open2window(self):
        if self.listWidget.count() > 0:
            self.file_index = self.listWidget.currentRow()

            # build a new data window
            data_window = mySpcWindow(self.file_names, self.file_paths)
            self.windows.append(data_window)
            self.windows[-1].listWidget.list_changed_signal.connect(self.refresh_list)

            # get selected file
            item = self.listWidget.currentItem()
            add_name = [item.text()]
            if item.text().find('.spc') != -1 and item.text().find('_pass') == -1:
                add_name.append(item.text())

            # add files to new window
            self.windows[-1].listWidget.addItems(add_name)
            self.windows[-1].set_list_checked(0)
            self.windows[-1].refresh_list(0)
            self.windows[-1].refresh_list(2)
            self.windows[-1].refresh_data(0)
            self.windows[-1].update_graph()
            self.windows[-1].show()

    # Processing | copy to new window button slot
    def copy2window(self):
        data_window = mySpcWindow(self.file_names, self.file_paths)
        self.windows.append(data_window)
        self.windows[-1].listWidget.list_changed_signal.connect(self.refresh_list)
        self.windows[-1].listWidget.addItems(self.previous_window.plot_list)
        self.windows[-1].set_list_checked(0)
        self.windows[-1].refresh_list(0)
        self.windows[-1].refresh_list(2)
        self.windows[-1].refresh_data(0)
        self.windows[-1].listWidget_Processed.addItems(self.previous_window.processed_list)
        self.windows[-1].processed_data = copy.deepcopy(self.previous_window.processed_data)
        self.windows[-1].set_list_checked(1)
        self.windows[-1].refresh_list(1)
        self.windows[-1].show()

    # Processing | weighted average do it button slot
    def do_weighted_avg(self):
        self.previous_window.weightedAVG.init_list(self.displayed_file_names, self.displayed_file_paths)
        self.previous_window.weightedAVG.show()
        self.previous_window.weightedAVG.raise_()

    # Processing | algebra do it button slot
    def do_algebra(self):
        mode = self.comboBox_algebra.currentIndex()
        if self.lineEdit_algebra.text() != '':
            value = float(self.lineEdit_algebra.text())
        else:
            value = 1.0
        self.previous_window.algebra(mode, value)

    # Processing | advanced algebra button slot
    def do_adv_algebra(self):
        self.previous_window.show_advAGB()

    # Processing | fft / ifft do it button slot
    def do_fft(self, index):
        self.previous_window.fft(index)

    # Processing | sim curve do it button slot
    def do_simcurve(self):
        self.previous_window.show_simCurve()

    # Processing | filter do it button slot
    def do_filter(self):
        method = self.comboBox_filter.currentIndex()
        lfreq = self.spinBox_lowfreq_filter.value()/100
        hfreq = self.spinBox_highfreq_filter.value()/100
        self.previous_window.filter(method, lfreq, hfreq)

    # Processing | smooth do it button slot
    def do_smooth(self):
        method = self.comboBox_smooth.currentText()
        factor = self.spinBox_smooth.value()
        self.previous_window.smooth(method, factor)

    # Processing | plot 2D3D do it button slot
    def do_plot(self):
        self.previous_window.plot2D3D()

    # Processing | draw 2D3D do it button slot
    def do_draw(self):
        self.previous_window.draw2D3D()

    # Close slot | close all sub windows
    def closeEvent(self, a0: QtGui.QCloseEvent) -> None:
        sys.exit(0)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = mySpcProcessing()
    app.setStyle("Fusion")
    window.show()
    sys.exit(app.exec_())