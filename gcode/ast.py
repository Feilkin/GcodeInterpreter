"""Abstract Syntax Tree for G-code parser"""


class Program:
    """Entry point for G-code Program"""
    number = 0
    lines = []

    def __init__(self, number: int, lines):
        self.number = number
        self.lines = lines


class Instruction:
    """Single G-code instruction"""
    letter = None
    arg = None

    def __init__(self, letter: str, arg: float):
        self.letter = letter
        self.arg = arg
