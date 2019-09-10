from PyQt5 import QtWidgets, uic

qtMainWindow = "mainwindow.ui"
Ui_MainWindow, QtBaseClass = uic.loadUiType(qtMainWindow)

class Gui(QtWidgets.QMainWindow, Ui_MainWindow):
