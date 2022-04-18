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
        self.state = "forward_small_to_big"
        self.goal = None
        self.is_turning = False
        self.turning_big = False
        self.turning_small = False
        self.current_turn_action = None


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

    def opposite_turn(self, turn_action):
        if turn_action == Action.Right:
            self.current_turn_action = Action.Left
        elif turn_action == Action.Left:
            self.current_turn_action = Action.Right

    def turning(self):
        self.is_turning = False if self.is_turning else True
        old_turn_action = self.current_turn_action
        # Changing to opposite turn action to start reverse
        # if self.second_turn
        self.opposite_turn(self.current_turn_action)
        self.second_turn = True
        return old_turn_action

    def get_action(self, board):
        self.board = board

        # Check when spiral is going big if it collides with something
        if self.is_turning:
            return self.turning()

        if self.state == "forward_small_to_big" and (self.close_to_bot() or self.close_to_edge()):
            self.collision_point = copy.deepcopy(self.xy)
            self.state = "reverse"
            self.current = 0
            self.n_cycles = 0
            breakpoint()
            return self.turning()

        if self.state == "forward_big_to_small" and (self.close_to_bot() or self.close_to_edge() or self.goal == 0):
            self.collision_point = copy.deepcopy(self.xy)
            self.state = "reverse"
            return self.turning_side

        return getattr(self, self.state)()

    def forward_small_to_big(self, turn_action=Action.Right):
        print(f"forward_small_to_big {self.n_cycles=} {self.current=} {self.goal=}")
        self.current_turn_action = turn_action
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

            print("RIGHT")
            return Action.Right

        self.current += 1
        print("forward_small_to_big")
        return Action.Forward

    def forward_big_to_small(self, goal_size=10, orientation=Orientation.North, turn_action=Action.Left):
        print(f"forward_big_to_small {self.n_cycles=} {self.current=} {self.goal=}")
        self.current_turn_action = turn_action

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
            self.goal = None
            self.forward_big_to_small(10)
            print("😍😍😍😍😍")

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
