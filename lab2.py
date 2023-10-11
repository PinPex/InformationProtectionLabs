from lab1 import *

keys = {}

def generate_coprime(p):
    result = random.randint(2, p)
    # print(result)
    while math.gcd(p, result) != 1:
        result = random.randint(2, p)
        # print(result)
    return result

def convert_str_ascii(s):
    return [ord(c) for c in s]

def convert_ascii_str(l):
    return "".join([chr(i) for i in l])

# шифр Шамира
def Shamir_encode(m) -> list:
    result = list()

    p = get_prime(0, 10 ** 9)
    #print("p = ", p)
    Ca = generate_coprime(p - 1)
    #print("Ca = ", Ca)
    Da = extended_euclidean_algorithm(p - 1, Ca)[2]
    if Da < 0:
        Da += p - 1
    #print("Da = ", Da)

    Cb = generate_coprime(p - 1)
    #print("Cb = ", Cb)
    Db = extended_euclidean_algorithm(p - 1, Cb)[2]
    if Db < 0:
        Db += p - 1
    #print("Db = ", Db)
    keys['shamir'] = {'p': p, 'Ca': Ca, 'Da': Da, 'Cb': Cb, 'Db': Db}

    for part in m:
        x1 = pow_mod(part, Ca, p)
        x2 = pow_mod(x1, Cb, p)
        x3 = pow_mod(x2, Da, p)
        result.append(x3)
        # print("x1 = ", x1)
        # print("x2 = ", x2)
        # print("x3 = ", x3)
    return result

def Shamir_decode(x3) -> list:
    result = list()
    p = keys["shamir"]["p"]
    Db = keys["shamir"]["Db"]
    for part in x3:
        # print(part)
        x4 = pow_mod(part, Db, p)
        result.append(x4)
        # print("x4 = ", x4)
    return result

def ElGamal_encode(m) -> list:
    result = list()
    g = 0
    while True:
        q = get_prime(0, 10 ** 9)
        p = 2 * q + 1
        if is_prime(p):
            break
    #print("p = ", p)
    while pow_mod(g, q, p) != 1:
        g = random.randint(2, p - 1)

    #print("g = ", g)
    x = get_prime(0, p - 1)
    #print("x = ", x)
    y = pow_mod(g, x, p)
    #print("y = ", y)

    k = get_prime(0, p - 2)
    #print("k = ", k)
    a = pow_mod(g, k, p)
    #print("a = ", a)
    keys['gamal'] = {'p': p, 'g': g, 'x': x, 'y': y, 'k': k, 'a': a}
    for part in m:
        # print(part)
        b = (part * pow_mod(y, k, p)) % p
        result.append(b)
        # print("b = ", b)
    return result

def ElGamal_decode(b) -> list:
    result = list()
    p = keys["gamal"]["p"]
    x = keys["gamal"]["x"]
    a = keys["gamal"]["a"]
    for part in b:
        # print(part)
        m1 = (part * pow_mod(a, p - 1 - x, p)) % p
        result.append(m1)
        # print("m1 = ", m1)
    return result

def RSA_encode(m) -> list:
    result = list()

    P = get_prime(0, 10 ** 9)
    #print("P = ", P)
    Q = get_prime(0, 10 ** 9)
    #print("Q = ", Q)
    N = P * Q
    #print("N = ", N)
    Phi = (P - 1) * (Q - 1)
    #print("Phi = ", Phi)
    d = generate_coprime(Phi)
    #print("d = ", d)
    # d = 3
    c = extended_euclidean_algorithm(d, Phi)[1]
    if c < 0:
        c += Phi
    #print("c = ", c)

    keys['RSA'] = {'c': c, 'N': N}  # 'P': P, 'Q': Q, 'Phi': Phi, 'd': d}
    for part in m:
        # print(part)
        e = pow_mod(part, d, N)
        result.append(e)
        # print("e = ", e)
    return result

def RSA_decode(e) -> list:
    result = list()
    c = keys["RSA"]["c"]
    N = keys["RSA"]["N"]
    for part in e:
        # print(part)
        m1 = pow_mod(part, c, N)
        result.append(m1)
    #print("m1 = ", m1)
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

def lab2_launch():
    message = "Hello world!"
    # Shamir
    coding_print(Shamir_encode, Shamir_decode, message)
    # RSA
    coding_print(RSA_encode, RSA_decode, message)
    # ElGamal
    coding_print(ElGamal_encode, ElGamal_decode, message)
    # Vernam
    coding_print(Vernam_encode, Vernam_decode, message)

