
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
		return ( move >= 0 and move < 6) and  (0 != self.board[player*6+move])


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


