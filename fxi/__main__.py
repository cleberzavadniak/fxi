import sys

from . import FXI


fxi = FXI()

try:
    command_line_arg = sys.argv[1]
except IndexError:
    command_line_arg = None

fxi.start(command_line_arg)
