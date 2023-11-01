from lab1 import *
import sys

keys = {}

def generate_coprime(p):
    result = random.randint(2, p)
    while math.gcd(p, result) != 1:
        result = random.randint(2, p)
    return result

def convert_str_ascii(s):
    return [ord(c) for c in s]

def convert_ascii_str(l):
    return "".join([chr(i) for i in l])

# шифр Шамира
def Shamir_encode(m) -> list:
    result = list()

    p = get_prime(0, 10 ** 9)
    Ca = generate_coprime(p - 1)
    Da = extended_euclidean_algorithm(p - 1, Ca)[2]
    if Da < 0:
        Da += p - 1

    Cb = generate_coprime(p - 1)
    Db = extended_euclidean_algorithm(p - 1, Cb)[2]
    if Db < 0:
        Db += p - 1
    keys['shamir'] = {'p': p, 'Ca': Ca, 'Da': Da, 'Cb': Cb, 'Db': Db}

    for part in m:
        x1 = pow_mod(part, Ca, p)
        x2 = pow_mod(x1, Cb, p)
        x3 = pow_mod(x2, Da, p)
        result.append(x3)
    return result

def Shamir_decode(x3) -> list:
    result = list()
    p = keys["shamir"]["p"]
    Db = keys["shamir"]["Db"]
    for part in x3:
        x4 = pow_mod(part, Db, p)
        result.append(x4)
    return result

def ElGamal_encode(m) -> list:
    result = list()
    g = 1

    p = get_prime(0, 10 ** 9)

    while True:
        q = get_prime(0, 10 ** 9)
        p = 2 * q + 1
        if is_prime(p):
            break

    while pow_mod(g, q, p) == 1:
        g = random.randint(2, p - 1)

    Cb = get_prime(0, p - 1)
    Db = pow_mod(g, Cb, p)

    Ka = get_prime(0, p - 2)
    Ra = pow_mod(g, Ka, p)

    keys['gamal'] = {'p': p, 'g': g, 'Cb': Cb, 'Db': Db, 'Ka': Ka, 'Ra': Ra}
    for part in m:
        b = (part * pow_mod(Db, Ka, p)) % p
        result.append(b)
    return result

def ElGamal_decode(b) -> list:
    result = list()
    p = keys["gamal"]["p"]
    Cb = keys["gamal"]["Cb"]
    Ra = keys["gamal"]["Ra"]
    for part in b:
        m1 = (part * pow_mod(Ra, p - 1 - Cb, p)) % p
        result.append(m1)
    return result

def RSA_encode(m) -> list:
    result = list()

    while True:
        Pb = get_prime(0, 10 ** 9)
        Qb = get_prime(0, 10 ** 9)
        if Pb != Qb:
            break

    Nb = Pb * Qb
    PhiB = (Pb - 1) * (Qb - 1)
    Db = generate_coprime(PhiB)
    Cb = extended_euclidean_algorithm(Db, PhiB)[1]

    if Cb < 0:
        Cb += PhiB

    keys['RSA'] = {'Cb': Cb, 'Nb': Nb}
    for part in m:
        e = pow_mod(part, Db, Nb)
        result.append(e)
    return result

def RSA_decode(e) -> list:
    result = list()
    Cb = keys["RSA"]["Cb"]
    Nb = keys["RSA"]["Nb"]
    for part in e:
        m1 = pow_mod(part, Cb, Nb)
        result.append(m1)
    return result

def Vernam_encode(m) -> list:
    codes = [random.randint(0, 255) for _ in range(len(m))]
    keys['vernam'] = codes
    return [m[i] ^ codes[i] for i in range(len(m))]

def Vernam_decode(e) -> list:
    codes = keys['vernam']
    return [e[i] ^ codes[i] for i in range(len(e))]

def coding_print(encode_function, decode_function, message):
    print(f"Исходное сообщение: '{message}'")

    print(f"Название функции кодирования: {encode_function.__name__}")
    encoded = encode_function(convert_str_ascii(message))
    print(f"Закодированное сообщение: '{encoded}'")

    print(f"Название функции кодирования: {decode_function.__name__}")
    decoded = convert_ascii_str(decode_function(encoded))
    print(f"Декодированное сообщение: '{decoded}'")

    return (message, encoded, decoded)

def read_file(filename: str) -> bytearray:
    with open(filename, 'rb') as origin_file:
        return bytearray(origin_file.read())

def write_bytes_to_file(data, file_name):
    file = open(file_name, "wb")

    for byte in data:
        file.write(byte.to_bytes(1, sys.byteorder))

def write_to_file(data, file_name):
    with open(file_name, "w") as file:
        print(data, file=file)

def lab2_launch():
    message = read_file("котята.jpg")
    # Shamir
    encode = Shamir_encode(message)
    write_to_file(encode, "котята_encoded_Shamir.txt")
    decode = Shamir_decode(encode)
    write_bytes_to_file(decode, "котята_decoded_Shamir.jpg")
    # RSA
    encode = RSA_encode(message)
    write_to_file(encode, "котята_encoded_RSA.txt")
    decode = RSA_decode(encode)
    write_bytes_to_file(decode, "котята_decoded_RSA.jpg")
    # ElGamal
    encode = ElGamal_encode(message)
    write_to_file(encode, "котята_encoded_ElGamal.txt")
    decode = ElGamal_decode(encode)
    write_bytes_to_file(decode, "котята_decoded_ElGamal.jpg")
    # Vernam
    encode = Vernam_encode(message)
    write_to_file(encode, "котята_encoded_Vernam.txt")
    decode = Vernam_decode(encode)
    write_bytes_to_file(decode, "котята_decoded_Vernam.jpg")

