from src.ui.components.chess_pieces import King, Queen, Rook, Knight, Bishop, Pawn

class ChessBoard:
    def __init__(self, chess=None):
        self.chess = chess

    def init_board(self):
        return [
            [Rook('white', 0, 0), Knight('white', 0, 1), Bishop('white', 0, 2), Queen('white', 0, 3),
             King('white', 0, 4), Bishop('white', 0, 5), Knight('white', 0, 6), Rook('white', 0, 7)],
            [Pawn('white', 1, i, self.chess) for i in range(8)],
            [None] * 8,
            [None] * 8,
            [None] * 8,
            [None] * 8,
            [Pawn('black', 6, i, self.chess) for i in range(8)],
            [Rook('black', 7, 0), Knight('black', 7, 1), Bishop('black', 7, 2), Queen('black', 7, 3),
             King('black', 7, 4), Bishop('black', 7, 5), Knight('black', 7, 6), Rook('black', 7, 7)]
        ]

    def init_check(self):
        return [
            [Rook('white', 0, 0), Knight('white', 0, 1), Bishop('white', 0, 2), None,
             King('white', 0, 4), Bishop('white', 0, 5), Knight('white', 0, 6), Rook('white', 0, 7)],
            [Pawn('white', 1, i, self.chess) for i in range(8)],
            [None] * 8,
            [None, None, None, Queen('white', 3, 3), None, None, None, None],
            [None] * 8,
            [None] * 8,
            [Pawn('black', 6, i, self.chess) for i in range(8)],
            [Rook('black', 7, 0), Knight('black', 7, 1), Bishop('black', 7, 2), Queen('black', 7, 3),
             King('black', 7, 4), Bishop('black', 7, 5), Knight('black', 7, 6), Rook('black', 7, 7)]
        ]

    def init_checkmate_1(self):
        return [
            [Rook('white', 0, 0), Knight('white', 0, 1), Bishop('white', 0, 2), None,
             King('white', 0, 4), None, Knight('white', 0, 6), Rook('white', 0, 7)],
            [Pawn('white', 1, 0, self.chess), Pawn('white', 1, 1, self.chess), Pawn('white', 1, 2, self.chess),
             Pawn('white', 1, 3, self.chess),
             Pawn('white', 1, 4, self.chess), Pawn('white', 1, 5, self.chess), Pawn('white', 1, 6, self.chess),
             Pawn('white', 1, 7, self.chess)],
            [None, None, None, None, None, Queen('white', 2, 5), None, None],
            [None, None, Bishop('white', 3, 2), None, None, None, None, None],
            [None, None, None, None, None, None, None, None],
            [None, None, None, None, None, None, None, None],
            [Pawn('black', 6, 0, self.chess), Pawn('black', 6, 1, self.chess), Pawn('black', 6, 2, self.chess),
             Pawn('black', 6, 3, self.chess),
             Pawn('black', 6, 4, self.chess), Pawn('black', 6, 5, self.chess), Pawn('black', 6, 6, self.chess),
             Pawn('black', 6, 7, self.chess)],
            [Rook('black', 7, 0), Knight('black', 7, 1), Bishop('black', 7, 2), Queen('black', 7, 3),
             King('black', 7, 4), Bishop('black', 7, 5), Knight('black', 7, 6), Rook('black', 7, 7)]
        ]

    def init_checkmate_2(self):
        pass

    def init_castling_long(self):
        return [
            [Rook('white', 0, 0), None, None, None,
             King('white', 0, 4), Bishop('white', 0, 2), Knight('white', 0, 1), Rook('white', 0, 5)],
            [Pawn('white', 1, i, self.chess) for i in range(8)],
            [None] * 8,
            [None] * 8,
            [None] * 8,
            [None] * 8,
            [Pawn('black', 6, i, self.chess) for i in range(8)],
            [Rook('black', 7, 0), None, None, None,
             King('black', 7, 4), Bishop('black', 7, 5), Knight('black', 7, 6), Rook('black', 7, 7)]
        ]

    def init_castling_short(self):
        return [
            [Rook('white', 0, 0), Knight('white', 0, 1), Bishop('white', 0, 2), Queen('white', 0, 3),
             King('white', 0, 4), None, None, Rook('white', 0, 7)],
            [Pawn('white', 1, i, self.chess) for i in range(8)],
            [None] * 8,
            [None] * 8,
            [None] * 8,
            [None] * 8,
            [Pawn('black', 6, i, self.chess) for i in range(8)],
            [Rook('black', 7, 0), Knight('black', 7, 1), Bishop('black', 7, 2), Queen('black', 7, 3),
             King('black', 7, 4), None, None, Rook('black', 7, 7)]
        ]

    def init_en_passant(self):
        return [
            [Rook('white', 0, 0), Knight('white', 0, 1), Bishop('white', 0, 2), Queen('white', 0, 3),
             King('white', 0, 4), Bishop('white', 0, 5), Knight('white', 0, 6), Rook('white', 0, 7)],
            [Pawn('white', 1, i, self.chess) for i in range(8)],
            [None, None, None, None, None, None, None, None],
            [None, None, Pawn('black', 3, 2, self.chess), None, None, None, None, None],
            [None, None, None, Pawn('white', 4, 3, self.chess), None, None, None, None],
            [None, None, None, None, None, None, None, None],
            [Pawn('black', 6, i, self.chess) for i in range(8)],
            [Rook('black', 7, 0), Knight('black', 7, 1), Bishop('black', 7, 2), Queen('black', 7, 3),
             King('black', 7, 4), Bishop('black', 7, 5), Knight('black', 7, 6), Rook('black', 7, 7)]
        ]

    def init_pawn_promotion(self):
        return [
            [None, None, None, None, None, None, None, None],
            [None, Pawn('black', 1, 1, self.chess), None, None, None, None, None, None],
            [None, None, None, None, None, None, None, None],
            [None, None, None, None, None, None, None, None],
            [None, None, None, None, None, None, None, None],
            [None, None, None, None, None, None, None, None],
            [None, None, None, None, None, None, Pawn('white', 6, 6, self.chess), None],
            [None, None, None, None, None, None, None, None],
        ]

    def init_stalemate(self):
        return [
            [King('black', 0, 0), None, None, None, None, None, None, None],
            [None, None, None, None, Queen('white', 1, 4), None, None, None],
            [None, None, None, None, None, None, None, None],
            [None, None, None, None, None, None, None, None],
            [None, None, None, None, None, None, None, None],
            [None, None, None, None, None, None, None, None],
            [None, None, None, None, None, None, King('white', 6, 6), None],
            [None, None, None, Pawn('black', 7, 3, self.chess), None, None, None, None],
        ]

    def empty_board(self):
        return [
            [None, None, None, None, None, None, None, None],
            [None, None, None, None, None, None, None, None],
            [None, None, None, None, None, None, None, None],
            [None, None, None, None, None, None, None, None],
            [None, None, None, None, None, None, None, None],
            [None, None, None, None, None, None, None, None],
            [None, None, None, None, None, None, None, None],
            [None, None, None, None, None, None, None, None],
        ]
