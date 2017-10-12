#!/usr/bin/env python
'''
Paul Miller
Mancala AI Bot
	Implemented using Alpha-Beta Pruning to find best move. 
'''
import multiprocessing
import random
import sys # used to catch interrupts

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



def ai_battle():
	#tests the different heuristics by having ai play each other
	P1 = 0
	P2 = 1
	# multiprocess computaion
	parallel = True
	lookahead = 8 # AI lookahead depth, set to negative to search entire game	
	board = Board()
	ai = AI(P1, lookahead, relative_score= False)
	#ai_horder = AI(P2, lookahead, horde=True) # hordes pieces on its side
	ai_relative = AI(P2, lookahead, relative_score= True, horde=True, relative_horde=True) #horde relative is better then not
	next = random.randint(0,1)
	
	starting_ai = next 
	ai_cur = None # ai with current turn
	
	while not board.game_over():
		
		if not board.has_move(next):
			next = (next+1)%2
		if next == ai.player:
			ai_cur = ai	
		else:
			ai_cur = ai_relative	
		move = ai_cur.move(board, parallel)
		print board
		## get the move for the ai player
		#if ai.player == ai_basic.player:				
		#	print 'Basic picked ', move+1			
		#else:
		#	print 'Horder picked ', move+1			
		next = board.move(ai_cur.player, move)
	
	print ' 		FINAL'
	print board
	p1_score = board.get_score(P1)
	p2_score = board.get_score(P2)

	if next == ai:				
		print  'P1 Started'
	else:
		print  'P2  Started' 
	if p1_score > p2_score:
		print 'P1 Wins!'
	elif p1_score < p2_score:
		print 'P2 Wins!'
	else:
		print 'It\'s a tie !'


def main():
	P1 = 0
	P2 = 1
	# multiprocess computaion
	parallel = True
	lookahead = 6 # AI lookahead depth, set to negative to search entire game	
	board = Board()
	# ai Player
	ai = AI(P2, lookahead)
	# starting player is random
	current_player = random.randint(0,1) 
	next = (current_player+1)%2
	move = 0
	while not board.game_over() and move != 'quit':		
		print board
		print '\nP'+str(current_player+1) + '\'s Turn' 
		# if the current player has a move, else switch
		if board.has_move(current_player):
			# not ai turn, user turn
			if current_player != ai.player:	
				move = ''
				next = current_player
				while current_player == next and board.has_move(current_player) and move != 'quit':
					move = get_user_move(board, current_player)					
					if not board.check_move(current_player, move) :
						print 'No pieces', move	
					if move != 'quit':
						next = board.move(current_player, move)					
						print board
						print 'Play again!'
						print '\nP'+str(current_player+1)
									
			else:
				# AI turn		
				move = ai.move(board, parallel)
				# get the move for the ai player
				print '\tAI picked ', move+1			
				next = board.move(ai.player, move)
				# while AI has another move
				while ai.player == next and board.has_move(ai.player) and move != 'quit':
					print board				
					print '\tAI Playing Again...'
					move = ai.move(board, parallel)
					print '\tAI picked ', move+1			
					next = board.move(ai.player, move)	 
			# set player to the next			
			current_player = next
		else:
			print '\n P'+str(current_player+1) + ' has no moves!'
			current_player = (current_player+1)%2
	
	# If game is over and user did not quit
	if move != 'quit':
		print ' 		FINAL'
		print board
		p1_score = board.get_score(P1)
		p2_score = board.get_score(P2)
		if p1_score > p2_score:
			print 'Player 1 Wins!'
		elif p1_score < p2_score:
			print 'Player 2 Wins!'
		else:
			print 'It\'s a tie !'
	print 'Goodbye!'


if __name__ == '__main__':
	#main()  # user interactive
	ai_battle() # watch AI's battle it out
	#board = Board()
	#print 'State Space Size: ', get_state_space(board, 0, 10)
