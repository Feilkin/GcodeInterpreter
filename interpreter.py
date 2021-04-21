import string

from client import MachineClient
from gcode import ast


class Interpreter:
    client: MachineClient = None
    instruction_table = {}
    # some ugly statefull stuff because I ran out of time
    # should have gone with parser combinators instead
    selected_tool = None  # set with T instruction, changed with M06
    target = [0., 0., 0.]  # absolute target coordinates for linear interpolation, not the best way to do this but works
    should_move = False

    def __init__(self, client: MachineClient):
        # initialize all letters to noop
        instruction_table = {letter: self.noop for letter in string.ascii_uppercase}

        # fill in the letter addresses we support
        instruction_table["F"] = self.set_feed_rate
        instruction_table["G"] = self.handle_g
        instruction_table["M"] = self.handle_m
        instruction_table["S"] = self.set_spindle_speed
        instruction_table["T"] = self.select_tool
        instruction_table["X"] = self.set_x
        instruction_table["Y"] = self.set_y
        instruction_table["Z"] = self.set_z

        self.instruction_table = instruction_table
        self.client = client

    def execute(self, program: ast.Program):
        for line in program.lines:
            self.should_move = False
            # process each instruction in this line/block
            for instruction in line:
                if self.instruction_table[instruction.letter](instruction.arg):
                    return

            # execute move commands so we get correct interpolation
            if self.should_move:
                # this uses linear interpolation for all moves, when we actually should also support rapid positioning
                # but the client doesn't expose rapid positioning functionality
                self.client.move(self.target[0], self.target[1], self.target[2])

    def noop(self, _arg):
        pass

    def select_tool(self, tool):
        self.selected_tool = tool

    def handle_m(self, arg):
        # python doesn't have switch/match?
        # would be cleaner to use lookup table like the instruction_table, but we only support few M codes
        # so this is faster
        if arg == "03":
            # TODO: spindle on
            return
        if arg == "05":
            # TODO: spindle off
            return
        if arg == "06":
            self.client.change_tool(self.selected_tool)
            return
        if arg == "09":
            self.client.coolant_off()
            return
        if arg == "30":
            # end program
            return True
        # TODO: notify user of unimplemented instruction?

    def handle_g(self, arg):
        # Again, not the best way to do this, but it'll work for now. Refactor later :)
        if arg == "00":
            self.should_move = True
            # TODO: use rapid positioning when moving
            return
        if arg == "01":
            self.should_move = True
            return
        if arg == "28":
            self.client.home()
            return
        if arg == "54":
            # TODO: WCSs
            return
        if arg == "90":
            # TODO: handle absolute programming
            return
        if arg == "91":
            # TODO: handle incremental programming
            return

    def set_x(self, x):
        self.target[0] = float(x)

    def set_y(self, y):
        self.target[1] = float(y)

    def set_z(self, z):
        self.target[2] = float(z)

    def set_spindle_speed(self, speed):
        self.client.set_spindle_speed(int(speed))

    def set_feed_rate(self, feed_rate):
        self.client.set_feed_rate(float(feed_rate))
