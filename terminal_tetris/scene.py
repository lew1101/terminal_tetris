import curses
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .game import Tetris


def draw_debug_info(stdscr: 'curses._CursesWindow', /, **info):
    stdscr.addstr(0, 0, "[DEBUG]")
    for k in info:
        stdscr.addstr(f" {k}: {info[k]} |")

    for i in range(1, 8):
        stdscr.addstr('█', curses.color_pair(i))


def _draw_cell(win: 'curses._CursesWindow', y: int, x: int, color: int):
    win.addstr(y, x, '█'*2,
               curses.color_pair(color))


def draw_game(win: 'curses._CursesWindow', game: 'Tetris'):
    try:
        win.box()

        # playfield
        for y, row in enumerate(game.field):
            for x, cell in enumerate(row):
                if cell != 0:
                    _draw_cell(win, y+1, x*2+1, cell)

        # current tetromino
        t = game.curr_tetromino
        if t:
            for x, y in t.get_squares():
                if 0 <= y <= game.rows and 0 <= x <= game.cols:
                    _draw_cell(win, y+1, x*2+1, t.val)

    except curses.error:
        pass


def draw_score(win: 'curses._CursesWindow', game: 'Tetris'):
    try:
        win.box()
        win.addstr(1, 1, "SCORE")
        win.addstr(3, 1, str(game.score))
    except curses.error:
        pass


def draw_next_tetromino(win: 'curses._CursesWindow', game: 'Tetris'):
    try:
        win.box()
        win.addstr(1, 1, "NEXT")
        t = game.next_tetromino
        if t:
            for offset in t.shape:
                x = offset % 4
                y = offset // 4
                if 0 <= y <= game.rows and 0 <= x <= game.cols:
                    _draw_cell(win, y+3, x*2+1, t.val)
    except curses.error:
        pass
