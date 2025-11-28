import itertools

import matplotlib.pyplot as plt
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
PLAYER2_COLOR = (0, 0, 255)  # Bleu (joueur 2)
PLAYER4_COLOR = (255, 0, 0)  # Rouge (joueur 4)


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
    champion_score,
    challenger_score,
    champion_name,
    challenger_name,
):
    sidebar_rect = pygame.Rect(BOARD_PIXELS, 0, SIDEBAR_WIDTH, SCREEN_HEIGHT)
    pygame.draw.rect(screen, SIDEBAR_BG, sidebar_rect)

    def blit_line(text, y_offset):
        surf = font.render(text, True, WHITE)
        screen.blit(surf, (BOARD_PIXELS + 12, y_offset))
        return y_offset + surf.get_height() + 6

    y = 16
    y = blit_line(f"Match: {match_index}", y)
    y = blit_line(f"Champion ({champion_name}) bleu: {champion_score:.1f}", y)
    y = blit_line(f"Challenger ({challenger_name}) rouge: {challenger_score:.1f}", y)

    if game_over:
        winner = board.get_winner()
        status = "Jeu terminé"
        if winner == 2:
            winner_text = "Gagnant: Joueur Bleu"
        elif winner == 4:
            winner_text = "Gagnant: Joueur Rouge"
        else:
            winner_text = "Match nul"
        y = blit_line(status, y)
        y = blit_line(winner_text, y)
    else:
        player_label = "Joueur Bleu" if current_player == 2 else "Joueur Rouge"
        y = blit_line(f"Tour: {player_label}", y)

    def render_cpu_info(cpu, y_offset):
        label = "Bleu" if cpu.player == 2 else "Rouge"
        y_cursor = blit_line(f"Heuristiques Joueur {label}:", y_offset + 10)
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

    plt.ion()
    fig, ax = plt.subplots()
    ax.set_xlabel("Duel")
    ax.set_ylabel("Score du champion")
    ax.set_title("Performance du meilleur CPU")
    fig.canvas.manager.set_window_title("Evolution du meilleur CPU")

    best_weights = {
        "grouping": 1.0,
        "connection": 1.0,
        "enemy_sep": 1.0,
        "mobility": 1.0,
    }

    def next_cpu_name(counter):
        return f"CPU{counter:03d}"

    cpu_counter = itertools.count(1)
    champion_name = next_cpu_name(next(cpu_counter))
    challenger_name = next_cpu_name(next(cpu_counter))

    def new_match(champion_weights, challenger_weights):
        board = Board()  # Initialize the game board
        player2 = CPUPlayer(2, champion_weights)
        player4 = CPUPlayer(4, challenger_weights)
        return board, player2, player4

    challenger_weights = perturb(best_weights, PERTURBATION_SIGMA)
    board, player2, player4 = new_match(best_weights, challenger_weights)

    match_index = 1
    duel_scores = {2: 0.0, 4: 0.0}
    duel_games_played = 0

    champion_history = []

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
                    duel_scores[2] += 1.5
                    duel_scores[4] -= 1
                elif winner == 4:
                    duel_scores[4] += 1
                    duel_scores[2] -= 1

                duel_games_played += 1

                if duel_games_played >= 2:
                    champion_score = duel_scores[2]
                    challenger_score = duel_scores[4]
                    champion_keeps_title = champion_score >= challenger_score

                    if champion_keeps_title:
                        champion_history.append((match_index, champion_score, champion_name))
                    else:
                        best_weights = challenger_weights
                        champion_name = challenger_name
                        champion_history.append((match_index, challenger_score, champion_name))
                        challenger_name = next_cpu_name(next(cpu_counter))

                    challenger_weights = perturb(best_weights, PERTURBATION_SIGMA)
                    duel_scores = {2: 0.0, 4: 0.0}
                    duel_games_played = 0

                    ax.clear()
                    ax.set_xlabel("Duel")
                    ax.set_ylabel("Score du champion")
                    ax.set_title(f"Performance du meilleur CPU ({champion_name})")
                    if champion_history:
                        xs = [d[0] for d in champion_history]
                        ys = [d[1] for d in champion_history]
                        ax.plot(xs, ys, marker="o")
                        for x, y, name in champion_history:
                            ax.annotate(name, (x, y))
                    fig.canvas.draw()
                    fig.canvas.flush_events()

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
            duel_scores[2],
            duel_scores[4],
            champion_name,
            challenger_name,
        )
        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()

if __name__ == "__main__":
    main()
