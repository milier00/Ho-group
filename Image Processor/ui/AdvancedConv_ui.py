# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'AdvancedConv.ui'
#
# Created by: PyQt5 UI code generator 5.15.4
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_AdvancedConv(object):
    def setupUi(self, AdvancedConv):
        AdvancedConv.setObjectName("AdvancedConv")
        AdvancedConv.resize(618, 718)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/menuIcon/data/sea-lion-1.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        AdvancedConv.setWindowIcon(icon)
        self.gridLayout_4 = QtWidgets.QGridLayout(AdvancedConv)
        self.gridLayout_4.setObjectName("gridLayout_4")
        self.groupBox_33 = QtWidgets.QGroupBox(AdvancedConv)
        self.groupBox_33.setMinimumSize(QtCore.QSize(600, 0))
        self.groupBox_33.setCheckable(True)
        self.groupBox_33.setObjectName("groupBox_33")
        self.gridLayout = QtWidgets.QGridLayout(self.groupBox_33)
        self.gridLayout.setObjectName("gridLayout")
        self.spinBox_00_33 = QtWidgets.QSpinBox(self.groupBox_33)
        self.spinBox_00_33.setMaximumSize(QtCore.QSize(36, 16777215))
        self.spinBox_00_33.setButtonSymbols(QtWidgets.QAbstractSpinBox.NoButtons)
        self.spinBox_00_33.setMinimum(-99)
        self.spinBox_00_33.setObjectName("spinBox_00_33")
        self.gridLayout.addWidget(self.spinBox_00_33, 0, 0, 1, 1)
        self.spinBox_01_33 = QtWidgets.QSpinBox(self.groupBox_33)
        self.spinBox_01_33.setMaximumSize(QtCore.QSize(36, 16777215))
        self.spinBox_01_33.setButtonSymbols(QtWidgets.QAbstractSpinBox.NoButtons)
        self.spinBox_01_33.setMinimum(-99)
        self.spinBox_01_33.setObjectName("spinBox_01_33")
        self.gridLayout.addWidget(self.spinBox_01_33, 0, 1, 1, 1)
        self.spinBox_02_33 = QtWidgets.QSpinBox(self.groupBox_33)
        self.spinBox_02_33.setMaximumSize(QtCore.QSize(36, 16777215))
        self.spinBox_02_33.setButtonSymbols(QtWidgets.QAbstractSpinBox.NoButtons)
        self.spinBox_02_33.setMinimum(-99)
        self.spinBox_02_33.setObjectName("spinBox_02_33")
        self.gridLayout.addWidget(self.spinBox_02_33, 0, 2, 1, 1)
        self.spinBox_10_33 = QtWidgets.QSpinBox(self.groupBox_33)
        self.spinBox_10_33.setMaximumSize(QtCore.QSize(36, 16777215))
        self.spinBox_10_33.setButtonSymbols(QtWidgets.QAbstractSpinBox.NoButtons)
        self.spinBox_10_33.setMinimum(-99)
        self.spinBox_10_33.setObjectName("spinBox_10_33")
        self.gridLayout.addWidget(self.spinBox_10_33, 1, 0, 1, 1)
        self.spinBox_11_33 = QtWidgets.QSpinBox(self.groupBox_33)
        self.spinBox_11_33.setMaximumSize(QtCore.QSize(36, 16777215))
        self.spinBox_11_33.setButtonSymbols(QtWidgets.QAbstractSpinBox.NoButtons)
        self.spinBox_11_33.setMinimum(-99)
        self.spinBox_11_33.setProperty("value", 1)
        self.spinBox_11_33.setObjectName("spinBox_11_33")
        self.gridLayout.addWidget(self.spinBox_11_33, 1, 1, 1, 1)
        self.spinBox_12_33 = QtWidgets.QSpinBox(self.groupBox_33)
        self.spinBox_12_33.setMaximumSize(QtCore.QSize(36, 16777215))
        self.spinBox_12_33.setButtonSymbols(QtWidgets.QAbstractSpinBox.NoButtons)
        self.spinBox_12_33.setMinimum(-99)
        self.spinBox_12_33.setObjectName("spinBox_12_33")
        self.gridLayout.addWidget(self.spinBox_12_33, 1, 2, 1, 1)
        self.spinBox_20_33 = QtWidgets.QSpinBox(self.groupBox_33)
        self.spinBox_20_33.setMaximumSize(QtCore.QSize(36, 16777215))
        self.spinBox_20_33.setButtonSymbols(QtWidgets.QAbstractSpinBox.NoButtons)
        self.spinBox_20_33.setMinimum(-99)
        self.spinBox_20_33.setObjectName("spinBox_20_33")
        self.gridLayout.addWidget(self.spinBox_20_33, 2, 0, 1, 1)
        self.spinBox_21_33 = QtWidgets.QSpinBox(self.groupBox_33)
        self.spinBox_21_33.setMaximumSize(QtCore.QSize(36, 16777215))
        self.spinBox_21_33.setButtonSymbols(QtWidgets.QAbstractSpinBox.NoButtons)
        self.spinBox_21_33.setMinimum(-99)
        self.spinBox_21_33.setObjectName("spinBox_21_33")
        self.gridLayout.addWidget(self.spinBox_21_33, 2, 1, 1, 1)
        self.spinBox_22_33 = QtWidgets.QSpinBox(self.groupBox_33)
        self.spinBox_22_33.setMaximumSize(QtCore.QSize(36, 16777215))
        self.spinBox_22_33.setButtonSymbols(QtWidgets.QAbstractSpinBox.NoButtons)
        self.spinBox_22_33.setMinimum(-99)
        self.spinBox_22_33.setObjectName("spinBox_22_33")
        self.gridLayout.addWidget(self.spinBox_22_33, 2, 2, 1, 1)
        self.gridLayout_4.addWidget(self.groupBox_33, 0, 0, 1, 1)
        self.groupBox_55 = QtWidgets.QGroupBox(AdvancedConv)
        self.groupBox_55.setMinimumSize(QtCore.QSize(600, 0))
        self.groupBox_55.setCheckable(True)
        self.groupBox_55.setChecked(False)
        self.groupBox_55.setObjectName("groupBox_55")
        self.gridLayout_2 = QtWidgets.QGridLayout(self.groupBox_55)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.spinBox_00_55 = QtWidgets.QSpinBox(self.groupBox_55)
        self.spinBox_00_55.setMaximumSize(QtCore.QSize(36, 16777215))
        self.spinBox_00_55.setButtonSymbols(QtWidgets.QAbstractSpinBox.NoButtons)
        self.spinBox_00_55.setMinimum(-99)
        self.spinBox_00_55.setObjectName("spinBox_00_55")
        self.gridLayout_2.addWidget(self.spinBox_00_55, 0, 0, 1, 1)
        self.spinBox_01_55 = QtWidgets.QSpinBox(self.groupBox_55)
        self.spinBox_01_55.setMaximumSize(QtCore.QSize(36, 16777215))
        self.spinBox_01_55.setButtonSymbols(QtWidgets.QAbstractSpinBox.NoButtons)
        self.spinBox_01_55.setMinimum(-99)
        self.spinBox_01_55.setObjectName("spinBox_01_55")
        self.gridLayout_2.addWidget(self.spinBox_01_55, 0, 1, 1, 1)
        self.spinBox_02_55 = QtWidgets.QSpinBox(self.groupBox_55)
        self.spinBox_02_55.setMaximumSize(QtCore.QSize(36, 16777215))
        self.spinBox_02_55.setButtonSymbols(QtWidgets.QAbstractSpinBox.NoButtons)
        self.spinBox_02_55.setMinimum(-99)
        self.spinBox_02_55.setObjectName("spinBox_02_55")
        self.gridLayout_2.addWidget(self.spinBox_02_55, 0, 2, 1, 1)
        self.spinBox_03_55 = QtWidgets.QSpinBox(self.groupBox_55)
        self.spinBox_03_55.setMaximumSize(QtCore.QSize(36, 16777215))
        self.spinBox_03_55.setButtonSymbols(QtWidgets.QAbstractSpinBox.NoButtons)
        self.spinBox_03_55.setMinimum(-99)
        self.spinBox_03_55.setObjectName("spinBox_03_55")
        self.gridLayout_2.addWidget(self.spinBox_03_55, 0, 3, 1, 1)
        self.spinBox_04_55 = QtWidgets.QSpinBox(self.groupBox_55)
        self.spinBox_04_55.setMaximumSize(QtCore.QSize(36, 16777215))
        self.spinBox_04_55.setButtonSymbols(QtWidgets.QAbstractSpinBox.NoButtons)
        self.spinBox_04_55.setMinimum(-99)
        self.spinBox_04_55.setObjectName("spinBox_04_55")
        self.gridLayout_2.addWidget(self.spinBox_04_55, 0, 4, 1, 1)
        self.spinBox_10_55 = QtWidgets.QSpinBox(self.groupBox_55)
        self.spinBox_10_55.setMaximumSize(QtCore.QSize(36, 16777215))
        self.spinBox_10_55.setButtonSymbols(QtWidgets.QAbstractSpinBox.NoButtons)
        self.spinBox_10_55.setMinimum(-99)
        self.spinBox_10_55.setObjectName("spinBox_10_55")
        self.gridLayout_2.addWidget(self.spinBox_10_55, 1, 0, 1, 1)
        self.spinBox_11_55 = QtWidgets.QSpinBox(self.groupBox_55)
        self.spinBox_11_55.setMaximumSize(QtCore.QSize(36, 16777215))
        self.spinBox_11_55.setButtonSymbols(QtWidgets.QAbstractSpinBox.NoButtons)
        self.spinBox_11_55.setMinimum(-99)
        self.spinBox_11_55.setObjectName("spinBox_11_55")
        self.gridLayout_2.addWidget(self.spinBox_11_55, 1, 1, 1, 1)
        self.spinBox_12_55 = QtWidgets.QSpinBox(self.groupBox_55)
        self.spinBox_12_55.setMaximumSize(QtCore.QSize(36, 16777215))
        self.spinBox_12_55.setButtonSymbols(QtWidgets.QAbstractSpinBox.NoButtons)
        self.spinBox_12_55.setMinimum(-99)
        self.spinBox_12_55.setObjectName("spinBox_12_55")
        self.gridLayout_2.addWidget(self.spinBox_12_55, 1, 2, 1, 1)
        self.spinBox_13_55 = QtWidgets.QSpinBox(self.groupBox_55)
        self.spinBox_13_55.setMaximumSize(QtCore.QSize(36, 16777215))
        self.spinBox_13_55.setButtonSymbols(QtWidgets.QAbstractSpinBox.NoButtons)
        self.spinBox_13_55.setMinimum(-99)
        self.spinBox_13_55.setObjectName("spinBox_13_55")
        self.gridLayout_2.addWidget(self.spinBox_13_55, 1, 3, 1, 1)
        self.spinBox_14_55 = QtWidgets.QSpinBox(self.groupBox_55)
        self.spinBox_14_55.setMaximumSize(QtCore.QSize(36, 16777215))
        self.spinBox_14_55.setButtonSymbols(QtWidgets.QAbstractSpinBox.NoButtons)
        self.spinBox_14_55.setMinimum(-99)
        self.spinBox_14_55.setObjectName("spinBox_14_55")
        self.gridLayout_2.addWidget(self.spinBox_14_55, 1, 4, 1, 1)
        self.spinBox_20_55 = QtWidgets.QSpinBox(self.groupBox_55)
        self.spinBox_20_55.setMaximumSize(QtCore.QSize(36, 16777215))
        self.spinBox_20_55.setButtonSymbols(QtWidgets.QAbstractSpinBox.NoButtons)
        self.spinBox_20_55.setMinimum(-99)
        self.spinBox_20_55.setObjectName("spinBox_20_55")
        self.gridLayout_2.addWidget(self.spinBox_20_55, 2, 0, 1, 1)
        self.spinBox_21_55 = QtWidgets.QSpinBox(self.groupBox_55)
        self.spinBox_21_55.setMaximumSize(QtCore.QSize(36, 16777215))
        self.spinBox_21_55.setButtonSymbols(QtWidgets.QAbstractSpinBox.NoButtons)
        self.spinBox_21_55.setMinimum(-99)
        self.spinBox_21_55.setObjectName("spinBox_21_55")
        self.gridLayout_2.addWidget(self.spinBox_21_55, 2, 1, 1, 1)
        self.spinBox_22_55 = QtWidgets.QSpinBox(self.groupBox_55)
        self.spinBox_22_55.setMaximumSize(QtCore.QSize(36, 16777215))
        self.spinBox_22_55.setButtonSymbols(QtWidgets.QAbstractSpinBox.NoButtons)
        self.spinBox_22_55.setMinimum(-99)
        self.spinBox_22_55.setProperty("value", 1)
        self.spinBox_22_55.setObjectName("spinBox_22_55")
        self.gridLayout_2.addWidget(self.spinBox_22_55, 2, 2, 1, 1)
        self.spinBox_23_55 = QtWidgets.QSpinBox(self.groupBox_55)
        self.spinBox_23_55.setMaximumSize(QtCore.QSize(36, 16777215))
        self.spinBox_23_55.setButtonSymbols(QtWidgets.QAbstractSpinBox.NoButtons)
        self.spinBox_23_55.setMinimum(-99)
        self.spinBox_23_55.setObjectName("spinBox_23_55")
        self.gridLayout_2.addWidget(self.spinBox_23_55, 2, 3, 1, 1)
        self.spinBox_24_55 = QtWidgets.QSpinBox(self.groupBox_55)
        self.spinBox_24_55.setMaximumSize(QtCore.QSize(36, 16777215))
        self.spinBox_24_55.setButtonSymbols(QtWidgets.QAbstractSpinBox.NoButtons)
        self.spinBox_24_55.setMinimum(-99)
        self.spinBox_24_55.setObjectName("spinBox_24_55")
        self.gridLayout_2.addWidget(self.spinBox_24_55, 2, 4, 1, 1)
        self.spinBox_30_55 = QtWidgets.QSpinBox(self.groupBox_55)
        self.spinBox_30_55.setMaximumSize(QtCore.QSize(36, 16777215))
        self.spinBox_30_55.setButtonSymbols(QtWidgets.QAbstractSpinBox.NoButtons)
        self.spinBox_30_55.setMinimum(-99)
        self.spinBox_30_55.setObjectName("spinBox_30_55")
        self.gridLayout_2.addWidget(self.spinBox_30_55, 3, 0, 1, 1)
        self.spinBox_31_55 = QtWidgets.QSpinBox(self.groupBox_55)
        self.spinBox_31_55.setMaximumSize(QtCore.QSize(36, 16777215))
        self.spinBox_31_55.setButtonSymbols(QtWidgets.QAbstractSpinBox.NoButtons)
        self.spinBox_31_55.setMinimum(-99)
        self.spinBox_31_55.setObjectName("spinBox_31_55")
        self.gridLayout_2.addWidget(self.spinBox_31_55, 3, 1, 1, 1)
        self.spinBox_32_55 = QtWidgets.QSpinBox(self.groupBox_55)
        self.spinBox_32_55.setMaximumSize(QtCore.QSize(36, 16777215))
        self.spinBox_32_55.setButtonSymbols(QtWidgets.QAbstractSpinBox.NoButtons)
        self.spinBox_32_55.setMinimum(-99)
        self.spinBox_32_55.setObjectName("spinBox_32_55")
        self.gridLayout_2.addWidget(self.spinBox_32_55, 3, 2, 1, 1)
        self.spinBox_33_55 = QtWidgets.QSpinBox(self.groupBox_55)
        self.spinBox_33_55.setMaximumSize(QtCore.QSize(36, 16777215))
        self.spinBox_33_55.setButtonSymbols(QtWidgets.QAbstractSpinBox.NoButtons)
        self.spinBox_33_55.setMinimum(-99)
        self.spinBox_33_55.setObjectName("spinBox_33_55")
        self.gridLayout_2.addWidget(self.spinBox_33_55, 3, 3, 1, 1)
        self.spinBox_34_55 = QtWidgets.QSpinBox(self.groupBox_55)
        self.spinBox_34_55.setMaximumSize(QtCore.QSize(36, 16777215))
        self.spinBox_34_55.setButtonSymbols(QtWidgets.QAbstractSpinBox.NoButtons)
        self.spinBox_34_55.setMinimum(-99)
        self.spinBox_34_55.setObjectName("spinBox_34_55")
        self.gridLayout_2.addWidget(self.spinBox_34_55, 3, 4, 1, 1)
        self.spinBox_40_55 = QtWidgets.QSpinBox(self.groupBox_55)
        self.spinBox_40_55.setMaximumSize(QtCore.QSize(36, 16777215))
        self.spinBox_40_55.setButtonSymbols(QtWidgets.QAbstractSpinBox.NoButtons)
        self.spinBox_40_55.setMinimum(-99)
        self.spinBox_40_55.setObjectName("spinBox_40_55")
        self.gridLayout_2.addWidget(self.spinBox_40_55, 4, 0, 1, 1)
        self.spinBox_41_55 = QtWidgets.QSpinBox(self.groupBox_55)
        self.spinBox_41_55.setMaximumSize(QtCore.QSize(36, 16777215))
        self.spinBox_41_55.setButtonSymbols(QtWidgets.QAbstractSpinBox.NoButtons)
        self.spinBox_41_55.setMinimum(-99)
        self.spinBox_41_55.setObjectName("spinBox_41_55")
        self.gridLayout_2.addWidget(self.spinBox_41_55, 4, 1, 1, 1)
        self.spinBox_42_55 = QtWidgets.QSpinBox(self.groupBox_55)
        self.spinBox_42_55.setMaximumSize(QtCore.QSize(36, 16777215))
        self.spinBox_42_55.setButtonSymbols(QtWidgets.QAbstractSpinBox.NoButtons)
        self.spinBox_42_55.setMinimum(-99)
        self.spinBox_42_55.setObjectName("spinBox_42_55")
        self.gridLayout_2.addWidget(self.spinBox_42_55, 4, 2, 1, 1)
        self.spinBox_43_55 = QtWidgets.QSpinBox(self.groupBox_55)
        self.spinBox_43_55.setMaximumSize(QtCore.QSize(36, 16777215))
        self.spinBox_43_55.setButtonSymbols(QtWidgets.QAbstractSpinBox.NoButtons)
        self.spinBox_43_55.setMinimum(-99)
        self.spinBox_43_55.setObjectName("spinBox_43_55")
        self.gridLayout_2.addWidget(self.spinBox_43_55, 4, 3, 1, 1)
        self.spinBox_44_55 = QtWidgets.QSpinBox(self.groupBox_55)
        self.spinBox_44_55.setMaximumSize(QtCore.QSize(36, 16777215))
        self.spinBox_44_55.setButtonSymbols(QtWidgets.QAbstractSpinBox.NoButtons)
        self.spinBox_44_55.setMinimum(-99)
        self.spinBox_44_55.setObjectName("spinBox_44_55")
        self.gridLayout_2.addWidget(self.spinBox_44_55, 4, 4, 1, 1)
        self.gridLayout_4.addWidget(self.groupBox_55, 1, 0, 1, 1)
        self.groupBox_3 = QtWidgets.QGroupBox(AdvancedConv)
        self.groupBox_3.setMinimumSize(QtCore.QSize(600, 0))
        self.groupBox_3.setObjectName("groupBox_3")
        self.gridLayout_3 = QtWidgets.QGridLayout(self.groupBox_3)
        self.gridLayout_3.setObjectName("gridLayout_3")
        self.textBrowser = QtWidgets.QTextBrowser(self.groupBox_3)
        self.textBrowser.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)
        self.textBrowser.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOn)
        self.textBrowser.setSizeAdjustPolicy(QtWidgets.QAbstractScrollArea.AdjustToContentsOnFirstShow)
        self.textBrowser.setObjectName("textBrowser")
        self.gridLayout_3.addWidget(self.textBrowser, 0, 0, 1, 1)
        self.gridLayout_4.addWidget(self.groupBox_3, 2, 0, 1, 1)

        self.retranslateUi(AdvancedConv)
        QtCore.QMetaObject.connectSlotsByName(AdvancedConv)

    def retranslateUi(self, AdvancedConv):
        _translate = QtCore.QCoreApplication.translate
        AdvancedConv.setWindowTitle(_translate("AdvancedConv", "Advanced Convolution"))
        self.groupBox_33.setTitle(_translate("AdvancedConv", "3×3 kernel"))
        self.groupBox_55.setTitle(_translate("AdvancedConv", "5×5 kernel"))
        self.groupBox_3.setTitle(_translate("AdvancedConv", "Reference"))
        self.textBrowser.setHtml(_translate("AdvancedConv", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'MS Shell Dlg 2\'; font-size:10.125pt; font-weight:400; font-style:normal;\">\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:\'SimSun\'; font-size:9pt;\">Default kernels:</span></p>\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-family:\'SimSun\'; font-size:9pt;\"><br /></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:\'SimSun\'; font-size:9pt; font-weight:600; text-decoration: underline;\">blur</span></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:\'SimSun\'; font-size:9pt;\">1    2    1</span></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:\'SimSun\'; font-size:9pt;\">2    4    2</span></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:\'SimSun\'; font-size:9pt;\">1    2    1</span></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:\'SimSun\'; font-size:9pt; font-weight:600; text-decoration: underline;\">slight blur</span></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:\'SimSun\'; font-size:9pt;\">0    1    0</span></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:\'SimSun\'; font-size:9pt;\">1    9    1</span></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:\'SimSun\'; font-size:9pt;\">0    1    0</span></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:\'SimSun\'; font-size:9pt; font-weight:600; text-decoration: underline;\">sobel</span></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:\'SimSun\'; font-size:9pt;\">-1    -2    -1</span></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:\'SimSun\'; font-size:9pt;\">0    0    0</span></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:\'SimSun\'; font-size:9pt;\">1    2    1</span></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:\'SimSun\'; font-size:9pt; font-weight:600; text-decoration: underline;\">emboss</span></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:\'SimSun\'; font-size:9pt;\">-2    -1    0</span></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:\'SimSun\'; font-size:9pt;\">-1    1    1</span></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:\'SimSun\'; font-size:9pt;\">0    1    2</span></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:\'SimSun\'; font-size:9pt; font-weight:600; text-decoration: underline;\">outline</span></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:\'SimSun\'; font-size:9pt;\">-1    -1    -1</span></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:\'SimSun\'; font-size:9pt;\">-1    8    -1</span></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:\'SimSun\'; font-size:9pt;\">-1    -1    -1</span></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:\'SimSun\'; font-size:9pt; font-weight:600; text-decoration: underline;\">sharpen</span></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:\'SimSun\'; font-size:9pt;\">0    -1    0</span></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:\'SimSun\'; font-size:9pt;\">-1    5    -1</span></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:\'SimSun\'; font-size:9pt;\">0    -1    0</span></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:\'SimSun\'; font-size:9pt; font-weight:600; text-decoration: underline;\">laplacian</span></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:\'SimSun\'; font-size:9pt;\">0    1    0</span></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:\'SimSun\'; font-size:9pt;\">1    -4    1</span></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:\'SimSun\'; font-size:9pt;\">0    1    0</span></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:\'SimSun\'; font-size:9pt; font-weight:600; text-decoration: underline;\">kernel_sharpen_1</span></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:\'SimSun\'; font-size:9pt;\">-1    -1    -1</span></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:\'SimSun\'; font-size:9pt;\">-1    9    -1</span></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:\'SimSun\'; font-size:9pt;\">-1    -1    -1</span></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:\'SimSun\'; font-size:9pt; font-weight:600; text-decoration: underline;\">kernel_sharpen_2</span></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:\'SimSun\'; font-size:9pt;\">1    1    1</span></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:\'SimSun\'; font-size:9pt;\">1    -7    1</span></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:\'SimSun\'; font-size:9pt;\">1    1    1</span></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:\'SimSun\'; font-size:9pt; font-weight:600; text-decoration: underline;\">kernel_sharpen_3</span></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:\'SimSun\'; font-size:9pt;\">-1  -1  -1  -1  -1</span></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:\'SimSun\'; font-size:9pt;\">-1   2   2   2  -1</span></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:\'SimSun\'; font-size:9pt;\">-1   2   8   2  -1</span></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:\'SimSun\'; font-size:9pt;\">-1   2   2   2  -1</span></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:\'SimSun\'; font-size:9pt;\">-1  -1  -1  -1  -1</span></p></body></html>"))
import logo_rc
