# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'AdvancedLinecut.ui'
#
# Created by: PyQt5 UI code generator 5.15.1
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_AdvancedLinecut(object):
    def setupUi(self, AdvancedLinecut):
        AdvancedLinecut.setObjectName("AdvancedLinecut")
        AdvancedLinecut.resize(404, 266)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/menuIcon/data/shark_and_lollipop_1.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        AdvancedLinecut.setWindowIcon(icon)
        self.gridLayout_6 = QtWidgets.QGridLayout(AdvancedLinecut)
        self.gridLayout_6.setObjectName("gridLayout_6")
        self.groupBox_energy = QtWidgets.QGroupBox(AdvancedLinecut)
        self.groupBox_energy.setCheckable(True)
        self.groupBox_energy.setChecked(True)
        self.groupBox_energy.setObjectName("groupBox_energy")
        self.gridLayout_2 = QtWidgets.QGridLayout(self.groupBox_energy)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.widget = QtWidgets.QWidget(self.groupBox_energy)
        self.widget.setObjectName("widget")
        self.gridLayout = QtWidgets.QGridLayout(self.widget)
        self.gridLayout.setObjectName("gridLayout")
        self.label = QtWidgets.QLabel(self.widget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Maximum, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label.sizePolicy().hasHeightForWidth())
        self.label.setSizePolicy(sizePolicy)
        self.label.setObjectName("label")
        self.gridLayout.addWidget(self.label, 0, 0, 1, 1)
        self.radioButton_ON = QtWidgets.QRadioButton(self.widget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Maximum, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.radioButton_ON.sizePolicy().hasHeightForWidth())
        self.radioButton_ON.setSizePolicy(sizePolicy)
        self.radioButton_ON.setObjectName("radioButton_ON")
        self.gridLayout.addWidget(self.radioButton_ON, 0, 1, 1, 1)
        self.radioButton_OFF = QtWidgets.QRadioButton(self.widget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Maximum, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.radioButton_OFF.sizePolicy().hasHeightForWidth())
        self.radioButton_OFF.setSizePolicy(sizePolicy)
        self.radioButton_OFF.setChecked(True)
        self.radioButton_OFF.setObjectName("radioButton_OFF")
        self.gridLayout.addWidget(self.radioButton_OFF, 0, 2, 1, 1)
        self.gridLayout_2.addWidget(self.widget, 0, 0, 1, 2)
        self.pushButton_do_energy = QtWidgets.QPushButton(self.groupBox_energy)
        self.pushButton_do_energy.setObjectName("pushButton_do_energy")
        self.gridLayout_2.addWidget(self.pushButton_do_energy, 1, 0, 1, 1)
        self.pushButton_export_energy = QtWidgets.QPushButton(self.groupBox_energy)
        self.pushButton_export_energy.setObjectName("pushButton_export_energy")
        self.gridLayout_2.addWidget(self.pushButton_export_energy, 1, 1, 1, 1)
        self.gridLayout_6.addWidget(self.groupBox_energy, 0, 0, 1, 1)
        self.groupBox_angle = QtWidgets.QGroupBox(AdvancedLinecut)
        self.groupBox_angle.setCheckable(True)
        self.groupBox_angle.setChecked(False)
        self.groupBox_angle.setObjectName("groupBox_angle")
        self.gridLayout_5 = QtWidgets.QGridLayout(self.groupBox_angle)
        self.gridLayout_5.setObjectName("gridLayout_5")
        self.widget_2 = QtWidgets.QWidget(self.groupBox_angle)
        self.widget_2.setObjectName("widget_2")
        self.gridLayout_3 = QtWidgets.QGridLayout(self.widget_2)
        self.gridLayout_3.setObjectName("gridLayout_3")
        self.label_2 = QtWidgets.QLabel(self.widget_2)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Maximum, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_2.sizePolicy().hasHeightForWidth())
        self.label_2.setSizePolicy(sizePolicy)
        self.label_2.setObjectName("label_2")
        self.gridLayout_3.addWidget(self.label_2, 0, 0, 1, 1)
        self.spinBox_delta = QtWidgets.QDoubleSpinBox(self.widget_2)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.spinBox_delta.sizePolicy().hasHeightForWidth())
        self.spinBox_delta.setSizePolicy(sizePolicy)
        self.spinBox_delta.setObjectName("spinBox_delta")
        self.gridLayout_3.addWidget(self.spinBox_delta, 0, 1, 1, 1)
        self.label_5 = QtWidgets.QLabel(self.widget_2)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Maximum, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_5.sizePolicy().hasHeightForWidth())
        self.label_5.setSizePolicy(sizePolicy)
        self.label_5.setObjectName("label_5")
        self.gridLayout_3.addWidget(self.label_5, 0, 2, 1, 1)
        self.spinBox_num = QtWidgets.QSpinBox(self.widget_2)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.spinBox_num.sizePolicy().hasHeightForWidth())
        self.spinBox_num.setSizePolicy(sizePolicy)
        self.spinBox_num.setMinimum(1)
        self.spinBox_num.setMaximum(360)
        self.spinBox_num.setObjectName("spinBox_num")
        self.gridLayout_3.addWidget(self.spinBox_num, 0, 3, 1, 1)
        self.gridLayout_5.addWidget(self.widget_2, 0, 0, 1, 2)
        self.pushButton_do_angle = QtWidgets.QPushButton(self.groupBox_angle)
        self.pushButton_do_angle.setObjectName("pushButton_do_angle")
        self.gridLayout_5.addWidget(self.pushButton_do_angle, 1, 0, 1, 1)
        self.pushButton_export_angle = QtWidgets.QPushButton(self.groupBox_angle)
        self.pushButton_export_angle.setObjectName("pushButton_export_angle")
        self.gridLayout_5.addWidget(self.pushButton_export_angle, 1, 1, 1, 1)
        self.gridLayout_6.addWidget(self.groupBox_angle, 1, 0, 1, 1)

        self.retranslateUi(AdvancedLinecut)
        QtCore.QMetaObject.connectSlotsByName(AdvancedLinecut)

    def retranslateUi(self, AdvancedLinecut):
        _translate = QtCore.QCoreApplication.translate
        AdvancedLinecut.setWindowTitle(_translate("AdvancedLinecut", "Advanced Linecut"))
        self.groupBox_energy.setTitle(_translate("AdvancedLinecut", "Linecut VS Energy"))
        self.label.setText(_translate("AdvancedLinecut", "Azimuth average:"))
        self.radioButton_ON.setText(_translate("AdvancedLinecut", "ON"))
        self.radioButton_OFF.setText(_translate("AdvancedLinecut", "OFF"))
        self.pushButton_do_energy.setText(_translate("AdvancedLinecut", "Do it"))
        self.pushButton_export_energy.setText(_translate("AdvancedLinecut", "Export"))
        self.groupBox_angle.setTitle(_translate("AdvancedLinecut", "Linecut VS Angle"))
        self.label_2.setText(_translate("AdvancedLinecut", "Δθ："))
        self.label_5.setText(_translate("AdvancedLinecut", "Num："))
        self.pushButton_do_angle.setText(_translate("AdvancedLinecut", "Do it"))
        self.pushButton_export_angle.setText(_translate("AdvancedLinecut", "Export"))
import logo_rc
