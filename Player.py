PAWN_BASE = 1
KING_BASE = 2
PAWN_POS = [0, 1, 3, 4]
KING_POS = 2

from functools import cache
import Cards
import random
from nn import get_model_and_scaler, predict

# Ensure the model is loaded or trained
model, scaler = get_model_and_scaler(csv_file= 'game_moves.csv')
def retrain():
    get_model_and_scaler(csv_file= 'game_moves.csv', retrain = True)

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
    
    def replaceCard(self, newCard, cardIndex):
        tempCard = self.cards[cardIndex]
        self.cards[cardIndex] = newCard
        return tempCard
        
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
            pieceLocation, cardIndex, move = self.getRandomMove()
            valid = self.validateMove(move, pieceLocation)
        return pieceLocation, cardIndex, move

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
        baseMove = self.cards[cardIndex][moveIndex]
        activeId = self.id
        move =  [baseMove[0] * activeId, baseMove[1] * activeId]
        return move
    
    def getRandomMove(self):
        pieceLocation = self.pieceLocation(self.randomPiece())
        cardIndex, moveIndex = self.randomChoice()
        move = self.getMove(cardIndex, moveIndex)
        return pieceLocation, cardIndex, move
    
    def makeMoveDecision(self, board, statePrefix = []):
        grid_size = len(board)
        self.piecesFromBoard(board)
        decision_state_prefix = statePrefix[1:]

        #for each piece, for each move: getMoveState , getStateFromLocation
        bestMoveValue = -999.9
        bestMove = (-10, -10)
        bestPiece = (-10, -10)
        bestCardIndex = 3
        for cardIndex in [0, 1]:
            for move in self.cards[cardIndex]:
                for pawn in self.pawnPos:
                    stateSuffix = self.getStateSuffix(grid_size, cardIndex, move, pawn)
                    testState = decision_state_prefix + stateSuffix
                    score = predict(model, scaler, testState)
                    if score > bestMoveValue:
                        bestMoveValue = score
                        bestMove = move
                        bestPiece = pawn
                        bestCardIndex = cardIndex
                stateSuffix = self.getStateSuffix(grid_size, cardIndex, move, self.kingPos)
                testState = decision_state_prefix + stateSuffix
                score = predict(model, scaler, testState)
                if score > bestMoveValue:
                    bestMoveValue = score
                    bestMove = move
                    bestPiece = self.kingPos
                    bestCardIndex = cardIndex
                    
        return bestPiece, bestCardIndex, bestMove
        #return self.getRandomMove()
    
    #@cache
    def getStateSuffix(self, gridSize, cardIndex, moveTuple, pieceLocation):
        stateSuffix = self.getMoveState(gridSize, cardIndex, moveTuple)
        stateSuffix.extend(self.getStateFromLocation(gridSize, pieceLocation))
        return stateSuffix

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
    
    def getMoveState(self, gridSize, cardIndex, moveTuple):
        # 2x 5x5 for each card
        # moveTuple is -2 indexed 
        boardSize =  gridSize * gridSize
        state = [False] * boardSize * 2
        selectedMove = cardIndex * boardSize + (moveTuple[0] + 2) * gridSize + (moveTuple[1] + 2)
        state[selectedMove] = True
        return state
        
    def getStateFromLocation(self, gridSize, locationXY):
        state = [False] * gridSize * gridSize
        location = locationXY[0] * gridSize + locationXY[1]
        state[location] = True
        return state