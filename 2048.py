# author:WangErPang(wang.erpang@qq.com)
#!/usr/bin/env python
# -*- coding=utf-8 -*-

import curses
from random import randrange, choice
from collections import defaultdict

# basic actions
ACTIONS = ['Up', 'Left', 'Down', 'Right', 'Restart', 'exit']
# code linker
LETTERCODE = [ord(ch) for ch in 'WASDRQwasdrq']
# linker
Action_Dict = dict(zip(LETTERCODE, ACTIONS * 2))

#logic
# Init:init()
#     ->game
# Game: game()
#     ->Game
#     ->Win
#     ->Gameover
#     ->exit
# Win :not_game(win)
#     ->init
#     ->exit
# Game: notgame(Gameover)
#     ->init
#     ->exit
# Exit: break


# game main circle
def get_user_action(keyboard):
    char = 'N'
    while char not in Action_Dict:
        char = keyboard.getch()
    return Action_Dict[char]


def transpose(field):
    return [list(row) for row in zip(*field)]  # for moving


def invent(field):
    return [row[::-1] for row in field]  # for moving


class GameField(object):
    def __init__(self, height=4, width=4, win=2048):
        self.height = height
        self.width = width
        self.win_value = 2048
        self.score = 0
        self.highscore = 0
        self.reset()

    def reset(self):
        if self.score > self.highscore:
            self.highscore = self.score
        self.score = 0
        self.field = [[0 for i in range(self.width)]
                      for j in range(self.width)]
        self.spawn()
        self.spawn()  # general 2

    def spawn(self):  # gengral 2 or 4 in the UI
        new_element = 4 if randrange(100) > 89 else 2
        (i, j) = choice([(i, j)
                         for i in range(self.width)
                         for j in range(self.height) if self.field[i][j] == 0])

    def move(self, direction):
        def move_row_left(row):
            def tighten(row):
                new_row = [i for i in row if i != 0]
                new_row += [0 for i in range(len(row) - len(new_row))]
                return new_row

            def merge(row):
                pair = False
                new_row = []
                for i in range(len(row)):
                    if pair:
                        new_row.append(2 * row[i])
                        self.score += 2 * row[i]
                        pair = False
                    else:
                        if i + 1 < len(row) and row[i] == row[i + 1]:
                            pair = True
                            new_row.append(0)
                        else:
                            new_row.append(row[i])
                assert len(new_row) == len(row)
                return new_row

            return tighten(merge(tighten(row)))

        moves = {}
        moves['Left'] = lambda field: [move_row_left(row) for row in field]
        moves['Right'] = lambda field: invent(moves['Left'](invent(field)))
        moves['Up'] = lambda field: transpose(moves['Left'](transpose(field)))
        moves[
            'Down'] = lambda field: transpose(moves['Right'](transpose(field)))
        if direction in moves:
            if self.move_is_possible(direction):
                self.field = moves[direction](self.field)
                self.spawn()
                return True
            else:
                return False

    def move_is_possible(self, direction):
        "Judge can move or not"

        def row_is_left_moveable(row):
            "move to left is possible"

            def change(i):
                """ if can move, return True. Else return False"""

                if row[i] == 0 and row[i + 1] != 0:  # Can Move
                    return True
                if row[i] != 0 and row[i + 1] == row[i]:  # Can Merge
                    return True
                return False

            return any(change(i) for i in range(len(row) - 1))

        check = {}
        check['Left']=lambda field:any(row_is_left_moveable(row) for row in field)
        check['Right'] = lambda field: check['Left'](invent(field))
        check['Up'] = lambda field: check['Left'](transpose(field))
        check['Down'] = lambda field: check['Right'](transpose(field))
        if direction in check:
            return check[direction](self.field)
        else:
            return False

    def is_win(self):
        "iswin"
        return any(any(i >= self.win_value for i in row) for row in self.field)

    def is_gameover(self):
        "gameover"
        return not any(self.move_is_possible(move) for move in ACTIONS)

    def draw(self, screen):
        "Draw the game UI"
        help_string1 = '(W)Up  (S)Down  (A)Left  (D)Right'
        help_string2 = '(R)Restart  (Q)Exit'
        gameover_string = 'GAMEOVER'
        win_string = 'WIN'

        def cast(string):
            "show the help string on screen"
            screen.addstr(string + '\n')
        # TODO:


def main(stdscr):
    "main func"

    def init():
        "inition"
        return 'Game'

    # Gameover and Win
    def not_game(state):
        "not in game state"
        responses = defaultdict(lambda: state)  # defalut state
        responses['Restart'], responses[
            'Exit'] = 'Init', 'Exit'  # action with state
        return responses[action]  # FIXME:

    # game Func
    def game():
        if action == 'Restart':  # FIXME:
            return "Init"
        if action == 'Exit':  # FIXME:
            return 'Exit'
        # if Success move a step:#TODO:
        #    if win:
        #       return 'Win'
        #    if Fail:
        #       return 'Gameover'
        return 'Game'

    state_actions = {
        'Init': init,
        'Win': lambda: not_game('Win'),
        'Gameover': lambda: not_game('Gameover'),
        'Game': game
    }
    state = 'Init'

    while state != 'Exit':
        state = state_actions[state]()
