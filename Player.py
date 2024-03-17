PAWN_BASE = 1
KING_BASE = 2
PAWN_POS = [0, 1, 3, 4]
KING_POS = 2

import Cards
import random

class Player:
    def __init__(self, id, backRow):
        self.id = id #id should be -1 or 1
        self.backRow = backRow
        self.kingValue = KING_BASE * id
        self.pawnValue = PAWN_BASE * id
        self.cards = []
        self.kingPos = []
        self.pawnPos = []
    
    def initPlace(self, board):
        board[KING_POS][self.backRow] = self.kingValue

        for i in PAWN_POS:
            board[i][self.backRow] = self.pawnValue

    def addCard(self, card):
        self.cards.append(card)

    def piecesFromBoard(self, board):
        self.pawnPos = []
        for x in range(len(board)):
            for y in range (len(board)):
                if board[x][y] == self.kingValue:
                    self.kingPos = [x, y]
                if board[x][y] == self.pawnValue:
                    self.pawnPos.append([x, y])

    def getRandomValidatedMove(self):
        valid = False
        while not valid:
            move = self.getRandomMove()
            pieceLocation = self.pieceLocation(self.randomPiece())
            valid = self.validateMove(move, pieceLocation)
        return move, pieceLocation

    def validateMove(self, move, piecePos):
        poss = range(5)
        x = move[0] + piecePos[0]
        y = move[1] + piecePos[1]
        if x in poss and y in poss:
            otherPieceLocations = []
            if piecePos != self.kingPos:
                otherPieceLocations.append(self.kingPos)
            for p in self.pawnPos:
                if piecePos != p:
                    otherPieceLocations.append(p)
            for o in otherPieceLocations:
                if x == o[0] and y == o[1]:
                    return False
            return True
        return False
        
    def getMove(self, cardIndex, moveIndex):
        return self.cards[cardIndex][moveIndex]
    
    def getRandomMove(self):
        card, move = self.randomChoice()
        return self.getMove(card, move)

    # def getChoice(self, board, heldCard, otherPlayerCards):
    def pieceLocation(self, pieceIndex):
        if pieceIndex ==  len(self.pawnPos):
            return self.kingPos
        else:
            return self.pawnPos[pieceIndex]
        
    def randomPiece(self):
        randPieceIndex = random.randint(0, len(self.pawnPos))
        return randPieceIndex

    def randomChoice(self):
        randomCardIndex = random.randint(0, len(self.cards) - 1)
        movesOnCard = len(self.cards[randomCardIndex])
        randomMove = random.randint(0, movesOnCard - 1)
        return randomCardIndex, randomMove
        
