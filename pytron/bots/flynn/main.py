from pytron.bot import Bot, Action, Orientation
import math
import numpy as np
import random
import copy
from functools import lru_cache

ACTION_FROM_PAIR = {
    Orientation.North: {
        Orientation.East: Action.Right,
        Orientation.West: Action.Left,
        Orientation.South: random.choice([Action.Right, Action.Left]),
    },
    Orientation.South: {
        Orientation.East: Action.Left,
        Orientation.West: Action.Right,
        Orientation.North: random.choice([Action.Right, Action.Left]),
    },
    Orientation.West: {
        Orientation.East: Action.Left,
        Orientation.South: Action.Left,
        Orientation.North: Action.Right,
    },
    Orientation.East: {
        Orientation.West: Action.Right,
        Orientation.South: Action.Right,
        Orientation.North: Action.Left,
    },
}

COLLITION_SIDE = {
    Orientation.North: {
        Action.Right: (1, 0),
        Action.Left: (-1, 0)
    },
    Orientation.South: {
        Action.Right: (-1, 0),
        Action.Left: (1, 0)
    },
    Orientation.East: {
        Action.Right: (0, 1),
        Action.Left: (0, -1)
    },
    Orientation.West: {
        Action.Right: (0, -1),
        Action.Left: (0, 1)
    }
}


class PlayerBot(Bot):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.n_cycles = 0
        self.n_forwards = 0
        self.current = 0
        self.margin = 3
        self.margin_iteration = 1
        self.state = "forward_small_to_big"
        self.goal = None
        self.turning_big = False
        self.turning_small = False

    def close_to_edge(self, margin=1) -> bool:
        x, y = self.board.bots_path[self.id][-1]
        return ((x <= margin) or
                (y <= margin) or
                (x >= self.board_column_size-margin) or
                (y >= self.board_row_size-margin))

    @lru_cache(maxsize=None)
    def math_sqrt(self, value):
        return math.sqrt(value)

    def close_to_bot(self, margin=1) -> bool:
        x, y = self.xy
        for x0, y0 in self.board.used_positions:
            if (x0, y0) in self.board.bots_path[self.id]:
                continue
            if self.math_sqrt((x - x0)**2 + (y - y0)**2) <= margin:
                return True
        return False


    def get_action(self, board):
        self.board = board

        # Check when spiral is going big if it collides with something
        # breakpoint()
        if self.turning_big:
            self.turning_big = False
            self.turning_side = Action.Left
            return Action.Right

        if self.state == "forward_small_to_big" and (self.close_to_bot() or self.close_to_edge()):
            self.collision_point = copy.deepcopy(self.xy)
            self.state = "reverse"
            self.current = 0
            self.n_cycles = 0
            self.turning_big = True
            self.turning_side = Action.Right

            return self.turning_side

        if self.turning_small:
            self.turning_small = False
            self.turning_side = Action.Right
            return Action.Left


        if self.state == "forward_big_to_small" and (self.close_to_bot() or self.close_to_edge() or self.goal == 0):
            self.collision_point = copy.deepcopy(self.xy)
            self.state = "reverse"
            self.turning_small = True
            self.turning_side = Action.Left

            return self.turning_side

        return getattr(self, self.state)()

    def forward_small_to_big(self):
        print(f"forward_small_to_big {self.n_cycles=} {self.current=} {self.goal=}")
        if self.goal is None:
            self.goal = self.margin

        if self.current == self.goal:
            self.current = 1
            if self.n_cycles:
                self.n_cycles = False
                self.margin_iteration += 1
                self.goal = self.margin_iteration * self.margin
            else:
                self.n_cycles = True
            return Action.Right
        self.current += 1
        print("forward_small_to_big")
        return Action.Forward

    def forward_big_to_small(self, goal_size=10, orientation=Orientation.North, side="right"):
        print(f"forward_big_to_small {self.n_cycles=} {self.current=} {self.goal=}")

        if self.goal is None:
            self.margin = 2
            self.goal = goal_size - (goal_size % self.margin)
            self.margin_iteration = 1
            self.current = 1
            self.n_cycles = False

        if self.current == self.goal:
            self.current = 1
            if self.n_cycles:
                self.n_cycles = False
                self.goal -= self.margin
            else:
                self.n_cycles = True

            print("RIGHT")
            return Action.Right

        self.current += 1
        print("forward_small_to_big")
        return Action.Forward


    def reverse(self):
        if not self.collision_forward():
            return Action.Forward
        if self.collision_turning_side():
            self.state = "exitting"
            if self.turning_side == Action.Right:
                self.turning_side = Action.Left
            elif self.turning_side == Action.Left:
                self.turning_side = Action.Right
        return self.turning_side

    def exitting(self):
        collx, colly = self.collision_point
        x, y = self.xy
        if (abs(collx-x) == self.margin-1 and abs(colly-y) == 0) or \
            (abs(collx-x) == 0 and abs(colly-y) == self.margin-1):
            # TODO Aqui tu amazing function!
            self.goal = None
            self.state = "travelling"
            return self.travelling()

        if not self.collision_forward():
            return Action.Forward

        return self.turning_side

    def travelling(self):
        next_action = self.find_next_action()
        print("wohoooooo!! I'm travelling!!!", next_action)
        return next_action

    @property
    def xy(self):
        camino = self.board.bots_path[self.id]
        x, y = camino[-1]
        return x, y

    def collision_forward(self, check_all=False):
        current_orientation = self.board.bots_orientation[self.id]
        x, y = copy.deepcopy(self.xy)
        if current_orientation == Orientation.North:
            y -= 1
        elif current_orientation == Orientation.South:
            y += 1
        elif current_orientation == Orientation.East:
            x += 1
        else:
            x -= 1

        if not check_all and (x, y) in self.board.bots_path[self.id]:
            return True

        if check_all and (x, y) in zip(*self.board.bots_path):
            return True
        return False

    def collision_turning_side(self, ):
        current_orientation = self.board.bots_orientation[self.id]
        x, y = copy.deepcopy(self.xy)

        nextx, nexty = COLLITION_SIDE[current_orientation][self.turning_side]
        x += nextx
        y += nexty
        if (x, y) in self.board.bots_path[self.id]:
            return True
        return False

    def collision_on_side(self, side):
        current_orientation = self.board.bots_orientation[self.id]
        x, y = copy.deepcopy(self.xy)
        nextx, nexty = COLLITION_SIDE[current_orientation][side]
        x += nextx
        y += nexty
        r = (x, y) in zip(*self.board.bots_path)
        return r

    def occupied_pixels(self):
        """Returns a matrix where a 1 represents a bot's step"""
        occupied = np.zeros((self.board_column_size, self.board_row_size))
        for idx, bot_path in enumerate(self.board.bots_path):
            for x, y in bot_path:
                if x < occupied.shape[0] and y < occupied.shape[1]:
                    occupied[x, y] = 1
        return occupied

    def find_best_point_ever(self, occupied, size=5,):
        corners = []
        for x in range(self.board_column_size - size):
            for y in range(self.board_row_size - size):
                if np.sum(occupied[x:x+size, y:y+size]) == 0:
                    corners.append((x, y, Orientation.South, Orientation.East))
                    corners.append((x+size, y, Orientation.South, Orientation.West))
                    corners.append((x, y+size, Orientation.North, Orientation.East))
                    corners.append((x+size, y+size, Orientation.North, Orientation.West))
        current_x, current_y = self.xy
        distances = []
        for idx, (x, y, orientation, action) in enumerate(corners):
            distance = abs(x - current_x) + abs(y - current_y)
            distances.append((idx, distance))
        if distances:
            return corners[min(distances, key=lambda x: x[1])[0]]
        return x, y, Orientation.South, Orientation.East

    def find_path_to_best_point(self, occupied, size=5):
        best_point = self.find_best_point_ever(occupied=occupied, size=size)
        print(best_point)
        current_orientation = self.board.bots_orientation[self.id]
        best_point_x, best_point_y, _, _ = best_point
        board_size = np.array((self.board_column_size, self.board_row_size))
        steps_x, steps_y = (  # Figure 1.1
            (board_size - np.array(self.xy)) - (board_size - np.array((best_point_x, best_point_y)))
        )
        if steps_x == 0:
            if steps_y == 0:
                self.state = "forward_big_to_small"
                print("#### LLEGASTE CRACK ####")
                return self.forward_big_to_small(size)
            elif steps_y > 0:
                objective_orientation = Orientation.South
            else:
                objective_orientation = Orientation.North
        elif steps_x > 0:
            objective_orientation = Orientation.East
        else:
            objective_orientation = Orientation.West

        if current_orientation == objective_orientation:
            return Action.Forward
        r = ACTION_FROM_PAIR[current_orientation][objective_orientation]
        print(current_orientation, objective_orientation,">>>", r)
        return ACTION_FROM_PAIR[current_orientation][objective_orientation]

    def find_next_action(self, size=15) -> Action:
        occupied = self.occupied_pixels()
        action = self.find_path_to_best_point(occupied=occupied, size=size)
        collisions = {
            Action.Forward: self.collision_forward(check_all=True),
            Action.Right: self.collision_on_side(Action.Right),
            Action.Left: self.collision_on_side(Action.Left),
        }
        if collisions[action]:
            print("action results in a collision, guessing a nice action :)")
            return [k for k, v in collisions if k != action and not v][0]
        return action
