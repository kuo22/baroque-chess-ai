'''
terminator_BC_Player.py
'''

import BC_state_etc as BC
import terminator_BC_module_validStates as vs
# import terminator_BC_module_staticEval as se
import terminator_BC_module_zobrist_hashing as zh
import time

BLACK = 0
WHITE = 1
start_time = 0

def makeMove(currentState, currentRemark, timelimit=10):
    global start_time
    start_time = time.perf_counter()

    # Compute the new state for a move.
    # This is a placeholder that just copies the current state.
    newState = BC.BC_state(currentState.board, currentState.whose_move)

    # Fix up whose turn it will be.
    # newState.whose_move = currentState.whose_move

    best_state = None
    last_best = None
    current_max_ply = 1
    while current_max_ply < 10:
        last_best = best_state
        best_state = alpha_beta(newState, 0, current_max_ply, newState.whose_move, float("-inf"), float("inf"), timelimit)
        current_max_ply += 1
        end_time = time.perf_counter()
        if end_time - start_time > timelimit * 0.90:
            best_state = last_best
            break 

    # move = ((6, 4), (3, 4)) <-- what move looks like
    position_A = False
    position_B = False
    # Checks the board to determing the position of the piece that moved
    for i in range(8):
        for j in range(8):
            if newState.whose_move == WHITE:
                # Old cell has piece on my side -> New cell is empty, then this is the old position 
                if newState.board[i][j] % 2 == 1 and best_state.board[i][j] == 0:
                    position_A = (i, j)
                # Old cell is empty or has opponent's piece -> New cell has piece on my side, then this is the new position
                if newState.board[i][j] % 2 == 0 and best_state.board[i][j] % 2 == 1:
                    position_B = (i, j)
            else:
                if (newState.board[i][j] % 2 == 0 and newState.board[i][j] != 0) and best_state.board[i][j] == 0:
                    position_A = (i, j)
                if (newState.board[i][j] == 0 or newState.board[i][j] % 2 == 1) and (best_state.board[i][j] != 0 and best_state.board[i][j] % 2 == 0):
                    position_B = (i, j)
    
    move = (position_A, position_B)
    #print('the coordinates: ' + str(move))

    # Change who's turn
    best_state.whose_move = 1 - currentState.whose_move

    # Make up a new remark
    newRemark = "I'll think harder in some future game. Here's my move"

    return [[move, best_state], newRemark]

# Game search tree algorithm
def alpha_beta(current_state, current_depth, max_ply, player, alpha, beta, time_lim):
    global start_time
    current_time = time.perf_counter()
    if current_time - start_time > time_lim * 0.9:
        return current_state

    moves = vs.valid_moves(current_state)
    if not moves or current_depth == max_ply:
        return current_state

    optimal_state = current_state
    # For each valid move, find the best move in the next ply
    for move in moves:
        state = alpha_beta(move, current_depth + 1, max_ply, 1 - player, alpha, beta, time_lim)
        move_value = 0
        hash_value = zh.hash_state(state)
        # Check if state has been hashed already.  Add to the hash table if not with its corresponding static evaluation value.
        if hash_value in zh.zob_table:
            move_value = zh.zob_table[hash_value]
        else:
            move_value = staticEval(state)
            zh.zob_table[hash_value] = move_value
        if player == WHITE:
            if move_value > alpha:
                alpha = move_value
                if current_depth == 0:
                    optimal_state = move
                else:
                    optimal_state = state
        else:
            if move_value < beta:
                beta = move_value
                if current_depth == 0:
                    optimal_state = move
                else:
                    optimal_state = state
        
        if alpha >= beta:
            return optimal_state

    return optimal_state

def nickname():
    return "Terminator"

def introduce():
    return "I come from the future where people actually play Baroque Chess.  My sole purpose is to destroy it so no one has to play this abomination."

def prepare(player2Nickname):
    zh.init_table()




######################

# given a barque state object evaluate the position of the board.
# WHITE is assumed to be the maximizing player and BLACK the minimizing

# Like in chess how we associate a given point value to each piece.
# the most basic form of understanding the position of the game
# Uses the piece number / 2 as the key and the piece value as the value
# 1 = Pincer, 2 = Coordinator, 3 = Leaperm 4 = imitator, 5 = withdrawer, 6 = King, 7 = Freezer
# 0 = EMPTY square
PIECE_VALUES = {0:0, 1:1, 2:2, 3:5, 4:5, 5:2, 6:10000, 7:8}
weights = {'piece':1, 'freezing':1, 'withdraw':1 }

DIAGONAL_MOVES = [(1,-1), (1,1), (-1,1), (-1,-1)]
ROOK_MOVES = [(0,1), (1,0), (-1,0), (0,-1)]
QUEEN_MOVES = ROOK_MOVES + DIAGONAL_MOVES

def staticEval(board):
    white_score = 0
    black_score = 0
    for i, row in enumerate(board.board):
        for j, piece in enumerate(row):

            ortho_neighbors = get_neighbors(board, i, j, ROOK_MOVES)
            diag_neighbors = get_neighbors(board, i,j, DIAGONAL_MOVES)
            all_neighbors = ortho_neighbors + diag_neighbors

            # find piece score: you get a better score if you have more pieces
            if piece % 2 == 0:
                black_score += weights['piece'] * PIECE_VALUES[piece // 2]
            else:
                white_score += weights['piece'] * PIECE_VALUES[piece // 2]

            # find freezing score: you get a better score if you have more enemy pieces frozen
            #                    your score is higher if you freeze higher valued pieces
            if piece == 14: # black freezer
                black_score += weights['freezing'] * sum([PIECE_VALUES[x // 2] for x in all_neighbors if x % 2 == 1 ])
            elif piece == 15:
                white_score += weights['freezing'] * sum([PIECE_VALUES[x // 2] for x in all_neighbors if x % 2 == 0 ])


            # find withdrawer score: higher score if withdrawer has a chance of capturing a good piece
            elif piece == 10:
                black_score += weights['withdraw'] * sum([PIECE_VALUES[x // 2] for x in all_neighbors if x % 2 == 1 ])
            elif piece == 11:
                white_score += weights['withdraw'] * sum([PIECE_VALUES[x // 2] for x in all_neighbors if x % 2 == 0 ])

            # Pawn/pincer structure: Give points if the pawns have lots of self pinching power: i.e. they lie in an open


            # Open 
            

    return white_score - black_score

def get_neighbors(board, i, j, directions):
    neighbors = []

    for (dr, dc) in directions:
        try:
            neighbors.append(board.board[i + dr][j + dc])
        except:
            pass

    return neighbors

