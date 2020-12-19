class QTable():
  def __init__(self):
    self.table = {}

  def put_state(self, board, score):
    self.table[self._board_hash(board)] = score

  def get_state(self, board):
    if self.has_state(board):
      return self.table[self._board_hash(board)]
    return (0, 0)

  def has_state(self, board):
    return self._board_hash(board) in self.table

  def _board_hash(self, board):
    b_hash = ''
    for row in board:
      for cell in row:
        b_hash = b_hash + '' + str(cell)

    return b_hash
