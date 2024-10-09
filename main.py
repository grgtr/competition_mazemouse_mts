import requests
import time

SIZE = 16

class Mouse:
    def __init__(self, token="", url="http://127.0.0.1:8801/api/v1"):
        self.token = token
        self.url = url
        self.maze = [[0 for _ in range(SIZE)] for _ in range(SIZE)]
        self.data: dict
        self.x = 15
        self.y = 0
        self.direction = "up"

    def forward(self):
        r = requests.post(self.url + "/robot-cells/forward", params={"token": self.token})
        if r.status_code != requests.codes.ok:
            raise RuntimeError
        if self.direction == "up":
            self.x -= 1
        elif self.direction == "right":
            self.y += 1
        elif self.direction == "left":
            self.y -= 1
        elif self.direction == "down":
            self.x += 1
        time.sleep(0.1)

    def turn_left(self):
        r = requests.post(self.url + "/robot-cells/left", params={"token": self.token})
        if r.status_code != requests.codes.ok:
            raise RuntimeError
        next_d = {
            "up":    "left",
            "right": "up",
            "left":  "down",
            "down":  "right",
        }
        self.direction = next_d[self.direction]

    def turn_right(self):
        r = requests.post(self.url + "/robot-cells/right", params={"token": self.token})
        if r.status_code != requests.codes.ok:
            raise RuntimeError
        next_d = {
            "up":    "right",
            "right": "down",
            "left":  "up",
            "down":  "left",
        }
        self.direction = next_d[self.direction]

    def backward(self):
        r = requests.post(self.url + "/robot-cells/backward", params={"token": self.token})
        if r.status_code != requests.codes.ok:
            raise RuntimeError
        if self.direction == "up":
            self.x += 1
        elif self.direction == "right":
            self.y -= 1
        elif self.direction == "left":
            self.y += 1
        elif self.direction == "down":
            self.x -= 1
        time.sleep(0.1)

    def submit_task1(self):
        r = requests.post(self.url + "/matrix/send", params={"token": self.token}, json=self.maze)
        if r.status_code != requests.codes.ok:
            raise RuntimeError
        print(r.text)

    def go(self, direction: str):
        if direction == "up":
            if self.direction == "up":
                self.forward()
                return
            if self.direction == "right":
                self.turn_left()
                self.forward()
                return
            if self.direction == "left":
                self.turn_right()
                self.forward()
                return
            if self.direction == "down":
                self.turn_right()
                self.turn_right()
                self.forward()
                return
        if direction == "right":
            if self.direction == "up":
                self.turn_right()
                self.forward()
                return
            if self.direction == "right":
                self.forward()
                return
            if self.direction == "left":
                self.turn_right()
                self.turn_right()
                self.forward()
                return
            if self.direction == "down":
                self.turn_left()
                self.forward()
                return
        if direction == "left":
            if self.direction == "up":
                self.turn_left()
                self.forward()
                return
            if self.direction == "right":
                self.turn_right()
                self.turn_right()
                self.forward()
                return
            if self.direction == "left":
                self.forward()
                return
            if self.direction == "down":
                self.turn_right()
                self.forward()
                return
        if direction == "down":
            if self.direction == "up":
                self.turn_right()
                self.turn_right()
                self.forward()
                return
            if self.direction == "right":
                self.turn_right()
                self.forward()
                return
            if self.direction == "left":
                self.turn_left()
                self.forward()
                return
            if self.direction == "down":
                self.forward()
                return

    def upd_sensor_data(self):
        r = requests.get(self.url + "/robot-cells/sensor-data", params={"token": self.token})
        if r.status_code != requests.codes.ok:
            raise RuntimeError
        self.data = r.json()

    def restart(self):
        r = requests.post(self.url + "/robot-cells/restart", params={"token": self.token})
        if r.status_code != requests.codes.ok:
            raise RuntimeError

    @staticmethod
    def __dist_to_wall(dist: int):
        return int(round(dist / 166.67))

    def get_walls(self):
        f = self.__dist_to_wall(self.data["front_distance"])
        r = self.__dist_to_wall(self.data["right_side_distance"])
        l = self.__dist_to_wall(self.data["left_side_distance"])
        b = self.__dist_to_wall(self.data["back_distance"])
        return f, r, l, b

    def get_abs_walls(self):
        f, r, l, b = self.get_walls()
        # True if there is wall
        # False if we can pass through
        up = not ((self.direction == "up" and f != 0) or (self.direction == "right" and l != 0) or (self.direction == "down" and b != 0) or (self.direction == "left" and r != 0))
        right = not ((self.direction == "up" and r != 0) or (self.direction == "right" and f != 0) or (self.direction == "down" and l != 0) or (self.direction == "left" and b != 0))
        down = not ((self.direction == "up" and b != 0) or (self.direction == "right" and r != 0) or (self.direction == "down" and f != 0) or (self.direction == "left" and l != 0))
        left = not ((self.direction == "up" and l != 0) or (self.direction == "right" and b != 0) or (self.direction == "down" and r != 0) or (self.direction == "left" and f != 0))
        return up, right, left, down

    def fill_cell(self):
        walls = {
            #  (up, right, left, down)
            (False, False, False, False): 0,
            (False, False, True,  False): 1,
            (True,  False, False, False): 2,
            (False, True,  False, False): 3,
            (False, False, False, True ): 4,
            (False, False, True,  True ): 5,
            (False, True,  False, True ): 6,
            (True,  True,  False, False): 7,
            (True,  False, True,  False): 8,
            (False, True,  True,  False): 9,
            (True,  False, False, True ): 10,
            (True,  True,  False, True ): 11,
            (True,  True,  True,  False): 12,
            (True,  False, True,  True ): 13,
            (False, True,  True,  True ): 14,
            (True,  True,  True,  True ): 15,
        }
        self.maze[self.x][self.y] = walls[*self.get_abs_walls()]

    def fill_maze(self):
        self._fill_maze([[False for _ in range(SIZE)] for _ in range(SIZE)])

    def _fill_maze(self, visited):
        self.upd_sensor_data()
        self.fill_cell()
        visited[self.x][self.y] = True
        up, right, left, down = self.get_abs_walls()
        if not up and not visited[self.x - 1][self.y]:
            self.go("up")
            self._fill_maze(visited)
            self.go("down")
        if not right and not visited[self.x][self.y + 1]:
            self.go("right")
            self._fill_maze(visited)
            self.go("left")
        if not left and not visited[self.x][self.y - 1]:
            self.go("left")
            self._fill_maze(visited)
            self.go("right")
        if not down and not visited[self.x + 1][self.y]:
            self.go("down")
            self._fill_maze(visited)
            self.go("up")

m = Mouse()
m.fill_maze()
m.submit_task1()
