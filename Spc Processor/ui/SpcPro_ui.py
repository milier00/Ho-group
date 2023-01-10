# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'SpcPro.ui'
#
# Created by: PyQt5 UI code generator 5.15.4
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_SpcPro(object):
    def setupUi(self, SpcPro):
        SpcPro.setObjectName("SpcPro")
        SpcPro.resize(532, 586)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/menuIcon/data/ducky.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        SpcPro.setWindowIcon(icon)
        self.centralwidget = QtWidgets.QWidget(SpcPro)
        self.centralwidget.setObjectName("centralwidget")
        self.gridLayout_12 = QtWidgets.QGridLayout(self.centralwidget)
        self.gridLayout_12.setObjectName("gridLayout_12")
        self.groupBox = QtWidgets.QGroupBox(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.groupBox.sizePolicy().hasHeightForWidth())
        self.groupBox.setSizePolicy(sizePolicy)
        self.groupBox.setMinimumSize(QtCore.QSize(0, 0))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.groupBox.setFont(font)
        self.groupBox.setObjectName("groupBox")
        self.gridLayout = QtWidgets.QGridLayout(self.groupBox)
        self.gridLayout.setObjectName("gridLayout")
        self.pushButton_Next = QtWidgets.QPushButton(self.groupBox)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Maximum, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.pushButton_Next.sizePolicy().hasHeightForWidth())
        self.pushButton_Next.setSizePolicy(sizePolicy)
        self.pushButton_Next.setText("")
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap(":/toolbar/data/right.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.pushButton_Next.setIcon(icon1)
        self.pushButton_Next.setFlat(True)
        self.pushButton_Next.setObjectName("pushButton_Next")
        self.gridLayout.addWidget(self.pushButton_Next, 2, 3, 1, 1)
        self.pushButton_Open = QtWidgets.QPushButton(self.groupBox)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Maximum, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.pushButton_Open.sizePolicy().hasHeightForWidth())
        self.pushButton_Open.setSizePolicy(sizePolicy)
        self.pushButton_Open.setText("")
        icon2 = QtGui.QIcon()
        icon2.addPixmap(QtGui.QPixmap(":/toolbar/data/open.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.pushButton_Open.setIcon(icon2)
        self.pushButton_Open.setFlat(True)
        self.pushButton_Open.setObjectName("pushButton_Open")
        self.gridLayout.addWidget(self.pushButton_Open, 0, 3, 1, 1)
        self.pushButton_Previous = QtWidgets.QPushButton(self.groupBox)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Maximum, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.pushButton_Previous.sizePolicy().hasHeightForWidth())
        self.pushButton_Previous.setSizePolicy(sizePolicy)
        self.pushButton_Previous.setText("")
        icon3 = QtGui.QIcon()
        icon3.addPixmap(QtGui.QPixmap(":/toolbar/data/left.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.pushButton_Previous.setIcon(icon3)
        self.pushButton_Previous.setFlat(True)
        self.pushButton_Previous.setObjectName("pushButton_Previous")
        self.gridLayout.addWidget(self.pushButton_Previous, 2, 2, 1, 1)
        self.lineEdit = QtWidgets.QLineEdit(self.groupBox)
        self.lineEdit.setObjectName("lineEdit")
        self.gridLayout.addWidget(self.lineEdit, 0, 0, 1, 3)
        self.listWidget = QtWidgets.QListWidget(self.groupBox)
        self.listWidget.setMinimumSize(QtCore.QSize(0, 0))
        self.listWidget.setObjectName("listWidget")
        self.gridLayout.addWidget(self.listWidget, 4, 0, 1, 4)
        self.pushButton_Refresh = QtWidgets.QPushButton(self.groupBox)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Maximum, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.pushButton_Refresh.sizePolicy().hasHeightForWidth())
        self.pushButton_Refresh.setSizePolicy(sizePolicy)
        self.pushButton_Refresh.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.pushButton_Refresh.setText("")
        icon4 = QtGui.QIcon()
        icon4.addPixmap(QtGui.QPixmap(":/toolbar/data/Reset.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.pushButton_Refresh.setIcon(icon4)
        self.pushButton_Refresh.setFlat(True)
        self.pushButton_Refresh.setObjectName("pushButton_Refresh")
        self.gridLayout.addWidget(self.pushButton_Refresh, 2, 1, 1, 1)
        self.gridLayout_12.addWidget(self.groupBox, 0, 0, 1, 1)
        SpcPro.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(SpcPro)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 532, 26))
        self.menubar.setObjectName("menubar")
        SpcPro.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(SpcPro)
        self.statusbar.setObjectName("statusbar")
        SpcPro.setStatusBar(self.statusbar)
        self.dockWidget_AG = QtWidgets.QDockWidget(SpcPro)
        self.dockWidget_AG.setObjectName("dockWidget_AG")
        self.dockWidgetContents_2 = QtWidgets.QWidget()
        self.dockWidgetContents_2.setObjectName("dockWidgetContents_2")
        self.gridLayout_4 = QtWidgets.QGridLayout(self.dockWidgetContents_2)
        self.gridLayout_4.setObjectName("gridLayout_4")
        self.pushButton_do_algebra = QtWidgets.QPushButton(self.dockWidgetContents_2)
        self.pushButton_do_algebra.setObjectName("pushButton_do_algebra")
        self.gridLayout_4.addWidget(self.pushButton_do_algebra, 1, 0, 1, 1)
        self.groupBox_2 = QtWidgets.QGroupBox(self.dockWidgetContents_2)
        self.groupBox_2.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)
        self.groupBox_2.setObjectName("groupBox_2")
        self.gridLayout_3 = QtWidgets.QGridLayout(self.groupBox_2)
        self.gridLayout_3.setObjectName("gridLayout_3")
        self.comboBox_algebra = QtWidgets.QComboBox(self.groupBox_2)
        self.comboBox_algebra.setSizeAdjustPolicy(QtWidgets.QComboBox.AdjustToContents)
        self.comboBox_algebra.setObjectName("comboBox_algebra")
        self.comboBox_algebra.addItem("")
        self.comboBox_algebra.addItem("")
        self.comboBox_algebra.addItem("")
        self.comboBox_algebra.addItem("")
        self.comboBox_algebra.addItem("")
        self.comboBox_algebra.addItem("")
        self.comboBox_algebra.addItem("")
        self.comboBox_algebra.addItem("")
        self.gridLayout_3.addWidget(self.comboBox_algebra, 0, 0, 1, 1)
        self.lineEdit_algebra = QtWidgets.QLineEdit(self.groupBox_2)
        self.lineEdit_algebra.setObjectName("lineEdit_algebra")
        self.gridLayout_3.addWidget(self.lineEdit_algebra, 1, 0, 1, 1)
        self.gridLayout_4.addWidget(self.groupBox_2, 0, 0, 1, 1)
        self.pushButton_Adv_algebra = QtWidgets.QPushButton(self.dockWidgetContents_2)
        self.pushButton_Adv_algebra.setObjectName("pushButton_Adv_algebra")
        self.gridLayout_4.addWidget(self.pushButton_Adv_algebra, 2, 0, 1, 1)
        self.dockWidget_AG.setWidget(self.dockWidgetContents_2)
        SpcPro.addDockWidget(QtCore.Qt.DockWidgetArea(1), self.dockWidget_AG)
        self.dockWidgetSC = QtWidgets.QDockWidget(SpcPro)
        self.dockWidgetSC.setObjectName("dockWidgetSC")
        self.dockWidgetContents_3 = QtWidgets.QWidget()
        self.dockWidgetContents_3.setObjectName("dockWidgetContents_3")
        self.gridLayout_5 = QtWidgets.QGridLayout(self.dockWidgetContents_3)
        self.gridLayout_5.setObjectName("gridLayout_5")
        self.pushButton_do_SC = QtWidgets.QPushButton(self.dockWidgetContents_3)
        self.pushButton_do_SC.setObjectName("pushButton_do_SC")
        self.gridLayout_5.addWidget(self.pushButton_do_SC, 0, 0, 1, 1)
        self.dockWidgetSC.setWidget(self.dockWidgetContents_3)
        SpcPro.addDockWidget(QtCore.Qt.DockWidgetArea(2), self.dockWidgetSC)
        self.dockWidget_BP = QtWidgets.QDockWidget(SpcPro)
        self.dockWidget_BP.setObjectName("dockWidget_BP")
        self.dockWidgetContents_4 = QtWidgets.QWidget()
        self.dockWidgetContents_4.setObjectName("dockWidgetContents_4")
        self.gridLayout_7 = QtWidgets.QGridLayout(self.dockWidgetContents_4)
        self.gridLayout_7.setObjectName("gridLayout_7")
        self.groupBox_5 = QtWidgets.QGroupBox(self.dockWidgetContents_4)
        self.groupBox_5.setObjectName("groupBox_5")
        self.gridLayout_9 = QtWidgets.QGridLayout(self.groupBox_5)
        self.gridLayout_9.setObjectName("gridLayout_9")
        self.pushButton_weightedAVG = QtWidgets.QPushButton(self.groupBox_5)
        self.pushButton_weightedAVG.setObjectName("pushButton_weightedAVG")
        self.gridLayout_9.addWidget(self.pushButton_weightedAVG, 0, 0, 1, 1)
        self.gridLayout_7.addWidget(self.groupBox_5, 1, 0, 1, 1)
        self.groupBox_4 = QtWidgets.QGroupBox(self.dockWidgetContents_4)
        self.groupBox_4.setObjectName("groupBox_4")
        self.gridLayout_8 = QtWidgets.QGridLayout(self.groupBox_4)
        self.gridLayout_8.setObjectName("gridLayout_8")
        self.pushButton_fft = QtWidgets.QPushButton(self.groupBox_4)
        self.pushButton_fft.setObjectName("pushButton_fft")
        self.gridLayout_8.addWidget(self.pushButton_fft, 0, 0, 2, 2)
        self.pushButton_ifft = QtWidgets.QPushButton(self.groupBox_4)
        self.pushButton_ifft.setEnabled(False)
        self.pushButton_ifft.setObjectName("pushButton_ifft")
        self.gridLayout_8.addWidget(self.pushButton_ifft, 2, 0, 1, 2)
        self.gridLayout_7.addWidget(self.groupBox_4, 2, 0, 1, 1)
        self.groupBox_3 = QtWidgets.QGroupBox(self.dockWidgetContents_4)
        self.groupBox_3.setObjectName("groupBox_3")
        self.gridLayout_6 = QtWidgets.QGridLayout(self.groupBox_3)
        self.gridLayout_6.setObjectName("gridLayout_6")
        self.pushButton_Copy = QtWidgets.QPushButton(self.groupBox_3)
        self.pushButton_Copy.setObjectName("pushButton_Copy")
        self.gridLayout_6.addWidget(self.pushButton_Copy, 0, 0, 1, 1)
        self.gridLayout_7.addWidget(self.groupBox_3, 0, 0, 1, 1)
        self.dockWidget_BP.setWidget(self.dockWidgetContents_4)
        SpcPro.addDockWidget(QtCore.Qt.DockWidgetArea(1), self.dockWidget_BP)
        self.dockWidget_AP = QtWidgets.QDockWidget(SpcPro)
        self.dockWidget_AP.setObjectName("dockWidget_AP")
        self.dockWidgetContents_5 = QtWidgets.QWidget()
        self.dockWidgetContents_5.setObjectName("dockWidgetContents_5")
        self.gridLayout_11 = QtWidgets.QGridLayout(self.dockWidgetContents_5)
        self.gridLayout_11.setObjectName("gridLayout_11")
        self.groupBox_6 = QtWidgets.QGroupBox(self.dockWidgetContents_5)
        self.groupBox_6.setObjectName("groupBox_6")
        self.gridLayout_10 = QtWidgets.QGridLayout(self.groupBox_6)
        self.gridLayout_10.setObjectName("gridLayout_10")
        self.label_2 = QtWidgets.QLabel(self.groupBox_6)
        self.label_2.setObjectName("label_2")
        self.gridLayout_10.addWidget(self.label_2, 2, 0, 1, 1)
        self.label = QtWidgets.QLabel(self.groupBox_6)
        self.label.setObjectName("label")
        self.gridLayout_10.addWidget(self.label, 1, 0, 1, 1)
        self.comboBox_filter = QtWidgets.QComboBox(self.groupBox_6)
        self.comboBox_filter.setObjectName("comboBox_filter")
        self.comboBox_filter.addItem("")
        self.comboBox_filter.addItem("")
        self.comboBox_filter.addItem("")
        self.gridLayout_10.addWidget(self.comboBox_filter, 0, 0, 1, 2)
        self.spinBox_highfreq_filter = QtWidgets.QDoubleSpinBox(self.groupBox_6)
        self.spinBox_highfreq_filter.setObjectName("spinBox_highfreq_filter")
        self.gridLayout_10.addWidget(self.spinBox_highfreq_filter, 2, 1, 1, 1)
        self.spinBox_lowfreq_filter = QtWidgets.QDoubleSpinBox(self.groupBox_6)
        self.spinBox_lowfreq_filter.setObjectName("spinBox_lowfreq_filter")
        self.gridLayout_10.addWidget(self.spinBox_lowfreq_filter, 1, 1, 1, 1)
        self.pushButton_do_filter = QtWidgets.QPushButton(self.groupBox_6)
        self.pushButton_do_filter.setObjectName("pushButton_do_filter")
        self.gridLayout_10.addWidget(self.pushButton_do_filter, 3, 0, 1, 2)
        self.gridLayout_11.addWidget(self.groupBox_6, 0, 0, 1, 1)
        self.groupBox_7 = QtWidgets.QGroupBox(self.dockWidgetContents_5)
        self.groupBox_7.setObjectName("groupBox_7")
        self.gridLayout_13 = QtWidgets.QGridLayout(self.groupBox_7)
        self.gridLayout_13.setObjectName("gridLayout_13")
        self.label_3 = QtWidgets.QLabel(self.groupBox_7)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Maximum, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_3.sizePolicy().hasHeightForWidth())
        self.label_3.setSizePolicy(sizePolicy)
        self.label_3.setObjectName("label_3")
        self.gridLayout_13.addWidget(self.label_3, 2, 0, 1, 1)
        self.spinBox_smooth = QtWidgets.QSpinBox(self.groupBox_7)
        self.spinBox_smooth.setProperty("value", 20)
        self.spinBox_smooth.setObjectName("spinBox_smooth")
        self.gridLayout_13.addWidget(self.spinBox_smooth, 2, 1, 1, 1)
        self.pushButton_do_smooth = QtWidgets.QPushButton(self.groupBox_7)
        self.pushButton_do_smooth.setObjectName("pushButton_do_smooth")
        self.gridLayout_13.addWidget(self.pushButton_do_smooth, 3, 0, 1, 2)
        self.comboBox_smooth = QtWidgets.QComboBox(self.groupBox_7)
        self.comboBox_smooth.setObjectName("comboBox_smooth")
        self.comboBox_smooth.addItem("")
        self.comboBox_smooth.addItem("")
        self.comboBox_smooth.addItem("")
        self.comboBox_smooth.addItem("")
        self.gridLayout_13.addWidget(self.comboBox_smooth, 0, 0, 1, 2)
        self.gridLayout_11.addWidget(self.groupBox_7, 1, 0, 1, 1)
        self.dockWidget_AP.setWidget(self.dockWidgetContents_5)
        SpcPro.addDockWidget(QtCore.Qt.DockWidgetArea(2), self.dockWidget_AP)
        self.dockWidget_PL = QtWidgets.QDockWidget(SpcPro)
        self.dockWidget_PL.setObjectName("dockWidget_PL")
        self.dockWidgetContents_6 = QtWidgets.QWidget()
        self.dockWidgetContents_6.setObjectName("dockWidgetContents_6")
        self.gridLayout_14 = QtWidgets.QGridLayout(self.dockWidgetContents_6)
        self.gridLayout_14.setObjectName("gridLayout_14")
        self.pushButton_do_plot = QtWidgets.QPushButton(self.dockWidgetContents_6)
        self.pushButton_do_plot.setObjectName("pushButton_do_plot")
        self.gridLayout_14.addWidget(self.pushButton_do_plot, 0, 0, 1, 1)
        self.pushButton_do_draw = QtWidgets.QPushButton(self.dockWidgetContents_6)
        self.pushButton_do_draw.setObjectName("pushButton_do_draw")
        self.gridLayout_14.addWidget(self.pushButton_do_draw, 1, 0, 1, 1)
        self.dockWidget_PL.setWidget(self.dockWidgetContents_6)
        SpcPro.addDockWidget(QtCore.Qt.DockWidgetArea(2), self.dockWidget_PL)

        self.retranslateUi(SpcPro)
        QtCore.QMetaObject.connectSlotsByName(SpcPro)

    def retranslateUi(self, SpcPro):
        _translate = QtCore.QCoreApplication.translate
        SpcPro.setWindowTitle(_translate("SpcPro", "Spc Processing"))
        self.groupBox.setTitle(_translate("SpcPro", "Data list"))
        self.pushButton_Next.setToolTip(_translate("SpcPro", "Next"))
        self.pushButton_Open.setToolTip(_translate("SpcPro", "Open folder"))
        self.pushButton_Previous.setToolTip(_translate("SpcPro", "Previous"))
        self.pushButton_Refresh.setToolTip(_translate("SpcPro", "Refresh data list"))
        self.dockWidget_AG.setWindowTitle(_translate("SpcPro", "Algebra"))
        self.pushButton_do_algebra.setText(_translate("SpcPro", "Do it"))
        self.groupBox_2.setTitle(_translate("SpcPro", "Single line"))
        self.comboBox_algebra.setItemText(0, _translate("SpcPro", "+"))
        self.comboBox_algebra.setItemText(1, _translate("SpcPro", "×"))
        self.comboBox_algebra.setItemText(2, _translate("SpcPro", "Log"))
        self.comboBox_algebra.setItemText(3, _translate("SpcPro", "Exp"))
        self.comboBox_algebra.setItemText(4, _translate("SpcPro", "Norm AVG"))
        self.comboBox_algebra.setItemText(5, _translate("SpcPro", "Norm 1PT"))
        self.comboBox_algebra.setItemText(6, _translate("SpcPro", "× (x-axis)"))
        self.comboBox_algebra.setItemText(7, _translate("SpcPro", "Offset (x-axis)"))
        self.pushButton_Adv_algebra.setText(_translate("SpcPro", "Advanced"))
        self.dockWidgetSC.setWindowTitle(_translate("SpcPro", "Sim Curve"))
        self.pushButton_do_SC.setText(_translate("SpcPro", "Do it"))
        self.dockWidget_BP.setWindowTitle(_translate("SpcPro", "Basic Processing"))
        self.groupBox_5.setTitle(_translate("SpcPro", "Weighted AVG"))
        self.pushButton_weightedAVG.setText(_translate("SpcPro", "Do it"))
        self.groupBox_4.setTitle(_translate("SpcPro", "FFT/IFFT"))
        self.pushButton_fft.setText(_translate("SpcPro", "Do FFT"))
        self.pushButton_ifft.setText(_translate("SpcPro", "Do IFFT"))
        self.groupBox_3.setTitle(_translate("SpcPro", "Copy to new window"))
        self.pushButton_Copy.setText(_translate("SpcPro", "Do it"))
        self.dockWidget_AP.setWindowTitle(_translate("SpcPro", "Advanced Processing"))
        self.groupBox_6.setTitle(_translate("SpcPro", "Filter"))
        self.label_2.setText(_translate("SpcPro", "High"))
        self.label.setText(_translate("SpcPro", "Low"))
        self.comboBox_filter.setItemText(0, _translate("SpcPro", "dy/dx"))
        self.comboBox_filter.setItemText(1, _translate("SpcPro", "dy2/dx2"))
        self.comboBox_filter.setItemText(2, _translate("SpcPro", "Cut off"))
        self.spinBox_highfreq_filter.setSuffix(_translate("SpcPro", "%"))
        self.spinBox_lowfreq_filter.setSuffix(_translate("SpcPro", "%"))
        self.pushButton_do_filter.setText(_translate("SpcPro", "Do it"))
        self.groupBox_7.setTitle(_translate("SpcPro", "Smooth"))
        self.label_3.setText(_translate("SpcPro", "Factor"))
        self.pushButton_do_smooth.setText(_translate("SpcPro", "Do it"))
        self.comboBox_smooth.setItemText(0, _translate("SpcPro", "movmean"))
        self.comboBox_smooth.setItemText(1, _translate("SpcPro", "movmedian"))
        self.comboBox_smooth.setItemText(2, _translate("SpcPro", "gaussian"))
        self.comboBox_smooth.setItemText(3, _translate("SpcPro", "sgolay"))
        self.dockWidget_PL.setWindowTitle(_translate("SpcPro", "Plot 2D/3D"))
        self.pushButton_do_plot.setText(_translate("SpcPro", "Plot 2D3D"))
        self.pushButton_do_draw.setText(_translate("SpcPro", "Draw 2D3D"))
import logo_rc
