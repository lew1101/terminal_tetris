from time import sleep, perf_counter

SMOOTHING_FACTOR = 0.9


def calc_smooth_fps(frames: int, time_diff: float, avg_fps: float, smoothing_factor: float = SMOOTHING_FACTOR):
    curr_fps = frames / time_diff
    if avg_fps < 0:
        avg_fps = curr_fps
    else:
        avg_fps = (avg_fps * smoothing_factor) + \
            (curr_fps * (1-smoothing_factor))
    return avg_fps


class Clock:
    def __init__(self, target_fps: int):
        self.target_fps = target_fps

        self.delay = 1/self.target_fps
        self.prev_tick = perf_counter()
        self.frames = 0

    def tick(self) -> float:
        curr_tick = perf_counter()
        elapsed = curr_tick - self.prev_tick

        if (sleep_time := self.delay - elapsed) > 0:
            sleep(sleep_time)

        self.prev_tick = curr_tick
        self.frames += 1

        return elapsed

    def frame_interval_has_passed(self, frames: int) -> bool:
        return self.frames % frames == 0 and self.frames != 0
