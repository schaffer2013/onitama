PAWN_BASE = 1
KING_BASE = 2
PAWN_POS = [0, 1, 3, 4]
KING_POS = 2

import Cards

class Player:
    def __init__(self, id, backRow):
        self.id = id #id should be -1 or 1
        self.backRow = backRow
        self.kingValue = KING_BASE * id
        self.pawnValue = PAWN_BASE * id
        self.cards = []
    
    def initPlace(self, board):
        board[KING_POS][self.backRow] = self.kingValue

        for i in PAWN_POS:
            board[i][self.backRow] = self.pawnValue

    def addCard(self, card):
        self.cards.append(card)
