import pygame
import sys

# Initialize Pygame
pygame.init()

# Define colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)

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

# Set up the display
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Grid Layout")

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
def set_cell_color(grid_index, row, col, color, flip = True):
    grid_dims = all_grid_dims[grid_index]
    x, y = grid_dims[0]
    if flip:
        row = GRID_SIZE - row - 1
    cell_size = LARGE_CELL_SIZE if grid_index == LARGE_GRID_INDEX else SMALL_CELL_SIZE
    
    cell_x = x + col * cell_size
    cell_y = y + row * cell_size

    # Set the cell to the given color
    rect = pygame.Rect(cell_x, cell_y, cell_size, cell_size)
    pygame.draw.rect(screen, color, rect)

# Main loop
def main():
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        # Get mouse position
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
        font = pygame.font.Font(None, 36)
        text = font.render(f"Mouse X: {mouse_x}, Mouse Y: {mouse_y}", True, BLACK)
        screen.blit(text, (10, 10))

        # Set cell at row 2, column 3 of the large grid to red
        set_cell_color(LARGE_GRID_INDEX, 2, 3, RED)

        # Set cell at row 1, column 4 of the upper left small grid to green
        set_cell_color(TOP_LEFT_GRID_INDEX, 1, 4, GREEN)

        # Set cell at row 0, column 2 of the upper right small grid to blue
        set_cell_color(TOP_RIGHT_GRID_INDEX, 0, 2, BLUE)

        pygame.display.flip()

# Run the main function
if __name__ == "__main__":
    main()
