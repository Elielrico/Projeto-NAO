import json
import os
import random
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

# Nome do arquivo onde a memória da IA será salva
ARQUIVO_MEMORIA = "tabela_q.json"

# 1. ESTADOS e AÇÕES do nosso ambiente
estados = ["triste", "com_raiva"]
acoes = ["dancar_macarena", "jogar_bola", "contar_piada", "fazer_pergunta", "ficar_em_silencio", "fazer_flexao", "brincar_de_siga_o_mestre", "conversar", "fazer_contas", "contar_historias"]


# 2. FUNÇÕES PARA SALVAR E CARREGAR A MEMÓRIA
def carregar_tabela_q():
    """Carrega a Tabela Q do arquivo JSON se ele existir, senão cria uma nova zerada."""
    if os.path.exists(ARQUIVO_MEMORIA):
        with open(ARQUIVO_MEMORIA, "r", encoding="utf-8") as f:
            print("💾 Memória anterior carregada com sucesso!")
            return json.load(f)
    else:
        print("🌱 Nenhuma memória encontrada. Criando nova Tabela Q...")
        return {
            "triste": {
                "dancar_macarena": 0.0,
                "jogar_bola": 0.0,
                "contar_piada": 0.0,
                "fazer_pergunta": 0.0,
                "ficar_em_silencio": 0.0,
                "fazer_flexao": 0.0,
                "brincar_de_siga_o_mestre": 0.0,
                "conversar": 0.0,
                "fazer_contas": 0.0,
                "contar_historias": 0.0

            },
            "com_raiva": {
                "dancar_macarena": 0.0,
                "jogar_bola": 0.0,
                "contar_piada": 0.0,
                "fazer_pergunta": 0.0,
                "ficar_em_silencio": 0.0,
                "fazer_flexao": 0.0,
                "brincar_de_siga_o_mestre": 0.0,
                "conversar": 0.0,
                "fazer_contas": 0.0,
                "contar_historias": 0.0
            },
        }


def salvar_tabela_q(tabela):
    """Salva o estado atual da Tabela Q no arquivo JSON."""
    with open(ARQUIVO_MEMORIA, "w", encoding="utf-8") as f:
        json.dump(tabela, f, indent=4, ensure_ascii=False)
    print("💾 Progresso salvo no arquivo JSON!")


# 3. HIPERPARÂMETROS
taxa_aprendizado = 0.3
taxa_exploracao = 0.8

# Inicializa a tabela carregando o histórico salvo
tabela_q = carregar_tabela_q()


def escolher_acao(estado):
    """Política: decide entre explorar algo novo ou usar o melhor conhecimento."""
    if random.random() < taxa_exploracao:
        return random.choice(acoes)

    opcoes = tabela_q[estado]
    return max(opcoes, key=opcoes.get)


def atualizar_conhecimento(estado, acao, recompensa):
    """Atualiza a nota e salva o arquivo em seguida."""
    nota_antiga = tabela_q[estado][acao]
    nova_nota = nota_antiga + taxa_aprendizado * (recompensa - nota_antiga)
    tabela_q[estado][acao] = round(nova_nota, 2)

    # Persiste o aprendizado imediatamente no arquivo
    salvar_tabela_q(tabela_q)


# === LOOP DE INTERAÇÃO ===
print("\n=== SIMULADOR COM MEMÓRIA PERSISTENTE ===")
print("Digite 'sair' a qualquer momento para encerrar.\n")

i=0

for rodada in range(1, 6):
    print(f"--- Rodada {rodada} ---")

    estado_atual = (estados[i])
    print(f"\nCriança está: [{estado_atual.upper()}]")

    acao_escolhida = escolher_acao(estado_atual)
    print(f"Robô respondeu: [{acao_escolhida}]")

    entrada = input("Pontuação (-10 a +10) ou 'sair': ").strip()

    if entrada.lower() == "sair":
        print("Encerrando o sistema...")
        break
    if(i==0):
        i=1
    else:
        i=0

    try:
        recompensa = float(entrada)
        atualizar_conhecimento(estado_atual, acao_escolhida, recompensa)
    except ValueError:
        print("⚠️ Entrada inválida. Digite um número de -10 a 10.")

def plotar_grade_q(tabela):
    # 1. Converte o dicionário da Tabela Q em um DataFrame do Pandas
    # Transpomos (T) para que Estados fiquem nas linhas e Ações nas colunas
    df = pd.DataFrame(tabela).T

    # 2. Configura o tamanho da janela da imagem
    plt.figure(figsize=(8, 5))

    # 3. Desenha o mapa de calor (Heatmap)
    # cmap='RdYlGn': Escala Vermelho (Ruim) -> Amarelo -> Verde (Bom)
    # annot=True: Escreve os números numéricos das notas dentro de cada quadrado
    # fmt=".1f": Formata o número para exibir 1 casa decimal
    sns.heatmap(
        df,
        annot=True,
        cmap="YlOrRd",
        center=0,
        linewidths=1.5,
        cbar_kws={"label": "Nota Q (Peso)"},
        fmt=".1f",
    )

    # 4. Ajusta títulos e rótulos
    plt.title("Matriz de Conhecimento do Robô NAO (Tabela Q)", fontsize=14)
    plt.xlabel("Ações do Robô", fontsize=12)
    plt.ylabel("Estado da Criança", fontsize=12)

    # Exibe o gráfico na tela
    plt.tight_layout()
    plt.show()

print("\n=== TABELA Q ATUALIZADA NO ARQUIVO ===")
print(json.dumps(tabela_q, indent=4, ensure_ascii=False))
plotar_grade_q(tabela_q)