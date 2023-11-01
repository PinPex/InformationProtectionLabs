from lab1 import *
from lab2 import generate_coprime, convert_ascii_str, convert_str_ascii
import hashlib
import random
import sys

class RSA_keys:
    def __init__(self, Ni, Di, Ci):
        self.N = Ni
        self.D = Di
        self.C = Ci
class ElGamal_global_keys:
    def __init__(self, p, g):
        self.p = p
        self.g = g
class GOST_global_keys:
    def __init__(self, p, q, a):
        self.p = p
        self.q = q
        self.a = a

class ElGamal_keys:
    def __init__(self, x, y):
        self.x = x
        self.y = y
def generate_ElGamal_keys(global_keys: ElGamal_global_keys):
    x = get_prime(0, global_keys.p - 1)
    y = pow_mod(global_keys.g, x, global_keys.p)
    return ElGamal_keys(x, y)

def generate_ElGamal_global_keys():
    g = 0
    while True:
        q = get_prime(0, 10 ** 9)
        p = 2 * q + 1
        if is_prime(p):
            break
    while pow_mod(g, q, p) != 1:
        g = random.randint(2, p - 1)
    return ElGamal_global_keys(p, g)

class ElGamal_signed:
    def __init__(self, m, r, s):
        self.m = m
        self.r = r
        self.s = s
def sign_ElGamal(m, keys: ElGamal_keys, glob_keys: ElGamal_global_keys):
    k = generate_coprime(glob_keys.p - 1)
    r = pow_mod(glob_keys.g, k, glob_keys.p)
    h = hashlib.md5(m).hexdigest()
    h_b = ''.join(str(pow_mod(glob_keys.g, int(i, 16), glob_keys.p)) for i in h)
    print(f"Before encoding: g^h % p = {h_b}")
    u = [(int(i, 16) - keys.x * r) % (glob_keys.p - 1) for i in h]
    s = [(extended_euclidean_algorithm(k, glob_keys.p - 1)[1] * i) % (glob_keys.p - 1) for i in u]
    return ElGamal_signed(m,r,s)
def check_sign_ElGamal(m_signed: ElGamal_signed, glob_keys: ElGamal_global_keys, y):
    h = hashlib.md5(m_signed.m).hexdigest()
    h_b = ''.join(str(pow_mod(glob_keys.g, int(i, 16), glob_keys.p)) for i in h)
    print(f"Before decoding: g^h % p = {h_b}")
    res = ''.join(str(pow_mod(y, m_signed.r, glob_keys.p) * pow_mod(m_signed.r, i, glob_keys.p) % glob_keys.p) for i in m_signed.s)
    print(f"Decoding: (y^r % p) * (r ^ s % p) % p = {res}")
    return h_b == res

def sign_ElGamal_launch(m):
    global_keys = generate_ElGamal_global_keys()
    alice_keys = generate_ElGamal_keys(global_keys)
    signed_text = sign_ElGamal("bla bla bla".encode("utf-8"), alice_keys, global_keys)
    print(check_sign_ElGamal(signed_text, global_keys, alice_keys.y))
    pass

def generate_RSA_keys():
    while True:
        Pi = get_prime(0, 10 ** 9)
        Qi = get_prime(0, 10 ** 9)
        if Pi != Qi:
            break

    Ni = Pi * Qi
    Phii = (Pi - 1) * (Qi - 1)
    Di = generate_coprime(Phii)
    Ci = extended_euclidean_algorithm(Di, Phii)[1]

    if Ci < 0:
        Ci += Phii
    return RSA_keys(Ni, Di, Ci)

def sign_RSA(m, C, N):
    y = hashlib.md5(m).hexdigest()
    y_int = ''.join(str(int(i, 16)) for i in y)
    print(f"Hash before encoding: {y_int}")
    s = [pow_mod(int(i, 16), C, N) for i in y]
    return s

def check_sign_RSA(m_signed, D, N):
    y = hashlib.md5(m_signed[0]).hexdigest()
    y_int = ''.join(str(int(i, 16)) for i in y)
    print(f"Hash before decoding: {y_int}")
    w = ''.join(str(pow_mod(i, D, N)) for i in m_signed[1])
    print(f'Decoded hash: {w}')
    return w == y_int

def sign_RSA_launch(m):
    alice_keys = generate_RSA_keys()
    m_signed = (m, sign_RSA(m, alice_keys.C, alice_keys.N))
    print(check_sign_RSA(m_signed, alice_keys.D, alice_keys.N))

def generate_GOST_global_keys():
    q = get_prime(1 << 255, (1 << 256) - 1)
    while True:
        b = random.randint(math.ceil((1 << 1023) / q), ((1 << 1024) - 1) // q)
        p = q * b + 1
        if is_prime(q * b + 1):
            break

    g = random.randint(1, p - 1)
    a = pow_mod(g, b, p)
    while not a > 1:
        g = random.randint(1, p - 1)
        a = pow_mod(g, b, p)
    return GOST_global_keys(p, q, a)

def generate_GOST_keys(global_keys: GOST_global_keys):
    x = random.randrange(1, global_keys.q)
    y = pow_mod(global_keys.a, x, global_keys.p)
    return ElGamal_keys(x, y)

def sign_GOST(m, keys: ElGamal_keys, glob_keys: GOST_global_keys):
    h = hashlib.md5(m).hexdigest()
    h = int(h, 16)
    r = 0
    s = 0
    while s == 0:
        while r == 0:
            k = random.randint(1, glob_keys.q - 1)
            r = pow_mod(glob_keys.a, k, glob_keys.p) % glob_keys.q
        s = (k * h + keys.x * r) % glob_keys.q
    return ElGamal_signed(m, r, s)

def check_sign_GOST(m_signed: ElGamal_signed, glob_keys: GOST_global_keys, y):
    h = int(hashlib.md5(m_signed.m).hexdigest(), 16)

    temp = extended_euclidean_algorithm(h, glob_keys.q)[1]
    if temp < 1:
        temp += glob_keys.q

    u1 = (m_signed.s * temp) % glob_keys.q
    u2 = (-m_signed.r * temp) % glob_keys.q
    v = ((pow_mod(glob_keys.a, u1, glob_keys.p) * pow_mod(y, u2, glob_keys.p)) % glob_keys.p) % glob_keys.q
    print(m_signed.r)
    print(v)
    return m_signed.r == v

def sign_GOST_launch(m):
    global_keys = generate_GOST_global_keys()
    alice_keys = generate_GOST_keys(global_keys)
    singed_text = sign_GOST(m, alice_keys, global_keys)
    print(check_sign_GOST(singed_text, global_keys, alice_keys.y))
def lab3_launch():
    sign_RSA_launch("bla bla bla".encode('utf-8'))
    sign_ElGamal_launch("bla bla bla".encode('utf-8'))
    sign_GOST_launch("bla bla bla".encode('utf-8'))