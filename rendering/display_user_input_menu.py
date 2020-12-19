import qprompt

def create_menu(node_list):
  menu = qprompt.Menu()
  for i in range(0, len(node_list)):
    menu.add(str(i), node_list[i])

  return menu

def display_user_input_menu(root):
  menu = create_menu(root.get_children())
  return menu.show(returns="desc", header=str.format("Turn {}, {} to move", root.get_move_count(), root.get_player()))
