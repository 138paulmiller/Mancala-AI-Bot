# Mancala-AI-Bot
A Mancala AI Bot implemented in Python using Minimax with Alpha-Beta Pruning for decision making.

To launch this application make sure you are in a Python2.7 environment with Flask setup.
Navigate to the Mancala-AI-Bot folder in your terminal and run command: FLASK_APP=mancala_flask.py flask run
The application should then be launched on a local server.

For more information about Flask you can visit: http://flask.pocoo.org

# Rules

There are many variations of rules for Mancala since it is one of the oldest games. The particular rules we used allowed for the AI's to calculate a path to victory fairly. By fairly, we mean that some variations of this game are not perfect allowing for a extrememly calculate first move to end the game. [Here is an example of a MatLab script that will win in one turn if played  first](https://blogs.mathworks.com/loren/2017/05/22/how-to-win-all-marbles-in-mancala-on-your-first-move-with-matlab/#a7d8ead7-8e1a-499d-b104-2a7d385db486). So the set of rules we chose allow for a fun experience against the AI.

### Setup
There are 12 slots and 2 bowls on each board. This is a 2-player game meaning that each player has 6 slots and 1 bowl. The six slots facing the player, and the bowl to their right. There are 48 marbles the entire game. Initially, 4 marbles are dropped into each of the 12 slots. 

### Playing
The first player to start is randomly chosen. The player must choose one of the 6 slots on their side that has marbles. To move, the player picks up all the marbles in that slot and moves right one slot for each marble. For each slot visited, the player drops one marble and stops until there are no marbles. When the player visits the bowl on their side, tje plauer drops one marble into it. There are three cases of what to do depending on where tje last marble is dropped. If the player drops his last marble into an enpty slot, or a slot on the other player's side their turn is over. If the player drops his last marble onto a nonempty slot on their side, tje player must pick up all the marbles in that slot and continue the move. And, lastly  the player drops his last marble into his bowl, the player can select a new slot play if available. 
The game ends when there are no more marbles on the board. There is a popular variant where the game ends when one players side is empty, however, an we discovered an AI with a deep enough lookahead is capable of winning in one turn if it plays first. 
