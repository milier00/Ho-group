# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'DataAnalysis.ui'
#
# Created by: PyQt5 UI code generator 5.15.1
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets
import pyqtgraph as pg

class Ui_DataAnalysis(object):
    def setupUi(self, DataAnalysis):
        pg.setConfigOption('background', (240, 240, 240, 255))
        pg.setConfigOption('foreground', 'k')
        DataAnalysis.setObjectName("DataAnalysis")
        DataAnalysis.resize(922, 417)
        DataAnalysis.setMinimumSize(QtCore.QSize(0, 0))
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/menuIcon/data/pack_1.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        DataAnalysis.setWindowIcon(icon)
        self.graphicsLayoutWidget = GraphicsLayoutWidget(DataAnalysis)
        self.graphicsLayoutWidget.setGeometry(QtCore.QRect(11, 11, 256, 192))
        self.graphicsLayoutWidget.setMinimumSize(QtCore.QSize(0, 0))
        self.graphicsLayoutWidget.setObjectName("graphicsLayoutWidget")

        self.retranslateUi(DataAnalysis)
        QtCore.QMetaObject.connectSlotsByName(DataAnalysis)

    def retranslateUi(self, DataAnalysis):
        _translate = QtCore.QCoreApplication.translate
        DataAnalysis.setWindowTitle(_translate("DataAnalysis", "Data Analysis"))
from pyqtgraph import GraphicsLayoutWidget
import logo_rc
