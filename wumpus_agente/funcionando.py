import os
import sys
import json
import random
from typing import Dict, List, Tuple, Optional
from datetime import datetime

# ============================================
# CONFIGURAÇÃO SEGURA DA API KEY
# ============================================

def configurar_chave_groq():
    """
    Configura a chave da API Groq de forma segura:
    1. Tenta variável de ambiente GROQ_API_KEY
    2. Tenta arquivo .env
    3. Solicita input do usuário se necessário
    """
    
    # Variável de ambiente
    chave = os.getenv("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")
    if chave:
        print("✅ Chave carregada da variável de ambiente GROQ_API_KEY")
        return chave


# ============================================
# 1. SIMULADOR DO MUNDO DE WUMPUS
# ============================================

class MundoWumpus:
    """Simula o ambiente do Mundo de Wumpus"""
    
    def __init__(self, tamanho=4):
        self.tamanho = tamanho
        self.posicao_jogador = (1, 1)
        self.posicao_wumpus = self._gerar_posicao_aleatoria()
        self.posicao_ouro = self._gerar_posicao_aleatoria()
        self.abismos = self._gerar_abismos()
        self.flecha_disponivel = True
        self.ouro_coletado = False
        self.jogo_ativo = True
        self.mensagem_final = ""
        self.historico_acoes = []
        
        # Garantir posições únicas
        self._garantir_posicoes_validas()
    
    def _garantir_posicoes_validas(self):
        """Garante que nenhuma posição especial se sobreponha"""
        while self.posicao_wumpus == self.posicao_jogador:
            self.posicao_wumpus = self._gerar_posicao_aleatoria()
        
        while self.posicao_ouro in [self.posicao_jogador, self.posicao_wumpus] or self.posicao_ouro in self.abismos:
            self.posicao_ouro = self._gerar_posicao_aleatoria()
        
        # Garantir que abismos não estão na entrada
        abismos_temp = []
        for abismo in self.abismos:
            if abismo != (1, 1) and abismo != self.posicao_wumpus:
                abismos_temp.append(abismo)
        self.abismos = abismos_temp
        
        # Se não há abismos suficientes, adicionar mais
        if len(self.abismos) < 2:
            while len(self.abismos) < 2:
                nova_pos = self._gerar_posicao_aleatoria()
                if nova_pos not in self.abismos and nova_pos != (1, 1) and nova_pos != self.posicao_wumpus:
                    self.abismos.append(nova_pos)
    
    def _gerar_posicao_aleatoria(self):
        return (random.randint(1, self.tamanho), random.randint(1, self.tamanho))
    
    def _gerar_abismos(self):
        num_abismos = random.randint(2, 3)
        abismos = set()
        while len(abismos) < num_abismos:
            pos = self._gerar_posicao_aleatoria()
            if pos != (1, 1):
                abismos.add(pos)
        return list(abismos)
    
    def _obter_sensor(self):
        """Retorna percepções sensoriais da posição atual"""
        x, y = self.posicao_jogador
        sensores = []
        
        # Verifica morte imediata
        if self.posicao_jogador == self.posicao_wumpus and self.jogo_ativo:
            self.jogo_ativo = False
            self.mensagem_final = "💀 Você foi devorado pelo Wumpus!"
            return ["MORTO"]
        
        if self.posicao_jogador in self.abismos:
            self.jogo_ativo = False
            self.mensagem_final = "💀 Você caiu em um abismo!"
            return ["MORTO"]
        
        # Sensores de proximidade
        for dx, dy, direcao in [(0,1,"N"), (1,0,"L"), (0,-1,"S"), (-1,0,"O")]:
            vizinho = (x + dx, y + dy)
            if 1 <= vizinho[0] <= self.tamanho and 1 <= vizinho[1] <= self.tamanho:
                if vizinho == self.posicao_wumpus:
                    sensores.append("👃 FEDOR")
                if vizinho in self.abismos:
                    sensores.append("💨 BRISA")
        
        # Sensor de ouro
        if self.posicao_jogador == self.posicao_ouro and not self.ouro_coletado:
            sensores.append("✨ BRILHO")
        
        # Sensores de parede
        if x == 1: sensores.append("🧱 PAREDE-N")
        if x == self.tamanho: sensores.append("🧱 PAREDE-S")
        if y == 1: sensores.append("🧱 PAREDE-O")
        if y == self.tamanho: sensores.append("🧱 PAREDE-L")
        
        return sensores if sensores else ["⬜ NORMAL"]
    
    def andar(self, direcao: str) -> str:
        """Move o agente para uma casa adjacente válida"""
        if not self.jogo_ativo:
            return f"Jogo já terminou: {self.mensagem_final}"
        
        direcoes = {"N": (-1, 0), "S": (1, 0), "L": (0, 1), "O": (0, -1)}
        
        if direcao not in direcoes:
            return f"❌ Direção inválida: {direcao}. Use N, S, L ou O."
        
        dx, dy = direcoes[direcao]
        nova_pos = (self.posicao_jogador[0] + dx, self.posicao_jogador[1] + dy)
        
        if not (1 <= nova_pos[0] <= self.tamanho and 1 <= nova_pos[1] <= self.tamanho):
            return f"❌ Movimento inválido! Há uma parede na direção {direcao}."
        
        # Registra movimento
        self.historico_acoes.append({
            "acao": "andar",
            "direcao": direcao,
            "posicao_anterior": self.posicao_jogador,
            "posicao_nova": nova_pos
        })
        
        self.posicao_jogador = nova_pos
        sensores = self._obter_sensor()
        
        if "MORTO" in sensores:
            return self.mensagem_final
        
        return f"✅ Andou para {direcao}. Posição: {self.posicao_jogador}. Sensores: {', '.join(sensores)}"
    
    def atirar(self, direcao: str) -> str:
        """Dispara a única flecha na tentativa de matar o Wumpus"""
        if not self.jogo_ativo:
            return f"Jogo já terminou: {self.mensagem_final}"
        
        if not self.flecha_disponivel:
            return "❌ Você já usou sua única flecha!"
        
        direcoes = {"N": (-1, 0), "S": (1, 0), "L": (0, 1), "O": (0, -1)}
        
        if direcao not in direcoes:
            return f"❌ Direção inválida: {direcao}. Use N, S, L ou O."
        
        self.flecha_disponivel = False
        dx, dy = direcoes[direcao]
        
        # Flecha percorre até a parede
        x, y = self.posicao_jogador
        acertou = False
        distancia = 0
        
        for passo in range(1, self.tamanho):
            x += dx
            y += dy
            distancia += 1
            if not (1 <= x <= self.tamanho and 1 <= y <= self.tamanho):
                break
            if (x, y) == self.posicao_wumpus:
                acertou = True
                break
        
        self.historico_acoes.append({
            "acao": "atirar",
            "direcao": direcao,
            "acertou": acertou
        })
        
        if acertou:
            self.posicao_wumpus = None
            return f"🏹 Flecha disparada para {direcao}! 🎯 ACERTOU! Você matou o Wumpus a {distancia} casas de distância!"
        else:
            # Wumpus se move se errar
            self._mover_wumpus()
            return f"🏹 Flecha disparada para {direcao}! ❌ ERROU! O Wumpus se moveu com o barulho!"
    
    def _mover_wumpus(self):
        """Move o Wumpus para uma casa adjacente (efeito de alerta)"""
        if self.posicao_wumpus is None:
            return
        
        direcoes = [(0,1), (1,0), (0,-1), (-1,0)]
        random.shuffle(direcoes)
        
        for dx, dy in direcoes:
            nova_pos = (self.posicao_wumpus[0] + dx, self.posicao_wumpus[1] + dy)
            if 1 <= nova_pos[0] <= self.tamanho and 1 <= nova_pos[1] <= self.tamanho:
                if nova_pos != self.posicao_jogador and nova_pos not in self.abismos:
                    self.posicao_wumpus = nova_pos
                    break
    
    def pegar_ouro(self) -> str:
        """Coleta o ouro se estiver na mesma casa"""
        if not self.jogo_ativo:
            return f"Jogo já terminou: {self.mensagem_final}"
        
        if self.posicao_jogador == self.posicao_ouro:
            self.ouro_coletado = True
            self.historico_acoes.append({"acao": "pegar_ouro"})
            return "💰✨ Você pegou o ouro! Agora fuja para a saída (1,1)! ✨💰"
        else:
            return "❌ Não há ouro nesta casa!"
    
    def escalar_saida(self) -> str:
        """Finaliza o jogo se o agente estiver na casa [1,1]"""
        if not self.jogo_ativo:
            return f"Jogo já terminou: {self.mensagem_final}"
        
        if self.posicao_jogador == (1, 1):
            self.jogo_ativo = False
            if self.ouro_coletado:
                resultado = "🏆 VITÓRIA! Você escapou da caverna com o ouro! 🏆"
            elif self.posicao_wumpus is None:
                resultado = "🏆 VITÓRIA! Você escapou depois de matar o Wumpus! 🏆"
            else:
                resultado = "⚠️ Você escapou, mas sem o ouro..."
            
            self.mensagem_final = resultado
            self.historico_acoes.append({"acao": "escalar_saida"})
            return resultado
        else:
            return f"❌ Você não está na saída! Posição atual: {self.posicao_jogador}. A saída é (1,1)."
    
    def obter_estado_resumido(self) -> str:
        """Retorna estado atual formatado para o LLM"""
        if not self.jogo_ativo:
            return f"JOGO TERMINADO: {self.mensagem_final}"
        
        sensores = self._obter_sensor()
        return f"""
┌─────────────────────────────────────────┐
│         ESTADO ATUAL DO JOGO            │
├─────────────────────────────────────────┤
│ 📍 Posição: {self.posicao_jogador}                    │
│ 🏹 Flecha: {'Disponível' if self.flecha_disponivel else 'Usada'}        │
│ 💰 Ouro: {'Coletado' if self.ouro_coletado else 'Não coletado'}     │
│ 👃 Sensores: {', '.join(sensores)} │
└─────────────────────────────────────────┘
"""
    
    def exibir_mapa_visao(self):
        """Exibe o mapa com a visão atual do agente (para debug)"""
        print("\n🗺️  MAPA ATUAL (visão limitada do agente):")
        print("   " + " ".join([f"{j}" for j in range(1, self.tamanho+1)]))
        for i in range(1, self.tamanho+1):
            linha = f"{i}  "
            for j in range(1, self.tamanho+1):
                if (i, j) == self.posicao_jogador:
                    linha += "🤖 "
                elif (i, j) == self.posicao_ouro and not self.ouro_coletado:
                    linha += "💰 "
                else:
                    linha += "⬜ "
            print(linha)


# ============================================
# 2. PROMPT DO SISTEMA (Padrão ReAct)
# ============================================

SYSTEM_PROMPT = """Você é o "WumpusExplorer", um agente autônomo especializado em explorar o Mundo de Wumpus.

## SUA MISSÃO
Navegar pela caverna, interpretar os sensores, evitar perigos e cumprir os objetivos do usuário.

## FERRAMENTAS DISPONÍVEIS

### 1. andar(direcao)
Move o agente para uma casa adjacente.
- direcao: "N" (Norte), "S" (Sul), "L" (Leste), "O" (Oeste)

Exemplo:
{
  "action": "andar",
  "action_input": {"direcao": "N"}
}

### 2. atirar(direcao)
Dispara a única flecha em uma direção.
- direcao: "N", "S", "L", "O"

Exemplo:
{
  "action": "atirar",
  "action_input": {"direcao": "L"}
}

### 3. pegar_ouro()
Coleta o ouro se estiver na mesma casa.

Exemplo:
{
  "action": "pegar_ouro",
  "action_input": {}
}

### 4. escalar_saida()
Sai da caverna (apenas na posição [1,1]).

Exemplo:
{
  "action": "escalar_saida",
  "action_input": {}
}

## INTERPRETAÇÃO DOS SENSORES

| Sensor | Significado |
|--------|-------------|
| 👃 FEDOR | Wumpus está em uma casa adjacente (N, S, L, O) |
| 💨 BRISA | Abismo está em uma casa adjacente |
| ✨ BRILHO | Ouro está na mesma casa! |
| 🧱 PAREDE-X | Há parede na direção X |
| ⬜ NORMAL | Nada de especial |

## REGRAS IMPORTANTES

1. ⚠️ Você morre se entrar na casa do Wumpus ou em um abismo
2. 🏹 Você tem apenas UMA flecha. Use com sabedoria!
3. 🚪 A posição (1,1) é a entrada/saída da caverna
4. 🦇 O Wumpus pode se mover se você errar a flecha
5. 💰 O ouro só pode ser pego se você estiver na mesma casa

## FORMATO DE RESPOSTA (PADRÃO ReAct)

Sempre responda no seguinte formato:

Thought: [Seu raciocínio baseado nos sensores e no objetivo do usuário]
Action: 
{
  "action": "nome_da_ferramenta",
  "action_input": {"parametro": "valor"}
}

## EXEMPLO DE RACIOCÍNIO

Thought: Estou na posição (1,1). Os sensores indicam NORMAL. O usuário quer que eu encontre o ouro. Devo começar explorando para leste.
Action:
{
  "action": "andar",
  "action_input": {"direcao": "L"}
}

Thought: Senti BRISA! Isso significa que há um abismo adjacente. Devo evitar Norte e Sul. Vou tentar Leste novamente.
Action:
{
  "action": "andar",
  "action_input": {"direcao": "L"}
}

Thought: Senti FEDOR! O Wumpus está próximo. Devo atirar para Leste onde o fedor é mais forte.
Action:
{
  "action": "atirar",
  "action_input": {"direcao": "L"}
}

Lembre-se: SEMPRE inclua seu raciocínio no campo "Thought" antes da ação!
"""


# ============================================
# 3. AGENTE REACT PARA WUMPUS
# ============================================

class AgenteReActWumpus:
    """Agente que usa padrão ReAct (Reasoning + Acting) com LLM da Groq"""
    
    def __init__(self, api_key: str, modelo="mixtral-8x7b-32768"):
        self.client = Groq(api_key=api_key)
        self.modelo = modelo
        self.historico_pensamentos = []
        self.passos_executados = []
    
    def executar(self, mundo: MundoWumpus, instrucao_usuario: str, max_iteracoes=30, verbose=True):
        """
        Executa o ciclo ReAct completo
        
        Args:
            mundo: Instância do simulador
            instrucao_usuario: Missão do agente em linguagem natural
            max_iteracoes: Número máximo de passos
            verbose: Se True, mostra detalhes da execução
        """
        
        print("\n" + "="*70)
        print(f"🎮 MUNDO DE WUMPUS - AGENTE REAct")
        print("="*70)
        print(f"📝 INSTRUÇÃO: {instrucao_usuario}")
        print("="*70)
        
        # Mostra posições iniciais (debug)
        if verbose:
            print("\n🔍 POSIÇÕES INICIAIS (apenas para debug):")
            print(f"   🦇 Wumpus: {mundo.posicao_wumpus}")
            print(f"   💰 Ouro: {mundo.posicao_ouro}")
            print(f"   🕳️  Abismos: {mundo.abismos}")
            print("="*70)
        
        for passo in range(max_iteracoes):
            # Verifica fim de jogo
            if not mundo.jogo_ativo:
                print(f"\n💀 {mundo.mensagem_final}")
                break
            
            # Obtém estado atual
            estado = mundo.obter_estado_resumido()
            
            if verbose:
                print(f"\n{'─'*70}")
                print(f"📍 PASSO {passo + 1}")
                print(f"{'─'*70}")
                print(estado)
            
            # Prepara prompt para o LLM
            user_prompt = f"""
## INSTRUÇÃO DO USUÁRIO:
{instrucao_usuario}

## ESTADO ATUAL:
{estado}

## HISTÓRICO RECENTE:
{chr(10).join(self.historico_pensamentos[-3:]) if self.historico_pensamentos else "Nenhuma ação anterior ainda."}

## AÇÃO ANTERIOR:
{self.passos_executados[-1] if self.passos_executados else "Nenhuma ação anterior."}

Aja agora! Analise os sensores, planeje sua próxima ação e responda no formato:
Thought: (seu raciocínio)
Action: (JSON da ação)
"""
            
            try:
                # Chama o LLM da Groq
                response = self.client.chat.completions.create(
                    model=self.modelo,
                    messages=[
                        {"role": "system", "content": SYSTEM_PROMPT},
                        {"role": "user", "content": user_prompt}
                    ],
                    temperature=0.3,
                    max_tokens=500
                )
                
                resposta_texto = response.choices[0].message.content
                
                if verbose:
                    print(f"\n🤖 RESPOSTA DO LLM:")
                    print("─" * 40)
                    print(resposta_texto)
                    print("─" * 40)
                
                # Extrai Thought e Action
                thought = ""
                action_json = None
                
                linhas = resposta_texto.split('\n')
                for i, linha in enumerate(linhas):
                    if linha.strip().startswith("Thought:"):
                        thought = linha.replace("Thought:", "").strip()
                    elif "{" in linha and "action" in linha:
                        try:
                            # Tenta extrair JSON
                            import re
                            json_match = re.search(r'\{.*\}', linha)
                            if json_match:
                                action_json = json.loads(json_match.group())
                        except json.JSONDecodeError:
                            # Pula linhas seguintes se necessário
                            pass
                
                if not action_json:
                    print("\n⚠️  LLM não retornou ação válida. Tentando novamente...")
                    continue
                
                # Registra pensamento
                self.historico_pensamentos.append(f"Passo {passo+1}: {thought}")
                
                # Executa a ação
                acao = action_json['action']
                action_input = action_json.get('action_input', {})
                
                print(f"\n⚡ EXECUTANDO: {acao}")
                
                if acao == 'andar':
                    direcao = action_input.get('direcao', '').upper()
                    resultado = mundo.andar(direcao)
                elif acao == 'atirar':
                    direcao = action_input.get('direcao', '').upper()
                    resultado = mundo.atirar(direcao)
                elif acao == 'pegar_ouro':
                    resultado = mundo.pegar_ouro()
                elif acao == 'escalar_saida':
                    resultado = mundo.escalar_saida()
                else:
                    resultado = f"❌ Ação desconhecida: {acao}"
                
                print(f"📢 RESULTADO: {resultado}")
                
                # Registra ação
                self.passos_executados.append({
                    "passo": passo + 1,
                    "thought": thought,
                    "action": acao,
                    "resultado": resultado
                })
                
                # Mostra mapa atual (opcional)
                if verbose and passo % 3 == 0:
                    mundo.exibir_mapa_visao()
                
                # Verifica vitória
                if "VITÓRIA" in resultado:
                    print(f"\n🏆 {resultado}")
                    break
                
                if "Game Over" in resultado or "morreu" in resultado.lower():
                    print(f"\n💀 {resultado}")
                    break
                
            except Exception as e:
                print(f"\n❌ ERRO na execução: {e}")
                import traceback
                traceback.print_exc()
                break
        
        # Resumo Final
        self._exibir_resumo_final(mundo)
    
    def _exibir_resumo_final(self, mundo: MundoWumpus):
        """Exibe resumo estatístico da partida"""
        print("\n" + "="*70)
        print("📊 RESUMO FINAL")
        print("="*70)
        
        print(f"\n🎯 Missão: {'✅ Sucesso' if mundo.vitoria() else '❌ Falha'}")
        print(f"📈 Passos executados: {len(self.passos_executados)}")
        print(f"💰 Ouro: {'✅ Coletado' if mundo.ouro_coletado else '❌ Não coletado'}")
        print(f"🏹 Flecha: {'✅ Usada' if not mundo.flecha_disponivel else '❌ Não usada'}")
        
        if mundo.posicao_wumpus is None:
            print(f"🦇 Wumpus: ✅ Morto")
        else:
            print(f"🦇 Wumpus: ❌ Vivo (posição {mundo.posicao_wumpus})")
        
        print(f"\n📝 HISTÓRICO DE AÇÕES:")
        for acao in self.passos_executados:
            print(f"   {acao['passo']:2d}. {acao['action']:12} - {acao['resultado'][:50]}...")
    
    def mostrar_estatisticas(self):
        """Mostra estatísticas do agente"""
        acoes = {}
        for acao in self.passos_executados:
            acoes[acao['action']] = acoes.get(acao['action'], 0) + 1
        
        print("\n📊 ESTATÍSTICAS DO AGENTE:")
        print(f"   Total de ações: {len(self.passos_executados)}")
        for acao, count in acoes.items():
            print(f"   - {acao}: {count} vez(es)")


# ============================================
# 4. FUNÇÃO PARA TESTE AUTOMÁTICO
# ============================================

def testar_agente(api_key: str, instrucao: str, seed: int = None):
    """Executa um teste completo do agente"""
    
    if seed is not None:
        random.seed(seed)
    
    mundo = MundoWumpus()
    agente = AgenteReActWumpus(api_key)
    
    print("\n" + "🔬"*35)
    print("INICIANDO TESTE AUTOMÁTICO")
    print("🔬"*35)
    
    agente.executar(mundo, instrucao, max_iteracoes=25, verbose=True)
    agente.mostrar_estatisticas()
    
    return mundo, agente


# ============================================
# 5. MAIN
# ============================================

def main():
    """Função principal do programa"""
    
    print("""
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║   🦇  MUNDO DE WUMPUS - AGENTE COM IA (Groq)  🦇            ║
║                                                              ║
║   Um agente autônomo que explora uma caverna perigosa       ║
║   usando raciocínio baseado em LLM e o padrão ReAct         ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
    """)
    
    # Configura chave da API
    api_key = configurar_chave_groq()
    
    # Verifica se a chave é válida
    if not api_key:
        print("❌ Não foi possível configurar a chave da API.")
        return
    
    # Menu principal
    while True:
        print("\n" + "="*50)
        print("MENU PRINCIPAL")
        print("="*50)
        print("1. 🎮 Jogar com instrução personalizada")
        print("2. 🧪 Executar testes pré-definidos")
        print("3. 📖 Ver instruções de uso")
        print("4. 🚪 Sair")
        
        opcao = input("\nEscolha uma opção (1-4): ").strip()
        
        if opcao == "1":
            print("\n📝 Digite a instrução para o agente:")
            print("   Exemplos:")
            print("   - 'Encontre o ouro e fuja sem machucar o Wumpus'")
            print("   - 'Sua única missão é matar o Wumpus'")
            print("   - 'Explore e volte vivo'")
            instrucao = input("\nInstrução: ").strip()
            
            if not instrucao:
                instrucao = "Encontre o ouro e saia da caverna com vida!"
            
            mundo = MundoWumpus()
            agente = AgenteReActWumpus(api_key)
            agente.executar(mundo, instrucao, max_iteracoes=30, verbose=True)
            
        elif opcao == "2":
            print("\n🧪 Executando testes pré-definidos...")
            
            testes = [
                "Encontre o ouro e fuja sem machucar o Wumpus.",
                "Sua única missão é matar o Wumpus. Esqueça o ouro.",
                "Explore a caverna e volte vivo para a saída."
            ]
            
            for i, teste in enumerate(testes, 1):
                print(f"\n{'='*60}")
                print(f"TESTE {i}: {teste}")
                print(f"{'='*60}")
                input("\nPressione Enter para continuar...")
                
                # Usa seeds diferentes para cada teste
                testar_agente(api_key, teste, seed=i)
                
                if i < len(testes):
                    continuar = input("\nContinuar para próximo teste? (s/N): ").strip().lower()
                    if continuar != 's':
                        break
        
        elif opcao == "3":
            print("""
╔══════════════════════════════════════════════════════════════╗
║                      INSTRUÇÕES DE USO                       ║
╠══════════════════════════════════════════════════════════════╣
║                                                              ║
║ 1. OBTER CHAVE DA API GROQ:                                 ║
║    - Acesse: https://console.groq.com/keys                  ║
║    - Crie uma conta gratuita                                ║
║    - Gere uma API key (começa com gsk_)                     ║
║                                                              ║
║ 2. SENSORES DO JOGO:                                        ║
║    - 👃 FEDOR: Wumpus está ao lado                          ║
║    - 💨 BRISA: Abismo está ao lado                          ║
║    - ✨ BRILHO: Ouro está na mesma casa                     ║
║    - 🧱 PAREDE: Parede na direção indicada                  ║
║                                                              ║
║ 3. AÇÕES DO AGENTE:                                         ║
║    - andar(N/S/L/O): Move para uma direção                  ║
║    - atirar(N/S/L/O): Dispara flecha (apenas 1)             ║
║    - pegar_ouro(): Coleta o ouro                            ║
║    - escalar_saida(): Sai da caverna em (1,1)               ║
║                                                              ║
║ 4. DICAS:                                                   ║
║    - Use fedor para localizar o Wumpus                      ║
║    - Evite brisa (indica abismo)                            ║
║    - Brilho significa que você achou o ouro!                ║
║    - Volte para (1,1) para sair                             ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
            """)
            input("\nPressione Enter para continuar...")
        
        elif opcao == "4":
            print("\n👋 Obrigado por usar o Mundo de Wumpus!")
            break
        
        else:
            print("❌ Opção inválida! Escolha 1, 2, 3 ou 4.")


# ============================================
# 6. EXECUÇÃO
# ============================================

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Programa interrompido pelo usuário. Até mais!")
    except Exception as e:
        print(f"\n❌ Erro inesperado: {e}")
        import traceback
        traceback.print_exc()


# ============================================
# MÉTODO ADICIONAL PARA A CLASSE MundoWumpus
# ============================================

def vitoria(self) -> bool:
    """Verifica se o jogador venceu"""
    return not self.jogo_ativo and (
        (self.ouro_coletado and self.posicao_jogador == (1, 1)) or
        (self.posicao_wumpus is None and self.posicao_jogador == (1, 1)))