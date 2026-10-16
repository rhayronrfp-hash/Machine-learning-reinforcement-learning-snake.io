import subprocess
import os
import numpy as np

#nem faz sentido esse arquivo ser chamado mais de colisoes_wrapper mas to com preguica
class Calculo_da_rede:
    def __init__(self, caminho_executavel="./calculo"):
        self.exe = caminho_executavel

        if not os.path.exists(self.exe):
            raise FileNotFoundError(
                f"Executável {self.exe} não encontrado. "
                "Rode: g++ -std=c++17 -O3 calculo_ML.cpp -o calculo"
            )

        self.processo = subprocess.Popen(
            [self.exe],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            text=True,
            bufsize=1
        )

    def _enviar(self, linha):
        self.processo.stdin.write(linha + "\n")
        self.processo.stdin.flush()
        return self.processo.stdout.readline().strip()

    @staticmethod
    def _numeros(valores):
        return " ".join(map(str, np.asarray(valores).flatten()))

    def inicializar(self):
        return self._enviar("0")

    def salvar(self, epsilon):
        self._enviar(f"2 {epsilon}")

    def carregar(self):
        return self._enviar("3") == "OK"

    def obter_epsilon(self):
        return float(self._enviar("8"))

    def set_minimo_amostras(self, n):
        self._enviar(f"9 {n}")

    def set_epsilon(self, valor):
        self._enviar(f"4 {valor}")

    def calcular_lote(self, ids, estados):
        linha = f"7 {len(ids)}"
        for id_, estado in zip(ids, estados):
            linha += f" {id_} {self._numeros(estado)}"

        resposta = self._enviar(linha)
        partes = resposta.split()
        n = int(partes[0])
        return [int(x) for x in partes[1:1 + n]]

    def treino_lote(self, ids, estados, acoes, recompensas, novos_estados, mortos):
        linha = f"6 {len(ids)}"
        for id_, estado, acao, recompensa, novo_estado, morto in zip(
            ids, estados, acoes, recompensas, novos_estados, mortos
        ):
            linha += f" {id_} {self._numeros(estado)} {acao} {recompensa} {self._numeros(novo_estado)} {int(morto)}"
    
        self._enviar(linha)

    def calcular_colisoes(self, cobras, limiar=17.00):
        linha = f"5 {len(cobras)} {limiar}"
    
        for cobra in cobras:
            segmentos = cobra["segmentos"]
            cabeca = segmentos[-1]["fim"]
    
            linha += f" {cabeca[0]} {cabeca[1]} {len(segmentos)}"
    
            for seg in segmentos:
                linha += f" {seg['inicio'][0]} {seg['inicio'][1]} {seg['fim'][0]} {seg['fim'][1]}"
    
        resposta = self._enviar(linha)
        partes = resposta.split()
    
        pos = 0
        n = int(partes[pos])
        pos += 1
    
        resultado = []
    
        for i in range(n):
            quantidade = int(partes[pos])
            pos += 1
    
            colisoes = []
    
            for _ in range(quantidade):
                j = int(partes[pos])
                tipo = int(partes[pos + 1])
                pos += 2
                colisoes.append((j, tipo))
    
            resultado.append(colisoes)
    
        return resultado
    def fechar(self):
        self.processo.terminate()
        self.processo.wait()