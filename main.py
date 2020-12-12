import sys
import qprompt
import random
from enum import Enum
from copy import deepcopy
from itertools import groupby
import numpy as np
from scipy.ndimage import rotate
from rich.progress import (
    BarColumn,
    TimeRemainingColumn,
    Progress,
)

class Player(Enum):
  X = 1
  O = 2

def standardPositionRenderer(position, space):
  position_str = '\033[96m | \033[0m'
  if position == Player.X.value:
    position_str += f'\033[91m{Player.X.name}\033[0m'
  elif position == Player.O.value:
    position_str += f'\033[92m{Player.O.name}\033[0m'
  else:
    position_str += f'{space}'

  return position_str

def row_separator_renderer(column_count):
  separator = '\033[96m -\033[0m'
  for j in range(0, column_count):
    separator += '\033[96m----\033[0m'
  separator += '\n'

  return separator

def row_terminator_renderer():
  return '\033[96m | \033[0m\n'

def value_is_neutral(value):
  return value != Player.X.value and value != Player.O.value

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

def get_available_moves(board):
  available_moves = []
  for i in range(0, len(board)):
    for j in range(0, len(board)):
      if board[i][j] == -1:
        available_moves.append((i, j))

  return available_moves

def create_menu(node_list):
  menu = qprompt.Menu()
  for i in range(0, len(node_list)):
    menu.add(str(i), node_list[i])

  return menu

def menu_prompt(root):
  menu = create_menu(root.get_children())
  return menu.show(returns="desc", header=str.format("Turn {}, {} to move", root.get_move_count(), root.get_player()))

def set_board_position(board, position, value):
  x, y = position
  board[x][y] = value

def detect_horizontal_win_states(board):
  for row in board:
    if value_is_neutral(row[0]):
      continue

    # group row by unique values, if all the values are the same, the iterator will return one value followed by False
    grouped_iterator = groupby(row)
    if next(grouped_iterator, True) and not next(grouped_iterator, False):
      return row[0]

  return None

def transpose_board(board):
  return zip(*board)

def detect_win_state(board):
  orthogonal_win_state = detect_horizontal_win_states(transpose_board(board)) or detect_horizontal_win_states(board)
  diagonal_win_state = detect_horizontal_win_states([np.diag(board)]) or detect_horizontal_win_states([np.diag(np.flip(board, axis=1))])

  return orthogonal_win_state or diagonal_win_state

def calculate_board_fitness(board, player):
  opponent = Player.X
  if player == Player.X:
    opponent = Player.O

  if detect_win_state(board) == None:
    return 0.25
  elif Player(detect_win_state(board)) == player:
    return 10.0
  elif Player(detect_win_state(board)) == opponent:
    return -10.0
  elif get_current_move(board) == 9:
    return 0.5

def get_current_move(board):
  move = 0
  for row in board:
    for cell in row:
      if cell in Player._value2member_map_:
        move += 1

  return move

def get_current_player(board):
    if get_current_move(board) % 2 == 1:
      return Player.O

    return Player.X

def board_hash(board):
  b_hash = ''
  for row in board:
    for cell in row:
      b_hash = b_hash + '' + str(cell)

  return b_hash

class QTable():
  def __init__(self):
    self.table = {}

  def put_state(self, board, score):
    self.table[board_hash(board)] = score

  def get_state(self, board):
    if self.has_state(board):
      return self.table[board_hash(board)]
    return (0, 0)

  def has_state(self, board):
    return board_hash(board) in self.table

class Node():
  def __init__(self):
    self.board = [[-1, -1, -1], [-1, -1, -1], [-1, -1, -1]]
    self.move = None
    self.player = Player.O
    self.children = None
    self.parent = None
    self.q_table = QTable()

  def copy(self, move):
    copy = Node()
    copy.board = deepcopy(self.get_board())
    copy.parent = self
    set_board_position(copy.get_board(), move, self.get_player().value)
    copy.move = move
    copy.children = None
    copy.set_score((0, 0))
    copy.q_table = self.q_table

    if self.q_table.has_state(copy.get_board()):
      self.q_table.put_state(copy.get_board(), copy.get_score())

    return copy

  def get_player(self):
    return get_current_player(self.board)

  def get_previous_player(self):
    if self.get_player() == Player.X:
      return Player.O
    else:
      return Player.X

  def get_board(self):
    return self.board

  def has_win_state(self):
    return detect_win_state(self.get_board()) != None

  def get_children(self):
    if self.children == None:
      self.children = []
      for move in get_available_moves(self.get_board()):
        self.children.append(self.copy(move))
      
    return self.children

  def get_heuristic(self):
    return calculate_board_fitness(self.board, self.player)

  def update_score(self):
    self.set_score((self.get_heuristic(), 0))

  def propagate_score(self):
    parent = self.parent
    discounted_score = self.get_score()[0]
    while parent != None:
      discounted_score = discounted_score * 0.8
      parent.set_score((parent.get_score()[0] + discounted_score, 0))
      parent = parent.parent

  def get_move(self):
    return self.move

  def has_children(self):
    return len(self.get_children()) > 0

  def get_move_count(self):
    return get_current_move(self.get_board())

  def display_board(self):
    display_board(self.get_board())

  def get_score(self):
    return self.q_table.get_state(self.get_board())

  def set_score(self, score):
    self.q_table.put_state(self.get_board(), score)
  
  def get_next_move(self):
    highest = None
    for child in self.get_children():
      if highest == None or child.get_score()[0] > highest.get_score()[0]:
        highest = child

    return highest
  
def calculate_ratio(o_wins, x_wins):
  if o_wins == 0:
    return 0
  
  if x_wins == 0:
    return o_wins

  return o_wins / x_wins

explore = 90
def computer_compute_move(root, depth=8):
  global explore
  if root.parent == None or explore < random.randint(0, 101):
    return random.choice(root.get_children())

  return root.get_next_move()

def computer_random_move(root):
  return random.choice(root.get_children())

_game_counter = 0
_draws = 0
_x_wins = 0
_o_wins = 0

_games_to_play = 1000000
_global_sum = 0
_global_draws = 0
_global_x_wins = 0
_global_o_wins = 0
_generation = 0

root = Node()
root.get_children()

_cohort_size = 1000
_generation_size = 100 * _cohort_size

while True:
  head = root
  if _game_counter == 0 or _game_counter % _generation_size == 0:
    print()
    print(f'\tGAME\tRATIO\tLOSSES\tWINS\tDRAWS\tGLOBAL\t')

  if _game_counter > 0 and _game_counter % _cohort_size == 0:
    _ratio = calculate_ratio(_o_wins + _draws, _x_wins)
    _global_sum = _global_sum + _ratio
    _generation = _generation + 1
    
    
    if _ratio < _global_sum / _generation:
      print(f'\t\033[91m{_game_counter}\t{_ratio:3.2f}\t{_x_wins}\t{_o_wins}\t{_draws}\t{(_global_sum/_generation):3.2f}\033[0m')
    else:
      print(f'\t\033[92m{_game_counter}\t{_ratio:3.2f}\t{_x_wins}\t{_o_wins}\t{_draws}\t{(_global_sum/_generation):3.2f}\033[0m')
    _draws = 0
    _x_wins = 0
    _o_wins = 0

  while head.has_children():
    if _game_counter > _games_to_play:
      explore = 105
      head.display_board()

    if head.get_player() == Player.X:
      if _game_counter > _games_to_play:
        head = menu_prompt(head)
      else:
        head = computer_random_move(head)
    else:
        
      new_head = computer_compute_move(head)
      head.set_score(new_head.get_score())
      head = new_head

    if _game_counter > _games_to_play:
      head.display_board()

    if head.has_win_state():
      head.update_score()
      head.propagate_score()
      if head.get_previous_player() == Player.X:
        _x_wins += 1
      else:
        _o_wins += 1
      break

  if not head.has_win_state():
    _draws += 1

  _game_counter += 1
