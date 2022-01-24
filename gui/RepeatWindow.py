from gui.compiled.Ui_RepeatWindow import Ui_RepeatWindow
import gui.MainMenuWindow
import model.Repeater
from PyQt5.QtWidgets import QMainWindow, QMessageBox, QPushButton


class RepeatWindow(QMainWindow, Ui_RepeatWindow):
    def __init__(self, deck, size_val=(-1, -1), pos_val=(-1, -1)):
        super().__init__()
        self.setupUi(self)

        if size_val != (-1, -1):
            self.resize(size_val[0], size_val[1])
        if pos_val != (-1, -1):
            self.move(pos_val[0], pos_val[1])

        self.showAnswerPushButton.clicked.connect(self.show_answer)

        self.repeater = model.Repeater.Repeater(deck)
        self.deck = deck
        self.card = None

        self.zeroPushButton.clicked.connect(self.zero_button_action)
        self.onePushButton.clicked.connect(self.one_button_action)
        self.twoPushButton.clicked.connect(self.two_button_action)
        self.threePushButton.clicked.connect(self.three_button_action)
        self.fourPushButton.clicked.connect(self.four_button_action)
        self.fivePushButton.clicked.connect(self.five_button_action)
        self.goBackPushButton.clicked.connect(self.go_to_main_menu)

        self.play()

    def play(self):
        self.hide_buttons()
        self.showAnswerPushButton.show()
        self.frontSideTextBrowser.clear()
        self.reverseSideTextBrowser.clear()
        self.reverseSideTextBrowser.setStyleSheet('background-color: rgb(130, 130, 130);')
        self.card = self.repeater.next_repeat_step()
        if self.card is None:
            count_of_bad_cards = self.repeater.get_count_of_bad_cards()
            if count_of_bad_cards:
                inform_box = QMessageBox()
                w1, w2 = self.morph(count_of_bad_cards)
                inform_box.setText(f'Вы поставили оценку меньше 4 баллов {count_of_bad_cards} '
                                   f'{w1}. '
                                   f'Рекомендуем повторить {w2} снова.')
                inform_box.addButton(QPushButton('Repeat'), QMessageBox.YesRole)
                inform_box.addButton(QPushButton('Cancel'), QMessageBox.NoRole)
                inform_box.setWindowTitle('Сообщение')
                inform_box.setIcon(QMessageBox.Information)
                return_value = inform_box.exec()
                if return_value == 1:
                    self.go_to_main_menu()
                    return
                self.card = self.repeater.next_repeat_step()
            else:
                self.go_to_main_menu()
                return
        self.initialize_card()

    def hide_buttons(self):
        self.zeroPushButton.hide()
        self.onePushButton.hide()
        self.twoPushButton.hide()
        self.threePushButton.hide()
        self.fourPushButton.hide()
        self.fivePushButton.hide()

    def show_buttons(self):
        self.zeroPushButton.show()
        self.onePushButton.show()
        self.twoPushButton.show()
        self.threePushButton.show()
        self.fourPushButton.show()
        self.fivePushButton.show()

    def initialize_card(self):
        self.frontSideTextBrowser.setHtml(self.card.get_front_side_html())
        text = self.frontSideTextBrowser.toPlainText().replace('\n', '<br>')
        self.frontSideTextBrowser.clear()
        self.frontSideTextBrowser.insertHtml(text)

    def show_answer(self):
        self.reverseSideTextBrowser.setStyleSheet('background-color: rgb(255, 255, 255)')
        self.reverseSideTextBrowser.setHtml(self.card.get_reverse_side_html())
        text = self.reverseSideTextBrowser.toPlainText().replace('\n', '<br>')
        self.reverseSideTextBrowser.clear()
        self.reverseSideTextBrowser.insertHtml(text)
        self.show_buttons()

    def zero_button_action(self):
        self.update_card_info(0)
        self.play()

    def one_button_action(self):
        self.update_card_info(1)
        self.play()

    def two_button_action(self):
        self.update_card_info(2)
        self.play()

    def three_button_action(self):
        self.update_card_info(3)
        self.play()

    def four_button_action(self):
        self.update_card_info(4)
        self.play()

    def five_button_action(self):
        self.update_card_info(5)
        self.play()

    def update_card_info(self, val):
        self.repeater.set_result_for_repeating_card(val)
        self.deck.increment_statistics_1(val)

    def go_to_main_menu(self):
        self.main_window = gui.MainMenuWindow.MainMenuWindow(
            size_val=(self.width(), self.height()), pos_val=(self.x(), self.y())
        )
        self.main_window.show()
        self.close()

    @staticmethod
    def morph(num):
        if num == 1:
            return 'карте', 'её'
        if str(num)[-1] == '1' and str(num)[-2] != '1':
            return 'карте', 'их'
        return 'картам', 'их'
