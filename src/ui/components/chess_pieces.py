class Piece:
    def __init__(self, color, x, y):
        self.color = color
        self.x = x
        self.y = y

    def available_moves(self, board, last_move):
        raise NotImplementedError

    def move_piece(self, new_x, new_y):
        self.x = new_x
        self.y = new_y


class King(Piece):
    def available_moves(self, board, last_move):
        return [(self.x + dx, self.y + dy) for dx in [-1, 0, 1] for dy in [-1, 0, 1] if (dx, dy) != (0, 0)]


class Queen(Piece):
    def available_moves(self, board, last_move):
        moves = []
        moves.extend(Rook(self.color, self.x, self.y).available_moves(board, last_move))
        moves.extend(Bishop(self.color, self.x, self.y).available_moves(board, last_move))
        return moves


class Rook(Piece):
    def available_moves(self, board, last_move):
        moves = []
        for dx, dy in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
            x, y = self.x, self.y
            while 0 <= x + dx < 8 and 0 <= y + dy < 8:
                x += dx
                y += dy
                if board[x][y] is None:
                    moves.append((x, y))
                elif board[x][y].color != self.color:
                    moves.append((x, y))
                    break
                else:
                    break
        return moves


class Knight(Piece):
    def available_moves(self, board, last_move):
        moves = []
        for dx, dy in [(2, 1), (2, -1), (-2, 1), (-2, -1), (1, 2), (1, -2), (-1, 2), (-1, -2)]:
            x, y = self.x + dx, self.y + dy
            if 0 <= x < 8 and 0 <= y < 8:
                target = board[x][y]
                if target is None or target.color != self.color:
                    moves.append((x, y))
        return moves


class Bishop(Piece):
    def available_moves(self, board, last_move):
        moves = []
        for dx, dy in [(1, 1), (1, -1), (-1, 1), (-1, -1)]:
            x, y = self.x, self.y
            while 0 <= x + dx < 8 and 0 <= y + dy < 8:
                x += dx
                y += dy
                if board[x][y] is None:
                    moves.append((x, y))
                elif board[x][y].color != self.color:
                    moves.append((x, y))
                    break
                else:
                    break
        return moves


class Pawn(Piece):
    def __init__(self, color, x, y):
        super().__init__(color, x, y)
        self.is_moved = False

    def available_moves(self, board, last_move):
        moves = []
        direction = 1 if self.color == 'white' else -1
        start_row = 1 if self.color == 'white' else 6
        en_passant_row = 4 if self.color == 'white' else 3

        # Normal move forward
        if 0 <= self.x + direction < 8 and board[self.x + direction][self.y] is None:
            moves.append((self.x + direction, self.y))

            # First double move
            if not self.is_moved and self.x == start_row and board[self.x + 2 * direction][self.y] is None:
                moves.append((self.x + 2 * direction, self.y))

        # Capture diagonally
        for dy in [-1, 1]:
            if 0 <= self.y + dy < 8 and 0 <= self.x + direction < 8:
                target = board[self.x + direction][self.y + dy]
                if target and target.color != self.color:
                    moves.append((self.x + direction, self.y + dy))

        # En passant
        if self.x == en_passant_row and last_move:
            last_piece, (old_x, old_y), (new_x, new_y) = last_move
            if isinstance(last_piece, Pawn) and last_piece.color != self.color:
                if abs(old_x - new_x) == 2 and new_x == self.x and abs(new_y - self.y) == 1:
                    moves.append((self.x + direction, new_y))

        return moves


