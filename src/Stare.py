import copy

from UserInterface import Joc


class Player:

    def __init__(self, sign, k, pos):
        self.sign = sign
        self.bomb_auto_placing = k
        self.list_of_bombs = []
        self.nums_of_shields = 0
        self.inactive_bomb = None  # it can be a single inactive bomb
        self.lost = False
        self.pos = pos

    def __str__(self):
        print(self.list_of_bombs)
        return f"The sign use for player {self.sign}, number of shields {self.nums_of_shields}, placing bomb time {self.bomb_auto_placing} "


def bomb_explode(stare, line_bomb, column_bomb, time=0):  # time = 0 means now, time = 1 means next step will explode
    up = [line_bomb - 1, column_bomb]
    cell_explode = []
    while stare.matr[up[0]][up[1]] != Joc.WALL:
        if up[0] > 0:
            cell_explode.append((up[0], up[1]))
            up[0] -= 1
        else:
            break

    down = [line_bomb + 1, column_bomb]
    while stare.matr[down[0]][down[1]] != Joc.WALL:
        if down[0] < len(stare.matr) - 1:
            cell_explode.append((down[0], down[1]))
            down[0] += 1
        else:
            break

    right = [line_bomb, column_bomb + 1]
    while stare.matr[right[0]][right[1]] != Joc.WALL:
        if right[1] < len(stare.matr[-1]) - 1:
            cell_explode.append((right[0], right[1]))
            right[1] += 1
        else:
            break

    left = [line_bomb, column_bomb - 1]
    while stare.matr[left[0]][left[1]] != Joc.WALL:
        if left[1] > 0:
            cell_explode.append((left[0], left[1]))
            left[1] -= 1
        else:
            break

    set2 = set(stare.end_zone).union(set(cell_explode))
    stare.end_zone = list(set2)



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
        self.next_step_explode = []
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

    def check_final(self):
        player = self.current_player
        if player.pos in self.end_zone:
            if player.nums_of_shields > 0:
                player.nums_of_shields -= 1
            else:
                self.JMIN.lost = True
                return True
        return False

    def has_valid_moves(self, linie, coloana):
        directions = [(0, +1), (0, -1), (1, 0), (-1, 0)]
        has_moves = False
        for elem in directions:
            if self.is_valid_move(self.matr, (linie, coloana), elem):
                has_moves = True
        return has_moves

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

    def mutari(self, player_sign):
        l_stari = []
        directions = [(0, +1), (0, -1), (1, 0), (-1, 0)]

        player_pos = self.current_player.pos
        for elem in directions:
            stare_cpy = copy.deepcopy(self)
            if self.is_valid_move(stare_cpy.matr, player_pos, elem):  # default movements without bombing

                if stare_cpy.current_player.bomb_auto_placing > 0:
                    stare_cpy.matr[player_pos[0]][player_pos[1]] = Joc.GOL
                    stare_cpy.matr[player_pos[0] + elem[0]][player_pos[1] + elem[1]] = player_sign
                    stare_cpy.current_player.pos = (player_pos[0] + elem[0], player_pos[1] + elem[1])
                    stare_cpy.current_player.bomb_auto_placing -= 1
                    l_stari.append(stare_cpy)

                    # add a version with bomb behind
                    stare_cpy_with_bomb = copy.deepcopy(stare_cpy)
                    stare_cpy_with_bomb.matr[player_pos[0]][player_pos[1]] = Joc.IBOMB
                    if stare_cpy_with_bomb.current_player.inactive_bomb is not None:
                        stare_cpy_with_bomb.matr[stare_cpy.current_player.inactive_bomb[0]][
                            stare_cpy_with_bomb.current_player.inactive_bomb[1]] = Joc.ABOMB
                        bomb_explode(stare_cpy_with_bomb, stare_cpy.current_player.inactive_bomb[0],
                                     stare_cpy.current_player.inactive_bomb[1], 1)
                    stare_cpy_with_bomb.current_player.inactive_bomb = (player_pos[0], player_pos[1])
                    stare_cpy_with_bomb.current_player.bomb_auto_placing = Joc.TIME_AUTO_BOMB
                    l_stari.append(stare_cpy_with_bomb)
                else:
                    stare_cpy.matr[player_pos[0]][player_pos[1]] = Joc.IBOMB
                    stare_cpy.matr[player_pos[0] + elem[0]][player_pos[1] + elem[1]] = player_sign
                    stare_cpy.current_player.pos = (player_pos[0] + elem[0], player_pos[1] + elem[1])
                    if stare_cpy.current_player.inactive_bomb is not None:
                        stare_cpy.matr[stare_cpy.current_player.inactive_bomb[0]][
                            stare_cpy.current_player.inactive_bomb[1]] = Joc.ABOMB
                        bomb_explode(stare_cpy, stare_cpy.current_player.inactive_bomb[0],
                                     stare_cpy.current_player.inactive_bomb[1], 1)
                        # print(
                        #     f"Computer end-zones position bomb: ({stare_cpy.current_player.inactive_bomb[0]}, {stare_cpy.current_player.inactive_bomb[1]})")
                        # print(stare_cpy.end_zone)
                    stare_cpy.current_player.inactive_bomb = (player_pos[0], player_pos[1])
                    stare_cpy.current_player.bomb_auto_placing = Joc.TIME_AUTO_BOMB
                    l_stari.append(stare_cpy)

        # if self.current_player.inactive_bomb is not None:
        #     stare_cpy = copy.deepcopy(self)
        #     stare_cpy.matr[stare_cpy.current_player.inactive_bomb[0]][stare_cpy.current_player.inactive_bomb[1]] = Joc.ABOMB
        #     bomb_explode(stare_cpy, stare_cpy.current_player.inactive_bomb[0], stare_cpy.current_player.inactive_bomb[1])
        #     stare_cpy.current_player.inactive_bomb = None
        #     l_stari.append(stare_cpy)
        self.mutari_posibile = l_stari

    # linie deschisa inseamna linie pe care jucatorul mai poate forma o configuratie castigatoare
    # practic e o linie fara simboluri ale jucatorului opus
    def estimeaza_scor(self, adancime):
        t_final = self.check_final()
        # if (adancime==0):
        if t_final == 2:  # jucatorul a pierdut
            return 100
        elif t_final == 1:  # calculatorul a pierdut
            return -100
        elif t_final == 0:  # este remiza
            return 0
        else:
            return self.all_valid_spaces(self.JMAX)

    def all_valid_spaces(self, player):
        pos_player = player.pos
        directions = [(0, -1), (-1, 0), (1, 0), (0, 1)]
        tail = [pos_player]
        was_in_tail = [pos_player]
        num_of_free_spaces = 0
        while tail:
            for direction in directions:
                new_pos_x = tail[0][0] + direction[0]
                new_pos_y = tail[0][1] + direction[1]
                if (self.matr[new_pos_x][new_pos_y] == Joc.GOL or self.matr[new_pos_x][new_pos_y] == Joc.SHIELD )and (new_pos_x, new_pos_y) not in self.end_zone and (new_pos_x, new_pos_y) not in was_in_tail:
                    tail.append((new_pos_x, new_pos_y))
                    num_of_free_spaces += 1
                    was_in_tail.append((new_pos_x, new_pos_y))
                    # if num_of_free_spaces > 200:
                    #     print(num_of_free_spaces)
                    #     return 100
                    # if self.matr[new_pos_x][new_pos_y] == Joc.SHIELD:
                    #     num_of_free_spaces += 2

            tail.pop(0)
        print(num_of_free_spaces)

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
