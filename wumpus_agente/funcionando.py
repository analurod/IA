import os
import json
import random
import re
from dotenv import load_dotenv
from groq import Groq

# ============================================
# CONFIG API
# ============================================
load_dotenv()


def configurar_chave():
    key = os.getenv("GROQ_API_KEY")
    if not key:
        key = input("Digite sua API key: ")
    return key


# ============================================
# MUNDO
# ============================================

class MundoWumpus:

    def __init__(self):
        self.tamanho = 4
        self.posicao_jogador = (1, 1)
        self.posicao_wumpus = self.rand()
        self.posicao_ouro = self.rand()
        self.abismos = [self.rand(), self.rand()]
        self.flecha = True
        self.ouro = False
        self.vivo = True

    def rand(self):
        return (random.randint(1, 4), random.randint(1, 4))

    def sensores(self):
        x, y = self.posicao_jogador
        s = []

        for dx, dy in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
            v = (x+dx, y+dy)
            if v == self.posicao_wumpus:
                s.append("FEDOR")
            if v in self.abismos:
                s.append("BRISA")

        if self.posicao_jogador == self.posicao_ouro:
            s.append("BRILHO")

        return list(set(s)) if s else ["NORMAL"]

    def andar(self, d):
        dirs = {"N": (-1, 0), "S": (1, 0), "L": (0, 1), "O": (0, -1)}
        dx, dy = dirs[d]
        nx = self.posicao_jogador[0]+dx
        ny = self.posicao_jogador[1]+dy

        if not (1 <= nx <= 4 and 1 <= ny <= 4):
            return "Parede"

        self.posicao_jogador = (nx, ny)

        if self.posicao_jogador == self.posicao_wumpus:
            self.vivo = False
            return "Morreu para o Wumpus"

        if self.posicao_jogador in self.abismos:
            self.vivo = False
            return "Caiu no abismo"

        return f"OK {self.sensores()}"

    def atirar(self, d):
        if not self.flecha:
            return "Sem flecha"

        self.flecha = False
        dirs = {"N": (-1, 0), "S": (1, 0), "L": (0, 1), "O": (0, -1)}
        dx, dy = dirs[d]
        x, y = self.posicao_jogador

        for _ in range(4):
            x += dx
            y += dy
            if (x, y) == self.posicao_wumpus:
                self.posicao_wumpus = None
                return "Matou o Wumpus"

        return "Errou"

    def pegar_ouro(self):
        if self.posicao_jogador == self.posicao_ouro:
            self.ouro = True
            return "Pegou ouro"
        return "Nada aqui"

    def escalar_saida(self):
        if self.posicao_jogador == (1, 1):
            if self.ouro:
                return "VITORIA"
            return "Saiu sem ouro"
        return "Nao esta na saida"


# ============================================
# AGENTE
# ============================================

SYSTEM_PROMPT = """
Você é um agente do Mundo de Wumpus.

Você pode usar ferramentas:

andar(direcao)
atirar(direcao)
pegar_ouro()
escalar_saida()

Sensores:
FEDOR = Wumpus perto
BRISA = abismo perto
BRILHO = ouro aqui

Responda SEMPRE:

Thought: ...
Action: { "action": "...", "action_input": {...} }
"""


class Agente:

    def __init__(self, key):
        self.client = Groq(api_key=key)

    def extrair(self, texto):
        m = re.search(r'\{[\s\S]*\}', texto)
        if m:
            return json.loads(m.group())
        return None

    def executar(self, mundo, objetivo):

        for i in range(20):

            if not mundo.vivo:
                print("Game Over")
                break

            estado = f"""
Pos: {mundo.posicao_jogador}
Sensores: {mundo.sensores()}
Ouro: {mundo.ouro}
Flecha: {mundo.flecha}
"""

            prompt = f"""
Objetivo: {objetivo}

Estado:
{estado}
"""

            resp = self.client.chat.completions.create(
                model="mixtral-8x7b-32768",
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": prompt}
                ]
            )

            txt = resp.choices[0].message.content
            print("\n", txt)

            acao = self.extrair(txt)
            if not acao:
                continue

            nome = acao["action"]
            inp = acao.get("action_input", {})

            if nome == "andar":
                print(mundo.andar(inp.get("direcao", "N")))
            elif nome == "atirar":
                print(mundo.atirar(inp.get("direcao", "N")))
            elif nome == "pegar_ouro":
                print(mundo.pegar_ouro())
            elif nome == "escalar_saida":
                print(mundo.escalar_saida())


# ============================================
# MAIN
# ============================================

def main():
    key = configurar_chave()

    mundo = MundoWumpus()
    agente = Agente(key)

    print("DEBUG:")
    print("Wumpus:", mundo.posicao_wumpus)
    print("Ouro:", mundo.posicao_ouro)

    agente.executar(mundo, "Encontre o ouro e saia vivo")


if __name__ == "__main__":
    main()
