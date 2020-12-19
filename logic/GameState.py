class GameState():
  def __init__(self, games_per_generation):
    self.game_per_generation = games_per_generation
    self._global_game_counter = 0
    self._local_draw_counter = 0
    self._local_x_win_counter = 0
    self._local_o_win_counter = 0
  
  def get_games_per_generation(self):
    return self.game_per_generation

  def get_global_game_count(self):
    return self._global_game_counter

  def get_local_draw_count(self):
    return self._local_draw_counter

  def get_local_x_win_count(self):
    return self._local_x_win_counter

  def get_local_o_win_count(self):
    return self._local_o_win_counter
  
  def increment_global_game_counter(self):
    self._global_game_counter = self._global_game_counter + 1
  
  def increment_local_draw_counter(self):
    self._local_draw_counter = self._local_draw_counter + 1

  def increment_local_x_win_counter(self):
    self._local_x_win_counter = self._local_x_win_counter + 1

  def increment_local_o_win_counter(self):
    self._local_o_win_counter = self._local_o_win_counter + 1

  def get_error_rate(self):
    if self.get_local_o_win_count() == 0:
      return 0
  
    if self.get_local_x_win_count() == 0:
      return self.get_local_x_win_count()

    return ((1.0 / self.get_games_per_generation()) * self.get_local_x_win_count())

  def reset_local(self):
    self._local_draw_counter = 0
    self._local_x_win_counter = 0
    self._local_o_win_counter = 0
