import copy
import os
import logging
import sys
import time

import pygame
from argparse import ArgumentParser
from src import Consts


def parse_args():
    parser = ArgumentParser()
    parser.add_argument("-d",
                        action="store_true",
                        help="with d flag you can run in debug mode")

    tmp = vars(parser.parse_args())
    debug_mode = tmp["d"]

    log = logging.getLogger("app_logger")
    log.setLevel(logging.INFO)

    if debug_mode is True:
        log.setLevel(logging.DEBUG)
        file_handler = logging.FileHandler("../debug.log", "w")
        file_handler.setFormatter(Consts.FORMATTER)
        log.addHandler(file_handler)

    log.info("This is an info message")
    log.debug("This is an debug message")
    log.debug("This is an debug message")


def read_map():
    mat = []
    src_dir = os.path.dirname(__file__)
    map_path = os.path.join(src_dir, '../Config/map')
    fin = open(map_path, "r")

    line = fin.readline()
    protecion_list = []
    pc_pos = (-1, -1)
    player_pos = (-1, -1)
    x = 0
    while line:
        if line[-1] == '\n':
            line = line[:-1]
        mat.append([])
        for y in range(len(line)):
            if line[y] == 'p':
                protecion_list.append((x, y))
            if line[y] == '1':
                player_pos = (x, y)
            if line[y] == '2':
                pc_pos = (x, y)
            mat[-1].append(line[y])
        line = fin.readline()
        x += 1
    # for index in range(len(mat)):
    #     print("".join([str(elem) for elem in mat[index]]))
    fin.close()
    return mat, player_pos, pc_pos, protecion_list


class Joc:
    """
    Clasa care defineste jocul. Se va schimba de la un joc la altul.
    """
    GOL = None
    player1_img = None
    dim_celula = None
    display = None
    ABOMB = None
    IBOMB = None
    SHIELD = None
    PLAYER1 = None
    active_bomb_img = None
    celuleGrid = None
    player2_img = None
    JMIN = None
    JMAX = None
    WALL = '#'
    NR_LINII = None
    NR_COLOANE = None
    scor_maxim = 0

    def __init__(self, matr, NR_LINII=None, NR_COLOANE=None):
        # creez proprietatea ultima_mutare # (l,c)
        self.ultima_mutare = None

        if matr:
            # e data tabla, deci suntem in timpul jocului
            self.matr = matr

        if NR_LINII is not None:
            self.__class__.NR_LINII = NR_LINII
        if NR_COLOANE is not None:
            self.__class__.NR_COLOANE = NR_COLOANE

            # ######## calculare scor maxim ###########
            # sc_randuri = (NR_COLOANE - 3) * NR_LINII
            # sc_coloane = (NR_LINII - 3) * NR_COLOANE
            # sc_diagonale = (NR_LINII - 3) * (NR_COLOANE - 3) * 2
            # self.__class__.scor_maxim = sc_randuri + sc_coloane + sc_diagonale

    def deseneaza_grid(self, index=None, click=0):  # tabla de exemplu este ["#","x","#","0",......] click-ul stang
        for ind in range(self.__class__.NR_COLOANE * self.__class__.NR_LINII):
            linie = ind // self.__class__.NR_COLOANE  # // inseamna div
            coloana = ind % self.__class__.NR_COLOANE
            background_cell_color = Consts.white

            if click == 0:
                if ind == index:
                    self.player1_img.set_alpha(500)  # make bigger opacity
                else:
                    self.player1_img.set_alpha(80)
            if click == 1:
                if ind == index:
                    self.player1_img.set_alpha(500)
                    background_cell_color = Consts.red
                else:
                    background_cell_color = Consts.white
            coord_cell = (
                coloana * (self.__class__.dim_celula + 1), Header.height + linie * (self.__class__.dim_celula + 1))
            pygame.draw.rect(self.__class__.display, background_cell_color, self.__class__.celuleGrid[ind])
            if self.matr[linie][coloana] == Joc.PLAYER1:
                self.__class__.display.blit(self.__class__.player1_img, coord_cell)
            elif self.matr[linie][coloana] == Joc.PLAYER2:
                self.__class__.display.blit(self.__class__.player2_img, coord_cell)
            elif self.matr[linie][coloana] == Joc.WALL:
                self.__class__.display.blit(self.__class__.wall_img, coord_cell)
            elif self.matr[linie][coloana] == Joc.IBOMB:
                self.__class__.display.blit(self.__class__.inactive_bomb_img, coord_cell)
            elif self.matr[linie][coloana] == Joc.ABOMB:
                self.__class__.display.blit(self.__class__.active_bomb_img, coord_cell)
            elif self.matr[linie][coloana] == Joc.SHIELD:
                self.__class__.display.blit(self.__class__.shield_img, coord_cell)

        # pygame.draw.rect(self.__class__.display, Consts.grey, Footer.grid_cells[0])
        # self.__class__.display.blit(Footer.text, Footer.grid_cells[0])
        pygame.display.update()

    def update_header(self):
        pygame.draw.rect(self.__class__.display, Consts.footer_background_color, Header.grid_cells[0])
        self.__class__.display.blit(Header.text, Header.text_rect)
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
        cls.player2_img = pygame.image.load(images_dir + 'player2_tmp.png')
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

    def parcurgere(self, directie):
        um = self.ultima_mutare  # (l,c)
        culoare = self.matr[um[0]][um[1]]
        nr_mutari = 0
        while True:
            um = (um[0] + directie[0], um[1] + directie[1])
            if not 0 <= um[0] < self.__class__.NR_LINII or not 0 <= um[1] < self.__class__.NR_COLOANE:
                break
            if not self.matr[um[0]][um[1]] == culoare:
                break
            nr_mutari += 1
        return nr_mutari

    def final(self):
        if not self.ultima_mutare:  # daca e inainte de prima mutare
            return False
        directii = [[(0, 1), (0, -1)], [(1, 1), (-1, -1)], [(1, -1), (-1, 1)], [(1, 0), (-1, 0)]]
        um = self.ultima_mutare
        rez = False
        for per_dir in directii:
            len_culoare = self.parcurgere(per_dir[0]) + self.parcurgere(per_dir[1]) + 1  # +1 pt chiar ultima mutare
            if len_culoare >= 4:
                rez = self.matr[um[0]][um[1]]

        if (rez):
            return rez
        elif all(self.__class__.GOL not in x for x in self.matr):
            return 'remiza'
        else:
            return False

    def mutari(self, jucator):
        l_mutari = []
        for j in range(self.__class__.NR_COLOANE):
            last_poz = None
            if self.matr[0][j] != self.__class__.GOL:
                continue
            for i in range(self.__class__.NR_LINII):
                if self.matr[i][j] != self.__class__.GOL:
                    last_poz = (i - 1, j)
                    break
            if last_poz is None:
                last_poz = (self.__class__.NR_LINII - 1, j)
            matr_tabla_noua = copy.deepcopy(self.matr)
            matr_tabla_noua[last_poz[0]][last_poz[1]] = jucator
            jn = Joc(matr_tabla_noua)
            jn.ultima_mutare = (last_poz[0], last_poz[1])
            l_mutari.append(jn)
        return l_mutari

    # linie deschisa inseamna linie pe care jucatorul mai poate forma o configuratie castigatoare
    # practic e o linie fara simboluri ale jucatorului opus
    def linie_deschisa(self, lista, jucator):
        jo = self.jucator_opus(jucator)
        # verific daca pe linia data nu am simbolul jucatorului l
        if not jo in lista:
            # return 1
            return lista.count(jucator)
        return 0

    def linii_deschise(self, jucator):

        linii = 0
        for i in range(self.__class__.NR_LINII):
            for j in range(self.__class__.NR_COLOANE - 3):
                linii += self.linie_deschisa(self.matr[i][j:j + 4], jucator)

        for j in range(self.__class__.NR_COLOANE):
            for i in range(self.__class__.NR_LINII - 3):
                linii += self.linie_deschisa([self.matr[k][j] for k in range(i, i + 4)], jucator)

        # \
        for i in range(self.__class__.NR_LINII - 3):
            for j in range(self.__class__.NR_COLOANE - 3):
                linii += self.linie_deschisa([self.matr[i + k][j + k] for k in range(0, 4)], jucator)

        # /
        for i in range(self.__class__.NR_LINII - 3):
            for j in range(3, self.__class__.NR_COLOANE):
                linii += self.linie_deschisa([self.matr[i + k][j - k] for k in range(0, 4)], jucator)

        return linii

    def estimeaza_scor(self, adancime):
        t_final = self.final()
        # if (adancime==0):
        if t_final == self.__class__.JMAX:
            return self.__class__.scor_maxim + adancime
        elif t_final == self.__class__.JMIN:
            return -self.__class__.scor_maxim - adancime
        elif t_final == 'remiza':
            return 0
        else:
            return (self.linii_deschise(self.__class__.JMAX) - self.linii_deschise(self.__class__.JMIN))

    def sirAfisare(self):
        sir = "  |"
        sir += " ".join([str(i) for i in range(self.NR_COLOANE)]) + "\n"
        sir += "-" * (self.NR_COLOANE + 1) * 2 + "\n"
        sir += "\n".join([str(i) + " |" + " ".join([str(x) for x in self.matr[i]]) for i in range(len(self.matr))])
        return sir

    def __str__(self):
        return self.sirAfisare()

    def __repr__(self):
        return self.sirAfisare()


class Stare:
    """
    Clasa folosita de algoritmii minimax si alpha-beta
    Are ca proprietate tabla de joc
    Functioneaza cu conditia ca in cadrul clasei Joc sa fie definiti JMIN si JMAX (cei doi jucatori posibili)
    De asemenea cere ca in clasa Joc sa fie definita si o metoda numita mutari() care ofera lista cu configuratiile posibile in urma mutarii unui jucator
    """

    def __init__(self, tabla_joc, j_curent, adancime, parinte=None, scor=None):
        self.end_zone = []
        self.tabla_joc = tabla_joc
        self.j_curent = j_curent

        # adancimea in arborele de stari
        self.adancime = adancime

        # scorul starii (daca e finala) sau al celei mai bune stari-fiice (pentru jucatorul curent)
        self.scor = scor

        # lista de mutari posibile din starea curenta
        self.mutari_posibile = []

        # cea mai buna mutare din lista de mutari posibile pentru jucatorul curent
        self.stare_aleasa = None

    def mutari(self):
        l_mutari = self.tabla_joc.mutari(self.j_curent)
        juc_opus = Joc.jucator_opus(self.j_curent)
        l_stari_mutari = [Stare(mutare, juc_opus, self.adancime - 1, parinte=self) for mutare in l_mutari]

        return l_stari_mutari

    def __str__(self):
        sir = str(self.tabla_joc) + "(Juc curent:" + self.j_curent + ")\n"
        return sir

    def __repr__(self):
        sir = str(self.tabla_joc) + "(Juc curent:" + self.j_curent + ")\n"
        return sir


def checkValidMove(line_player, column_player, new_line, new_column):
    if abs(line_player - new_line) + abs(column_player - new_column) <= 1:
        return True
    else:
        return False


class Player:
    # sign = None
    # list_of_bombs = None
    # nums_of_shiels = None
    # placing_bomb_time = None
    def __init__(self, sign, k):
        self.sign = sign
        self.placing_bomb_time = k
        self.list_of_bombs = []
        self.nums_of_shiels = 0

    def __str__(self):
        print(self.list_of_bombs)
        return f"The sign use for playe {self.sign}, number of shields {self.nums_of_shiels}, placing bomb time {self.placing_bomb_time}"


def bomb_explode(stare: Stare, line_bomb, column_bomb):
    up = [line_bomb - 1, column_bomb]
    cell_explode = []
    while stare.tabla_joc.matr[up[0]][up[1]] != Joc.WALL:
        if up[0] > 0:
            cell_explode.append((up[0], up[1]))
            up[0] -= 1
        else:
            break

    down = [line_bomb + 1, column_bomb]
    while stare.tabla_joc.matr[down[0]][down[1]] != Joc.WALL:
        if down[0] < len(stare.tabla_joc.matr) - 1:
            cell_explode.append((down[0], down[1]))
            down[0] += 1
        else:
            break

    right = [line_bomb, column_bomb + 1]
    while stare.tabla_joc.matr[right[0]][right[1]] != Joc.WALL:
        if right[1] < len(stare.tabla_joc.matr[-1]) - 1:
            cell_explode.append((right[0], right[1]))
            right[1] += 1
        else:
            break

    left = [line_bomb, column_bomb - 1]
    while stare.tabla_joc.matr[left[0]][left[1]] != Joc.WALL:
        if left[1] > 0:
            cell_explode.append((left[0], left[1]))
            left[1] -= 1
        else:
            break
    set2 = set(cell_explode).union(set(stare.end_zone))
    stare.end_zone = list(set2)


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


def main():
    parse_args()
    mat, player_pos, pc_pos, protection_list = read_map()
    num_of_colons = len(mat[-1])
    num_of_lines = len(mat)
    wide = 50
    bottom_left = (0, num_of_lines * (wide + 1) - 1)
    Header(num_of_colons * (wide + 1) - 1, 100)
    ecran = pygame.display.set_mode(
        size=(num_of_colons * (wide + 1) - 1, num_of_lines * (wide + 1) - 1 + Header.height))  # N *w+ N-1= N*(w+1)-1
    pygame.init()
    pygame.display.set_caption("Bomberman")

    Joc.initializeaza(ecran, NR_LINII=num_of_lines, NR_COLOANE=num_of_colons, dim_celula=wide)

    current_table = Joc(mat, NR_LINII=num_of_lines, NR_COLOANE=num_of_colons)

    k = 1
    # System variables
    Joc.PLAYER1 = '1'
    Joc.PLAYER2 = '2'
    Joc.GOL = ' '
    Joc.SHIELD = 'p'
    Joc.IBOMB = 'b'
    Joc.ABOMB = 'B'
    Joc.TIME_AUTO_BOMB = k
    # End


    Joc.JMAX = Player(Joc.PLAYER2, k)
    Joc.JMIN = Player(Joc.PLAYER1, k)

    stare_curenta = Stare(current_table, '1', 2)
    stare_curenta.current_player = Joc.JMIN
    current_table.deseneaza_grid()
    marked = False
    bomb_down = False
    player1_win = 0  # -1 win the computer 0 tie 1 win the player
    player2_win = 0
    while True and player1_win == 0 and player2_win == 0:

        if stare_curenta.current_player == Joc.JMIN:
            msg = "Your turn"
            Header.change_message(msg)
            # stare_curenta.tabla_joc.deseneaza_grid()
            stare_curenta.tabla_joc.update_header()
            for event in pygame.event.get():
                msg = "Your turn"
                Header.change_message(msg)
                # stare_curenta.tabla_joc.deseneaza_grid()
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                elif event.type == pygame.MOUSEBUTTONDOWN:
                    pos = pygame.mouse.get_pos()  # coordonatele cursorului la momentul clickului
                    mouse_button = pygame.mouse.get_pressed()
                    # print (mouse_button)
                    for np in range(len(Joc.celuleGrid)):

                        if Joc.celuleGrid[np].collidepoint(pos):
                            # print(Joc.JMIN)
                            linie = np // Joc.NR_COLOANE
                            coloana = np % Joc.NR_COLOANE

                            # mark the player to move press left click
                            if stare_curenta.tabla_joc.matr[linie][coloana] == Joc.JMIN.sign and mouse_button[0] is True:
                                if marked and marked[0] == linie and marked[1] == coloana:
                                    marked = False
                                    stare_curenta.tabla_joc.deseneaza_grid()
                                else:
                                    marked = (linie, coloana)
                                    stare_curenta.tabla_joc.deseneaza_grid(np)

                            # right click to put a bomb down
                            if stare_curenta.tabla_joc.matr[linie][coloana] == Joc.JMIN.sign and mouse_button[2] is True:
                                if marked and marked[0] == linie and marked[1] == coloana:
                                    marked = False
                                    bomb_down = False
                                    stare_curenta.tabla_joc.deseneaza_grid(-1, 1)
                                else:
                                    bomb_down = True
                                    marked = (linie, coloana)
                                    stare_curenta.tabla_joc.deseneaza_grid(np, 1)

                            if (stare_curenta.tabla_joc.matr[linie][coloana] == Joc.GOL or \
                                stare_curenta.tabla_joc.matr[linie][coloana] == Joc.SHIELD) and marked and \
                                    checkValidMove(marked[0], marked[1], linie, coloana):
                                # automatic placement bomb or you want to do it or just let an empty space behind him
                                if Joc.JMIN.placing_bomb_time == 0 or bomb_down is True:
                                    stare_curenta.tabla_joc.matr[marked[0]][marked[1]] = Joc.IBOMB
                                    Joc.JMIN.list_of_bombs.append(marked)
                                    Joc.JMIN.placing_bomb_time = Joc.TIME_AUTO_BOMB + 1
                                    bomb_down = False
                                else:
                                    stare_curenta.tabla_joc.matr[marked[0]][marked[1]] = Joc.GOL
                                marked = False
                                if (linie, coloana) in stare_curenta.end_zone:
                                    player1_win = -1

                                stare_curenta.tabla_joc.matr[linie][coloana] = Joc.JMIN.sign
                                stare_curenta.tabla_joc.deseneaza_grid()
                                if stare_curenta.tabla_joc.matr[linie][coloana] == Joc.SHIELD:
                                    Joc.JMIN.nums_of_shiels += 1
                                Joc.JMIN.placing_bomb_time -= 1
                                if Joc.JMIN.placing_bomb_time < 0:
                                    Joc.JMIN.placing_bomb_time = k

                                stare_curenta.current_player = Joc.jucator_opus(stare_curenta.current_player)

                            if stare_curenta.tabla_joc.matr[linie][coloana] == Joc.IBOMB:
                                if (linie, coloana) in Joc.JMIN.list_of_bombs:
                                    stare_curenta.tabla_joc.matr[linie][coloana] = Joc.ABOMB
                                    stare_curenta.tabla_joc.deseneaza_grid()
                                    bomb_explode(stare_curenta, linie, coloana)
                                    # print(stare_curenta.end_zone)

                            # if stare_curenta.tabla_joc.matr[linie][coloana] == Joc.ABOMB:
                            #     if (linie, coloana) in Joc.JMIN.list_of_bombs:
                            #         stare_curenta.tabla_joc.matr[linie][coloana] = Joc.IBOMB
        else:
            print("This is the computer round")
            footer_message = "Computer turn"
            Header.change_message(footer_message)
            stare_curenta.tabla_joc.update_header()
            time.sleep(0.5)
            stare_curenta.current_player = Joc.jucator_opus(stare_curenta.current_player)

    message = "You win!" if player2_win == -1 else "You lose!"

    while True:
        for event in pygame.event.get():
            footer_message = message
            Header.change_message(footer_message)
            stare_curenta.tabla_joc.update_header()
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()


if __name__ == "__main__":
    main()
