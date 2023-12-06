import copy

from lab1 import get_prime, is_prime, extended_euclidean_algorithm, pow_mod
from lab2 import generate_coprime
import random

from PyQt6.QtWidgets import QMainWindow, QApplication, QMessageBox
from PyQt6.QtGui import QPixmap, QIcon
from PyQt6.QtCore import Qt
from PyQt6 import uic
import sys

def throwMessageBox(self, windowTitle: str, message: str):
    mes = QMessageBox(self)
    mes.show()
    mes.setWindowTitle(windowTitle)
    mes.setText(message)

class Player:
    def __init__(self, p):
        self.gen_keys(p)
    def gen_keys(self, p):
        C_temp = generate_coprime(p - 1)
        D_temp = extended_euclidean_algorithm(C_temp, p - 1)[1]
        if D_temp < 0:
            D_temp += (p - 1)
        self.__D = C_temp
        self.__C = D_temp
    def decode(self, num, p):
        return pow_mod(num, self.__D, p)
    def encode(self, num, p):
        return pow_mod(num, self.__C, p)

class MentalPoker(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi('pokerMainWindow.ui', self)
        self.__textures_path = "images/textures/"
        self.__images_path = "images/pokerImages/"
        self.__icons_path = "images/windowTitles/"

        self.setWindowIcon(QIcon(self.__icons_path + "card-game.png"))

        self.setStyleSheet("QLabel#playerLabel{color: white}"
                           "QMainWindow#MainWindow{background-image:url('" + self.__textures_path + "poker-table.jpg')}"
                           "QLabel#playersCountLabel{color: white}")

        self.show()

        self.__generate_keys()
        self.__original_deck = self.__gen_deck()
        self.__players = []
        self.__current_player = 0

        self.prevButton.clicked.connect(self.__prevButton_clicked)
        self.nextButton.clicked.connect(self.__nextButton_clicked)
        self.recastButton.clicked.connect(self.__recastButton_clicked)

    def __prevButton_clicked(self):
        if len(self.__players) == 0:
            return
        self.__current_player -= 1
        if self.__current_player < 0:
            self.__current_player = len(self.__players) - 1
        self.__setPlayer(self.__current_player)

    def __nextButton_clicked(self):
        if len(self.__players) == 0:
            return
        self.__current_player += 1
        if self.__current_player > len(self.__players) - 1:
            self.__current_player = 0
        self.__setPlayer(self.__current_player)

    def __recastButton_clicked(self):
        self.__current_player = 0

        self.__deck_keys = list(self.__original_deck.keys())

        if len(self.playersCountLineEdit.text()) != 0:
            self.__players = [Player(self.__p) for _ in range(int(self.playersCountLineEdit.text()))]
        else:
            throwMessageBox(self, "Ошибка", "Введите количество игроков.")
            return

        if int(self.playersCountLineEdit.text()) > 10:
            throwMessageBox(self, "Ошибка", "Слишком большое количество игроков.\n"
                                            "Игроков должно быть не больше 10.")
            return

        self.__deck_encoding()

        self.__hands = list()

        self.__get_cards_2_sametime()

        self.__table = self.__deck_keys[:5]

        self.__setTable()
        self.__setPlayer(0)

    def __setCard(self, label, image_path):
        pixmap = QPixmap(image_path)
        pixmap = pixmap.scaled(label.size(), aspectRatioMode=Qt.AspectRatioMode.KeepAspectRatio)
        label.setPixmap(pixmap)

    def __setPlayer(self, player_num):
        card_player = self.__decode_cards(player_num)
        self.__setCard(self.hiddenCard_1, QPixmap(self.__images_path + str(card_player[0]) + '.png'))
        self.__setCard(self.hiddenCard_2, QPixmap(self.__images_path + str(card_player[1]) + '.png'))
        self.playerLabel.setText(f"Player №{player_num + 1}")

    def __setTable(self):
        table = self.__decode_table()
        self.__setCard(self.sharedCard_1, QPixmap(self.__images_path + str(table[0]) + '.png'))
        self.__setCard(self.sharedCard_2, QPixmap(self.__images_path + str(table[1]) + '.png'))
        self.__setCard(self.sharedCard_3, QPixmap(self.__images_path + str(table[2]) + '.png'))
        self.__setCard(self.sharedCard_4, QPixmap(self.__images_path + str(table[3]) + '.png'))
        self.__setCard(self.sharedCard_5, QPixmap(self.__images_path + str(table[4]) + '.png'))

    def __decode_cards(self, player_num):
        cards = copy.deepcopy(self.__hands[player_num])
        for player in self.__players:
            for i in range(len(cards)):
                cards[i] = player.decode(cards[i], self.__p)
        hand = [self.__original_deck[key] for key in cards]
        return hand

    def __gen_deck(self) -> dict:
        faces = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12']
        suits = ['0', '1', '2', '3']
        cards = [face + suit for face in faces for suit in suits]

        return {i: cards[i - 2] for i in range(2, 54)}

    def __generate_keys(self):
        while True:
            q = get_prime(0, 10 ** 9)
            self.__p = 2 * q + 1
            if is_prime(self.__p):
                break

    def __deck_encoding(self):
        for player in self.__players:
            self.__deck_keys = [player.encode(j, self.__p) for j in self.__deck_keys]
            random.shuffle(self.__deck_keys)

    def __get_cards_2_sametime(self):
        for i in range(len(self.__players)):
            self.__hands.append([])
            for j in range(2):
                card = self.__deck_keys[j]
                self.__deck_keys.remove(card)
                self.__hands[i].append(card)

    def __decode_table(self):
        table = copy.deepcopy(self.__table)
        for player in self.__players:
            table = [player.decode(table[j], self.__p) for j in range(len(table))]
        table = [self.__original_deck[key] for key in table]
        return table

def lab4_launch():
    app = QApplication(sys.argv)
    window = MentalPoker()

    window.show()
    app.exec()