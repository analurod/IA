import numpy as np
import random as r
import heapq

class WumpusWorldEnv:
    def __init__(self):
        self.size = 4
        self.grid = np.full((4, 4), ".", dtype=object)

        # memória do agente
        self.safe_cells = set()
        self.visited = set()
        self.possible_wumpus = set()

        self.has_gold = False
        self.score = 0
        self.arrow = True
        self.wumpus_alive = True

        self.direction = "E"

        # posição inicial fixa
        self.player_pos = (3, 0)
        self.grid[3,0] = "=)"

        # distribuição
        self._distribute(3, 1)
        self._distribute(2, 1)
        self._distribute(1, 1)

        self.safe_cells.add(self.player_pos)

    # ========================================================
    def _distribute(self, tipo, qtd):
        for _ in range(qtd):
            while True:
                x, y = r.randint(0, 3), r.randint(0, 3)
                if self.grid[x, y] == ".":
                    break

            if tipo == 1:
                self.grid[x, y] = "A"
            elif tipo == 2:
                self.grid[x, y] = "W"
            elif tipo == 3:
                self.grid[x, y] = "O"

    # ========================================================
    def get_percepts(self):
        x, y = self.player_pos
        percepts = []

        vizinhos = [(x+1,y),(x-1,y),(x,y+1),(x,y-1)]

        for i, j in vizinhos:
            if 0 <= i < 4 and 0 <= j < 4:
                if self.grid[i, j] == "A":
                    percepts.append("Brisa")
                if self.grid[i, j] == "W" and self.wumpus_alive:
                    percepts.append("Cheiro")

        if self.grid[x, y] == "O":
            percepts.append("Brilho")

        # ========================================================
        #atualiza 
        # sem perigo → vizinhos seguros
        if "Brisa" not in percepts and "Cheiro" not in percepts:
            for i, j in vizinhos:
                if 0 <= i < 4 and 0 <= j < 4:
                    self.safe_cells.add((i,j))

        # possível Wumpus
        if "Cheiro" in percepts:
            for i, j in vizinhos:
                if 0 <= i < 4 and 0 <= j < 4:
                    self.possible_wumpus.add((i,j))

        return percepts

    # ========================================================
    def try_shoot(self):
        if not self.arrow:
            return

        x, y = self.player_pos

        for wx, wy in self.possible_wumpus:
            if wx == x or wy == y:
                print("Atirando à la Katniss Everdeen!")
                self.shoot()
                return

    # ========================================================
    def shoot(self):
        self.score -= 10
        self.arrow = False

        x, y = self.player_pos
        dx, dy = {"N":(-1,0),"S":(1,0),"E":(0,1),"W":(0,-1)}[self.direction]

        while 0 <= x < 4 and 0 <= y < 4:
            if self.grid[x,y] == "W":
                print("Ele gritou! O monstro morreu!")
                self.wumpus_alive = False
                self.grid[x,y] = "."
                self.possible_wumpus.clear()
                return
            x += dx
            y += dy

    # ========================================================
    def _heuristica(self, a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    # ========================================================
    def _neighbors(self, pos):
        x, y = pos
        moves = [(x+1,y),(x-1,y),(x,y+1),(x,y-1)]

        valid = []
        for i, j in moves:
            if 0 <= i < 4 and 0 <= j < 4:
                if (i, j) in self.safe_cells:
                    valid.append((i, j))

        return valid

    # ========================================================
    def _find_path(self, start, target):
        fila = []
        heapq.heappush(fila, (0, start))

        g = {start: 0} #custo até lá
        pai = {start: None}

        while fila:
            _, atual = heapq.heappop(fila)

            if atual == target: #considera os vizinhos
                return self._reconstruir(pai, atual)

            for v in self._neighbors(atual):
                custo = g[atual] + 1

                if v not in g or custo < g[v]:
                    g[v] = custo
                    f = custo + self._heuristica(v, target)
                    heapq.heappush(fila, (f, v))
                    pai[v] = atual

        return None

    # ========================================================
    def _reconstruir(self, pai, atual):
        caminho = []
        while atual:
            caminho.append(atual)
            atual = pai[atual]
        return caminho[::-1]

    # ========================================================
    def move_to(self, next_pos):
        self.score -= 1
        self.player_pos = next_pos

        if self.grid[next_pos] in ["A", "W"]:
            print("Ih, Morreu!")
            self.score -= 1000
            exit()

    # ========================================================
    def run(self):
        print("MAPA (debug):")
        for linha in self.grid:
            print(" ".join(linha))
        print()

        while True:
            print("\nPosição:", self.player_pos)

            percepts = self.get_percepts()
            print("Percepções:", percepts)

            self.visited.add(self.player_pos)

            # encontrou ouro
            if "Brilho" in percepts:
                print("Ouro à vista!")
                self.has_gold = True
                self.grid[self.player_pos] = "."
                break

            # tenta atirar
            self.try_shoot()

            # movimentos seguros
            next_moves = [c for c in self.safe_cells if c not in self.visited]

            if next_moves:
                next_pos = next_moves[0]
                path = self._find_path(self.player_pos, next_pos)

                if path:
                    step = path[1]
                    self.move_to(step)
                    print("Movendo (seguro):", step)
                    continue

            # ========================================================
            print("Sem movimentos seguros... assumindo risco!")

            x, y = self.player_pos
            vizinhos = [(x+1,y),(x-1,y),(x,y+1),(x,y-1)]

            risky_moves = [
                (i,j) for i,j in vizinhos
                if 0 <= i < 4 and 0 <= j < 4 and (i,j) not in self.visited
            ]

            if risky_moves:
                next_pos = r.choice(risky_moves)
                print("Arriscando para:", next_pos)
                self.move_to(next_pos)
            else:
                print("Nada mais a explorar!")
                break

        # ========================================================
        # 🔥 VOLTA COM A*
        # ========================================================
        if self.has_gold:
            path_back = self._find_path(self.player_pos, (3,0))
            print("\nCaminho de volta:", path_back)

            if path_back:
                for step in path_back[1:]:
                    self.move_to(step)
                    print("Voltando para:", step)

            if self.player_pos == (3,0):
                print("Saiu com o ouro! Parabéns!")
                self.score += 1000

        print("Score final:", self.score)


env = WumpusWorldEnv()
env.run()