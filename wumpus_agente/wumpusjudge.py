"""
Template do Agente - Mundo do Wumpus ------------------------------------ 
INSTRUÇÕES PARA OS ALUNOS: 
1. Este script se comunicará automaticamente com o Judge (Avaliador). 
2. Não utilize funções como `input()` esperando digitar no teclado. O 
Judge enviará as informações do ambiente diretamente pela entrada 
padrão do sistema. 
3. As ações permitidas que você deve retornar (exatamente como escrito) 
são: 
   - MOVER 
   - VIRAR (E) 
   - VIRAR (D) 
   - ATIRAR 
   - AGARRAR 
   - ESCALAR 
4. Os sensores que você receberá são: 
   CHEIRO, BRISA, BRILHO, CHOQUE, GRITO, OURO, NO ESCADA, ou NADA 
"""

import sys

MOVER = "MOVER"
VIRAR_E = "VIRAR (E)"
VIRAR_D = "VIRAR (D)"
ATIRAR = "ATIRAR"
AGARRAR = "AGARRAR"
ESCALAR = "ESCALAR"
ACOES_VALIDAS = {MOVER, VIRAR_E, VIRAR_D, ATIRAR, AGARRAR, ESCALAR}

# ===================================================================
# ÁREA DO SEU AGENTE IMPLEMENTADO
# ===================================================================


class Agente:
    def __init__(self):
        self.nome = "Agente_Templário"
        self.estado = "EXPLORANDO"

    def tomar_decisao(self, sensores):
        """
        sensores: lista de strings recebida do ambiente.
        Ex: [BRISA] ou retorne uma das ações permitidas:
        "MOVER", "VIRAR (E)", "VIRAR (D)", "ATIRAR", "AGARRAR",
        "ESCALAR"
        """
        # ===========================================================
        # COMECE A IMPLEMENTAR SUA LÓGICA DE IA A PARTIR DAQUI!
        # Dica: guardar o histórico do mapa (estado interno) e
        # planejar a rota.
        # ===========================================================

        # Exemplo de lógica muito simples (e ruim):
        acao = MOVER

        if "BRILHO" in sensores:
            acao = AGARRAR
        elif "OURO" in sensores:
            acao = ESCALAR
        elif "BRISA" in sensores or "CHEIRO" in sensores:
            acao = VIRAR_E

        return acao if acao in ACOES_VALIDAS else MOVER

        # ========================================================
        # FIM DA LÓGICA DO AGENTE
        # ========================================================

# =================================================================
# SISTEMA DE AVALIAÇÃO E CHAVEAMENTO (NÃO MODIFICAR NADA A SEGUIR)
# =================================================================


def modo_master():
    agente = Agente()
    print(agente.nome, flush=True)

    while True:
        linha = sys.stdin.readline()

        if not linha:
            break

        linha = linha.strip()
        sensores = linha.split(',') if linha != "NADA" else []
        acao = agente.tomar_decisao(sensores)
        print(acao, flush=True)


def carregar_mundo_stdin():
    linhas = []

    for _ in range(4):
        linha = sys.stdin.readline()

        if not linha:
            break

        linhas.append(linha.strip().split())

    if len(linhas) < 4:
        return None

    mundo = {
        'wumpus': None,
        'buraco': None,
        'ouro': None,
        'wumpus_vivo': True
    }

    for r in range(4):
        for c in range(4):
            val = linhas[r][c]
            x, y = c + 1, 4 - r

            if val == '#':
                mundo['wumpus'] = (x, y)
            elif val == '*':
                mundo['buraco'] = (x, y)
            elif val == '$':
                mundo['ouro'] = (x, y)
            elif val == '@':
                mundo['saida'] = (x, y)

    if mundo['ouro'] is None and mundo['wumpus'] is not None:
        mundo['ouro'] = mundo['wumpus']

    return mundo


def modo_judge_interno():
    mundo = carregar_mundo_stdin()

    if not mundo:
        print("FRACASSO")
        return

    agente = Agente()
    x, y = 1, 1
    direcao = 0
    dx, dy = [1, 0, -1, 0], [0, 1, 0, -1]

    flechas = 2
    tem_ouro = False
    jogo_ativo = True
    resultado_final = "FRACASSO"

    bateu_parede = False
    gritou = False
    pegou_ouro = False
    erro_escada = False
    entrou_sala_ouro = False

    ukjnpjke = 0

    while jogo_ativo and turnos < 500:
        turnos += 1

        if (x, y) == mundo['wumpus'] and mundo['wumpus_vivo']:
            break

        if (x, y) == mundo['buraco']:
            break

        sensores = []
        adjacentes = [(x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)]

        if mundo['buraco'] in adjacentes:
            sensores.append("BRISA")

        if mundo['wumpus_vivo'] and mundo['wumpus'] in adjacentes:
            sensores.append("CHEIRO")

        if entrou_sala_ouro:
            sensores.append("BRILHO")
            entrou_sala_ouro = False

        if bateu_parede:
            sensores.append("CHOQUE")
            bateu_parede = False

        if gritou:
            sensores.append("GRITO")
            gritou = False

        if pegou_ouro:
            sensores.append("OURO")
            pegou_ouro = False

        if erro_escada:
            sensores.append("NO ESCADA")
            erro_escada = False

        acao = agente.tomar_decisao(sensores)

        if acao == MOVER:
            nx, ny = x + dx[direcao], y + dy[direcao]

            if 1 <= nx <= 4 and 1 <= ny <= 4:
                x, y = nx, ny

                if (x, y) == mundo['ouro'] and not tem_ouro:
                    entrou_sala_ouro = True
            else:
                bateu_parede = True

        elif acao == VIRAR_E:
            direcao = (direcao + 1) % 4

        elif acao == VIRAR_D:
            direcao = (direcao - 1) % 4

        elif acao == ATIRAR:
            if flechas > 0:
                flechas -= 1
                tx, ty = x + dx[direcao], y + dy[direcao]

                if (tx, ty) == mundo['wumpus'] and mundo['wumpus_vivo']:
                    mundo['wumpus_vivo'] = False
                    gritou = True

        elif acao == AGARRAR:
            if (x, y) == mundo['ouro'] and not tem_ouro:
                tem_ouro = True
                pegou_ouro = True

        elif acao == ESCALAR:
            if (x, y) == (1, 1):
                if tem_ouro:
                    resultado_final = "SUCESSO"
                    jogo_ativo = False
                else:
                    erro_escada = True

    print(resultado_final)


if __name__ == "__main__":
    if "--master" in sys.argv:
        modo_master()
    else:
        modo_judge_interno()
