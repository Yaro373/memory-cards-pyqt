import AppParameters
from gui.MainMenuWindow import MainMenuWindow
from PyQt5.QtWidgets import QApplication
import sqlite3
import sys
import os


def except_hook(cls, exception, traceback):
    sys.__excepthook__(cls, exception, traceback)


def check_directories():
    if not os.path.exists(AppParameters.PATH_TO_IMAGES):
        os.makedirs(os.path.join(os.getcwd(), AppParameters.PATH_TO_IMAGES))
    if not os.path.exists(AppParameters.PATH_TO_STATS_IMAGES):
        os.makedirs(os.path.join(os.getcwd(), AppParameters.PATH_TO_STATS_IMAGES))
    if not os.path.exists(AppParameters.PATH_TO_STATISTICS):
        os.makedirs(os.path.join(os.getcwd(), AppParameters.PATH_TO_STATISTICS))
    if not os.path.exists(AppParameters.PATH_TO_DATABASE):
        os.mkdir(os.path.split(AppParameters.PATH_TO_DATABASE)[0])
        open(AppParameters.PATH_TO_DATABASE, 'w', encoding='utf-8').close()
        con = sqlite3.connect(os.path.join(os.getcwd(),
                                           AppParameters.PATH_TO_DATABASE))
        cur = con.cursor()
        cur.execute('''CREATE TABLE "cards" (
            "id"	INTEGER NOT NULL UNIQUE,
            "description"	TEXT,
            "deck"	INTEGER NOT NULL,
            "front_html"	NUMERIC,
            "reverse_html"	INTEGER,
            "date"	TEXT,
            "images"	TEXT NOT NULL DEFAULT '',
            "n"	INTEGER NOT NULL DEFAULT 0,
            "EF"	REAL NOT NULL DEFAULT 2.5,
            "I"	INTEGER NOT NULL DEFAULT 0,
            PRIMARY KEY("id"),
            FOREIGN KEY("deck") REFERENCES "decks"("id") ON DELETE SET NULL);''')
        cur.execute('''CREATE TABLE "decks" (
            "id"	INTEGER NOT NULL UNIQUE,
            "name"	TEXT,
            "path_to_statistics_1"	TEXT,
            "path_to_statistics_2"	TEXT,
            PRIMARY KEY("id" AUTOINCREMENT)
        );''')
        con.close()


if __name__ == '__main__':
    check_directories()

    app = QApplication(sys.argv)
    sys.excepthook = except_hook
    start_window = MainMenuWindow()
    start_window.show()
    sys.exit(app.exec_())
