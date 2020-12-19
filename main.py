import random
from copy import deepcopy
from itertools import groupby
import numpy as np
from scipy.ndimage import rotate
from rendering.ConsoleColours import ConsoleColours
from rendering.display_board import display_board
from rendering.render_table_row import render_table_row
from rendering.display_user_input_menu import display_user_input_menu
from logic.Player import Player
from logic.value_is_neutral import value_is_neutral
from logic.ai.QTable import QTable

def get_available_moves(board):
  available_moves = []
  for i in range(0, len(board)):
    for j in range(0, len(board)):
      if board[i][j] == -1:
        available_moves.append((i, j))

  return available_moves

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
    return 1.0
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

explore = 80
def computer_compute_move(root, depth=8):
  global explore
  if explore < random.randint(0, 101):
    return random.choice(root.get_children())

  return root.get_next_move()

def compute_random_move_set():
  return [random.randint(0, i) for i in reversed(range(0, 9, 2))]

def computer_random_move(root):
  return random.choice(root.get_children())

def select_move_by_index(root, index):
  if index > len(root.get_children()):
    return root.get_children()[-1]

  return root.get_children()[index]

def is_progression(ratio, global_ratio):
  return ratio < global_ratio

def should_render_heading(game_counter, generation_size):
  return game_counter == 0 or game_counter % generation_size == 0

def should_render_stats(game_counter, cohort_size):
  return game_counter > 0 and game_counter % cohort_size == 0

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

random_move_set = compute_random_move_set()
while True:
  head = root
  if should_render_heading(_game_counter, _generation_size):
    print(render_table_row([
        "GAME",
        "RATIO",
        "LOSSES",
        "WINS",
        "DRAWS",
        "GLOBAL",
      ],
      ConsoleColours.PURPLE))

  if should_render_stats(_game_counter, _cohort_size):
    _ratio = calculate_ratio(_o_wins + _draws, _x_wins)
    _global_sum = _global_sum + _ratio
    _generation = _generation + 1
    _global_sum_ratio = _global_sum / _generation
    
    print(render_table_row(
      [
        str(_game_counter),
        str(f'{_ratio:3.2f}'),
        str(_x_wins),
        str(_o_wins),
        str(_draws),
        str(f'{_global_sum_ratio:3.2f}')
      ],
      ConsoleColours.RED if is_progression(_ratio, _global_sum_ratio) else ConsoleColours.GREEN))

    _draws = 0
    _x_wins = 0
    _o_wins = 0

  if _game_counter > _games_to_play:
    explore = 101
    head.display_board()

  move_index = 0
  while head.has_children():
    if head.get_player() == Player.X:
      if _game_counter > _games_to_play:
        head = display_user_input_menu(head)
      else:
        head = select_move_by_index(head, random_move_set[move_index])
        move_index = move_index + 1
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
        random_move_set = compute_random_move_set()
      else:
        _o_wins += 1
      break

  if not head.has_win_state():
    _draws += 1

  _game_counter += 1
