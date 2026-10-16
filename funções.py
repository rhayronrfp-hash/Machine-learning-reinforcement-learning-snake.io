import ML as m
import random
import math
from collections import deque
comidas = []
import pygame

class pooldeds:
    def __init__(self, capacidade):
        self.livres = list(range(capacidade))

    def alocar(self):
        if not self.livres:
            raise RuntimeError(f"sem IDs livres para novas cobras (limite: {len(self.livres)})")
        return self.livres.pop(0)

    def liberar(self, id):
        if id not in self.livres:
            self.livres.append(id)


pool_ids = pooldeds(100)
historico_recompensas = {}
historico_avaliacao = deque(maxlen=100)


def registrar_vida(id, recompensa_total):
    if id not in historico_recompensas:
        historico_recompensas[id] = deque(maxlen=10)
    historico_recompensas[id].append(recompensa_total)

def registrar_vida_avaliacao(recompensa_total):
    historico_avaliacao.append(recompensa_total)

contagem = {}


def zerar_contagem():
    contagem.clear()
    for chave in ("frames_cobra", "comidas", "kills", "mortes_corpo", "mortes_cabeca", "mortes_mutua", "mortes_parede"):
        contagem[chave] = 0


def contar(chave, quantidade=1):
    contagem[chave] += quantidade

def mortes_contagem():
    return sum(valor for chave, valor in contagem.items() if chave.startswith("mortes_"))


def pontuacao_contagem():
    if contagem["frames_cobra"] == 0:
        return None
    return 1000 * (10 * contagem["comidas"] + 40 * contagem["kills"] - 20 * mortes_contagem()) / contagem["frames_cobra"]

def resumo_contagem():
    frames = max(contagem["frames_cobra"], 1)
    mortes = mortes_contagem()
    pontuacao = pontuacao_contagem()
    duelos = contagem["kills"] + contagem["mortes_corpo"]
    frames_por_vida = f"{frames / mortes:.0f}" if mortes else "sem_mortes"
    return (
        f"frames_cobra={contagem['frames_cobra']} "
        f"comidas/1k={1000 * contagem['comidas'] / frames:.2f} "
        f"kills/1k={1000 * contagem['kills'] / frames:.2f} "
        f"mortes/1k={1000 * mortes / frames:.2f} "
        f"frames/vida={frames_por_vida} "
        f"duelos_ganhos={contagem['kills']}/{duelos} "
        f"(corpo={contagem['mortes_corpo']} cabeca={contagem['mortes_cabeca']} "
        f"mutua={contagem['mortes_mutua']} parede={contagem['mortes_parede']}) "
        f"pontuacao={pontuacao if pontuacao is None else round(pontuacao, 2)}"
    )


zerar_contagem()


def criarcobra(x, y, cor, movimentox, movimentoy, mandar):
    comprimento_inicial = 40
    segmentos = [{
        "inicio": [x - movimentox * comprimento_inicial, y - movimentoy * comprimento_inicial],
        "fim": [x, y]
    }]

    id_ia = pool_ids.alocar()
    historico_recompensas.pop(id_ia, None)

    return {
        "acao": 0,
        "segmentos": segmentos,
        "comprimento_alvo": comprimento_inicial,
        "recompensa": 0,
        "recompensa_total": 0,
        "movimentox": movimentox,
        "movimentoy": movimentoy,
        "movimentox_anterior": movimentox,
        "movimentoy_anterior": movimentoy,
        "velocidade": 3,
        "crescer": 0,
        "dist_anterior": None,
        "dist_anterior_cobra": None,
        "_estado_cache": None,
        "ia": m.ML(mandar, id_ia)
    }


def spawn(vezes, mandar, largura, altura):
    b = []
    distancia_minima = 100

    for vezes in range(vezes + 1):
        tentativas = 0
        while True:
            x = random.randint(10, largura)
            y = random.randint(10, altura)
            longe_o_suficiente = True

            for outra in b:
                outra_cabeca = outra["segmentos"][-1]["fim"]
                dx = x - outra_cabeca[0]
                dy = y - outra_cabeca[1]

                if dx * dx + dy * dy < distancia_minima * distancia_minima:
                    longe_o_suficiente = False
                    break
            tentativas += 1
            
            if longe_o_suficiente or tentativas > 50:
                break
        a = criarcobra(
            x,
            y,
            (50, 220, 80),
            1,
            0,
            mandar
        )
        b.append(a)

    return b


def distancia_da_comida(cobra, comida):
    if not comida:
        return float("inf")

    cabeca = cobra["segmentos"][-1]["fim"]

    menor_distancia = float("inf")

    for x, y in comida:
        dx = cabeca[0] - x
        dy = cabeca[1] - y
        distancia = dx * dx + dy * dy

        if distancia < menor_distancia:
            menor_distancia = distancia

    return math.sqrt(menor_distancia)

def segmento_intercepta(p1, p2, q1, q2):
    def ccw(A, B, C):
        return (C[1] - A[1]) * (B[0] - A[0]) > (B[1] - A[1]) * (C[0] - A[0])
    return ccw(p1, q1, q2) != ccw(p2, q1, q2) and ccw(p1, p2, q1) != ccw(p1, p2, q2)
    
def vetor_atecomida(cobra, comida):
    if not comida:
        return 0, 0

    cabeca = cobra["segmentos"][-1]["fim"]
    corpo = cobra["segmentos"][:-1]
    
    comidas_ordenadas = sorted(comida, key=lambda c: (c[0] - cabeca[0])**2 + (c[1] - cabeca[1])**2)
    candidatas = comidas_ordenadas[:5]
    
    melhor_dx, melhor_dy = 0, 0
    menor_distancia = float("inf")

    for x, y in candidatas:
        comida_pos = [x, y]
        bloqueado = False
        for seg in corpo:
            if segmento_intercepta(cabeca, comida_pos, seg["inicio"], seg["fim"]):
                bloqueado = True
                break
        if not bloqueado:
            dx = x - cabeca[0]
            dy = y - cabeca[1]
            distancia = dx * dx + dy * dy
            if distancia < menor_distancia:
                menor_distancia = distancia
                melhor_dx, melhor_dy = dx, dy
                break

    if menor_distancia == float("inf") and candidatas:
        x, y = candidatas[0]
        melhor_dx = x - cabeca[0]
        melhor_dy = y - cabeca[1]

    return melhor_dx, melhor_dy



def ponto_mais_proximo_segmento(px, py, inicio, fim):
    dx = fim[0] - inicio[0]
    dy = fim[1] - inicio[1]
    comp2 = dx * dx + dy * dy

    if comp2 < 1e-10:
        return inicio[0], inicio[1]

    t = ((px - inicio[0]) * dx + (py - inicio[1]) * dy) / comp2
    t = max(0.0, min(1.0, t))
    return inicio[0] + t * dx, inicio[1] + t * dy


def vetor_atecobra(cobra, cobras):
    cabeca = cobra["segmentos"][-1]["fim"]
    menor_distancia = float("inf")
    melhor_dx, melhor_dy = 0, 0
    melhor_mx, melhor_my = 0, 0

    for outra in cobras:
        if outra is cobra:
            continue

        for segmento in outra["segmentos"]:
            px, py = ponto_mais_proximo_segmento(cabeca[0], cabeca[1], segmento["inicio"], segmento["fim"])
            dx = px - cabeca[0]
            dy = py - cabeca[1]

            distancia = dx * dx + dy * dy

            if distancia < menor_distancia:
                menor_distancia = distancia
                melhor_dx, melhor_dy = dx, dy
                melhor_mx, melhor_my = outra["movimentox"], outra["movimentoy"]

    return melhor_dx, melhor_dy, melhor_mx, melhor_my


def distancia_da_cobra(cobra, cobras):
    margem_pescoco = 60.0
    cabeca_propria = cobra["segmentos"][-1]["fim"]
    corpo = segmentos_sem_pescoco(cobra["segmentos"] + [{"inicio": cabeca_propria, "fim": cabeca_propria}], margem_pescoco)
    menor_distancia = float("inf")

    for outra in cobras:
        if outra is cobra:
            continue

        cabeca = outra["segmentos"][-1]["fim"]

        for segmento in corpo:
            px, py = ponto_mais_proximo_segmento(cabeca[0], cabeca[1], segmento["inicio"], segmento["fim"])
            dx = cabeca[0] - px
            dy = cabeca[1] - py
            distancia = dx * dx + dy * dy

            if distancia < menor_distancia:
                menor_distancia = distancia

    return math.sqrt(menor_distancia)


def segmentos_sem_pescoco(segmentos, margem):
    resultado = []
    percorrido = 0.0
    n = len(segmentos)

    for indice in range(n - 1, -1, -1):
        seg = segmentos[indice]
        comprimento = math.hypot(
            seg["fim"][0] - seg["inicio"][0],
            seg["fim"][1] - seg["inicio"][1]
        )

        if indice == n - 1:
            percorrido += comprimento
            continue
        if percorrido + comprimento <= margem:
            percorrido += comprimento
            continue
        if percorrido >= margem:
            resultado.append(seg)
            continue

        falta = margem - percorrido
        fr = falta / comprimento
        novo = {
            "inicio": seg["inicio"],
            "fim": [
                seg["fim"][0] + (seg["inicio"][0] - seg["fim"][0]) * fr,
                seg["fim"][1] + (seg["inicio"][1] - seg["fim"][1]) * fr
            ]
        }
        resultado.append(novo)
        percorrido = margem

    resultado.reverse()
    return resultado


def dist_parede(px, py, dx, dy, largura, altura):
    if dx > 0:
        return largura - px
    if dx < 0:
        return px
    if dy > 0:
        return altura - py
    if dy < 0:
        return py
    return float("inf")


def perigos(cobra, cobras, mx, my, largura, altura):
      cabeca = cobra["segmentos"][-1]["fim"]
      frente = (mx, my)
      direita = (-my, mx)
      esquerda = (my, -mx)  
           
      alcance = 900
      largura_area = 260
      margem_pescoco = 60.0
      
      perigo_frente = dist_parede(cabeca[0], cabeca[1], frente[0], frente[1], largura, altura)
      perigo_direita = dist_parede(cabeca[0], cabeca[1], direita[0], direita[1], largura, altura)
      perigo_esquerda = dist_parede(cabeca[0], cabeca[1], esquerda[0], esquerda[1], largura, altura)
  
              
      for outra in cobras:
        if outra is cobra:
            segmentos_avaliar = segmentos_sem_pescoco(outra["segmentos"], margem_pescoco)
            
        else:
            segmentos_avaliar = outra["segmentos"]
        for segmento in segmentos_avaliar:
            ponto2 = segmento["inicio"]
            ponto = segmento["fim"]
            distancia = math.hypot(
                ponto[0] - ponto2[0],
                ponto[1] - ponto2[1]
            )
            passos = max(1, int(distancia / 5))
            for i in range(passos + 1):
                t = i / passos

                x = ponto2[0] + (ponto[0] - ponto2[0]) * t
                y = ponto2[1] + (ponto[1] - ponto2[1]) * t
                dx = x - cabeca[0]
                dy = y - cabeca[1]
                
                dist_frente = dx * frente[0] + dy * frente[1]
                dist_lado = dx * direita[0] + dy * direita[1]
                if 0 <= dist_frente < perigo_frente and abs(dist_lado) <= largura_area:
                    perigo_frente = dist_frente
                        
                dist_direita = dx * direita[0] + dy * direita[1]
                dist_lado = dx * frente[0] + dy * frente[1]
                
                if 0 <= dist_direita < perigo_direita and -50 <= dist_lado <= largura_area:
                    perigo_direita = dist_direita 
                                            
                dist_esquerda = dx * esquerda[0] + dy * esquerda[1]
                dist_lado = dx * frente[0] + dy * frente[1]  
                              
                if 0 <= dist_esquerda < perigo_esquerda and -50 <= dist_lado <= largura_area:
                    perigo_esquerda = dist_esquerda
                    
      perigo_frente = 1.0 - min(perigo_frente, alcance) / alcance
      perigo_direita = 1.0 - min(perigo_direita, alcance) / alcance
      perigo_esquerda = 1.0 - min(perigo_esquerda, alcance) / alcance
      return perigo_frente, perigo_direita, perigo_esquerda

def ver(cobra, tela, mx, my):
    alcance = 900
    largura_area = 260
    
    cabeca = cobra["segmentos"][-1]["fim"]
    
    frente = (mx, my)
    direita = (-my, mx)
    
    p1 = (
        cabeca[0] + direita[0] * largura_area,
        cabeca[1] + direita[1] * largura_area
    )
    
    p2 = (
        cabeca[0] + direita[0] * -largura_area,
        cabeca[1] + direita[1] * -largura_area
    )
    
    p3 = (
        p2[0] + frente[0] * alcance,
        p2[1] + frente[1] * alcance
    )
    
    p4 = (
        p1[0] + frente[0] * alcance,
        p1[1] + frente[1] * alcance
    )
    
    pygame.draw.polygon(tela, (255, 0, 0), [p1, p2, p3, p4], 2)         
                  
                  
                      
                              
def observar(cobra, cobras, largura, altura):
    cabeca = cobra["segmentos"][-1]["fim"]

    dx_comida, dy_comida = vetor_atecomida(cobra, comidas)
    dx_cobra, dy_cobra, mx_cobra, my_cobra = vetor_atecobra(cobra, cobras)
    d = math.hypot(dx_comida, dy_comida)
    
    if d > 0:
        comida_vertical = (dx_comida * cobra["movimentox"] + dy_comida * cobra["movimentoy"]) / d
        comida_horizontal = (dx_comida * (-cobra["movimentoy"]) + dy_comida * cobra["movimentox"]) / d
    else:
        comida_vertical = 0
        comida_horizontal = 0
  
    
        
    frente, direita, esquerda = perigos(cobra, cobras, cobra["movimentox"], cobra["movimentoy"], largura, altura)
    return [
        cobra["movimentox"],
        cobra["movimentoy"],
        cabeca[0] / largura,
        cabeca[1] / altura,
        comida_vertical,
        comida_horizontal,
        dx_cobra / largura,
        dy_cobra / altura,
        frente,
        direita,
        esquerda,
        cobra["movimentox_anterior"],
        cobra["movimentoy_anterior"],
        mx_cobra,
        my_cobra
    ]


def criarcomida(largura, altura):
    x = random.randint(20, largura)
    y = random.randint(20, altura)
    comidas.append([x, y])


def comprimento_segmento(seg):
    return math.hypot(
        seg["fim"][0] - seg["inicio"][0],
        seg["fim"][1] - seg["inicio"][1]
    )


def comprimento_total(cobra):
    return sum(comprimento_segmento(s) for s in cobra["segmentos"])


def movercobra(cobra, largura, altura):
    segmentos = cobra["segmentos"]
    movimentox = cobra["movimentox"]
    movimentoy = cobra["movimentoy"]
    velocidade = cobra["velocidade"]
    cabeca_seg = segmentos[-1]

    novox = cabeca_seg["fim"][0] + movimentox * velocidade
    novoy = cabeca_seg["fim"][1] + movimentoy * velocidade
    novox = max(0, min(novox, largura))
    novoy = max(0, min(novoy, altura))

    cabeca_seg["fim"][0] = novox
    cabeca_seg["fim"][1] = novoy
    if cobra["crescer"] > 0:
        crescimento = min(velocidade, cobra["crescer"])
        cobra["comprimento_alvo"] += crescimento
        cobra["crescer"] -= crescimento
    else:
        ex = comprimento_total(cobra) - cobra["comprimento_alvo"]
        while ex > 0 and segmentos:
            cauda = segmentos[0]
            c = comprimento_segmento(cauda)
            if c <= ex:
                ex -= c
                segmentos.pop(0)
            else:
                dx = cauda["fim"][0] - cauda["inicio"][0]
                dy = cauda["fim"][1] - cauda["inicio"][1]
                fr = ex / c
                cauda["inicio"][0] += dx * fr
                cauda["inicio"][1] += dy * fr
                ex = 0

def respawnar(cobra, todasascobras, largura, altura):
    comprimento_inicial = 40
    tentativas = 0

    while True:
        x = random.randint(50, largura - 50)
        y = random.randint(50, altura - 50)

        longe_o_suficiente = True

        for outra in todasascobras:
            if outra is cobra:
                continue

            cabeca = outra["segmentos"][-1]["fim"]

            dx = x - cabeca[0]
            dy = y - cabeca[1]

            if dx * dx + dy * dy < 100 * 100:
                longe_o_suficiente = False
                break

        tentativas += 1

        if longe_o_suficiente or tentativas > 50:
            break

    cobra["segmentos"] = [{
        "inicio": [x - comprimento_inicial, y],
        "fim": [x, y]
    }]

    cobra["comprimento_alvo"] = comprimento_inicial
    cobra["recompensa_total"] = 0
    cobra["crescer"] = 0
    cobra["movimentox"] = 1
    cobra["movimentoy"] = 0
    cobra["movimentox_anterior"] = 1
    cobra["movimentoy_anterior"] = 0
    cobra["acao"] = 0
    cobra["dist_anterior"] = None
    cobra["dist_anterior_cobra"] = None
    cobra["_estado_cache"] = None
    for outra in todasascobras:
        outra["dist_anterior_cobra"] = None
    
def acaoo(cobra, fazer):
    movimentox = cobra["movimentox"]
    movimentoy = cobra["movimentoy"]

    cobra["movimentox_anterior"] = movimentox
    cobra["movimentoy_anterior"] = movimentoy

    if fazer == 1:
        nova_movimentox = -movimentoy
        nova_movimentoy = movimentox
    elif fazer == 2:
        nova_movimentox = movimentoy
        nova_movimentoy = -movimentox
    else:
        return
    cobra["movimentox"] = nova_movimentox
    cobra["movimentoy"] = nova_movimentoy

    cabeca = list(cobra["segmentos"][-1]["fim"])

    cobra["segmentos"].append({
        "inicio": cabeca,
        "fim": list(cabeca)
    })