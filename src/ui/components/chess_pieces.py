from nicegui import ui

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
    def __init__(self, color, x, y):
        super().__init__(color, x, y)
        self.has_moved = False  # Add this line to track if the king has moved

    def available_moves(self, board, last_move):
        moves = []
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                if dx == 0 and dy == 0:
                    continue  # Pomijamy aktualną pozycję
                new_x = self.x + dx
                new_y = self.y + dy
                if 0 <= new_x < 8 and 0 <= new_y < 8:
                    target = board[new_x][new_y]
                    if target is None or target.color != self.color:  # 🔥 Tylko puste lub wrogie!
                        moves.append((new_x, new_y))
        return moves


class Queen(Piece):
    def available_moves(self, board, last_move):
        moves = []
        moves.extend(Rook(self.color, self.x, self.y).available_moves(board, last_move))
        moves.extend(Bishop(self.color, self.x, self.y).available_moves(board, last_move))
        return moves

class Rook(Piece):
    def __init__(self, color, x, y):
        super().__init__(color, x, y)
        self.has_moved = False  # Prawidłowa flaga

    def move_piece(self, new_x, new_y):
        # Jeśli wieża się ruszyła, zaznaczamy to
        if not self.has_moved:
            self.has_moved = True
        self.x, self.y = new_x, new_y


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
    def __init__(self, color, x, y, chess):
        super().__init__(color, x, y)
        self.is_moved = False
        self.chess = chess

    def available_moves(self, board, last_move):
        moves = []
        direction = 1 if self.color == 'white' else -1
        start_row = 1 if self.color == 'white' else 6
        en_passant_row = 4 if self.color == 'white' else 3

        if 0 <= self.x + direction < 8 and board[self.x + direction][self.y] is None:
            moves.append((self.x + direction, self.y))

            if not self.is_moved and 0 <= self.x + 2 * direction < 8 and board[self.x + 2 * direction][self.y] is None:
                moves.append((self.x + 2 * direction, self.y))

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
