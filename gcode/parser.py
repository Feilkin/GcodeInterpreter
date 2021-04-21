"""G-code (subset) parser.

Implemented as a recursive descent parser.

Pseudo-EBNF grammar of the supported subset:

    program        = % newline
                     program_number newline
                     { line }
                     % ;
    program_number = "O" integer ;
    line           = [line_number] { instruction } newline ;
    line_number    = "N" integer [space] ;
    instruction    = letter decimal [space] ;
    integer        = digit { digit } ;
    newline        = [ "(" any ")" ] "\n" ;

"""

import math

from gcode import ast


class ParseError(Exception):
    source = None
    message = None

    def __init__(self, source, message):
        self.source = source
        self.message = message


def program(source: str) -> ast.Program:
    _, tail = consume("%", source)
    _, tail = newline(tail)
    number, tail = program_number(tail)
    _, tail = newline(tail)

    lines = []

    while tail[0] != "%":
        l, tail = line(tail)

        if len(l) > 0:
            lines.append(l)

    return ast.Program(int(number), lines)


def program_number(source: str) -> (int, str):
    _, tail = consume("O", source)
    return integer(tail)


def line_number(source: str) -> (int, str):
    _, tail = consume("N", source)
    number, tail = integer(tail)
    _, tail = maybe_space(tail)

    return number, tail


def line(source: str) -> ([ast.Instruction], str):
    # line numbers are optional
    try:
        _, tail = line_number(source)
        source = tail
    except ParseError:
        pass

    instructions = []

    while source[0] != "\n":
        try:
            instruction, tail = alpha(source)

            # In our subset, each instruction has exactly one argument, which might be a unsigned integer or a signed
            # decimal. Because I'm lazy, I'm parsing all arguments as a signed decimal. :)
            arg, tail = decimal(tail)

            instructions.append(ast.Instruction(instruction, arg))

            # skip any spaces
            _, tail = maybe_space(tail)

            source = tail
        except ParseError:
            break

    _, tail = newline(source)

    return instructions, tail


def consume(needle: str, source: str) -> (str, str):
    """Checks that source starts with given needle

    Returns:
        A tuple with needle and tail (rest of the source)
    """
    if not source.startswith(needle):
        raise ParseError(source, "Expected " + needle)

    return needle, source[len(needle):]


def newline(source: str) -> (str, str):
    """Consumes a newline along with any comments and spaces

    Returns:
        A tuple of the newline and the tail
    """
    _, tail = maybe_space(source)

    # ignore comment
    if tail[0] == "(":
        while tail[0] != ")":
            tail = tail[1:]
        tail = tail[1:]

    if tail[0] != "\n":
        raise ParseError(source, "Expected newline")

    return "\n", tail[1:]


def alpha(source: str) -> (str, str):
    head = source[0]
    tail = source[1:]

    if not head.isalpha():
        raise ParseError(source, "Expected alphabet character")

    return head, tail


def digit(source: str) -> (str, str):
    head = source[0]
    tail = source[1:]

    if not head.isdecimal():
        raise ParseError(source, "Expected integer value")

    return head, tail


def integer(source: str) -> (str, str):
    """Attempts to parse an unsigned integer (sequence of digits)

    Returns:
        A tuple of the integer and tail
    """
    # Should have at least one number
    number, tail = digit(source)

    # attempt to parse digits until digit parser fails
    while True:
        try:
            n, tail = digit(tail)
            number += n
        except ParseError:
            break

    return number, tail


def decimal(source: str) -> (str, str):
    """Attempts to parse a simple floating point number.

    Only supports simple signed floats eq. -0.123, where decimal part may be omitted (eq 123.).

    Returns:
        A tuple of the float and tail
    """
    buffer = ""

    # using if instead of try-block with consume to keep the control flow simpler
    if source[0] == "-":
        buffer = "-"
        source = source[1:]

    number, tail = integer(source)
    buffer += number

    if tail[0] == ".":
        tail = tail[1:]

        # early exit in case of a newline because I'm lazy
        if tail[0] != "\n":
            d, tail = integer(tail)
            buffer += "." + d

    return buffer, tail


def maybe_space(source: str) -> (str, str):
    """Captures spaces if there is any.

    This function will not raise parse errors.

    Returns:
        A tuple of captures spaces, and the tail
    """
    captured = ""
    while source[0] == " ":
        source = source[1:]
        captured += " "

    return captured, source
