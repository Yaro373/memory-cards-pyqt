import AppParameters
from gui.CardsWindow import CardsWindow
from gui.DeckWidget import DeckWidget
from gui.AddWidget import AddWidget
from model.Deck import DeckCreator
from model.Deck import Deck
import gui.RepeatWindow
import gui.StatsWidget
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QScrollArea, QWidget, QSizePolicy
from PyQt5.QtWidgets import QInputDialog, QMessageBox, QGridLayout, QPushButton
import sqlite3


class MainMenuWindow(QScrollArea):
    def __init__(self, size_val=(-1, -1), pos_val=(-1, -1)):
        super().__init__()

        self.size_val = size_val
        self.pos_val = pos_val

        self.SPACING = 15
        self.COLUMNS_COUNT = 4
        self.DEFAULT_WIDTH = 1200
        self.DEFAULT_HEIGHT = 750
        self.MINIMUM_WIDTH = 600
        self.WIDGET_MINIMUM_WIDTH = 200
        self.WIDGET_MINIMUM_HEIGHT = 350

        self.initUI()

    def initUI(self):
        self.setWindowTitle('Главное меню')
        if self.size_val != (-1, -1):
            self.resize(self.size_val[0], self.size_val[1])
        else:
            self.resize(self.DEFAULT_WIDTH, self.DEFAULT_HEIGHT)
        if self.pos_val != (-1, -1):
            self.move(self.pos_val[0], self.pos_val[1])
        self.setMinimumWidth(self.MINIMUM_WIDTH)

        self.widget_deck_dict = dict()
        self.widget_pos_info = dict()

        self.column = 0
        self.row = 0

        widget = QWidget()
        self.setWidgetResizable(True)
        self.setWidget(widget)
        self.main_layout = QGridLayout(widget)
        self.main_layout.setVerticalSpacing(self.SPACING)
        self.main_layout.setHorizontalSpacing(self.SPACING)
        self.main_layout.setAlignment(Qt.AlignTop)

        self.add_deck_widget = AddWidget()
        self.add_deck_widget.setMinimumSize(self.WIDGET_MINIMUM_WIDTH, self.WIDGET_MINIMUM_HEIGHT)
        self.add_deck_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.add_deck_widget.addPushButton.clicked.connect(self.add_new_deck_action)
        self.main_layout.addWidget(self.add_deck_widget, 0, 0)
        self.widget_pos_info[self.add_deck_widget] = (0, 0)

        con = sqlite3.connect(AppParameters.PATH_TO_DATABASE)
        cur = con.cursor()
        data = cur.execute('SELECT id, name FROM decks').fetchall()
        for info in data:
            self.add_new_deck_widget(Deck(info[0]))
        con.close()

    # Добавление новой колоды
    def add_new_deck_action(self):
        name, ok_pressed = QInputDialog.getText(self, 'Введите название колоды', 'Название колоды')
        if ok_pressed:
            deck = DeckCreator.create_deck(name)
            self.add_new_deck_widget(deck)

    # Добавление виджета новой колды
    def add_new_deck_widget(self, deck):
        dw = DeckWidget()
        dw.setMinimumSize(self.WIDGET_MINIMUM_WIDTH, self.WIDGET_MINIMUM_HEIGHT)
        dw.setMaximumHeight(self.WIDGET_MINIMUM_HEIGHT)
        dw.titleOfDeckTextBrowser.insertHtml(f'<div align="center">{deck.get_name()}</div>')
        dw.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        dw.deletePushButton.clicked.connect(self.delete_deck_action)
        dw.editPushButton.clicked.connect(self.rename_deck_action)
        dw.cardsOfDeckPushButton.clicked.connect(self.go_to_cards_of_deck_action)
        dw.playPushButton.clicked.connect(self.play_deck_action)
        dw.statsPushButton.clicked.connect(self.go_to_stats_push_button_action)

        count_of_cards_to_repeat = deck.get_count_of_cards_to_repeat()
        count_of_cards = deck.get_count_of_cards()
        dw.infoTextEdit.insertHtml(f'<div align="left" style="font-size: 12em">Всего: {count_of_cards} '
                                   f'{self.morph_card(count_of_cards)}</div><br>')
        if 0 < count_of_cards_to_repeat:
            dw.infoTextEdit.insertHtml(f'<div align="center"><b>Нужно повторить: '
                                       f'{count_of_cards_to_repeat} '
                                       f'{self.morph_card(count_of_cards_to_repeat)}'
                                       f'</b></div>')

        # Добавляем информацию о созданном виджете в словари, удаляем виджет создания новой карты,
        # добавляем созданный виджет
        self.widget_deck_dict[dw] = deck
        self.widget_pos_info[dw] = (self.row, self.column)
        self.main_layout.removeWidget(self.add_deck_widget)
        self.main_layout.addWidget(dw, self.row, self.column)

        # Обратно добавляем виджет создания новой карты
        self.row, self.column = self.transform_indexes(self.row, self.column)
        self.main_layout.addWidget(self.add_deck_widget, self.row, self.column)
        self.widget_pos_info[self.add_deck_widget] = (self.row, self.column)

    # Повторение карт колоды
    def play_deck_action(self):
        deck_to_play = self.widget_deck_dict[self.sender().parentWidget()]
        if deck_to_play.get_count_of_cards() == 0:
            inform_box = QMessageBox()
            inform_box.setText(f'В этой колоде нет карт.')
            inform_box.addButton(QPushButton('OK'), QMessageBox.YesRole)
            inform_box.setWindowTitle('Предупреждение')
            inform_box.setIcon(QMessageBox.Warning)
            inform_box.exec()
            return
        elif deck_to_play.get_count_of_cards_to_repeat() == 0:
            inform_box = QMessageBox()
            inform_box.setText(f'Вы повторили все карты в этой колоде.')
            inform_box.addButton(QPushButton('OK'), QMessageBox.YesRole)
            inform_box.setWindowTitle('Сообщение')
            inform_box.setIcon(QMessageBox.Information)
            inform_box.exec()
            return
        self.repeat_window = gui.RepeatWindow.RepeatWindow(
            deck_to_play, size_val=(self.width(), self.height()), pos_val=(self.x(), self.y())
        )
        self.repeat_window.show()
        self.close()

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

    # Удаление колоды
    def delete_deck_action(self):
        delete_confirm_box = QMessageBox()
        delete_confirm_box.setText(f"Вы уверены, что хотите удалить колоду?")
        delete_confirm_box.setWindowTitle("Подтверждение действия")
        delete_confirm_box.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
        return_value = delete_confirm_box.exec()
        if return_value == QMessageBox.Ok:
            widget_to_delete = self.sender().parentWidget()
            self.main_layout.removeWidget(widget_to_delete)
            widget_to_delete.deleteLater()

            deck = self.widget_deck_dict[widget_to_delete]
            deck.delete()
            self.widget_deck_dict.pop(widget_to_delete)

            # Смещение виджетов на одну позицию назад
            y, x = self.widget_pos_info[widget_to_delete]
            n_y, n_x = self.transform_indexes(y, x)
            for k, v in self.widget_pos_info.items():
                if v[0] > y or (v[0] == y and v[1] > x):
                    self.widget_pos_info[k] = self.transform_indexes(v[0], v[1], back=True)
            while (item := self.main_layout.itemAtPosition(n_y, n_x)) is not None:
                widget = item.widget()
                self.main_layout.addWidget(widget, y, x)
                y, x = n_y, n_x
                n_y, n_x = self.transform_indexes(y, x)
            self.row, self.column = self.transform_indexes(self.row, self.column, back=True)
            self.widget_pos_info.pop(widget_to_delete)

    # Переименование колоды
    def rename_deck_action(self):
        name, ok_pressed = QInputDialog.getText(self, 'Введите новое название колоды',
                                                'Название колоды')
        if ok_pressed:
            name = name[:40]
            deck_to_rename = self.widget_deck_dict[self.sender().parentWidget()]
            deck_to_rename.set_name(name)
            self.sender().parentWidget().titleOfDeckTextBrowser.clear()
            self.sender().parentWidget().titleOfDeckTextBrowser.insertHtml(
                f'<div align="center">{name}</div>'
            )

    # Переход к окну просмотра карт
    def go_to_cards_of_deck_action(self):
        deck = self.widget_deck_dict[self.sender().parentWidget()]
        self.new_window = CardsWindow(
            deck, size_val=(self.width(), self.height()), pos_val=(self.x(), self.y())
        )
        self.new_window.show()
        self.close()

    # Переход к окну просмотра статистики
    def go_to_stats_push_button_action(self):
        deck = self.widget_deck_dict[self.sender().parentWidget()]
        self.stats_window = gui.StatsWidget.StatsWidget(deck)
        self.stats_window.show()

    @staticmethod
    def morph_card(num):
        if num == 1 or (len(str(num)) > 1 and str(num)[-1] == '1' and str(num)[-2] != '1'):
            return 'карту'
        if num > 9 and str(num)[-2] == '1':
            return 'карт'
        if str(num)[-1] in ('2', '3', '4'):
            return 'карты'
        return 'карт'
