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

Navigate to the Mancala-AI-Bot folder in your terminal and run command: 

  FLASK_APP=mancala_flask.py flask run

The application should then be launched on a local server and can be viewed by a browser.
For more information about Flask you can visit: http://flask.pocoo.org

# Mancala Rules

There are many variations of rules for Mancala since it is one of the oldest games. The particular rules we used allowed for the AI's to calculate a path to victory fairly. By fairly, we mean that some variations of this game are not perfect allowing for a extrememly calculate first move to end the game. [Here is an example of a MatLab script that will win in one turn if played  first](https://blogs.mathworks.com/loren/2017/05/22/how-to-win-all-marbles-in-mancala-on-your-first-move-with-matlab/#a7d8ead7-8e1a-499d-b104-2a7d385db486). So the set of rules we chose allow for a fun experience against the AI.

### Setup
There are 12 slots and 2 bowls on each board. This is a 2-player game meaning that each player has 6 slots and 1 bowl. The six slots facing the player, and the bowl to their right. There are 48 pebbles the entire game. Initially, 4 pebbles are dropped into each of the 12 slots. 

### Playing
The first player to start is randomly chosen. The player must choose one of the 6 slots on their side that has pebbles. To move, the player picks up all the pebbless in that slot and moves right one slot for each pebble. For each slot visited, the player drops one pebbles and stops until there are no pebbless. When the player visits the bowl on their side, tje plauer drops one pebbles into it. There are three cases of what to do depending on where tje last pebble is dropped. If the player drops his last pebbles into an enpty slot, or a slot on the other player's side their turn is over. If the player drops his last pebbles onto a nonempty slot on their side, tje player must pick up all the pebbless in that slot and continue the move. And, lastly  the player drops his last pebbles into his bowl, the player can select a new slot play if available. 
The game ends when there are no more pebbless on the board. There is a popular variant where the game ends when one players side is empty, however, an we discovered an AI with a deep enough lookahead is capable of winning in one turn if it plays first. 

# Algorithms
Mancala is triavially a decision problem since each AI agent muct decide on what move to play.
Each of our AI agents make use of varying algotithms for decision making.  
We used:
- Minimax with Alpha-Beta Pruning
- Monte-Carlo Tree Search
- Genetic Algorithm with binary encoded moves
The algortihms we used vary in the method of deciding. For example, our Minimax, Monte-Carlo and Genetic algorithms make use of traversing current game tree. However, both of the searching algorithms use different heuristics to limit the state space being search. The state space for an entire game is very large, and running an exhaustive search on the entire game tree will run in about O(6^n) time. Where n is number of total turns, where each player has at most 6 choices.
A naive exhaustive searching algorithm for this is completely inefficient, so adding a maximum lookahead depth allows us to bound the search space for our algorithms making them run in a reasonable enough time to play against. 
### Heuristics 
All our algorithms make use of a variable heuristic function. This function analyzes the current state of the board to help the AI make the best possible decision. 
This heuristic can be used to:
- Maximize AI's score
- maximize the difference bewteen the AI and players score
- Maximize the number of pebbles on the AI side  
- Maximize the difference bewteen the number of pebbles on AI side from players side
- Or a weighted polynomial of the above (x = score, p = pebble diff = x+p*0.3)

### Playability 
Each of our algorithms performs differently. The Minimax algorithm with Alpha-Beta pruning is a more exhaustive searching making it much slower but also much more difficult to win. With a turn lookahead depth of around 6-8, the AI is quick enough to play and very difficult to beat. However, if the lookahead is not set and the AI searches the entire game tree, the AI will be unbeatable, however due to the time complexity of the game tree the AI takes far too long to decide on a move even with alpha-beta pruning. So, both Monte-Carlo and Genetic Algorithm decision making approaches are much more user-friendly. The Monte-Carlo algorithm makes uses of a probabilistic adversarial decision making which chooses the other players mosty likely move. This allows the algorithm to be far less exhaustive making it capable of making more human-like decisions, since the enemy may not always choose the predicted move. 
