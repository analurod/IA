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
            v = (x + dx, y + dy)
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
        nx = self.posicao_jogador[0] + dx
        ny = self.posicao_jogador[1] + dy

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

Responda APENAS com JSON válido, no formato:

{
  "action": "andar | atirar | pegar_ouro | escalar_saida",
  "action_input": { "direcao": "N | S | L | O" }
}

Regras principais:
1. OBJETIVO TEM PRIORIDADE MÁXIMA.
2. Use o estado atual (posição, sensores) e histórico recente para decidir.
3. NÃO repita ações inúteis (ex: andar para Parede).
4. NÃO aja aleatoriamente.
5. Você tem apenas uma flecha, ao atirar uma vez não tente novamente.

Regras do ambiente:
- "BRILHO" → usar pegar_ouro
- "FEDOR" → pode usar atirar (apenas se necessário)
- "BRISA" → evite risco, verifique seu histórico de passos

Regras de missão:
- Se pegou o ouro → volte para (1,1) → escalar_saida
- Não continue explorando após pegar o ouro

Importante:
- Use SOMENTE "N", "S", "L", "O"
- Nunca escreva texto fora do JSON
"""


class Agente:

    def __init__(self, key):
        self.client = Groq(api_key=key)

    def extrair(self, texto):
        m = re.search(r'\{[\s\S]*\}', texto)
        if m:
            json_str = m.group()

            # Corrige aspas simples, caso o modelo erre.
            json_str = json_str.replace("'", '"')

            try:
                return json.loads(json_str)
            except json.JSONDecodeError:
                print("Erro ao interpretar:", json_str)
                return None

        return None

    def executar(self, mundo, objetivo):

        historico = []
        max_passos = 100

        for i in range(max_passos):

            if not mundo.vivo:
                print("Game Over")
                break

            estado = f"""
Passo: {i + 1}/{max_passos}
Pos: {mundo.posicao_jogador}
Sensores: {mundo.sensores()}
Ouro: {mundo.ouro}
Flecha: {mundo.flecha}
Historico recente: {historico[-8:]}
"""

            prompt = f"""
Objetivo principal do usuário: {objetivo}

Estado atual:
{estado}

Escolha UMA ação que ajude diretamente a cumprir o objetivo.
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

            elif nome == "atirar":
                d = inp.get("direcao", "N")
                d = d if d in ["N", "S", "L", "O"] else "N"
                resultado = mundo.atirar(d)

            elif nome == "pegar_ouro":
                resultado = mundo.pegar_ouro()

            elif nome == "escalar_saida":
                resultado = mundo.escalar_saida()

            else:
                resultado = "Acao invalida"

            print(resultado)

            historico.append({
                "passo": i + 1,
                "posicao": mundo.posicao_jogador,
                "sensores": mundo.sensores(),
                "acao": nome,
                "entrada": inp,
                "resultado": resultado
            })

            if resultado in [
                "VITORIA",
                "Saiu sem ouro",
                "Morreu para o Wumpus",
                "Caiu no abismo"
            ]:
                print("Fim de jogo")
                break

        else:
            print("Fim de jogo: limite de passos atingido")


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
    print("Abismos:", mundo.abismos)

    objetivo = input("Digite o objetivo do agente: ")

    agente.executar(mundo, objetivo)


if __name__ == "__main__":
    main()
