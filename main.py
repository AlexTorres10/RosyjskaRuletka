import pygame

from display import *
from jogador import *
from jogar_roleta import *
from textos_menu import *
from inputbox import *
import pandas as pd
from os import listdir
from math import ceil
from random import randrange, shuffle, uniform
import random
import sys
import locale
import unicodedata
def remover_acentos(texto):
    return ''.join(
        c for c in unicodedata.normalize('NFD', texto)
        if unicodedata.category(c) != 'Mn'
    )
locale.setlocale(locale.LC_ALL, 'PL.UTF-8')
pygame.init()


def load_sounds():
    dict_sounds = {}
    for som in listdir('sounds'):
        dict_sounds[som[6:-4]] = pygame.mixer.Sound('sounds/' + som)
    return dict_sounds


def limpa_tela(w):
    w.fill('black')
    rr_bg = Image("img/rr_bg.jpg", 0, 0)
    rr_bg.draw(w)


def round_img(round_number, jogadores):
    """
    Animação completa do início do round:
      1. Fecha a cortina sobre a tela atual
      2. Troca a parte de baixo pela imagem do round atual
      3. Abre a cortina revelando o jogo
    
    Parâmetros:
      - round_number: int, usado para carregar "round_{n}.png"
      - jogadores: passado para blit_all()
    """
    clock = pygame.time.Clock()

    # 1. Cortina inicial com conteúdo genérico (ex: "FIRST")
    if round_number == 0:
        curtain = Curtain("img/intro_up.png", "img/intro_down.png")
    elif round_number < 5:
        curtain = Curtain("img/round.png", f"img/round_{round_number}.png")
    else:
        curtain = Curtain("img/final.png", "img/round_5.png")
    curtain.top_y = curtain.target_closed_top_y
    curtain.bot_y = curtain.target_closed_bot_y
    curtain.state = 'idle'

    delay = 2500
    start = pygame.time.get_ticks()
    while pygame.time.get_ticks() - start < delay:
        blit_all(sair_do_jogo, essentials, jogadores)
        curtain.draw(window)
        pygame.display.flip()
        clock.tick(60)


    # 3. Animação de abertura
    curtain.open()
    while curtain.state != 'idle':
        dt = clock.tick(60) / 1000.0
        blit_all(sair_do_jogo, essentials, jogadores)
        curtain.update(dt)
        curtain.draw(window)
        pygame.display.flip()


def comeco_jogo():
    global window
    fr = ['Jeśli zapadnia się nie ','otworzy zostajecie w grze,', 'ale jeśli się otworzy ','tracicie grunt pod stopami!']
    for i in range(len(fr)):
        frase = Texto(fr[i], 'FreeSansBold',
                      60, 1360, 700 + 80 * i)
        frase.show_texto(window, align='center')


def jogar_roleta(modo, alav, chances_de_cair=0, jogador_em_risco=Jogador('Zé', 1, 0), jogadores=[]):
    global sair_do_jogo, essentials, window, sounds
    blit_all(sair_do_jogo, essentials, jogadores)
    pygame.display.update()
    

    if modo == 'normal':
        comeca = jogador_em_risco.pos
        if chances_de_cair == 1:
            vermelhos = [0]
        elif chances_de_cair == 2:
            vermelhos = [0, 3]
        elif chances_de_cair == 3:
            vermelhos = [0, 2, 4]
        elif chances_de_cair == 4:
            vermelhos = [0, 2, 3, 4]

        vermelhos = [(v + comeca) % 6 for v in vermelhos]
        roleta.update_image(f'img/roleta_play_{str(jogador_em_risco.pos)}.png')
        sounds['mex_open'].play(0)

        for i in range(13):
            blit_all(sair_do_jogo, essentials, jogadores)
            alav.update_image('img/alavanca1-' + str(i) + '.png')
            pygame.display.update()
        i = 1
        space = False
        if jogador_em_risco.tipo == 0:
            while not space:
                blit_vermelho(sair_do_jogo, essentials, jogadores, vermelhos)
                vermelhos = [(v + 1) % 6 for v in vermelhos]

                pygame.display.update()
                ms_delay = int(1000 // i)
                ms_delay = 100 if ms_delay < 100 else ms_delay
                pygame.time.delay(ms_delay)
                i+=1
                for events in pygame.event.get():
                    if events.type == pygame.QUIT:
                        space = True
                    if events.type == pygame.KEYDOWN:
                        if events.key == pygame.K_SPACE:
                            return para_roleta('normal', alav, vermelhos=vermelhos, jogador_em_risco=jogador_em_risco,
                                               jogadores=jogadores)
                    if events.type == pygame.MOUSEBUTTONDOWN and events.button == 1:
                        if alav.check_click():
                            return para_roleta('normal', alav, vermelhos=vermelhos, jogador_em_risco=jogador_em_risco,
                                               jogadores=jogadores)
        else:
            jogando_roleta = uniform(4, 12)
            start = pygame.time.get_ticks()
            while not space:
                segundos = (pygame.time.get_ticks() - start) / 1000
                blit_vermelho(sair_do_jogo, essentials, jogadores, vermelhos)
                vermelhos = [(v + 1) % 6 for v in vermelhos]
                pygame.display.update()
                ms_delay = int(1000 // i)
                ms_delay = 100 if ms_delay < 100 else ms_delay
                pygame.time.delay(ms_delay)
                i+=1
                if segundos > jogando_roleta:
                    return para_roleta('normal', alav, vermelhos=vermelhos, jogador_em_risco=jogador_em_risco,
                                       jogadores=jogadores)
    elif modo == 'carrasco':
        em_risco = get_em_risco(jogadores)
        pos_risco = randrange(len(em_risco))
        vermelho = randrange(6)
        space = False
        roleta.update_image('img/roleta_play.png')
        for i in range(13):
            blit_all(sair_do_jogo, essentials, jogadores)
            alav.update_image('img/alavanca1-' + str(i) + '.png')
            pygame.display.update()

        i = 1
        sounds['mex_open'].play(0)
        lider = get_leader(jogadores)
        if (lider is not None and lider.tipo == 0):
            # Se temos um líder e ele é humano OU não temos líder, joga a roleta.
            while not space:
                vermelho = (vermelho + 1) % 6  # São 6 buracos
                blit_vermelho(sair_do_jogo, essentials, jogadores, [vermelho])
                pygame.display.update()
                pos_risco = (pos_risco + 1) % len(em_risco)  # Enquanto a roleta joga normal, internamente escolhe 1
                ms_delay = int(1000 // i)
                ms_delay = 100 if ms_delay < 100 else ms_delay
                pygame.time.delay(ms_delay)
                i+=1
                for events in pygame.event.get():
                    if events.type == pygame.QUIT:
                        space = True
                    if events.type == pygame.KEYDOWN:
                        if events.key == pygame.K_SPACE:
                            roleta_verdadeira = em_risco[pos_risco]
                            return para_roleta('carrasco', alav, eliminado=roleta_verdadeira, vermelhos=[vermelho], jogadores=jogadores)
                    if events.type == pygame.MOUSEBUTTONDOWN and events.button == 1:
                        if alav.check_click():
                            roleta_verdadeira = em_risco[pos_risco]
                            return para_roleta('carrasco', alav, eliminado=roleta_verdadeira, vermelhos=[vermelho], jogadores=jogadores)
        else:
            jogando_roleta = uniform(4, 12)
            start = pygame.time.get_ticks()
            while not space:
                segundos = (pygame.time.get_ticks() - start) / 1000
                vermelho = (vermelho + 1) % 6  # São 6 buracos
                blit_vermelho(sair_do_jogo, essentials, jogadores, [vermelho])
                pygame.display.update()
                pos_risco = (pos_risco + 1) % len(em_risco)  # Enquanto a roleta joga normal, internamente escolhe 1
                ms_delay = int(1000 // i)
                ms_delay = 100 if ms_delay < 100 else ms_delay
                pygame.time.delay(ms_delay)
                i+=1
                if segundos > jogando_roleta:
                    roleta_verdadeira = em_risco[pos_risco]
                    return para_roleta('carrasco', alav, eliminado=roleta_verdadeira, vermelhos=[vermelho], jogadores=jogadores)
    elif modo == 'comeco':
        roleta.update_image('img/roleta_0.png')
        candidatos = get_em_risco(jogadores)  # Não estão bem em risco, só de fazer a primeira pergunta

        pos_azul = randrange(len(candidatos))
        space = False
        for i in range(13):
            blit_all(sair_do_jogo, essentials, jogadores)
            alav.update_image('img/alavanca1-' + str(i) + '.png')
            pygame.display.update()

        jogando_roleta = uniform(4, 10)
        start = pygame.time.get_ticks()
        comeca = randrange(6)
        i = 1
        sounds['mex_open'].play(0)
        while not space:
            pos_azul = (pos_azul + 1) % len(candidatos)
            segundos = (pygame.time.get_ticks() - start) / 1000
            
            blit_azul(sair_do_jogo, essentials, jogadores, comeca)
            comeca = (comeca + 1) % 6  # São 6 buracos
            ms_delay = int(1000 // i)
            ms_delay = 100 if ms_delay < 100 else ms_delay
            pygame.time.delay(ms_delay)
            i+=1
            for events in pygame.event.get():
                if events.type == pygame.QUIT:
                    space = True
                if events.type == pygame.KEYDOWN:
                    if events.key == pygame.K_SPACE:
                        pygame.mixer.stop()
                        roleta_verdadeira = candidatos[pos_azul]
                        return para_roleta('comeco', alav,
                                           jog_comeca=roleta_verdadeira, vermelhos=[comeca], jogadores=jogadores)
                if events.type == pygame.MOUSEBUTTONDOWN and events.button == 1:
                    if alav.check_click():
                        pygame.mixer.stop()
                        roleta_verdadeira = candidatos[pos_azul]
                        return para_roleta('comeco', alav,
                                           jog_comeca=roleta_verdadeira, vermelhos=[comeca], jogadores=jogadores)
            if todos_bots(jogadores) and (segundos > jogando_roleta):
                roleta_verdadeira = candidatos[pos_azul]
                return para_roleta('comeco', alav,
                                   jog_comeca=roleta_verdadeira, vermelhos=[comeca], jogadores=jogadores)
    elif modo == 'final':
        comeca = randrange(6)
        if chances_de_cair == 3:
            vermelhos = [0, 2, 4]
        elif chances_de_cair == 4:
            vermelhos = [0, 2, 3, 4]
        elif chances_de_cair == 5:
            vermelhos = [0, 1, 2, 3, 4]

        vermelhos = [(v + comeca) % 6 for v in vermelhos]
        roleta.update_image(f'img/roleta_0.png')
        sounds['mex_open'].play(0)

        for i in range(13):
            blit_all(sair_do_jogo, essentials, jogadores)
            alav.update_image('img/alavanca1-' + str(i) + '.png')
            pygame.display.update()
        i = 1
        space = False
        if jogador_em_risco.tipo == 0:
            while not space:
                blit_vermelho(sair_do_jogo, essentials, jogadores, vermelhos)
                vermelhos = [(v + 1) % 6 for v in vermelhos]

                pygame.display.update()
                ms_delay = int(1000 // i)
                ms_delay = 100 if ms_delay < 100 else ms_delay
                pygame.time.delay(ms_delay)
                i+=1
                for events in pygame.event.get():
                    if events.type == pygame.QUIT:
                        space = True
                    if events.type == pygame.KEYDOWN:
                        if events.key == pygame.K_SPACE:
                            
                            for i in range(12, -1, -1):
                                blit_vermelho(sair_do_jogo, essentials, jogadores, range(6))
                                alav.update_image('img/alavanca1-' + str(i) + '.png')
                                pygame.display.update()
                            blit_vermelho(sair_do_jogo, essentials, jogadores, range(6))
                            pygame.display.update()
                            todos = list(range(6))
                            todos.remove(vermelhos[0])  # remove a posição já ocupada
                            buracos = random.sample(todos, chances_de_cair - 1)
                            buracos.append(vermelhos[0])
                            pygame.mixer.stop()
                            sounds['mex_close_slow_heartbeat'].play()
                            return buracos
                    if events.type == pygame.MOUSEBUTTONDOWN and events.button == 1:
                        if alav.check_click():
                            
                            for i in range(12, -1, -1):
                                blit_vermelho(sair_do_jogo, essentials, jogadores, range(6))
                                alav.update_image('img/alavanca1-' + str(i) + '.png')
                                pygame.display.update()
                            blit_vermelho(sair_do_jogo, essentials, jogadores, range(6))
                            pygame.display.update()
                            todos = list(range(6))
                            todos.remove(vermelhos[0])  # remove a posição já ocupada
                            buracos = random.sample(todos, chances_de_cair - 1)
                            buracos.append(vermelhos[0])
                            pygame.mixer.stop()
                            sounds['mex_close_slow_heartbeat'].play()
                            return buracos
        else:
            jogando_roleta = uniform(4, 12)
            start = pygame.time.get_ticks()
            while not space:
                segundos = (pygame.time.get_ticks() - start) / 1000
                blit_vermelho(sair_do_jogo, essentials, jogadores, vermelhos)
                vermelhos = [(v + 1) % 6 for v in vermelhos]
                pygame.display.update()
                ms_delay = int(1000 // i)
                ms_delay = 100 if ms_delay < 100 else ms_delay
                pygame.time.delay(ms_delay)
                i+=1
                if segundos > jogando_roleta:
                    for i in range(12, -1, -1):
                        blit_vermelho(sair_do_jogo, essentials, jogadores, range(6))
                        alav.update_image('img/alavanca1-' + str(i) + '.png')
                        pygame.display.update()
                    todos = list(range(6))
                    todos.remove(vermelhos[0])  # remove a posição já ocupada
                    buracos = random.sample(todos, chances_de_cair - 1)
                    buracos.append(vermelhos[0])
                    pygame.mixer.stop()
                    sounds['mex_close_slow_heartbeat'].play()
                    return buracos


def para_roleta(modo, alav, eliminado=Jogador('Zé', 1, 0), vermelhos=[0], jogador_em_risco=Jogador('Zé', 1, 0),
                jog_comeca=Jogador('Zé', 1, 0), jogadores=[]):
    global window, essentials, sair_do_jogo, sounds
    blit_all(sair_do_jogo, essentials, jogadores)
    min_delay, max_delay = 100.0, 1000.0
    total_duration = 10500.0
      # milissegundos
    if modo == 'normal':
        for i in range(12, -1, -1):
            blit_vermelho(sair_do_jogo, essentials, jogadores, vermelhos)
            alav.update_image('img/alavanca1-' + str(i) + '.png')
            pygame.display.update()
        sounds['mex_open'].stop()
        sound_options = [
            sounds['mex_close_slow_heartbeat'],
            sounds['mex_close_fast_heartbeat']
        ]

        random.choice(sound_options).play()
        passos = randint(10, 18)
        pygame.event.clear()

        # 2. Gerar N delays crescentes linearmente
        raw_delays = [
            min_delay + (max_delay - min_delay) * (i / (passos - 1))
            for i in range(passos)
        ]

        # 3. Normalizar para que somem exatamente 11000 ms
        scale = total_duration / sum(raw_delays)
        delays = [d * scale for d in raw_delays]

        for d in delays:
            vermelhos = [(v + 1) % 6 for v in vermelhos]
            blit_vermelho(sair_do_jogo, essentials, jogadores, vermelhos)
            pygame.time.delay(int(d))
        pygame.time.delay(200)
        if jogador_em_risco.pos in vermelhos:
            sounds['fall_1'].play(0)
            jogador_em_risco.eliminar(jogadores)
            blit_queda(sair_do_jogo, essentials, jogadores, vermelhos, jogador_em_risco)
            return True
        else:
            sounds['save'].play()
            pygame.time.delay(1000)
            
            return False
    elif modo == 'carrasco':
        loc_vermelho = vermelhos[0]
        for i in range(12, -1, -1):
            blit_vermelho(sair_do_jogo, essentials, jogadores, [loc_vermelho])
            alav.update_image('img/alavanca1-' + str(i) + '.png')
            pygame.display.update()
        sounds['mex_open'].stop()
        sound_options = [
            sounds['mex_close_slow_heartbeat'],
            sounds['mex_close_fast_heartbeat']
        ]

        random.choice(sound_options).play()
        passos = randint(10, 18)
        pygame.event.clear()

        offset = (eliminado.pos - loc_vermelho) % 6
        # adiciona múltiplos de 6 (voltas completas)
        N = offset + 12

        # 2. Gerar N delays crescentes linearmente
        raw_delays = [
            min_delay + (max_delay - min_delay) * (i / (N - 1))
            for i in range(N)
        ]
        scale = total_duration / sum(raw_delays)
        delays = [d * scale for d in raw_delays]

        for d in delays:
            loc_vermelho = (loc_vermelho + 1) % 6
            blit_vermelho(sair_do_jogo, essentials, jogadores, [loc_vermelho])
            pygame.time.delay(int(d))
        

        while loc_vermelho != eliminado.pos:
            loc_vermelho = (loc_vermelho + 1) % 6
            blit_vermelho(sair_do_jogo, essentials, jogadores, [loc_vermelho])
            pygame.time.delay(1000)
        sounds['fall_1'].play(0)
        eliminado.eliminar(jogadores)
        blit_queda(sair_do_jogo, essentials, jogadores, [loc_vermelho], eliminado)
        return eliminado
    elif modo == 'comeco':
        total_duration = 11500.0
        pygame.mixer.stop()
        for i in range(12, -1, -1):
            blit_all(sair_do_jogo, essentials, jogadores)
            alav.update_image('img/alavanca1-' + str(i) + '.png')
            pygame.display.update()
        sounds['mex_close_with_bg'].play()
        comeca = vermelhos[0]
        
        offset = (jog_comeca.pos - comeca) % 6
        # adiciona múltiplos de 6 (voltas completas)
        voltas = randint(1, 2)  # pode ajustar: 2 a 3 voltas
        N = offset + 6 * voltas  # total de passos

        # 2. Gerar N delays crescentes linearmente
        raw_delays = [
            min_delay + (max_delay - min_delay) * (i / (N - 1))
            for i in range(N)
        ]

        # 3. Normalizar para que somem exatamente 11000 ms
        scale = total_duration / sum(raw_delays)
        delays = [d * scale for d in raw_delays]

        
        blit_azul(sair_do_jogo, essentials, jogadores, comeca)
        # 4. Rodar a roleta pelos N passos e parar exatamente no jog_comeca.pos
        for d in delays:
            comeca = (comeca + 1) % 6
            blit_azul(sair_do_jogo, essentials, jogadores, comeca)
            pygame.time.delay(int(d))

        while comeca != jog_comeca.pos:
            comeca = (comeca + 1) % 6
            blit_azul(sair_do_jogo, essentials, jogadores, comeca)
            pygame.time.delay(1200)
            
        return jog_comeca


def blit_all(s, ess, jogadores):
    global window
    window.fill('black')
    s.show_texto(window)
    mostra_essentials(window, ess)
    mostra_jogadores(window, jogadores)


def blit_vermelho(s, ess, jogadores, vermelhos, texto_final=''):
    global window
    window.fill('black')
    s.show_texto(window)
    mostra_essentials(window, ess)
    bota_vermelho(window, vermelhos)
    mostra_jogadores(window, jogadores)
    if texto_final:
        blit_texto_final(
            texto_final,
            tam_fonte=36
        )
    pygame.display.update()


def blit_azul(s, ess, jogadores, a):
    global window
    window.fill('black')
    s.show_texto(window)
    mostra_essentials(window, ess)
    bota_azul(window, a)
    mostra_jogadores(window, jogadores)
    pygame.display.update()


def blit_queda(s, ess, jogadores, vermelhos, jogador, final=False, pre_final=False):
    global window
    window.fill('black')
    s.show_texto(window)
    mostra_essentials(window, ess)
    if not final and not pre_final:
        queda(window, vermelhos, jogador.pos)
    elif not final and pre_final:
        blit_all(s, ess, jogadores)
        for dropzone in [1, 3, 5]:
            pygame.mixer.stop()
            queda(window, vermelhos, dropzone, c='rodada4')
            sounds['open_hole'].play()
            pygame.time.delay(300)
    else:
        vetor_vermelhos = []
        if jogador.pos in vermelhos:
            vermelhos.remove(jogador.pos)
            vermelhos.append(jogador.pos)
        blit_vermelho(sair_do_jogo, essentials, jogadores, range(6))
        for v in vermelhos[:-1]:
            vetor_vermelhos.append(v)
            blit_varios_buracos(vetor_vermelhos, c='caiu')
            sounds['open_hole'].play()
            pygame.time.delay(500)

        if jogador.pos in vermelhos:
            jogador.eliminar(jogadores, rodada=5)
            vetor_vermelhos.append(vermelhos[-1])
            blit_varios_buracos(vetor_vermelhos, c='caiu', vermelhos=range(6), s=sair_do_jogo, ess=essentials, jogadores=jogadores)
            sounds['fall_1'].play()
            pygame.time.delay(8000)
        else:
            vetor_vermelhos.append(vermelhos[-1])
            blit_varios_buracos(vetor_vermelhos, c='caiu')
            sounds['open_hole'].play()
            pygame.time.delay(1000)
            sounds['save'].play()
            pygame.time.delay(4000)
            
    mostra_jogadores(window, jogadores)
    pygame.display.update()


def blit_varios_buracos(list_buracos, c='caiu', vermelhos=None, s=None, ess=None, jogadores=None):
    global window
    if vermelhos:
        window.fill('black')
        s.show_texto(window)
        bota_vermelho(window, vermelhos)
        mostra_essentials(window, ess)
        bota_vermelho(window, vermelhos)
        mostra_jogadores(window, jogadores)
    for b in list_buracos:
        if c == 'caiu':
            window.blit(caiu, pos_buracos[b])
        else:
            window.blit(buraco, pos_buracos[b])
    pygame.display.update()


def blit_pergunta(perg, final_valor=False):
    global window
    global img_pergunta

    img_pergunta.draw(window)

    words = perg.split(' ')
    pergunta_split = []
    current_line = ''
    tam_fonte = 48

    if final_valor:
        pergunta_split.append('PYTANIE ZA '+str(final_valor)+' ZŁ')

    for word in words:
        test_line = f"{current_line} {word}".strip()
        line_width, _ = pygame.font.Font('fonts/Varela.ttf', int(tam_fonte)).size(test_line)
        if line_width <= 680:
            current_line = test_line
        else:
            # atualiza lista de linhas e começa nova com a palavra
            pergunta_split.append(current_line)
            current_line = word

    # não esquecer de adicionar a última linha
    
    if current_line:
        pergunta_split.append(current_line)

    for p, i in zip(pergunta_split, range(len(pergunta_split))):
        if 'PYTANIE' in p:
            pergunta = Texto(p, 'FreeSansBold', tam_fonte, 1214, 60 + 65 * i)
        else:
            pergunta = Texto(p, 'Varela', tam_fonte, 1214, 60 + 65 * i)
        pergunta.show_texto(window, 'topleft')


def blit_texto_final(texto_final, tam_fonte):
    global window

    words = texto_final.split(' ')
    texto_split = []
    current_line = ''

    for word in words:
        test_line = f"{current_line} {word}".strip()
        line_width, _ = pygame.font.Font('fonts/FreeSans.ttf', int(tam_fonte)).size(test_line)
        if line_width <= 720:
            current_line = test_line
        else:
            # atualiza lista de linhas e começa nova com a palavra
            texto_split.append(current_line)
            current_line = word

    # não esquecer de adicionar a última linha
    if current_line:
        texto_split.append(current_line)

    for p, i in zip(texto_split, range(len(texto_split))):
        pergunta = Texto(p, 'FreeSans', tam_fonte, 1060, 60 + 70 * i)
        pergunta.show_texto(window, 'topleft')


def blit_alternativas(perg, alternativas, final_valor=False):
    global window
    global img_pergunta
    img_pergunta.draw(window)
    blit_pergunta(perg, final_valor)
    for a, i in zip(alternativas, range(len(alternativas))):
        Image('img/option.png', 1245, 480 + 107 * i).draw(window)
        alternativa = Texto(a, 'Varela', 36, 1315, 486 + 107 * i)
        alternativa.show_texto(window, 'topleft')


def blit_resposta_escolhida(perg, alternativas, escolhida, final_valor=False):
    global window
    global img_pergunta
    img_pergunta.draw(window)
    blit_pergunta(perg, final_valor)
    for a, i in zip(alternativas, range(len(alternativas))):
        if a == escolhida:
            Image('img/chosen_answer.png', 1222, 464 + 107 * i).draw(window)
        Image('img/option.png', 1245, 480 + 107 * i).draw(window)
        alternativa = Texto(a, 'Varela', 36, 1315, 486 + 107 * i)
        alternativa.show_texto(window, 'topleft')


def blit_certo_errado(perg, alternativas, escolhida, resposta_certa, final_valor=False):
    global window
    global img_pergunta
    blit_pergunta(perg, final_valor)
    for a, i in zip(alternativas, range(len(alternativas))):
        if (a == escolhida) and (a == resposta_certa):
            Image('img/right_answer.png', 1222, 464 + 107 * i).draw(window)
        elif a == escolhida:
            Image('img/wrong_answer.png', 1222, 464 + 107 * i).draw(window)
        elif a == resposta_certa:
            Image('img/right_answer.png', 1222, 464 + 107 * i).draw(window)
        Image('img/option.png', 1245, 480 + 107 * i).draw(window)
        alternativa = Texto(a, 'Varela', 36, 1315, 486 + 107 * i)
        alternativa.show_texto(window, 'topleft')


def blit_errado(perg, alternativas, escolhida, final_valor=False):
    global window
    global img_pergunta
    blit_pergunta(perg, final_valor)
    for a, i in zip(alternativas, range(len(alternativas))):
        if a == escolhida:
            Image('img/wrong_answer.png', 1222, 464 + 107 * i).draw(window)
        Image('img/option.png', 1245, 480 + 107 * i).draw(window)
        alternativa = Texto(a, 'Varela', 36, 1315, 486 + 107 * i)
        alternativa.show_texto(window, 'topleft')


def distribute_money(jogadores, dinheiro, ess, pergunta=None, eliminado=None):
    global window
    global sair_do_jogo
    global sounds
    sounds['money'].play()
    qtd_fatias = 5
    for _ in range(qtd_fatias):
        for pl in jogadores:
            if not pl.eliminado:
                pl.dinheiro += (dinheiro // qtd_fatias)
        if eliminado:
            blit_queda(sair_do_jogo, ess, jogadores, [eliminado.pos], eliminado)
        else:
            blit_all(sair_do_jogo, ess, jogadores)
        if pergunta:
            blit_pergunta(pergunta)
        pygame.time.delay(200)
        pygame.display.update()


def seleciona_pergunta(rodada):
    global df_perguntas
    df = df_perguntas.copy()
    df = df[~df['used']]  # Pegando somente as perguntas que não foram feitas

    if df[df['round'] == 3].shape[0] == 0 or \
            df[df['round'] == 1].shape[0] == 0 or \
            df[df['round'] == 2].shape[0] == 0 or \
            df[df['round'] == 4].shape[0] == 0 or \
            df[df['round'] == 5].shape[0] == 0:
        df_perguntas['used'] = False  # Se não houver mais perguntas a serem selecionadas, reinicia a base.
        df = df_perguntas.copy()
        df = df[~df['used']]

    if rodada <= 4:
        df = df[df['round'] == rodada]
        list_index = df.index.to_list()
        pos_pergunta = random.choice(list_index)
        df_aux = df.loc[pos_pergunta]
        pergunta = df_aux['question']
        alternativas = [df_aux['right'], df_aux['alt1'], df_aux['alt2'], df_aux['alt3'], df_aux['alt4']]
        alternativas = [alt for alt in alternativas if alt != '-']
        emb = str(df_aux['shuffle'])
        if emb.isdigit():
            alt_aux = alternativas.copy()
            for option, i in zip(emb, range(len(alternativas))):
                option = int(option)
                alternativas[i] = alt_aux[option - 1]
        else:
            shuffle(alternativas)
        df_perguntas.loc[df_perguntas['question'] == pergunta, 'used'] = True
        return pergunta, alternativas, df_aux['right']
    else:  # Estamos na rodada final
        
        df = df[df['round'] == 5]
        list_index = df.index.to_list()
        pos_pergunta = random.choice(list_index)
        df_aux = df.loc[pos_pergunta]
        pergunta = df_aux['question']
        alternativas_originais = [
            df_aux['right'],
            df_aux['alt1'],
            df_aux['alt2'],
            df_aux['alt3'],
            df_aux['alt4']
        ]

        # Gera variações para cada uma
        alternativas = set()
        for alt in alternativas_originais:
            if not isinstance(alt, str):
                continue
            alt = alt.strip()
            alternativas.add(alt)
            alternativas.add(alt.lower())
            alternativas.add(remover_acentos(alt))
            alternativas.add(remover_acentos(alt.lower()))
        
        df_perguntas.loc[df_perguntas['question'] == pergunta, 'used'] = True
        return pergunta, alternativas, df_aux['right']


def wait_until_enter(segundos, mus=''):
    global sair_do_jogo
    loop_jogo = True
    start = pygame.time.get_ticks()
    pygame.event.clear()
    while loop_jogo:
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                pygame.quit()
            if ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
                if sair_do_jogo.check_click():
                    pygame.mixer.stop()
                    menu_principal()
            if ev.type == pygame.KEYDOWN:
                if ev.key == pygame.K_RETURN:
                    loop_jogo = False
                if ev.key == pygame.K_F1:
                    segundos = segundos * 10
                if ev.key == pygame.K_F2:
                    if mus != '':
                        pygame.mixer.stop()
                        sounds[mus].play()
                if ev.key == pygame.K_F3:
                    pygame.mixer.stop()
                if ev.key == pygame.K_F4:
                    pygame.mixer.stop()
                    sounds['final_inicio'].play()
                if ev.key == pygame.K_p:
                    loop_pause = True
                    while loop_pause:
                        frase = Texto('JOGO PAUSADO', 'Varela', 72, 960, 760, cor=(255, 0, 0))
                        frase.show_texto_cor(window, align='center', color=(0, 0, 0))
                        pygame.display.update()
                        for ev in pygame.event.get():
                            if ev.type == pygame.KEYDOWN:
                                if ev.key == pygame.K_p:
                                    loop_pause = False
        time = pygame.time.get_ticks() - start
        if time > (segundos * 1000):
            loop_jogo = False


def get_pulso(pulso_anterior):
    dif_anterior = randint(-2, 2)
    return pulso_anterior + dif_anterior


def todos_bots(jogadores):
    for pl in jogadores:
        if pl.tipo == 0 and not pl.eliminado:
            return False
    return True


def mostrar_frases(frases, x_inicial=960,y_inicial=820, tam=72, enter=80, fonte='FreeSans'):
    for i, frase in enumerate(frases):
        Texto(frase, fonte, tam, x_inicial, y_inicial + enter * i).show_texto(window, align='center')
    pygame.display.update()


def mostrar_frases_controlado(frase, x_inicial=1465,y_inicial=60, tam_fonte=72, enter=80, fonte='FreeSansBold'):

    words = frase.split(' ')
    pergunta_split = []
    current_line = ''
    for word in words:
        test_line = f"{current_line} {word}".strip()
        line_width, _ = pygame.font.Font('fonts/'+fonte+'.ttf', int(tam_fonte)).size(test_line)
        if line_width <= 750:
            current_line = test_line
        else:
            # atualiza lista de linhas e começa nova com a palavra
            pergunta_split.append(current_line)
            current_line = word

    # não esquecer de adicionar a última linha
    if current_line:
        pergunta_split.append(current_line)

    for p, i in zip(pergunta_split, range(len(pergunta_split))):
        pergunta = Texto(p, fonte, tam_fonte, x_inicial, y_inicial + enter * i)
        pergunta.show_texto(window, 'center')
    pygame.display.update()


def iniciar_jogo():
    global window, essentials, sair_do_jogo, df_perguntas, img_pergunta, sounds
    for som in sounds.keys():
        sounds[som].stop()
    window.fill('black')
    df_jogadores = pd.read_json("players.json")
    jogadores = []
    zonas_de_risco = [[3], [0, 3], [3, 1, 5], [4, 0, 1, 2], [0, 1, 2, 3, 4]]
    dinheiro_rodada = [300, 600, 1000, 1500, 5000]
    qtd_alternativas = [2, 3, 4, 5]
    num_perguntas = [8, 7, 6, 5]

    blit_all(sair_do_jogo, essentials, jogadores)
    sounds['intro'].set_volume(vol + 0.3)
    sounds['before_mex_open'].set_volume(0.1)
    sounds['intro'].play()

    round_img(0, jogadores)

    # Flag para controle
    pular_intro = False

    # Primeiro ciclo de vermelho
    for i in range(12):
        for ev in pygame.event.get():
            if ev.type == pygame.KEYDOWN and ev.key == pygame.K_RETURN:
                pular_intro = True
            elif ev.type == pygame.QUIT:
                pygame.quit()
                exit()
        if pular_intro:
            break
        roleta.update_image(f'img/roleta_play_{str(i % 6)}.png')
        blit_vermelho(sair_do_jogo, essentials, jogadores, [i % 6])
        pygame.display.update()
        pygame.time.delay(250)

    # Segundo ciclo de azul
    if not pular_intro:
        for i in range(12):
            for ev in pygame.event.get():
                if ev.type == pygame.KEYDOWN and ev.key == pygame.K_RETURN:
                    pular_intro = True
                elif ev.type == pygame.QUIT:
                    pygame.quit()
                    exit()
            if pular_intro:
                break
            roleta.update_image(f'img/roleta_0.png')
            blit_azul(sair_do_jogo, essentials, jogadores, i % 6)
            pygame.display.update()
            pygame.time.delay(250)

    # Terceiro ciclo de vermelho
    if not pular_intro:
        for i in range(12):
            for ev in pygame.event.get():
                if ev.type == pygame.KEYDOWN and ev.key == pygame.K_RETURN:
                    pular_intro = True
                elif ev.type == pygame.QUIT:
                    pygame.quit()
                    exit()
            if pular_intro:
                break
            roleta.update_image(f'img/roleta_play.png')
            blit_vermelho(sair_do_jogo, essentials, jogadores, [i % 6])
            pygame.display.update()
            pygame.time.delay(250)
    # Ciclo para queda
    if not pular_intro:
        for i in range(4):
            for ev in pygame.event.get():
                if ev.type == pygame.KEYDOWN and ev.key == pygame.K_RETURN:
                    pular_intro = True
                elif ev.type == pygame.QUIT:
                    pygame.quit()
                    exit()
            if pular_intro:
                break
            roleta.update_image(f'img/roleta_play.png')
            blit_vermelho(sair_do_jogo, essentials, jogadores, range(6))
            pygame.display.update()
            pygame.time.delay(250)

    if not pular_intro:
        pos_aleatorios = random.sample(range(1, 6), 2)
        for p in pos_aleatorios:
            roleta.update_image(f'img/roleta_play_{str(p)}.png')
            blit_queda(sair_do_jogo, essentials, jogadores, range(6), Jogador('Zé', p, 0))
            pygame.display.update()
            start = pygame.time.get_ticks()
            while (pygame.time.get_ticks() - start) < 2000:  # 2 segundos = 2000 ms
                for ev in pygame.event.get():
                    if ev.type == pygame.KEYDOWN and ev.key == pygame.K_RETURN:
                        pular_intro = True
                        break
                    elif ev.type == pygame.QUIT:
                        pygame.quit()
                        exit()
                if pular_intro:
                    break
            if pular_intro:
                break

    # Logo final
    if not pular_intro:
        roleta_logo.draw(window)
        pygame.display.update()
        start = pygame.time.get_ticks()
        while (pygame.time.get_ticks() - start) < 12500:
            for ev in pygame.event.get():
                if ev.type == pygame.KEYDOWN and ev.key == pygame.K_RETURN:
                    pular_intro = True
                elif ev.type == pygame.QUIT:
                    pygame.quit()
                    exit()
            if pular_intro:
                break

    if pular_intro:
        sounds['intro'].stop()

    roleta.update_image('img/roleta.png')
    blit_all(sair_do_jogo, essentials, jogadores)
    sounds['aplausos1'].play()
    if not pular_intro:
        pygame.display.update()
        wait_until_enter(4)

    for n, i, tipo in zip(df_jogadores['nome'], range(1, 6), df_jogadores['tipo']):
        jogadores.append(Jogador(n, i, tipo))

    
    round_img(1, jogadores)
    
    roleta.update_image('img/roleta.png')
    img_dados.update_image('img/jogadores.png')
    blit_all(sair_do_jogo, essentials, jogadores)
    # blit_vermelho(sair_do_jogo, essentials, jogadores, range(0, 6))
    pygame.display.update()
    wait_until_enter(2)
    blit_all(sair_do_jogo, essentials, jogadores)

    comeco_jogo()
    pygame.display.update()
    wait_until_enter(5)

    blit_all(sair_do_jogo, essentials, jogadores)
    pygame.mixer.stop()
    sounds['open_hole'].play()
    assim_o(window, texto='')
    wait_until_enter(3)

    blit_all(sair_do_jogo, essentials, jogadores)
    pygame.display.update()


    roleta.update_image('img/roleta.png')
    pygame.display.update()
    nao_respondeu_nunca = [pl for pl in jogadores if not pl.eliminado]
    # RODADAS ELIMINATÓRIAS
    for rodada in range(1, 5):
        if rodada > 1:
            sounds['open_round'].play(0)
            round_img(rodada, jogadores)
        blit_all(sair_do_jogo, essentials, jogadores)
        pygame.display.update()

        # Primeiro, veremos quem é líder
        lider = get_leader(jogadores)
        if lider is None:
            # Se não há líder, jogamos a roleta para ver quem começa.
            
            roleta.update_image('img/roleta.png')
            blit_all(sair_do_jogo, essentials, jogadores)
            if rodada > 1 and rodada < 4:
                mostrar_frases(['Mamy remis na prowadzeniu!', 
                              'Dlatego musimy zakręcić ruletą, ',
                              'aby zdecydować, kto zacznie','rundę wyzwania!'],
                              x_inicial=1400, y_inicial=700, tam=60, enter=80, fonte='FreeSansBold')

            if rodada == 4:
                # Não tem líder, mas temos que começar com quem tem mais dinheiro
                desafiante = None
                dinheiro_lider = -1
                for pl in jogadores:
                    if not pl.eliminado:
                        if pl.dinheiro > dinheiro_lider:
                            dinheiro_lider = pl.dinheiro
                            desafiante = pl
            elif todos_bots(jogadores):
                wait_until_enter(5)
                desafiante = jogar_roleta('comeco', alavanca, jogadores=jogadores)
            else:
                loop = True
                while loop:
                    for ev in pygame.event.get():
                        if ev.type == pygame.QUIT:
                            pygame.quit()
                        if ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
                            if sair_do_jogo.check_click():
                                pygame.mixer.stop()
                                return
                            if alavanca.check_click():
                                desafiante = jogar_roleta('comeco', alavanca, jogadores=jogadores)
                                loop = False
                        if ev.type == pygame.KEYDOWN:
                            if ev.key == pygame.K_SPACE:
                                desafiante = jogar_roleta('comeco', alavanca, jogadores=jogadores)
                                loop = False
            
        else:
            desafiante = lider
        
        roleta.update_image('img/roleta.png')
        
        for som in sounds.keys():
            sounds[som].stop()
        
        sounds['before_mex_open'].play(loops=5)
        blit_vermelho(sair_do_jogo, essentials, jogadores, zonas_de_risco[rodada-1])

        valor = str(locale.currency(dinheiro_rodada[rodada - 1],  grouping=True))
        alternativas = str(qtd_alternativas[rodada - 1])

        if rodada == 1:
            frase_dist = ['Poprawna odpowiedź jest warta ' + valor + ', ',
                        'będziemy mieć ' + alternativas + ' opcje odpowiedzi i',
                        'e ' + str(rodada) + ' szansę na wpadnięcie w razie błędu!']
        else:
            frase_dist = ['Poprawna odpowiedź jest warta ' + valor + ', ',
                        'będziemy mieć ' + alternativas + ' opcje odpowiedzi i',
                        'e ' + str(rodada) + ' szanse na wpadnięcie w razie błędu!']
        mostrar_frases(frase_dist, x_inicial=1400, y_inicial=720, tam=48, enter=80, fonte='FreeSans')
        wait_until_enter(8)
        jog_eliminado = False

        nao_respondeu = [pl for pl in jogadores if not pl.eliminado]
        # PERGUNTAS
        for num_pergunta in range(num_perguntas[rodada - 1]):
            if jog_eliminado:
                continue
            
            roleta.update_image('img/roleta_inicio.png')
            
            pergunta, alternativas, resposta_certa = seleciona_pergunta(rodada)
            wait_time = uniform(2, 7)
            wait_until_enter(wait_time)  # Um tempinho de ‘suspense’
            roleta.update_image('img/roleta.png')
            img_pergunta.update_image('img/pergunta.png')
            blit_all(sair_do_jogo, essentials, jogadores)
            blit_pergunta(pergunta)
            sounds['question'].play()
            pygame.display.update()
            if desafiante.tipo != 0 and rodada < 4:
                wait_until_enter(6)

            if rodada == 4:
                # Na 4ª rodada, o desafiante é obrigado a desafiar o outro
                escolhido = desafiante.bot_escolhe(get_escolhas(jogadores, desafiante), get_leader(jogadores),
                                                    nao_respondeu, nao_respondeu_nunca, rodada)
            else:
                if rodada == 1 and num_pergunta == 0:
                    distribute_money(jogadores, 300, essentials, pergunta=pergunta)
                if desafiante.tipo == 0:
                    escolhido = passa_pra_quem(get_escolhas(jogadores, desafiante), sair_do_jogo)
                else:
                    wait_time = uniform(3, 10)
                    wait_until_enter(wait_time)

                    escolhido = desafiante.bot_escolhe(get_escolhas(jogadores, desafiante), get_leader(jogadores),
                                                    nao_respondeu, nao_respondeu_nunca, rodada)
            if escolhido is None:
                return
            if escolhido in nao_respondeu:
                nao_respondeu.remove(escolhido)
            if escolhido in nao_respondeu_nunca:
                nao_respondeu_nunca.remove(escolhido)

            roleta.update_image("img/roleta_" + str(escolhido.pos) + ".png")
            blit_all(sair_do_jogo, essentials, jogadores)
            blit_pergunta(pergunta)
            pygame.display.update()

            # PASSOU PARA ALGUÉM — Sem alternativas ainda
            wait_time = 5 if escolhido.tipo == 0 else 2
            wait_until_enter(wait_time)
            blit_all(sair_do_jogo, essentials, jogadores)
            blit_alternativas(pergunta, alternativas)
            pygame.display.update()
            # Um tempo para ler as alternativas
            start = pygame.time.get_ticks()
            # PASSOU PARA ALGUÉM — Mostra alternativas
            loop_jogo = True
            wait_pc = 9000
            time_limit = 15000 if escolhido.tipo == 0 else wait_pc
            sounds['answers'].play()
            while loop_jogo:
                blit_all(sair_do_jogo, essentials, jogadores)
                blit_alternativas(pergunta, alternativas)
                pygame.display.update()
                for ev in pygame.event.get():
                    if ev.type == pygame.QUIT:
                        pygame.quit()
                    if ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
                        if sair_do_jogo.check_click():
                            pygame.mixer.stop()
                            return
                    if ev.type == pygame.KEYDOWN:
                        if ev.key == pygame.K_RETURN:
                            loop_jogo = False
                        if ev.key == pygame.K_F1:
                            time_limit = time_limit * 10
                time = pygame.time.get_ticks() - start
                if time > time_limit:  # Espera 15 segundos para contar o tempo
                    loop_jogo = False
            img_pergunta.update_image('img/pergunta.png')
            pygame.display.update()
            start = pygame.time.get_ticks()
            loop_jogo = True

            resposta_escolhida = ''
            # TEMPO!
            if escolhido.tipo != 0:
                pos_resp_escolh, tempo_restante = escolhido.bot_responde(rodada, alternativas=alternativas, resposta_certa=resposta_certa)

            loop_jogo = True
            respondeu = False

            sounds['time_30_sec'].play()

            while loop_jogo:
                time = (30000 - (pygame.time.get_ticks() - start)) / 1000
                if time > 0:
                    seg = Texto(str(int(ceil(time))), 'Technology', 200, 1062, 610)
                else:
                    seg = Texto('0', 'Technology', 200, 1062, 610)
                # Blits comuns
                blit_all(sair_do_jogo, essentials, jogadores)
                blit_alternativas(pergunta, alternativas)

                Image('img/time.png', 942, 472).draw(window)
                if time <= 10:
                    time_runout = Image('img/time_runout.png', 942, 472)
                    alpha = int((time % 1) * 255)
                    time_runout.set_alpha(alpha)
                    time_runout.draw(window)

                
                seg.show_texto(window, 'center')

                pygame.display.update()

                if escolhido.tipo != 0:
                    # Bot responde quando chega o tempo limite
                    if time < tempo_restante:
                        resposta_escolhida = alternativas[pos_resp_escolh - 1]
                        blit_resposta_escolhida(pergunta, alternativas, resposta_escolhida)
                        pygame.display.update()
                        respondeu = True
                        loop_jogo = False

                for ev in pygame.event.get():
                    if ev.type == pygame.QUIT:
                        pygame.quit()

                    if ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
                        if sair_do_jogo.check_click():
                            pygame.mixer.stop()
                            return

                    if escolhido.tipo == 0 and ev.type == pygame.KEYDOWN:
                        key_map = {
                            pygame.K_a: 0, pygame.K_1: 0, pygame.K_KP1: 0,
                            pygame.K_b: 1, pygame.K_2: 1, pygame.K_KP2: 1,
                            pygame.K_c: 2, pygame.K_3: 2, pygame.K_KP3: 2,
                            pygame.K_d: 3, pygame.K_4: 3, pygame.K_KP4: 3,
                            pygame.K_e: 4, pygame.K_5: 4, pygame.K_KP5: 4
                        }

                        if ev.key in key_map:
                            index = key_map[ev.key]
                            num_alternativas = rodada + 1
                            if index < num_alternativas:
                                blit_resposta_escolhida(pergunta, alternativas, index)
                                resposta_escolhida = alternativas[index]
                                pos_resp_escolh = index + 1
                                respondeu = True
                                loop_jogo = False

                # Se o tempo acabar e ninguém respondeu
                if escolhido.tipo == 0 and time < 0:
                    pos_resp_escolh = None
                    loop_jogo = False
                    wait_until_enter(4)
            
            sounds['time_30_sec'].stop()
            if time < 0:
                tempo_restante = 0
            else:
                tempo_restante = int(ceil(time))
            pygame.display.update()

            # Respondeu a pergunta! Tempo de suspense
            suspense = 3000
            if respondeu:
                start = pygame.time.get_ticks()
                loop_jogo = True
                while loop_jogo:
                    blit_all(sair_do_jogo, essentials, jogadores)
                    blit_alternativas(pergunta, alternativas)
                    blit_resposta_escolhida(pergunta, alternativas, resposta_escolhida)
                    pygame.display.update()
                    for ev in pygame.event.get():
                        if ev.type == pygame.QUIT:
                            pygame.quit()
                        if ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
                            if sair_do_jogo.check_click():
                                pygame.mixer.stop()
                                return
                        if ev.type == pygame.KEYDOWN:
                            if ev.key == pygame.K_RETURN:
                                loop_jogo = False
                            if ev.key == pygame.K_F1:
                                time_limit = 10000
                    time = pygame.time.get_ticks() - start
                    if time > suspense:  # Botando 20 segundos até revelar
                        loop_jogo = False
            pygame.mixer.stop()
            
            if resposta_escolhida == resposta_certa:
                sounds['true'].play()
                pygame.time.delay(2500)
                sounds['aplausos1'].play()
                blit_certo_errado(pergunta, alternativas, resposta_escolhida, resposta_certa)
            else:
                sounds['false'].play()
                pygame.time.delay(1000)
                blit_errado(pergunta, alternativas, resposta_escolhida)
                pygame.display.update()
                if rodada > 1:
                    wait_until_enter(6)
                else:
                    wait_until_enter(3)
                sounds['true'].play()
                pygame.time.delay(2500)
                blit_certo_errado(pergunta, alternativas, resposta_escolhida, resposta_certa)
            
            pygame.display.update()
            if resposta_escolhida != resposta_certa:
                wait_until_enter(5)
                if escolhido.dinheiro > 0:
                    sounds['money'].play(0)
                if desafiante != escolhido:
                    if escolhido.dinheiro > 0:
                        desafiante.pega_dinheiro_do_outro(escolhido, window, sair_do_jogo, essentials, jogadores)
                else:
                    for pl in jogadores:
                        if not pl.eliminado:
                            if pl != desafiante:
                                outro_jogador = pl
                    outro_jogador.pega_dinheiro_do_outro(escolhido, window, sair_do_jogo, essentials, jogadores)
                loop = True
                wait_until_enter(5)
                start = pygame.time.get_ticks()
                joga_roleta = False
                time_limit = 5
                while loop:
                    segundos = (pygame.time.get_ticks() - start) / 1000
                    for ev in pygame.event.get():
                        if ev.type == pygame.QUIT:
                            pygame.quit()
                        if ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
                            if sair_do_jogo.check_click():
                                pygame.mixer.stop()
                                return
                            if alavanca.check_click():
                                pygame.mixer.stop()
                                caiu_ou_nao = jogar_roleta('normal', alavanca, rodada, escolhido, jogadores)
                                loop = False
                        if ev.type == pygame.KEYDOWN:
                            if ev.key == pygame.K_SPACE:
                                pygame.mixer.stop()
                                caiu_ou_nao = jogar_roleta('normal', alavanca, rodada, escolhido, jogadores)
                                loop = False
                            if ev.key == pygame.K_RETURN and escolhido.tipo != 0:
                                joga_roleta = True
                            if ev.key == pygame.K_F1 and escolhido.tipo != 0:
                                time_limit *= 10
                            if ev.key == pygame.K_F2:
                                pygame.mixer.stop()
                                sounds['bg_errado'].play()
                            if ev.key == pygame.K_F3:
                                pygame.mixer.stop()
                    if (segundos > time_limit and escolhido.tipo != 0) or (joga_roleta and escolhido.tipo != 0):
                        pygame.mixer.stop()
                        caiu_ou_nao = jogar_roleta('normal', alavanca, rodada, escolhido, jogadores)
                        loop = False

                if caiu_ou_nao:
                    jog_eliminado = True
                    wait_until_enter(int(sounds['fall_1'].get_length() - 1))
                    sounds['bg'].play()
                else:
                    wait_until_enter(int(sounds['save'].get_length() - 3))
                    desafiante = escolhido
            else:
                wait_until_enter(4)
                pygame.display.update()
                sounds['money'].play()
                escolhido.ganha_dinheiro(dinheiro_rodada[rodada - 1], window, sair_do_jogo, essentials, jogadores)
                pygame.display.update()
                desafiante = escolhido
                wait_until_enter(2)
            if not jog_eliminado:
                sounds['before_mex_open'].play(loops=5)
                roleta.update_image('img/roleta.png')
                blit_all(sair_do_jogo, essentials, jogadores)
                pygame.display.update()
                wait_until_enter(1)  # Tempo de espera para próxima pergunta
        if not jog_eliminado:
            blit_all(sair_do_jogo, essentials, jogadores)
            pygame.display.update()
            wait_until_enter(3)
            lider = get_leader(jogadores)
            if lider is not None:
                lider.move_center()

            blit_all(sair_do_jogo, essentials, jogadores)
            pygame.display.update()
            loop = True
            wait_until_enter(1)
            if lider is not None:
                if lider.tipo == 0:
                    while loop:
                        for ev in pygame.event.get():
                            if ev.type == pygame.QUIT:
                                pygame.quit()
                            if ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
                                if sair_do_jogo.check_click():
                                    pygame.mixer.stop()
                                    return
                                if alavanca.check_click():
                                    pygame.mixer.stop()
                                    eliminado = jogar_roleta('carrasco', alavanca, jogadores=jogadores)
                                    loop = False
                            if ev.type == pygame.KEYDOWN:
                                if ev.key == pygame.K_SPACE:
                                    pygame.mixer.stop()
                                    eliminado = jogar_roleta('carrasco', alavanca, jogadores=jogadores)
                                    loop = False
                else:
                    wait_until_enter(2)
                    pygame.mixer.stop()
                    eliminado = jogar_roleta('carrasco', alavanca, jogadores=jogadores)
            else:
                wait_until_enter(2)
                pygame.mixer.stop()
                eliminado = jogar_roleta('carrasco', alavanca, jogadores=jogadores)
                
            wait_until_enter(int(sounds['fall_1'].get_length() - 1))
            if lider is not None:
                lider.change_pos(lider.pos)
            sounds['bg'].play()
            espolios = int(eliminado.dinheiro // (5 - rodada))
            wait_until_enter(5)
            if espolios > 0 and rodada < 4:
                distribute_money(jogadores, espolios, essentials, eliminado=eliminado)
            elif espolios > 0 and rodada == 4:
                get_leader(jogadores).pega_dinheiro_do_outro(eliminado, window, sair_do_jogo, essentials, jogadores)
        wait_until_enter(10)
        roleta.update_image('img/roleta_inicio.png')
        pygame.mixer.stop()

    rodada = 5
    finalista = get_leader(jogadores)  # O líder é logicamente o finalista!
    finalista.move_center()
    sounds['open_round'].play()
    round_img(rodada, jogadores)

    
    img_pergunta.draw(window)
    
    blit_all(sair_do_jogo, essentials, jogadores)
    pygame.display.update()
    wait_until_enter(2)
    sounds['before_mex_open'].play(loops=20)

    loc_vermelho = [randrange(6)]
    esperando_enter = True
    start = pygame.time.get_ticks()
    while esperando_enter:
        seg = (pygame.time.get_ticks() - start) / 1000
        if seg > 5 and finalista.tipo != 0:
            esperando_enter = False
        roleta.update_image(f'img/roleta_play_{str(loc_vermelho[0])}.png')
        blit_vermelho(sair_do_jogo, essentials, jogadores, loc_vermelho, texto_final='Na rodada final, você terá que acertar perguntas sem alternativas. A primeira vale 5.000 (com 3 chances de cair), '
            'a segunda 25.000 (com 4 chances de cair), e a terceira 100.000 (com 5 chances de cair). '
            'Antes de cada pergunta, você deverá jogar a roleta e escolher uma das zonas de risco. '
            'Se errar, os buracos abrem, e se você cair, leva apenas o dinheiro acumulado das rodadas anteriores. '
            'Se acertar, pode continuar rumo aos 100.000!')
        loc_vermelho = [(v + 1) % 6 for v in loc_vermelho]
        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if sair_do_jogo.check_click():
                    pygame.mixer.stop()
                    return
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                esperando_enter = False
        pygame.time.delay(250)
        
    pygame.display.update()
    pygame.mixer.stop()
    roleta.update_image('img/roleta.png')
    blit_queda(sair_do_jogo, essentials, jogadores, [], finalista, pre_final=True)

    wait_until_enter(2)
    pygame.display.update()

    start = pygame.time.get_ticks()

    valor_finais = [5000, 25000, 100000]
    chances_de_cair = [3, 4, 5]
    time_limit = 5

    joga_roleta = False
    loop_play_roulette = True
    etapa = 0
    qtd_erradas = 0
    while etapa < len(valor_finais):
        blit_all(sair_do_jogo, essentials, jogadores)
        pygame.display.update()
        if finalista.tipo != 0:
            wait_until_enter(2)
        vf = valor_finais[etapa]
        cc = chances_de_cair[etapa]
        loop_play_roulette = True
        while loop_play_roulette:
            segundos = (pygame.time.get_ticks() - start) / 1000
            if finalista.tipo == 0:
                for ev in pygame.event.get():
                    if ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
                        if sair_do_jogo.check_click():
                            pygame.mixer.stop()
                            return
                        if alavanca.check_click():
                            pygame.mixer.stop()
                            vermelhos = jogar_roleta('final', alavanca, chances_de_cair=cc,
                                                        jogador_em_risco=finalista,
                                                        jogadores=jogadores)
                            loop_play_roulette = False
                    if ev.type == pygame.KEYDOWN:
                        if ev.key == pygame.K_SPACE:
                            pygame.mixer.stop()
                            vermelhos = jogar_roleta('final', alavanca, chances_de_cair=cc,
                                                        jogador_em_risco=finalista,
                                                        jogadores=jogadores)
                            loop_play_roulette = False
                        if ev.key == pygame.K_RETURN and finalista.tipo != 0:
                            joga_roleta = True
            if (segundos > time_limit and finalista.tipo != 0) or (joga_roleta and finalista.tipo != 0):
                pygame.mixer.stop()
                vermelhos = jogar_roleta('final', alavanca, chances_de_cair=cc, jogador_em_risco=finalista, jogadores=jogadores)
                loop_play_roulette = False
            joga_roleta = False

        pos_buraco = None
        
        while pos_buraco is None:
            if finalista.tipo == 0:
                for ev in pygame.event.get():
                    if ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
                        pos_buraco = click_on_buraco(pygame.mouse.get_pos())
            else:
                wait_until_enter(sounds['mex_close_slow_heartbeat'].get_length() - 1)
                pos_buraco = randrange(6)
        
        sounds['before_mex_open'].play(loops=20)
        finalista.change_pos(pos_buraco)
        roleta.update_image(f'img/roleta_play.png')
        blit_all(sair_do_jogo, essentials, jogadores)
        pygame.display.update()
        pergunta, list_accepted, right_answer_text = seleciona_pergunta(5)
        window.fill('black')
        img_pergunta.draw(window)
        wait_until_enter(3)
        blit_all(sair_do_jogo, essentials, jogadores)
        blit_pergunta(pergunta, final_valor=vf)
        sounds['final_question'].play()
        pygame.display.update()

        resposta_escrita = ''
        resposta = ''
        loop_jogo = True
        
        wait_until_enter(10)
        sounds['time_30_sec'].play()
        if finalista.tipo != 0:
            # 🤖 BOT RESPONDE
            resposta, tempo = finalista.bot_responde(5, resposta_certa=right_answer_text)

        else:
            # 👤 HUMANO VAI DIGITAR
            pygame.key.start_text_input()
            resposta_escrita = ''

        start_time = pygame.time.get_ticks()
        while loop_jogo:
            now = pygame.time.get_ticks()
            time = (30000 - (now - start_time)) / 1000

            window.fill('black')
            blit_all(sair_do_jogo, essentials, jogadores)
            blit_pergunta(pergunta, final_valor=vf)
            
            Image('img/time.png', 942, 472).draw(window)
            if time <= 10:
                time_runout = Image('img/time_runout.png', 942, 472)
                alpha = int((time % 1) * 255)
                time_runout.set_alpha(alpha)
                time_runout.draw(window)
            
            seg = Texto(str(int(ceil(max(0, time)))), 'Technology', 200, 1062, 610)
            seg.show_texto(window, 'center')

            # 🖋️ Mostra resposta atual
            if finalista.tipo == 0:
                blit_resposta_escolhida(pergunta, [resposta_escrita], 0, final_valor=vf)
            else:
                if time <= tempo:
                    resposta_mostrada = resposta if resposta else 'Bot nie wie.'
                    blit_resposta_escolhida(pergunta, [resposta_mostrada], 0, final_valor=vf)
                    resposta_escrita = resposta_mostrada
                    loop_jogo = False

            pygame.display.update()

            for ev in pygame.event.get():
                if ev.type == pygame.QUIT:
                    pygame.quit()

                if ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
                    if sair_do_jogo.check_click():
                        pygame.mixer.stop()
                        if finalista.tipo == 0:
                            pygame.key.stop_text_input()
                        return

                if finalista.tipo == 0:
                    if ev.type == pygame.TEXTINPUT:
                        resposta_escrita += ev.text

                    elif ev.type == pygame.KEYDOWN:
                        if ev.key == pygame.K_BACKSPACE:
                            resposta_escrita = resposta_escrita[:-1]
                        elif ev.key == pygame.K_RETURN:
                            loop_jogo = False

            # ⏱️ Tempo acabou
            if time <= 0:
                loop_jogo = False

        if finalista.tipo == 0:
            pygame.key.stop_text_input()
        pygame.mixer.stop()
        alternativas = [resposta_escrita]
        if resposta_escrita in list_accepted or resposta_escrita.lower() in list_accepted:
            sounds['true'].play()
            pygame.time.delay(2500)
            sounds['aplausos2'].play()
            alternativas = [right_answer_text]
            blit_certo_errado(pergunta, alternativas, right_answer_text, right_answer_text, final_valor=vf)
            pygame.display.update()
            wait_until_enter(5)
            finalista.ganha_dinheiro(vf, window, sair_do_jogo, essentials, jogadores)
            if vf == 5000:
                '''

                '''
                mostrar_frases_controlado('Udało Ci się odpowiedzieć poprawnie! Możesz teraz przejść do 25 000 zł, ale w razie niepowodzenia ' \
                                        'masz 4 szanse na wpadnięcie i ryzykujesz swoje 5 000 zł. Czy chcesz kontynuować?',
                            x_inicial=1400, y_inicial=60, tam_fonte=60, enter=80, fonte='FreeSans')
            elif vf == 25000:
                mostrar_frases_controlado('Udało Ci się odpowiedzieć poprawnie! Możesz teraz przejść do 100 000 zł, ale w razie niepowodzenia ' \
                                        'masz 4 szanse na wpadnięcie i ryzykujesz swoje 25 000 zł. Czy chcesz kontynuować?',
                            x_inicial=1400, y_inicial=60, tam_fonte=60, enter=80, fonte='FreeSans')
            else:
                break
            # Decidir entre continuar ou não
            loop = True
            parou = False
            continuar = Botao('Kontynuować', 1400, 700, align='center')
            parar = Botao('Zakończyć', 1400, 855, align='center')
            continuar.show_texto(window)
            parar.show_texto(window)
            pygame.display.update()
            sounds['before_mex_open'].play(loops=20)
            start = pygame.time.get_ticks()
            decision_time = 5
            while loop:
                for ev in pygame.event.get():
                    if ev.type == pygame.QUIT:
                        pygame.quit()
                    if ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
                        if sair_do_jogo.check_click():
                            pygame.mixer.stop()
                            return
                        if finalista.tipo == 0: # Clicar aqui só tem valor se for humano
                            if continuar.check_click():
                                etapa += 1
                                finalista.move_center()
                                finalista.dinheiro -= vf
                                loop = False
                            if parar.check_click():
                                loop = False
                                parou = True
                segundos = (pygame.time.get_ticks() - start) / 1000
                if segundos > decision_time and finalista.tipo != 0:
                    loop = False
                    if finalista.bot_para_ou_continua(qtd_erradas):
                        etapa += 1
                        finalista.move_center()
                        finalista.dinheiro -= vf
                    else:
                        parou = True
            blit_all(sair_do_jogo, essentials, jogadores)
            pygame.display.update()
            if parou:
                break
            wait_until_enter(2)
        else:     # Não acertou a pergunta
            sounds['false'].play()
            qtd_erradas += 1
            pygame.time.delay(1000)
            blit_errado(pergunta, alternativas, resposta_escrita, final_valor=vf)
            pygame.display.update()
            wait_until_enter(6)
            sounds['true'].play()
            pygame.time.delay(2500)
            alternativas = [resposta_escrita, right_answer_text]
            blit_certo_errado(pergunta, alternativas, resposta_escrita, right_answer_text, final_valor=vf)
            pygame.display.update()
            wait_until_enter(5)
            blit_queda(sair_do_jogo, essentials, jogadores, vermelhos, finalista, final=True)
            if not finalista.eliminado and vf == 100000:
                finalista.dinheiro += 100000
                etapa += 1
                sounds['aplausos2'].play()

        if finalista.eliminado:
            break
        else:
            finalista.move_center()
            blit_all(sair_do_jogo, essentials, jogadores)
    sounds['before_mex_open'].stop()
    sounds['closing'].play()
    finalista.move_center()
    premio_final = str(finalista.dinheiro) + ' zł'
    mostrar_frases(['NAGRODA GŁÓWNA'], x_inicial=1400, y_inicial=450, tam=80, enter=80, fonte='FreeSansBold')
    
    mostrar_frases([premio_final.upper()], x_inicial=1400, y_inicial=640, tam=180, enter=80, fonte='Technology')
    pygame.display.update()
    # FIM DE JOGO - GRAVA RECORDE
    if finalista.tipo == 0:
        df_recordes = pd.read_json("records.json")
        vencedor = {'name': finalista.nome, 'money': finalista.dinheiro}
        df_vencedor = pd.DataFrame(vencedor, index=[0])
        df_recordes = pd.concat([df_recordes, df_vencedor], ignore_index=True)
        df_recordes = df_recordes.sort_values(by=['money'],
                                              ascending=False)
        df_recordes = df_recordes.head(10)
        df_recordes.to_json("records.json", orient="records")
    
    for som in sounds.keys():
        sounds[som].stop()
    
    wait_until_enter(120)
    return


def configuracoes():
    global window
    global volta_menu
    global sounds
    global vol
    global df_perguntas
    global nome_da_base

    nome_inicial = nome_da_base
    limpa_tela(window)
    x = 60
    y = 170

    df_jogadores = pd.read_json("players.json")
    df_jogadores = df_jogadores.copy()
    input_boxes = []
    opcoes_bot = []
    config_salva = False
    tudo_salvo = Texto('Ustawienia zostały pomyślnie zapisane!', 'FreeSans', tam=36, x=1880, y=985)
    tipos = []

    for n, t in zip(df_jogadores['nome'], df_jogadores['tipo']):
        input_box = InputBox(x, y, 355, 45, text=n)
        input_boxes.append(input_box)

        option_box_tipo = OptionBox(x + 360, y, 425, 45, (25, 25, 25), (120, 120, 120), selected=t)
        opcoes_bot.append(option_box_tipo)
        tipos.append(t)
        # x += 360
        y += 50

    txt_base = Texto('Baza pytań', 'FreeSans', tam=48, x=1100, y=170)
    bases = [b for b in listdir('base') if '.csv' in b]

    main_loc = bases.index(nome_da_base)
    base = OptionBox(900, 220, 400, 45, (25, 25, 25), (120, 120, 120), option_list=bases, selected=main_loc)
    loop_config = True

    salvar = Botao('Zapisz ustawienia', 1880, 880, align='topright')
    while loop_config:

        limpa_tela(window)

        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                pygame.quit()
            if ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
                if volta_menu.check_click():
                    pygame.mixer.stop()
                    return
                if salvar.check_click():
                    novos_jogadores = []
                    for box in input_boxes:
                        novos_jogadores.append(box.text)
                    for i in range(len(novos_jogadores)):
                        df_jogadores.loc[i, 'nome'] = novos_jogadores[i]
                        df_jogadores.loc[i, 'tipo'] = opcoes_bot[i].selected
                    df_jogadores.to_json("players.json", orient="records")
                    pygame.mixer.music.set_volume(vol)
                    for som in sounds.keys():
                        sounds[som].set_volume(vol)

                    nome_da_base = base.option_list[base.selected]
                    if nome_da_base != nome_inicial:
                        df_perguntas = pd.read_csv('base/' + nome_da_base, encoding='utf-8', sep=';')
                        df_perguntas['used'] = False
                        nome_inicial = nome_da_base
                    config_salva = True
                for i in range(len(tipos)):
                    opcoes_bot[i].update(ev)
                base.update(ev)

            if ev.type == pygame.QUIT:
                pygame.quit()
            for box in input_boxes:
                box.handle_event(ev)
            if ev.type == pygame.KEYDOWN:
                if ev.key == pygame.K_MINUS:
                    input_box_active = False
                    for ib in input_boxes:
                        if ib.active:
                            input_box_active = True
                            break
                    if not input_box_active:
                        vol -= 0.1
                    # pygame.mixer.music.set_volume(vol)
                if ev.key == pygame.K_EQUALS or ev.key == pygame.K_PLUS:
                    vol += 0.1
                    vol = 1 if vol > 1 else vol
                    # pygame.mixer.music.set_volume(vol)

        for box in input_boxes:
            box.update()

        for box in input_boxes:
            box.draw(window)

        volta_menu.show_texto(window)
        if config_salva:
            tudo_salvo.show_texto(window, align='topright')

        titulo = Texto('USTAWIENIA', 'FreeSansBold', 48, 960, 40)
        titulo.show_texto(window, 'center')

        txt_jogadores = Texto('Gracze', 'FreeSansBold', 48, 45, 100)
        txt_jogadores.show_texto(window, 'topleft')

        txt_controles = Texto('Jak grać: ', 'FreeSansBold', 48, 45, 450)
        txt_controles.show_texto(window, 'topleft')

        txt_controles_1 = Texto('SPACJA – Zakręć ruletą', 'FreeSans', 30, 60, 525)
        txt_controles_1.show_texto(window, 'topleft')

        txt_controles_1 = Texto(
            'ENTER – Pomiń (jeśli jakaś akcja gry trwa długo); Wprowadź odpowiedź w rundzie finałowej',
            'FreeSans', 30, 60, 575)
        txt_controles_1.show_texto(window, 'topleft')

        txt_controles_2 = Texto('Aby wyzwać – Kliknij numer gracza lub wpisz numer gracza',
                                'FreeSans', 30, 60, 625)
        txt_controles_2.show_texto(window, 'topleft')

        txt_controles_2 = Texto('Aby odpowiedzieć na pytanie – Wpisz literę opcji (A do E) lub numer (1 do 5)',
                                'FreeSans', 30, 60, 675)
        txt_controles_2.show_texto(window, 'topleft')

        txt_controles_2 = Texto('P – Pauza gry (z wyjątkiem rundy finałowej)',
                                'FreeSans', 30, 60, 725)
        txt_controles_2.show_texto(window, 'topleft')

        txt_volume = Texto('Głośność: ' + str(int(vol * 100)) + '%', 'FreeSansBold', 48, 45, 800)
        txt_volume.show_texto(window, 'topleft')

        txt_volume = Texto('‘+’ – zwiększa głośność; ‘–’ – zmniejsza głośność', 'FreeSans', 36, 45, 860)
        txt_volume.show_texto(window, 'topleft')

        txt_base.show_texto(window, 'center')

        salvar.show_texto(window)

        for op in opcoes_bot:
            if not op.draw_menu:
                op.draw(window)
        for op in opcoes_bot:
            if op.draw_menu:
                op.draw(window)
        base.draw(window)

        pygame.display.update()


def mostra_regras():
    global window
    global volta_menu
    limpa_tela(window)
    titulo = 'ZASADY: ROSYJSKA RULETKA'

    # Fonte usada para medir largura
    import pygame.freetype
    font_path = 'fonts/FreeSans.ttf'
    font_size = 27
    font = pygame.freetype.Font(font_path, font_size)
    max_width = 1840

    # Texto bruto (sem quebras)
    texto_bruto = (
        'Gra składa się dokładnie z 6 otworów, 5 graczy, 4 rund eliminacyjnych oraz rundy finałowej. Na początku gry każdy gracz otrzymuje 300 zł. '
        'Po zakończeniu każdej z rund jeden gracz zostaje wyeliminowany. 1. runda: 8 pytań; 2. runda: 7 pytań; 3. runda: 6 pytań; 4 runda: 5 pytań.'
        'Każde pytanie musi zostać przekazane przeciwnikowi. Gracz ma 30 sekund na udzielenie odpowiedzi. Jeśli odpowie poprawnie, otrzymuje określoną '
        'kwotę pieniędzy. Jeśli odpowie błędnie lub się nie wyrobi, traci swoje pieniądze na rzecz wyzywającego i musi zakręcić kołem ruletki z liczbą '
        'czerwonych pól równą numerowi rundy.'
        'Jeśli czerwone pole nie zatrzyma się na tym graczu, runda trwa dalej, a on zostaje następnym wyzywającym (o ile to nie było ostatnie pytanie danej rundy).'
        'Jeśli czerwone pole się na nim zatrzyma, wpada do otworu, zostaje wyeliminowany, a runda się kończy.'
        'W każdej kolejnej rundzie rośnie ryzyko eliminacji: 1. runda – 1 czerwona szansa na 6; 2. runda – 2 czerwone szanse na 6; ;3. runda – 3 czerwone szanse na 6;'
        '4. runda – 4 czerwone szanse na 6. Jeśli po zadaniu wszystkich pytań nikt nie zostanie wyeliminowany, lider (gracz z największą sumą pieniędzy) jest chroniony '
        'przed eliminacją i kręci ruletką, aby wyeliminować jednego z pozostałych. W przypadku remisu między dwoma lub więcej graczami nikt nie jest chroniony, a '
        'ruletka jest kręcona z równą szansą wpadnięcia dla wszystkich uczestników.'
        'Eliminowany gracz dzieli swój majątek po równo — jego pieniądze są rozdzielane między pozostałych.'
        'Wynagrodzenia za poprawną odpowiedź w rundach 1–4 to kolejno: 300 zł, 600 zł, 1000 zł i 1500 zł. Liczba opcji odpowiedzi również wzrasta: '
        '2 w 1. rundzie, aż do 5 w 4. rundzie. Gdy zostaje tylko 1 gracz, staje się on finalistą i przechodzi do rundy finałowej. Zapewniona jest mu '
        'przynajmniej całkowita suma zgromadzona do tej pory. Aby wygrać maksymalną nagrodę 100 000 zł, musi kolejno poprawnie odpowiedzieć na pytania '
        'o wartości 5 000 zł (3 szanse eliminacji przy błędzie), 25 000 zł (4 szanse) i wreszcie 100 000 zł (5 szans).'
        'Jeśli przegra przy pytaniu o 100 000 zł, ale uniknie eliminacji, i tak zgarnia 100 000 zł.'
        'Jeśli przegra przy pytaniu o 25 000 zł lub 5 000 zł, ale uniknie eliminacji, pozostaje przy tej samej wartości aż do momentu wygranej lub eliminacji.'
        'Po udzieleniu poprawnej odpowiedzi finalista może przerwać grę i zabrać zgromadzone środki lub kontynuować, wówczas przechodzimy do kolejnego etapu.'
    )

    # Quebra de linha automática
    palavras = texto_bruto.split()
    linhas = []
    linha_atual = ""
    for palavra in palavras:
        tentativa = f"{linha_atual} {palavra}".strip()
        largura = font.get_rect(tentativa).width
        if largura <= max_width:
            linha_atual = tentativa
        else:
            linhas.append(linha_atual)
            linha_atual = palavra
    if linha_atual:
        linhas.append(linha_atual)

    # Título
    txt_titulo = Texto(titulo, 'FreeSansBold', 48, 960, 40)
    txt_titulo.show_texto(window, 'center')

    volta_menu.show_texto(window)

    # Renderizar texto linha por linha
    for i, linha in enumerate(linhas):
        txt = Texto(linha, 'FreeSans', font_size, 45, 80 + 35 * i)
        txt.show_texto(window, 'topleft')


    # Loop
    loop_regras = True
    while loop_regras:
        pygame.display.update()
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                pygame.quit()
            if ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
                if volta_menu.check_click():
                    pygame.mixer.stop()
                    loop_regras = False

def mostra_creditos():
    global window
    global volta_menu
    limpa_tela(window)
    volta_menu.show_texto(window)

    titulo = 'TWÓRCY'
    txt_titulo = Texto(titulo, 'FreeSansBold', 48, 960, 40)
    txt_titulo.show_texto(window, 'center')

    cred = [
        'Kody i grafika – Alex Torres',
        'Wykorzystane technologie – biblioteka Pygame',
        'Muzyka w tle – Krystian Jabłoński (który dostarczył mi utwory użyte w programie)',
        'Inspiracja kodem – QWERule Studios (autorzy rosyjskiej wersji gry, którzy umieścili część kodu na GitHubie)',
        'Stworzenie formatu gry oraz innych utworów w tle i dźwięków – Gunnar Wetterberg i Sony Pictures Television'
    ]

    agrad = 'PODZIĘKOWANIA'
    list_ag = [
        '– Jezus Chrystus. Przede wszystkim i przede wszystkim Jemu, bo bez Niego nic nie jestem. On obdarzył mnie darami i miłością, bym mógł stworzyć te gry.',
        '– Moi rodzice, Alex & Juliana – za to, że uczynili mnie osobą, którą jestem. Oglądali brazylijski program, a ja, mając zaledwie 5 lat, także go oglądałem. Podobał mi się tak bardzo, że stworzyłem grę opartą na brazylijskiej wersji, a teraz także na polskiej.',
        '– Misael Castro – mój duchowy przewodnik, a obecnie lider mojej komórki, który zmotywował mnie do stworzenia gry opartej na brazylijskiej wersji po tym, jak znalazłem utwory użyte w programie. Polski odpowiednik powstał później. Przy okazji byłem ojcem chrzestnym na jego ślubie z Emilią Tainá, która tym razem nie przyczyniła się do polskiej wersji (ani ona, ani ja nie mówimy po polsku!)',
        '– Alexandre Simplício – wielki przyjaciel, który inspiruje wszystkich wokół siebie.',
        '– Komórka BOLD (@boldgds na Instagramie) – komórka, która dopiero się rozwijała, gdy gra została ukończona. Wierzę, że przeżyję w niej wiele wspaniałych chwil, bo powstała ona z komórki opisanej poniżej.',
        '– Komórka HOME (@gdshome na Instagramie) – mówię zarówno do HOME, jak i BOLD: mieć przyjaciół takich jak wy to milion razy lepsze niż ominięcie pięciu czerwonych pól.',
        '– RecordTV – za wprowadzenie tego znakomitego programu na brazylijską telewizję.',
        '– Krystian Jabłoński – za zachęcenie mnie do stworzenia polskiej wersji Roleta Russa oraz pomoc przy zasadach i efektach dźwiękowych gry. Bez tego gra by nie powstała.',
        '– Mateusz Fret – za wkład w formułę pytań, udostępnianie materiałów wideo z polskiej wersji programu i tym samym odzwierciedlenie przebiegu show z maksymalną dokładnością.',
        '– ChatGPT – za wsparcie przy pisaniu i ulepszaniu kodu oraz przetłumaczenie wszystkich tych tekstów na język polski.'
    ]

    font = pygame.font.Font('fonts/FreeSans.ttf', 30)
    max_width = 1700
    y = 80

    for linha in cred:
        palavras = linha.split()
        linha_atual = ""
        for palavra in palavras:
            tentativa = f"{linha_atual} {palavra}".strip()
            largura = font.size(tentativa)[0]
            if largura <= max_width:
                linha_atual = tentativa
            else:
                txt = Texto(linha_atual, 'FreeSans', 30, 100, y)
                txt.show_texto(window, 'topleft')
                y += 35
                linha_atual = palavra
        if linha_atual:
            txt = Texto(linha_atual, 'FreeSans', 30, 100, y)
            txt.show_texto(window, 'topleft')
            y += 35

    # Título dos agradecimentos
    txt_titulo_2 = Texto(agrad, 'FreeSansBold', 48, 960, y + 50)
    txt_titulo_2.show_texto(window, 'center')
    y += 100

    for bloco in list_ag:
        if bloco.strip() == "":
            y += 16  # espaço extra
            continue
        palavras = bloco.split()
        linha_atual = ""
        primeira_linha = True
        for palavra in palavras:
            tentativa = f"{linha_atual} {palavra}".strip()
            largura = font.size(tentativa)[0]
            if largura <= max_width:
                linha_atual = tentativa
            else:
                if primeira_linha and bloco.strip().startswith('-'):
                    linha_atual = "     " + linha_atual
                    primeira_linha = False
                txt = Texto(linha_atual, 'FreeSans', 30, 100, y)
                txt.show_texto(window, 'topleft')
                y += 35
                linha_atual = palavra
        if linha_atual:
            if primeira_linha and bloco.strip().startswith('-'):
                linha_atual = "     " + linha_atual
            txt = Texto(linha_atual, 'FreeSans', 30, 100, y)
            txt.show_texto(window, 'topleft')
            y += 35

    loop_creditos = True
    while loop_creditos:
        pygame.display.update()
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                pygame.quit()
            if ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
                if volta_menu.check_click():
                    pygame.mixer.stop()
                    loop_creditos = False


def mostra_recordes():
    global window
    global volta_menu
    limpa_tela(window)
    volta_menu.show_texto(window)

    df_recordes = pd.read_json("records.json")
    df_recordes = df_recordes.sort_values(by=['money'], ascending=False)
    df_recordes = df_recordes.head(10)

    titulo = 'REKORDY'
    tam_fonte = 54
    intervalo = 72

    for n, d, i in zip(df_recordes['name'], df_recordes['money'], range(10)):
        dinheiro_final = str(d) + ' zł'
        if n != '--':
            txt_dinheiro_final = Texto(dinheiro_final.upper(), 'Technology', 72, 960, 235 + intervalo * i)
        else:
            txt_dinheiro_final = Texto('--', 'Technology', tam_fonte, 960, 235 + intervalo * i)
        txt_nome = Texto(n, 'FreeSans', tam_fonte, 330, 235 + intervalo * i)

        txt_nome.show_texto(window, 'center')
        txt_dinheiro_final.show_texto(window, 'center')

    txt_titulo = Texto(titulo, 'FreeSansBold', 90, 960, 60)
    txt_titulo.show_texto(window, 'center')

    txt_tabela = Texto('Mistrz', 'FreeSansBold', 72, 330, 150)
    txt_tabela.show_texto(window, 'center')

    txt_tabela = Texto('NAGRODA', 'FreeSansBold', 72, 960, 150)
    txt_tabela.show_texto(window, 'center')
    loop_recordes = True
    while loop_recordes:

        pygame.display.update()
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                pygame.quit()
            if ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
                if volta_menu.check_click():
                    pygame.mixer.stop()
                    loop_recordes = False


def menu_principal():
    loop = True
    while loop:

        window.fill('black')
        roleta_logo.draw(window)
        iniciar.show_texto(window)
        config.show_texto(window)
        regras.show_texto(window)
        recordes.show_texto(window)
        creditos.show_texto(window)
        sair.show_texto(window)
        versao_do_jogo.show_texto(window, align='topleft')

        pygame.display.update()

        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                pygame.quit()
            if ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
                if iniciar.check_click():
                    iniciar_jogo()
                if config.check_click():
                    configuracoes()
                if regras.check_click():
                    mostra_regras()
                if recordes.check_click():
                    mostra_recordes()
                if creditos.check_click():
                    mostra_creditos()
                if sair.check_click():
                    sys.exit()


infoObject = pygame.display.Info()
res_usuario = (infoObject.current_w, infoObject.current_h)

window = pygame.display.set_mode(DISPLAYS[get_display_index()], pygame.FULLSCREEN)
# window = pygame.display.set_mode((1920, 1080), pygame.FULLSCREEN)

icon = pygame.image.load('img/rr_icon.png')
pygame.display.set_caption('Rosyjska Ruletka')
pygame.display.set_icon(icon)

roleta_logo = Image("img/RR_Poland.jpg", 0, 0)

roleta = Image("img/roleta_inicio.png", 360, 50)
img_dados = Image("img/jogadores.png", 17, 660)
alavanca = Image("img/alavanca1-0.png", 0, 75)
essentials = [roleta, img_dados, alavanca]

iniciar = Botao('Nowa Gra', 1850, 25, cor_contorno=(0,0,0))
config = Botao('Ustawienia', 1850, 150, cor_contorno=(0,0,0))
regras = Botao('Zasady', 1850, 275, cor_contorno=(0,0,0))
recordes = Botao('Rekordy', 1850, 400, cor_contorno=(0,0,0))
creditos = Botao('Twórcy', 1850, 850, cor_contorno=(0,0,0))
sair = Botao('Wyjście', 1850, 950, cor_contorno=(0,0,0))
sair_do_jogo = Botao('Wyjście z gry', 10, 10, tam=30, align='topleft')
volta_menu = Botao('Powrót do menu', 10, 10, tam=30, align='topleft')
versao_do_jogo = Texto('Wersja 1.0', 'FreeSans', 48, 40, 1000, cor_contorno=(0,0,0))

img_pergunta = Image('img/pergunta.png', 0, 0)

try:
    nome_da_base = 'main.csv'
    df_perguntas = pd.read_csv('base/main.csv', encoding='utf-8', sep=';')
except:
    nome_da_base = listdir('base')[0]
    df_perguntas = pd.read_csv('base/'+nome_da_base, encoding='utf-8', sep=';')
df_perguntas['used'] = False

sounds = load_sounds()
vol = round(0.4, 2)
for som in sounds.keys():
    sounds[som].set_volume(vol)
pygame.mixer.music.set_volume(vol)
main_loop = True
menu_principal()