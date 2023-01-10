# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'PlaneFitWindow.ui'
#
# Created by: PyQt5 UI code generator 5.15.4
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_PlaneFitWindow(object):
    def setupUi(self, PlaneFitWindow):
        PlaneFitWindow.setObjectName("PlaneFitWindow")
        PlaneFitWindow.resize(1258, 479)
        self.gridLayout = QtWidgets.QGridLayout(PlaneFitWindow)
        self.gridLayout.setObjectName("gridLayout")
        self.widget = QtWidgets.QWidget(PlaneFitWindow)
        self.widget.setObjectName("widget")
        self.gridLayout_2 = QtWidgets.QGridLayout(self.widget)
        self.gridLayout_2.setContentsMargins(-1, 11, -1, -1)
        self.gridLayout_2.setVerticalSpacing(6)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.label_3 = QtWidgets.QLabel(self.widget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_3.sizePolicy().hasHeightForWidth())
        self.label_3.setSizePolicy(sizePolicy)
        self.label_3.setMaximumSize(QtCore.QSize(16777215, 16777215))
        font = QtGui.QFont()
        font.setFamily("Yu Gothic UI")
        font.setPointSize(10)
        font.setBold(True)
        font.setItalic(False)
        font.setUnderline(False)
        font.setWeight(75)
        font.setStrikeOut(False)
        font.setKerning(True)
        self.label_3.setFont(font)
        self.label_3.setAlignment(QtCore.Qt.AlignCenter)
        self.label_3.setObjectName("label_3")
        self.gridLayout_2.addWidget(self.label_3, 0, 4, 1, 1)
        self.pushButton_full_left = QtWidgets.QPushButton(self.widget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Maximum, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.pushButton_full_left.sizePolicy().hasHeightForWidth())
        self.pushButton_full_left.setSizePolicy(sizePolicy)
        self.pushButton_full_left.setText("")
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/toolbar/data/fullscreen.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.pushButton_full_left.setIcon(icon)
        self.pushButton_full_left.setFlat(True)
        self.pushButton_full_left.setObjectName("pushButton_full_left")
        self.gridLayout_2.addWidget(self.pushButton_full_left, 0, 1, 1, 1)
        self.pushButton_full_mid = QtWidgets.QPushButton(self.widget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Maximum, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.pushButton_full_mid.sizePolicy().hasHeightForWidth())
        self.pushButton_full_mid.setSizePolicy(sizePolicy)
        self.pushButton_full_mid.setText("")
        self.pushButton_full_mid.setIcon(icon)
        self.pushButton_full_mid.setFlat(True)
        self.pushButton_full_mid.setObjectName("pushButton_full_mid")
        self.gridLayout_2.addWidget(self.pushButton_full_mid, 0, 3, 1, 1)
        self.label_2 = QtWidgets.QLabel(self.widget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_2.sizePolicy().hasHeightForWidth())
        self.label_2.setSizePolicy(sizePolicy)
        self.label_2.setMaximumSize(QtCore.QSize(16777215, 16777215))
        font = QtGui.QFont()
        font.setFamily("Yu Gothic UI")
        font.setPointSize(10)
        font.setBold(True)
        font.setItalic(False)
        font.setUnderline(False)
        font.setWeight(75)
        font.setStrikeOut(False)
        font.setKerning(True)
        self.label_2.setFont(font)
        self.label_2.setAlignment(QtCore.Qt.AlignCenter)
        self.label_2.setObjectName("label_2")
        self.gridLayout_2.addWidget(self.label_2, 0, 2, 1, 1)
        self.label = QtWidgets.QLabel(self.widget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label.sizePolicy().hasHeightForWidth())
        self.label.setSizePolicy(sizePolicy)
        self.label.setMaximumSize(QtCore.QSize(16777215, 16777215))
        font = QtGui.QFont()
        font.setFamily("Yu Gothic UI")
        font.setPointSize(10)
        font.setBold(True)
        font.setItalic(False)
        font.setUnderline(False)
        font.setWeight(75)
        font.setStrikeOut(False)
        font.setKerning(True)
        self.label.setFont(font)
        self.label.setAlignment(QtCore.Qt.AlignCenter)
        self.label.setObjectName("label")
        self.gridLayout_2.addWidget(self.label, 0, 0, 1, 1)
        self.pushButton_full_right = QtWidgets.QPushButton(self.widget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Maximum, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.pushButton_full_right.sizePolicy().hasHeightForWidth())
        self.pushButton_full_right.setSizePolicy(sizePolicy)
        self.pushButton_full_right.setText("")
        self.pushButton_full_right.setIcon(icon)
        self.pushButton_full_right.setFlat(True)
        self.pushButton_full_right.setObjectName("pushButton_full_right")
        self.gridLayout_2.addWidget(self.pushButton_full_right, 0, 5, 1, 1)
        self.graphicsView_left = GraphicsLayoutWidget(self.widget)
        self.graphicsView_left.setMinimumSize(QtCore.QSize(400, 400))
        self.graphicsView_left.setMaximumSize(QtCore.QSize(400, 400))
        self.graphicsView_left.setObjectName("graphicsView_left")
        self.gridLayout_2.addWidget(self.graphicsView_left, 1, 0, 1, 2)
        self.graphicsView_mid = GraphicsLayoutWidget(self.widget)
        self.graphicsView_mid.setMinimumSize(QtCore.QSize(400, 400))
        self.graphicsView_mid.setMaximumSize(QtCore.QSize(400, 400))
        self.graphicsView_mid.setObjectName("graphicsView_mid")
        self.gridLayout_2.addWidget(self.graphicsView_mid, 1, 2, 1, 2)
        self.graphicsView_right = GraphicsLayoutWidget(self.widget)
        self.graphicsView_right.setMinimumSize(QtCore.QSize(400, 400))
        self.graphicsView_right.setMaximumSize(QtCore.QSize(400, 400))
        self.graphicsView_right.setObjectName("graphicsView_right")
        self.gridLayout_2.addWidget(self.graphicsView_right, 1, 4, 1, 2)
        self.gridLayout.addWidget(self.widget, 0, 0, 1, 1)

        self.retranslateUi(PlaneFitWindow)
        QtCore.QMetaObject.connectSlotsByName(PlaneFitWindow)

    def retranslateUi(self, PlaneFitWindow):
        _translate = QtCore.QCoreApplication.translate
        PlaneFitWindow.setWindowTitle(_translate("PlaneFitWindow", "Plane fit"))
        self.label_3.setText(_translate("PlaneFitWindow", "Basic plane fit"))
        self.label_2.setText(_translate("PlaneFitWindow", "Four-point plane fit"))
        self.label.setText(_translate("PlaneFitWindow", "Raw"))
from pyqtgraph import GraphicsLayoutWidget
import logo_rc
