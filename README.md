# Reinforcement  learning Tic-Tac-Toe AI

This is fairly a naive reinforcement learning AI implementation for the game Tic-Tac-Toe.

![Screenshot of the program running. It prints table of data with 6 columns: GAME, RATIO, LOSSES, WINS, DRAWS and Global. The GAME column increments by 1000 for each new row and RATIO, LOSSES, WINS and DRAWS describe how many of those 1000 games resulted in wins, losses or draws. The RATIO describes the number of WINS plus DRAWS divided by the number of LOSSES each row. The GLOBAL column is the overall ratio of WINS plus DRAWS divided by the number of LOSSES for all games so far.](images/demo.png)

This program plays 1000000 training games of Tic-Tac-Toe against a randomized policy. It implements a very loose interpretation of the [Bellman Equation](https://en.wikipedia.org/wiki/Bellman_equation). For each decision it can either exploit its past experience or it can explore alternative options, this is randomly controlled with a bias towards exploitation. It's important to find the right balance between exploitation/exploration. Explore too much during training, it'll struggle to optimise good decision making policies; explore too little during training, it might over optimise locally optimal policies. Once all of the training games have played through, it allows a human played to take over from the randomized policy.

The randomized policy pre-computes its move sequence before each training game, which gets replayed until the reinforcement AI adapts to counter it.

I've adapted [Minimax Tic-Tac-Toe](https://github.com/spacekitcat/minimax-tic-tac-toe-python), a project I did as a Kata a few weeks earlier. This adapted version tries to get good at the game through experience rather than exhaustively traversing the decision tree. It uses the directed graph to model a Markov Decision Process (MDP), every node in this graph shares a reference to an auxiliary state table. When the game reaches a terminal state (win/draw/lose), the reinforcement AI updates the state's cumulative score in the state table, it then traverses the graph backwards to visit all of the previous states in chronological order. For each parent state, it visits, it discounts the terminal state's score at a fixed rate (beta) before updating the state table.

Each node can generate a list of child nodes, each one describes an action and the resultant state. When it is the reinforcement AI's turn to play, it can either choose an action at random (explore), or it can pick the Action it thinks will yield the greatest reward based on past experience (exploitation). This implementation has a constant that controls the probability of it choosing exploration or exploitation, it currently has a 90% bias towards exploitation.

The program drops into interactive mode after training so that the policy can be evaluated.

N.B. The first decision is always random because you can force a draw from any move made in move 1 (X) or move 2 (O), randomizing the first move is a hack to stop it over training one specific path at the expense of all others.

## Performance

It's reasonably fast, I estimate it can do 1000 games a second.

## Running

You need Python 3.

```bash
git clone https://github.com/spacekitcat/reinforement-tic-tac-toe-python.git
cd reinforement-tic-tac-toe-python
pip3 install -r requirements.txt
python3 main.py
```

## Results

I like to think that tic-tac-toe has three classes of AI policy:

- Class 1: Understands the rules, is able to form a line and block a line. Has a 50/50 chance of winning/losing against other class 1 players. Will lose against Class 2 or above.
- Class 2: Knows at least one predicament scenario and how to block most of them, will win against class 1 players, will draw with class 2 players, might occasionally be caught off guard by a class 3 policy.
- Class 3: Knows all of the predicament scenario and how to block all of them, will never do worse than a draw against any policy.

From my evaluations, the worst policy the training algorithm produces is a class 1 policy. It's more likely to produce a class 2 and will sometimes produce a class 3 policy.

I'd like to fine tune the training to consistently produce a class 3 policy. I think a higher number of generations would improve the chances, but I feel there's room to improve the learning efficiency of the algorithm to get more out of each training generation. The first area I'd want to look at is the explore/exploit ratio, I think this needs to by dynamically adjusted with some selection criteria for finding the optimal value. The second thing I'd like to look at is enhancing the bad game replay mechanism to collect replay games with good learning potential that it replays periodically.

## Next steps

The next step is design a version of this program where the random AI is replaced with one that purely exploits the data in state table. I think a more adversarial training program will bridge the gap between the sort of policies currently generated and the optimal strategy of [Minimax Tic-Tac-Toe](https://github.com/spacekitcat/minimax-tic-tac-toe-python).

## License

MIT
