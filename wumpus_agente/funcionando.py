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

Ações permitidas:
1) andar
2) atirar
3) pegar_ouro
4) escalar_saida

Direções permitidas:
"N", "S", "L", "O"

Formato obrigatório:

{
  "action": "andar",
  "action_input": {
    "direcao": "S"
  }
}

Regras:
- O objetivo do usuário é a prioridade máxima. Não aja aleatoriamente.
- Antes de escolher uma ação, considere: objetivo, posição atual, sensores e histórico recente.
- Atire apenas se FEDOR nos sensores.
- Se houver BRILHO, a próxima ação deve ser pegar_ouro.
- Se estiver com ouro e estiver em (1,1), a próxima ação deve ser escalar_saida.
- Se uma direção deu Parede, não tente essa mesma direção de novo na mesma posição.
- Evite andar para casas desconhecidas quando houver BRISA ou FEDOR, a menos que seja necessário. Utilize o histórico para se locomover.
- Você tem apenas 1 flecha, ou seja, pode atirar apenas uma vez.
- Quando você atira uma flecha na direção do Wumpus você machuca e mata o Wumpus.
"""


class Agente:

    def __init__(self, key):
        self.client = Groq(api_key=key)

    def extrair(self, texto):
        m = re.search(r'\{[\s\S]*\}', texto)
        if m:
            json_str = m.group()

            # corrige aspas simples
            json_str = json_str.replace("'", '"')

            try:
                return json.loads(json_str)
            except json.JSONDecodeError:
                print("Erro ao interpretar:", json_str)
                return None

        return None

    def executar(self, mundo, objetivo):

        historico = []

        for i in range(20):

            if not mundo.vivo:
                print("Game Over")
                break

            estado = f"""
Pos: {mundo.posicao_jogador}
Sensores: {mundo.sensores()}
Ouro: {mundo.ouro}
Flecha: {mundo.flecha}
Historico recente: {historico[-5:]}
"""

            prompt = f"""
Objetivo: {objetivo}

Estado:
{estado}
"""

            resp = self.client.chat.completions.create(
                model="llama-3.3-70b-versatile",
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

            resultado = ""

            if nome == "andar":
                d = inp.get("direcao", "N")
                d = d if d in ["N", "S", "L", "O"] else "N"
                resultado = mundo.andar(d)
                print(resultado)

            elif nome == "atirar":
                d = inp.get("direcao", "N")
                d = d if d in ["N", "S", "L", "O"] else "N"
                resultado = mundo.atirar(d)
                print(resultado)

            elif nome == "pegar_ouro":
                resultado = mundo.pegar_ouro()
                print(resultado)

            elif nome == "escalar_saida":
                resultado = mundo.escalar_saida()
                print(resultado)

            historico.append({
                "posicao": mundo.posicao_jogador,
                "sensores": mundo.sensores(),
                "acao": nome,
                "entrada": inp,
                "resultado": resultado
            })


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

    objetivo = input("Digite o objetivo do agente: ")

    agente.executar(
        mundo, objetivo)


if __name__ == "__main__":
    main()
