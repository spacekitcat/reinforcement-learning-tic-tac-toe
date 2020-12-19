from logic.Player import Player

def value_is_neutral(value):
  return value != Player.X.value and value != Player.O.value
