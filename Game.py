from Player import Player
import Cards
import random

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
        
    def initPlace(self):
        for p in self.players:
            p.initPlace(self.pieceLocations)
            p.piecesFromBoard(self.pieceLocations)

    def nextPlayer(self):
        self.activePlayerIndex = (self.activePlayerIndex + 1) % len(self.players)
        
    def getActivePlayer(self):
        return self.players[self.activePlayerIndex]

    