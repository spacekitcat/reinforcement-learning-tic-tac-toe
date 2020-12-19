from rendering.ConsoleColours import ConsoleColours

def render_table_row(cells, colour, spacing=9):
  row = f"{colour}"
  for cell in cells:
    row = row + cell.rjust(spacing)

  return row + f'{ConsoleColours.ENDC}'
