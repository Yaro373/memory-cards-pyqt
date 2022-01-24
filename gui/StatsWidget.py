import AppParameters
from PyQt5.QtWidgets import QLabel, QWidget
from PyQt5.QtGui import QPixmap
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os


class StatsWidget(QWidget):
    def __init__(self, deck):
        super().__init__()

        self.DEFAULT_WIDTH = 1350
        self.DEFAULT_HEIGHT = 500
        self.deck = deck
        self.initUI()

    def initUI(self):
        self.setGeometry(300, 300, self.DEFAULT_WIDTH, self.DEFAULT_HEIGHT)
        self.setMaximumSize(self.DEFAULT_WIDTH, self.DEFAULT_HEIGHT)
        self.setWindowTitle('Статистика')

        path_1 = self.prepare_stats_1()
        path_2 = self.prepare_stats_2()

        self.pixmap_1 = QPixmap(path_1)
        self.image_1 = QLabel(self)
        self.image_1.move(0, 0)
        self.image_1.resize(700, 500)
        self.image_1.setPixmap(self.pixmap_1)

        self.pixmap_2 = QPixmap(path_2)
        self.image_2 = QLabel(self)
        self.image_2.move(700, 0)
        self.image_2.resize(700, 500)
        self.image_2.setPixmap(self.pixmap_2)

    def prepare_stats_1(self):
        df = pd.read_csv(self.deck.path_to_statistics_1, delimiter=';')

        path = os.path.join(AppParameters.PATH_TO_STATS_IMAGES, 'stats_1.png')
        bp = sns.barplot(data=df, x='pos', y='count')
        bp.set_yticks(range(0, max(10, max(list(df['count']))) + 11,
                            max(10, max(list(df['count']))) // 10 + 1))
        bp.set(xlabel='ответы', ylabel='количество')
        fig = bp.get_figure()
        fig.savefig(path)
        plt.gcf().clear()

        return path

    def prepare_stats_2(self):
        df = pd.read_csv(self.deck.path_to_statistics_2, delimiter=';')

        path = os.path.join(AppParameters.PATH_TO_STATS_IMAGES, 'stats_2.png')
        bp = sns.barplot(data=df, x='n', y='count')
        bp.set_yticks(range(0, max(10, max(list(df['count']))) + 11,
                            max(10, max(list(df['count']))) // 10 + 1))
        bp.set(xlabel='этапы', ylabel='количество')
        fig = bp.get_figure()
        fig.savefig(path)
        plt.gcf().clear()

        return path
