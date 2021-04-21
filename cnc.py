"""Parser and interpreter for a subset of G-Code.

Handles the following codes:
G00 - Rapid positioning
G01 - Linear interpolation
G28 - Return to home position
G54 - TODO: Work Coordinate Systems
G90 - TODO: Absolute programming
G91 - TODO: Incremental programming
T   - Tool selection
M03 - TODO: Spindle on (clockwise rotation)
M05 - TODO: Spindle stop
M06 - Automatic Tool Change
M09 - Coolant off
M30 - End of program
S   - Spindle speed
F   - Feed Rate
"""

from gcode import parser
from client import MachineClient
from interpreter import Interpreter


def load_and_execute(filename):
    file = open(filename, "r")
    program = parser.program(file.read())

    client = MachineClient()
    interpreter = Interpreter(client)

    interpreter.execute(program)
