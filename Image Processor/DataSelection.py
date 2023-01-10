# -*- coding: utf-8 -*-
"""
@Date     : 2021/5/24 09:26:33
@Author   : milier00
@FileName : DataSelection.py
"""
import copy
import sys
sys.path.append("../ui/")
sys.path.append("../data/")
sys.path.append("../Matlab/")
sys.path.append("../model/")
sys.path.append("../fittingSC/")
sys.path.append("../Plot2D3D/")
from PyQt5.QtWidgets import QAction, QMenu, QApplication, QWidget, QMessageBox, QAbstractItemView, QGridLayout, QShortcut, QListWidget
from PyQt5.QtCore import pyqtSignal, Qt
from PyQt5.QtGui import QKeySequence
from pyqtgraph.Qt import QtGui, QtCore
from DataSelection_ui import Ui_DataSelection
from Data import *
from func1D import *
import ctypes

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

class myDataSelection(QWidget, Ui_DataSelection):
    # Common signal
    close_signal = pyqtSignal(list)
    list_changed_signal = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.init_UI()
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("myappid")
        
    def init_UI(self):

        # signals |
        QApplication.instance().focusObjectChanged.connect(self.focus_changed)
        # listWidget | source
        self.listWidget_source.setDragEnabled(True)
        self.listWidget_source.setDragDropOverwriteMode(False)
        self.listWidget_source.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.listWidget_source.setDefaultDropAction(Qt.MoveAction)

        self.listWidget_source.setContextMenuPolicy(Qt.CustomContextMenu)
        self.listWidget_source.customContextMenuRequested[QtCore.QPoint].connect(lambda: self.rightMenuShow(0))

        # self.listWidget_source.itemDoubleClicked.connect(lambda: self.file_changed(0))
        # self.listWidget_source.itemClicked.connect(lambda: self.file_changed(1))
        # self.listWidget.setCurrentRow(-1)

        # keyboard event |
        QShortcut(QtGui.QKeySequence('Up', ), self, lambda: self.select_file(0))
        QShortcut(QtGui.QKeySequence('Down', ), self, lambda: self.select_file(1))
        QShortcut(QtGui.QKeySequence('Left', ), self, lambda: self.select_file(0))
        QShortcut(QtGui.QKeySequence('Right', ), self, lambda: self.select_file(1))
        
        # listWidget | sink
        self.listWidget_sink = DropInList()
        self.listWidget_sink.setObjectName('listWidget_sink')
        self.listWidget_sink.list_changed_signal.connect(lambda: self.refresh_list(1))
        # self.listWidget_sink.itemClicked.connect(ft.partial(self.update_graph, 0))
        # self.listWidget_sink.itemSelectionChanged.connect(self.edit_selection)
        self.listWidget_sink.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.listWidget_sink.setContextMenuPolicy(Qt.CustomContextMenu)
        self.listWidget_sink.customContextMenuRequested[QtCore.QPoint].connect(lambda: self.rightMenuShow(1))
        grid = QGridLayout()
        grid.addWidget(self.listWidget_sink, 1, 1)
        self.groupBox_2.setLayout(grid)

        # keyBoard event | Delete
        self.shortcut = QShortcut(QKeySequence('Delete'), self)
        self.shortcut.activated.connect(self.edit_delete)

    def init_list(self, data_list):
        self.listWidget_source.clear()
        self.listWidget_sink.clear()
        self.parent_list = copy.deepcopy(data_list)
        self.sink_list = []
        self.listWidget_source.addItems(data_list)
        self.refresh_list(0)

    # Source(0) & Sink(1) | right click menu
    def rightMenuShow(self, index):
        if index == 0:  # plot list
            rightMenu = QMenu(self.listWidget_source)
            deleteAction = QAction("Delete", self, triggered=lambda: self.delete(0))
            addAction = QAction("Add", self, triggered=self.add)
            rightMenu.addAction(deleteAction)
            rightMenu.addAction(addAction)
            rightMenu.exec_(QtGui.QCursor.pos())
        elif index == 1:  # processed list
            rightMenu = QMenu(self.listWidget_sink)
            deleteAction = QAction("Delete", self, triggered=lambda: self.delete(1))
            rightMenu.addAction(deleteAction)
            rightMenu.exec_(QtGui.QCursor.pos())

    # Source(0) & Sink(1) | refresh
    def refresh_list(self, index):
        if index == 0:  
            # get current plot list from listWidget
            self.source_list = []
            for row in range(self.listWidget_source.count()):
                self.source_list.append(self.listWidget_source.item(row).text())

            # remove repeated items
            self.source_list = list(set(self.source_list))
            # sort plot list
            self.source_list = sorted(self.source_list, key=self.parent_list.index)
            # add items to listWidget
            self.listWidget_source.clear()
            self.listWidget_source.addItems(self.source_list)
            self.listWidget_source.setCurrentRow(-1)

        elif index == 1:
            self.sink_list = []
            for row in range(self.listWidget_sink.count()):
                self.sink_list.append(self.listWidget_sink.item(row).text())
            self.listWidget_sink.clear()
            self.listWidget_sink.addItems(self.sink_list)

    # Source(0) & Sink(1) | delete
    def delete(self, index):
        if index == 0:  
            items = self.listWidget_source.selectedItems()

            for item in items:
                # get list of index to delete
                delete_items = []
                delete_items.append(item.text())

                # delete from listWidget
                for i in range(len(self.source_list) - 1, -1, -1):
                    if self.source_list[i] in delete_items:
                        self.source_list.pop(i)

            self.listWidget_source.clear()
            self.listWidget_source.addItems(self.source_list)
            self.refresh_list(0)

        elif index == 1:
            items = self.listWidget_sink.selectedItems()

            for item in items:
                # get list of index to delete
                delete_items = []
                delete_items.append(item.text())

                # delete from listWidget
                for i in range(len(self.sink_list) - 1, -1, -1):
                    if self.sink_list[i] in delete_items:
                        self.sink_list.pop(i)

                # add back to source list
                self.listWidget_source.addItems(delete_items)
                self.refresh_list(0)

            self.listWidget_sink.clear()
            self.listWidget_sink.addItems(self.sink_list)
            self.refresh_list(1)

    # Source | add to sink
    def add(self):
        add_list = []
        for item in self.listWidget_source.selectedItems():
            add_list.append(item.text())
        self.listWidget_sink.addItems(add_list)
        self.delete(0)
        self.refresh_list(1)

    # Data List | file type in comboBox changed slot
    def select_file(self, index):
        if self.current_list == self.listWidget_source:
            if index == 0:  # previous
                if self.listWidget_source.currentRow() - 1 == -1:
                    self.listWidget_source.setCurrentRow(len(self.source_list) - 1)
                else:
                    self.listWidget_source.setCurrentRow(self.listWidget_source.currentRow() - 1)
            elif index == 1:  # next
                if self.listWidget_source.currentRow() + 1 == len(self.source_list):
                    self.listWidget_source.setCurrentRow(0)
                else:
                    self.listWidget_source.setCurrentRow(self.listWidget_source.currentRow() + 1)
        elif self.current_list == self.listWidget_sink:
            if index == 0:  # previous
                if self.listWidget_sink.currentRow() - 1 == -1:
                    self.listWidget_sink.setCurrentRow(len(self.sink_list) - 1)
                else:
                    self.listWidget_sink.setCurrentRow(self.listWidget_sink.currentRow() - 1)
            elif index == 1:  # next
                if self.listWidget_sink.currentRow() + 1 == len(self.sink_list):
                    self.listWidget_sink.setCurrentRow(0)
                else:
                    self.listWidget_sink.setCurrentRow(self.listWidget_sink.currentRow() + 1)

    # delete keyboard event slot, to figure out target list
    def edit_delete(self):
        if self.current_list == self.listWidget_source:
            self.delete(0)
        elif self.current_list == self.listWidget_sink:
            self.delete(1)

    # focus object changed
    def focus_changed(self, obj):
        if obj != None:
            if obj == self.listWidget_source or obj == self.listWidget_sink:
                self.current_list = obj

    # Emit close signal
    def closeEvent(self, event):
        if len(self.sink_list) != 0 and len(self.sink_list) <= 4:
            self.close_signal.emit(self.sink_list)
            event.accept()
        else:
            reply = QMessageBox.warning(None, "Data Selection", 'Please select 1~4 data for further operation. Are you sure to exit?', QMessageBox.Yes | QMessageBox.No)
            if reply == QMessageBox.Yes:
                event.accept()
            else:
                event.ignore()
 

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
    window = myDataSelection()
    window.init_list(names)
    # window.listWidget.addItems(names)
    # window.refresh_list(0)
    window.show()
    sys.exit(app.exec_())