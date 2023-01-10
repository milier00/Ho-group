# -*- coding: utf-8 -*-
"""
@Date     : 12/24/2022 18:44:50
@Author   : milier00
@FileName : WeightedAVG.py
"""
import sys
sys.path.append("./ui/")
sys.path.append("./model/")
sys.path.append("./Plot2D3D/")
from PyQt5.QtWidgets import QApplication, QMenu, QAction, QWidget, QMessageBox, \
    QAbstractItemView, QGridLayout, QShortcut, QListWidget
from PyQt5.QtCore import pyqtSignal, Qt
from PyQt5.QtGui import QKeySequence
from pyqtgraph.Qt import QtGui, QtCore
from WeightedAVG_ui import Ui_WeightedAVG
from SpcPassEditor import mySpcPassEditor
from message_dialog import MessageDialog
from Data import *
from func1D import *
import numpy as np
import copy
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


class myWeightedAVG(QWidget, Ui_WeightedAVG):
    # Common signal
    close_signal = pyqtSignal(list, list)
    list_changed_signal = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.init_UI()
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("myappid")

    def init_UI(self):
        self.del_pass_dict = {}

        self.passEditor = mySpcPassEditor()
        self.passEditor.close_signal.connect(self.update_del_pass)

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
        self.listWidget_sink.list_changed_signal.connect(self.addto_del_pass)
        self.listWidget_sink.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.listWidget_sink.setContextMenuPolicy(Qt.CustomContextMenu)
        self.listWidget_sink.customContextMenuRequested[QtCore.QPoint].connect(lambda: self.rightMenuShow(1))
        grid = QGridLayout()
        grid.addWidget(self.listWidget_sink, 1, 1)
        self.groupBox_2.setLayout(grid)

        # keyBoard event | Delete
        self.shortcut = QShortcut(QKeySequence('Delete'), self)
        self.shortcut.activated.connect(self.edit_delete)

    def init_list(self, data_list, path_list):
        self.listWidget_source.clear()
        self.parent_data_list = copy.deepcopy(data_list)
        self.parent_data_paths = copy.deepcopy(path_list)
        self.sink_list = []
        self.listWidget_source.addItems(data_list)
        self.refresh_list(0)

    # Source(0) & Sink(1) | right click menu
    def rightMenuShow(self, index):
        if index == 0:  # plot list
            rightMenu = QMenu(self.listWidget_source)
            deleteAction = QAction("Delete", self, triggered=lambda: self.delete(0))
            addAction = QAction("Add", self, triggered=self.add)
            editpassAction = QAction("Edit pass", self, triggered=self.edit_pass)
            rightMenu.addAction(deleteAction)
            rightMenu.addAction(addAction)
            rightMenu.addAction(editpassAction)
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
            self.source_list = sorted(self.source_list, key=self.parent_data_list.index)
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
            self.addto_del_pass()

    # Source | add to sink
    def add(self):
        add_list = []
        for item in self.listWidget_source.selectedItems():
            add_list.append(item.text())
        self.listWidget_sink.addItems(add_list)
        self.delete(0)
        self.refresh_list(1)
        self.addto_del_pass()

    # Source | open in Pass Editor Window
    def edit_pass(self):
        index = self.parent_data_list.index(self.listWidget_source.currentItem().text())
        data_path = self.parent_data_paths[index]
        data = SpcData(data_path)
        if data.every:
            self.passEditor.init_list(data)
            self.passEditor.show()
        else:
            self.showDialog('No single pass data available!')

    def showDialog(self, content):
        w = MessageDialog('Warning', content, self)
        w.exec()

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

    def update_del_pass(self, name, del_pass_list):
        self.del_pass_dict[name] = del_pass_list
        self.listWidget_sink.addItems([name])
        self.delete(0)
        self.refresh_list(1)
        self.update_del_info()
        print(self.del_pass_dict)

    def addto_del_pass(self):

        # delete addtional keys if they are deleted from sink
        for name in list(self.del_pass_dict.keys()):
            if name not in self.sink_list:
                del self.del_pass_dict[name]

        # fresh from sink list, add new key value as None, old key doesn't change
        for name in self.sink_list:
            if name not in self.del_pass_dict.keys():
                self.del_pass_dict[name] = None
            else:
                continue

        # update text browser
        self.update_del_info()

    def update_del_info(self):
        self.textBrowser_delPasses.clear()
        for name, passes in self.del_pass_dict.items():
            text = name + "\n"
            if passes is not None:
                for i in range(len(passes)):
                    text += '\tPoint#' + str(i+1) + ":\t" + str(np.array(passes[i])+1) +'\n'
            else:
                text += '\t'+'None'+'\n'
            self.textBrowser_delPasses.append(text)

    def get_weighted_avg(self):
        """ Average selected data by pass number """
        ## check if all data have same pt_num
        ## check if all data have same ch_num
        ## check if all data have same data_num
        ## if false, return -1
        ## if true, get average, return result

        # init data list
        self.data_list = []
        for name, passes in self.del_pass_dict.items():
            path = self.parent_data_paths[self.parent_data_list.index(name)]
            data = SpcData(path)
            self.data_list.append(data)
        print('data_list:', len(self.data_list))

        # check if selected data have same dimensions
        ptnum = self.data_list[0].pt_num; badpt = 0;
        chnum = self.data_list[0].ch_num; badch = 0;
        datnum = self.data_list[0].dat_num; baddat = 0;
        for data in self.data_list:
            if ptnum == data.pt_num:
                badpt += 0
            else:
                badpt += 1
            if chnum == data.ch_num:
                badch += 0
            else:
                badch += 1
            if datnum == data.dat_num:
                baddat += 0
            else:
                baddat += 1
        if badpt != 0:
            print("Sorry, point num not match")
            raise Exception("Sorry, point num not match")
        if badch != 0:
            print("Sorry, channel num not match")
            raise Exception("Sorry, channel num not match")
        if baddat != 0:
            print("Sorry, data num not match")
            raise Exception("Sorry, data num not match")
        # if data is same: 0 0 0
        print('if data is same:', badpt, badch, baddat)

        # average each data by del pass list, show AVG
        # get pass num list for each data
        print('del_pass_dict:', self.del_pass_dict)
        # del_pass_dict: {'11111111.spc': None, '22222222.spc': None, '33333333.spc': [[1]]}
        avg_list = []
        passnum_list = []
        for name, passes in self.del_pass_dict.items():
            path = self.parent_data_paths[self.parent_data_list.index(name)]
            data = SpcData(path)
            if data.every:
                avg = data.avg_child_part(False, passes)
                # a list of pts, each element is like avg[i] = [(x, ch0), (x, ch1), (x, ch2)]
            else:
                avg = []
                for i in range(data.pt_num):
                    avg.append(data.pt_data[i].pack_data(False))
                    # avg[i] = [(x,I),(x,X1), (x, X2)]
            avg_list.append(avg)
            passNum = []
            for i in range(data.pt_num):
                passNum.append(data.pass_num)
            passnum_list.append(passNum)
        # avg_list: 3 pass num list: [[2], [2], [2]]
        print('avg_list:', len(avg_list), 'pass num list:', passnum_list)

        # data times pass number and pack them up
        # update pass num for each file and each point
        y = np.zeros((chnum, datnum))
        allydata = []
        x = avg_list[0][0][0][0]
        for data, passnum, del_passes, pass_Num in zip(avg_list, passnum_list, self.del_pass_dict.values(), passnum_list):
            ydata = []
            for i in range(ptnum):
                for j in range(chnum):
                    y[j] = data[i][j][1] * (passnum[i] - len(del_passes[i])) if del_passes is not None else data[i][j][1] * passnum[i]
                pass_Num[i] = pass_Num[i] - len(del_passes[i]) if del_passes is not None else pass_Num[i]
                ydata.append(y)
            ydata = np.array(ydata)
            allydata.append(ydata)
        allydata = np.array(allydata)
        # all y data: (file, point, channel, data)
        # all y data: (3, 1, 3, 218) pass num list: [[2], [2], [1]]
        print('all y data:', allydata.shape, 'pass num list:', passnum_list)

        # calculate total pass number, deleted passes are not considered yet
        passnum_list = np.array(passnum_list)
        tot_passnum = np.sum(passnum_list, axis=0)
        # pass num list: [[1], [1], [2]] tot_passnum: [4]
        print('pass num list:', passnum_list, 'tot_passnum:', tot_passnum)


        # divide data by total pass number
        # get result list and name list
        name_list = []
        result_list = []
        for i in range(ptnum):
            name = 'wAVG-Pt#'+str(i+1).zfill(2)
            for j in range(chnum):
                y = np.sum(allydata[:, i, j, :], axis=0)/tot_passnum[i]  # (dat_num, )
                # print('==', np.average(np.sum(allydata[:, i, j, :], axis=0)), np.average(y))
                result_list.append(np.vstack((x, y)))
                text = name+'-Ch'+str(j+1)
                name_list.append(text)

        # name list: ['wAVG-Pt#01-Ch1', 'wAVG-Pt#01-Ch2', 'wAVG-Pt#01-Ch3'] result_list: 3
        # result list: [(x,ch0), (x,ch1), (x,ch2)]
        print('name list:', name_list, 'result_list:', len(result_list))
        return name_list, result_list

    # Emit close signal
    def closeEvent(self, event):
        if len(self.sink_list) > 1:
            try:
                name_list, result_list = self.get_weighted_avg()
            except:
                self.showDialog('Your data are not same, cannot be averaged!')
                return
            else:
                self.close_signal.emit(name_list, result_list)
                event.accept()
        else:
            reply = QMessageBox.warning(None, "Weighted AVG",
                                        'Please select data for further operation. Are you sure to exit?',
                                        QMessageBox.Yes | QMessageBox.No)
            if reply == QMessageBox.Yes:
                event.accept()
            else:
                event.ignore()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = myWeightedAVG()
    import pickle
    with open('./dspfilenames.fname', 'rb') as input:
        names = pickle.load(input)
    with open('./dspfilepaths.fpath', 'rb') as input:
        paths = pickle.load(input)
    window.init_list(names, paths)
    window.show()
    sys.exit(app.exec_())