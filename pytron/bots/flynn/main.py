from pytron.bot import Bot, Action, Orientation
import copy


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
        self.state = "forward"
        self.goal = self.margin
        self.turning = False


    def close_to_edge(self, margin=1) -> bool:
        x, y = self.board.bots_path[self.id][-1]
        return ((x <= margin) or
                (y <= margin) or
                (x >= self.board_column_size-margin) or
                (y >= self.board_row_size-margin))


    def close_to_bot(self, margin=1) -> bool:
        x, y = self.board.bots_path[self.id][-1]
        for x0, y0 in self.board.used_positions:
            if (x0, y0) in self.board.bots_path[self. id]:
                continue
            if abs(x-x0) <= margin or abs(y-y0) <= margin:
                return True
        return False


    def get_action(self, board):
        self.board = board

        # Check when spiral is going big if it collides with something
        # breakpoint()
        if self.turning:
            self.turning = False
            self.turning_side = Action.Left
            return Action.Right

        if self.state == "forward" and (self.close_to_bot() or self.close_to_edge()):
            self.collision_point = copy.deepcopy(self.xy)
            self.state = "reverse"
            self.current = 0
            self.n_cycles = 0
            self.turning = True
            self.turning_side = Action.Right

            return self.turning_side

        return getattr(self, self.state)()


    def forward(self):
        print(f"forward {self.n_cycles=} {self.current=} {self.goal=}")

        if self.current == self.goal:
            self.current = 1
            if self.n_cycles:
                self.n_cycles = False
                self.margin_iteration += 1
                self.goal = self.margin_iteration * self.margin
            else:
                self.n_cycles = True

            print("RIGHT")
            return Action.Right

        self.current += 1
        print("FORWARD")
        return Action.Forward

    def reverse(self):
        print(f"reverse {self.n_cycles=} {self.current=} {self.goal=}")
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
        print(f"exitting {self.n_cycles=} {self.current=} {self.goal=}")
        collx, colly = self.collision_point
        x, y = self.xy
        if (abs(collx-x) == self.margin-1 and abs(colly-y) == 0) or \
            (abs(collx-x) == 0 and abs(colly-y) == self.margin-1):
            # TODO Aqui tu amazing function!
            pass

        if not self.collision_forward():
            return Action.Forward

        return self.turning_side

    @property
    def xy(self):
        camino = self.board.bots_path[self.id]
        x, y = camino[-1]
        print(camino[-1])
        return x, y

    def collision_forward(self):
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

        print(f"next position {x=} {y=} {current_orientation=}")
        if (x, y) in self.board.bots_path[self.id]:
            return True
        return False

    def collision_turning_side(self):
        current_orientation = self.board.bots_orientation[self.id]
        x, y = copy.deepcopy(self.xy)

        nextx, nexty = COLLITION_SIDE[current_orientation][self.turning_side]
        x += nextx
        y += nexty
        print(f"next position {x=} {y=} {current_orientation=}")
        if (x, y) in self.board.bots_path[self.id]:
            return True
        return False
