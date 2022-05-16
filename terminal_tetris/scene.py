import curses
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .tetris import Tetris


def draw_debug_info(stdscr: 'curses._CursesWindow', /, **info):
    stdscr.addstr(0, 0, "[DEBUG]")
    for k in info:
        stdscr.addstr(f" {k}: {info[k]} |")


def _draw_cell(win: 'curses._CursesWindow', y: int, x: int, color: int):
    win.addstr(y, x, '  ',
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
        t = game.active_tetromino
        if t:
            for x, y in t.get_squares():
                if 0 <= y <= game.rows and 0 <= x <= game.cols:
                    _draw_cell(win, y+1, x*2+1, t.val)

    except curses.error:
        pass


def draw_score(win: 'curses._CursesWindow', game: 'Tetris'):
    try:
        win.box()
        win.addstr(1, 4, "SCORE")
        display_score = str(game.score)
        win.addstr(3, 6 - (len(display_score) // 2), display_score)
    except curses.error:
        pass


def draw_next_tetromino(win: 'curses._CursesWindow', game: 'Tetris'):
    try:
        win.box()
        win.addstr(1, 5, "NEXT")
        t = game.next_tetromino
        if t:
            for offset in t.shape:
                x = offset % 4
                y = offset // 4
                if 0 <= y <= game.rows and 0 <= x <= game.cols:
                    _draw_cell(win, y+3, x*2+3, t.val)
    except curses.error:
        pass
