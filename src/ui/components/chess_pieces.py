from nicegui import ui

class Piece:
    def __init__(self, color, x, y):
        self.color = color
        self.x = x
        self.y = y

    def available_moves(self, board):
        raise NotImplementedError

    def move_piece(self, new_x, new_y):
        self.x = new_x
        self.y = new_y


class King(Piece):
    def available_moves(self, board):
        return [(self.x + dx, self.y + dy) for dx in [-1, 0, 1] for dy in [-1, 0, 1] if (dx, dy) != (0, 0)]


class Queen(Piece):
    def available_moves(self, board):
        moves = []
        moves.extend(Rook(self.color, self.x, self.y).available_moves(board))
        moves.extend(Bishop(self.color, self.x, self.y).available_moves(board))
        return moves


class Rook(Piece):
    def available_moves(self, board):
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
    def available_moves(self, board):
        moves = []
        for dx, dy in [(2, 1), (2, -1), (-2, 1), (-2, -1), (1, 2), (1, -2), (-1, 2), (-1, -2)]:
            x, y = self.x + dx, self.y + dy
            if 0 <= x < 8 and 0 <= y < 8:
                target = board[x][y]
                if target is None or target.color != self.color:
                    moves.append((x, y))
        return moves


class Bishop(Piece):
    def available_moves(self, board):
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
    def __init__(self, color, x, y, chess):
        super().__init__(color, x, y)
        self.is_moved = False
        self.chess = chess

    def available_moves(self, board):
        moves = []
        direction = 1 if self.color == 'white' else -1

        # Single step forward
        if 0 <= self.x + direction < 8 and board[self.x + direction][self.y] is None:
            moves.append((self.x + direction, self.y))

            # Double step forward (only if the pawn hasn't moved)
            if not self.is_moved and 0 <= self.x + 2 * direction < 8 and board[self.x + 2 * direction][self.y] is None:
                moves.append((self.x + 2 * direction, self.y))

        # Capturing diagonally
        for dy in [-1, 1]:
            if 0 <= self.y + dy < 8 and 0 <= self.x + direction < 8:
                target = board[self.x + direction][self.y + dy]
                if target and target.color != self.color:
                    moves.append((self.x + direction, self.y + dy))

        return moves

    def move_piece(self, new_x, new_y, board):
        """Moves the pawn and handles promotion."""
        self.x = new_x
        self.y = new_y
        self.is_moved = True
        if (self.color == 'white' and self.x == 7) or (self.color == 'black' and self.x == 0):
            if self.promote_pawn(board):
                return True

    def promote_pawn(self, board):
        """Handles pawn promotion to a chosen piece."""
        def select_promotion(piece_name):
            piece_classes = {'Queen': Queen, 'Rook': Rook, 'Bishop': Bishop, 'Knight': Knight}
            board[self.x][self.y] = piece_classes[piece_name](self.color, self.x, self.y)
            ui.notify(f"Pionek promowany na {piece_name}!", color='green')
            dialog.close()
            self.chess.update_square(self.x, self.y)

        with ui.dialog() as dialog, ui.card():
            ui.label('Promote your pawn').classes('text-xl font-bold')
            with ui.row():
                for strname in ['Queen', 'Rook', 'Bishop', 'Knight']:
                    ui.button(strname, on_click=lambda name=strname: select_promotion(name)).classes('m-2')
        dialog.open()