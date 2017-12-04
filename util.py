import Board
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


