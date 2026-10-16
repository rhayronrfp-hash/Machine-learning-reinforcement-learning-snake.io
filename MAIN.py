import ML as m
import pygame
import math
import funções as f
import random
from collections import deque
#fiz o melhor que consegui pra otimizar(talvez seja meu celular que esteja mt travado)
textos = {
    "pt": {
        "respawn": "Respawn",
        "dados": "Dados",
        "normal": "+ Cobra normal",
        "comida": "+ Comida",
        "remover": "- Remover cobra",
        "estado": "Estado",
        "acao": "Ação",
        "frente": "Frente",
        "direita": "Direita",
        "esquerda": "Esquerda",
        "avaliacao": "Avaliação",
        "epsilon": "Epsilon",
        "idioma": "PT"
    },
    "en": {
        "respawn": "Respawn",
        "dados": "Data",
        "normal": "+ Normal snake",
        "comida": "+ Food",
        "remover": "- Remove snake",
        "estado": "State",
        "acao": "Action",
        "frente": "Forward",
        "direita": "Right",
        "esquerda": "Left",
        "avaliacao": "Evaluation",
        "epsilon": "Epsilon",
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
    (0, 255, 255),
    (255, 255, 255)
]

def cor():
    return random.choice(cores)

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

def criar_botoes(largura, altura):
    y_botoes = altura - 90
    quantidade, espacamento= 8, 10
    largura_idioma = 100
    largura_botao = (largura - (espacamento * (quantidade - 1)) - largura_idioma - 40) // 7
    
    x = 20

    ativarespawn = pygame.Rect(x, y_botoes, largura_botao, 60)
    x += largura_botao + espacamento

    ativadados = pygame.Rect(x, y_botoes, largura_botao, 60)
    x += largura_botao + espacamento

    spawnanormal = pygame.Rect(x, y_botoes, largura_botao, 60)
    x += largura_botao + espacamento

    botaocomida = pygame.Rect(x, y_botoes, largura_botao, 60)
    x += largura_botao + espacamento

    removercobra = pygame.Rect(x, y_botoes, largura_botao, 60)
    x += largura_botao + espacamento

    ativaravaliacao = pygame.Rect(x, y_botoes, largura_botao, 60)
    x += largura_botao + espacamento
    
    epsilion = pygame.Rect(x, y_botoes, largura_botao, 60)
    x+= largura_botao + espacamento
    
    botaoidioma = pygame.Rect(x, y_botoes, largura_idioma, 60)
    x += largura_idioma + espacamento
    
    return (
        ativarespawn,
        ativadados,
        spawnanormal,
        botaocomida,
        removercobra,
        ativaravaliacao,
        epsilion,
        botaoidioma
    )
    
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

def desenhar_menu_epsilon():
    largura_menu = 400
    altura_menu = 220
    x = largura // 2 - largura_menu // 2
    y = altura // 2 - altura_menu // 2

    pygame.draw.rect(tela, (30, 30, 30), (x, y, largura_menu, altura_menu), border_radius=15)
    pygame.draw.rect(tela, (180, 190, 255), (x, y, largura_menu, altura_menu), width=3, border_radius=15)

    titulo = fonte.render("Epsilon", True, (255, 255, 255))
    tela.blit(titulo, (x + largura_menu // 2 - titulo.get_width() // 2, y + 25))

    campo = pygame.Rect(x + 40, y + 80, largura_menu - 80, 45)
    pygame.draw.rect(tela, (60, 60, 60), campo, border_radius=8)
    pygame.draw.rect(tela, (220, 220, 220), campo, width=2, border_radius=8)

    texto = fonte.render(texto_epsilon, True, (255, 255, 255))
    tela.blit(texto, (campo.x + 10, campo.y + 5))

    confirmar = fonte_pequena.render("ENTER = Confirmar    ESC = Cancelar", True, (220, 220, 220))
    tela.blit(confirmar, (x + largura_menu // 2 - confirmar.get_width() // 2, y + 150))


pygame.init()
info = pygame.display.Info()
largura, altura = info.current_w, info.current_h
tela = pygame.display.set_mode((largura, altura))
pygame.display.set_caption("Snake.io")
relogio = pygame.time.Clock()
fundo = (50, 50, 50)
comidacor = (255, 200, 50)
fonte = pygame.font.Font(None, 36)
fonte_pequena = pygame.font.Font(None, 22)
(
    ativarespawn,
    ativadados,
    spawnanormal,
    botaocomida,
    removercobra,
    ativaravaliacao,
    episilion,
    botaoidioma
) = criar_botoes(largura, altura)
respawn = True
dados = False
rodando = True
contador_frames = 0
framedesenho = 4

try:
    with open("melhor_avaliacao.txt") as arquivo:
        melhor_pontuacao_conhecida = float(arquivo.read())
except (FileNotFoundError, ValueError):
    melhor_pontuacao_conhecida = float("-inf")

minimo_amostras = 64
epsilon_final = 0.1
decaimento_epsilon = 0.00001
parede_mata = True
frames_janela = 0
frames_janela_avaliacao = 5000
frames_treinados = 0
minimo_frames_para_salvar = 20000
margem_melhoria = 2.0
epsilon_manual = False
epsilon_anterior = 0
menu_epsilon = False
texto_epsilon = ""
avaliacao = False
mandar = m.Calculo_da_rede()

ok = mandar.carregar()
if not ok:
    mandar.inicializar()

c = f.spawn(1, mandar, largura, altura)
for cobra in c:
    cobra["cor"] = cor()

epsilon_atual = mandar.obter_epsilon()
mandar.set_minimo_amostras(minimo_amostras)

for i in range(10):
    f.criarcomida(largura, altura)
while rodando:
    contador_frames += 1
    t = textos[idioma]
    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            rodando = False

        if menu_epsilon:
            if evento.type == pygame.MOUSEBUTTONDOWN:
                largura_menu = 400
                altura_menu = 220
                x = largura // 2 - largura_menu // 2
                y = altura // 2 - altura_menu // 2
                campo = pygame.Rect(x + 40, y + 80, largura_menu - 80, 45)

                if campo.collidepoint(evento.pos):
                    pass

            if evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_RETURN:
                    try:
                        valor = float(texto_epsilon.replace(",", "."))

                        if 0 <= valor <= 1:
                            epsilon_manual = True
                            epsilon_atual = valor

                            if not avaliacao:
                                mandar.set_epsilon(epsilon_atual)

                            menu_epsilon = False
                        else:
                            texto_epsilon = ""
                    except ValueError:
                        texto_epsilon = ""

                elif evento.key == pygame.K_ESCAPE:
                    menu_epsilon = False

                elif evento.key == pygame.K_BACKSPACE:
                    texto_epsilon = texto_epsilon[:-1]

                elif evento.unicode in "0123456789.,":
                    if evento.unicode in "., " and (("." in texto_epsilon) or ("," in texto_epsilon)):
                        continue
                    texto_epsilon += evento.unicode

            continue

        if evento.type == pygame.MOUSEBUTTONDOWN:
            
            if ativarespawn.collidepoint(evento.pos):
                respawn = not respawn
                
            if ativadados.collidepoint(evento.pos):
                dados = not dados
                
            if spawnanormal.collidepoint(evento.pos):
                try:
                    novacobra = f.spawn(0, mandar, largura, altura)[0]
                    novacobra["cor"] = cor()
                    c.append(novacobra)
                    for cobra in c:
                        cobra["_estado_cache"] = None
                        cobra["dist_anterior_cobra"] = None
                except RuntimeError as erro:
                    print(erro)                      
                             
            if botaocomida.collidepoint(evento.pos):
                f.criarcomida(largura, altura)
                for cobra in c:
                    cobra["_estado_cache"] = None
                    cobra["dist_anterior"] = None
                                
            if removercobra.collidepoint(evento.pos):
                if c:
                    cobra_removida = c.pop()
                    f.pool_ids.liberar(cobra_removida["ia"].id)
                    for cobra in c:
                        cobra["_estado_cache"] = None
                        cobra["dist_anterior_cobra"] = None
                        
                        
            if botaoidioma.collidepoint(evento.pos):
                idioma = "en" if idioma == "pt" else "pt"
                
                             
            if ativaravaliacao.collidepoint(evento.pos):
                avaliacao = not avaliacao
                f.zerar_contagem()
                frames_janela = 0
                if avaliacao:
                    mandar.set_epsilon(0.0)
                    f.historico_avaliacao.clear()
                    for cobra in c:
                        f.respawnar(cobra, c, largura, altura)
                else:
                    if epsilon_manual:
                        mandar.set_epsilon(epsilon_atual)
                    else:
                        mandar.set_epsilon(epsilon_atual)
                    
            if episilion.collidepoint(evento.pos):
                if epsilon_manual:
                    epsilon_manual = False
                    epsilon_atual = epsilon_anterior

                    if avaliacao:
                        mandar.set_epsilon(0.0)
                    else:
                        mandar.set_epsilon(epsilon_atual)
                else:
                    epsilon_anterior = epsilon_atual
                    texto_epsilon = ""
                    menu_epsilon = True

    #sim, eu poderia remover esse c e colocar so todasascobras
#mas to com preguicakkkk
    todasascobras = c

    if menu_epsilon:
        if contador_frames % framedesenho == 0:
            tela.fill(fundo)

            for cobra in todasascobras:
                corcobra = cobra["cor"]
                for seg in cobra["segmentos"]:
                    pygame.draw.line(tela, corcobra, (int(seg["inicio"][0]), int(seg["inicio"][1])), (int(seg["fim"][0]), int(seg["fim"][1])), 16)

            for comida in f.comidas:
                pygame.draw.circle(tela, comidacor, (int(comida[0]), int(comida[1])), 5)

        desenhar_menu_epsilon()
        pygame.display.flip()
        relogio.tick()
        continue
    
    f.contar("frames_cobra", len(todasascobras))
    estados = []
    for cobra in todasascobras:
        estado_em_cache = cobra.get("_estado_cache")
        if estado_em_cache is not None:
            estados.append(estado_em_cache)
        else:
            estados.append(f.observar(cobra, todasascobras, largura, altura))
        cobra["_estado_cache"] = None

    ids_lote = [cobra["ia"].id for cobra in todasascobras]
    acoes = mandar.calcular_lote(ids_lote, estados) if todasascobras else []

    for cobra, estado, acao in zip(todasascobras, estados, acoes):
        f.acaoo(cobra, acao)
        cobra["acao"] = acao        
        recompensa = -0.1
        f.movercobra(cobra, largura, altura)


        dist_atual = f.distancia_da_comida(cobra, f.comidas) / largura
        if cobra["dist_anterior"] is not None and dist_atual != float("inf") and cobra["dist_anterior"] != float("inf"):
            recompensa += 50 * (cobra["dist_anterior"] -  dist_atual)
        cobra["dist_anterior"] = dist_atual

        dist_atual_cobra = f.distancia_da_cobra(cobra, todasascobras) / largura
        if cobra["dist_anterior_cobra"] is not None and dist_atual_cobra != float("inf") and cobra["dist_anterior_cobra"] != float("inf"):
            recompensa += 50 * (cobra["dist_anterior_cobra"] -  dist_atual_cobra)
        cobra["dist_anterior_cobra"] = dist_atual_cobra

        cabeca = cobra["segmentos"][-1]["fim"]

        for comida in f.comidas[:]:
            diferencax = cabeca[0] - comida[0]
            diferencay = cabeca[1] - comida[1]

            distancia = diferencax * diferencax + diferencay * diferencay
            if distancia < 15 * 15:
                f.comidas.remove(comida)
                recompensa += 10
                cobra["crescer"] += 10
                f.contar("comidas")
                for outra in todasascobras:
                    outra["dist_anterior"] = None

                for o in range(1):
                    f.criarcomida(largura, altura)
        cobra["_ia_cache"] = {"recompensa": recompensa, "morreu": False, "estado": estado}

    colisoes_resultado = mandar.calcular_colisoes(todasascobras)
    cobrasmortas = []
    vencedores = []
    if parede_mata:
        for cobra in todasascobras:
            cabeca = cobra["segmentos"][-1]["fim"]
            if cabeca[0] <= 0 or cabeca[0] >= largura or cabeca[1] <= 0 or cabeca[1] >= altura:
                cobra["_ia_cache"]["recompensa"] -= 20
                cobra["_ia_cache"]["morreu"] = True
                cobrasmortas.append(cobra)
                f.contar("mortes_parede")
               
    pares_processados = set()
    for i, cobra1 in enumerate(todasascobras):
        if cobra1 in cobrasmortas:
            continue
        for j, tipo in colisoes_resultado[i]:
            if i == j:
                continue
    
            par = tuple(sorted((i, j)))    
            if par in pares_processados:
                continue    
            pares_processados.add(par)    
            cobra2 =todasascobras[j]    
            colisao_inversa=None
    
            for outro_j, outro_tipo in colisoes_resultado[j]:
                if outro_j == i:
                    colisao_inversa = outro_tipo
                    break
    
            if tipo == 1 or colisao_inversa == 1:
                if cobra1 not in cobrasmortas:
                    cobra1["_ia_cache"]["recompensa"] -= 20
                    cobra1["_ia_cache"]["morreu"] = True
                    cobrasmortas.append(cobra1)
                    f.contar("mortes_cabeca")
    
                if cobra2 not in cobrasmortas:
                    cobra2["_ia_cache"]["recompensa"] -= 20
                    cobra2["_ia_cache"]["morreu"] = True
                    cobrasmortas.append(cobra2)
                    f.contar("mortes_cabeca")
    
            elif colisao_inversa == 0:
                if cobra1 not in cobrasmortas:
                    cobra1["_ia_cache"]["recompensa"] -= 20
                    cobra1["_ia_cache"]["morreu"] = True
                    cobrasmortas.append(cobra1)
                    f.contar("mortes_mutua")
    
                if cobra2 not in cobrasmortas:
                    cobra2["_ia_cache"]["recompensa"] -= 20
                    cobra2["_ia_cache"]["morreu"] = True
                    cobrasmortas.append(cobra2)
                    f.contar("mortes_mutua")
    
            else:
                if cobra1 not in cobrasmortas:
                    cobra1["_ia_cache"]["recompensa"] -= 20
                    cobra1["_ia_cache"]["morreu"] = True
                    cobrasmortas.append(cobra1)    
                    f.contar("mortes_corpo")
                vencedores.append(cobra2)
    
    for vencedor in vencedores:
        if vencedor not in cobrasmortas:
            vencedor["_ia_cache"]["recompensa"] += 40
            f.contar("kills")
    
    ids_treino = []
    estados_originais_treino = []
    acoes_treino = []
    recompensas_treino = []
    estados_treino = []
    mortos_treino = []
    
    for cobra in todasascobras:
        cache = cobra["_ia_cache"]
        novo_estado = f.observar(cobra, todasascobras, largura, altura)
        ids_treino.append(cobra["ia"].id)
        estados_originais_treino.append(cache["estado"])
        acoes_treino.append(cobra["acao"])
        recompensas_treino.append(cache["recompensa"])
        estados_treino.append(novo_estado)
        mortos_treino.append(cache["morreu"])   
        cobra["recompensa_total"] = cobra.get("recompensa_total", 0) + cache["recompensa"]



        if not cobrasmortas:
            cobra["_estado_cache"] = novo_estado    
    if ids_treino and not avaliacao:
        mandar.treino_lote(
            ids_treino,
            estados_originais_treino,
            acoes_treino,
            recompensas_treino,
            estados_treino,
            mortos_treino
        )
        
        frames_treinados += 1    
        epsilon_atual = max(epsilon_final, epsilon_atual - decaimento_epsilon)
        mandar.set_epsilon(epsilon_atual)

    for cobra in cobrasmortas:
        if cobra not in todasascobras:
            continue
        if avaliacao:
            f.registrar_vida_avaliacao(
                cobra["recompensa_total"]
            )
        else:
            f.registrar_vida(
                cobra["ia"].id,
                cobra["recompensa_total"]
            )

    for cobra in cobrasmortas:
        if cobra not in todasascobras:
            continue
        if respawn:
            f.respawnar(cobra, todasascobras, largura, altura)
        else:
            f.pool_ids.liberar(cobra["ia"].id)
            todasascobras.remove(cobra)

    frames_janela += 1
    if frames_janela >= frames_janela_avaliacao:
        pontuacao_janela = f.pontuacao_contagem()
        print(("AVALIACAO " if avaliacao else "TREINO ") + f.resumo_contagem() + f" epsilon={epsilon_atual:.3f}")
        
        if avaliacao and pontuacao_janela is not None and frames_treinados >= minimo_frames_para_salvar and pontuacao_janela > melhor_pontuacao_conhecida + margem_melhoria:
            
            melhor_pontuacao_conhecida = pontuacao_janela
            mandar.salvar(epsilon_atual)
            
            
            with open("melhor_avaliacao.txt", "w") as arquivo:
                arquivo.write(str(melhor_pontuacao_conhecida))
        f.zerar_contagem()
        frames_janela = 0
        

    if contador_frames % framedesenho == 0:
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
            botaocomida,
            (200, 150, 40),
            (255, 230, 150),
            t["comida"],
            (255, 255, 255),
            fonte_pequena,
            alpha_do_botao(botaocomida, todasascobras)
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
            ativaravaliacao,
            (60, 150, 150) if avaliacao else (90, 90, 90),
            (255, 255, 255),
            t["avaliacao"] + ": " + ("ON" if avaliacao else "OFF"),
            (255, 255, 255),
            fonte,
            alpha_do_botao(ativaravaliacao, todasascobras)
        )
        desenhar_botao(
            episilion,
            (70, 90, 170) if epsilon_manual else (70, 70, 110),
            (180, 190, 255),
            t["epsilon"] + ": " + ("ON" if epsilon_manual else "OFF"),
            (255, 255, 255),
            fonte,
            alpha_do_botao(episilion, todasascobras)
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

            corcobra = cobra["cor"]
            if dados:
                f.ver(cobra, tela, cobra["movimentox"], cobra["movimentoy"])
            if cobra is cobra_destaque:
                for seg in cobra["segmentos"]:
                    pygame.draw.line(tela, (255, 255, 120), (int(seg["inicio"][0]), int(seg["inicio"][1])), (int(seg["fim"][0]), int(seg["fim"][1])), 28)

            if dados:
                a = f.observar(cobra, todasascobras, largura, altura)
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
                tela.blit(texto, (largura/3 + largura / 3,  40 + indice_cobra * 30))

            for seg in cobra["segmentos"]:
                pygame.draw.line(tela, corcobra, (int(seg["inicio"][0]), int(seg["inicio"][1])), (int(seg["fim"][0]), int(seg["fim"][1])), 16)
        for comida in f.comidas:
            pygame.draw.circle(tela, comidacor, (int(comida[0]), int(comida[1])), 5)
        pygame.display.flip()
#nao é necessario, mas, talvez, eu use
    relogio.tick()

mandar.fechar()
pygame.quit()