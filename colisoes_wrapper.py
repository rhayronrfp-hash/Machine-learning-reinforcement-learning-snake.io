import subprocess
import os

class ColisoesCPP:
    def __init__(self, caminho_executavel="./colisoes"):
        self.exe = caminho_executavel
        if not os.path.exists(self.exe):
            raise FileNotFoundError(f"Executável {self.exe} não encontrado. Rode: g++ -std=c++17 -O3 colisoes.cpp -o colisoes")
        
        self.processo = subprocess.Popen(
            [self.exe],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1
        )
    
    def calcular_colisoes(self, cobras, limiar=12*24):
        num_cobras = len(cobras)
        
        linha = f"{num_cobras} {limiar}"
        
        for cobra in cobras:
            cabeca = cobra["segmentos"][-1]["fim"]
            linha += f" {cabeca[0]} {cabeca[1]} {len(cobra['segmentos'])}"
            
            for seg in cobra["segmentos"]:
                x1, y1 = seg["inicio"]
                x2, y2 = seg["fim"]
                linha += f" {x1} {y1} {x2} {y2}"
        
        self.processo.stdin.write(linha + "\n")
        self.processo.stdin.flush()
        
        resposta = self.processo.stdout.readline().strip()
        
        partes = resposta.split()
        idx = 0
        n = int(partes[idx])
        idx += 1
        
        colisoes = []
        for i in range(n):
            num_colisoes = int(partes[idx])
            idx += 1
            cobra_colisoes = []
            for _ in range(num_colisoes):
                cobra_colisoes.append(int(partes[idx]))
                idx += 1
            colisoes.append(cobra_colisoes)
        
        return colisoes
    
    def fechar(self):
        self.processo.terminate()
        self.processo.wait()

if __name__ == "__main__":
    colisoes_cpp = ColisoesCPP()
    
    cobras_teste = [
        {"segmentos": [{"inicio": [0, 0], "fim": [10, 10]}, {"inicio": [10, 10], "fim": [20, 20]}]},
        {"segmentos": [{"inicio": [100, 100], "fim": [110, 110]}]},
        {"segmentos": [{"inicio": [15, 15], "fim": [25, 25]}]},
    ]
    
    resultado = colisoes_cpp.calcular_colisoes(cobras_teste)
    print("Resultado:", resultado)
    
    colisoes_cpp.fechar()
