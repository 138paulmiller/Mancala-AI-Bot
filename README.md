 
# Mancala-AI-Bot
A Mancala AI Bot implemented in Python using Flask.
 
# Install
To launch this application make sure you are in a Python2.7 environment with Flask setup.
 
1.Installing Python2.7
 
- On Mac
 brew install python python-pip
 
- On Debian based Linux
 
 sudo apt-get install python python-pip python-wheel
 
- On Fedora based Linux
  sudo yum install python python-pip python-wheel
 
2. To install Flask
 
 pip2 install flask
 
# Running
There are two options to interact with the AI agents. The user can either play against the AI using the command terminal or use our webpage. Notice that Flask is only necessary to have if you plan to use the webpage.
 
### Webpage
Navigate to the Mancala-AI-Bot folder in your terminal and run command:
 
 FLASK_APP=mancala_flask.py flask run
 
The application should then be launched on a local server and can be viewed by a browser.
For more information about Flask you can visit: http://flask.pocoo.org


Monte Carlo simulation
 
Files:
            board.py
            mcts.py
            mancala.py
 
The mancala.py is the main file that utilizes the Board class and the MCTS class.
In the main of mancala allows you to run the following:
            
- Run a single game of agent using Monte Carlo simulation and an agent
that chooses moves randomly.
- Run an analysis of multiple games using multiple number of simulation
and represents the results in a graph
- Run a single game of agent using Monte Carlo simulation and an agent using Minimax
with Alpha-beta pruning
- Run two agents using Minimax to battle against each other
 
System requirements
            Using terminal with python 2.7
            Python libraries used: numpy, matplotlib, random, multiprocessing, and math
            There are no open source code used in the development for Monte Carlo simulation.
 
How to run:
 
            python mancala.py
 
            A prompt will appear in the console.
            “1 : Monte Carlo Ai vs Random player"
            "2 : Monte Carlo Ai analysis"
            "3 : Monte Carlo Ai vs Minimax with pruning"
            "4 : Minimax Ai vs Minimax Ai"
 
            Enter choice ->
 
            Enter 1-4 to run different functions and watch games or analysis unfold.
            Option 2 requires numpy and matplotlib to display a graph.

# Mancala Rules
 
There are many variations of rules for Mancala since it is one of the oldest games. The particular rules we used allowed for the AI's to calculate a path to victory fairly. By fairly, we mean that some variations of this game are not perfect allowing for an extremely calculate first move to end the game. [Here is an example of a MatLab script that will win in one turn if played  first](https://blogs.mathworks.com/loren/2017/05/22/how-to-win-all-marbles-in-mancala-on-your-first-move-with-matlab/#a7d8ead7-8e1a-499d-b104-2a7d385db486). So, the set of rules we chose allow for a fun experience against the AI.
 
### Setup
There are 12 slots and 2 bowls on each board. This is a 2-player game meaning that each player has 6 slots and 1 bowl. The six slots facing the player, and the bowl to their right. There are 48 pebbles the entire game. Initially, 4 pebbles are dropped into each of the 12 slots.
 
### Playing
The first player to start is randomly chosen. The player must choose one of the 6 slots on their side that has pebbles. To move, the player picks up all the pebbles in that slot and moves right one slot for each pebble. For each slot visited, the player drops one pebbles and stops until there are no pebbles. When the player visits the bowl on their side, the player drops one pebbles into it. There are three cases of what to do depending on where the last pebble is dropped. If the player drops his last pebbles into an empty slot, or a slot on the other player's side their turn is over. If the player drops his last pebbles onto a nonempty slot on their side, the player must pick up all the pebbles in that slot and continue the move. And, lastly  the player drops his last pebbles into his bowl, the player can select a new slot play if available.
The game ends when there are no more pebbles on the board. There is a popular variant where the game ends when one player’s side is empty, however, we discovered an AI with a deep enough lookahead is capable of winning in one turn if it plays first.
 
# Algorithms
Mancala is trivially a decision problem since each AI agent must decide on what move to play.
Each of our AI agents make use of varying algorithms for decision making.  
We used:
- Minimax with Alpha-Beta Pruning
- Monte-Carlo Tree Search
- Evolutionary Algorithm with binary encoded moves
 
The algorithms we used vary in the method of deciding. For example, our Minimax, Monte-Carlo and Evolutionary algorithms make use of traversing current game tree. However, both searching algorithms use different heuristics to limit the state space being search. The state space for an entire game is very large, and running an exhaustive search on the entire game tree will run in about O(6^n) time. Where n is number of total turns, where each player has at most 6 choices.
A naive exhaustive searching algorithm for this is completely inefficient, so adding a maximum lookahead depth allows us to bound the search space for our algorithms making them run in a reasonable enough time to play against.
 
### Heuristics
All our algorithms make use of a variable heuristic function. This function analyzes the current state of the board to help the AI make the best possible decision.
This heuristic can be used to:
- Maximize AI's score
- maximize the difference between the AI and players score
- Maximize the number of pebbles on the AI side  
- Maximize the difference between the number of pebbles on AI side from player’s side
- Or a weighted polynomial of the above (x = score, p = pebble diff = x+p*0.3)
 
Modifying the evaluation heuristic also changes the difficulty of the AI. For instance, in the Minimax algorithm, evaluating the score performs much better than evaluating number of pebbles on each side. Also, measuring the relative score between the player and the AI performs better than just maximizing the AI. The reasoning behind this would be that the AI not only maximizes his own score, but also makes sure that the next best move for the player will be far lower than the AI's score. So, it would preference 9 vs 3 over 10 vs 8.
 
### Playability
Each of our algorithms performs differently.
The Minimax algorithm with Alpha-Beta pruning is a more exhaustive searching making it much slower but also much more difficult to win. With a turn lookahead depth of around 6-8, the AI is quick enough to play and very difficult to beat. However, if the lookahead is not set and the AI searches the entire game tree, the AI will be unbeatable, however due to the time complexity of the game tree the AI takes far too long to decide on a move even with alpha-beta pruning. So, both Monte-Carlo and Evolutionary Algorithm decision making approaches are much more user-friendly.
The Monte-Carlo algorithm makes uses of a probabilistic adversarial decision making which chooses the other players most likely move. This allows the algorithm to be far less exhaustive making it capable of making more human-like decisions, since the enemy may not always choose the predicted move.
The Evolutionary algorithm makes use of binary programs that encode possible moves for the AI. The programs are initially randomly and evolved using probabilistic mutation and crossover. Each population is evaluated by testing the heuristic for each next potential move, and the programs with the highest score move are chosen by the probability of their score.  
 
### Conclusion
This was a very interesting project. Since the game tree is simple enough to visualize, yet results in an exponential explosion of possible game states. Each AI plays the game differently.
 
# Class descriptions
# Board
There is a Board class that provides both the AI and the player an interface to making moves and getting feedback on which player's turn is next. Mancala has two sides of 6 slots which is mapped onto a single integer array of length 12. Each move is modulates across the array, adding values to the current players bowl. Player one's bowl gets incremented if the player passes index 5 while, player two's bowl get incremented if they pass index 11. Each player is an integer value 0 or 1, and the choice of their move is offset by the player value multiplied by 6. This simulates the mapping of 2X6 array into a single 12X1 array where each player value (0, 1) represents the current row of slots. This made it much easier to simply iterate the index when dropping pebbles into the slots.
2D to 1D mapping
 
            A1[WIDTH*HEIGHT] == A2[WIDTH][HEIGHT]
            A2[row][col] == A1[WIDTH*row+col]  
   
This class provides the following features to get the current game state:
- move(player, slot)
    
      Accepts a player and the given move and takes the pebbles from the slot and distributes them across the board. If dropped into a slot on the player’s side, it will pick up those pebbles and continue the turn. This function returns the id to the next player, since the player may get to play again
- check_move(player, move)
  
      Takes a player id and the slot to make the move and checks if the slot has any pebbles
- has_move(player)
  
      Takes a player id and if the player has any pebbles of his side, will return true. Otherwise false
- game_over()
  
      If all pieces are in the bowls, game over
- get_score(player)
  
      Returns the score from a given player id
- get_pieces()
  
      Returns the number of pieces on a given player's side
- getBowls()
  
      Get the values of the bowls
- getBoard()
  
      Get the 1D array of slots
 
 
# AI Agents
All AI agents must contain a function named move that takes in the current board and returns the next player. This is the base object being used.

# Minimax

- eval_heuristic(board)
- alphabeta( board, alpha, beta, player, depth)

- get_move_score( move)

- move_parallel( board)
- move_serial( board)
- move(board, parallel=True)



# Monte Carlo Search Tree

### Node
The node class has the following properties:
Number of node visits
Score along the path
Possible actions on the current board configuration
Has children
Next move from this board configuration
Move taken to this board configuration

And has the following functions to update properties:
update_score(self, score_param):
update_visit(self, visit_param):
update_nextPlayer(self, nextPlayer_param): 
update_move_taken(self, slot):
 
### Monte Carlo Search Tree
Mcts class has the following property:
 Player id
 Node        
And the class has the following functions:
- expansion(current, player)
- selection( current, player)
- UCB1(current)
- rollout( current, player)
- findMove(current, player, iterate)
- mcts_vs_random(iterate)
- analysis()
 
#### Monte Carlo Simulation
 
Monte Carlo simulation has four stages: Selection, Expansion, Rollout, and Back propagation. Selection will decide which node to explore with a balance of exploration and exploitation using UCB1 formula. Expansion generates all possible moves with the current board configuration. Rollout simulates n-number of random games with the current board configuration. And Back propagation will update all node or previous board configurations values.
 
### Analysis
The agent uses a Monte Carlo simulation and runs on different parameters. Initial number of simulation taken before picking the next move is 5 and increments by 5 for each set of 30 games. The second analysis is similar but of set of 50 games. 

