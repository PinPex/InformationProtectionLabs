from collections import defaultdict
import random
from lab1 import is_prime, get_prime, pow_mod, extended_euclidean_algorithm
from lab2 import generate_coprime

def gcd(a,b):
    while b != 0:
        r = a % b
        a = b
        b = r
    return a

def Fill_Graph():
    try:
        with open('Path.txt', 'r') as f:
            nums = f.read().splitlines()
    except OSError:
        print("Ошибка открытия файла с графами")
        return -1

    N = int(nums[0])
    M = int(nums[1])
    id = list()
    firststr = "\t"

    for i in range(N):
        id.append(i + 1)
        firststr += str(i + 1) + "\t"

    Graph_G = [[0] * N for i in range(N)]
    Graph_H = [[0] * N for i in range(N)]

    print("Стартовый граф:")
    print(firststr)
    for i in range(len(Graph_G)):
        print(" " + str(i + 1), end="\t")
        for j in range(len(Graph_G[i])):
            Graph_G[i][j] = 0
            print(Graph_G[i][j], end="\t")
        print("\n", end="")
    print()

    # заполнение графа Алисой
    for k in range(M):
        line = nums[k + 2]
        split_line = line.split(",")
        i = int(split_line[0])
        j = int(split_line[1])
        Graph_G[i - 1][j - 1] = 1
        Graph_G[j - 1][i - 1] = 1
        Graph_H[i - 1][j - 1] = 1
        Graph_H[j - 1][i - 1] = 1


    print("Граф после заполнения Алисой:")
    print(firststr)
    for i in range(len(Graph_G)):
        print(" " + str(i + 1), end="\t")
        for j in range(len(Graph_G[i])):
            print(Graph_G[i][j], end="\t")
        print("\n", end="")

    return N, M, Graph_G, Graph_H, firststr


def All_Path(Graph):
    Dict = defaultdict(list)
    for i in range(len(Graph)):
        for j in range(len(Graph[i])):
            if Graph[i][j] == 1:
                Dict[i].append(j + 1)
    return Dict


def Search_Gamilton_Cycle(G, size, pt, path=[]):
    if pt not in set(path):
        path.append(pt)
        if len(path) == size:
            return path
        for pt_next in G.get(pt - 1, []):
            candidate = Search_Gamilton_Cycle(G, size, pt_next, path)
            if candidate is not None:
                return candidate


def RSA_Matrix_Encode(NewGraph, x, p, N):
    TempGraph = [[0] * N for i in range(N)]
    for i in range(len(NewGraph)):
        for j in range(len(NewGraph[i])):
            TempGraph[i][j] = pow_mod(NewGraph[i][j], x, p)

    return TempGraph


def Gamilton_Cycle():
    N, M, Graph_G, Graph_H, firststr = Fill_Graph()

    List_Path = list()
    New_Graph_H = [[0] * N for i in range(N)]
    New_Graph_G = [[0] * N for i in range(N)]



    print(f"\nN = {N}, M = {M}")

    # Находим все переходы из вершин
    Dict = All_Path(Graph_G)
    print("\nПереходы:")
    for i in range(len(Dict)):
        print(f"{i + 1}: {Dict[i]}")

    # Поиск Гамильтонова цикла
    Path = Search_Gamilton_Cycle(Dict, N, 1, List_Path)
    print(f"\nГамильтонов цикл: {Path}\n")

    print("--------------------------------------")
    print("Действия первого абонента - Алисы")
    print("--------------------------------------")

    NewList = list(range(N))
    random.shuffle(NewList)

    NewList_str = [i + 1 for i in NewList]
    print(f"Алиса рандомит вершины графа: {NewList_str} \n")

    k = 0
    z = 0
    for i in NewList:
        for j in NewList:
            # print(f"[{i}][{j}]: {Graph_G[int(i)][int(j)]}")
            New_Graph_H[k][z] = Graph_G[int(i)][int(j)]
            z += 1
        z = 0
        k += 1

    print("Изоморфный граф: ")
    print(firststr)
    for i in range(len(New_Graph_H)):
        print(" " + str(i + 1), end="\t")
        for j in range(len(New_Graph_H[i])):
            print(New_Graph_H[i][j], end="\t")
        print("\n", end="")

    # Получаем рандомные числа для прибавления в матрицу
    LeftRandom = list(range(1, N + 1))
    random.shuffle(LeftRandom)


    print("\nПеред кодировкой алгоритмом RSA\n" +
          f"Припишем рандомное число из списка {LeftRandom}")
    k = 0
    z = 0
    for i in LeftRandom:
        for j in LeftRandom:
            New_Graph_H[k][z] = int(str(j) + str(New_Graph_H[k][z]))
            z += 1
        z = 0
        k += 1

    print("\nПодготовленная матрица до RSA:")
    print(firststr)
    for i in range(len(New_Graph_H)):
        print(" " + str(i + 1), end="\t")
        for j in range(len(New_Graph_H[i])):
            print(New_Graph_H[i][j], end="\t")
        print("\n", end="")

    print("\nАлиса генерирует ключи;")
    P = get_prime(0, 10 ** 9)
    # print("P = ", P)
    Q = get_prime(0, 10 ** 9)
    # print("Q = ", Q)
    N_encode = P * Q
    print("Ключ N: ", N_encode)
    Phi = (P - 1) * (Q - 1)
    # print("Phi = ", Phi)

    d = generate_coprime(Phi)

    c = extended_euclidean_algorithm(d, Phi)[1]
    if c < 0:
        c += Phi
    print("Ключ c: ", c)

    Graph_F = RSA_Matrix_Encode(New_Graph_H, d, N_encode, N)

    print("\nМатрица после RSA, для Боба:")
    print(firststr)
    for i in range(len(Graph_F)):
        print(" " + str(i + 1), end="\t")
        for j in range(len(Graph_F[i])):
            print(Graph_F[i][j], end="\t")
        print("\n", end="")

    print()
    print("--------------------------------------")
    print("Действия Второго абонента - Боба")
    print("--------------------------------------")
    print("Боб получил матрицу F\n")
    print("Какой вопрос выберет Боб?")
    print("1.'Алиса, каков Гамильтонов цикл для графа H?'")
    print("2.'Алиса, действительно ли граф H изоморфен G?'")
    answer = int(input())

    if answer == 1:
        print("-'Алиса, покажи Гамильтонов цикл?'")
        print("Алиса отсылает Бобу Гамильтонов цикл")
        print(f"Гамильтонов цикл: {Path}")
        print("Боб проходит по Матрице Н-штрих, преобразуя соответствующий элемент цикла")
        print("Если элементы Матрицы F равны этим преобразованным, то Боб пытается по данному циклу пройти свой граф\n" +
              "Если ему это удается, то Все впорядке. Если нет, то возникла ошибка в алгоритме")

        Bob_Check = RSA_Matrix_Encode(New_Graph_H, d, N_encode, N)

        flag = False
        check = 0

        for i in range(len(Graph_F)):
            for j in range(len(Graph_F[i])):
                if Bob_Check[i][j] == Graph_F[i][j]:
                    check += 1

        graph_h_ = RSA_Matrix_Encode(Graph_F, c, N_encode, N)

        for i in range(len(graph_h_)):
            for j in range(len(graph_h_[i])):
                graph_h_[i][j] = int(str(graph_h_[i][j])[1:])
        lst_path = list()
        dict_ = All_Path(graph_h_)

        gam_cycle = Search_Gamilton_Cycle(dict_, N, 1, lst_path)

        #print(gam_cycle, Path)
        if check == pow(N, 2) and gam_cycle != None:
            flag = True
        if flag:
            print(f"\nМатрицы идентичны, т.к. flag = {flag}")
            print(f"Гамильтонов цикл Алисы: {Path}")
            print(f"Гамильтонов цикл Боба: {gam_cycle}")
        else:
            print(f"Матрицы разные flag = {flag}")


    if answer == 2:
        print("-'Докажи изоморфизм, Алиса?'")
        print("\nАлиса отсылает Бобу матрицу, которая еще не преобразована в RSA\n" +
              "И рандом столбцов, который она использовала после получения Гамильтонова цикла")
        print("\nБоб проверяет матрицы: сравнивает матрицы F и H-штрих путем\n" +
              "повторного шифрования и сравнения матриц")

        Bob_Check = RSA_Matrix_Encode(New_Graph_H, d, N_encode, N)

        flag = False
        check = 0
        for i in range(len(Graph_F)):
            for j in range(len(Graph_F[i])):
                if Bob_Check[i][j] == Graph_F[i][j]:
                    check += 1
        if check == pow(N, 2):
            flag = True
        if flag:
            print(f"\nМатрицы идентичны, т.к. flag = {flag}")
        else:
            print(f"\nМатрицы разные flag = {flag}")

        print("Далее Боб отбрасывает все разряды кроме единичного от каждого элемента матрицы и получает матрицу,\n" +
              "изоморфную стартовой\n")

        print(firststr)
        for i in range(len(New_Graph_H)):
            print(" " + str(i + 1), end="\t")
            for j in range(len(New_Graph_H[i])):
                Numstr = str(New_Graph_H[i][j])
                New_Graph_H[i][j] = int(Numstr[-1])
                print(New_Graph_H[i][j], end="\t")
            print("\n", end="")

        print("\nЗатем Боб переставляет столбцы в соответствии с полученной нумерацией от Алисы")
        print(f"\nРандом Алисы вершин графа: {NewList_str}")

        k = 0
        z = 0
        for i in NewList:
            for j in NewList:
                # print(f"{i},{j}")
                # print(f"{k},{z}")
                New_Graph_G[int(i)][int(j)] = New_Graph_H[k][z]
                z += 1
            z = 0
            k += 1

        print("\nЗатем Боб проверяет граф H,преобразуя его по ряду Алисы, и исходный граф Алисы\n" +
              "Если они идентичны, то из графа H мы получили граф G")

        flag = False
        check = 0
        for i in range(len(New_Graph_G)):
            for j in range(len(New_Graph_G[i])):
                # print(f"[{i}][{j}]: {Graph_G[int(i)][int(j)]}")
                if Graph_H[i][j] == New_Graph_G[i][j]:
                    check += 1
        if check == pow(N, 2):
            flag = True
        if flag:
            print()
            print(f"Матрицы идентичны, т.к. flag = {flag}")
        else:
            print(f"Матрицы разные flag = {flag}")
        #
        # print(firststr)
        # for i in range(len(New_Graph_G)):
        #     print(" " + str(i + 1), end="\t")
        #     for j in range(len(New_Graph_G[i])):
        #         Numstr = str(New_Graph_G[i][j])
        #         New_Graph_G[i][j] = int(Numstr[-1])
        #         print(New_Graph_G[i][j], end="\t")
        #     print("\n", end="")

def rgr_launch():
    Gamilton_Cycle()
