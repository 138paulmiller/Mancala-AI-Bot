Readme.txt

Monte carlo simulation 

Files:
	board.py
	mcts.py
	mancala.py

	The mancala.py is the main file that utilizes the Board class and the MCTS class.
	In the main of mancala allows you to run the following:
	
	- Run a single game of agent using Monte Carlo simulation and an agent that choses moves randomly.
	
	- Run an analysis of multiple games using multiple number of simulation
		and represents the results in a graph

	- Run a single game of agent using Monte Carlo simulation and an agent using Minimax 
		with Alpha-beta pruning

	- Run two agents using Minimax to battle against each other




System requirements
	Using terminal with python 2.7
	Python libraries used: numpy, matplotlib, random, multiprocessing, and math
	There were no open source code used in the development for Monte carlo simulation.

How to run:

	python mancala.py

	This will prompt you options:
	'1 : Monte Carlo Ai vs Random player"
    "2 : Monte Carlo Ai analysis"
    "3 : Monte Carlo Ai vs Minimax with pruning"
    "4 : Minimax Ai vs Minimax Ai"

    Enter choice ->

    Enter 1-4 to run different functions and watch games or analysis unfold.


