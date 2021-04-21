import copy

import pygame
import os
import Consts


class Header:
    text_rect = None
    height = None
    width = None
    grid_cells = None
    font = None
    text = None

    def __init__(self, width, height):
        self.__class__.width = width
        self.__class__.height = height
        self.__class__.grid_cells = []
        pygame.font.init()
        self.__class__.font = pygame.font.SysFont(name='Arial', size=68)
        patr = pygame.Rect((0, 0), (self.__class__.width, self.__class__.height))  # top left corner
        self.__class__.grid_cells.append(patr)
        self.__class__.text = self.__class__.font.render("InitMessage", True, Consts.footer_text_color,
                                                         Consts.footer_background_color)
        self.__class__.text = self.__class__.font.render("Init Message", True, Consts.footer_text_color)
        self.__class__.text_rect = self.__class__.text.get_rect(
            center=(self.__class__.width // 2, self.__class__.height // 2))

    @classmethod
    def change_message(cls, message):
        cls.text = cls.font.render(message, True, Consts.footer_text_color, Consts.footer_background_color)


class Joc:
    """
    Clasa care defineste jocul. Se va schimba de la un joc la altul.
    """
    TIME_AUTO_BOMB = None
    display = None
    JMIN = None
    JMAX = None
    celuleGrid = None
    dim_celula = None

    # constants for game (game variables)
    PLAYER2 = None
    GOL = None
    WALL = None
    ABOMB = None
    IBOMB = None
    SHIELD = None
    PLAYER1 = None

    player1_img = None
    player2_img = None
    wall_img = None
    shield_img = None
    active_bomb_img = None
    inactive_bomb_img = None

    def __init__(self, NR_LINII=None, NR_COLOANE=None):
        if NR_LINII is not None:
            self.__class__.NR_LINII = NR_LINII
        if NR_COLOANE is not None:
            self.__class__.NR_COLOANE = NR_COLOANE

        # ######## calculare scor maxim ###########
        # sc_randuri = (NR_COLOANE - 3) * NR_LINII
        # sc_coloane = (NR_LINII - 3) * NR_COLOANE
        # sc_diagonale = (NR_LINII - 3) * (NR_COLOANE - 3) * 2
        # self.__class__.scor_maxim = sc_randuri + sc_coloane + sc_diagonale

    @classmethod
    def deseneaza_grid(cls, matr, index=None, click=0):  # tabla de exemplu este ["#","x","#","0",......] click-ul stang
        NR_COLOANE = len(matr[0])
        NR_LINII = len(matr)

        for ind in range(NR_COLOANE * NR_LINII):
            linie = ind // NR_COLOANE  # // inseamna div
            coloana = ind % NR_COLOANE
            background_cell_color = Consts.white

            if click == 0:
                if ind == index:
                    cls.player1_img.set_alpha(500)  # make bigger opacity
                else:
                    cls.player1_img.set_alpha(80)
            if click == 1:
                if ind == index:
                    cls.player1_img.set_alpha(500)
                    background_cell_color = Consts.red
                else:
                    background_cell_color = Consts.white
            cell_coord = (
                coloana * (cls.dim_celula + 1), Header.height + linie * (cls.dim_celula + 1))
            pygame.draw.rect(cls.display, background_cell_color, cls.celuleGrid[ind])
            if matr[linie][coloana] == Joc.PLAYER1:
                cls.display.blit(cls.player1_img, cell_coord)
            elif matr[linie][coloana] == Joc.PLAYER2:
                cls.display.blit(cls.player2_img, cell_coord)
            elif matr[linie][coloana] == Joc.WALL:
                cls.display.blit(cls.wall_img, cell_coord)
            elif matr[linie][coloana] == Joc.IBOMB:
                cls.display.blit(cls.inactive_bomb_img, cell_coord)
            elif matr[linie][coloana] == Joc.ABOMB:
                cls.display.blit(cls.active_bomb_img, cell_coord)
            elif matr[linie][coloana] == Joc.SHIELD:
                cls.display.blit(cls.shield_img, cell_coord)

        pygame.display.update()

    @classmethod
    def update_header(cls, message):
        Header.change_message(message)
        pygame.draw.rect(cls.display, Consts.footer_background_color, Header.grid_cells[0])
        cls.display.blit(Header.text, Header.text_rect)
        pygame.display.update()

    @classmethod
    def jucator_opus(cls, jucator):
        return cls.JMAX if jucator == cls.JMIN else cls.JMIN

    @classmethod
    def initializeaza(cls, display, NR_LINII=6, NR_COLOANE=7, dim_celula=100):
        cls.display = display
        cls.dim_celula = dim_celula
        images_dir = os.path.join(os.path.dirname(__file__), "../Images/")
        cls.player1_img = pygame.image.load(images_dir + 'player1.png')
        cls.player1_img = pygame.transform.scale(cls.player1_img, (dim_celula, dim_celula))
        cls.player2_img = pygame.image.load(images_dir + 'player2.png')
        cls.player2_img = pygame.transform.scale(cls.player2_img, (dim_celula, dim_celula))
        cls.wall_img = pygame.image.load(images_dir + 'wall.jpeg')
        cls.wall_img = pygame.transform.scale(cls.wall_img, (dim_celula, dim_celula))
        cls.active_bomb_img = pygame.image.load(images_dir + 'Active_bomb.jpeg')
        cls.active_bomb_img = pygame.transform.scale(cls.active_bomb_img, (dim_celula, dim_celula))
        cls.inactive_bomb_img = pygame.image.load(images_dir + 'Inactive_bomb.jpeg')
        cls.inactive_bomb_img = pygame.transform.scale(cls.inactive_bomb_img, (dim_celula, dim_celula))
        cls.shield_img = pygame.image.load(images_dir + 'shield.png')
        cls.shield_img = pygame.transform.scale(cls.shield_img, (dim_celula, dim_celula))

        cls.celuleGrid = []  # este lista cu patratelele din grid
        for linie in range(NR_LINII):
            for coloana in range(NR_COLOANE):
                patr = pygame.Rect(coloana * (dim_celula + 1), Header.height + linie * (dim_celula + 1), dim_celula,
                                   dim_celula)
                cls.celuleGrid.append(patr)
