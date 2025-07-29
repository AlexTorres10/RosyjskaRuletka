import pygame
from display import Image, get_ratio, mostra_essentials
from textos_menu import Texto
from copy import copy
from random import randint, choice, uniform
                   #0          #1          #2            #3         #4        #5
pos_buracos = [(584, 466), (417, 370), (417, 180), (584, 80), (762, 180), (762, 370)]
pos_players = [(610, 495), (442, 398), (442, 208), (610, 107), (790, 208), (790, 398)]
pos_nome = [(240, 690), (240, 765), (240, 840), (240, 915), (240, 990)]
pos_dinheiro = [(680, 690), (680, 765), (680, 840), (680, 915), (680, 990)]

for list_of_pos in [pos_dinheiro, pos_nome]:
    for i in range(len(list_of_pos)):
        list_of_pos[i] = (int(list_of_pos[i][0] * get_ratio()), int(list_of_pos[i][1] * get_ratio()))


class Jogador:
    def __init__(self, nome, pos, tipo, currency="zł", sep=' ', front=False):
        self.nome = nome
        self.dinheiro = 0
        self.eliminado = False
        self.pos = pos
        self.pos_original = pos
        self.image = Image("img/number" + str(pos) + ".png", pos_players[pos][0], pos_players[pos][1])
        self.tam_fonte = int(36 * get_ratio())
        self.tipo = tipo
        self.currency = currency
        self.sep = sep
        self.front = front

    def set_tipo(self, tipo):
        self.tipo = tipo

    def pega_dinheiro_do_outro(self, outro_jogador, w, s, ess, jog):
        fatias = int(outro_jogador.dinheiro / 10)
        for i in range(10):
            self.dinheiro += fatias
            outro_jogador.dinheiro -= fatias
            w.fill('black')
            s.show_texto(w)
            mostra_essentials(w, ess)
            mostra_jogadores(w, jog)
            pygame.time.delay(100)
            pygame.display.update()
        if outro_jogador.dinheiro > 0:
            self.dinheiro += outro_jogador.dinheiro
            outro_jogador.dinheiro = 0
            w.fill('black')
            s.show_texto(w)
            mostra_essentials(w, ess)
            mostra_jogadores(w, jog)
            pygame.display.update()

        if (self.dinheiro % 10) >= 8:
            self.dinheiro += (10 - (self.dinheiro % 10))
            w.fill('black')
            s.show_texto(w)
            mostra_essentials(w, ess)
            mostra_jogadores(w, jog)
            pygame.display.update()

    def ganha_dinheiro(self, dinheiro, w, s, ess, jog):
        fatia = int(dinheiro // 5)
        for _ in range(5):
            w.fill('black')
            s.show_texto(w)
            self.dinheiro += fatia
            mostra_essentials(w, ess)
            mostra_jogadores(w, jog)

            pygame.time.delay(200)
            pygame.display.update()


    def eliminar(self, jogadores, rodada=0):
        self.eliminado = True
        if rodada < 5:
            if self.dinheiro > 0:
                count = 0
                for pl in jogadores:
                    if not pl.eliminado:
                        count += 1
                dinheiro_repartido = int(self.dinheiro / count)
                return dinheiro_repartido
        return self.dinheiro
        

    def change_pos(self, nova_pos):
        self.image = Image("img/number" + str(self.pos_original) + ".png", pos_players[nova_pos][0],
                               pos_players[nova_pos][1])
        self.pos = nova_pos


    def move_center(self, nova_pos=(610, 300)):
        self.image = Image("img/number" + str(self.pos_original) + ".png", nova_pos[0], nova_pos[1])


    def display_nome(self, window):
        texto_nome = pygame.font.Font('fonts/FreeSansBold.ttf', self.tam_fonte).render(self.nome, True, (255, 255, 255))
        text_rect = texto_nome.get_rect(center=pos_nome[self.pos_original - 1])
        window.blit(texto_nome, text_rect)


    def display_dinheiro(self, window):
        dinheiro = f'{self.dinheiro:,.0f}'.replace(',', self.sep)
        if self.front:
            text_dinheiro = self.currency + " " + dinheiro
        else:
            text_dinheiro = dinheiro + " " + self.currency
        texto_dinheiro = pygame.font.Font('fonts/Technology.ttf', 60).render(text_dinheiro,
                                                                                       True, (255, 255, 255))
        text_rect = texto_dinheiro.get_rect(center=pos_dinheiro[self.pos_original - 1])
        window.blit(texto_dinheiro, text_rect)


    def bot_responde(self, rodada, alternativas='', resposta_certa=''):
        # Nível 1 - Bot Carla Perez na final
        # 0% para acertar - 100% para chutar
        # Nível 2 - Bot Leigo
        # 20% para acertar - 80% para chutar
        # Nível 3 - Bot Normal
        # 40% para acertar - 60% para chutar
        # Nível 4 - Bot Inteligente
        # 60% para acertar - 40% para chutar
        # Nível 5 - Bot Cacá Rosset na final
        # 80% para acertar - 20% para chutar
        limiar = 10 - 2 * (self.tipo - 1)
        decisao = randint(1, 10)

        if decisao > limiar:
            # Bot acerta
            if rodada < 5:
                resposta = alternativas.index(resposta_certa) + 1
                tempo = uniform(5 + self.tipo * 2, 29)
            else:
                resposta = resposta_certa
                tempo = uniform(10 + self.tipo * 2, 29)
        else:
            # Bot chuta
            if rodada < 5:
                chute = choice(alternativas)
                resposta = alternativas.index(chute) + 1
            else:
                resposta = 0  # 0 indica erro na rodada final
            tempo = uniform(0, 29)

        return resposta, tempo

    def bot_escolhe(self, escolhas, lider, nao_respondeu, nao_respondeu_nunca, rodada):
        if rodada == 4:  # Se estiver na 4ª rodada
            escolhas = [esc for esc in escolhas if esc != self]
            # Desafie o outro obrigatoriamente.
        else:
            for nr in nao_respondeu:  # Quem não respondeu tem mais chances de ser escolhido.
                if nr in escolhas:
                    escolhas.append(nr)
                    if rodada == 1:
                        # Se estivermos na primeira rodada, teremos uma tendência bem maior
                        # a perguntar de quem não respondeu.
                        escolhas.append(nr)
                        escolhas.append(nr)
                        escolhas.append(nr)
                        escolhas.append(nr)
            for nr in nao_respondeu_nunca:
                if rodada > 1:
                    if nr in escolhas:
                        escolhas.append(nr)
                        escolhas.append(nr)
                        escolhas.append(nr)
            if lider is not None and lider != self:  # Se temos um líder e não é o bot desafiante
                escolhas.append(lider)  # Ele terá um peso a mais para ser escolhido. É o líder.
            if self.dinheiro == 0 and lider is not None:  # Se tá sem grana, tem mais tendência a perguntar ao líder!
                escolhas.append(lider)
                if rodada == 1:  # E também de perguntar ao líder se acabou de perder a grana.
                    escolhas.append(lider)
                    escolhas.append(lider)
                    escolhas.append(lider)
        return choice(escolhas)
    
    def bot_para_ou_continua(self, qtd_erradas):
        # Nível 1 - Bot Carla Perez na final
        # 0% para acertar - 100% para chutar
        # Nível 2 - Bot Leigo
        # 20% para acertar - 80% para chutar
        # Nível 3 - Bot Normal
        # 40% para acertar - 60% para chutar
        # Nível 4 - Bot Inteligente
        # 60% para acertar - 40% para chutar
        # Nível 5 - Bot Cacá Rosset na final
        # 80% para acertar - 20% para chutar
        limiar = 9 - 2 * (self.tipo - 1) + qtd_erradas
        decisao = randint(1, 10)

        # Se decisão > limiar, bot continua. Se <= limiar, bot para.
        return decisao > limiar


def mostra_jogadores(window, jogadores):
    for pl in jogadores:
        if not pl.eliminado:
            pl.image.draw(window)
            pl.display_nome(window)
            pl.display_dinheiro(window)


def copy_jogadores(jogadores):
    jogadores_copy = []
    for pl in jogadores:
        jogadores_copy.append(copy(pl))
    return jogadores_copy


def get_leader(jogadores):
    maior_dinheiro = -1
    players_alive = 0
    for pl in jogadores:
        if not pl.eliminado:
            players_alive += 1
            if pl.dinheiro > maior_dinheiro:
                maior_dinheiro = pl.dinheiro
                lider = pl
            elif pl.dinheiro == maior_dinheiro:
                lider = None
    return lider if players_alive != 2 else None


def get_em_risco(jogadores):
    lider = get_leader(jogadores)
    pode_cair = []
    if lider is None:
        for pl in jogadores:
            if not pl.eliminado:
                pode_cair.append(pl)
        return pode_cair
    else:
        for pl in jogadores:
            if pl != lider and not pl.eliminado:
                pode_cair.append(pl)
        return pode_cair


def click_on_player(jogadores, mouse_pos):
    for pl in jogadores:
        # se clicou na imagem
        if pl.image.rect.collidepoint(mouse_pos):
            return pl


def get_escolhas(jogadores, desafiante):
    escolhas = []
    for pl in jogadores:
        if not pl.eliminado:
            if pl != desafiante:
                escolhas.append(pl)
    if len(escolhas) == 1:
        escolhas.append(desafiante)
    return escolhas


def passa_pra_quem(escolhas, s):
    num_escolhas = [pl.pos for pl in escolhas]
    while True:
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                pygame.quit()
            if ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
                chosen = click_on_player(escolhas, pygame.mouse.get_pos())
                if s.check_click():
                    pygame.mixer.pause()
                    return None
                if chosen is not None:
                    if chosen.pos in num_escolhas:
                        return chosen
            if ev.type == pygame.KEYDOWN:
                if ((ev.key == pygame.K_1) or (ev.key == pygame.K_KP1)) and (1 in num_escolhas):
                    return [pl for pl in escolhas if pl.pos == 1][0]
                if ((ev.key == pygame.K_2) or (ev.key == pygame.K_KP2)) and (2 in num_escolhas):
                    return [pl for pl in escolhas if pl.pos == 2][0]
                if ((ev.key == pygame.K_3) or (ev.key == pygame.K_KP3)) and (3 in num_escolhas):
                    return [pl for pl in escolhas if pl.pos == 3][0]
                if ((ev.key == pygame.K_4) or (ev.key == pygame.K_KP4)) and (4 in num_escolhas):
                    return [pl for pl in escolhas if pl.pos == 4][0]
                if ((ev.key == pygame.K_5) or (ev.key == pygame.K_KP5)) and (5 in num_escolhas):
                    return [pl for pl in escolhas if pl.pos == 5][0]
                if ev.key == pygame.K_F11:
                    pygame.mixer.Sound('sons/rr_aplausos1.mp3').play()
                if ev.key == pygame.K_F12:
                    pygame.mixer.Sound('sons/rr_aplausos2.mp3').play()

def click_on_buraco(mouse_pos):
    """
    Retorna o índice do buraco clicado, de 0 a 5.
    Se nenhum buraco foi clicado, retorna None.
    """
    largura = altura = int(154 * get_ratio())
    for i, (x, y) in enumerate(pos_buracos):
        rect = pygame.Rect(x, y, largura, altura)
        if rect.collidepoint(mouse_pos):
            return i
    return None
