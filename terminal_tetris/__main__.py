import curses
import argparse
import locale
from time import perf_counter

from .game import Tetris, TETRIS_ROWS, TETRIS_COLS
from .scene import *
from .misc import Clock, calc_smooth_fps

FPS = 25
FPS_DISPLAY_UPDATE_RATE = FPS

# CYAN, PINK, ORANGE, YELLOW, RED, PURPLE, GREEN
GAME_COLORS = (45, 205, 208, 226, 196, 126, 70)
GAME_TICK_RATE = FPS//2
GAME_DISPLAY_ROWS = TETRIS_ROWS+2
GAME_DISPLAY_COLS = (TETRIS_COLS*2)+2


def parse_args():
    parser = argparse.ArgumentParser(
        "ascii_tetris", description="Tetris in the terminal made using the Python curses module.")
    parser.add_argument("-g", "--debug", action="store_true",
                        help="enable debug mode")
    return parser.parse_args()


def init_color():
    curses.start_color()
    curses.use_default_colors()

    for i, color in enumerate(GAME_COLORS, start=1):
        curses.init_pair(i, color, color)


def main(stdscr: 'curses._CursesWindow', argv: 'argparse.Namespace'):
    locale.setlocale(locale.LC_ALL, "")  # enable unicode support, if it exists

    stdscr.nodelay(1)
    curses.curs_set(0)
    curses.def_prog_mode()

    try:
        init_color()
    except:
        pass

    debug = argv.debug

    game_win = stdscr.subwin(GAME_DISPLAY_ROWS, GAME_DISPLAY_COLS, 2, 4)
    next_tetromino_win = stdscr.subwin(8, 14, 2, GAME_DISPLAY_COLS + 8)
    score_win = stdscr.subwin(5, 14, 11, GAME_DISPLAY_COLS + 8)

    game = Tetris()
    clock = Clock(target_fps=FPS)

    paused = False

    if debug:
        fps_display_last_update = perf_counter()
        avg_fps = -1.0
        last_key = -1
        game_tick_count = 0

    try:
        while True:
            # ----------------
            # LOGIC
            # ----------------
            if not paused:
                is_game_tick = clock.interval_has_passed(GAME_TICK_RATE)
                if is_game_tick:
                    game.tick()

            # ----------------
            # INPUT
            # ----------------

            # Get key press
            key = stdscr.getch()

            if key != -1:
                if key in (ord('q'), ord('Q')):  # quit
                    break

                if key == ord('p'):
                    paused = not paused

                if not paused and not game.flags & Tetris.Flags.GAME_END:
                    if key in (curses.KEY_LEFT, ord('a')):
                        game.move_curr_tetromino(0, -1)

                    if key in (curses.KEY_RIGHT, ord('d')):
                        game.move_curr_tetromino(0, 1)

                    if key in (curses.KEY_UP, ord('z'), ord('w')):
                        game.rotate_curr_tetromino()

                    if key in (curses.KEY_DOWN, ord('s')):
                        game.move_curr_tetromino(1, 0)

            # ----------------
            # RENDERING
            # ----------------
            stdscr.erase()

            draw_game(game_win, game)
            draw_next_tetromino(next_tetromino_win, game)
            draw_score(score_win, game)

            if debug:
                # fps info
                if clock.interval_has_passed(FPS_DISPLAY_UPDATE_RATE):
                    now = perf_counter()
                    time_diff = now - fps_display_last_update

                    avg_fps = calc_smooth_fps(
                        FPS_DISPLAY_UPDATE_RATE, time_diff, avg_fps)

                    fps_display_last_update = now

                if is_game_tick and not paused:
                    game_tick_count += 1

                k = last_key if key == -1 else key
                if k == -1:
                    display_key = None
                elif not 0 < k < 256:
                    if k == curses.KEY_UP:
                        display_key = 'KEY_UP'
                    elif k == curses.KEY_DOWN:
                        display_key = 'KEY_DOWN'
                    elif k == curses.KEY_LEFT:
                        display_key = 'KEY_LEFT'
                    elif k == curses.KEY_RIGHT:
                        display_key = 'KEY_RIGHT'
                else:
                    display_key = f"'{chr(k)}'"

                draw_debug_info(stdscr,
                                FPS=round(avg_fps, 2),
                                ELAPSED=f"{clock.elapsed:.2f}",
                                PAUSED=paused,
                                KEY_PRESS=display_key,
                                GAME_END=bool(game.flags & Tetris.Flags.GAME_END))
                last_key = key

            game_win.refresh()
            next_tetromino_win.refresh()
            score_win.refresh()
            stdscr.refresh()

            clock.tick()

            # ----------------

    except (KeyboardInterrupt, EOFError):
        pass

    stdscr.keypad(0)
    curses.endwin()
    raise SystemExit


def run():
    argv = parse_args()
    curses.wrapper(main, argv)


if __name__ == "__main__":
    run()
