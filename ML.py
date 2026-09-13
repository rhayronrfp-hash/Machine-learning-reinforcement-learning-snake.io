import time
import numpy as np
import random
#reutilizei algumas coisas do primeiro codigo de rede neural que fiz
def softmax(logits):
    logits = logits - np.max(logits, axis=1, keepdims=True)
    
    expoente = np.exp(logits)
    soma = np.sum(expoente, axis=1, keepdims=True)

    return expoente / soma

class ML:
    def __init__(self):
        self.pesos = [
        np.random.randn(24, 6),
        np.random.randn(24, 24),
        np.random.randn(3, 24)
        ]
        
        self.biases = [
        np.random.randn(24),
        np.random.randn(24),
        np.random.randn(3)]        
        
        
    def escolha(self, acao):
        global ultimolog
        agora = time.time()
        
        if agora - ultimolog >= 3:
            print("Estado:", estado)
            print("Resultado:", resultado)
            print("Ação:", acao)
            ultimolog = agora
    
        return acao
    
    def calcular(self, estado):
        valor = np.array([estado])
        
        z1 = (valor @ self.pesos[0].T) + self.biases[0]
        camada1 = np.maximum(0, z1)
    
        z2 = (camada1 @ self.pesos[1].T) + self.biases[1]
        camada2 = np.maximum(0, z2)
        
        z3 = camada2 @ self.pesos[2].T + self.biases[2]
        camada3 = z3
#isso aqui é o valorq (to me divertindo bastante até)
        
        if random.random() < 0.05:
            acao = random.randint(0, 2)
        else:
            acao = np.argmax(camada3)
        
        return acao, camada3, z1, z2, camada2, camada1, valor
        
#estado= velho, nestado=novo        
    def calcular_alvo(self, estado, recompensa, acao, nestado):       
        qnovo =  np.max(self.calcular(nestado)[1]) 
        qacao = estado[0][acao]     
        queremos = recompensa + 0.9 * qnovo
        lossreal= (qacao- queremos) ** 2 
        return qacao, queremos, acao
        
#TA MT DIFICIL DE ENTENDER ISSO AQUIIIIIII
    def propagacao(self, z1, z2, camada2, camada1, valor, qacao, queremos, acao):
        z1 = z1.ravel()
        z2 = z2.ravel()
        camada2 = camada2.ravel()
        camada1 = camada1.ravel()
        valor = valor.ravel()

        erro = qacao - queremos
        erro = np.clip(erro, -10, 10)

        dz3 = np.zeros(3)
        dz3[acao] = 2*erro
        gradiente_pesos3 = dz3[:, np.newaxis] * camada2
        gradiente_bias3 = dz3
    
        dz2 = dz3 @ self.pesos[2]
        dz2 = dz2 * (z2 > 0)
        gradiente_pesos2 = dz2[:, np.newaxis] * camada1
        gradiente_bias2 = dz2
    
        dz1 = dz2 @ self.pesos[1]
        dz1 = dz1 * (z1 > 0)
        gradiente_pesos1 = dz1[:, np.newaxis] * valor
        gradiente_bias1 = dz1#olhando assim, não parece dificil(é mt dificil)

        for g in (gradiente_pesos1, gradiente_pesos2, gradiente_pesos3,
                  gradiente_bias1, gradiente_bias2, gradiente_bias3):
            np.clip(g, -5, 5, out=g)

        self.pesos[0] -= 0.01 * gradiente_pesos1
        self.pesos[1] -= 0.01 * gradiente_pesos2
        self.pesos[2] -= 0.01 * gradiente_pesos3
    
        self.biases[0] -= 0.01 * gradiente_bias1
        self.biases[1] -= 0.01 * gradiente_bias2
        self.biases[2] -= 0.01 * gradiente_bias3
