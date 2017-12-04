import random, mancala_board

class genesis:
    def __init__(self, player, lookahead, relative_score=False, horde=False, relative_horde=False):
        self.player = player
        # other player to opponent
        self.opponent = (player + 1) % 2
        self.search_count = 0  # is not locked, does not update in parallel move
        self.lookahead = lookahead
        self.board = None
        self.horde = horde  # evaluate by number of pieces on ai's side
        self.relative_score = relative_score  # judge score by difference between opponent's
        self.relative_horde = relative_horde  # judge score by difference between opponent's
        self.generation = self.init_pop()
        self.total_fitness = 0

    '''
        Summary:            initializes the first generation
        generation size:    is anywhere from 0 to 100
        strand size:        is based on lookahead
        When used:          used at initialization
        returns:            population
    '''
    def init_pop(self):
        population = []
        for index in range(0, 200):
            strand = ""
            for i in range(0, self.lookahead):
                num = random.randint(0, 5)
                strand += str(num)
            if strand not in population:
                population.append(strand)
        return population

    '''
        Summary:            encodes a strand of moves from dec to binary
        strand size:        each binary representation is formatted to four binary spaces
        When used:          to create next generation
        returns:            no return
    '''
    def gen_encode(self):
        for i in range(0, len(self.generation)):
            tup = (self.strand_encode(self.generation[i][0]), self.generation[i][1])
            self.generation[i] = tup

    '''
        Summary:            encodes strand elements
        strand size:        each binary representation is formatted to four binary spaces
        When used:          to create next generation
        returns:            binary strand
    '''
    def strand_encode(self, strand):
        tmp = ""
        tmp_strand = ""
        for i in range(0, len(strand)):
            tmp = format(int(strand[i]), "b")
            # if statements used to ensure formatting to 4 place binary size
            if len(tmp) == 3:
                tmp = str(0) + tmp

            if len(tmp) == 2:
                tmp = "00" + tmp

            if len(tmp) == 1:
                tmp = "000" + tmp
            tmp_strand = tmp_strand + tmp
            #spaces binary sequences apart makes decoding easy
            if i + 1 != len(strand):
                tmp_strand += " "
        return tmp_strand

    '''
        Summary:            decodes strand elements
        strand size:        each binary representation is formatted back to decimal
        When used:          to evaluate population
        returns:            no return
    '''
    def gen_decode(self):
        for i in range(0, len(self.generation)):
            tup = (self.strand_decode(self.generation[i][0]), self.generation[i][1])
            self.generation[i] = tup

    '''
        Summary:            decodes strand elements
        strand size:        each binary representation is formatted back to decimal
        When used:          to evaluate population
        returns:            returns decimal strand of moves
    '''
    def strand_decode(self, strand):
        tmp = ""
        tmp_strand = strand.split(" ")

        for i in range(0, len(tmp_strand)):
            tmp += str(int(tmp_strand[i], 2))
        return tmp

    '''
        Summary:            tests the strand to ensure that the combinations are valid moves
        When used:          during each population test
        returns:            returns bool true if valid false if invalid
    '''
    def test_strand(self, population, strand_id, player, istuple=False):
        # variable init
        if istuple:
            strand = population[strand_id][0]
        else:
            strand = population[strand_id]
        strand_health = True
        board_copy = mancala_board.Board(self.board)

        # for each move in strand test if move is possible option
        i = 0
        while i < len(strand) and i < self.lookahead:
        # for i in range(0, len(strand)):
            if 0 == board_copy.board[player * 6 + int(strand[i])]:
				strand_health = False
            elif strand_health:
				board_copy.move(player, int(strand[i]))
				player = (player + 1) % 2
            i+=1

        # returns if move sequence is possible
        return strand_health

    '''
        Summary:            gets score of strand
        When used:          during each population test
        returns:            returns score resulting from moves strand
    '''
    def get_strand_score(self, population, strand_id, player):
        # variable init
        strand = population[strand_id]
        board_copy = mancala_board.Board(self.board)
        strand_score = 0
        # for each move in strand test if move is possible option
        for i in range(0, len(strand)):
            board_copy.move(player, int(strand[i]))
            strand_score += self.eval_heuristic(board_copy)
            player = (player + 1) % 2

        # returns if move sequence is possible
        return strand_score

    '''
        Summary:            assigning fitness by get_strand_score and sums total_fitness
        When used:          after each generation creation
        returns:            returns score resulting from moves strand
    '''
    # evaluates if the moves are even possible to make
    def test_pop(self, player):
        # variable init
        pop_length = len(self.generation) - 1
        strand_id = 0
        self.total_fitness = 0

        # tests each strand in population
        while strand_id <= pop_length:
            # if move is not possible removes from the population
            # if not self.test_strand(self.generation, strand_id, player):
            #    self.generation.remove(self.generation[strand_id])
            #    strand_id -= 1
            #    pop_length -= 1
            # else the sequence is evaluated.
            #else:
            strand_score = self.get_strand_score(self.generation, strand_id, player)
            self.total_fitness += int(strand_score)
            # strand = self.strand_encode(population[strand_id])
            tup = (self.generation[strand_id], strand_score)
            self.generation[strand_id] = tup
            strand_id += 1

    '''
        Summary:            returns how many moves are able to be made in generation
        When used:          before pruning moves that cant be made
        returns:            returns number of legal moves
    '''
    # evaluates if the moves are even possible to make
    def count_legal_moves(self, player):
        # variable init
        pop_length = len(self.generation) - 1
        strand_id = 0
        count = 0
        # tests each strand in population
        while strand_id <= pop_length:
            # if move is not possible removes from the population
            if self.test_strand(self.generation, strand_id, player, True):
                count +=1
            strand_id += 1
        return count


    '''
        Summary:            tests the population ensuring valid moves and assigning fitness by get_strand_score
        When used:          before move selection
        returns:            returns score resulting from moves strand
    '''
    # evaluates if the moves are even possible to make
    def test_pop_and_prune(self, player):
        # variable init
        pop_length = len(self.generation) - 1
        strand_id = 0

        # tests each strand in population
        while strand_id <= pop_length:
            # if move is not possible removes from the population
            if not self.test_strand(self.generation, strand_id, player, True):
                self.generation.remove(self.generation[strand_id])
                pop_length -= 1
            strand_id += 1


    '''
        Summary:            sorts the generation by fitness then reverses to have the most fit in the front
        When used:          before each gen prune to ensure the best are selected
        returns:            no return
    '''
    def sortandreverse(self):
        generation = sorted(self.generation, key=self.get_key)
        self.generation.reverse()

    '''
        Summary:            used to get the fitness from tuple
        When used:          during sor and reverse
        returns:            returns item
    '''
    def get_key(self, item):
        return item[1]

    '''
        Summary:            used to determine fitness of strand
        When used:          during test pop
        returns:            returns possible score
    '''
    def eval_heuristic(self, board):
        score = board.get_score(self.player)
        pieces = 0
        if self.horde:
            if self.relative_horde:
                pieces = (pieces - board.get_pieces(self.opponent))
            else:
                pieces = board.get_pieces(self.player)
        if self.relative_score:
            score = (score - board.get_score(self.opponent))
        return score + pieces

    '''
        Summary:            used to shorten generation size by 75 percent
        When used:          used before gen evolution
        returns:            no return
    '''
    def gen_prune(self):
        portion = len(self.generation) * .25
        pruned_gen = []
        for i in range(0, int(portion)):
            pruned_gen.append(self.generation[i])

    '''
        Summary:            used to return a member index for crossover
        When used:          used crossover
        returns:            id of member to be used in crossover
    '''
    def roullete_wheel_selection(self):
        temp_sum = 0
        i = 0
        random_fitness = random.randint(0, self.total_fitness-10)
        while i < len(self.generation)-1 and temp_sum < random_fitness:
            i += 1
            temp_sum += int(self.generation[i][1])
        return i

    '''
        Summary:            evolves gen using crossover and mutation
                            creates a gen of 50 using the last generation
        When used:          after move is made
        returns:            no return
    '''
    def gen_evolution(self):
        evolution_list = []
        self.sortandreverse() # needed for roullete wheel selection
        while len(evolution_list) < 200:
            #strand_one_id = random.randint(0, len(self.generation) - 1)
            #strand_two_id = random.randint(0, len(self.generation) - 1)
            strand_one_id = self.roullete_wheel_selection()
            strand_two_id = self.roullete_wheel_selection()
            strand_two_id = self.strand_uniq_id_test(self.generation, strand_one_id, strand_two_id)
            cross_strand = self.gen_crossover(self.generation[strand_one_id][0], self.generation[strand_two_id][0])
            gen_next_strand = self.mutate_strand(cross_strand)
            gen_next_strand = self.strand_decode(gen_next_strand)
            if len(gen_next_strand) == self.lookahead:
                if self.eval_new_strand(gen_next_strand):
                    evolution_list.append(gen_next_strand)
        # print evolution_list
        self.generation = evolution_list

    '''
        Summary:            used to ensure an oversized strand is not created
        When used:          used during generation evolution
        returns:            returns bool used to allow strand to be added.
    '''
    def eval_new_strand(self, strand):
        strand_health = True
        for i in range(0, len(strand)):
            if int(strand[i]) >= 6:
                strand_health = False
        return strand_health

    '''
        Summary:            used to ensure a strand is not picked double for crossover
        When used:          during gen evolution
        returns:            returns strand two id (index)
    '''
    def strand_uniq_id_test(self, generation, strand_one_id, strand_two_id):
        while strand_one_id == strand_two_id:
            strand_two_id = random.randint(0, len(generation) - 1)
        return strand_two_id

    '''
        Summary:            crosses over two strings based on random point
        When used:          during gen evolution
        returns:            returns the crossed over string
    '''
    def gen_crossover(self, strand_one, strand_two):
        tmp_one = []
        tmp_two = []
        tmp_one = strand_one.split(" ")
        tmp_two = strand_two.split(" ")
        sequence_one = ""
        sequence_two = ""

        for i in range(0, len(tmp_one)):
            sequence_one += tmp_one[i]
            sequence_two += tmp_two[i]

        crosspoint = random.randint(1, len(strand_one) - 1)

        # print ("crossing " + str(strand_one) + " and " + str(strand_two) + " at " + str(crosspoint))
        crossover_strand = strand_one[0:crosspoint + 1] + strand_two[crosspoint + 1:]
        return crossover_strand

    '''
        Summary:            used to mutate newly crossed over string
        When used:          during gen evolution
        returns:            returns mutated strand
    '''
    def mutate_strand(self, strand):
        if(random.randint(0, 100) <= 20):
          mutate_point = random.randint(1, len(strand) - 1)
          if strand[mutate_point] == '0':
              strand = strand[0:mutate_point] + '1' + strand[mutate_point + 1:]
          else:
              strand = strand[0:mutate_point] + '0' + strand[mutate_point + 1:]
          # print strand
        return strand

    '''
        Summary:            selects random move from pruned list
        When used:          to make a move
        returns:            returns the slot to move
    '''
    def random_move_select(self):
        print("gen length before random move is selected", len(self.generation))
        strand_id = random.randint(0, len(self.generation) - 1)
        return int(self.generation[strand_id][0][0])
    #def random_move_select(self):
        #print("generation length", len(self.generation))
        #strand_id = random.randint(0, len(self.generation) - 1)
        # self.generation = self.gen_decode()
        # self.gen_decode()
        #print("testing generation in random_move_select",self.generation[0][0],self.generation[strand_id][0])
        #print("testing generation in random_move_select",int(self.generation[strand_id][0][0:4],2))
        # print("testing generation in random_move_select",self.generation[strand_id][0][0:4].fromBinaryToInt())
        #return int(self.generation[strand_id][0])
        #return int(self.generation[strand_id][0][0:4],2)

    '''
        Summary:            used to make a move
        When used:          when its the ai's turn
        returns:            returns the slot chosen to move
    '''
    def move(self, board):
		valid = False
		move = 0
		while not valid:        
			self.board = mancala_board.Board(board)
			self.generation = self.init_pop()
			self.test_pop(self.player)
			for i in range(50):
			    self.gen_encode()
			    self.gen_evolution()
			    self.test_pop(self.player) # to reinitialize total_fitness
			    #print ("generation", i)
			x = 50
			temp_lookahead = self.lookahead
			while self.count_legal_moves(self.player) == 0:
			    if self.lookahead > 1:
			        self.lookahead -= 1
			    self.gen_encode()
			    #print ("generation", x)
			    self.gen_evolution()
			    self.test_pop(self.player) # to reinitialize total_fitness
			    x +=1
			self.test_pop_and_prune(self.player)
			self.lookahead = temp_lookahead
			self.sortandreverse()
			#print ("selecting most move with fitness: ", self.generation[0][0][0], self.generation[0][0][1])
			# self.gen_prune()
			move = int(self.generation[0][0][0])
			valid = board.check_move(self.player, move)	
		return move


