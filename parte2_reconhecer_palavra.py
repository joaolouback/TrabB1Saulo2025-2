import os

def ler_afd(caminho_arquivo):
    """Lê um arquivo de definição de AFD e retorna suas propriedades."""
    try:
        with open(caminho_arquivo, 'r', encoding='utf-8') as f:
            linhas = [linha.strip() for linha in f.readlines() if linha.strip()]
    except FileNotFoundError:
        print(f"Erro: Arquivo de definição do AFD '{caminho_arquivo}' não encontrado.")
        print("Por favor, execute o script da Parte 1 primeiro para gerar este arquivo.")
        return None

    estados = set(linhas[0].split())
    estado_inicial = linhas[1]
    estados_finais = set(linhas[2].split())
    transicoes = {}
    alfabeto = set()

    for linha in linhas[3:]:
        origem, simbolo, destino = linha.split()
        alfabeto.add(simbolo)
        transicoes[(origem, simbolo)] = destino
        
    return {
        "estados": estados,
        "alfabeto": sorted(list(alfabeto)),
        "transicoes": transicoes,
        "estado_inicial": estado_inicial,
        "estados_finais": estados_finais,
    }

def reconhecer_palavras(afd, arq_palavras, arq_saida):
    """Lê palavras de um arquivo e verifica se são aceitas pelo AFD."""
    try:
        with open(arq_palavras, 'r', encoding='utf-8') as f:
            palavras = [linha.strip() for linha in f.readlines() if linha.strip()]
    except FileNotFoundError:
        print(f"Erro: Arquivo de palavras '{arq_palavras}' não encontrado.")
        return

    # Cria a pasta de saída da Parte 2 se ela não existir
    os.makedirs(os.path.dirname(arq_saida), exist_ok=True)

    with open(arq_saida, 'w', encoding='utf-8') as f:
        for palavra in palavras:
            estado_atual = afd["estado_inicial"]
            valida = True
            
            if palavra == "":
                 if estado_atual in afd["estados_finais"]:
                      resultado = "aceito"
                 else:
                      resultado = "nao aceito"
                 f.write(f"(palavra vazia) {resultado}\n")
                 continue

            for simbolo in palavra:
                if simbolo not in afd["alfabeto"]:
                    print(f"Aviso: A palavra '{palavra}' contém o símbolo '{simbolo}' que não pertence ao alfabeto. Será considerada 'nao aceito'.")
                    valida = False
                    break
                
                estado_atual = afd["transicoes"].get((estado_atual, simbolo))
                if estado_atual is None:
                    valida = False
                    break
            
            if valida and estado_atual in afd["estados_finais"]:
                resultado = "aceito"
            else:
                resultado = "nao aceito"
            
            f.write(f"{palavra} {resultado}\n")
    print(f"Resultados do reconhecimento de palavras salvos em: '{arq_saida}'")


# --- Execução Principal da Parte 2 ---
if __name__ == "__main__":
    # CAMINHOS ATUALIZADOS
    PASTA_ENTRADA_P1 = "resultado_parte1"
    PASTA_SAIDA_P2 = "resultado_parte2"
    ARQUIVO_PALAVRAS = "palavras.txt"
    
    ARQUIVO_ENTRADA_AFD = os.path.join(PASTA_ENTRADA_P1, "saida_afd.txt")
    ARQUIVO_SAIDA_RESULTADO = os.path.join(PASTA_SAIDA_P2, "resultado_palavras.txt")

    print("\n--- Iniciando Parte 2: Reconhecimento de Palavras ---")
    
    afd = ler_afd(ARQUIVO_ENTRADA_AFD)

    if afd:
      print(f"AFD lido com sucesso de '{ARQUIVO_ENTRADA_AFD}'.")
      reconhecer_palavras(afd, ARQUIVO_PALAVRAS, ARQUIVO_SAIDA_RESULTADO)