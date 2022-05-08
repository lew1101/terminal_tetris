from random import randint

TETRIS_ROWS = 20
TETRIS_COLS = 10
# index corresponds number of lines cleared
TETRIS_POINTS = (0, 400, 1000, 3000, 12000)

# ---------------------
# | 0  | 1  | 2  | 3  |
# ---------------------
# | 4  | 5  | 6  | 7  |
# ---------------------
# | 8  | 9  | 10 | 11 |
# ---------------------
# | 12 | 13 | 14 | 15 |
# ---------------------
TETROMINO_SHAPES = (
    ((4, 5, 6, 7), (2, 6, 10, 14), (8, 9, 10, 11), (1, 5, 9, 13)),  # I
    ((0, 4, 5, 6), (1, 2, 5, 9), (4, 5, 6, 10), (1, 5, 8, 9)),  # J
    ((2, 4, 5, 6), (1, 5, 9, 10), (4, 5, 6, 8), (0, 1, 5, 9)),  # L
    ((1, 2, 5, 6),),  # O
    ((1, 2, 4, 5), (1, 5, 6, 10), (5, 6, 8, 9), (0, 4, 5, 9)),  # S
    ((1, 4, 5, 6), (1, 5, 6, 9), (4, 5, 6, 9), (1, 4, 5, 9)),  # T
    ((0, 1, 5, 6), (2, 5, 6, 9), (4, 5, 9, 10), (1, 4, 5, 8)),  # Z
)
TETROMINO_SPAWN_X = 3
TETROMINO_SPAWN_Y = -2


class Tetromino:

    def __init__(self, x: int, y: int, type: int = 0, rot_index: int = 0):
        self.x = x  # top left corner
        self.y = y
        self.type = type
        self.val = self.type + 1
        self.rot_index = rot_index

    @staticmethod
    def get_random_tetromino(x: int, y: int) -> 'Tetromino':
        type = randint(0, len(TETROMINO_SHAPES) - 1)
        return Tetromino(x, y, type)

    @property
    def shape(self) -> tuple[tuple[int, ...]]:
        return TETROMINO_SHAPES[self.type][self.rot_index]

    def rotate(self) -> None:
        self.rot_index = (
            self.rot_index + 1) % len(TETROMINO_SHAPES[self.type])

    def get_squares(self) -> list[int]:
        squares = []
        for offset in self.shape:
            x = self.x + (offset % 4)
            y = self.y + (offset // 4)
            squares.append((x, y))
        return squares


class Tetris:

    def __init__(self, rows=TETRIS_ROWS, cols=TETRIS_COLS):
        self.rows = rows
        self.cols = cols
        self.field = [[0 for _ in range(cols)] for _ in range(rows)]
        self.flags = 0
        self.score = 0

        self.curr_tetromino = Tetromino.get_random_tetromino(
            x=TETROMINO_SPAWN_X, y=TETROMINO_SPAWN_Y)
        self.next_tetromino = Tetromino.get_random_tetromino(
            x=TETROMINO_SPAWN_X, y=TETROMINO_SPAWN_Y)

    def tetromino_intersects_placed(self, t: Tetromino) -> bool:
        for x, y in t.get_squares():
            if (0 <= y < self.rows and 0 <= x < self.cols) \
                    and self.field[y][x] != 0:
                return True
        return False

    # applies to bottom, left, and right
    # walls => left, bottom, right
    def tetromino_exceeds_walls(self, t: Tetromino) -> bool:
        for x, y in t.get_squares():
            if y >= self.rows or not (0 <= x < self.cols):
                return True
        return False

    def tetromino_exceeds_roof(self, t: Tetromino) -> bool:  # roof => top
        for offset in t.shape:
            if t.y + (offset // 4) < 0:
                return True
        return False

    def move_curr_tetromino(self, dy: int, dx: int) -> 0 | -1:
        self.curr_tetromino.y += dy
        self.curr_tetromino.x += dx
        if self.tetromino_exceeds_walls(self.curr_tetromino) or \
                self.tetromino_intersects_placed(self.curr_tetromino):
            # undo
            self.curr_tetromino.y -= dy
            self.curr_tetromino.x -= dx
            return -1
        return 0

    def rotate_curr_tetromino(self) -> 0 | -1:
        old_rot = self.curr_tetromino.rot_index
        for dx in (0, 1, -1):  # normal, *wall_kicks
            self.curr_tetromino.x += dx
            self.curr_tetromino.rotate()
            if self.tetromino_exceeds_walls(self.curr_tetromino) or \
                    self.tetromino_intersects_placed(self.curr_tetromino):
                # undo
                self.curr_tetromino.x -= dx
                self.curr_tetromino.rot_index = old_rot
            else:
                return 0  # success
        return -1  # fail

    def clear_lines(self) -> int:
        lines_cleared = 0
        for i, line in enumerate(self.field):
            if 0 not in line:
                self.field = [[0]*TETRIS_COLS] + \
                    self.field[:i] + self.field[i+1:]
                lines_cleared += 1
        self.score += TETRIS_POINTS[lines_cleared]
        return lines_cleared

    def tick(self) -> 0 | -1:
        if self.flags & Tetris.Flags.GAME_END:
            return -1

        if self.move_curr_tetromino(1, 0) == -1:
            if self.tetromino_exceeds_roof(self.curr_tetromino):
                # tetromino out of bounds
                self.flags |= Tetris.Flags.GAME_END
                return -1

            for x, y in self.curr_tetromino.get_squares():
                self.field[y][x] = self.curr_tetromino.val

            self.curr_tetromino = self.next_tetromino
            self.next_tetromino = Tetromino.get_random_tetromino(
                x=TETROMINO_SPAWN_X, y=TETROMINO_SPAWN_Y)

            self.clear_lines()

        return 0

    class Flags:
        GAME_END = 1
