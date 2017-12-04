#!/usr/bin/env python
import sys, os,random # used to catch interrupts
import mancala_board 
import inspect
import minimax, genesis, mcts # AI agents
from flask import Flask, redirect, render_template, url_for, jsonify, request

app = Flask(__name__)
app._static_folder = os.path.dirname(os.path.realpath(__file__))+'/static'
print app._static_folder
# use these variables for players to prevent error checking on board
DEBUG = True


class Human:
	def __init__(self, player):
		self.player = player


def get_user_move(board, player):
	#if DEBUG:
	#	return random.randint(0,5)
	valid = False
	move = 0
	while not valid:
		try:
			# get move input (1-6), offset to index (0-5)
			move = raw_input('>')
			move = int(move)-1
			while move < 0 or move > 5:
				print 'Pick slots (1-6)'
				move = int(	raw_input('>'))-1
			valid = True
		except:
			if move == 'quit':
				valid = True
			else:
				print 'Pick slots (1-6) Integers only!'
				valid = False
	return move


def resetBoard():
	return mancala_board.Board()

def updateCurrentPlayer():
	global nextMove
	global board
	if not board.has_move(nextMove):
		nextMove = (nextMove+1)%2
	if nextMove == playerOne.player:
		current = playerOne
	else:
		current = playerTwo
	return current


def initiatePlayerMove(current_player, move):
	next = board.move(current_player.player, move)
	return next

@app.route('/launchAIBattle', methods=['POST'])
def launchAIBattle():
	return render_template('mancala.html', game_type="AI vs AI")

@app.route('/launchPlayerVersusMinimax', methods=['POST'])
def launchPlayerVersusMinimax():
	global agent
	agent = "Minimax"
	print "Launching ", agent
	return render_template('mancala.html', game_type="Player vs AI", ai_agent="Minimax")


@app.route('/launchPlayerVersusGenesis', methods=['POST'])
def launchPlayerVersusGenesis():
	global agent
	agent = "Genesis"
	print "Launching ", agent
	return render_template('mancala.html', game_type="Player vs AI",ai_agent="Genesis")


@app.route('/launchPlayerVersusMonteCarlo', methods=['POST'])
def launchPlayerVersusMonteCarlo():
	global agent
	agent = "MonteCarlo"
	print "Launching ", agent			
	return render_template('mancala.html', game_type="Player vs AI",ai_agent="MonteCarlo")


@app.route('/initializeVersusAIVariables')
def initializeVersusAIVariables():
	global playerOne
	global playerTwo
	global current
	global nextMove
	global board
	global agent
	P1 = 0
	P2 = 1
	# multiprocess computaion
	print "board", agent	
	board = mancala_board.Board()
	playerOne = Human(P1)
	# ai Player

	print agent, 'sdddddddddddddddddddddddddddd'
	if agent == "Minimax":
		playerTwo = minimax.AI(P2, 8)
	elif agent == "Genesis":
		playerTwo = genesis.genesis(P2, 3)
	elif agent == "MonteCarlo":
		playerTwo = mcts.MCTS(P2, mancala_board.Board())
	
	print "Versus AI Agent:", agent
	# starting player is random
	# current = random.randint(0,1)  # todo this line is a fucking problem......
	current = None
	nextMove = random.randint(0,1)
	return jsonify({'initialized' : True})

@app.route('/initializeAIBattleVariables')
def initializeAIBattleVariables():
	global playerOne
	global playerTwo
	global current
	global nextMove
	global parallel
	global board
	P1 = 0
	P2 = 1
	# multiprocess computaion
	parallel = True
	lookahead = 8 # AI lookahead depth, set to negative to search entire game
	# board = Board() commented out, moved it to global scope in hopes dynamic
	playerOne = minimax.AI(P1, lookahead, relative_score= False)
	#ai_horder = AI(P2, lookahead, horde=True) # hordes pieces on its side
	playerTwo = minimax.AI(P2, lookahead, relative_score= True, horde=True, relative_horde=True) #horde relative is better then not
	nextMove = random.randint(0,1)
	starting_ai = nextMove
	current = None # ai with current turn
	board = mancala_board.Board()
	return jsonify({'initialized' : True})

@app.route('/makePlayerMove')
def makePlayerMove():
	global current
	global nextMove
	print "Players Move"
	# todo remove below from this function, only ok for continuous AI loops
	# current = getCurrentPlayer(playerOne, playerTwo, nextMove)
	playerMove = request.args.get('playerMove', type=int)
	print("testing player move")
	print (request.args)
	print(playerMove)
	nextMove = initiatePlayerMove(current, playerMove)
	print board
	return jsonify({'board' : board.getBoard(),'bowls': board.getBowls(), 'gameOver': board.game_over(),'winnerString': getWinnerIfGameIsOver()})



@app.route('/makeNextAIMove')
def makeNextAIMove():
	global playerTwo
	global nextMove
	global board
	print "AI Move"
	# todo remove below from this function, only ok for continuous AI loops
	# current = getCurrentPlayer(playerOne, playerTwo, nextMove)
	print board	
	print "AI ", current, "Thinking" 
	move = current.move(board)
	print board, move, current.player
	nextMove = board.move(current.player, move)

	
	print "Got move"
	return jsonify({'board' : board.getBoard(),'bowls': board.getBowls(), 'gameOver': board.game_over(),'winnerString': getWinnerIfGameIsOver()})



@app.route('/getCurrentPlayerNumber')
def getCurrentPlayerNumber():
	global current
	current = updateCurrentPlayer()
	return jsonify({'playerNumber' : current.player})

def getWinner():
	print ' 		FINAL'
	print board
	p1_score = board.get_score(0)
	p2_score = board.get_score(1)
	winnerString = ''

	if p1_score > p2_score:
		winnerString = "Player One Wins!"
	elif p1_score < p2_score:
		winnerString = "Player Two Wins!"
	else:
		winnerString = "It\'s a tie!"
	return winnerString

def getWinnerIfGameIsOver():
	if board.game_over() == True:
		return getWinner()

@app.route('/')
def loadHomePage():
	return render_template('homepage.html')
