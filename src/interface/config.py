import sys
import random

import toml
from PySide6 import QtCore, QtWidgets, QtGui
import lib.Search


# noinspection DuplicatedCode
class Config(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()

        self.update_button = QtWidgets.QPushButton("Update Config")

        self.layout = QtWidgets.QFormLayout(self)
        self.layout.addWidget(self.update_button)

        self.config = toml.load('config.toml')
        print(self.config)
        for i in self.config.keys():
            self.layout.addRow(QtWidgets.QLabel(i))
            for j in self.config[i].keys():
                self.layout.addRow(j, QtWidgets.QLineEdit(str(self.config[i][j])))

        self.layout.addWidget(self.update_button)

        self.update_button.clicked.connect(self.update_method)

    @QtCore.Slot()
    def update_method(self):
        widgets = (self.layout.itemAt(i).widget() for i in range(self.layout.count()))
        # for widget in widgets:
        #     if isinstance(widget, QtWidgets.QLineEdit):
        #         print("linedit:%s %s" % (widget.objectName(), widget.text()))
        #     if isinstance(widget, QtWidgets.QLabel):
        #         print("label:%s %s" % (widget.objectName(), widget.text()))

        offset = 0
        chng_config = {}
        keys = []
        for i in range(0, self.layout.count(), 2):
            widget = self.layout.itemAt(i-offset).widget()
            next_widget = self.layout.itemAt(i+1-offset).widget()
            if isinstance(widget, QtWidgets.QLabel) and isinstance(next_widget, QtWidgets.QLabel):
                offset += 1
                keys.append(widget.text())
                chng_config[widget.text()] = {}
                continue
            else:
                print(widget.text(), next_widget.text())
                key = keys[len(keys)-1]
                chng_config[key][widget.text()] = next_widget.text()

        print(chng_config)