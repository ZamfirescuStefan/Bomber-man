import copy

from UserInterface import Joc


class Player:

    def __init__(self, sign, k):
        self.sign = sign
        self.bomb_auto_placing = k
        self.list_of_bombs = []
        self.nums_of_shields = 0
        self.inactive_bomb = None  # it can be a single inactive bomb
        self.lost = False

    def __str__(self):
        print(self.list_of_bombs)
        return f"The sign use for player {self.sign}, number of shields {self.nums_of_shields}, placing bomb time {self.bomb_auto_placing} "


class Stare:
    """
    Clasa folosita de algoritmii minimax si alpha-beta
    Are ca proprietate tabla de joc
    Functioneaza cu conditia ca in cadrul clasei Joc sa fie definiti JMIN si JMAX (cei doi jucatori posibili)
    De asemenea cere ca in clasa Joc sa fie definita si o metoda numita mutari() care ofera lista cu configuratiile posibile in urma mutarii unui jucator
    """
    NR_LINII = None
    NR_COLOANE = None

    def __init__(self, mat, j_curent, JMIN, JMAX, adancime, parinte=None, scor=None):
        self.end_zone = []
        self.matr = mat
        self.__class__.NR_LINII = len(mat)
        self.__class__.NR_COLOANE = len(mat[0])
        self.current_player = j_curent
        self.JMIN = JMIN
        self.JMAX = JMAX
        # adancimea in arborele de stari
        self.adancime = adancime

        # scorul starii (daca e finala) sau al celei mai bune stari-fiice (pentru jucatorul curent)
        self.scor = scor

        # lista de mutari posibile din starea curenta
        self.mutari_posibile = []

        # cea mai buna mutare din lista de mutari posibile pentru jucatorul curent
        self.stare_aleasa = None

    # def mutari(self):
    #     l_mutari = self.tabla_joc.mutari(self.current_player)
    #     juc_opus = Joc.jucator_opus(self.current_player)
    #     l_stari_mutari = [Stare(mutare, juc_opus, self.adancime - 1, parinte=self) for mutare in l_mutari]
    #
        # return l_stari_mutari

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

    def jucator_opus(self, jucator):
        self.current_player = self.JMAX if self.current_player == self.JMIN else self.JMIN
        # return self.JMAX if jucator == self.JMIN else self.JMIN

    @classmethod
    def checkValidMove(cls, line_player, column_player, new_line, new_column):
        if abs(line_player - new_line) + abs(column_player - new_column) <= 1:
            return True
        else:
            return False

    def is_valid_move(self, mat, pos, direction):
        new_x, new_y = (pos[0] + direction[0], pos[1] + direction[1])
        invalid_character = [Joc.WALL, Joc.ABOMB, Joc.IBOMB, Joc.PLAYER1, Joc.PLAYER2]

        if mat[new_x][new_y] not in invalid_character:
            return True
        else:
            return False

    def mutari(self, jucator):
        l_mutari = []
        directions = [(0, +1), (0, -1), (1, 0), (-1, 0)]
        player_pos = (0, 0)

        for index in range(len(self.matr)):
            for index2 in range(len(self.matr[0])):
                if self.matr[index][index2] == jucator:
                    player_pos = (index, index2)
        if player_pos == (0, 0):
            print("This map doesn't have this player sign")
            exit()

        jucator_cpy = copy.deepcopy(self.current_player)

        for elem in directions:
            matr_cpy = copy.deepcopy(self.matr)
            if self.is_valid_move(matr_cpy, player_pos, elem):
                matr_cpy[player_pos[0]][player_pos[1]] = Joc.GOL
                matr_cpy[player_pos[0] + elem[0]][player_pos[1] + elem[1]] = jucator
                l_mutari.append(matr_cpy)
                if jucator_cpy.bomb_auto_placing == 0:
                    matr_cpy[player_pos[0]][player_pos[1]] = Joc.IBOMB
                    if jucator_cpy.inactive_bomb is not None:
                        matr_cpy[jucator_cpy.inactive_bomb[0]][jucator_cpy.inactive_bomb[1]] = Joc.ABOMB
                    jucator_cpy.inactive_bomb = (player_pos[0], player_pos[1])
                    l_mutari.append(matr_cpy)

        l_mutari_cpy = copy.deepcopy(l_mutari)
        for mats in l_mutari_cpy:
            matr_cpy = copy.deepcopy(mats)
            if jucator_cpy.inactive_bomb is not None:
                matr_cpy[jucator_cpy.inactive_bomb[0]][jucator_cpy.inactive_bomb[1]] = Joc.ABOMB
            matr_cpy[player_pos[0]][player_pos[1]] = Joc.IBOMB
            jucator_cpy.inactive_bomb = (player_pos[0], player_pos[1])
            l_mutari.append(mats)

        matr_cpy = copy.deepcopy(self.matr)
        if jucator_cpy.inactive_bomb is not None:
            matr_cpy[jucator_cpy.inactive_bomb[0]][jucator_cpy.inactive_bomb[1]] = Joc.ABOMB

        self.mutari_posibile = l_mutari

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
            return self.linii_deschise(self.__class__.JMAX) - self.linii_deschise(self.__class__.JMIN)

    def sirAfisare(self):
        sir = "  |"
        sir += " ".join([str(i) for i in range(self.NR_COLOANE)]) + "\n"
        sir += "-" * (self.NR_COLOANE + 1) * 2 + "\n"
        sir += "\n".join([str(i) + " |" + " ".join([str(x) for x in self.matr[i]]) for i in range(len(self.matr))])
        return sir

    def __str__(self):
        sir = str(self.tabla_joc) + "(Juc curent:" + self.current_player + ")\n"
        return sir

    def __repr__(self):
        sir = str(self.tabla_joc) + "(Juc curent:" + self.current_player + ")\n"
        return sir
