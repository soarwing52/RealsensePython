# -*- coding: utf-8 -*-
import sys
import multiprocessing as mp
from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtGui import QImage, QPixmap
from temp import Ui_MainWindow
from cmd_class import RScam
import cv2
import threading

a = RScam()


class MainWindow(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent=parent)
        self.setupUi(self)
        self.setWindowIcon(QtGui.QIcon('img/intel.png'))

        self.timer_camera = QtCore.QTimer()
        self.timer_camera.timeout.connect(self.show_image)
        self.timer_camera.start(int(1000 / 15))

        self.timer_msg = QtCore.QTimer()
        self.timer_msg.timeout.connect(self.get_msg)
        self.timer_msg.start(1000)

        self.btn_start.clicked.connect(lambda : self.start())
        self.btn_restart.clicked.connect(lambda: self.restart())
        self.btn_photo.clicked.connect(lambda: self.foto())
        self.btn_quit.clicked.connect(lambda: self.quit_btn())

        self.spinBox.setValue(a.distance)
        self.checkBox.stateChanged.connect(lambda : self.auto_change())
        self.spinBox.valueChanged.connect(lambda : self.dis_change())


    def keyPressEvent(self, event):
        key = event.key()
        if key == 16777238:
            if a.auto is True:
                self.checkBox.setChecked(False)
            else:
                self.checkBox.setChecked(True)
            print(a.auto)
        elif key == 16777239:
            self.restart()
        elif key == 66:
            self.foto()

    def start(self):
        if a.gps_status.value == 0:
            a.start_gps()
            a.restart = True
            t = threading.Thread(target=a.main_loop)
            t.start()
            print("start loop")
            return "started camera"
        elif a.gps_status.value == 2:
            print("wait for signal")
            return "waiting for signal"
        else:
            print(a.gps_status.value, a.camera_command.value)
            return "start but waiting GPS"

    def show_image(self):
        try:
            self.img = a.img
            self.img = cv2.resize(self.img, (400, 500))
            height, width, channel = self.img.shape
        except:
            print('no image, get default')
            self.img = cv2.imread('1.jpg')
            self.img = cv2.resize(self.img, (400, 500))
            height, width, channel = self.img.shape

        bytesPerline = 3 * width
        self.qImg = QImage(self.img.data, width, height, bytesPerline, QImage.Format_RGB888).rgbSwapped()
        # 將QImage顯示出來
        self.label.setPixmap(QPixmap.fromImage(self.qImg))

    def restart(self):
        print("restart")
        a.command = "restart"

    def foto(self):
        print("foto")
        a.command = 'shot'

    def quit_btn(self):
        print("quit")
        a.restart = False
        a.command = 'quit'

    def auto_change(self):
        if self.checkBox.isChecked() is False:
            print('no')
            self.checkBox.setText('Auto off')
            self.checkBox.setChecked(False)
            a.auto = False
        else:
            print('checked')
            self.checkBox.setText('Auto on')
            self.checkBox.setChecked(True)
            a.auto = True

    def dis_change(self):
        a.distance = self.spinBox.value()
        print(a.distance)

    def get_msg(self):
        self.statusbar.showMessage(a.msg)



class msgThread(QThread):
    msg = pyqtSignal(str)

    def __int__(self, parent=None):
        super(msgThread, self).__init__(parent)

    def run(self):
        while True:
            #print('ruuning')
            self.msg.emit(a.msg)

if __name__ == "__main__":
    mp.freeze_support()
    app = QtWidgets.QApplication(sys.argv)
    w = MainWindow()
    w.show()
    sys.exit(app.exec_())