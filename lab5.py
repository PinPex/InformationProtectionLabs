import hashlib
import math
import sys
from enum import Enum
from lab1 import get_prime, pow_mod, extended_euclidean_algorithm
from lab2 import generate_coprime

def inverse(n, p):
    gcd, inv, _ = extended_euclidean_algorithm(n, p)
    assert gcd == 1
    if inv < 0:
        inv += p
    return inv


class VOTE(Enum):
    YES = 1
    NO = 2
    ABSTAIN = 3

def get_hash(n):
    hash = hashlib.sha3_512(n.to_bytes(math.ceil(n.bit_length() / 8), byteorder=sys.byteorder))
    hash_16 = hash.hexdigest()
    hash_10 = int(hash_16, base=16)
    return hash, hash_16, hash_10

class Server:
    def __init__(self):
        p = q = get_prime(1 << 1023, (1 << 1024) - 1)
        while p == q:
            q = get_prime(1 << 1023, (1 << 1024) - 1)

        phi = (p - 1) * (q - 1)

        self.n = p * q
        self.d = generate_coprime(phi)  # Открытый ключ
        self._c = inverse(self.d, phi)  # Закрытый ключ
        self._voted = set()
        self.votes = list()

        print(f"{p = }",
              f"{q = }",
              f"{phi = }",
              '-' * 10,
              f"{self.n = }",
              f"{self.d = }",
              f"{self._c = }",
              '*' * 30,
              "[SERVER] Сервер запущен",
              sep='\n'
              )

    def get_blank(self, name: str, hh: int) -> int:
        print(f"[SERVER] Пришел запрос на получение бюллетеня от {name}")
        if name in self._voted:
            print(f"[SERVER] Пользователь {name} уже проголосовал")
            return None
        else:
            print(f"[SERVER] Пользователю {name} отправлен бюллетень")
            self._voted.add(name)
            return pow_mod(hh, self._c, self.n)

    def set_blank(self, n: int, s: int) -> bool:
        print(f"[SERVER] Полечен бюллетень")

        _, _, hash_10 = get_hash(n)

        if hash_10 == pow_mod(s, self.d, self.n):
            self.votes.append((n, s))
            print(f'[SERVER] Полученный бюллетень успешно прошел проверку и был принят')

            return True
        else:
            print(f'[SERVER] Полученный бюллетень не прошел проверку и был отклонён')
            print(f"\t{hash_10} = ", f"\t{pow_mod(s, self.d, self.n)} = ", sep='\n')
            return False

    def voting_results(self):
        votes = dict([(i, 0) for i in VOTE])
        print(votes)
        print(self.votes)
        for n, s in self.votes:
            votes[VOTE(n & ((1 << len(VOTE)) - 1))] += 1
        print("[SERVER] Текущие итоги голосования:")
        print(*(f"\t{key.name} = {value}" for key, value in votes.items()), sep='\n')

    def vote_table(self):
        print("№\tn\ts")
        for i in range(len(self.votes)):
            h1 = hash(self.votes[i][0])
            h2 = hash(self.votes[i][1])
            print(f"{i + 1}\t{h1}\t{h2}")



class Client:
    def __init__(self, server: Server, name: str = 'Clint'):
        self.server = server
        self.name = name

    def vote(self, vote: VOTE):
        # Хэширование голоса и запрос бюллетеня
        rnd = get_prime(1 << 511, (1 << 512) - 1)
        n = rnd << 512 | vote.value


        r = generate_coprime(self.server.n)

        _, _, hash_10 = get_hash(n)

        hh = hash_10 * pow_mod(r, self.server.d, self.server.n) % self.server.n

        ss = self.server.get_blank(self.name, hh)

        if ss:
            # Вычисление подписи бюллетеня
            s = ss * inverse(r, self.server.n) % self.server.n

            # Отправка голоса на сервер
            if self.server.set_blank(n, s):
                print(f"[CLIENT] {self.name}, Ваш бюллетень принят")
            else:
                print(f"[CLIENT] {self.name}, Ваш бюллетень не прошел проверку на сервере и не был принят")

        else:
            print(f"[CLIENT] {self.name}, Вы уже проголосовали")



def lab5_launch():
    server = Server()

    client = Client(server, 'Алиса')
    client.vote(VOTE.YES)

    client = Client(server, 'Алина')
    client.vote(VOTE.YES)

    client = Client(server, 'Боб')
    client.vote(VOTE.NO)

    client = Client(server, 'Поп')
    client.vote(VOTE.YES)

    client = Client(server, 'Иваныч')
    client.vote(VOTE.ABSTAIN)

    server.vote_table()

    client = Client(server, 'Иваныч')
    client.vote(VOTE.ABSTAIN)

    client = Client(server, 'Петрович')
    client.vote(VOTE.ABSTAIN)

    server.vote_table()