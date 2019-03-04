

from BC_state_etc import BC_state

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

def static_eval(board):
    white_score = 0
    black_score = 0
    for i, row in enumerate(board.board):
        for j, piece in enumerate(row):

            ortho_neighbors = get_neighbors(board, i, j, ROOK_MOVES)
            diag_neighbors = get_neighbors(board, i,j, DIAGONAL_MOVES)
            all_neighbors = ortho_neighbors + diag_neighbors

            # find piece score: you get a better score if you have more pieces
            if piece % 2 == 0:
                white_score += weights['piece'] * PIECE_VALUES[piece // 2]
            else:
                black_score += weights['piece'] * PIECE_VALUES[piece // 2]

            # find freezing score: you get a better score if you have more enemy pieces frozen
            #                    your score is higher if you freeze higher valued pieces
            if piece == 14: # black freezer
                white_score += weights['freezing'] * sum([PIECE_VALUES[x // 2] for x in all_neighbors if x % 2 == 1 ])
            elif piee == 15:
                black_score += weights['freezing'] * sum([PIECE_VALUES[x // 2] for x in all_neighbors if x % 2 == 0 ])


            # find withdrawer score: higher score if withdrawer has a chance of capturing a good piece
            if piece == 10:
                white_score += weights['withdraw'] * sum([PIECE_VALUES[x // 2] for x in all_neighbors if x % 2 == 1 ])
            elif piece == 11:
                black_score += weights['withdraw'] * sum([PIECE_VALUES[x // 2] for x in all_neighbors if x % 2 == 0 ])

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

