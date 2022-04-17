from pytron.bot import Bot, Action


class PlayerBot(Bot):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.n_cycles = 0
        self.n_forwards = 0
        self.n_current_forwards = 0
        self.margin = 3
        self.is_reverse = False
        self.turning_ticks = 0
        self.turned = False
        self.action = "forward"

    def get_action(self, board):

        if self.action == "reverse":
            # breakpoint()
            return self.reverse()
        else:
            return self.forward()

    def forward(self):

        
        if self.n_forwards == 9:
            # Return to same n_forwards
            self.n_forwards -= self.margin
            self.margin -= 1
            self.n_cycles = 1
            print("RIGHT TURN")
            self.action = "reverse"
            return Action.Right
        print(f"forward {self.n_cycles=} {self.n_forwards=} {self.n_current_forwards=}")

        if self.n_current_forwards == self.n_forwards:
            if self.n_cycles == 1:
                self.n_cycles = 0
                self.n_forwards += self.margin
            else:
                self.n_cycles += 1
            self.n_current_forwards = 0
            print("RIGHT")
            return Action.Right
        self.n_current_forwards += 1
        print("FORWARD")
        return Action.Forward

    def reverse(self):
        print(f"reverse {self.n_cycles=} {self.n_forwards=} {self.n_current_forwards=} {self.margin=}")
        if self.n_forwards == 0:
            self.is_reverse = False

        if self.n_current_forwards == self.n_forwards-1:
            if self.n_cycles == 1:
                self.n_cycles = 0
                self.n_forwards -= self.margin
            else:
                self.n_cycles += 1
            self.n_current_forwards = 0
            print("LEFT")
            return Action.Left
        self.n_current_forwards += 1
        print("FORWARD")
        return Action.Forward
