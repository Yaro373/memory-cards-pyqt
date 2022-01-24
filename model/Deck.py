import AppParameters
import model
import pandas as pd
import sqlite3
import time
import csv
import os


class Deck:
    def __init__(self, deck_id):
        data = self.get_data_by_deck_id(deck_id)

        self.deck_id = deck_id
        self.name = data[1]
        self.path_to_statistics_1 = data[2]
        self.path_to_statistics_2 = data[3]

    @staticmethod
    def get_data_by_deck_id(id_val):
        con = sqlite3.connect(AppParameters.PATH_TO_DATABASE)
        cur = con.cursor()
        data = cur.execute('SELECT * FROM decks WHERE id=? LIMIT 1',
                           (id_val,)).fetchone()
        return data

    def get_deck_id(self):
        return self.deck_id

    def get_name(self):
        return self.name

    def get_path_to_statistics_1(self):
        return self.path_to_statistics_1

    def get_path_to_statistics_2(self):
        return self.path_to_statistics_2

    def get_count_of_cards(self):
        con = sqlite3.connect(AppParameters.PATH_TO_DATABASE)
        cur = con.cursor()
        data = cur.execute('SELECT id FROM cards WHERE deck=?', (self.deck_id, )).fetchall()
        con.commit()
        con.close()
        return len(data)

    # Возвращает количество карт, которые нужно повторить
    def get_count_of_cards_to_repeat(self):
        con = sqlite3.connect(AppParameters.PATH_TO_DATABASE)
        cur = con.cursor()
        data = cur.execute('SELECT id FROM cards WHERE deck=?', (self.deck_id, ))\
            .fetchall()
        con.commit()
        con.close()
        if data is None:
            return

        return list(map(lambda data_el: model.Card.Card(data_el[0]).is_need_to_repeat(), data))\
            .count(True)

    def set_name(self, name):
        self.name = name
        con = sqlite3.connect(AppParameters.PATH_TO_DATABASE)
        cur = con.cursor()
        cur.execute('UPDATE decks SET name=? WHERE id=?',
                    (self.name, self.deck_id))
        con.commit()
        con.close()
        return self.name

    # Увеличение значения количества выборов определённого ответа статистики 1
    def increment_statistics_1(self, answer):
        df = pd.read_csv(self.path_to_statistics_1, delimiter=';')
        df.at[answer, 'count'] = df.at[answer, 'count'] + 1
        df.to_csv(self.path_to_statistics_1, sep=';', index=False)

    # Уменьшение одного столбца и увеличение другого на единицу статистики 2
    def update_statistics_2(self, prev_n, n):
        df = pd.read_csv(self.path_to_statistics_2, delimiter=';')
        df.at[prev_n, 'count'] = df.at[prev_n, 'count'] - 1
        df.at[n, 'count'] = df.at[n, 'count'] + 1
        df.to_csv(self.path_to_statistics_2, index=False, sep=';')

    # Увеличение столбца на единицу статистики 2
    def increment_statistics_2(self, index):
        df = pd.read_csv(self.path_to_statistics_2, delimiter=';')
        df.at[index, 'count'] = df.at[index, 'count'] + 1
        df.to_csv(self.path_to_statistics_2, index=False, sep=';')

    # Уменьшение столбца на единицу статистики 2
    def decrement_statistics_2(self, index):
        df = pd.read_csv(self.path_to_statistics_2, delimiter=';')
        df.at[index, 'count'] = df.at[index, 'count'] - 1
        df.to_csv(self.path_to_statistics_2, index=False, sep=';')

    # Удаление колоды
    def delete(self):
        con = sqlite3.connect(AppParameters.PATH_TO_DATABASE)
        cur = con.cursor()
        cards_id = cur.execute('SELECT id FROM cards WHERE deck=?', (self.deck_id,)).fetchall()
        con.close()
        for id_val in cards_id:
            model.Card.Card(id_val[0]).delete()

        con = sqlite3.connect(AppParameters.PATH_TO_DATABASE)
        cur = con.cursor()
        cur.execute('DELETE FROM decks WHERE id=?', (self.deck_id,)).fetchall()
        con.commit()
        con.close()

        os.remove(self.path_to_statistics_1)
        os.remove(self.path_to_statistics_2)


class DeckCreator:
    @classmethod
    def create_deck(cls, name):
        # Запись начальных данных статистики 1
        stats_path_1 = os.path.join(AppParameters.PATH_TO_STATISTICS,
                                    f'{int(time.time() * 1000)}_1.csv')
        with open(stats_path_1, 'w', newline='') as stats_1:
            data = [{'pos': 0, 'count': 0},
                    {'pos': 1, 'count': 0},
                    {'pos': 2, 'count': 0},
                    {'pos': 3, 'count': 0},
                    {'pos': 4, 'count': 0},
                    {'pos': 5, 'count': 0}]
            writer = csv.DictWriter(
                stats_1, fieldnames=list(data[0].keys()),
                delimiter=';', quoting=csv.QUOTE_NONNUMERIC)
            writer.writeheader()
            for data_el in data:
                writer.writerow(data_el)

        # Запись начальных данных статистики 2
        stats_path_2 = os.path.join(AppParameters.PATH_TO_STATISTICS,
                                    f'{int(time.time() * 1000)}_2.csv')
        with open(stats_path_2, 'w', newline='') as stats_2:
            data = [{'n': 0, 'count': 0},
                    {'n': 1, 'count': 0},
                    {'n': 2, 'count': 0},
                    {'n': 3, 'count': 0},
                    {'n': 4, 'count': 0},
                    {'n': 5, 'count': 0},
                    {'n': 6, 'count': 0},
                    {'n': 7, 'count': 0},
                    {'n': 8, 'count': 0},
                    {'n': 9, 'count': 0},
                    {'n': 10, 'count': 0}]
            writer = csv.DictWriter(
                stats_2, fieldnames=list(data[0].keys()),
                delimiter=';', quoting=csv.QUOTE_NONNUMERIC)
            writer.writeheader()
            for data_el in data:
                writer.writerow(data_el)

        con = sqlite3.connect(AppParameters.PATH_TO_DATABASE)
        cur = con.cursor()

        # Получаем текущий максимальный идентификатор, вычисляем новый
        max_id = cur.execute('SELECT MAX(id) FROM decks').fetchone()
        new_id = 1 if max_id[0] is None else (max_id[0] + 1)

        cur.execute(f'INSERT INTO decks(id, name, path_to_statistics_1, '
                    f'path_to_statistics_2) VALUES (?, ?, ?, ?)', (new_id, name, stats_path_1,
                                                                   stats_path_2))
        con.commit()
        con.close()

        return Deck(new_id)
