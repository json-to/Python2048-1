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

        def draw_hor_separator():
            '画出水平分割线'
            line = '+' + ('+------' * self.width + '+')[1:]
            separator = defaultdict(lambda: line)
            if not hasattr(draw_hor_separator, 'counter'):
                draw_hor_separator.counter = 0
            cast(separator[draw_hor_separator.counter])
            draw_hor_separator.counter += 1

        def draw_row(row):
            'draw row'
            cast(''.join('|{: ^5} '.format(num) if num > 0 else '|     '
                         for num in row) + '|')

        screen.clear()
        cast('SCORE: ' + str(self.score))
        if 0 != self.highscore:
            cast("HIGHSCORE: " + str(self.highscore))
        for row in self.field:
            draw_hor_separator()
            draw_row(row)
        draw_hor_separator()
        if self.is_win():
            cast(win_string)
        else:
            if self.is_gameover():
                cast(gameover_string)
            else:
                cast(help_string1)
        cast(help_string2)


def main(stdscr):
    def init():
        #重置游戏棋盘
        game_field.reset()
        return 'Game'

    def not_game(state):
        #画出 GameOver 或者 Win 的界面
        game_field.draw(stdscr)
        #读取用户输入得到action，判断是重启游戏还是结束游戏
        action = get_user_action(stdscr)
        responses = defaultdict(lambda: state) #默认是当前状态，没有行为就会一直在当前界面循环
        responses['Restart'], responses['Exit'] = 'Init', 'Exit' #对应不同的行为转换到不同的状态
        return responses[action]

    def game():
        #画出当前棋盘状态
        game_field.draw(stdscr)
        #读取用户输入得到action
        action = get_user_action(stdscr)

        if action == 'Restart':
            return 'Init'
        if action == 'Exit':
            return 'Exit'
        if game_field.move(action): # move successful
            if game_field.is_win():
                return 'Win'
            if game_field.is_gameover():
                return 'Gameover'
        return 'Game'


    state_actions = {
            'Init': init,
            'Win': lambda: not_game('Win'),
            'Gameover': lambda: not_game('Gameover'),
            'Game': game
        }

    curses.use_default_colors()
    game_field = GameField(win=32)


    state = 'Init'

    #状态机开始循环
    while state != 'Exit':
        state = state_actions[state]()

curses.wrapper(main)
