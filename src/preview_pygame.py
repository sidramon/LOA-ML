import pygame
from board import Board
from cpu import CPUPlayer

# Constants
WIDTH, HEIGHT = 800, 800
GRID_SIZE = 100
FPS = 30
MOVE_INTERVAL_MS = 250

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
    player2 = CPUPlayer(
        2,
        {
            "grouping": 1.0,
            "connection": 1.0,
            "enemy_sep": 1.0,
            "mobility": 1.0,
        },
    )
    player4 = CPUPlayer(
        4,
        {
            "grouping": 0.8,
            "connection": 1.2,
            "enemy_sep": 1.0,
            "mobility": 1.1,
        },
    )

    current_player = 2
    last_move_time = 0
    running = True
    game_over = False

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                # Exit the loop immediately to avoid drawing on a closing window,
                # which could cause the application to freeze or crash.
                running = False
                break

        if not running:
            break

        now = pygame.time.get_ticks()
        if not game_over and now - last_move_time >= MOVE_INTERVAL_MS:
            current_cpu = player2 if current_player == 2 else player4
            move = current_cpu.play(board, depth=2)

            if move is None:
                game_over = True
            else:
                board.make_move(move)
                current_player = 4 if current_player == 2 else 2
                if board.is_game_over():
                    game_over = True
            last_move_time = now

        screen.fill(BLACK)
        draw_board(screen, board)
        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()

if __name__ == "__main__":
    main()
