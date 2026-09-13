import ML as m
import random
import math
largura, altura = 1200, 1500 #usei o da minha tela aq
comidas = []


def criarcobra(x, y, cor, movimentox, movimentoy):
    comprimento_inicial = 40

    segmentos = [{
        "inicio": [x - movimentox * comprimento_inicial, y - movimentoy * comprimento_inicial],
        "fim": [x, y]
    }]

    return {
        "acao": 0,
        "segmentos": segmentos,
        "comprimento_alvo": comprimento_inicial,
        "recompensa": 0,
        "recompensa_total": 0,
        "movimentox": movimentox,
        "movimentoy": movimentoy,
        "velocidade": 3,
        "crescer": 0,
        "tipo": "normal",
        "ia": m.ML()
    }


def spawn(vezes):
    b = []
    distancia_minima = 100

    for vezes in range(vezes + 1):
        tentativas = 0
        while True:
            x = random.randint(10, 700)
            y = random.randint(10, 500)
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
            0
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


def distancia_da_cobra(cobra, cobras):
    cabeca = cobra["segmentos"][-1]["fim"]
    menor_distancia = float("inf")

    for outra in cobras:
        if outra is cobra:
            continue

        cabeca2 = outra["segmentos"][-1]["fim"]

        dx = cabeca[0] - cabeca2[0]
        dy = cabeca[1] - cabeca2[1]

        distancia = dx * dx + dy * dy

        if distancia < menor_distancia:
            menor_distancia = distancia

    if menor_distancia == float("inf"):
        return largura

    return math.sqrt(menor_distancia)


def observar(cobra, cobras):
    cabeca = cobra["segmentos"][-1]["fim"]

    distância = distancia_da_comida(cobra, comidas)
    distánciacobra = distancia_da_cobra(cobra, cobras)

    if distância == float("inf"):
        distância = largura

    return [
        cobra["movimentox"],
        cobra["movimentoy"],
        cabeca[0] / largura,
        cabeca[1] / altura,
        distância / largura,
        distánciacobra / largura
    ]


def criarcomida():
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


def segmentos_para_autocolisao(cobra, margem=40):
    segmentos = cobra["segmentos"]
    resultado = []
    percorrido = 0.0

    for indice in range(len(segmentos) - 1, -1, -1):
        seg = segmentos[indice]
        comprimento = comprimento_segmento(seg)

        if indice == len(segmentos) - 1:
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
        x1, y1 = seg["inicio"]
        x2, y2 = seg["fim"]

        novo_inicio = [
            x1 + (x2 - x1) * fr,
            y1 + (y2 - y1) * fr
        ]

        resultado.append({
            "inicio": novo_inicio,
            "fim": [x2, y2]
        })

        percorrido = margem

    resultado.reverse()
    return resultado


def movercobra(cobra):
    segmentos = cobra["segmentos"]
    movimentox = cobra["movimentox"]
    movimentoy = cobra["movimentoy"]
    velocidade = cobra["velocidade"]
    cabeca_seg = segmentos[-1]

    cabeca_seg["fim"][0] += movimentox * velocidade
    cabeca_seg["fim"][1] += movimentoy * velocidade

    novox = cabeca_seg["fim"][0] + movimentox * velocidade
    novoy = cabeca_seg["fim"][1] + movimentoy * velocidade

    if novox < 0 or novox > largura or novoy < 0 or novoy > altura:
        novox = random.randint(20, largura - 20)
        novoy = random.randint(20, altura)
    
        cabeca_seg["inicio"] = [
            novox - movimentox * comprimento_segmento(cabeca_seg),
            novoy - movimentoy * comprimento_segmento(cabeca_seg)
        ]
    
    cabeca_seg["fim"][0] = novox
    cabeca_seg["fim"][1] = novoy

    if cobra["crescer"] > 0:
        cobra["comprimento_alvo"] += velocidade
        cobra["crescer"] -= velocidade
    if cobra["crescer"] < 0:
        cobra["crescer"] = 0
        return

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


def acaoo(cobra, fazer):
    movimentox = cobra["movimentox"]
    movimentoy = cobra["movimentoy"]

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
