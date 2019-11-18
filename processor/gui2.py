# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'new.ui'
#
# Created by: PyQt5 UI code generator 5.13.1
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(608, 428)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.centralwidget)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.dir_button = QtWidgets.QPushButton(self.centralwidget)
        self.dir_button.setMaximumSize(QtCore.QSize(16777215, 16777215))
        self.dir_button.setToolTipDuration(2)
        self.dir_button.setObjectName("dir_button")
        self.verticalLayout_2.addWidget(self.dir_button)
        self.project_lable = QtWidgets.QLabel(self.centralwidget)
        self.project_lable.setToolTipDuration(2)
        self.project_lable.setAutoFillBackground(False)
        self.project_lable.setStyleSheet("QLabel {background-color:rgb(255, 255, 255);color:black;}")
        self.project_lable.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.project_lable.setFrameShadow(QtWidgets.QFrame.Plain)
        self.project_lable.setScaledContents(False)
        self.project_lable.setAlignment(QtCore.Qt.AlignCenter)
        self.project_lable.setOpenExternalLinks(False)
        self.project_lable.setProperty("folder_name", "")
        self.project_lable.setObjectName("project_lable")
        self.verticalLayout_2.addWidget(self.project_lable)
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")
        self.make_jpg = QtWidgets.QPushButton(self.centralwidget)
        self.make_jpg.setObjectName("make_jpg")
        self.verticalLayout.addWidget(self.make_jpg)
        self.make_list = QtWidgets.QPushButton(self.centralwidget)
        self.make_list.setObjectName("make_list")
        self.verticalLayout.addWidget(self.make_list)
        self.geotag = QtWidgets.QPushButton(self.centralwidget)
        self.geotag.setObjectName("geotag")
        self.verticalLayout.addWidget(self.geotag)
        self.verticalLayout_2.addLayout(self.verticalLayout)
        self.textBrowser = QtWidgets.QTextBrowser(self.centralwidget)
        self.textBrowser.setObjectName("textBrowser")
        self.verticalLayout_2.addWidget(self.textBrowser)
        self.progressBar = QtWidgets.QProgressBar(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.progressBar.sizePolicy().hasHeightForWidth())
        self.progressBar.setSizePolicy(sizePolicy)
        self.progressBar.setProperty("value", 0)
        self.progressBar.setObjectName("progressBar")
        self.verticalLayout_2.addWidget(self.progressBar)
        MainWindow.setCentralWidget(self.centralwidget)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "JPG Generator"))
        self.dir_button.setText(_translate("MainWindow", "Select Project"))
        self.project_lable.setText(_translate("MainWindow", "Projekt Ordner"))
        self.make_jpg.setText(_translate("MainWindow", "Generate JPG"))
        self.make_list.setText(_translate("MainWindow", "Match List"))
        self.geotag.setText(_translate("MainWindow", "Geotag"))
