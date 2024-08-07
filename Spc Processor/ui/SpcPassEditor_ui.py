# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'SpcPassEditor.ui'
#
# Created by: PyQt5 UI code generator 5.15.4
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_SpcPassEditor(object):
    def setupUi(self, SpcPassEditor):
        SpcPassEditor.setObjectName("SpcPassEditor")
        SpcPassEditor.resize(935, 590)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/menuIcon/data/shark_and_lollipop_2.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        SpcPassEditor.setWindowIcon(icon)
        self.gridLayout_4 = QtWidgets.QGridLayout(SpcPassEditor)
        self.gridLayout_4.setObjectName("gridLayout_4")
        self.groupBox = QtWidgets.QGroupBox(SpcPassEditor)
        font = QtGui.QFont()
        font.setPointSize(10)
        self.groupBox.setFont(font)
        self.groupBox.setObjectName("groupBox")
        self.gridLayout = QtWidgets.QGridLayout(self.groupBox)
        self.gridLayout.setObjectName("gridLayout")
        self.listWidget = QtWidgets.QListWidget(self.groupBox)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.listWidget.sizePolicy().hasHeightForWidth())
        self.listWidget.setSizePolicy(sizePolicy)
        self.listWidget.setMinimumSize(QtCore.QSize(300, 0))
        self.listWidget.setMaximumSize(QtCore.QSize(500, 16777215))
        self.listWidget.setObjectName("listWidget")
        self.gridLayout.addWidget(self.listWidget, 0, 0, 1, 1)
        self.gridLayout_4.addWidget(self.groupBox, 0, 0, 1, 1)
        self.widget = QtWidgets.QWidget(SpcPassEditor)
        self.widget.setObjectName("widget")
        self.gridLayout_2 = QtWidgets.QGridLayout(self.widget)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.widget_plot = QtWidgets.QWidget(self.widget)
        self.widget_plot.setObjectName("widget_plot")
        self.label_ptnum = QtWidgets.QLabel(self.widget_plot)
        self.label_ptnum.setGeometry(QtCore.QRect(11, 11, 34, 21))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.label_ptnum.setFont(font)
        self.label_ptnum.setObjectName("label_ptnum")
        self.label_num = QtWidgets.QLabel(self.widget_plot)
        self.label_num.setGeometry(QtCore.QRect(206, 11, 188, 33))
        self.label_num.setText("")
        self.label_num.setObjectName("label_num")
        self.scrollBar_ptnum = QtWidgets.QScrollBar(self.widget_plot)
        self.scrollBar_ptnum.setGeometry(QtCore.QRect(401, 17, 64, 21))
        self.scrollBar_ptnum.setOrientation(QtCore.Qt.Horizontal)
        self.scrollBar_ptnum.setObjectName("scrollBar_ptnum")
        self.gridLayout_2.addWidget(self.widget_plot, 0, 0, 1, 1)
        self.graphicsView = GraphicsLayoutWidget(self.widget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.graphicsView.sizePolicy().hasHeightForWidth())
        self.graphicsView.setSizePolicy(sizePolicy)
        self.graphicsView.setMinimumSize(QtCore.QSize(400, 400))
        self.graphicsView.setObjectName("graphicsView")
        self.gridLayout_2.addWidget(self.graphicsView, 1, 0, 1, 1)
        self.gridLayout_4.addWidget(self.widget, 0, 1, 3, 1)
        self.widget_2 = QtWidgets.QWidget(SpcPassEditor)
        self.widget_2.setObjectName("widget_2")
        self.gridLayout_5 = QtWidgets.QGridLayout(self.widget_2)
        self.gridLayout_5.setObjectName("gridLayout_5")
        self.pushButton_Scanner = QtWidgets.QPushButton(self.widget_2)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Maximum, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.pushButton_Scanner.sizePolicy().hasHeightForWidth())
        self.pushButton_Scanner.setSizePolicy(sizePolicy)
        self.pushButton_Scanner.setText("")
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap(":/toolbar/data/scanner.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.pushButton_Scanner.setIcon(icon1)
        self.pushButton_Scanner.setCheckable(True)
        self.pushButton_Scanner.setFlat(True)
        self.pushButton_Scanner.setObjectName("pushButton_Scanner")
        self.gridLayout_5.addWidget(self.pushButton_Scanner, 0, 4, 1, 1)
        self.pushButton_All1 = QtWidgets.QPushButton(self.widget_2)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Maximum, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.pushButton_All1.sizePolicy().hasHeightForWidth())
        self.pushButton_All1.setSizePolicy(sizePolicy)
        self.pushButton_All1.setText("")
        icon2 = QtGui.QIcon()
        icon2.addPixmap(QtGui.QPixmap(":/toolbar/data/All_.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.pushButton_All1.setIcon(icon2)
        self.pushButton_All1.setCheckable(True)
        self.pushButton_All1.setChecked(True)
        self.pushButton_All1.setFlat(True)
        self.pushButton_All1.setObjectName("pushButton_All1")
        self.gridLayout_5.addWidget(self.pushButton_All1, 0, 1, 1, 1)
        self.pushButton_yScale = QtWidgets.QPushButton(self.widget_2)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Maximum, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.pushButton_yScale.sizePolicy().hasHeightForWidth())
        self.pushButton_yScale.setSizePolicy(sizePolicy)
        self.pushButton_yScale.setText("")
        icon3 = QtGui.QIcon()
        icon3.addPixmap(QtGui.QPixmap(":/toolbar/data/up_down.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.pushButton_yScale.setIcon(icon3)
        self.pushButton_yScale.setFlat(True)
        self.pushButton_yScale.setObjectName("pushButton_yScale")
        self.gridLayout_5.addWidget(self.pushButton_yScale, 0, 6, 1, 1)
        self.pushButton_Avg = QtWidgets.QPushButton(self.widget_2)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Maximum, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.pushButton_Avg.sizePolicy().hasHeightForWidth())
        self.pushButton_Avg.setSizePolicy(sizePolicy)
        self.pushButton_Avg.setText("")
        icon4 = QtGui.QIcon()
        icon4.addPixmap(QtGui.QPixmap(":/toolbar/data/AVG.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.pushButton_Avg.setIcon(icon4)
        self.pushButton_Avg.setCheckable(True)
        self.pushButton_Avg.setFlat(True)
        self.pushButton_Avg.setObjectName("pushButton_Avg")
        self.gridLayout_5.addWidget(self.pushButton_Avg, 0, 0, 1, 1)
        self.pushButton_check = QtWidgets.QPushButton(self.widget_2)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Maximum, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.pushButton_check.sizePolicy().hasHeightForWidth())
        self.pushButton_check.setSizePolicy(sizePolicy)
        self.pushButton_check.setText("")
        icon5 = QtGui.QIcon()
        icon5.addPixmap(QtGui.QPixmap(":/toolbar/data/cansee.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.pushButton_check.setIcon(icon5)
        self.pushButton_check.setCheckable(False)
        self.pushButton_check.setFlat(True)
        self.pushButton_check.setObjectName("pushButton_check")
        self.gridLayout_5.addWidget(self.pushButton_check, 0, 2, 1, 1)
        self.pushButton_xScale = QtWidgets.QPushButton(self.widget_2)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Maximum, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.pushButton_xScale.sizePolicy().hasHeightForWidth())
        self.pushButton_xScale.setSizePolicy(sizePolicy)
        self.pushButton_xScale.setText("")
        icon6 = QtGui.QIcon()
        icon6.addPixmap(QtGui.QPixmap(":/toolbar/data/left_right.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.pushButton_xScale.setIcon(icon6)
        self.pushButton_xScale.setFlat(True)
        self.pushButton_xScale.setObjectName("pushButton_xScale")
        self.gridLayout_5.addWidget(self.pushButton_xScale, 0, 5, 1, 1)
        self.pushButton_uncheck = QtWidgets.QPushButton(self.widget_2)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Maximum, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.pushButton_uncheck.sizePolicy().hasHeightForWidth())
        self.pushButton_uncheck.setSizePolicy(sizePolicy)
        self.pushButton_uncheck.setText("")
        icon7 = QtGui.QIcon()
        icon7.addPixmap(QtGui.QPixmap(":/toolbar/data/cannotsee.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.pushButton_uncheck.setIcon(icon7)
        self.pushButton_uncheck.setCheckable(False)
        self.pushButton_uncheck.setFlat(True)
        self.pushButton_uncheck.setObjectName("pushButton_uncheck")
        self.gridLayout_5.addWidget(self.pushButton_uncheck, 0, 3, 1, 1)
        self.gridLayout_4.addWidget(self.widget_2, 2, 0, 1, 1)
        self.widget_3 = QtWidgets.QWidget(SpcPassEditor)
        self.widget_3.setObjectName("widget_3")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.widget_3)
        self.horizontalLayout.setContentsMargins(-1, 0, -1, 0)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.label = QtWidgets.QLabel(self.widget_3)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Maximum, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label.sizePolicy().hasHeightForWidth())
        self.label.setSizePolicy(sizePolicy)
        self.label.setObjectName("label")
        self.horizontalLayout.addWidget(self.label)
        self.label_delPass = QtWidgets.QLabel(self.widget_3)
        self.label_delPass.setText("")
        self.label_delPass.setObjectName("label_delPass")
        self.horizontalLayout.addWidget(self.label_delPass)
        self.gridLayout_4.addWidget(self.widget_3, 1, 0, 1, 1)

        self.retranslateUi(SpcPassEditor)
        QtCore.QMetaObject.connectSlotsByName(SpcPassEditor)

    def retranslateUi(self, SpcPassEditor):
        _translate = QtCore.QCoreApplication.translate
        SpcPassEditor.setWindowTitle(_translate("SpcPassEditor", "Spc Pass Editor"))
        self.groupBox.setTitle(_translate("SpcPassEditor", "GroupBox"))
        self.label_ptnum.setText(_translate("SpcPassEditor", "Pt#:"))
        self.pushButton_Scanner.setToolTip(_translate("SpcPassEditor", "Show/Hide scanner"))
        self.pushButton_All1.setToolTip(_translate("SpcPassEditor", "Check/Uncheck all"))
        self.pushButton_yScale.setToolTip(_translate("SpcPassEditor", "Auto-scale y"))
        self.pushButton_Avg.setToolTip(_translate("SpcPassEditor", "Average by selected passes"))
        self.pushButton_check.setToolTip(_translate("SpcPassEditor", "Check selected"))
        self.pushButton_xScale.setToolTip(_translate("SpcPassEditor", "Auto-scale x"))
        self.pushButton_uncheck.setToolTip(_translate("SpcPassEditor", "Uncheck selected"))
        self.label.setText(_translate("SpcPassEditor", "Deleted passes:"))
from pyqtgraph import GraphicsLayoutWidget
import logo_rc
