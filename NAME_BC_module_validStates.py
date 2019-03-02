# given a current Baroque Board, returns a generator which generates all the 
# valid move for the player whose turn it currently is
WHITE = 1
BLACK = 0

# NOTE: set to a non-integer value so that EMPTY % 2 != WHITE or BLACK
EMPTY = 0.5

QUEEN_MOVES = [(1,0), (0,1), (-1,0), (0,-1), (1,1), (-1,-1), (1, -1), (-1,1)]
ROOK_MOVES = [(1,0), (0,1), (-1,0), (0,-1)]

from BC_state_etc import BC_state

# For testing!
from BC_state_etc import parse
import time

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
                    for move in pincer_moves(board, position): yield move

                # coordinator
                elif square in [4,5]:
                    print("coordinator moves (start, end)")
                    for move in coordinator_moves(board, position): yield move
                
                # leaper
                elif square in [6,7]:
                    print("leaper moves (start, end)")
                    for move in leaper_moves(board, position): yield move

                # imitator
                elif square in [8,9]:
                    print("imitator moves (start, end)")
                    for move in imitator_moves(board, position): yield move

                # withdrawer
                elif square in [10,11]:
                    print("withdrawer moves (start, end)")
                    for move in withdrawer_moves(board, position): yield move

                # king
                elif square in [12,13]:
                    print("king moves (start, end)")
                    for move in king_moves(board, position): yield move

                # freezer
                else:
                    print("freezer Moves (start, end)")
                    for move in freezer_moves(board, position): yield move

# generate a new board object by moving the piece at 'position' to 'new_position'
def make_move(board, position, new_position):

    # make a new board
    new_board = BC_state(board.board, board.whose_move)

    # move the piece to its new square
    new_board.board[new_position[0]][new_position[1]] = new_board.board[position[0]][position[1]] 
    new_board.board[position[0]][position[1]] = EMPTY
    return new_board

# change all the EMPTY values back to zero
# all, changes whose turn it is so the board is ready to be returned
def revert_empty(board):
    for i, row in enumerate(board.board):
        for j, square in enumerate(row):
            if square == EMPTY:
                board.board[i][j] = 0

    board.whose_move = 1 - board.whose_move



def pincer_moves(board, position):
    '''
    board = current board before move has been made
    position = position of the piece to be moved on the board (row, col)

    returns: 
        new_board = new board object where given piece has been moved and all captures have been made
    '''
    row = position[0]
    col = position[1]

    for (dr, dc) in ROOK_MOVES:
        k = 1
        # had to add this condition because python allows negative indexing (i.e. list[-1])
        while row + k*dr >= 0 and col + k*dc >= 0:
            try:
                # if the square is empty (and all squares leading up to it by the else clause)
                # then it is a valid move
                if board.board[row + k*dr][col + k*dc] == EMPTY:
                    
                    new_position = (row + k*dr, col + k*dc)
                    print(new_position)
                    yield pincer_captures(board, position, new_position)
                    k += 1
                else:
                    # found an enemy or friendly piece that it cannot jump over/move past
                    break
            except:
                break


def pincer_captures(board, position, new_position):
    '''
    board = current board before move has been made
    position = old position of the piece on the board (row, col)
    new_position = new location of piece on the board (row, col)

    returns: 
        new_board = new board object where given piece has been moved and all captures have been made
    '''

    new_board = make_move(board, position, new_position)
    nrow = new_position[0]
    ncol = new_position[1]
    
    for (dr, dc) in ROOK_MOVES:
        # dr is change in row
        # dc is change in column
        try:
            # if theres a matching colored piece 2 steps away and an enemy one step away in this direction
            if new_board.board[nrow][ncol] % 2 == new_board.board[nrow + 2*dr][ncol + 2*dc] % 2 and new_board.board[nrow][ncol] % 2 != new_board.board[nrow + dr][ncol + dc] % 2:
                new_board.board[nrow + dr][ncol + dc] = EMPTY

        except:
            pass

    revert_empty(new_board)
    return new_board



def coordinator_moves(board, position):
    '''
    board = current board before move has been made
    position = position of the piece to be moved on the board (row, col)

    returns: 
        new_board = new board object where given piece has been moved and all captures have been made
    '''
    row = position[0]
    col = position[1]

    for (dr, dc) in QUEEN_MOVES:
        k = 1
        while row + k*dr >= 0 and col + k*dc >= 0:
            try:
                # if the square is empty (and all squares leading up to it by the else clause)
                # then it is a valid move
                if board.board[row + k*dr][col + k*dc] == EMPTY:
                    new_position = (row + k*dr, col + k*dc)
                    yield coordinator_captures(board, position, new_position)
                    k += 1
                else:
                    # square has an enemy or friendly piece. Cannot jumpy over these
                    break
            except:
                break

def coordinator_captures(board, position, new_position):
    '''
    board = current board before move has been made
    position = old position of the piece on the board (row, col)
    new_position = new location of piece on the board (row, col)

    returns: 
        new_board = new board object where given piece has been moved and all captures have been made
    '''

    new_board = make_move(board, position, new_position)
    nrow = new_position[0]
    ncol = new_position[1]

    # find the kings location
    for i, row in enumerate(new_board.board):
        for j, piece in enumerate(row):
            if piece in [12, 13] and piece % 2 == new_board.whose_move:
                king_row = i
                king_col = j
                break

    # if there is an enemy piece at the intersection of coordinator row and king column, capture it
    if new_board.board[nrow][king_col] % 2 != new_board.whose_move:
        new_board.board[nrow][king_col] = EMPTY

    # if there is an enemy piece at the intersection of coordinator row and king column, capture it
    if new_board.board[king_row][ncol] % 2 != new_board.whose_move:
        new_board.board[king_row][ncol] = EMPTY
    
    revert_empty(new_board)
    return new_board

def leaper_moves(board, position):
    '''
    board = current board before move has been made
    position = position of the piece to be moved on the board (row, col)

    returns: 
        new_board = new board object where given piece has been moved and all captures have been made
    '''
    row = position[0]
    col = position[1]
    whose_move = board.whose_move

    for (dr, dc) in QUEEN_MOVES:
        k = 1
        enemy_count = 0
        while row + k*dr >= 0 and col + k*dc >= 0:
            try:
                # can hop over at most one enemy
                if enemy_count > 1:
                    break

                # empty square; possible move
                elif board.board[row + k*dr][col + k*dc] == EMPTY:
                    new_position = (row + k*dr, col + k*dc)
                    yield leaper_captures(board, position, new_position, (dr, dc), k)

                # cannot jump over pieces on the same team
                elif board.board[row + k*dr][col + k*dc] % 2 == whose_move:
                    break

                # square contains an enemy piece
                else:
                    enemy_count += 1

                k += 1
            except:
                # array out of bounds; run off board
                break

def leaper_captures(board, position, new_position, direction, steps):
    '''
    board = current board before move has been made
    position = old position of the piece on the board (row, col)
    new_position = new location of piece on the board (row, col)

    returns: 
        new_board = new board object where given piece has been moved and all captures have been made
    '''

    new_board = make_move(board, position, new_position)
    row = position[0]
    col = position[1]
    dr = direction[0] 
    dc = direction[1]
        
    for k in range(1, steps):
        # dont have to worry about capturing a piece of the same color because
        # it would not be a valid move to jumpy over a teammate
        new_board.board[row + k*dr][col + k*dc] = EMPTY


    revert_empty(new_board)
    return new_board

# TODO FIX ME!
def imitator_moves(board, position):
    '''
    board = current board before move has been made
    position = position of the piece to be moved on the board (row, col)

    returns: 
        new_board = new board object where given piece has been moved and all captures have been made
    
    # NOTE there are a few special cases to consider for the imitator; mostly, it can move like a leaper when
    # capturing a leaper
    num_rows = len(board.board)
    num_cols = len(board.board[0])
    whose_move = board.whose_move

    for move in pincer_moves(board, position):
        yield move
    for move in diagonal_moves(board, position):
        yield move

    adj_squares = [(i,j) for i in range(max(0, position[0]-1), min(num_rows, position[0] + 2)) for j in range(max(0, position[1] - 1), min(num_cols, position[1] + 2))]
    adj_squares.remove(position)

    row = position[0]
    col = position[1]

    for square in adj_squares:
        piece = board.board[square[0]][square[1]]
        if piece - (1 - whose_move) == 6: ## if its a leaper of the opposite color
            dir = (square[0] - position[0], square[1] - position[1])
            
            k = 2
            new_row = row + k*dir[0]
            new_col = col + k*dir[1]
            while new_row >= 0 and new_row < num_rows and new_col >= 0 and new_col < num_cols and board.board[new_row][new_col] % 2 != whose_move:
                if board.board[new_row][new_col] == EMPTY:
                    leaper_moves.append((new_row, new_col))
                k += 1
                new_row = row + k*dir[0]
                new_col = col + k*dir[1]

    return leaper_moves + other_moves
    '''
    return []


# TODO IMPLEMENT ME!
def imitator_captures(board, position, new_position):
    '''
    board = current board before move has been made
    position = old position of the piece on the board (row, col)
    new_position = new location of piece on the board (row, col)

    returns: 
        new_board = new board object where given piece has been moved and all captures have been made
    '''

    new_board = make_move(board, position, new_position)
    row = new_position[0]
    col = new_position[1]

    revert_empty(new_board)
    return new_board

def withdrawer_moves(board, position):
    '''
    board = current board before move has been made
    position = position of the piece to be moved on the board (row, col)

    returns: 
        new_board = new board object where given piece has been moved and all captures have been made
    '''
    row = position[0]
    col = position[1]

    for (dr, dc) in QUEEN_MOVES:
        k = 1
        while row + k*dr >= 0 and col + k*dc >= 0:
            try:
                # if the square is empty (and all squares leading up to it by the else clause)
                # then it is a valid move
                if board.board[row + k*dr][col + k*dc] == EMPTY:
                    new_position = (row + k*dr, col + k*dc)
                    yield withdrawer_captures(board, position, new_position, (dr, dc))
                    k += 1
                else:
                    # square has an enemy or friendly piece. Cannot jumpy over these
                    break
            except:
                break

def withdrawer_captures(board, position, new_position, direction):
    '''
    board = current board before move has been made
    position = old position of the piece on the board (row, col)
    new_position = new location of piece on the board (row, col)
    direction = the direction the piece is moving in (dr, dc)

    returns: 
        new_board = new board object where given piece has been moved and all captures have been made
    '''

    new_board = make_move(board, position, new_position)
    row = position[0]
    col = position[1]

    try:
        if new_board.board[row - dr][col - dc] % 2 != new_board.whose_move:
            new_board.board[row - dr][col - dc] = EMPTY
    except:
        # ran off of board
        pass

    revert_empty(new_board)
    return new_board

    
def king_moves(board, position):
    '''
    board = current board before move has been made
    position = position of the piece to be moved on the board (row, col)

    returns: 
        new_board = new board object where given piece has been moved and all captures have been made
    '''
    whose_move = board.whose_move
    row = position[0]
    col = position[1]
    
    for (dr, dc) in QUEEN_MOVES:
        # whose move = 1 for white and % 2 == 1 for white pieces
        # whose move = 0 for black and % 2 == EMPTY for black pieces
        # i.e. king can move as long as there isnt a friendly piece there
        if row + dr >= 0 and col + d  >= 0 and board.board[row + dr][col + dc] % 2 != whose_move:
            yield king_captures(board, position, (row + dr, col + dc))


def king_captures(board, position, new_position):
    '''
    board = current board before move has been made
    position = old position of the piece on the board (row, col)
    new_position = new location of piece on the board (row, col)

    returns: 
        new_board = new board object where given piece has been moved and all captures have been made
    '''
    # since the king captures by occupying the square, all we have to do is move the king
    # to his new square.
    new_board = make_move(board, position, new_position)
    revert_empty(new_board) 
    return new_board
    
def freezer_moves(board, position):
    '''
    board = current board before move has been made
    position = position of the piece to be moved on the board (row, col)

    returns: 
        new_board = new board object where given piece has been moved and all captures have been made
    '''
    row = position[0]
    col = position[1]

    for (dr, dc) in QUEEN_MOVES:
        k = 1
        while row + k*dr >= 0 and col + k*dc >= 0:
            try:
                # if the square is empty (and all squares leading up to it by the else clause)
                # then it is a valid move
                if board.board[row + k*dr][col + k*dc] == EMPTY:
                    new_position = (row + k*dr, col + k*dc)
                    yield freezer_captures(board, position, new_position)
                    k += 1
                else:
                    # square has an enemy or friendly piece. Cannot jump over these
                    break
            except:
                break

def freezer_captures(board, position, new_position):
    '''
    board = current board before move has been made
    position = old position of the piece on the board (row, col)
    new_position = new location of piece on the board (row, col)

    returns: 
        new_board = new board object where given piece has been moved and all captures have been made
    '''
    # since the freezer does not capture, we just move it to its new square.
    new_board = make_move(board, position, new_position)
    revert_empty(new_board) 
    return new_board




# returns True if there is no adjacent freezer.
# Flag is to help in the case of a nearby imitator to prevent further rounds of recursion
# i.e. if there is in imitator nearby, it could be acting as a freezer so I have to check if a freezer
# is nearby that imitator. I wouldn't want a chain of imitators to cause this to recurse more than one 
# level as imitators CANNOT imitate themselves, so I stop that from happening with one flag
# NOTE: assumes immitators and freezers do NOT cancel out
def no_freezer_near(board, position, flag=False):
    num_rows = len(board.board)
    num_cols = len(board.board[0])
    whose_move = board.whose_move

    if flag: whose_move = 1-whose_move

    adj_squares = [(i,j) for i in range(max(0, position[0]-1), min(num_rows, position[0] + 2)) for j in range(max(0, position[1] - 1), min(num_cols, position[1] + 2))]
    adj_squares.remove(position)

    for square in adj_squares:
        piece = board.board[square[0]][square[1]]
        if whose_move == WHITE:
            if piece == 14: return False

            # NOTE: checks if there is an imitator acting as a freezer nearby
            elif piece == 8 and not flag and not no_freezer_near(board,square, flag=True): return False 
        else:
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
- - - - - - - -
- - - - - - - -
- - - - - - - -
- - P - L P - -
- - - P - - - -
- - f - - - - -
- - - - - - - - 
- - - - - - - -
''')

initial_board = BC_state(INITIAL)
initial_board.whose_move = BLACK
print(initial_board)
#print(initial_board.board)

start = time.time()

for i in range(1):
    for move in valid_moves(initial_board): 
       print(move) 

print("done!")
print("runtime: ", time.time() - start)
