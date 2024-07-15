import os
import time
import pygame
import sys
import Cards
import numpy as np

import Game
from Game import Game as G
import Player
from Player import Player as P

CSV_FILE = 'game_moves.csv'

# Initialize Pygame
pygame.init()

backline_P1 = 0
backline_P2 = 4

# Define colors
WHITE = (255, 255, 255)
LIGHT_GREY = (200, 200, 200)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)
RED = (255, 0, 0)
DARK_RED = (128, 0, 0)
GREEN = (0, 255, 0)
DARK_GREEN = (0, 128, 0)
BLUE = (0, 0, 255)
LIGHT_BLUE = (173, 216, 230)  # Light blue color
LIGHT_ORANGE = (255, 200, 150)  # Light orange color

# Define grid sizes
LARGE_CELL_SIZE = 51
SMALL_CELL_SIZE = LARGE_CELL_SIZE / 3
GRID_SIZE = 5

LARGE_GRID_INDEX = 0
TOP_LEFT_GRID_INDEX = 1
TOP_RIGHT_GRID_INDEX = 2
BOTTOM_LEFT_GRID_INDEX = 3
BOTTOM_RIGHT_GRID_INDEX = 4
RIGHT_GRID_INDEX = 5

all_grid_dims = []

# Calculate screen size
SCREEN_WIDTH = 750
SCREEN_HEIGHT = 750

SHOW_MOUSE_POS = False

# Set up the display
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Grid Layout")

#region Drawing
# Function to draw a grid
def draw_grid(x, y, grid_size, cell_size, color, corner='top-left'):
    if corner == 'top-left':
        top_left_x = x
        top_left_y = y
        bottom_right_x = x + grid_size * cell_size
        bottom_right_y = y + grid_size * cell_size
        start_x = x
        start_y = y
    elif corner == 'top-right':
        top_left_x = x - grid_size * cell_size
        top_left_y = y
        bottom_right_x = x
        bottom_right_y = y + grid_size * cell_size
        start_x = x - grid_size * cell_size
        start_y = y
    elif corner == 'bottom-left':
        top_left_x = x
        top_left_y = y - grid_size * cell_size
        bottom_right_x = x + grid_size * cell_size
        bottom_right_y = y
        start_x = x
        start_y = y - grid_size * cell_size
    elif corner == 'bottom-right':
        top_left_x = x - grid_size * cell_size
        top_left_y = y - grid_size * cell_size
        bottom_right_x = x
        bottom_right_y = y
        start_x = x - grid_size * cell_size
        start_y = y - grid_size * cell_size
    
    for i in range(grid_size):
        for j in range(grid_size):
            rect = pygame.Rect(start_x + i * cell_size, start_y + j * cell_size, cell_size, cell_size)
            pygame.draw.rect(screen, color, rect, 1)
    
    return (top_left_x, top_left_y), (bottom_right_x, bottom_right_y)

# Define function to set a cell of any grid to a given color
def set_cell_color(grid_index, col, row, color, flip = True):
    grid_dims = all_grid_dims[grid_index]
    x, y = grid_dims[0]
    if flip:
        row = GRID_SIZE - row - 1
    cell_size = LARGE_CELL_SIZE if grid_index == LARGE_GRID_INDEX else SMALL_CELL_SIZE
    
    cell_x = x + col * cell_size
    cell_y = y + row * cell_size

    # Set the cell to the given color
    rect = pygame.Rect(cell_x + 1, cell_y + 1, cell_size - 2, cell_size - 2)
    pygame.draw.rect(screen, color, rect)

def drawPiece(x, y, pieceType):
    if pieceType == Game.PAWN_P1:
        color = DARK_RED
    elif pieceType == Game.KING_P1:
        color = RED
    elif pieceType == Game.PAWN_P2:
        color = DARK_GREEN
    elif pieceType == Game.KING_P2:
        color = GREEN
    else:
        color = WHITE
    set_cell_color(LARGE_GRID_INDEX, x, y, color)

def draw_card_on_grid(gridIndex, card, playerId = 0):
    gridRotation = 0
    if gridIndex == TOP_LEFT_GRID_INDEX or gridIndex == TOP_RIGHT_GRID_INDEX:
        gridRotation = 2
    elif gridIndex == RIGHT_GRID_INDEX:
        gridRotation = 1 - playerId

    center = (2,2)
    for offset in card:
         pos = addTuple(center, offset)
         pos = rotateN(pos, center, gridRotation)
         set_cell_color(gridIndex, pos[0], pos[1], LIGHT_ORANGE)
    set_cell_color(gridIndex, center[0], center[1], LIGHT_BLUE)
#endregion
    
#region Tuple Math
def addTuple(t1:tuple, t2:tuple) -> tuple:
    res = tuple(map(sum, zip(t1, t2)))
    return res

def subTuple(t1:tuple, t2:tuple) -> tuple:
    return addTuple(t1, scaleTuple(t2, -1.0))

def scaleTuple(t1:tuple, scale:int) -> tuple:
    newTuple=()
    for i in t1:
        newTuple += (int(i * scale),)
    return newTuple

def rotate(t1, center):
    diff = subTuple(t1, center)
    newTuple = (center[0] - diff[1], center[1] + diff[0])
    return newTuple

def rotateN(t1, center, n):
    newTuple = t1
    for i in range(n):
        newTuple = rotate(newTuple, center)
    return newTuple
#endregion

#region Board State

def initGame():
    p1 = P(Game.PLAYER1, backline_P1)
    p2 = P(Game.PLAYER2, backline_P2)
    game = G(GRID_SIZE, CSV_FILE)
    game.addPlayer(p1)
    game.addPlayer(p2)

    game.initPlace()
    game.deal()
    return game, p1, p2


#endregion

# Main loop
def main():
    game, p1, p2 = initGame()
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                totalMoves = 0
                maxMoves = 0
                minMoves = float('inf')  # Set to infinity so any actual move count will be smaller
                numInvalidMoves = 0

                target = 10000
                highWater = 0
                start_time = time.time()
                while totalMoves < target:
                    
                    if int(totalMoves/target*1000) > highWater:
                        highWater = int(totalMoves/target*1000)
                        # Calculate elapsed time
                        elapsed_time = time.time() - start_time
                        # Estimate remaining time
                        remaining_time = (elapsed_time / (totalMoves / target)) - elapsed_time
                        # Convert remaining time to minutes and seconds
                        minutes, seconds = divmod(remaining_time, 60)
                        
                        # Print progress and ETA
                        print(f'{highWater/10}% complete. ETA: {int(minutes)} minutes {int(seconds)} seconds')

                    numMoves, invalid = game.playFull()
                    numInvalidMoves += invalid
                    totalMoves += numMoves
                    
                    # Update max and min moves
                    if numMoves > maxMoves:
                        maxMoves = numMoves
                    if numMoves < minMoves:
                        minMoves = numMoves
                    
                    # Initialize a new game
                    game, p1, p2 = initGame()
                

                print(f'Complete in {totalMoves} moves')
                print(f'Maximum moves in a game: {maxMoves}')
                print(f'Minimum moves in a game: {minMoves}')
                print(f'Invalid moves: {numInvalidMoves/totalMoves * 100}%')
                elapsed_time = elapsed_time = time.time() - start_time
                print(f'Time per move: {elapsed_time/totalMoves} sec/move')
                #Player.retrain()


        # Get mouse position
        if SHOW_MOUSE_POS:
            mouse_x, mouse_y = pygame.mouse.get_pos()

        # Fill the background with white
        screen.fill(WHITE)

        all_grid_dims.clear()
        # Draw the large grid
        large_dims = draw_grid(GRID_SIZE * LARGE_CELL_SIZE, GRID_SIZE * LARGE_CELL_SIZE, GRID_SIZE, LARGE_CELL_SIZE, BLACK)
        all_grid_dims.append(large_dims)

        # Draw the upper small grids
        all_grid_dims.append(draw_grid(large_dims[0][0], large_dims[0][1] - LARGE_CELL_SIZE, GRID_SIZE, SMALL_CELL_SIZE, GRAY, corner='bottom-left'))
        all_grid_dims.append(draw_grid(large_dims[1][0], large_dims[0][1] - LARGE_CELL_SIZE, GRID_SIZE, SMALL_CELL_SIZE, GRAY, corner='bottom-right'))

        # Draw the lower small grids
        all_grid_dims.append(draw_grid(large_dims[0][0], large_dims[1][1] + LARGE_CELL_SIZE, GRID_SIZE, SMALL_CELL_SIZE, GRAY, corner='top-left'))
        all_grid_dims.append(draw_grid(large_dims[1][0], large_dims[1][1] + LARGE_CELL_SIZE, GRID_SIZE, SMALL_CELL_SIZE, GRAY, corner='top-right'))

        # Draw the right small grid
        corner = 'top-left' if game.getActivePlayer().id == Game.PLAYER1 else 'bottom-left'
        all_grid_dims.append(draw_grid(large_dims[1][0] + LARGE_CELL_SIZE, large_dims[0][1] + (GRID_SIZE/2) * LARGE_CELL_SIZE, GRID_SIZE, SMALL_CELL_SIZE, GRAY, corner=corner))

        # Display mouse position
        if SHOW_MOUSE_POS:
            font = pygame.font.Font(None, 36)
            text = font.render(f"Mouse X: {mouse_x}, Mouse Y: {mouse_y}", True, BLACK)
            screen.blit(text, (10, 10))

        # Draw Cards
        draw_card_on_grid(BOTTOM_LEFT_GRID_INDEX, p1.cards[0])
        draw_card_on_grid(BOTTOM_RIGHT_GRID_INDEX, p1.cards[1])
        
        draw_card_on_grid(TOP_LEFT_GRID_INDEX, p2.cards[0])
        draw_card_on_grid(TOP_RIGHT_GRID_INDEX, p2.cards[1])

        draw_card_on_grid(RIGHT_GRID_INDEX, game.heldCard, game.getActivePlayer().id)

        # Draw Pieces
        for x in range(GRID_SIZE):
            for y in range(GRID_SIZE):
                drawPiece(x, y, game.pieceLocations[x][y])

        pygame.display.flip()

# Run the main function
if __name__ == "__main__":
    main()
