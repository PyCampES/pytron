from pytron.bot import Bot, Action


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
            return Action.Right

        if self.state == "forward" and (self.close_to_bot() or self.close_to_edge()):
            self.state = "reverse"
            self.current = 0
            self.n_cycles = 0
            self.turning = True
            return Action.Right

        return getattr(self, self.state)()

        # if self.state == "reverse":
        #     return self.reverse()
        # else:
        #     return self.forward()

    def forward(self):
        # right, right, margin, right, margin, right, margin*2, right, margin*2,
        print(f"forward {self.n_cycles=} {self.current=} {self.goal=}")

        if self.current == self.goal:
            self.current = 0
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

        if self.current == self.goal-1:
            self.current = 0
            if self.n_cycles:
                self.n_cycles = False
                self.margin_iteration -= 1
                self.goal = self.margin_iteration * self.margin
            else:
                self.n_cycles = True

            print("LEFT")
            return Action.Left

        self.current += 1
        print("FORWARD")
        return Action.Forward


    def warning_collision(self):
        return self.goal == 9

    # def forward(self):


    #     if self.n_forwards == 9:
    #         # Return to same n_forwards
    #         self.n_forwards -= self.margin
    #         self.margin -= 1
    #         self.n_cycles = 1
    #         print("RIGHT TURN")
    #         self.action = "reverse"
    #         return Action.Right
    #     print(f"forward {self.n_cycles=} {self.n_forwards=} {self.n_current_forwards=}")

    #     if self.n_current_forwards == self.n_forwards:
    #         if self.n_cycles == 1:
    #             self.n_cycles = 0
    #             self.n_forwards += self.margin
    #         else:
    #             self.n_cycles += 1
    #         self.n_current_forwards = 0
    #         print("RIGHT")
    #         return Action.Right
    #     self.n_current_forwards += 1
    #     print("FORWARD")
    #     return Action.Forward

    # def reverse(self):
    #     print(f"reverse {self.n_cycles=} {self.n_forwards=} {self.n_current_forwards=} {self.margin=}")
    #     if self.n_forwards == 0:
    #         self.is_reverse = False

    #     if self.n_current_forwards == self.n_forwards-1:
    #         if self.n_cycles == 1:
    #             self.n_cycles = 0
    #             self.n_forwards -= self.margin
    #         else:
    #             self.n_cycles += 1
    #         self.n_current_forwards = 0
    #         print("LEFT")
    #         return Action.Left
    #     self.n_current_forwards += 1
    #     print("FORWARD")
    #     return Action.Forward
