import pygame
from display import get_ratio


class Botao:
    def __init__(self, texto, pos_x, pos_y, tam=90, cor=(255, 255, 255), cor_contorno=None, outline=2, align='topright'):
        self.texto = texto
        self.pos_x = int(pos_x * get_ratio())
        self.pos_y = int(pos_y * get_ratio())
        self.tam = int(tam * get_ratio())
        self.cor = cor
        self.cor_contorno = cor_contorno  # None = sem contorno
        self.outline = outline
        self.align = align
        self.fonte = pygame.font.Font('fonts/FreeSansBold.ttf', self.tam)

    def render_texto(self):
        """Renderiza o texto com ou sem contorno"""
        if self.cor_contorno is None:
            return self.fonte.render(self.texto, True, self.cor)

        # Com contorno
        base = self.fonte.render(self.texto, True, self.cor)
        w, h = base.get_size()
        surface = pygame.Surface((w + 2*self.outline, h + 2*self.outline), pygame.SRCALPHA)

        for dx in range(-self.outline, self.outline + 1):
            for dy in range(-self.outline, self.outline + 1):
                if dx != 0 or dy != 0:
                    pos = (self.outline + dx, self.outline + dy)
                    surface.blit(self.fonte.render(self.texto, True, self.cor_contorno), pos)

        surface.blit(base, (self.outline, self.outline))
        return surface

    def show_texto(self, w):
        texto_surface = self.render_texto()

        if self.align == 'topright':
            text_rect = texto_surface.get_rect(topright=(self.pos_x, self.pos_y))
        elif self.align == 'center':
            text_rect = texto_surface.get_rect(center=(self.pos_x, self.pos_y))
        else:
            text_rect = texto_surface.get_rect(topleft=(self.pos_x, self.pos_y))

        w.blit(texto_surface, text_rect)

    def check_click(self):
        texto_surface = self.render_texto()

        if self.align == 'topright':
            text_rect = texto_surface.get_rect(topright=(self.pos_x, self.pos_y))
        elif self.align == 'center':
            text_rect = texto_surface.get_rect(center=(self.pos_x, self.pos_y))
        else:
            text_rect = texto_surface.get_rect(topleft=(self.pos_x, self.pos_y))

        return text_rect.collidepoint(pygame.mouse.get_pos())


class Texto:
    def __init__(self, texto, font, tam, x, y,
                 cor=(255, 255, 255),
                 cor_contorno=None,
                 outline=2):
        self.texto = texto
        self.font = pygame.font.Font('fonts/' + font + '.ttf', int(tam * get_ratio()))
        self.x = x
        self.y = y
        self.cor = cor
        self.cor_contorno = cor_contorno  # None = sem contorno
        self.outline = outline

    def render_texto(self):
        if self.cor_contorno is None:
            return self.font.render(self.texto, True, self.cor)

        # Com contorno
        base = self.font.render(self.texto, True, self.cor)
        w, h = base.get_size()
        surface = pygame.Surface((w + 2 * self.outline, h + 2 * self.outline), pygame.SRCALPHA)

        for dx in range(-self.outline, self.outline + 1):
            for dy in range(-self.outline, self.outline + 1):
                if dx != 0 or dy != 0:
                    pos = (self.outline + dx, self.outline + dy)
                    surface.blit(self.font.render(self.texto, True, self.cor_contorno), pos)

        surface.blit(base, (self.outline, self.outline))
        return surface

    def show_texto(self, w, align='center'):
        texto_surface = self.render_texto()
        x = int(self.x * get_ratio())
        y = int(self.y * get_ratio())

        if align == 'center':
            text_rect = texto_surface.get_rect(center=(x, y))
        elif align == 'topleft':
            text_rect = texto_surface.get_rect(topleft=(x, y))
        else:
            text_rect = texto_surface.get_rect(topright=(x, y))

        w.blit(texto_surface, text_rect)

    def show_texto_cor(self, w, align='center', color='black'):
        """Render alternativo com cor de fundo (background) específica"""
        show = self.font.render(self.texto, True, self.cor, color)
        x = int(self.x * get_ratio())
        y = int(self.y * get_ratio())

        if align == 'center':
            text_rect = show.get_rect(center=(x, y))
        elif align == 'topleft':
            text_rect = show.get_rect(topleft=(x, y))
        else:
            text_rect = show.get_rect(topright=(x, y))

        w.blit(show, text_rect)
