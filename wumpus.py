import numpy as np
import random as r

'''A função determina a posição dos atributos de do jogador de forma aleatória
Para o Jogador: Retorna a posição atual (inicial)'''


def distribute_elements(tipoElem, quantElem):
    for i in range(quantElem):
        cord_x = r.randint(0, 3)
        cord_y = r.randint(0, 3)

        while WumpusWorldEnv[cord_x, cord_y] != ".":
            cord_x = r.randint(0, 3)
            cord_y = r.randint(0, 3)

        if tipoElem == 1:
            WumpusWorldEnv[cord_x, cord_y] = "A"   # Abismo
        elif tipoElem == 2:
            WumpusWorldEnv[cord_x, cord_y] = "W"   # Wumpus
        elif tipoElem == 3:
            WumpusWorldEnv[cord_x, cord_y] = "O"   # Ouro
        else:
            WumpusWorldEnv[cord_x, cord_y] = "=)"  # Jogador
            posAtual = [cord_x, cord_y]
            return posAtual


'''A função recebe duas coordenadas (x e y atuais do jogador) e verifica para cada posição adjacente 
(cima, baixo, esquerda, direita) se há algum atributo como: Ouro, Wumous ou Abismo e retorna a percepção'''


def get_percepts(cordX, cordY):

    # cima
    if cordX - 1 >= 0:
        # Ouro
        if WumpusWorldEnv[cordX - 1, cordY] == "O":
            print("Estou vendo um brilho!")
        # Wumpus
        if WumpusWorldEnv[cordX - 1, cordY] == "W":
            print("Estou sentindo um cheiro forte!")
        # Abismo
        if WumpusWorldEnv[cordX - 1, cordY] == "A":
            print("Estou sentindo uma brisa!")

    # baixo
    if cordX + 1 < 4:
        # Ouro
        if WumpusWorldEnv[cordX + 1, cordY] == "O":
            print("Estou vendo um brilho!")
        # Wumpus
        if WumpusWorldEnv[cordX + 1, cordY] == "W":
            print("Estou sentindo um cheiro forte!")
        # Abismo
        if WumpusWorldEnv[cordX + 1, cordY] == "A":
            print("Estou sentindo uma brisa!")

    # esquerda
    if cordY - 1 >= 0:
        # Ouro
        if WumpusWorldEnv[cordX, cordY - 1] == "O":
            print("Estou vendo um brilho!")
        # Wumpus
        if WumpusWorldEnv[cordX, cordY - 1] == "W":
            print("Estou sentindo um cheiro forte!")
        # Abismo
        if WumpusWorldEnv[cordX, cordY - 1] == "A":
            print("Estou sentindo uma brisa!")

    # direita
    if cordY + 1 < 4:
        # Ouro
        if WumpusWorldEnv[cordX, cordY + 1] == "O":
            print("Estou vendo um brilho!")
        # Wumpus
        if WumpusWorldEnv[cordX, cordY + 1] == "W":
            print("Estou sentindo um cheiro forte!")
        # Abismo
        if WumpusWorldEnv[cordX, cordY + 1] == "A":
            print("Estou sentindo uma brisa!")


# Definição da Quantidade de Cada Atributo no Tabuleiro
nAbismos = 1
nWumpus = 1
nOuros = 1

# Tabuleiro 4x4 preenchido com '.'
WumpusWorldEnv = np.full((4, 4), ".", dtype=object)

# ================ Distribuição dos atributos
distribute_elements(3, nOuros)  # Ouro
distribute_elements(2, nWumpus)  # Wumpus
distribute_elements(1, nAbismos)    # Abismo
posAtual = distribute_elements(4, 1)  # Jogador


# Função apenas para imprimir o tabuleiro e ajudar no debug
for linha in WumpusWorldEnv:
    for elemento in linha:
        print(elemento, end=' ')
    print()
print()

# Utilizando sensores
get_percepts(posAtual[0], posAtual[1])
