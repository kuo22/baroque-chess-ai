# given a current Baroque Board, returns a generator which generates all the 
# valid move for the player whose turn it currently is
WHITE = 1
BLACK = 0

# NOTE: set to a non-integer value so that EMPTY % 2 != WHITE or BLACK
EMPTY = 0.5

from BC_state_etc import BC_state
from BC_state_etc import parse
import itertools

def valid_moves(current_board):

    # NOTE: deals with the annoying fact that the empty squares are the same as the black squar)es % 2
    # This allow for convenient checks using PIECE % 2 == whose_move to check that a given piece matches
    # the color of the player whose turn it is (or use != to check that the color is opposite) rather than
    # breaking down into a bunch of if WHITE else if BLACK statements.
    board = BC_state(current_board.board, current_board.whose_move)
    for i, row in enumerate(board.board):
        for j, square in enumerate(row):
            if square == 0: board.board[i][j] = EMPTY

    whose_move = board.whose_move

    for i, row in enumerate(board.board):
        for j, square in enumerate(row):
            position = (i,j)
            if square != EMPTY and square % 2 == whose_move and no_freezer_near(board, position):
                # pincer
                if square in [2,3]:
                    print("pincer moves (start, end)")
                    for move in pincer_moves(board, position): yield (position, move)

                # coordinator
                elif square in [4,5]:
                    print("coordinator moves (start, end)")
                    for move in coordinator_moves(board, position): yield (position, move)
                
                # leaper
                elif square in [6,7]:
                    print("leaper moves (start, end)")
                    for move in leaper_moves(board, position): yield (position, move)

                # imitator
                elif square in [8,9]:
                    print("imitator moves (start, end)")
                    for move in imitator_moves(board, position): yield (position, move)

                # withdrawer
                elif square in [10,11]:
                    print("withdrawer moves (start, end)")
                    for move in withdrawer_moves(board, position): yield (position, move)

                # king
                elif square in [12,13]:
                    print("king moves (start, end)")
                    for move in king_moves(board, position): yield (position, move)

                # freezer
                else:
                    print("freezer Moves (start, end)")
                    for move in freezer_moves(board, position): yield (position, move)


# position is in the form (row, column)

def pincer_moves(board, position):
    row = position[0]
    col = position[1]
    num_rows = len(board.board)
    num_cols = len(board.board[0])

    k = 1
    # 0 is the empty tile
    while col+k < num_cols and board.board[row][col + k] == EMPTY:
        yield (row, col + k)
        k += 1

    k = 1
    while col - k >= 0 and board.board[row][col - k] == EMPTY:
        yield (row, col - k)
        k += 1
    
    k = 1
    while row + k < num_rows and board.board[row + k][col] == EMPTY:
        yield (row + k, col)
        k += 1

    k = 1
    while row - k >= 0 and board.board[row - k][col] == EMPTY:
        yield (row - k, col)
        k += 1

def coordinator_moves(board, position):
    return itertools.chain(pincer_moves(board, position), diagonal_moves(board, position)) 

def leaper_moves(board, position):
    row = position[0]
    col = position[1]
    num_rows = len(board.board)
    num_cols = len(board.board[0])
    whose_move = board.whose_move

    k = 1
    # NOTE: if board piece's number % 2 == whose_move, then that board piece is the 
    # same color as the leaper. Cannot jump over friendly pieces.
    while col+k < num_cols and board.board[row][col + k] % 2 != whose_move:
        if board.board[row][col + k] == EMPTY:
            yield (row, col + k)
        k += 1

    k = 1
    while col - k >= 0 and board.board[row][col - k] % 2 != whose_move:
        if board.board[row][col - k] == EMPTY:
            yield (row, col - k)
        k += 1
    
    k = 1
    while row + k < num_rows and board.board[row + k][col] % 2 != whose_move:
        if board.board[row + k][col] == EMPTY:
            yield (row + k, col)
        k += 1

    k = 1
    while row - k >= 0 and board.board[row - k][col] % 2 != whose_move:
        if board.board[row - k][col] == EMPTY:
            yield (row - k, col)
        k+=1

    k = 1
    while col+k < num_cols and row + k < num_rows and board.board[row + k][col + k] % 2 != whose_move:
        if board.board[row + k][col + k] == EMPTY:
            yield (row + k, col + k)
        k += 1

    k = 1
    while col - k >= 0 and row + k < num_rows and board.board[row + k][col - k] % 2 != whose_move:
        if board.board[row + k][col - k] == EMPTY:
            yield (row + k, col - k)
        k += 1
    
    k = 1
    while row - k >= 0 and col - k >= 0 and board.board[row - k][col - k] % 2 != whose_move:
        if board.board[row - k][col - k] == EMPTY:
            yield (row - k, col - k)
        k += 1

    k = 1
    while row - k >= 0 and col + k < num_cols and board.board[row - k][col + k] % 2 != whose_move:
        if board.board[row - k][col + k] == EMPTY:
            yield (row - k, col + k)

        k += 1


def imitator_moves(board, position):
    return []

def withdrawer_moves(board, position):
    return itertools.chain(pincer_moves(board, position), diagonal_moves(board, position)) 

def king_moves(board, position):
    num_rows = len(board.board)
    num_cols = len(board.board[0])
    whose_move = board.whose_move

    adj_squares = [(i,j) for i in range(max(0, position[0]-1), min(num_rows, position[0] + 2)) for j in range(max(0, position[1] - 1), min(num_cols, position[1] + 2))]
    adj_squares.remove(position)

    for square in adj_squares:
        # whose move = 1 for white and % 2 == 1 for white pieces
        # whose move = 0 for black and % 2 == EMPTY for black pieces
        # i.e. king can move as long as there isnt a friendly piece there
        if board.board[square[0]][square[1]] % 2 != whose_move:
            yield square

    

def freezer_moves(board, position):
    return itertools.chain(pincer_moves(board, position), diagonal_moves(board, position)) 

# Used to reduce redundancy as many of the pieces move like a queen
def diagonal_moves(board, position):    
    row = position[0]
    col = position[1]
    num_rows = len(board.board)
    num_cols = len(board.board[0])
    
    k = 1
    while col+k < num_cols and row + k < num_rows and board.board[row + k][col + k] == EMPTY:
        yield (row + k, col + k)
        k += 1

    k = 1
    while col - k >= 0 and row + k < num_rows and board.board[row + k][col - k] == EMPTY:
        yield (row + k, col - k)
        k += 1
    
    k = 1
    while row - k >= 0 and col - k >= 0 and  board.board[row - k][col - k] == EMPTY:
        yield (row - k, col - k)
        k += 1

    k = 1
    while row - k >= 0 and col + k < num_cols and board.board[row - k][col + k] == EMPTY:
        yield (row - k, col + k)
        k += 1

# returns True if there is no adjacent freezer.
# Flag is to help in the case of a nearby imitator to prevent further rounds of recursion
# i.e. if there is in imitator nearby, it could be acting as a freezer so I have to check if a freezer
# is nearby that imitator. I wouldn't want a chain of imitators to cause this to recurse more than one 
# level as imitators CANNOT imitate themselves, so I stop that from happening with one flag
# NOTE: assumes immitators and freezers do NOT cancel out
def no_freezer_near(board, position, flag=False):
    num_rows = len(board.board)
    num_cols = len(board.board[0])

    # doesnt matter if we count the piece centered at position as it cannot
    # be an immoblizer of the opposite color of whose turn it is
    adj_squares = [(i,j) for i in range(max(0, position[0]-1), min(num_rows, position[0] + 2)) for j in range(max(0, position[1] - 1), min(num_cols, position[1] + 2))]

    for square in adj_squares:
        piece = board.board[square[0]][square[1]]
        if board.whose_move == WHITE:
            if piece == 14: return False

            # NOTE: checks if there is an imitator acting as a freezer nearby
            elif piece == 8 and not flag and not no_freezer_near(board,square, flag=True): return False 
        elif board.whose_move == BLACK and piece == 15:
            if piece == 15: return False

            # NOTE: checks if there is an imitator acting as a freezer nearby
            elif piece == 9 and not flag and not no_freezer_near(board,square, flag=True): return False 

    return True

# ===================================== TESTING CODE

INITIAL = parse('''
c l i w k i l f
p p p p p p p p
- - - - - - - -
- - - - - - - -
- - - - - - - -
- - - - - - - -
P P P P P P P P
F L I W K I L C
''')

INITIAL = parse('''
c l i w k i l f
- - p p p p p p
- - - - - - - -
- - - - - - - -
- - - - - - - -
- - - - - - - -
P P P P P P P P
F L I W K I L C
''')

initial_board = BC_state(INITIAL)
initial_board.whose_move = WHITE
print(initial_board)

for move in valid_moves(initial_board): print(move)
