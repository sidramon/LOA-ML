import pygame
from board import Board
from cpu import CPUPlayer
from optimization import perturb

# Constants
GRID_SIZE = 100
BOARD_PIXELS = GRID_SIZE * 8
SIDEBAR_WIDTH = 260
SCREEN_WIDTH = BOARD_PIXELS + SIDEBAR_WIDTH
SCREEN_HEIGHT = BOARD_PIXELS
FPS = 30
MOVE_INTERVAL_MS = 250
RESTART_DELAY_MS = 800
PERTURBATION_SIGMA = 0.35

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
SIDEBAR_BG = (30, 30, 30)
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


def format_move(move):
    if move is None:
        return "N/A"
    return f"{chr(move.fc + ord('A'))}{move.fr + 1} -> {chr(move.tc + ord('A'))}{move.tr + 1}"


def draw_sidebar(
    screen,
    board,
    player2,
    player4,
    current_player,
    game_over,
    font,
    match_index,
    champion_wins,
    challenger_wins,
):
    sidebar_rect = pygame.Rect(BOARD_PIXELS, 0, SIDEBAR_WIDTH, SCREEN_HEIGHT)
    pygame.draw.rect(screen, SIDEBAR_BG, sidebar_rect)

    def blit_line(text, y_offset):
        surf = font.render(text, True, WHITE)
        screen.blit(surf, (BOARD_PIXELS + 12, y_offset))
        return y_offset + surf.get_height() + 6

    y = 16
    y = blit_line(f"Match: {match_index}", y)
    y = blit_line(f"Champion (J2) victoires: {champion_wins}", y)
    y = blit_line(f"Challengers (J4) victoires: {challenger_wins}", y)

    if game_over:
        winner = board.get_winner()
        status = "Jeu terminé"
        winner_text = f"Gagnant: Joueur {winner}" if winner else "Match nul"
        y = blit_line(status, y)
        y = blit_line(winner_text, y)
    else:
        y = blit_line(f"Tour: Joueur {current_player}", y)

    def render_cpu_info(cpu, y_offset):
        y_cursor = blit_line(f"Heuristiques Joueur {cpu.player}:", y_offset + 10)
        for key in ["grouping", "connection", "enemy_sep", "mobility"]:
            val = cpu.weights.get(key, 0)
            y_cursor = blit_line(f"- {key}: {val:.2f}", y_cursor)

        move_text = format_move(cpu.last_best_move)
        score_text = (
            f"{cpu.last_best_score:.2f}" if cpu.last_best_score is not None else "N/A"
        )
        y_cursor = blit_line(f"Meilleur coup: {move_text}", y_cursor)
        y_cursor = blit_line(f"Score: {score_text}", y_cursor)
        return y_cursor

    y = render_cpu_info(player2, y)
    render_cpu_info(player4, y)


def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Board Game Preview")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont("arial", 18)

    best_weights = {
        "grouping": 1.0,
        "connection": 1.0,
        "enemy_sep": 1.0,
        "mobility": 1.0,
    }

    def new_match(champion_weights, challenger_weights):
        board = Board()  # Initialize the game board
        player2 = CPUPlayer(2, champion_weights)
        player4 = CPUPlayer(4, challenger_weights)
        return board, player2, player4

    challenger_weights = perturb(best_weights, PERTURBATION_SIGMA)
    board, player2, player4 = new_match(best_weights, challenger_weights)

    match_index = 1
    champion_wins = 0
    challenger_wins = 0

    current_player = 2
    last_move_time = 0
    running = True
    game_over = False
    restart_at = None

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
        if game_over:
            if restart_at is None:
                restart_at = now + RESTART_DELAY_MS
            elif now >= restart_at:
                challenger_weights = perturb(best_weights, PERTURBATION_SIGMA)
                board, player2, player4 = new_match(best_weights, challenger_weights)
                current_player = 2
                match_index += 1
                game_over = False
                restart_at = None
                last_move_time = now
            # Skip move generation while waiting to restart
        elif now - last_move_time >= MOVE_INTERVAL_MS:
            current_cpu = player2 if current_player == 2 else player4
            move = current_cpu.play(board, depth=2)

            if move is None:
                game_over = True
            else:
                board.make_move(move)
                current_player = 4 if current_player == 2 else 2
                if board.is_game_over():
                    game_over = True

            if game_over:
                winner = board.get_winner()
                if winner == 2:
                    champion_wins += 1
                elif winner == 4:
                    challenger_wins += 1
                    best_weights = challenger_weights
                restart_at = now + RESTART_DELAY_MS

            last_move_time = now

        screen.fill(BLACK)
        draw_board(screen, board)
        draw_sidebar(
            screen,
            board,
            player2,
            player4,
            current_player,
            game_over,
            font,
            match_index,
            champion_wins,
            challenger_wins,
        )
        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()

if __name__ == "__main__":
    main()
