import AppParameters
from model.Deck import Deck
import datetime
import sqlite3
import os


class Card:
    def __init__(self, card_id):
        data = self.get_data_by_card_id(card_id)

        self.card_id = card_id
        self.description = data[1]
        self.deck = Deck(data[2])
        self.front_side_html = data[3]
        self.reverse_side_html = data[4]
        self.date = datetime.date(*map(int, data[5].split('-')))
        self.images = [] if data[6] is None else data[6].split(';')
        self.n = data[7]
        self.ef = data[8]
        self.i = data[9]

    # Получение информации о карте из базы данных по идентификатору
    @staticmethod
    def get_data_by_card_id(id_val):
        con = sqlite3.connect(AppParameters.PATH_TO_DATABASE)
        cur = con.cursor()
        data = cur.execute("SELECT * FROM cards WHERE id=?", (id_val,)).fetchone()
        con.close()
        return data

    # Проверка, нуждается ли карта в повторении
    def is_need_to_repeat(self):
        return (datetime.date.today() - self.date).days >= self.i

    def get_card_id(self):
        return self.card_id

    def get_description(self):
        return self.description

    def get_deck(self):
        return self.deck

    def get_repeat_data(self):
        return self.n, self.ef, self.i

    def get_front_side_html(self):
        return self.front_side_html

    def get_reverse_side_html(self):
        return self.reverse_side_html

    # Сохраняет данные для повторённой карты
    def set_repeat_data(self, n, ef, i):
        self.n = n
        self.ef = ef
        self.i = i
        con = sqlite3.connect(AppParameters.PATH_TO_DATABASE)
        cur = con.cursor()
        cur.execute('UPDATE cards SET n=?, EF=?, I=? WHERE id=?', (self.n, self.ef, self.i,
                                                                   self.card_id))
        con.commit()
        con.close()

    # Получение текста, парсинг описания и его сохранение
    def set_description_by_text(self, text):
        self.description = self.parse_description(text)
        con = sqlite3.connect(AppParameters.PATH_TO_DATABASE)
        cur = con.cursor()
        cur.execute('UPDATE cards SET description=? WHERE id=?',
                    (self.description, self.card_id))
        con.commit()
        con.close()
        return self.description

    def set_front_side_html(self, html):
        self.front_side_html = html
        con = sqlite3.connect(AppParameters.PATH_TO_DATABASE)
        cur = con.cursor()
        cur.execute('UPDATE cards SET front_html=? WHERE id=?',
                    (self.front_side_html, self.card_id))
        con.commit()
        con.close()

    def set_reverse_side_html(self, html):
        self.reverse_side_html = html
        con = sqlite3.connect(AppParameters.PATH_TO_DATABASE)
        cur = con.cursor()
        cur.execute('UPDATE cards SET reverse_html=? WHERE id=?',
                    (self.reverse_side_html, self.card_id))
        con.commit()
        con.close()

    # Удаляет карту
    def delete(self):
        con = sqlite3.connect(AppParameters.PATH_TO_DATABASE)
        cur = con.cursor()
        cur.execute("DELETE FROM cards WHERE id=?", (self.card_id,))
        con.commit()
        con.close()
        for path in self.images:
            if path != '':
                os.remove(path)
        self.deck.decrement_statistics_2(self.n)

    # Сохраняет в базе данных путь к загруженному изображение
    def save_image(self, name):
        con = sqlite3.connect(AppParameters.PATH_TO_DATABASE)
        cur = con.cursor()
        result = cur.execute('SELECT images FROM cards WHERE id=? LIMIT 1', (self.card_id,)) \
            .fetchone()[0]
        result += f';{name}'
        cur.execute("UPDATE cards SET images=? WHERE id=?", (result, self.card_id, ))
        con.commit()
        con.close()
        self.images.append(name)

    # Парсит текст лицевой стороны и возвращает заголовок
    @staticmethod
    def parse_description(text):
        max_length = 16
        if len(text) > max_length:
            result = ' '.join(text[:max_length].split()[:-1])
            if len(result) == 0:
                return text[:13] + '...'
            return result
        return text


class CardCreator:
    @classmethod
    def create_card(cls, deck):
        con = sqlite3.connect(AppParameters.PATH_TO_DATABASE)
        cur = con.cursor()

        # Получаем текущий максимальный идентификатор, вычисляем новый
        max_id = cur.execute('SELECT MAX(id) FROM cards').fetchone()
        new_id = 1 if max_id[0] is None else (max_id[0] + 1)

        cur.execute('INSERT INTO cards(id, description, deck, date) VALUES(?, "", ?, ?)',
                    (new_id, deck.get_deck_id(), datetime.date.today(),))
        con.commit()
        con.close()

        deck.increment_statistics_2(0)

        return Card(new_id)
