# --- Importação de Módulos ---
# 'os' é usado para interagir com o sistema operacional, principalmente para
# manipular caminhos de arquivos (os.path.join) e criar pastas (os.makedirs).
import os

# --- Definição das Funções ---

def ler_afd(caminho_arquivo):
    """
    Lê um arquivo de definição de AFD e o carrega em uma estrutura de dados (dicionário).
    É mais simples que a função de ler o AFND, pois não precisa se preocupar com transições vazias
    ou múltiplos destinos para uma mesma transição.
    """
    try:
        # Tenta abrir e ler o arquivo de entrada (o resultado da Parte 1).
        with open(caminho_arquivo, 'r', encoding='utf-8') as f:
            linhas = [linha.strip() for linha in f.readlines() if linha.strip()]
    except FileNotFoundError:
        # Se o arquivo não for encontrado, exibe um erro claro. Isso geralmente acontece
        # se a Parte 1 não foi executada antes.
        print(f"Erro: Arquivo de definição do AFD '{caminho_arquivo}' não encontrado.")
        print("Por favor, execute o script da Parte 1 primeiro para gerar este arquivo.")
        return None

    # Processa as informações básicas do AFD.
    estados = set(linhas[0].split())        # Linha 0: Todos os estados do AFD.
    estado_inicial = linhas[1]              # Linha 1: O estado inicial do AFD.
    estados_finais = set(linhas[2].split()) # Linha 2: O conjunto de estados finais.
    
    # Inicializa o dicionário de transições e o conjunto do alfabeto.
    transicoes = {}
    alfabeto = set()

    # Itera sobre as linhas de transição.
    for linha in linhas[3:]:
        # Em um AFD, cada linha tem sempre 3 partes: origem, símbolo, destino.
        origem, simbolo, destino = linha.split()
        # Adiciona o símbolo ao alfabeto do autômato.
        alfabeto.add(simbolo)
        # Registra a transição. A chave é (origem, simbolo) e o valor é um ÚNICO destino.
        transicoes[(origem, simbolo)] = destino
        
    # Retorna um dicionário contendo toda a estrutura do AFD.
    return {
        "estados": estados,
        "alfabeto": sorted(list(alfabeto)),
        "transicoes": transicoes,
        "estado_inicial": estado_inicial,
        "estados_finais": estados_finais,
    }

def reconhecer_palavras(afd, arq_palavras, arq_saida):
    """
    Função PRINCIPAL: Simula a execução do AFD para uma lista de palavras
    e determina se cada uma é aceita ou não.
    """
    try:
        # Tenta abrir e ler o arquivo com as palavras a serem testadas.
        with open(arq_palavras, 'r', encoding='utf-8') as f:
            palavras = [linha.strip() for linha in f.readlines() if linha.strip()]
    except FileNotFoundError:
        print(f"Erro: Arquivo de palavras '{arq_palavras}' não encontrado.")
        return

    # Garante que a pasta de saída para os resultados exista.
    # os.path.dirname(arq_saida) pega o nome da pasta a partir do caminho completo do arquivo.
    os.makedirs(os.path.dirname(arq_saida), exist_ok=True)

    # Abre o arquivo de saída para escrever os resultados.
    with open(arq_saida, 'w', encoding='utf-8') as f:
        # Itera sobre cada palavra da lista.
        for palavra in palavras:
            # Para cada nova palavra, a simulação começa no estado inicial do AFD.
            estado_atual = afd["estado_inicial"]
            valida = True # Flag para controlar se a palavra continua válida durante o processo.
            
            # --- Tratamento de caso especial: palavra vazia ---
            if palavra == "":
                 # A palavra vazia só é aceita se o estado inicial também for um estado final.
                 if estado_atual in afd["estados_finais"]:
                      resultado = "aceito"
                 else:
                      resultado = "nao aceito"
                 f.write(f"(palavra vazia) {resultado}\n")
                 continue # Pula para a próxima palavra.

            # --- Simulação para palavras não vazias ---
            # Itera sobre cada símbolo (caractere) da palavra.
            for simbolo in palavra:
                # 1. Validação: O símbolo pertence ao alfabeto do autômato?
                if simbolo not in afd["alfabeto"]:
                    print(f"Aviso: A palavra '{palavra}' contém o símbolo '{simbolo}' que não pertence ao alfabeto. Será considerada 'nao aceito'.")
                    valida = False
                    break # Interrompe a análise desta palavra.
                
                # 2. Transição de Estado: Pega o próximo estado do dicionário de transições.
                # O método .get() é seguro: se a transição não existir, ele retorna None.
                estado_atual = afd["transicoes"].get((estado_atual, simbolo))
                
                # 3. Validação: A transição existia?
                if estado_atual is None:
                    # Se 'estado_atual' é None, significa que o autômato "travou".
                    # A palavra não pode ser reconhecida.
                    valida = False
                    break # Interrompe a análise desta palavra.
            
            # --- Decisão Final ---
            # Após percorrer todos os símbolos, a palavra é aceita se duas condições forem verdadeiras:
            # 1. A palavra se manteve válida durante todo o processo (flag 'valida').
            # 2. O estado em que o autômato parou é um dos estados finais.
            if valida and estado_atual in afd["estados_finais"]:
                resultado = "aceito"
            else:
                resultado = "nao aceito"
            
            # Escreve a palavra e o resultado no arquivo de saída.
            f.write(f"{palavra} {resultado}\n")
            
    print(f"Resultados do reconhecimento de palavras salvos em: '{arq_saida}'")


# --- Execução Principal da Parte 2 ---
if __name__ == "__main__":
    # Define os nomes das pastas e arquivos de entrada e saída.
    PASTA_ENTRADA_P1 = "resultado_parte1"
    PASTA_SAIDA_P2 = "resultado_parte2"
    ARQUIVO_PALAVRAS = "palavras.txt"
    
    # Monta os caminhos completos para os arquivos.
    # O arquivo de entrada desta parte é o arquivo de SAÍDA da Parte 1.
    ARQUIVO_ENTRADA_AFD = os.path.join(PASTA_ENTRADA_P1, "saida_afd.txt")
    # O arquivo de saída desta parte será salvo em sua própria pasta.
    ARQUIVO_SAIDA_RESULTADO = os.path.join(PASTA_SAIDA_P2, "resultado_palavras.txt")

    print("\n--- Iniciando Parte 2: Reconhecimento de Palavras ---")
    
    # 1. Lê o AFD que foi gerado pela Parte 1.
    afd = ler_afd(ARQUIVO_ENTRADA_AFD)

    # 2. Se a leitura for bem-sucedida, inicia o processo de reconhecimento.
    if afd:
      print(f"AFD lido com sucesso de '{ARQUIVO_ENTRADA_AFD}'.")
      # 3. Chama a função principal para simular o AFD com as palavras e salvar o resultado.
      reconhecer_palavras(afd, ARQUIVO_PALAVRAS, ARQUIVO_SAIDA_RESULTADO)