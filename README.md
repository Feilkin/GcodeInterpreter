# G-Code interpreter

How to run:
```shell
> git clone https://github.com/Feilkin/GcodeInterpreter
> python GcodeInterpreter some_fcode_file.gcode
```

Minimum support Python version is 3.8.0

## About

This small project implements a parser and interpreter for a subset of G-Code ("RS-274").

It is not meant to be fully compliant G-Code interpreter, and it will probably fail to parse, or not execute properly,
most G-Code scripts.

Entry point for execution is `cnc.py`, parsing is handled by `gcode/parser.py`, and interpretation by `interpreter.py`.


## Licence

All rights reserved. Do not use this. You have been warned.