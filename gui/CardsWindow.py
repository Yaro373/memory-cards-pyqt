from PyQt5.QtWidgets import QSizePolicy, QMainWindow
from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtCore import Qt
from gui.CardRedactorWidget import CardRedactorWidget
from gui.CardWidget import CardWidget
from gui.AddWidget import AddWidget
from model.Card import Card
import AppParameters
import gui.MainMenuWindow
from gui.compiled.Ui_CardsWindow import Ui_CardsWindow
import sqlite3


class CardsWindow(QMainWindow, Ui_CardsWindow):

    def __init__(self, deck, size_val=(-1, -1), pos_val=(-1, -1)):
        super().__init__()
        self.setupUi(self)

        self.size_val = size_val
        self.pos_val = pos_val
        self.deck = deck

        self.column = 0
        self.row = 0

        self.SPACING = 15
        self.COLUMNS_COUNT = 6
        self.DEFAULT_WIDTH = 1200
        self.DEFAULT_HEIGHT = 750
        self.WIDGET_MINIMUM_WIDTH = 150
        self.WIDGET_MINIMUM_HEIGHT = 150

        # Словарь, связывающий виджет окна с идентификатором карты в базе данных
        self.widget_card_dict = dict()
        # Словарь, связывающий виджет окна с её позицией в GridLayout окна
        self.widget_pos_info = dict()

        self.initUI()

    def initUI(self):
        self.setWindowTitle('Список карт')
        if self.size_val == (-1, -1):
            self.resize(self.DEFAULT_WIDTH, self.DEFAULT_HEIGHT)
        else:
            self.resize(self.size_val[0], self.size_val[1])
        if self.pos_val != (-1, -1):
            self.move(self.pos_val[0], self.pos_val[1])

        self.goBackPushButton.clicked.connect(self.go_back_action)

        self.add_card_widget = AddWidget()
        self.add_card_widget.setMinimumSize(self.WIDGET_MINIMUM_WIDTH, self.WIDGET_MINIMUM_HEIGHT)
        self.add_card_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.add_card_widget.addPushButton.clicked.connect(self.add_new_card_action)
        self.main_layout.setAlignment(Qt.AlignTop)
        self.main_layout.addWidget(self.add_card_widget, 0, 0)
        self.widget_pos_info[self.add_card_widget] = (0, 0)

        con = sqlite3.connect(AppParameters.PATH_TO_DATABASE)
        cur = con.cursor()
        data = cur.execute('SELECT id FROM cards WHERE deck=?',
                                (self.deck.get_deck_id(),)).fetchall()
        for data_el in data:
            self.add_new_card_widget(Card(data_el[0]))
        con.close()

    # Добавление карты
    def add_new_card_action(self):
        self.redactor = CardRedactorWidget(self.deck, None)
        self.redactor.show()

    # Редактирование карты
    def redact_card_action(self):
        self.sender_widget = self.sender().parentWidget()
        card = self.widget_card_dict[self.sender_widget]
        self.redactor = CardRedactorWidget(self.deck, card)
        self.redactor.show()

    # Удаление карты
    def delete_card_action(self):
        delete_confirm_box = QMessageBox()
        delete_confirm_box.setText(f"Вы уверены, что хотите удалить карту?")
        delete_confirm_box.setWindowTitle("Подтверждение действия")
        delete_confirm_box.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
        return_value = delete_confirm_box.exec()

        if return_value == QMessageBox.Ok:
            widget_to_delete = self.sender().parentWidget()
            self.main_layout.removeWidget(widget_to_delete)
            widget_to_delete.deleteLater()

            self.widget_card_dict[widget_to_delete].delete()
            self.widget_card_dict.pop(widget_to_delete)

            # Сдвигаем все следующие за удаленным виджетом на одну позицию влево
            y, x = self.widget_pos_info[widget_to_delete]
            n_y, n_x = self.transform_indexes(y, x)
            for k, v in self.widget_pos_info.items():
                if v[0] > y or (v[0] == y and v[1] > x):
                    self.widget_pos_info[k] = self.transform_indexes(v[0], v[1], back=True)
            while (item := self.main_layout.itemAtPosition(n_y, n_x)) is not None:
                widget = item.widget()
                self.main_layout.addWidget(widget, y, x)
                y, x = n_y, n_x
                n_y, n_x = self.transform_indexes(n_y, n_x)
            self.row, self.column = self.transform_indexes(self.row, self.column, back=True)
            self.widget_pos_info.pop(widget_to_delete)

    # Возврат в главное меню
    def go_back_action(self):
        self.main_menu_window = gui.MainMenuWindow.MainMenuWindow(
            size_val=(self.width(), self.height()), pos_val=(self.x(), self.y())
        )
        self.main_menu_window.show()
        self.close()

    # Меняет описание у последнего использованного виджета
    def change_description(self, new_description):
        self.sender_widget.titleOfDeckTextBrowser.clear()
        self.sender_widget.titleOfDeckTextBrowser.insertHtml(
            f'<div align="center">{new_description}</div>')

    # Добавяет виджет, соответствующий карте
    def add_new_card_widget(self, card):
        dw = CardWidget()
        dw.setMinimumSize(self.WIDGET_MINIMUM_WIDTH, self.WIDGET_MINIMUM_HEIGHT)
        dw.setMaximumHeight(self.WIDGET_MINIMUM_HEIGHT)
        dw.titleOfDeckTextBrowser.insertHtml(f'<div align="center">{card.get_description()}</div>')
        dw.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        dw.deletePushButton.clicked.connect(self.delete_card_action)
        dw.editPushButton.clicked.connect(self.redact_card_action)

        # Добавляем информацию о созданном виджете в словари, удаляем виджет создания новой карты,
        # добавляем созданный виджет
        self.widget_card_dict[dw] = card
        self.widget_pos_info[dw] = (self.row, self.column)
        self.main_layout.removeWidget(self.add_card_widget)
        self.main_layout.addWidget(dw, self.row, self.column)

        # Обратно добавляем виджет создания новой карты
        self.row, self.column = self.transform_indexes(self.row, self.column)
        self.main_layout.addWidget(self.add_card_widget, self.row, self.column)
        self.widget_pos_info[self.add_card_widget] = (self.row, self.column)

    # Функция для получения следующей/предыдущей позиции в GridLayout относительно текущих виджетов
    # Если back=True, то возвращается предыдущая позиция, иначе - следующая
    def transform_indexes(self, y_arg, x_arg, back=False):
        if back:
            x_arg -= 1
            if x_arg < 0:
                y_arg -= 1
                x_arg = self.COLUMNS_COUNT - 1
            return y_arg, x_arg
        x_arg = (x_arg + 1) % self.COLUMNS_COUNT
        if x_arg == 0:
            y_arg += 1
        return y_arg, x_arg
