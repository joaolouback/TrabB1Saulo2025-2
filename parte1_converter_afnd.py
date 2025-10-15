import os
from collections import deque

# ... (todo o código das funções ler_afnd, fecho_vazio, mover, etc., continua igual)
def ler_afnd(caminho_arquivo):
    """Lê um arquivo de definição de AFND e retorna suas propriedades."""
    try:
        with open(caminho_arquivo, 'r', encoding='utf-8') as f:
            linhas = [linha.strip() for linha in f.readlines() if linha.strip()]
    except FileNotFoundError:
        print(f"Erro: Arquivo de entrada '{caminho_arquivo}' não encontrado.")
        return None

    estados = set(linhas[0].split())
    estado_inicial = linhas[1]
    estados_finais = set(linhas[2].split())
    
    transicoes = {}
    alfabeto = set()

    for linha in linhas[3:]:
        partes = linha.split()
        if len(partes) != 3:
            print(f"Aviso: Ignorando linha de transição mal formatada: '{linha}'")
            continue
            
        origem, simbolo, destino = partes
        
        if simbolo not in ['0', '1', 'h']:
             print(f"Aviso: Símbolo '{simbolo}' na linha '{linha}' não pertence ao alfabeto {{0,1}} ou 'h'. Foi interpretado como 'h'.")
             simbolo = 'h'

        if simbolo != 'h':
            alfabeto.add(simbolo)

        if (origem, simbolo) not in transicoes:
            transicoes[(origem, simbolo)] = set()
        transicoes[(origem, simbolo)].add(destino)
        
    return {
        "estados": estados,
        "alfabeto": sorted(list(alfabeto)),
        "transicoes": transicoes,
        "estado_inicial": estado_inicial,
        "estados_finais": estados_finais,
    }

def fecho_vazio(estados_origem, transicoes):
    """Calcula o fecho-vazio (epsilon-closure) para um conjunto de estados."""
    if not isinstance(estados_origem, set):
        estados_origem = {estados_origem}
        
    fecho = set(estados_origem)
    pilha = list(estados_origem)
    
    while pilha:
        estado_atual = pilha.pop()
        destinos_vazios = transicoes.get((estado_atual, 'h'), set())
        
        for destino in destinos_vazios:
            if destino not in fecho:
                fecho.add(destino)
                pilha.append(destino)
    return frozenset(fecho)

def mover(estados_origem, simbolo, transicoes):
    """Calcula o conjunto de estados alcançáveis a partir de um conjunto de estados com um dado símbolo."""
    destinos = set()
    for estado in estados_origem:
        destinos.update(transicoes.get((estado, simbolo), set()))
    return destinos

def converter_afnd_para_afd(afnd):
    """Converte um AFND (com movimentos vazios) para um AFD."""
    afd_transicoes = {}
    afd_estados_finais = set()
    mapa_nomes_estados = {}
    contador_estados = 0

    estado_inicial_afd_set = fecho_vazio(afnd["estado_inicial"], afnd["transicoes"])
    
    fila = deque([estado_inicial_afd_set])
    estados_afd_explorados = {estado_inicial_afd_set}
    
    mapa_nomes_estados[estado_inicial_afd_set] = f"Q{contador_estados}"
    contador_estados += 1

    while fila:
        estado_atual_set = fila.popleft()
        
        if not estado_atual_set.isdisjoint(afnd["estados_finais"]):
            afd_estados_finais.add(estado_atual_set)

        for simbolo in afnd["alfabeto"]:
            proximo_estado_set_raw = mover(estado_atual_set, simbolo, afnd["transicoes"])
            if not proximo_estado_set_raw:
                continue

            proximo_estado_set = fecho_vazio(proximo_estado_set_raw, afnd["transicoes"])
            
            if proximo_estado_set not in estados_afd_explorados:
                estados_afd_explorados.add(proximo_estado_set)
                fila.append(proximo_estado_set)
                mapa_nomes_estados[proximo_estado_set] = f"Q{contador_estados}"
                contador_estados += 1
            
            nome_origem = mapa_nomes_estados[estado_atual_set]
            nome_destino = mapa_nomes_estados[proximo_estado_set]
            afd_transicoes[(nome_origem, simbolo)] = nome_destino

    return {
        "estados": set(mapa_nomes_estados.values()),
        "alfabeto": afnd["alfabeto"],
        "transicoes": afd_transicoes,
        "estado_inicial": mapa_nomes_estados[estado_inicial_afd_set],
        "estados_finais": {mapa_nomes_estados[s] for s in afd_estados_finais},
        "mapa_original": {v: k for k, v in mapa_nomes_estados.items()}
    }

def escrever_afd(afd, caminho_arquivo):
    """Escreve a definição do AFD em um arquivo de saída."""
    with open(caminho_arquivo, 'w', encoding='utf-8') as f:
        f.write(" ".join(sorted(list(afd["estados"]))) + "\n")
        f.write(afd["estado_inicial"] + "\n")
        f.write(" ".join(sorted(list(afd["estados_finais"]))) + "\n")
        for (origem, simbolo), destino in sorted(afd["transicoes"].items()):
            f.write(f"{origem} {simbolo} {destino}\n")
    print(f"Arquivo com a tabela do AFD foi gerado em: '{caminho_arquivo}'")

def gerar_graphviz(automato, nome, caminho_arquivo, tipo='AFND'):
    """Gera o código DOT para visualização do autômato com Graphviz."""
    dot_code = f"digraph {nome} {{\n"
    dot_code += "    rankdir=LR;\n    node [shape = circle];\n"
    for estado_final in automato["estados_finais"]:
        dot_code += f'    node [shape = doublecircle]; "{estado_final}";\n'
    dot_code += "    node [shape = circle];\n"
    dot_code += f'    "" [shape=point];\n    "" -> "{automato["estado_inicial"]}";\n\n'

    if tipo == 'AFND':
        for (origem, simbolo), destinos in sorted(automato["transicoes"].items()):
            simbolo_label = "ε" if simbolo == 'h' else simbolo
            for destino in destinos:
                dot_code += f'    "{origem}" -> "{destino}" [label = "{simbolo_label}"];\n'
    else: # AFD
        for (origem, simbolo), destino in sorted(automato["transicoes"].items()):
            dot_code += f'    "{origem}" -> "{destino}" [label = "{simbolo}"];\n'
    dot_code += "}"
    
    with open(caminho_arquivo, "w", encoding='utf-8') as f:
        f.write(dot_code)
    print(f"Arquivo Graphviz gerado em: '{caminho_arquivo}'")


# --- Execução Principal da Parte 1 ---
if __name__ == "__main__":
    # NOME DA PASTA DE SAÍDA ATUALIZADO
    PASTA_SAIDA = "resultado_parte1"
    ARQUIVO_ENTRADA_AFND = "entrada.txt"

    # Cria a pasta de resultados se ela não existir
    os.makedirs(PASTA_SAIDA, exist_ok=True)
    
    print("--- Iniciando Parte 1: Conversão de AFND para AFD ---")
    afnd = ler_afnd(ARQUIVO_ENTRADA_AFND)
    
    if afnd:
        print("AFND lido com sucesso.")
        caminho_dot_afnd = os.path.join(PASTA_SAIDA, "afnd.dot")
        gerar_graphviz(afnd, "AFND", caminho_dot_afnd, tipo='AFND')
        
        afd = converter_afnd_para_afd(afnd)
        print("Conversão para AFD concluída.")
        
        caminho_saida_afd = os.path.join(PASTA_SAIDA, "saida_afd.txt")
        escrever_afd(afd, caminho_saida_afd)
        
        caminho_dot_afd = os.path.join(PASTA_SAIDA, "afd.dot")
        gerar_graphviz(afd, "AFD", caminho_dot_afd, tipo='AFD')
        
        print("\n--- Mapeamento de estados do AFD para conjuntos de estados do AFND ---")
        for nome_q, conjunto_original in sorted(afd["mapa_original"].items()):
            print(f"{nome_q} -> {sorted(list(conjunto_original))}")