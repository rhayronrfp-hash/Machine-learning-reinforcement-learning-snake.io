import ML as m
import pygame
import math
import funções as f
import random
import numpy as np
from colisoes_wrapper import ColisoesCPP

textos = {
    "pt": {
        "respawn": "Respawn",
        "dados": "Dados",
        "normal": "+ Cobra normal",
        "mestre": "+ Cobra MESTRE",
        "remover": "- Remover cobra",
        "estado": "Estado",
        "acao": "Ação",
        "frente": "Frente",
        "direita": "Direita",
        "esquerda": "Esquerda",
        "idioma": "PT"
    },
    "en": {
        "respawn": "Respawn",
        "dados": "Data",
        "normal": "+ Normal snake",
        "mestre": "+ MASTER snake",
        "remover": "- Remove snake",
        "estado": "State",
        "acao": "Action",
        "frente": "Forward",
        "direita": "Right",
        "esquerda": "Left",
        "idioma": "EN"
    }
}
idioma = "pt"

cores = [
    (0, 0, 255),
    (255, 0, 0),
    (0, 255, 0),
    (255, 105, 180),
    (255, 165, 0),
    (0, 0, 0),
    (128, 0, 128),
    (255, 255, 0),
    (0, 255, 255)
]
usadas = []

def cor():
    disponiveis = [c for c in cores if c not in usadas]
    if disponiveis:
        escolhida = random.choice(disponiveis)
    else:
        escolhida = random.choice(cores)
    usadas.append(escolhida)
    return escolhida

def dist_ponto_rect(px, py, rect):
    cx = max(rect.left, min(px, rect.right))
    cy = max(rect.top, min(py, rect.bottom))
    dx = px - cx
    dy = py - cy
    return math.hypot(dx, dy)

def alpha_do_botao(rect, todasascobras):
    menor = None
    for cobra in todasascobras:
        for seg in cobra["segmentos"]:
            d1 = dist_ponto_rect(seg["inicio"][0], seg["inicio"][1], rect)
            d2 = dist_ponto_rect(seg["fim"][0], seg["fim"][1], rect)
            d = min(d1, d2)
            if menor is None or d < menor:
                menor = d
    if menor is None:
        return 255
    limite = 80
    if menor >= limite:
        return 255
    return int(60 + (menor / limite) * 195)

def desenhar_botao(rect, cor_fundo, cor_borda, texto, cor_texto, fonte_usada, alpha=255):
    superficie = pygame.Surface((rect.width + 6, rect.height + 6), pygame.SRCALPHA)
    pygame.draw.rect(superficie, (20, 20, 20, alpha), pygame.Rect(3, 3, rect.width, rect.height), border_radius=10)
    pygame.draw.rect(superficie, (*cor_fundo, alpha), pygame.Rect(0, 0, rect.width, rect.height), border_radius=10)
    pygame.draw.rect(superficie, (*cor_borda, alpha), pygame.Rect(0, 0, rect.width, rect.height), width=3, border_radius=10)

    texto_render = fonte_usada.render(texto, True, cor_texto)
    texto_superficie = pygame.Surface(texto_render.get_size(), pygame.SRCALPHA)
    texto_superficie.blit(texto_render, (0, 0))
    texto_superficie.set_alpha(alpha)

    superficie.blit(texto_superficie, (rect.width // 2 - texto_render.get_width() // 2, rect.height // 2 - texto_render.get_height() // 2))
    tela.blit(superficie, (rect.x, rect.y))


pygame.init()
info = pygame.display.Info()
largura = info.current_w
altura = info.current_h
tela = pygame.display.set_mode((largura, altura))
pygame.display.set_caption("Snake.io")
relogio = pygame.time.Clock()
fundo = (50, 50, 50)
comidacor = (255, 200, 50)
fonte = pygame.font.Font(None, 36)
fonte_pequena = pygame.font.Font(None, 22)

respawn = True
dados = False
rodando = True

colisoes_engine = ColisoesCPP()

for i in range(30):
    f.criarcomida()

c = f.spawn(1)
for cobra in c[:-1]:
    cobra["cor"] = cor()
    cobra["tipo"] = "normal"

c[-1]["cor"] = (255, 255, 255)
c[-1]["tipo"] = "mestre"

y_botoes = altura - 90
ativarespawn = pygame.Rect(70, y_botoes, 200, 60)
ativadados = pygame.Rect(300, y_botoes, 200, 60)
spawnanormal = pygame.Rect(530, y_botoes, 220, 60)
spawnamestre = pygame.Rect(770, y_botoes, 220, 60)
removercobra = pygame.Rect(1010, y_botoes, 220, 60)
botaoidioma = pygame.Rect(1250, y_botoes, 70, 60)


while rodando:
    t = textos[idioma]
    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            rodando = False
        if evento.type == pygame.MOUSEBUTTONDOWN:
            if ativarespawn.collidepoint(evento.pos):
                respawn = not respawn
            if ativadados.collidepoint(evento.pos):
                dados = not dados
            if spawnanormal.collidepoint(evento.pos):
                novacobra = f.spawn(0)[0]
                novacobra["cor"] = cor()
                novacobra["tipo"] = "normal"

                if c:
                    indice_mestre = next((i for i, cb in enumerate(c) if cb["tipo"] == "mestre"), len(c))
                    c.insert(indice_mestre, novacobra)
                else:
                    c.append(novacobra)
            if spawnamestre.collidepoint(evento.pos):
                novamestre = f.spawn(0)[0]
                novamestre["cor"] = (255, 255, 255)
                novamestre["tipo"] = "mestre"
                c.append(novamestre)
            if removercobra.collidepoint(evento.pos):
                if c:
                    c.pop()
            if botaoidioma.collidepoint(evento.pos):
                idioma = "en" if idioma == "pt" else "pt"

    todasascobras = c

    for cobra in todasascobras:
        ia = cobra["ia"]

        estado = f.observar(cobra, todasascobras)
        acao, valorq, z1, z2, camada2, camada1, valor = ia.calcular(estado)

        f.acaoo(cobra, acao)
        cobra["acao"] = acao
        f.movercobra(cobra)

        recompensa = -0.1

        cabeca = cobra["segmentos"][-1]["fim"]

        for comida in f.comidas[:]:
            diferencax = cabeca[0] - comida[0]
            diferencay = cabeca[1] - comida[1]

            distancia = diferencax * diferencax + diferencay * diferencay
            if distancia < 15 * 15:
                f.comidas.remove(comida)
                recompensa += 10
                cobra["crescer"] += 10

                for o in range(2):
                    f.criarcomida()

        cobra["_ia_cache"] = {"valorq": valorq, "z1": z1, "z2": z2, "camada1": camada1, "camada2": camada2, "valor": valor, "acao": acao, "recompensa": recompensa, "morreu": False}

    colisoes_resultado = colisoes_engine.calcular_colisoes(todasascobras)
    cobrasmortas = []

    for i, cobra1 in enumerate(todasascobras):
        if cobra1 in cobrasmortas:
            continue

        if colisoes_resultado[i]:
            j = colisoes_resultado[i][0]
            cobra2 = todasascobras[j]

            cobra2["_ia_cache"]["recompensa"] += 100
            cobra1["_ia_cache"]["recompensa"] -= 100
            cobra1["_ia_cache"]["morreu"] = True
#esse respawn aqui tava sendo colocado em um if no início desse código de for cobra mortas, aí eu estava fazendo esse código todo e depois repetia o código se não fosse true (mal otimizado,  aí um amigo meu viu isso e me chamou de burro, porque eu só poderia ter colocado aqui nessa parte
            if respawn:
                cabeca_seg = cobra1["segmentos"][-1]
                cabeca_seg["fim"][0] += 6767
                cabeca_seg["fim"][1] += 6767
            else:
                cobrasmortas.append(cobra1)

    mestres = [cobra for cobra in todasascobras if cobra["tipo"] == "mestre"]
    for mestre in mestres:
        for camada in range(len(mestre["ia"].pesos)):
            pesoss = [cobra["ia"].pesos[camada] for cobra in todasascobras]
            mestre["ia"].pesos[camada] = np.mean(pesoss, axis=0)

    for cobra in todasascobras:
        cache = cobra["_ia_cache"]
        ia = cobra["ia"]

        novo_estado = f.observar(cobra, todasascobras)

        if cache["morreu"]:
            qacao = cache["valorq"][0][cache["acao"]]
            queremos = cache["recompensa"]
            acao = cache["acao"]
        else:
            qacao, queremos, acao = ia.calcular_alvo(cache["valorq"], cache["recompensa"], cache["acao"], novo_estado)

        ia.propagacao(cache["z1"], cache["z2"], cache["camada2"], cache["camada1"], cache["valor"], qacao, queremos, acao)

        cobra["recompensa_total"] = cobra.get("recompensa_total", 0) + cache["recompensa"]

    for cobra in cobrasmortas:
        if cobra in todasascobras:
            todasascobras.remove(cobra)

    tela.fill(fundo)
#parte infernal
    desenhar_botao(
        ativarespawn,
        (60, 160, 70) if respawn else (140, 60, 60),
        (255, 255, 255),
        t["respawn"] + ": " + ("ON" if respawn else "OFF"),
        (255, 255, 255),
        fonte,
        alpha_do_botao(ativarespawn, todasascobras)
    )
    desenhar_botao(
        ativadados,
        (60, 120, 170) if dados else (90, 90, 90),
        (255, 255, 255),
        t["dados"] + ": " + ("ON" if dados else "OFF"),
        (255, 255, 255),
        fonte,
        alpha_do_botao(ativadados, todasascobras)
    )
    desenhar_botao(
        spawnanormal,
        (70, 130, 180),
        (200, 220, 255),
        t["normal"],
        (255, 255, 255),
        fonte_pequena,
        alpha_do_botao(spawnanormal, todasascobras)
    )
    desenhar_botao(
        spawnamestre,
        (180, 140, 40),
        (255, 230, 150),
        t["mestre"],
        (255, 255, 255),
        fonte_pequena,
        alpha_do_botao(spawnamestre, todasascobras)
    )
    desenhar_botao(
        removercobra,
        (150, 50, 50),
        (255, 200, 200),
        t["remover"],
        (255, 255, 255),
        fonte_pequena,
        alpha_do_botao(removercobra, todasascobras)
    )
    desenhar_botao(
        botaoidioma,
        (90, 90, 150),
        (220, 220, 255),
        t["idioma"],
        (255, 255, 255),
        fonte_pequena,
        alpha_do_botao(botaoidioma, todasascobras)
    )

    cobra_destaque = None
    if todasascobras:
        cobra_destaque = max(todasascobras, key=lambda cb: cb.get("recompensa_total", 0))

    for indice_cobra in range(len(todasascobras)):
        cobra = todasascobras[indice_cobra]

        corcobra = (255, 255, 255) if cobra["tipo"] == "mestre" else cobra["cor"]

        if cobra is cobra_destaque:
            for seg in cobra["segmentos"]:
                pygame.draw.line(tela, (255, 255, 120), (int(seg["inicio"][0]), int(seg["inicio"][1])), (int(seg["fim"][0]), int(seg["fim"][1])), 28)

        if dados:
            a = f.observar(cobra, todasascobras)
            texto2 = fonte.render(f"{t['estado']}: {[f'{valor:.1f}' for valor in a]}", True, corcobra)
            tela.blit(texto2, (10, 40 + indice_cobra * 30))

            acao = cobra["acao"]
            if acao == 0:
                textoacao = t["frente"]
            elif acao == 1:
                textoacao = t["direita"]
            elif acao == 2:
                textoacao = t["esquerda"]

            texto = fonte.render(t["acao"] + ": " + textoacao, True, corcobra)
            tela.blit(texto, (600, 40 + indice_cobra * 30))

        for seg in cobra["segmentos"]:
            pygame.draw.line(tela, corcobra, (int(seg["inicio"][0]), int(seg["inicio"][1])), (int(seg["fim"][0]), int(seg["fim"][1])), 16)

    for comida in f.comidas:
        pygame.draw.circle(tela, comidacor, (int(comida[0]), int(comida[1])), 5)

    pygame.display.flip()
    relogio.tick(60)

colisoes_engine.fechar()
pygame.quit()
