import pygame
from board import Board

# Constants
WIDTH, HEIGHT = 800, 800
GRID_SIZE = 100
FPS = 30

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
PLAYER2_COLOR = (0, 0, 255)  # Blue for player 2
PLAYER4_COLOR = (255, 0, 0)  # Red for player 4

def draw_board(screen, board):
    for y in range(8):
        for x in range(8):
            rect = pygame.Rect(x * GRID_SIZE, y * GRID_SIZE, GRID_SIZE, GRID_SIZE)
            if (x + y) % 2 == 0:
                pygame.draw.rect(screen, WHITE, rect)
            else:
                pygame.draw.rect(screen, BLACK, rect)

            piece = board.board[y][x]
            if piece == 2:
                pygame.draw.circle(screen, PLAYER2_COLOR, rect.center, GRID_SIZE // 3)
            elif piece == 4:
                pygame.draw.circle(screen, PLAYER4_COLOR, rect.center, GRID_SIZE // 3)

def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Board Game Preview")
    clock = pygame.time.Clock()

    board = Board()  # Initialize the game board
    running = True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        screen.fill(BLACK)
        draw_board(screen, board)
        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()

if __name__ == "__main__":
    main()
