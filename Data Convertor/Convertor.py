# -*- coding: utf-8 -*-
"""
@Date     : 1/8/2023 20:41:06
@Author   : milier00
@FileName : Convertor.py
"""
import sys
from PyQt5.QtWidgets import QMessageBox, QApplication, QFileDialog, QWidget
from convertor_ui import Ui_DataConvertor
import os
import numpy as np
import pickle
import ctypes
import copy

class myDataConvertor(Ui_DataConvertor, QWidget):

    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.init_UI()
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("myappid")

    def init_UI(self):
        self.source_path_nstm = None
        self.source_path_spc = None
        self.sink_path_nstm = None
        self.sink_path_spc = None

        self.pushButton_source_nstm.clicked.connect(lambda: self.open_old(0))
        self.pushButton_source_spc.clicked.connect(lambda: self.open_old(1))

        self.pushButton_sink_nstm.clicked.connect(lambda: self.open_new(0))
        self.pushButton_sink_spc.clicked.connect(lambda: self.open_new(1))

        self.pushButton_do_nstm.clicked.connect(lambda: self.do_convert(0))
        self.pushButton_do_spc.clicked.connect(lambda: self.do_convert(1))

    def open_old(self, index):
        if index == 0:
            self.source_path_nstm = QFileDialog.getExistingDirectory(self, "Select path", "./")
            self.lineEdit_source_nstm.setText(self.source_path_nstm)
            print('source_path_nstm:', self.source_path_nstm)
        elif index == 1:
            aFile, filt = QFileDialog.getOpenFileName(self, "Slect file", "./", "EXP(*.exp);;TXT(*.txt);;DAT(*.dat)")
            self.source_path_spc = aFile
            self.lineEdit_source_spc.setText(self.source_path_spc)
            print('source_path_spc:',self.source_path_spc)

    def open_new(self, index):
        if index == 0:
            self.sink_path_nstm = QFileDialog.getExistingDirectory(self, "Select path", "./")
            self.lineEdit_sink_nstm.setText(self.sink_path_nstm)
            print('sink_path_nstm:', self.sink_path_nstm)
        elif index == 1:
            self.sink_path_spc = QFileDialog.getExistingDirectory(self, "Select path", "./")
            self.lineEdit_sink_spc.setText(self.sink_path_spc)
            print('sink_path_spc:', self.sink_path_spc)

    def do_convert(self, index):

        if index == 0:

            if self.source_path_nstm == None or self.sink_path_nstm == None:
                QMessageBox.warning(self, "Data convertor", 'Select paths first!', QMessageBox.Ok)
                return
            else:
                data_list = []
                for root, dirs, files in os.walk(self.source_path_nstm, topdown=False):
                    for file in files:
                        if len(file) == 8:
                            print(file)

                            try:
                                data_path = os.path.join(root, file)
                                data_list.append(file)
                                img = np.flipud(np.loadtxt(data_path)).T[np.newaxis, :, :]
                                print(img.shape)
                                # open a dummy .nstm file as a model
                                with open("./11102208.nstm", 'rb') as input:
                                    fake_sample = pickle.load(input)
                                fake_sample.name = file
                                fake_sample.path = data_path
                                fake_sample.step_num = img.shape[1]
                                fake_sample.step_size = img.shape[2]
                                fake_sample.data = copy.deepcopy(img)
                                # where to save the converted .nstm, change it to your path
                                with open(self.sink_path_nstm+'/' + file + '.nstm', 'wb') as output:
                                    pickle.dump(fake_sample, output, pickle.HIGHEST_PROTOCOL)  # Save data
                            except:
                                continue


                self.listWidget_nstm.addItems(data_list)

        elif index == 1:

            if self.source_path_spc == None or self.sink_path_spc == None:
                QMessageBox.warning(self, "Data convertor", 'Select paths first!', QMessageBox.Ok)
                return
            else:
                dir_path, file = os.path.split(self.source_path_spc)
                file_list = []
                for root, dirs, files in os.walk(dir_path, topdown=False):
                    for file in files:
                        if len(file) == 12:
                            data_path = root + '/' + file
                            file_list.append(data_path)
                file_list = sorted(file_list)
                print(file_list)

                index = file_list.index(self.source_path_spc)
                file_name = os.path.split(file_list[index])[1][:-4]

                ivf = np.loadtxt(file_list[index], skiprows=1)
                didvf = np.loadtxt(file_list[index + 1], skiprows=1)
                ietsf = np.loadtxt(file_list[index + 2], skiprows=1)
                ivb = np.loadtxt(file_list[index + 3], skiprows=1)
                didvb = np.loadtxt(file_list[index + 4], skiprows=1)
                ietsb = np.loadtxt(file_list[index + 5], skiprows=1)

                bias = ivf[:, 0]

                data = np.vstack((bias, ivf[:, 1]));
                data = np.vstack((data, didvf[:, 1]));
                data = np.vstack((data, ietsf[:, 1]));
                data = np.vstack((data, ivb[:, 1]));
                data = np.vstack((data, didvb[:, 1]));
                data = np.vstack((data, ietsb[:, 1]));
                data = data[np.newaxis, :, :]
                print(data.shape)

                # open a dummy .nstm file as a model
                with open('./1104220f.spc', 'rb') as input:
                    dummy = pickle.load(input)
                dummy.name = file_name
                dummy.path = file_list[index]
                dummy.dir = dir_path
                dummy.ischild = False
                dummy.data = data
                dummy.pass_num = 0
                dummy.scan_dir = 2

                # write .spc file
                with open(self.sink_path_spc + '/' + file_name + '.spc', 'wb') as output:
                    pickle.dump(dummy, output, pickle.HIGHEST_PROTOCOL)  # Save data

                data_list = []
                for i in range(6):
                    _, name = os.path.split(file_list[index+i])
                    data_list.append(name)
                self.listWidget_spc.addItems(data_list)



if __name__ == "__main__":
    # create the application and the main window
    app = QApplication(sys.argv)
    window = myDataConvertor()
    app.setStyle("Fusion")
    window.show()
    sys.exit(app.exec_())
