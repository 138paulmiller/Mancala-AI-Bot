#!/usr/bin/env python
'''
Paul Miller
Mancala AI Bot
	Implemented using Alpha-Beta Pruning to find best move.
'''
import multiprocessing
from multiprocessing import Process
import random
import sys # used to catch interrupts
from flask import Flask, redirect, render_template, url_for, jsonify, request
app = Flask(__name__)

# use these variables for players to prevent error checking on board
DEBUG = True

class Board:
	def __init__(self, other=None):
		if other: #make copy
			self.board = [4,4,4,4,4,4,4,4,4,4,4,4]
			for i in range(0, len(other.board)):
				self.board[i] = other.board[i]
			self.bowl = [other.bowl[0], other.bowl[1]]
			self.move_num = other.move_num
		else:
			# player 0's side of board is board[0] and bowl[0]
			self.board = [4,4,4,4,4,4,4,4,4,4,4,4]
			self.bowl = [0,0]
			self.move_num = 0


	def move(self, player, slot):
		# add one piece in board until bowl
		# if still
		# 	remaining pieces roll them over into next players skip other players bowl
		# if in bowl and no remaining pieces, then play again
		# slot (0, 5), player (0,1)
		slot = slot + (player)*6;
		pieces = self.board[slot]
		self.board[slot] = 0
		next_player = player
		while pieces > 0:
			slot = (slot+1)%12
			# at players bowl,
			if slot == (player+1)*6%12:
				self.bowl[player]+=1
				next_player = player
				pieces -= 1 # drop piece in players bowl
			# if pieces, continue dropping in slots
			if pieces > 0:
				self.board[slot]+=1
				next_player = (player+1)%2 # next player
			pieces-=1
			# if no more pieces, and on player side, add those pieces if >1(just added)
			if pieces == 0 and slot < (player+1)*6 and slot > (player)*6 and self.board[slot] > 1:
				pieces = self.board[slot]
				self.board[slot] = 0
		self.move_num += 1
		return next_player

	def get_score(self, player):
		return self.bowl[player]

	def get_pieces(self, player):
		#number of pieces on players side
		pieces = 0
		for i in range(0, 6):
			pieces += self.board[player*6+i]
		return pieces


	def check_move(self, player, move):
		return ( move >= 0 and move <= 6) and  0 != self.board[player*6+move]


	def has_move(self, player):
		# if the player has any moves
		i = 0
		while i < 6 and  self.board[(player)*6+i] == 0:
			i+=1
		# if reached the end, not all zeroes
		return i != 6

	def game_over(self):
		# all pieces are in the bowls, game over
		return (self.bowl[0] + self.bowl[1]) == 48


	def __repr__(self):
		layout = '--------------'+ str(self.move_num) + '---------------\n'
		layout += 'P2:' + str(self.bowl[1]) + '      6 <-- 1   |\n       |'
		# show in reverse for player 1
		for p in reversed(self.board[6:14]):
			layout += str(p) + ' '
		layout += '|                    \n\n       |'
		for p in self.board[0:6]:
			layout += str(p) + ' '
		layout += '|\n       |  1 --> 6      P1: ' + str(self.bowl[0]) + '\n--------------------------------'
		return layout

	def getBowls(self):
		return self.bowl

	def getBoard(self):
		return self.board


class Human:
	def __init__(self, player):
		self.player = player

class AI:
	def __init__(self, player, lookahead, relative_score= False, horde=False, relative_horde=False):
		self.player = player
		# other player to opponent
		self.opponent = (player+1)%2
		self.search_count = 0 # is not locked, does not update in parallel move
		self.lookahead = lookahead
		self.board = None
		self.horde = horde # evaluate by number of pieces on ai's side
		self.relative_score = relative_score # judge score by difference between opponent's
		self.relative_horde = relative_horde # judge score by difference between opponent's


	def eval_heuristic(self, board):
		score =  board.get_score(self.player)
		pieces = 0
		if self.horde:
			if self.relative_horde:
				pieces = (pieces - board.get_pieces(self.opponent))
			else:
				pieces = board.get_pieces(self.player)
		if self.relative_score:
			score = (score - board.get_score(self.opponent))
		return score + pieces


	def alphabeta(self, board, alpha, beta, player, depth):
		value = 0
		# cound does not update correct when threaded, only works with serial move
		self.search_count += 1
		# traverse entire game to find best move
		if board.game_over() or depth == 0:
			value = self.eval_heuristic(board)
		elif player == self.player:
			cut = False
			value = -48
			i = 0
			while i < 6 and not cut:
				board_copy = Board(board)
				if board_copy.check_move(self.player, i):
					next_player = board_copy.move(self.player, i)
					value = max(value, self.alphabeta(board_copy, alpha, beta, next_player, depth-1))
					alpha  = max(value, alpha)
					if alpha >= beta:
						cut = True
				else: # penalize no moves
					alpha = -48
				i+=1
		else: # opponent
			cut = False
			value = 48
			i = 0
			# for each opponent move, check if its valid, if so get the value of the next possible move
			while i < 6 and not cut:
				board_copy = Board(board)
				# if i is a valid move
				if board_copy.check_move(self.opponent, i):
					next_player = board_copy.move(self.opponent, i)
					value = min(value, self.alphabeta(board_copy, alpha, beta, next_player, depth-1))
					beta  = min(value, beta)
					if alpha >= beta:
						cut = True
				else: # no moves
					beta = 48
				i+=1
		return value


	def get_move_score(self, move):
		value = -50
		board_copy = Board(self.board)
		next_player = self.player
		# repeats are prioritized by increasing score
		while next_player == self.player and board_copy.check_move(self.player, move):
			next_player = board_copy.move(self.player, move)
			# if the next player has no move, change to other player
			if not board_copy.has_move(self.player):
				next_player = (next_player+1)%2
			value = max(value, self.alphabeta(board_copy, -48, 48, next_player, self.lookahead))

		return value


	def move_parallel(self, board):

		move = 0
		#print 'AI Thinking...'
		try:
			pool = multiprocessing.Pool(multiprocessing.cpu_count())
			move = 0
			self.board = board
			# map all possible plays to unpack
			scores = pool.map_async(unpack_get_move_score, [(self,0), (self,1), (self,2), (self,3), (self,4), (self,5)]).get(60)
			scores = list(scores)
			# allow keyboard intteruptions
			for i in range(0, 6): # ignore first move, already chosen
				if scores[move] < scores[i]:
					move = i
		except KeyboardInterrupt:
			pool.terminate()
			sys.exit(-1)
		finally:
			pool.close()
		pool.join()
		return move

	# Simple NON-parallel approach
	def move_serial(self, board):
		alpha = -48
		beta = 48
		value = alpha
		i = move = 0
		# foreach move possible
		cut = False
		self.search_count = 0
		print 'AI Thinking...'
		# for each move, check if its valid, if so get the value of the next possible move
		while i < 6 and not cut:
			board_copy = Board(board)
			# if i is a valid move, else ignore
			if board_copy.check_move(self.player, i):
				next_player = board_copy.move(self.player, i)
				# if the next player has no move, change to other player
				if not board_copy.has_move(self.player):
					next_player = (next_player+1)%2
				# get next max move
				value = max(value, self.alphabeta(board_copy, alpha, beta, next_player, self.lookahead))
				if alpha < value:
					alpha = value
					move = i
				if alpha > beta:
					cut = True
			i+=1
		print 'Searched ', self.search_count, ' possibilities'
		return move

	def move(self, board, parallel):
		if parallel:
			return self.move_parallel(board)
		else:
			return self.move_serial(board)

#			 Helper functions
# upack the async map args , expecting (ai_obj, move)
def unpack_get_move_score(args):
	score = args[0].get_move_score(args[1])
	return score

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

# Performs BFS search to count number of possible states until a given Depth
def get_state_space(board, player, depth):
	count = 0
	if not board.game_over() and depth > 0:
		moves = [] # [(board,player) ,	...]
		# search siblings
		for i in range(0,6):
			if board.check_move(player, i):
				count += 1
				board_copy = Board(board)
				next_player = board_copy.move(player, i)
				moves.append((board_copy, next_player))
		# search sibling children
		for move in moves:
			count += get_state_space(move[0], move[1], depth-1)
	return count


def resetBoard():
	return Board()

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

# do this while game is not over
def makeAIBattleMove(current):
	move = current.move(board, parallel)
	print board
	next = board.move(current.player, move)
	return next

def initiatePlayerMove(current_player, move):
	next = board.move(current_player.player, move)
	return next

@app.route('/launchAIBattle', methods=['POST'])
def launchAIBattle():
	return render_template('mancala.html', game_type="AI vs AI")

@app.route('/launchPlayerVersusAI', methods=['POST'])
def launchPlayerVersusAI():
	return render_template('mancala.html', game_type="Player vs AI")

@app.route('/initializeVersusAIVariables')
def initializeVersusAIVariables():
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
	lookahead = 9 # AI lookahead depth, set to negative to search entire game
	board = Board()
	playerOne = Human(P1)
	# ai Player
	playerTwo = AI(P2, lookahead)
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
	playerOne = AI(P1, lookahead, relative_score= False)
	#ai_horder = AI(P2, lookahead, horde=True) # hordes pieces on its side
	playerTwo = AI(P2, lookahead, relative_score= True, horde=True, relative_horde=True) #horde relative is better then not
	nextMove = random.randint(0,1)
	starting_ai = nextMove
	current = None # ai with current turn
	board = Board()
	return jsonify({'initialized' : True})

@app.route('/makePlayerMove')
def makePlayerMove():
	global current
	global nextMove
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
	global current
	global nextMove
	# todo remove below from this function, only ok for continuous AI loops
	# current = getCurrentPlayer(playerOne, playerTwo, nextMove)
	nextMove = makeAIBattleMove(current)
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
