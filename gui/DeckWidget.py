from gui.compiled.Ui_DeckWidget import Ui_DeckWidget
from PyQt5.QtWidgets import QWidget


class DeckWidget(QWidget, Ui_DeckWidget):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

