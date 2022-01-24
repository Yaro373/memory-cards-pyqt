from gui.compiled.Ui_CardWidget import Ui_CardWidget
from PyQt5.QtWidgets import QWidget


class CardWidget(QWidget, Ui_CardWidget):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
