import sys

from logic.Player import Player
from logic.value_is_neutral import value_is_neutral
from rendering.ConsoleColours import ConsoleColours

def standardPositionRenderer(position, space):
  position_str = f'{ConsoleColours.CYAN} | {ConsoleColours.ENDC}'
  if position == Player.X.value:
    position_str += f'{ConsoleColours.RED}{Player.X.name}{ConsoleColours.ENDC}'
  elif position == Player.O.value:
    position_str += f'{ConsoleColours.GREEN}{Player.O.name}{ConsoleColours.ENDC}'
  else:
    position_str += f'{space}'

  return position_str

def row_separator_renderer(column_count):
  separator = f'{ConsoleColours.CYAN} -{ConsoleColours.ENDC}'
  for j in range(0, column_count):
    separator += f'{ConsoleColours.CYAN}----{ConsoleColours.ENDC}'
  separator += '\n'

  return separator

def row_terminator_renderer():
  return f'{ConsoleColours.CYAN} | {ConsoleColours.ENDC}\n'

def display_board(board, indent=0):
  space = 0
  for i in range(0, indent):
    sys.stdout.write('\t')
  for b in range(0, indent):
    sys.stdout.write('\t')
  sys.stdout.write(row_separator_renderer(len(board[0])))
  for i in board:
    for b in range(0, indent):
      sys.stdout.write('\t')
    for j in i:
      sys.stdout.write(standardPositionRenderer(j, space))
      if value_is_neutral(j):
        space = space + 1
    sys.stdout.write(row_terminator_renderer())
    for b in range(0, indent):
      sys.stdout.write('\t')

    sys.stdout.write(row_separator_renderer(len(i)))
