# --- Importação de Módulos ---
# 'os' é usado para interagir com o sistema operacional, como criar pastas.
import os
# 'deque' (deck) é uma lista otimizada para adicionar e remover elementos de suas extremidades.
# Usamos como uma fila (queue) para o nosso algoritmo.
from collections import deque


# --- Definição das Funções ---

def ler_afnd(caminho_arquivo):
    """Lê um arquivo de definição de AFND e o carrega em uma estrutura de dados (dicionário)."""
    try:
        # Tenta abrir e ler o arquivo de entrada.
        with open(caminho_arquivo, 'r', encoding='utf-8') as f:
            # Lê todas as linhas, removendo espaços em branco e linhas vazias.
            linhas = [linha.strip()
                      for linha in f.readlines() if linha.strip()]
    except FileNotFoundError:
        # Se o arquivo não for encontrado, exibe um erro e encerra a função.
        print(f"Erro: Arquivo de entrada '{caminho_arquivo}' não encontrado.")
        return None

    # Processa as primeiras linhas com informações básicas do autômato.
    estados = set(linhas[0].split())        # Linha 0: Todos os estados.
    estado_inicial = linhas[1]              # Linha 1: O estado inicial.
    estados_finais = set(linhas[2].split()) # Linha 2: Os estados finais.

    # Inicializa o dicionário de transições e o conjunto do alfabeto.
    transicoes = {}
    alfabeto = set()

    # Itera sobre as linhas restantes, que definem as transições.
    for linha in linhas[3:]:
        partes = linha.split()
        # Validação para garantir que a linha de transição tem 3 partes: origem, símbolo, destino.
        if len(partes) != 3:
            print(
                f"Aviso: Ignorando linha de transição mal formatada: '{linha}'")
            continue

        origem, simbolo, destino = partes

        # Tratamento de um possível erro de digitação no arquivo de entrada (ex: 'H' em vez de 'h').
        if simbolo not in ['0', '1', 'h']:
            print(
                f"Aviso: Símbolo '{simbolo}' na linha '{linha}' não pertence ao alfabeto {{0,1}} ou 'h'. Foi interpretado como 'h'.")
            simbolo = 'h'

        # Adiciona o símbolo ao alfabeto, se não for uma transição vazia.
        if simbolo != 'h':
            alfabeto.add(simbolo)

        # Adiciona a transição ao nosso dicionário.
        # A chave é uma tupla (origem, simbolo) e o valor é um conjunto de destinos.
        if (origem, simbolo) not in transicoes:
            transicoes[(origem, simbolo)] = set()
        transicoes[(origem, simbolo)].add(destino)

    # Retorna um dicionário contendo toda a estrutura do AFND.
    return {
        "estados": estados,
        "alfabeto": sorted(list(alfabeto)),  # Alfabeto ordenado.
        "transicoes": transicoes,
        "estado_inicial": estado_inicial,
        "estados_finais": estados_finais,
    }


def fecho_vazio(estados_origem, transicoes):
    """
    Função CRÍTICA: Calcula o ε-fecho (epsilon-closure) de um ou mais estados.
    O ε-fecho de um estado 'q' é o conjunto de todos os estados que podemos alcançar
    a partir de 'q' usando apenas transições vazias ('h').
    """
    # Garante que estamos trabalhando com um conjunto de estados.
    if not isinstance(estados_origem, set):
        estados_origem = {estados_origem}

    # O fecho inicial contém os próprios estados de origem.
    fecho = set(estados_origem)
    # Usamos uma pilha para controlar os estados que ainda precisamos visitar.
    pilha = list(estados_origem)

    while pilha:
        estado_atual = pilha.pop()
        # Pega todos os destinos alcançáveis com uma transição vazia a partir do estado atual.
        destinos_vazios = transicoes.get((estado_atual, 'h'), set())

        # Para cada destino encontrado...
        for destino in destinos_vazios:
            # ...se ainda não o visitamos...
            if destino not in fecho:
                fecho.add(destino)   # ...adiciona ao nosso conjunto de fecho...
                pilha.append(destino) # ...e o coloca na pilha para explorar a partir dele.
                
    # Retorna um 'frozenset', que é uma versão imutável de um conjunto.
    # Isso é necessário para que possamos usar conjuntos de estados como chaves de dicionário.
    return frozenset(fecho)


def mover(estados_origem, simbolo, transicoes):
    """
    Função CRÍTICA: Calcula para onde podemos ir a partir de um conjunto de estados
    ao consumir um único símbolo do alfabeto (ex: '0' ou '1').
    """
    destinos = set()
    # Para cada estado no conjunto de origem...
    for estado in estados_origem:
        # ...adiciona todos os estados alcançáveis com o símbolo dado.
        destinos.update(transicoes.get((estado, simbolo), set()))
    return destinos


def converter_afnd_para_afd(afnd):
    """
    Função PRINCIPAL: Implementa o Algoritmo de Construção de Subconjuntos,
    omitindo o estado de erro (PHI) para uma saída simplificada.
    """
    # Estruturas de dados para o novo AFD.
    afd_transicoes = {}
    afd_estados_finais = set()
    mapa_nomes_estados = {}

    def gerar_nome_estado(conjunto_estados):
        # Esta função agora nunca receberá um conjunto vazio, mas a mantemos por clareza.
        # Ordena os nomes dos estados (ex: {'C', 'A'}) e junta (ex: "AC")
        return "".join(sorted(list(conjunto_estados)))

    # PASSO 1: O estado inicial do AFD é o ε-fecho do estado inicial do AFND.
    estado_inicial_afd_set = fecho_vazio(
        afnd["estado_inicial"], afnd["transicoes"])

    # Inicializa a fila de exploração com o estado inicial do AFD.
    fila = deque([estado_inicial_afd_set])
    # Conjunto para rastrear os estados do AFD que já descobrimos.
    estados_afd_explorados = {estado_inicial_afd_set}

    # Gera e mapeia o nome descritivo do estado inicial.
    nome_estado_inicial = gerar_nome_estado(estado_inicial_afd_set)
    mapa_nomes_estados[estado_inicial_afd_set] = nome_estado_inicial
    
    # PASSO 2: Loop principal - explora cada estado do AFD até a fila ficar vazia.
    while fila:
        # Pega o próximo estado da fila para processar.
        estado_atual_set = fila.popleft()

        # REGRA: Se o conjunto de estados do AFND contém PELO MENOS UM estado final original,
        # então o novo estado do AFD é final.
        if not estado_atual_set.isdisjoint(afnd["estados_finais"]):
            afd_estados_finais.add(estado_atual_set)

        # PASSO 3: Para cada símbolo do alfabeto, calcula a próxima transição.
        for simbolo in afnd["alfabeto"]:
            # 3a: Calcula o 'mover'.
            proximo_estado_set_raw = mover(
                estado_atual_set, simbolo, afnd["transicoes"])
            
            # 3b: Calcula o 'fecho_vazio' do resultado do mover.
            proximo_estado_set = fecho_vazio(
                proximo_estado_set_raw, afnd["transicoes"])

            # --- MUDANÇA CRUCIAL ---
            # Só processa e cria a transição se o conjunto de destino NÃO for vazio.
            # Isso efetivamente remove o estado de erro PHI da definição.
            if proximo_estado_set:
                # Se este novo conjunto de estados nunca foi visto antes...
                if proximo_estado_set not in estados_afd_explorados:
                    estados_afd_explorados.add(proximo_estado_set) # Marca como explorado.
                    fila.append(proximo_estado_set)                 # Adiciona à fila para ser processado depois.
                    # Gera o nome descritivo para o novo estado e o mapeia.
                    mapa_nomes_estados[proximo_estado_set] = gerar_nome_estado(proximo_estado_set)

                # Registra a transição do AFD usando os nomes descritivos.
                nome_origem = mapa_nomes_estados[estado_atual_set]
                nome_destino = mapa_nomes_estados[proximo_estado_set]
                afd_transicoes[(nome_origem, simbolo)] = nome_destino

    # PASSO 4: Monta e retorna o dicionário final que representa o AFD.
    return {
        "estados": set(mapa_nomes_estados.values()),
        "alfabeto": afnd["alfabeto"],
        "transicoes": afd_transicoes,
        "estado_inicial": mapa_nomes_estados[estado_inicial_afd_set],
        "estados_finais": {mapa_nomes_estados[s] for s in afd_estados_finais},
        "mapa_original": {v: k for k, v in mapa_nomes_estados.items()} # Mapa reverso para consulta.
    }


def escrever_afd(afd, caminho_arquivo):
    """Função utilitária para salvar a tabela do AFD em um arquivo de texto."""
    estados_ordenados = sorted(list(afd["estados"]))
    estados_finais_ordenados = sorted(list(afd["estados_finais"]))
    
    with open(caminho_arquivo, 'w', encoding='utf-8') as f:
        f.write(" ".join(estados_ordenados) + "\n")
        f.write(afd["estado_inicial"] + "\n")
        f.write(" ".join(estados_finais_ordenados) + "\n")
        for (origem, simbolo), destino in sorted(afd["transicoes"].items()):
            f.write(f"{origem} {simbolo} {destino}\n")
    print(f"Arquivo com a tabela do AFD foi gerado em: '{caminho_arquivo}'")


def gerar_graphviz(automato, nome, caminho_arquivo, tipo='AFND'):
    """Função utilitária para gerar o código no formato DOT para o Graphviz."""
    dot_code = f"digraph {nome} {{\n"
    dot_code += "    rankdir=LR;\n    node [shape = circle];\n"
    for estado_final in automato["estados_finais"]:
        dot_code += f'    node [shape = doublecircle]; "{estado_final}";\n'
    dot_code += "    node [shape = circle];\n"
    dot_code += f'    "" [shape=point];\n    "" -> "{automato["estado_inicial"]}";\n\n'
    if tipo == 'AFND':
        for (origem, simbolo), destinos in sorted(automato["transicoes"].items()):
            simbolo_label = "ε" if simbolo == 'h' else simbolo # Usa o símbolo epsilon para 'h'.
            for destino in destinos:
                dot_code += f'    "{origem}" -> "{destino}" [label = "{simbolo_label}"];\n'
    else:  # AFD
        for (origem, simbolo), destino in sorted(automato["transicoes"].items()):
            dot_code += f'    "{origem}" -> "{destino}" [label = "{simbolo}"];\n'
    dot_code += "}"
    with open(caminho_arquivo, "w", encoding='utf-8') as f:
        f.write(dot_code)
    print(f"Arquivo Graphviz gerado em: '{caminho_arquivo}'")


# --- Execução Principal da Parte 1 ---
# O código dentro deste 'if' só roda quando o script é executado diretamente.
if __name__ == "__main__":
    # Define as constantes para os nomes das pastas e arquivos.
    PASTA_SAIDA = "resultado_parte1"
    ARQUIVO_ENTRADA_AFND = "entrada.txt"

    # Cria a pasta de resultados se ela ainda não existir.
    os.makedirs(PASTA_SAIDA, exist_ok=True)

    print("--- Iniciando Parte 1: Conversão de AFND para AFD ---")
    # 1. Lê o arquivo de entrada.
    afnd = ler_afnd(ARQUIVO_ENTRADA_AFND)

    # Continua somente se a leitura do arquivo foi bem-sucedida.
    if afnd:
        print("AFND lido com sucesso.")
        # 2. Gera o arquivo .dot para visualização do AFND original.
        caminho_dot_afnd = os.path.join(PASTA_SAIDA, "afnd.txt")
        gerar_graphviz(afnd, "AFND", caminho_dot_afnd, tipo='AFND')

        # 3. Realiza a conversão para AFD.
        afd = converter_afnd_para_afd(afnd)
        print("Conversão para AFD concluída.")

        # 4. Salva a tabela do novo AFD em um arquivo de texto.
        caminho_saida_afd = os.path.join(PASTA_SAIDA, "saida_afd.txt")
        escrever_afd(afd, caminho_saida_afd)

        # 5. Gera o arquivo .dot para visualização do AFD resultante.
        caminho_dot_afd = os.path.join(PASTA_SAIDA, "afd.txt")
        gerar_graphviz(afd, "AFD", caminho_dot_afd, tipo='AFD')

        # 6. Exibe no console o mapeamento dos novos estados para os conjuntos originais.
        print("\n--- Mapeamento de estados do AFD para conjuntos de estados do AFND ---")
        for nome_q, conjunto_original in sorted(afd["mapa_original"].items()):
            print(f"{nome_q} -> {sorted(list(conjunto_original))}")