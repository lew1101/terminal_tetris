import curses

from time import perf_counter
from dataclasses import dataclass

FPS_UPDATE_INTERVAL = 25
SMOOTHING_FACTOR = 0.9


def calc_smooth_fps(frames: int, time_diff: float, avg_fps: float, smoothing_factor: float = SMOOTHING_FACTOR):
    curr_fps = frames / time_diff
    if avg_fps < 0:
        avg_fps = curr_fps
    else:
        avg_fps = (avg_fps * smoothing_factor) + \
            (curr_fps * (1-smoothing_factor))
    return avg_fps


@dataclass
class Clock:
    target_fps: int

    def __post_init__(self):
        self.start = perf_counter()
        self.elapsed = 0
        self.prev_tick = -1.0
        self.delay = 1/self.target_fps
        self.frames = 0

    def tick(self) -> float:
        curr_tick = perf_counter()
        elapsed = curr_tick - self.prev_tick

        if (sleep_time := self.delay - elapsed) > 0:
            curses.napms(int(sleep_time*1000))

        self.prev_tick = curr_tick
        self.frames += 1
        self.elapsed = curr_tick - self.start

        return elapsed

    def interval_has_passed(self, interval: int) -> bool:
        return self.frames % interval == 0 and self.frames != 0
