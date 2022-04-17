import random
import numpy as np
from typing import Tuple, List
from pytron.bot import Bot, Action, Orientation
import enum

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
        Orientation.East: random.choice([Action.Right, Action.Left]),
        Orientation.South: Action.Left,
        Orientation.North: Action.Right,
    },
    Orientation.East: {
        Orientation.West: random.choice([Action.Right, Action.Left]),
        Orientation.South: Action.Right,
        Orientation.North: Action.Left,
    },
}

class Side(str, enum.Enum):
    top = "top"
    right = "right"
    left = "left"
    bottom = "bottom"


class PlayerBot(Bot):
    def get_action(self, board):
        self.board = board
        return self.find_next_action()

    @property
    def xy(self):
        camino = self.board.bots_path[self.id]
        y, x = camino[-1]
        return x, y

    def pixels_to_edge(self):
        x, y = self.xy
        return {
            Side.top: y,
            Side.bottom: abs(self.board_row_size - y),
            Side.right: x,
            Side.left: abs(self.board_column_size - x)
        }

    def occupied_pixels(self):
        """Returns a matrix where a 1 represents a bot's step"""
        occupied = np.zeros((self.board_column_size, self.board_row_size))
        for idx, bot_path in enumerate(self.board.bots_path):
            for x, y in bot_path:
                if idx == self.id:
                    occupied[x, y] = 2
                else:
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
        return corners[min(distances, key=lambda x: x[1])[0]]

    def find_path_to_best_point(self, occupied, ):
        best_point = self.find_best_point_ever(occupied=occupied)
        current_orientation = self.board.bots_orientation[self.id]
        best_point_x, best_point_y, _, _ = best_point
        board_size = np.array((self.board_column_size, self.board_row_size))
        steps_x, steps_y = (  # Figure 1.1
            (board_size - np.array(self.xy)) - (board_size - np.array((best_point_x, best_point_y)))
        )
        if steps_x == 0:
            if steps_y == 0:
                raise Exception("Llegaste crack")
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

        return ACTION_FROM_PAIR[current_orientation][objective_orientation]

    def find_next_action(self) -> Action:
        occupied = self.occupied_pixels()
        action = self.find_path_to_best_point(occupied=occupied)
        return action
