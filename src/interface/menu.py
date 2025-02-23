from configparser import SafeConfigParser
import sys
import random

import toml
from PySide6 import QtCore, QtWidgets, QtGui
from interface import search
from interface import config
from ingest import ingest


class Menu(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()

        self.s = search.Search()
        self.c = config.Config()

        self.ingest_button = QtWidgets.QPushButton("Run Ingest")
        self.search_button = QtWidgets.QPushButton("Search")
        self.config_button = QtWidgets.QPushButton("Config")

        self.l = QtWidgets.QGridLayout(self)
        self.l.setGeometry(QtCore.QRect(0, 0, 3, 3))
        self.l.addWidget(self.ingest_button, 0, 0, 1, 2)
        self.l.addWidget(self.search_button, 2, 0, 1, 2)
        self.l.addWidget(self.config_button, 3, 0, 1, 2)

        self.layout = QtWidgets.QWidget()
        self.layout.setLayout(self.l)

        self.setCentralWidget(self.layout)

        self.ingest_button.clicked.connect(self.ingest)
        self.search_button.clicked.connect(self.search)
        self.config_button.clicked.connect(self.change_config)

        self.config = toml.load('config.toml')

    @QtCore.Slot()
    def ingest(self):
        print("Running ingest")
        ingest(self.config["files"]['ingest'], self.config['files']['archive'], self.config['files']['check'])

    @QtCore.Slot()
    def search(self):
        print("Searching")
        if self.s.isVisible():
            pass
        else:
            self.s.show()

    @QtCore.Slot()
    def change_config(self):
        print("Config")
        if self.c.isVisible():
            pass
        else:
            self.c.show()


def start():
    app = QtWidgets.QApplication([])

    widget = Menu()
    widget.resize(800, 400)
    widget.setWindowTitle("Menu")
    widget.show()

    sys.exit(app.exec_())


if __name__ == "__main__":
    start()
