import AppParameters
from PyQt5.QtWidgets import QFileDialog, QMessageBox, QWidget
from PIL import Image
import pathlib
import time
import os
from gui.compiled.Ui_CardRedactorWidget import Ui_CardRedactorWidget
from model.Card import CardCreator


class CardRedactorWidget(Ui_CardRedactorWidget, QWidget):
    def __init__(self, deck_id, card):
        super().__init__()
        self.setupUi(self)

        self.card = card
        self.is_redact = False
        self.images = []

        if card is not None:
            self.frontSideEditor.setText(card.get_front_side_html())
            self.reverseSideEditor.setText(card.get_reverse_side_html())
            self.is_redact = True

        self.deck_id = deck_id
        self.main_window = self.sender().window()

        self.is_front_text_html = True
        self.is_reverse_text_html = True
        self.front_html = ''
        self.reverse_html = ''
        self.saved = False

        self.addImageToFrontPushButton.clicked.connect(self.add_image_to_front_push_button_action)
        self.addImageToReversePushButton.clicked.connect(
            self.add_image_to_reverse_push_button_action
        )
        self.boldTextFrontPushButton.clicked.connect(self.bold_text_front_push_button_action)
        self.italicTextFrontPushButton.clicked.connect(self.italic_text_front_push_button_action)
        self.underlinedTextFrontPushButton.clicked.connect(
            self.underlined_text_front_push_button_action
        )
        self.boldTextReversePushButton.clicked.connect(self.bold_text_reverse_push_button_action)
        self.italicTextReversePushButton.clicked.connect(
            self.italic_text_reverse_push_button_action
        )
        self.underlinedTextReversePushButton.clicked.connect(
            self.underlined_text_reverse_push_button_action
        )

        self.htmlToFromTextFrontPushButton.clicked.connect(
            self.html_to_from_text_front_push_button_action
        )
        self.htmlToFromTextReversePushButton.clicked.connect(
            self.html_to_from_text_reverse_push_button_action
        )
        self.savePushButton.clicked.connect(self.save_push_button_action)

    def closeEvent(self, event):
        if not self.saved and self.card is not None:
            self.save_push_button_action()

    # Сохранение карты
    def save_push_button_action(self):
        if self.card is None:
            self.card = CardCreator.create_card(self.deck_id)

        for path in self.images:
            self.card.save_image(path)

        self.card.set_front_side_html(self.frontSideEditor.toHtml() if self.front_html == ''
                                      else self.front_html)
        self.card.set_reverse_side_html(self.reverseSideEditor.toHtml() if self.reverse_html == ''
                                        else self.reverse_html)

        description = self.card.set_description_by_text(self.frontSideEditor.toPlainText())
        if self.is_redact:
            self.main_window.change_description(description)
        else:
            self.main_window.add_new_card_widget(self.card)
        self.saved = True
        self.close()

    # Преобразование html в текст и обратно на лицевой стороне
    def html_to_from_text_front_push_button_action(self):
        if self.is_front_text_html:
            self.front_html = self.frontSideEditor.toHtml()
            text = self.frontSideEditor.toPlainText().replace('\n', '<br>')
            self.frontSideEditor.clear()
            self.frontSideEditor.insertHtml(text)
            self.frontSideEditor.setReadOnly(True)
            self.frontSideEditor.setStyleSheet("background-color: rgb(240, 240, 240);")
            self.is_front_text_html = False
            self.htmlToFromTextFrontPushButton.setText('HTML')
        else:
            self.frontSideEditor.clear()
            self.frontSideEditor.setHtml(self.front_html)
            self.frontSideEditor.setReadOnly(False)
            self.frontSideEditor.setStyleSheet("background-color: rgb(255, 255, 255);")
            self.is_front_text_html = True
            self.htmlToFromTextFrontPushButton.setText('Text')

    # Преобразование html в текст и обратно на оборотной стороне
    def html_to_from_text_reverse_push_button_action(self):
        if self.is_reverse_text_html:
            self.reverse_html = self.reverseSideEditor.toHtml()
            text = self.reverseSideEditor.toPlainText().replace('\n', '<br>')
            self.reverseSideEditor.clear()
            self.reverseSideEditor.insertHtml(text)
            self.reverseSideEditor.setReadOnly(True)
            self.reverseSideEditor.setStyleSheet("background-color: rgb(240, 240, 240);")
            self.is_reverse_text_html = False
            self.htmlToFromTextReversePushButton.setText('HTML')
        else:
            self.reverseSideEditor.clear()
            self.reverseSideEditor.setHtml(self.reverse_html)
            self.reverseSideEditor.setReadOnly(False)
            self.reverseSideEditor.setStyleSheet("background-color: rgb(255, 255, 255);")
            self.is_reverse_text_html = True
            self.htmlToFromTextReversePushButton.setText('Text')

    def bold_text_front_push_button_action(self):
        self.frontSideEditor.insertPlainText('<b></b>')

    def italic_text_front_push_button_action(self):
        self.frontSideEditor.insertPlainText('<em></em>')

    def underlined_text_front_push_button_action(self):
        self.frontSideEditor.insertPlainText('<u></u>')

    def bold_text_reverse_push_button_action(self):
        self.reverseSideEditor.insertPlainText('<b></b>')

    def italic_text_reverse_push_button_action(self):
        self.reverseSideEditor.insertPlainText('<em></em>')

    def underlined_text_reverse_push_button_action(self):
        self.reverseSideEditor.insertPlainText('<u></u>')

    # Добавление изображения на лицевую сторону
    def add_image_to_front_push_button_action(self):
        if self.reverseSideEditor.isReadOnly():
            return
        result = QFileDialog.getOpenFileName(self, 'Выбрать изображение', '',
                                             'Изображение (*.png);; Изображение (*.jpg)')
        if result[0] == '':
            return
        if os.stat(result[0]).st_size > AppParameters.MAX_IMAGE_BYTES_SIZE:
            self.showInformBox()

        image_path = self.prepare_image(result[0])
        self.images.append(image_path)
        self.frontSideEditor.insertPlainText(f'<img src="{image_path}"/>')

    # Добавление изобржения на оборотную стоону
    def add_image_to_reverse_push_button_action(self):
        if self.reverseSideEditor.isReadOnly():
            return
        result = QFileDialog.getOpenFileName(self, 'Выбрать изображение', '',
                                             'Изображение (*.png);; Изображение (*.jpg)')
        if result[0] == '':
            return
        if os.stat(result[0]).st_size > AppParameters.MAX_IMAGE_BYTES_SIZE:
            self.showInformBox()

        image_path = self.prepare_image(result[0])
        self.images.append(image_path)
        self.reverseSideEditor.insertPlainText(f'<img src="{image_path}"/>')

    # Сохранение изображения в файловой системе и, если необходимо, уменьшение его размеров
    @staticmethod
    def prepare_image(path):
        max_size = 450

        img = Image.open(path)
        width, height = img.size
        if width > max_size:
            relation = width / height
            img = img.resize((max_size, int(max_size * relation)))
        elif height > max_size:
            relation = height / width
            img = img.resize((int(max_size * relation), max_size))
        image_name = f'{int(time.time() * 1000)}{pathlib.Path(path).suffix}'
        new_path = os.path.join(AppParameters.PATH_TO_IMAGES, image_name)
        img.save(new_path)
        return new_path

    # Предупреждение о превышении весом изображения максимального
    @staticmethod
    def showInformBox():
        inform_box = QMessageBox()
        inform_box.setText(f'Размер выбранной вами фотографии превышает максимальный - '
                           f'{AppParameters.MAX_IMAGE_BYTES_SIZE // (1024 * 1024)} МБ')
        inform_box.setWindowTitle('Сообщение')
        inform_box.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
        inform_box.exec()
