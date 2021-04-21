from UserInterface import Joc


class Stare:
    """
    Clasa folosita de algoritmii minimax si alpha-beta
    Are ca proprietate tabla de joc
    Functioneaza cu conditia ca in cadrul clasei Joc sa fie definiti JMIN si JMAX (cei doi jucatori posibili)
    De asemenea cere ca in clasa Joc sa fie definita si o metoda numita mutari() care ofera lista cu configuratiile posibile in urma mutarii unui jucator
    """
    NR_LINII = None
    NR_COLOANE = None

    def __init__(self, mat, j_curent, adancime, parinte=None, scor=None):
        self.end_zone = []
        self.matr = mat
        self.__class__.NR_LINII = len(mat)
        self.__class__.NR_COLOANE = len(mat[0])
        self.current_player = j_curent

        # adancimea in arborele de stari
        self.adancime = adancime

        # scorul starii (daca e finala) sau al celei mai bune stari-fiice (pentru jucatorul curent)
        self.scor = scor

        # lista de mutari posibile din starea curenta
        self.mutari_posibile = []

        # cea mai buna mutare din lista de mutari posibile pentru jucatorul curent
        self.stare_aleasa = None

    def mutari(self):
        l_mutari = self.tabla_joc.mutari(self.current_player)
        juc_opus = Joc.jucator_opus(self.current_player)
        l_stari_mutari = [Stare(mutare, juc_opus, self.adancime - 1, parinte=self) for mutare in l_mutari]

        return l_stari_mutari

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


class Player:

    def __init__(self, sign, k):
        self.sign = sign
        self.bomb_auto_placing = k
        self.list_of_bombs = []
        self.nums_of_shields = 0
        self.inactive_bomb = None  # it can be a single inactive bomb

    def __str__(self):
        print(self.list_of_bombs)
        return f"The sign use for player {self.sign}, number of shields {self.nums_of_shields}, placing bomb time {self.bomb_auto_placing} "
