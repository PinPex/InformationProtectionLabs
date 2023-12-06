from lab1 import *
from lab2 import generate_coprime
import hashlib
import random

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
    return [Ni, Di, Ci]

def sign_RSA(m, keys):
    y = hashlib.md5(m).hexdigest()
    y_int = ''.join(str(int(i, 16)) for i in y)
    #print(f"Hash before encoding: {y_int}")
    s = [pow_mod(int(i, 16), keys[2], keys[0]) for i in y]
    return [keys[0], keys[1], keys[2], s] # Ni, Di, Ci, s

def check_sign_RSA(m, keys):
    y = hashlib.md5(m).hexdigest()
    y_int = ''.join(str(int(i, 16)) for i in y)
    #print(f"Hash before decoding: {y_int}")
    w = ''.join(str(pow_mod(i, keys[1], keys[0])) for i in keys[3])
    #print(f'Decoded hash: {w}')
    return w == y_int

def sign_RSA_launch(m):
    alice_keys = generate_RSA_keys()
    sign = sign_RSA(m, alice_keys)
    return sign

def generate_ElGamal_global_keys():
    g = 0
    while True:
        q = get_prime(0, 10 ** 9)
        p = 2 * q + 1
        if is_prime(p):
            break
    while pow_mod(g, q, p) != 1:
        g = random.randint(2, p - 1)
    return [p, g]

def generate_ElGamal_keys(global_keys):
    x = get_prime(0, global_keys[0] - 1)
    y = pow_mod(global_keys[1], x, global_keys[0])
    return [global_keys[0], global_keys[1], x, y] # p, g, x, y
def sign_ElGamal(m, keys):
    k = generate_coprime(keys[0] - 1)
    r = pow_mod(keys[1], k, keys[0])
    h = hashlib.md5(m).hexdigest()
    h_b = ''.join(str(pow_mod(keys[1], int(i, 16), keys[0])) for i in h)
    #print(f"Before encoding: g^h % p = {h_b}")
    u = [(int(i, 16) - keys[2] * r) % (keys[0] - 1) for i in h]
    s = [(extended_euclidean_algorithm(k, keys[0] - 1)[1] * i) % (keys[0] - 1) for i in u]
    return [keys[0], keys[1], keys[2], keys[3], r, s] # p, g, x, y, r, s
def check_sign_ElGamal(m, keys):
    h = hashlib.md5(m).hexdigest()
    h_b = ''.join(str(pow_mod(keys[1], int(i, 16), keys[0])) for i in h)
    #print(f"Before decoding: g^h % p = {h_b}")
    res = ''.join(str(pow_mod(keys[3], keys[4], keys[0] ) * pow_mod(keys[4], i, keys[0]) % keys[0]) for i in keys[5])
    #print(f"Decoding: (y^r % p) * (r ^ s % p) % p = {res}")
    return h_b == res

def sign_ElGamal_launch(m):
    global_keys = generate_ElGamal_global_keys()
    keys = generate_ElGamal_keys(global_keys)
    sign = sign_ElGamal(m, keys)
    return sign

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
    return [p, q, a]

def generate_GOST_keys(global_keys):
    x = random.randrange(1, global_keys[1])
    y = pow_mod(global_keys[2], x, global_keys[0])
    return [global_keys[0], global_keys[1], global_keys[2], x, y] # p, q, a, x, y

def sign_GOST(m, keys):
    h = hashlib.md5(m).hexdigest()
    h = int(h, 16)
    r = 0
    s = 0
    while s == 0:
        while r == 0:
            k = random.randint(1, keys[1] - 1)
            r = pow_mod(keys[2], k, keys[0]) % keys[1]
        s = (k * h + keys[3] * r) % keys[1]
    return [keys[0], keys[1], keys[2], keys[3], keys[4], r, s] # p, q, a, x, y, r, s

def check_sign_GOST(m, keys):
    h = int(hashlib.md5(m).hexdigest(), 16)

    temp = extended_euclidean_algorithm(h, keys[1])[1]
    if temp < 1:
        temp += keys[1]

    u1 = (keys[6] * temp) % keys[1]
    u2 = (-keys[5] * temp) % keys[1]
    v = ((pow_mod(keys[2], u1, keys[0]) * pow_mod(keys[4], u2, keys[0])) % keys[0]) % keys[1]
    return keys[5] == v

def sign_GOST_launch(m):
    global_keys = generate_GOST_global_keys()
    keys = generate_GOST_keys(global_keys)
    sign = sign_GOST(m, keys)
    return sign

def read_from_file(filename):
    with open(filename) as f:
        return f.read()

def write_to_file(filename, data):
    with open(filename, 'w+') as f:
        f.write(data)

sign_types = {'rsa': check_sign_RSA, 'elgamal': check_sign_ElGamal, 'gost': check_sign_GOST}

def check_sign_file(filename, ext, sign_type: str, signer_name: str):
    origin_file = open(filename + "." + ext)
    sign_file = open(filename + "_sign_" + sign_type.lower() + "_" + signer_name.lower() + ".txt")
    text = origin_file.read()
    sign = eval(sign_file.read())
    return sign_types[sign_type.lower()](text.encode('utf-8'), sign)

def sign_file(filename, ext, sign_type: str, signer_name: str, sign):
    write_to_file(filename + "_sign_" + sign_type.lower() + "_" + signer_name.lower() + ".txt", str(sign))

def lab3_launch():
    text = read_from_file("unsigned.txt")

    Decode_data_RSA = sign_RSA_launch(text.encode('utf-8'))
    sign_file("unsigned", "txt", 'rsa', 'alice', Decode_data_RSA)
    print(check_sign_file("unsigned","txt", 'rsa', 'alice'))

    Decode_data_ElGamal = sign_ElGamal_launch(text.encode('utf-8'))
    sign_file("unsigned", "txt", 'elgamal', 'alice', Decode_data_ElGamal)
    print(check_sign_file("unsigned","txt", 'elgamal', 'alice'))

    Decode_data_GOST = sign_GOST_launch(text.encode('utf-8'))
    sign_file("unsigned", "txt", 'gost', 'alice', Decode_data_GOST)
    print(check_sign_file("unsigned","txt", 'gost', 'alice'))

