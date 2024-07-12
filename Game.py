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

# Outcome Values
WIN = 1
LOSE = 0
BAD_PLAY = -1
DRAW = 0.5

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

        self.move(1, (-2, -2))
        
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
        state.append(self.activePlayerIndex)
        # 5 x 24 bools for active player cards, inactive cards, held card
        for p in self.players:
            random.shuffle(p.cards)
            for c in p.cards:
                state.extend(self.getStateFromCard(c))
        state.extend(self.getStateFromCard(self.heldCard))

        # 4 x 25 for locations in this order:
        # active player king, active pawn, inactive king, inactive pawn
        # This should be relative to the active player's perspective, 
        # regardless of the absolute positions of the pieces on the board 
        state.extend(self.getStateFromBoard())
        return state
    
    def postProcessMove(self, cardIndex, moveTuple, moveWasValid = True):
        # 2x 5x5 for each card
        # moveTuple is -2 indexed 
        boardSize = self.grid_size * self.grid_size
        state = [False] * boardSize * 2
        selectedMove = cardIndex * boardSize + (moveTuple[0] + 2) * self.grid_size + (moveTuple[1] + 2)
        state[selectedMove] = True
        # Default outcome to 
        state.append(DRAW if moveWasValid else BAD_PLAY)
        return state

    def move(self, cardIndex, moveTuple):
        state = self.preProcessMove()
        # actual move logic here
        moveValid = False
        post_state = self.postProcessMove(cardIndex, moveTuple, moveValid)
        state.extend(post_state)

        # check win logic here
        win, loss = self.checkWin(moveValid)

        return win, loss, state
    
    def get_value(self, location):
        return self.pieceLocations[location[0]][location[1]]

    def checkWin(self, moveValid):
        win = False
        loss = False
        
        if not moveValid:
            loss = True
            return win, loss
        
        inactive_player_king = KING_BASE * self.getInactivePlayer().id
        active_player_king = KING_BASE * self.getActivePlayer().id
        
        # Check if the inactive player's king exists on the board
        inactive_king_exists = any(
            inactive_player_king == self.get_value([x, y])
            for x in range(self.grid_size) for y in range(self.grid_size)
        )
        
        if not inactive_king_exists:
            win = True
        
        # Check if the active player's king is in the starting position of the inactive player's king
        inactive_player_starting_king_position = (Player.KING_POS, self.getInactivePlayer().backRow)
        if self.get_value(inactive_player_starting_king_position) == active_player_king:
            win = True

        return win, loss

        

    