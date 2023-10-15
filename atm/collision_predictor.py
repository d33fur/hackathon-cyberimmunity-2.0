from random import randint
import threading
import time
from typing import Tuple, List, Dict, Set

INIT_TIME = time.time()


def get_time() -> float:
    return time.time() - INIT_TIME


class Measurement:
    x: int
    y: int
    z: int
    n: int
    time: float

    def __init__(self, x: int, y: int, z: int, n: int, t: float | None = None) -> None:
        assert z >= 0
        self.x = x
        self.y = y
        self.z = z
        self.n = n
        self.time = t if t is not None else get_time()

    def __str__(self) -> str:
        x, y, z, n, time = self.x, self.y, self.z, self.n, self.time
        return f"({x=} {y=} {z=} {n=} {time=})"


class Predicter:
    t: int
    last_coords: Dict[int, Tuple[int, int, int, float]]  # N -> last known x, y, z, time
    vectors: Dict[int, Tuple[float, float]]
    background_thread: threading.Thread
    ms_buffer: List[Measurement]

    def __init__(
        self,
        measurements: List[Measurement] = [],
        collision_distance=1.0,
        throttle_delay=1.1,
    ) -> None:
        get_time()
        self.last_coords = {}
        self.vectors = {}
        self.ms_buffer = []
        self._throttle_delay = throttle_delay
        self._collision_distance = collision_distance
        self.background_thread = threading.Thread(target=self._background_worker)
        self.background_thread.start()
        if len(measurements):
            self.predict(measurements)

    def _background_worker(self):
        while 1:
            time.sleep(self._throttle_delay)
            self._calc()
            self.ms_buffer.clear()

    def predict(self, measurement: Measurement | List[Measurement]):
        m: List[Measurement] = (
            [measurement] if not isinstance(measurement, list) else measurement
        )
        print(f"[DEBUG] added [{', '.join(map(str, m))}] to buffer")
        self.ms_buffer.extend(m)

    def _min_distance(
        self,
        x1: int,
        y1: int,
        vx1: float,
        vy1: float,
        x2: int,
        y2: int,
        vx2: float,
        vy2: float,
    ) -> Tuple[float, float]:
        dx = x2 - x1
        dy = y2 - y1
        rvx = vx2 - vx1
        rvy = vy2 - vy1

        a = rvx**2 + rvy**2
        b = 2 * (dx * rvx + dy * rvy)
        c = dx**2 + dy**2
        d = b**2 - 4 * a * c

        if d >= 0:
            t1 = (-b + (d) ** 0.5) / (2 * a)
            t2 = (-b - (d) ** 0.5) / (2 * a)
            if t1 >= 0 and t2 >= 0:
                t = min(t1, t2)
            else:
                t = max(t1, t2)
        else:
            t = -b / (2 * a)

        cx1: float = x1 + vx1 * t
        cy1: float = y1 + vy1 * t
        cx2: float = x2 + vx2 * t
        cy2: float = y2 + vy2 * t
        min_distance = ((cx2 - cx1) ** 2 + (cy2 - cy1) ** 2) ** 0.5
        return min_distance, t

    def _calc(self):
        if not len(self.ms_buffer):
            return
        print(f"[DEBUG] predicting for buffer=[{', '.join(map(str, self.ms_buffer))}]")
        for m in self.ms_buffer:
            if m.n in self.last_coords:
                lx, ly, _, lt = self.last_coords[m.n]
                if m.time == lt:
                    continue
                self.vectors[m.n] = (
                    (m.x - lx) / (m.time - lt),
                    (m.y - ly) / (m.time - lt),
                )
            self.last_coords[m.n] = (m.x, m.y, m.z, m.time)

        checked: Set[int] = set()
        for i in self.vectors:
            for j in self.vectors:
                if i == j or i in checked:
                    continue
                if self.last_coords[i][2] != self.last_coords[j][2]:
                    continue
                x1, y1 = self.last_coords[i][:2]
                x2, y2 = self.last_coords[j][:2]
                vx1, vy1 = self.vectors[i]
                vx2, vy2 = self.vectors[j]

                min_distance, dt = self._min_distance(
                    x1, y1, vx1, vy1, x2, y2, vx2, vy2
                )
                if min_distance <= self._collision_distance:
                    print(
                        f"{i} and {j} will collide in {dt}s\n  ETA: {get_time() + dt}s\n  minimum distance between each other: {min_distance}\n  current t: {get_time()}"
                    )
                checked.add(j)




# predictor.predict([Measurement(0, 2, 5, 1), Measurement(2, 0, 5, 2)])
# time.sleep(1)
# predictor.predict([Measurement(1, 2, 5, 1), Measurement(2, 1, 5, 2)])

# predictor.predict(Measurement(0, 4, 5, 27))
# time.sleep(0.4)
# predictor.predict(Measurement(4, 1, 5, 54))
# time.sleep(0.4)
# predictor.predict([Measurement(2, 4, 5, 27), Measurement(4, 2, 5, 54)])
# time.sleep(1)

# predictor = Predicter()
# predictor.predict([Measurement(0, 3, 5, 27), Measurement(3, 0, 5, 54)])
# time.sleep(0.4)
# predictor.predict([Measurement(1, 3, 5, 27), Measurement(3, 1, 5, 54)])

# while True:
#     time.sleep(0.1)
#     new_point = Measurement(
#         randint(-100, 100),
#         randint(-100, 100),
#         randint(0, 10),
#         randint(0, 10),
#     )
#     print(f"new_point={str(new_point)}")
#     predictor.predict(new_point)