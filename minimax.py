'''
Paul Miller
Mancala AI Bot
	Implemented using Alpha-Beta Pruning to find best move.
'''
import os, sys
import mancala_board
import multiprocessing
from multiprocessing import Process


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
		if board.game_over() or depth <= 0:
			value = self.eval_heuristic(board)
		elif player == self.player:
			cut = False
			value = -48
			i = 0
			while i < 6 and not cut:
				board_copy = mancala_board.Board(board)
								
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
				board_copy = mancala_board.Board(board)
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
		board_copy = mancala_board.Board(self.board)
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
			board_copy = mancala_board.Board(board)
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

	def move(self, board, parallel=True):
		if parallel:
			return self.move_parallel(board)
		else:
			return self.move_serial(board)


#			 Helper functions
# upack the async map args , expecting (ai_obj, move)
def unpack_get_move_score(args):
	score = args[0].get_move_score(args[1])
	return score


