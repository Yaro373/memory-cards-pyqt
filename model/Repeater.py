import AppParameters
from model.Card import Card
import sqlite3
import random


class Repeater:
    def __init__(self, deck):
        self.deck = deck
        self.bad_cards = []
        self.cards_to_repeat = []
        self.repeating_card = None
        self.set_data()

    # Иницализация данных
    def set_data(self):
        con = sqlite3.connect(AppParameters.PATH_TO_DATABASE)
        cur = con.cursor()
        cards_id = cur.execute("SELECT id FROM cards WHERE deck=?",
                               (self.deck.get_deck_id(),)).fetchall()
        for id_val in cards_id:
            card = Card(id_val[0])
            if card.is_need_to_repeat():
                self.cards_to_repeat.append(card)
        random.shuffle(self.cards_to_repeat)

    # Возвращает следующую карту для повторения
    def next_repeat_step(self):
        if len(self.cards_to_repeat) == 0:
            self.cards_to_repeat = self.bad_cards[:]
            self.bad_cards.clear()
            random.shuffle(self.cards_to_repeat)
            return None
        self.repeating_card = self.cards_to_repeat.pop(0)
        return self.repeating_card

    # Обновляет данные для повторённой карты
    def set_result_for_repeating_card(self, q):
        if q < 4:
            self.bad_cards.append(self.repeating_card)
        n, ef, i = self.memo_alg(*self.repeating_card.get_repeat_data(), q)
        self.repeating_card.set_repeat_data(n, ef, i)

    # Возвращает количество карт, которым пользователь поставил оценку меньше 4
    def get_count_of_bad_cards(self):
        return len(self.cards_to_repeat)

    # Алгоритм,вычисляющий новые данные для повторнной карты
    def memo_alg(self, n, ef, i, q):
        if n == 10:
            return
        if q > 3:
            if n == 0:
                i = 1
            elif n == 1:
                i = 6
            else:
                i = round(i * ef)
            self.deck.update_statistics_2(n, n + 1)
            n += 1
        else:
            self.deck.update_statistics_2(n, 0)
            n = 0
            i = 0
        ef = ef + (0.1 - (5 - q) * (0.08 + (5 - q) * 0.02))
        if ef < 1.3:
            ef = 1.3
        return n, ef, i
