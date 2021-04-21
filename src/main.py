import os
import logging
import sys
import time
import pygame
from argparse import ArgumentParser

from UserInterface import Joc, Header
from Stare import Stare, Player
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

    fin.close()
    return mat, player_pos, pc_pos, protecion_list


def checkValidMove(line_player, column_player, new_line, new_column):
    if abs(line_player - new_line) + abs(column_player - new_column) <= 1:
        return True
    else:
        return False


def bomb_explode(stare: Stare, line_bomb, column_bomb):
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
    set2 = set(cell_explode).union(set(stare.end_zone))
    stare.end_zone = list(set2)


def main():
    parse_args()
    mat, player_pos, pc_pos, protection_list = read_map()
    num_of_colons = len(mat[-1])
    num_of_lines = len(mat)
    wide = 50
    Header(num_of_colons * (wide + 1) - 1, 100)
    ecran = pygame.display.set_mode(
        size=(num_of_colons * (wide + 1) - 1, num_of_lines * (wide + 1) - 1 + Header.height))  # N *w+ N-1= N*(w+1)-1
    pygame.init()
    pygame.display.set_caption("Bomberman")

    Joc.initializeaza(ecran, NR_LINII=num_of_lines, NR_COLOANE=num_of_colons, dim_celula=wide)

    Joc(NR_LINII=num_of_lines, NR_COLOANE=num_of_colons)

    k = 1
    # System variables
    Joc.PLAYER1 = '1'
    Joc.PLAYER2 = '2'
    Joc.GOL = ' '
    Joc.WALL = '#'
    Joc.SHIELD = 'p'
    Joc.IBOMB = 'b'
    Joc.ABOMB = 'B'
    Joc.TIME_AUTO_BOMB = k
    # End

    Joc.JMAX = Player(Joc.PLAYER2, k)
    Joc.JMIN = Player(Joc.PLAYER1, k)

    current_state = Stare(mat, Joc.JMIN, 2)
    Joc.deseneaza_grid(mat)
    marked = False
    bomb_down = False
    player1_win = 0  # -1 win the computer 0 tie 1 win the player
    player2_win = 0
    while True and player1_win == 0 and player2_win == 0:

        # if current_state.current_player == Joc.JMIN:
        if True:
            msg = f"Player {current_state.current_player.sign}"
            Joc.update_header(msg)
            for event in pygame.event.get():

                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                elif event.type == pygame.MOUSEBUTTONDOWN:
                    pos = pygame.mouse.get_pos()  # coordonatele cursorului la momentul clickului
                    mouse_button = pygame.mouse.get_pressed()
                    for np in range(len(Joc.celuleGrid)):

                        if Joc.celuleGrid[np].collidepoint(pos):
                            linie = np // Stare.NR_COLOANE
                            coloana = np % Stare.NR_COLOANE

                            # mark the player to move press left click
                            if current_state.matr[linie][coloana] == current_state.current_player.sign and mouse_button[
                                0] is True:
                                if marked and marked[0] == linie and marked[1] == coloana:
                                    marked = False
                                    Joc.deseneaza_grid(current_state.matr)
                                else:
                                    marked = (linie, coloana)
                                    Joc.deseneaza_grid(current_state.matr, np)

                            # right click to put a bomb down
                            if current_state.matr[linie][coloana] == current_state.current_player.sign and mouse_button[
                                2] is True:
                                if marked and marked[0] == linie and marked[1] == coloana:
                                    marked = False
                                    bomb_down = False
                                    Joc.deseneaza_grid(current_state.matr, -1, 1)
                                else:
                                    bomb_down = True
                                    marked = (linie, coloana)
                                    Joc.deseneaza_grid(current_state.matr, np, 1)

                            if (current_state.matr[linie][coloana] == Joc.GOL or
                                current_state.matr[linie][coloana] == Joc.SHIELD) and marked and \
                                    checkValidMove(marked[0], marked[1], linie, coloana):
                                # automatic placement bomb or you want to do it or just let an empty space behind him
                                if current_state.current_player.bomb_auto_placing == 0 or bomb_down is True:
                                    current_state.matr[marked[0]][marked[1]] = Joc.IBOMB
                                    if current_state.current_player.inactive_bomb is not None:
                                        current_state.matr[current_state.current_player.inactive_bomb[0]][current_state.current_player.inactive_bomb[1]] = Joc.ABOMB
                                        bomb_explode(current_state, current_state.current_player.inactive_bomb[0], current_state.current_player.inactive_bomb[1])
                                    current_state.current_player.inactive_bomb = (marked[0], marked[1])

                                    current_state.current_player.list_of_bombs.append(marked)
                                    current_state.current_player.bomb_auto_placing = Joc.TIME_AUTO_BOMB + 1
                                    bomb_down = False
                                else:
                                    current_state.matr[marked[0]][marked[1]] = Joc.GOL
                                marked = False
                                if (linie, coloana) in current_state.end_zone:
                                    player1_win = -1

                                current_state.matr[linie][coloana] = current_state.current_player.sign
                                Joc.deseneaza_grid(current_state.matr)
                                if current_state.matr[linie][coloana] == Joc.SHIELD:
                                    current_state.current_player.nums_of_shields += 1
                                current_state.current_player.bomb_auto_placing -= 1
                                if current_state.current_player.bomb_auto_placing < 0:
                                    current_state.current_player.bomb_auto_placing = k

                                current_state.current_player = Joc.jucator_opus(current_state.current_player)

                            if current_state.matr[linie][coloana] == Joc.IBOMB:
                                if (linie, coloana) in current_state.current_player.list_of_bombs:
                                    current_state.matr[linie][coloana] = Joc.ABOMB
                                    if (linie, coloana) == current_state.current_player.inactive_bomb:
                                        current_state.current_player.inactive_bomb = None
                                    Joc.deseneaza_grid(current_state.matr)
                                    bomb_explode(current_state, linie, coloana)

                            # if current_state.tabla_joc.matr[linie][coloana] == Joc.ABOMB:
                            #     if (linie, coloana) in Joc.JMIN.list_of_bombs:
                            #         current_state.tabla_joc.matr[linie][coloana] = Joc.IBOMB
        else:
            header_message = "Player 2 (Computer)"
            Joc.update_header(header_message)
            time.sleep(0.5)
            current_state.current_player = Joc.jucator_opus(current_state.current_player)



    message = "You win!" if player2_win == -1 else "You lose!"

    while True:
        for event in pygame.event.get():
            header_message = message
            Joc.update_header(header_message)
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()


if __name__ == "__main__":
    main()
