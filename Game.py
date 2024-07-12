from Player import Player
import Cards
import random

# Piece Values 
PLAYER1 = 1
PLAYER2 = -1
PAWN_BASE = 1
KING_BASE = 2
EMPTY = 0
PAWN_P1 = PLAYER1 * PAWN_BASE
KING_P1 = PLAYER1 * KING_BASE
PAWN_P2 = PLAYER2 * PAWN_BASE
KING_P2 = PLAYER2 * KING_BASE

EMPTY = 0

class Game:
    def __init__(self, grid_size):
        self.players = []
        self.cardPool = [Cards.TIGER, Cards.DRAGON, Cards.FROG, Cards.CRAB, Cards.ELEPHANT]
        self.grid_size = grid_size
        self.pieceLocations = [ [EMPTY]*self.grid_size for i in range(self.grid_size)]
        self.activePlayerIndex = 0
        
    def addPlayer(self, player:Player):
        self.players.append(player)
        self.getActivePlayer()

    def deal(self):
        random.shuffle(self.cardPool)
        for p in self.players:
            p.addCard(self.cardPool.pop())
            p.addCard(self.cardPool.pop())
        self.heldCard = self.cardPool.pop()

        self.preProcessMove()
        
    def initPlace(self):
        for p in self.players:
            p.initPlace(self.pieceLocations)
            p.piecesFromBoard(self.pieceLocations)

    def nextPlayer(self):
        self.activePlayerIndex = (self.activePlayerIndex + 1) % len(self.players)
        
    def getActivePlayer(self):
        return self.players[self.activePlayerIndex]
    
    def getInactivePlayer(self):
        return self.players[(self.activePlayerIndex + 1) % len(self.players)]
    
    def getStateFromCard(self, card):
        availableMoves = []
        for x in range(-2, 3):
            for y in range(-2, 3):
                if x != 0 or y != 0:
                    availableMoves.append((x, y) in card)
        return availableMoves
    
    def getAlterateBoard(self):
        altBoard = [ [EMPTY]*self.grid_size for i in range(self.grid_size)]
        for act_x in range(5):
            for act_y in range(5):
                new_x, new_y = self.rotate_point_180(act_x, act_y)
                altBoard[new_x][new_y] = self.pieceLocations[act_x][act_y]
        return altBoard

    def rotate_point_180(self, x, y, cx=2, cy=2):
        # Translate point to origin
        translated_x = x - cx
        translated_y = y - cy
        
        # Rotate 180 degrees around origin
        rotated_x = -translated_x
        rotated_y = -translated_y
        
        # Translate back to the original center
        final_x = rotated_x + cx
        final_y = rotated_y + cy
        
        return final_x, final_y

    def getStateForPiece(self, board, pieceValue):
        state = []
        for x in range(5):
            for y in range(5):
                state.append(board[x][y] == pieceValue * self.getActivePlayer().id)
        return state

    def getStateFromBoard(self):
        state = []
        if self.getActivePlayer().id == PLAYER1:
            board = self.pieceLocations
        else:
            board = self.getAlterateBoard()
        for piece in [KING_BASE, PAWN_BASE, -1 * KING_BASE, -1 * PAWN_BASE]:
            state.extend(self.getStateForPiece(board, piece))
        return state


    def preProcessMove(self):
        state = []
        # 5 x 24 bools for active player cards, inactive cards, held card
        for p in self.players:
            random.shuffle(p.cards)
            for c in p.cards:
                state.extend(self.getStateFromCard(c))
        state.extend(self.getStateFromCard(self.heldCard))
        state.extend(self.getStateFromBoard())
        a = 1

            

    