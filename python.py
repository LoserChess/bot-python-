import random

# Constants for piece values and board representation
EMPTY = 0
PAWN = 1
KNIGHT = 2
BISHOP = 3
ROOK = 4
QUEEN = 5
KING = 6

BLACK = 8  # Changed from WHITE
WHITE = 16  # Changed from BLACK

PIECE_CHARS = {
    PAWN | BLACK: 'P', KNIGHT | BLACK: 'N', BISHOP | BLACK: 'B', ROOK | BLACK: 'R', QUEEN | BLACK: 'Q', KING | BLACK: 'K',
    PAWN | WHITE: 'p', KNIGHT | WHITE: 'n', BISHOP | WHITE: 'b', ROOK | WHITE: 'r', QUEEN | WHITE: 'q', KING | WHITE: 'k'
}

# Initialize the chess board
def init_board():
    return [
        ROOK|BLACK, KNIGHT|BLACK, BISHOP|BLACK, QUEEN|BLACK, KING|BLACK, BISHOP|BLACK, KNIGHT|BLACK, ROOK|BLACK,
        PAWN|BLACK, PAWN|BLACK, PAWN|BLACK, PAWN|BLACK, PAWN|BLACK, PAWN|BLACK, PAWN|BLACK, PAWN|BLACK,
        EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY,
        EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY,
        EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY,
        EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY,
        PAWN|WHITE, PAWN|WHITE, PAWN|WHITE, PAWN|WHITE, PAWN|WHITE, PAWN|WHITE, PAWN|WHITE, PAWN|WHITE,
        ROOK|WHITE, KNIGHT|WHITE, BISHOP|WHITE, QUEEN|WHITE, KING|WHITE, BISHOP|WHITE, KNIGHT|WHITE, ROOK|WHITE
    ]

# Get all possible moves for a given piece
def get_piece_moves(board, pos):
    piece = board[pos]
    color = piece & (WHITE | BLACK)
    piece_type = piece & 7
    moves = []

    if piece_type == PAWN:
        direction = 1 if color == WHITE else -1
        new_pos = pos + 8 * direction
        if 0 <= new_pos < 64 and board[new_pos] == EMPTY:
            moves.append(new_pos)
            if (color == WHITE and 48 <= pos <= 55) or (color == BLACK and 8 <= pos <= 15):
                new_pos = pos + 16 * direction
                if 0 <= new_pos < 64 and board[new_pos] == EMPTY:
                    moves.append(new_pos)
        for offset in [-1, 1]:
            new_pos = pos + 8 * direction + offset
            if 0 <= new_pos < 64 and board[new_pos] != EMPTY and (board[new_pos] & (WHITE | BLACK)) != color:
                moves.append(new_pos)

    elif piece_type == KNIGHT:
        offsets = [-17, -15, -10, -6, 6, 10, 15, 17]
        for offset in offsets:
            new_pos = pos + offset
            if 0 <= new_pos < 64 and abs((new_pos % 8) - (pos % 8)) <= 2:  # Check for valid knight move
                if board[new_pos] == EMPTY or (board[new_pos] & (WHITE | BLACK)) != color:
                    moves.append(new_pos)

    elif piece_type in [BISHOP, ROOK, QUEEN]:
        directions = []
        if piece_type in [BISHOP, QUEEN]:
            directions.extend([-9, -7, 7, 9])
        if piece_type in [ROOK, QUEEN]:
            directions.extend([-8, -1, 1, 8])
        for direction in directions:
            new_pos = pos + direction
            while 0 <= new_pos < 64 and abs((new_pos % 8) - ((new_pos - direction) % 8)) <= 1:
                if board[new_pos] == EMPTY:
                    moves.append(new_pos)
                elif (board[new_pos] & (WHITE | BLACK)) != color:
                    moves.append(new_pos)
                    break
                else:
                    break
                new_pos += direction

    elif piece_type == KING:
        offsets = [-9, -8, -7, -1, 1, 7, 8, 9]
        for offset in offsets:
            new_pos = pos + offset
            if 0 <= new_pos < 64 and abs((new_pos % 8) - (pos % 8)) <= 1:
                if board[new_pos] == EMPTY or (board[new_pos] & (WHITE | BLACK)) != color:
                    moves.append(new_pos)

    return moves

# Get all possible moves for a given color
def get_all_moves(board, color):
    all_moves = []
    for pos in range(64):
        if board[pos] != EMPTY and (board[pos] & (WHITE | BLACK)) == color:
            moves = get_piece_moves(board, pos)
            all_moves.extend([(pos, move) for move in moves])
    return all_moves

# Make a move on the board
def make_move(board, start, end):
    new_board = board.copy()
    new_board[end] = new_board[start]
    new_board[start] = EMPTY
    return new_board

# Count pieces on the board
def count_pieces(board, color):
    return sum(1 for piece in board if piece != EMPTY and (piece & (WHITE | BLACK)) == color)

# Calculate the number of squares a color can move to
def calculate_mobility(board, color):
    return sum(len(get_piece_moves(board, pos)) for pos in range(64) if board[pos] != EMPTY and (board[pos] & (WHITE | BLACK)) == color)

# Calculate the combined ranks of pawns
def calculate_pawn_ranks(board, color):
    pawn_ranks = 0
    for pos in range(64):
        if board[pos] == (PAWN | color):
            rank = 7 - (pos // 8) if color == WHITE else pos // 8
            pawn_ranks += rank
    return pawn_ranks

# Score the board position
def score_board(board, bot_color):
    opponent_color = WHITE if bot_color == BLACK else BLACK

    # Piece count
    bot_pieces = count_pieces(board, bot_color)
    opponent_pieces = count_pieces(board, opponent_color)
    score = (opponent_pieces - bot_pieces) * 10

    # Mandatory capture potential
    bot_moves = get_all_moves(board, bot_color)
    opponent_moves = get_all_moves(board, opponent_color)
    bot_must_capture = any(board[move[1]] != EMPTY for move in bot_moves)
    opponent_must_capture = any(board[move[1]] != EMPTY for move in opponent_moves)
    score += -5 if bot_must_capture else 0
    score += 5 if opponent_must_capture else 0

    # Additional captures
    bot_capture_count = sum(1 for move in bot_moves if board[move[1]] != EMPTY)
    opponent_capture_count = sum(1 for move in opponent_moves if board[move[1]] != EMPTY)
    score += (bot_capture_count - 1) * -0.5 if bot_capture_count > 1 else 0
    score += (opponent_capture_count - 1) * 0.5 if opponent_capture_count > 1 else 0

    # Pawn advancement
    bot_pawn_ranks = calculate_pawn_ranks(board, bot_color)
    opponent_pawn_ranks = calculate_pawn_ranks(board, opponent_color)
    score += -0.1 * bot_pawn_ranks + 0.1 * opponent_pawn_ranks

    # Piece mobility
    bot_mobility = calculate_mobility(board, bot_color)
    opponent_mobility = calculate_mobility(board, opponent_color)
    score += -0.1 * bot_mobility + 0.1 * opponent_mobility

    # Reward positions that lose rooks or the queen
    score += -8 if (QUEEN | bot_color) in board else 0
    score += 8 if (QUEEN | opponent_color) in board else 0
    score += -5 * board.count(ROOK | bot_color)
    score += 5 * board.count(ROOK | opponent_color)

    # Check for winning or losing positions
    if bot_pieces == 0:
        return 1000
    elif opponent_pieces == 0:
        return -1000

    return score

# Check if a player has any legal moves
def has_legal_moves(board, color):
    return len(get_all_moves(board, color)) > 0

# Make the best move for the bot
def make_best_move(board, bot_color, depth=3):
    def minimax(board, depth, maximizing_player, alpha, beta):
        if depth == 0:
            return score_board(board, bot_color)

        color = bot_color if maximizing_player else (WHITE if bot_color == BLACK else BLACK)
        moves = get_all_moves(board, color)

        if not moves:
            if not has_legal_moves(board, WHITE if color == BLACK else BLACK):
                return 0  # Draw
            return score_board(board, bot_color)

        if maximizing_player:
            max_eval = float('-inf')
            for start, end in moves:
                new_board = make_move(board, start, end)
                eval = minimax(new_board, depth - 1, False, alpha, beta)
                max_eval = max(max_eval, eval)
                alpha = max(alpha, eval)
                if beta <= alpha:
                    break
            return max_eval
        else:
            min_eval = float('inf')
            for start, end in moves:
                new_board = make_move(board, start, end)
                eval = minimax(new_board, depth - 1, True, alpha, beta)
                min_eval = min(min_eval, eval)
                beta = min(beta, eval)
                if beta <= alpha:
                    break
            return min_eval

    best_move = None
    best_score = float('-inf')
    moves = get_all_moves(board, bot_color)
    for start, end in moves:
        new_board = make_move(board, start, end)
        score = minimax(new_board, depth - 1, False, float('-inf'), float('inf'))
        if score > best_score:
            best_score = score
            best_move = (start, end)

    return best_move

# Play the game
def play_game():
    board = init_board()
    current_color = WHITE  # Start with White (human player)
    move_count = 0
    position_history = {}

    while True:
        print_board(board)
        print(f"{'White' if current_color == WHITE else 'Black'} to move")

        if not has_legal_moves(board, current_color):
            if not has_legal_moves(board, BLACK if current_color == WHITE else WHITE):
                print("Game over: Draw (stalemate)")
                return "Draw"
            print(f"{'White' if current_color == WHITE else 'Black'} has no legal moves. Skipping turn.")
            current_color = BLACK if current_color == WHITE else WHITE
            continue

        if current_color == BLACK:  # Bot's turn
            start, end = make_best_move(board, BLACK)
            print(f"Bot moves: {chess_notation(start)} to {chess_notation(end)}")
        else:  # Human's turn (WHITE)
            while True:
                move = input("Enter your move (e.g., e2e4): ").strip().lower()
                if len(move) != 4:
                    print("Invalid input. Please use the format 'e2e4'.")
                    continue
                start = chess_notation_to_index(move[:2])
                end = chess_notation_to_index(move[2:])
                if start is None or end is None:
                    print("Invalid square. Please use letters a-h and numbers 1-8.")
                    continue
                
                # Debug information
                print(f"Debug: start = {start}, end = {end}")
                print(f"Debug: piece at start = {PIECE_CHARS.get(board[start], 'Empty')}")
                print(f"Debug: piece at end = {PIECE_CHARS.get(board[end], 'Empty')}")
                
                legal_moves = get_all_moves(board, WHITE)
                print(f"Debug: legal moves = {[f'{chess_notation(m[0])}-{chess_notation(m[1])}' for m in legal_moves]}")
                
                if (start, end) not in legal_moves:
                    print("Invalid move. Please try again.")
                    continue
                break

        board = make_move(board, start, end)
        move_count += 1

        # Check for threefold repetition
        board_string = ''.join(map(str, board))
        position_history[board_string] = position_history.get(board_string, 0) + 1
        if position_history[board_string] == 3:
            print("Game over: Draw (threefold repetition)")
            return "Draw"

        # Check for fifty-move rule
        if move_count == 100:
            print("Game over: Draw (fifty-move rule)")
            return "Draw"

        # Check for winning condition
        if count_pieces(board, current_color) == 0:
            print(f"Game over: {'White' if current_color == BLACK else 'Black'} wins!")
            return "White" if current_color == BLACK else "Black"

        current_color = WHITE if current_color == BLACK else BLACK

# Helper functions for chess notation
def chess_notation(index):
    return chr(ord('a') + (index % 8)) + str(8 - (index // 8))

def chess_notation_to_index(notation):
    if len(notation) != 2 or notation[0] not in 'abcdefgh' or notation[1] not in '12345678':
        return None
    col = ord(notation[0]) - ord('a')
    row = 8 - int(notation[1])
    return row * 8 + col

# Print the chess board
def print_board(board):
    for i in range(8):
        row = ' '.join(PIECE_CHARS.get(board[i*8 + j], '.') for j in range(8))
        print(f"{8-i} {row}")
    print("  a b c d e f g h")

# Main function to start the game
if __name__ == "__main__":
    play_game()
