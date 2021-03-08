import sys
import random
from PySide6 import QtCore, QtWidgets, QtGui
import lib.Search


# noinspection DuplicatedCode
class Search(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()

        self.search_button = QtWidgets.QPushButton("Search")

        self.layout = QtWidgets.QFormLayout(self)
        self.layout.addWidget(self.search_button)

        self.vtype = QtWidgets.QLineEdit()
        self.vmake = QtWidgets.QLineEdit()
        self.vmodel = QtWidgets.QLineEdit()
        self.vserial = QtWidgets.QLineEdit()
        self.vproperty = QtWidgets.QLineEdit()
        self.vlocation = QtWidgets.QLineEdit()
        self.vinventory = QtWidgets.QLineEdit()
        self.valltable = QtWidgets.QCheckBox()
        self.layout.addRow("Type", self.vtype)
        self.layout.addRow("Make", self.vmake)
        self.layout.addRow("Model", self.vmodel)
        self.layout.addRow("Serial Number", self.vserial)
        self.layout.addRow("Property Control", self.vproperty)
        self.layout.addRow("Location", self.vlocation)
        self.layout.addRow("Inventory Tag", self.vinventory)
        self.layout.addRow("All tables", self.valltable)

        self.layout.addWidget(self.search_button)

        self.search_button.clicked.connect(self.search_method)

    @QtCore.Slot()
    def search_method(self):
        _type = self.vtype.text()
        if _type == '':
            _type = None
        _make = self.vmake.text()
        if _make == '':
            _make = None
        _model = self.vmodel.text()
        if _model == '':
            _model = None
        _serial = self.vserial.text()
        if _serial == '':
            _serial = None
        _property = self.vproperty.text()
        if _property == '':
            _property = None
        _location = self.vlocation.text()
        if _location == '':
            _location = None
        _inventory = self.vinventory.text()
        if _inventory == '':
            _inventory = None
        print(_type, _make, _model, _serial, _property, _location, _inventory)
        tables = ["Surplus", "Other", "Errors"]
        if self.valltable.isChecked():
            for i in range(0, 3):
                lib.Search.search(_type, _make, _model, _serial, _inventory, _property, _location, tables[i])
        else:
            lib.Search.search(_type, _make, _model, _serial, _inventory, _property, _location)


