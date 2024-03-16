import pygame
import sys
import Cards
import numpy as np

from Game import Game
from Player import Player

# Initialize Pygame
pygame.init()


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
backline_P1 = 0
backline_P2 = 4

# Define colors
WHITE = (255, 255, 255)
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
    if pieceType == PAWN_P1:
        color = DARK_RED
    elif pieceType == KING_P1:
        color = RED
    elif pieceType == PAWN_P2:
        color = DARK_GREEN
    elif pieceType == KING_P2:
        color = GREEN
    else:
        color = WHITE
    set_cell_color(LARGE_GRID_INDEX, x, y, color)

def draw_card_on_grid(gridIndex, card):
    gridRotation = 0
    if gridIndex == TOP_LEFT_GRID_INDEX or gridIndex == TOP_RIGHT_GRID_INDEX:
        gridRotation = 2
    elif gridIndex == RIGHT_GRID_INDEX:
        gridRotation = 1

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
p1 = Player(PLAYER1, backline_P1)
p2 = Player(PLAYER2, backline_P2)
game = Game(GRID_SIZE)
game.addPlayer(p1)
game.addPlayer(p2)

game.initPlace()
game.deal()

#endregion

# Main loop
def main():
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        # Get mouse position
        if SHOW_MOUSE_POS:
            mouse_x, mouse_y = pygame.mouse.get_pos()

        # Fill the background with white
        screen.fill(WHITE)

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
        all_grid_dims.append(draw_grid(large_dims[1][0] + LARGE_CELL_SIZE, large_dims[0][1] + LARGE_CELL_SIZE, GRID_SIZE, SMALL_CELL_SIZE, GRAY, corner='top-left'))

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

        draw_card_on_grid(RIGHT_GRID_INDEX, game.heldCard)

        # Draw Pieces
        for x in range(GRID_SIZE):
            for y in range(GRID_SIZE):
                drawPiece(x, y, game.pieceLocations[x][y])

        pygame.display.flip()

# Run the main function
if __name__ == "__main__":
    main()
