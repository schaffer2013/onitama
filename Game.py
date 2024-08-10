from functools import cache
from Player import Player
import Player as P
import Cards
import random
import os, csv

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
BAD_PLAY = -10
DRAW = 0.5

WAY_OF_THE_STONE = 1
WAY_OF_THE_STREAM = 2

EMPTY = 0

class Game:
    def __init__(self, grid_size, filename):
        self.players = []
        self.cardPool = [
            Cards.TIGER, Cards.DRAGON, Cards.FROG, Cards.RABBIT, Cards.CRAB, 
            Cards.ELEPHANT, Cards.GOOSE, Cards.ROOSTER, Cards.MONKEY, Cards.MANTIS, 
            Cards.HORSE, Cards.OX, Cards.CRANE, Cards.BOAR, Cards.COBRA, Cards.EEL
        ]
        self.grid_size = grid_size
        self.pieceLocations = [ [EMPTY]*self.grid_size for i in range(self.grid_size)]
        self.activePlayerIndex = 0
        self.moves = []  # Initialize moves list to store state after each move
        self.filename = filename
        
    def addPlayer(self, player:Player):
        self.players.append(player)
        #self.getActivePlayer()

    def deal(self):
        random.shuffle(self.cardPool)
        for p in self.players:
            p.addCard(self.cardPool.pop())
            p.addCard(self.cardPool.pop())
        self.heldCard = self.cardPool.pop()
    
    def playFull(self):
        numMoves = 0
        loss = False
        winType = None
        while not loss and not winType:
            numMoves += 1
            winType, loss, state, invalid = self.move()
        #print(f'Complete in {numMoves} moves')
        return numMoves, invalid, winType

    def movePiece(self, pieceLocation, move):
        pieceVal = self.pieceLocations[pieceLocation[0]][pieceLocation[1]]
        newLocationX = pieceLocation[0] + move[0]
        newLocationY = pieceLocation[1] + move[1]
        self.pieceLocations[newLocationX][newLocationY] = pieceVal
        self.pieceLocations[pieceLocation[0]][pieceLocation[1]] = 0

    def initPlace(self):
        for p in self.players:
            p.initPlace(self.pieceLocations)
            p.piecesFromBoard(self.pieceLocations)

    def nextPlayer(self):
        self.activePlayerIndex = (self.activePlayerIndex + 1) % len(self.players)
        
    def getActivePlayer(self) -> Player:
        return self.players[self.activePlayerIndex]
    
    def getInactivePlayer(self) -> Player:
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

    @cache
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
        return self.getPreState()

    def getPreState(self):
        state = []
        state.append(self.activePlayerIndex)
        # 5 x 24 bools for active player cards, inactive cards, held card
        for p in [self.getActivePlayer(), self.getInactivePlayer()]:
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
    
    def postProcessMove(self, cardIndex, movedPieceLocation, moveTuple, moveWasValid = True):

        state = []
        activePlayer = self.getActivePlayer()
        state.extend(activePlayer.getMoveState(self.grid_size, cardIndex, moveTuple))

        # 1x 5x5 to show where the selected piece was 
        state.extend(activePlayer.getStateFromLocation(self.grid_size, movedPieceLocation))

        # Default outcome to draw unless it was invalid
        state.append(DRAW if moveWasValid else BAD_PLAY)

        # TODO
        # Swap held card with used player card.
        self.heldCard = self.getActivePlayer().replaceCard(self.heldCard, cardIndex)
        # Replace new piece location with piece
        # Set old piece location to 0

        return state

    def move(self):
        state = self.preProcessMove()
        # actual move logic here

        pieceLocation, cardIndex, move = self.getActivePlayer().makeMoveDecision(self.pieceLocations, state)
        moveValid = self.getActivePlayer().validateMove(move, pieceLocation)
        if moveValid:
            self.movePiece(pieceLocation, move)
        post_state = self.postProcessMove(cardIndex, pieceLocation, move, moveValid)
        state.extend(post_state)
        self.moves.append(state) 

        # check win logic here
        winType, loss = self.checkWin(moveValid)

        if winType or loss:
            winning_player_id = self.getActivePlayer().id if winType else self.getInactivePlayer().id
            if moveValid:
                self.updateOutcomes(winning_player_id)
            self.writeMovesToCSV(self.filename)
        
        self.nextPlayer() #should be last!
        return winType, loss, state, not moveValid
    
    def get_value(self, location):
        return self.pieceLocations[location[0]][location[1]]

    def checkWin(self, moveValid):
        win = None
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
            win = WAY_OF_THE_STONE
        
        # Check if the active player's king is in the starting position of the inactive player's king
        inactive_player_starting_king_position = (P.KING_POS, self.getInactivePlayer().backRow)
        if self.get_value(inactive_player_starting_king_position) == active_player_king:
            win = WAY_OF_THE_STREAM

        return win, loss
    
    def updateOutcomes(self, winning_player_id):
        num_moves = len(self.moves)
        for i, move in enumerate(self.moves):
            player_id = move[0]
            if player_id == winning_player_id:
                move[-1] = 0.6 + 0.4 * (i / (num_moves - 1))  # Scale from 0.6 to 1.0
            else:
                move[-1] = 0.4 * (1 - i / (num_moves - 1))    # Scale from 0.4 to 0.0


    def writeMovesToCSV(self, filename):
        file_exists = os.path.isfile(filename)
        headers = [
            'active_player_index',             # Active player index (0 or 1)
            # Card States (5 cards * 24 columns)
            *[f'card1_active_{i}' for i in range(24)],  # Card 1 Active Player
            *[f'card2_active_{i}' for i in range(24)],  # Card 2 Active Player
            *[f'card1_inactive_{i}' for i in range(24)],  # Card 1 Inactive Player
            *[f'card2_inactive_{i}' for i in range(24)],  # Card 2 Inactive Player
            *[f'held_card_{i}' for i in range(24)],       # Held Card State
            # Piece Locations (4 pieces * 25 columns)
            *[f'active_king_{i}' for i in range(25)],     # Active Player King
            *[f'active_pawn_{i}' for i in range(25)],     # Active Player Pawns
            *[f'inactive_king_{i}' for i in range(25)],    # Inactive Player King
            *[f'inactive_pawn_{i}' for i in range(25)],    # Inactive Player Pawns
            # Possible Moves (2 * 25 columns)
            *[f'possible_move_1_{i}' for i in range(25)],  # Possible Move 1
            *[f'possible_move_2_{i}' for i in range(25)],  # Possible Move 2
            # Moved Piece Location (1 * 25 columns)
            *[f'moved_piece_location_{i}' for i in range(25)],  # Where the moved piece was
            'outcome'                          # Game outcome
        ]
        
        with open(filename, mode='a', newline='') as file:
            writer = csv.writer(file)
            if not file_exists:
                writer.writerow(headers)  # Write headers if file does not exist
            writer.writerows(self.moves)

    