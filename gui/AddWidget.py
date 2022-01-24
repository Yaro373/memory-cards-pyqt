from gui.compiled.Ui_AddDeckWidget import Ui_AddDeckWidget
from PyQt5.QtWidgets import QWidget


class AddWidget(QWidget, Ui_AddDeckWidget):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
