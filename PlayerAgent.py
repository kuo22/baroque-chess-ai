import BC_state_etc as BC
import time

BLACK = 0
WHITE = 1
start_time = 0

def makeMove(currentState, currentRemark, timelimit=10000):
    global start_time
    start_time = time.perf_counter()

    # Compute the new state for a move.
    # This is a placeholder that just copies the current state.
    newState = BC.BC_state(currentState.board)

    # Fix up whose turn it will be.
    newState.whose_move = 1 - currentState.whose_move

    best_state = None
    last_best = None
    current_max_ply = 1
    while current_max_ply < 20:
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
                if newState.board[i][j] % 2 == 0 and best_state.board[i][j] == 1:
                    position_B = (i, j)
            if newState.whose_move == BLACK:
                if (newState.board[i][j] % 2 == 0 and newState.board[i][j] != 0) and best_state.board[i][j] == 0:
                    position_A = (i, j)
                if (newState.board[i][j] == 0 or newState.board[i][j] % 2 == 1) and (best_state.board[i][j] != 0 and best_state.board[i][j] % 2 == 0):
                    position_B = (i, j)
    
    move = (position_A, position_B)
    # Make up a new remark
    newRemark = "I'll think harder in some future game. Here's my move"

    return [[move, best_state], newRemark]

def alpha_beta(current_state, current_depth, max_ply, player, alpha, beta, time_lim):
    global start_time
    current_time = time.perf_counter
    if current_time - start_time > time_lim * 0.9:
        return current_state

    moves = valid_moves(current_state)
    if not moves or current_depth == max_ply:
        return current_state

    optimal_state = current_state
    for move in moves:
        state = alpha_beta(move, current_depth + 1, max_ply, 1 - player, alpha, beta, time_lim)
        move_value = static_eval(move) # to be changed depending on implementation of static eval
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
    return "Newman"

def introduce():
    return "I'm Newman Barry, a newbie Baroque Chess agent."

def prepare(player2Nickname):
    pass


