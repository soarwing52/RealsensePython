# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'cam.ui'
#
# Created by: PyQt5 UI code generator 5.13.1
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(428, 675)
        font = QtGui.QFont()
        font.setPointSize(14)
        MainWindow.setFont(font)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.gridLayoutWidget = QtWidgets.QWidget(self.centralwidget)
        self.gridLayoutWidget.setGeometry(QtCore.QRect(10, 10, 401, 191))
        self.gridLayoutWidget.setObjectName("gridLayoutWidget")
        self.gridLayout = QtWidgets.QGridLayout(self.gridLayoutWidget)
        self.gridLayout.setContentsMargins(0, 0, 0, 0)
        self.gridLayout.setObjectName("gridLayout")
        self.btn_start = QtWidgets.QPushButton(self.gridLayoutWidget)
        self.btn_start.setObjectName("btn_start")
        self.gridLayout.addWidget(self.btn_start, 0, 0, 1, 1)
        self.btn_photo = QtWidgets.QPushButton(self.gridLayoutWidget)
        self.btn_photo.setObjectName("btn_photo")
        self.gridLayout.addWidget(self.btn_photo, 1, 0, 1, 1)
        self.btn_restart = QtWidgets.QPushButton(self.gridLayoutWidget)
        self.btn_restart.setObjectName("btn_restart")
        self.gridLayout.addWidget(self.btn_restart, 0, 1, 1, 1)
        self.btn_quit = QtWidgets.QPushButton(self.gridLayoutWidget)
        self.btn_quit.setObjectName("btn_quit")
        self.gridLayout.addWidget(self.btn_quit, 1, 1, 1, 1)
        self.spinBox = QtWidgets.QSpinBox(self.gridLayoutWidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(10)
        sizePolicy.setHeightForWidth(self.spinBox.sizePolicy().hasHeightForWidth())
        self.spinBox.setSizePolicy(sizePolicy)
        self.spinBox.setMinimumSize(QtCore.QSize(0, 50))
        self.spinBox.setProperty("value", 15)
        self.spinBox.setObjectName("spinBox")
        self.gridLayout.addWidget(self.spinBox, 2, 0, 1, 1)
        self.checkBox = QtWidgets.QCheckBox(self.gridLayoutWidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Ignored)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.checkBox.sizePolicy().hasHeightForWidth())
        self.checkBox.setSizePolicy(sizePolicy)
        self.checkBox.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.checkBox.setChecked(False)
        self.checkBox.setTristate(False)
        self.checkBox.setObjectName("checkBox")
        self.gridLayout.addWidget(self.checkBox, 2, 1, 1, 1)
        self.label = QtWidgets.QLabel(self.centralwidget)
        self.label.setGeometry(QtCore.QRect(10, 210, 401, 441))
        self.label.setText("")
        self.label.setObjectName("label")
        MainWindow.setCentralWidget(self.centralwidget)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "D435"))
        self.btn_start.setText(_translate("MainWindow", "Start"))
        self.btn_photo.setText(_translate("MainWindow", "Foto"))
        self.btn_restart.setText(_translate("MainWindow", "Restart"))
        self.btn_quit.setText(_translate("MainWindow", "Quit"))
        self.checkBox.setText(_translate("MainWindow", "Auto off"))
