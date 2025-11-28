import threading

import pygame
from board import Board
from optimization import OptimizationRunner, OptimizationStats

# Constants
WIDTH, HEIGHT = 1100, 800
GRID_SIZE = 100
FPS = 30

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
PLAYER2_COLOR = (0, 0, 255)  # Blue for player 2
PLAYER4_COLOR = (255, 0, 0)  # Red for player 4
PANEL_BG = (30, 30, 30)
TEXT_COLOR = (240, 240, 240)


class OptimizationStatsStore:
    """Thread-safe container to share optimization stats with the UI."""

    def __init__(self):
        self.lock = threading.Lock()
        self.stats: OptimizationStats | None = None

    def update(self, stats: OptimizationStats):
        with self.lock:
            self.stats = stats

    def get(self) -> OptimizationStats | None:
        with self.lock:
            return self.stats


def create_initial_stats(runner: OptimizationRunner) -> OptimizationStats:
    return OptimizationStats(
        best_weights=runner.best,
        best_score=runner.best_score,
        iteration=runner.iteration,
        sigma=runner.sigma,
        last_candidate=runner.last_candidate,
        last_score=runner.last_score,
        improved=True,
    )


def optimization_loop(store: OptimizationStatsStore, stop_event: threading.Event):
    runner = OptimizationRunner()
    store.update(create_initial_stats(runner))

    while not stop_event.is_set():
        stats = runner.step()
        store.update(stats)


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


def draw_stats_panel(screen, font, stats: OptimizationStats | None):
    panel_rect = pygame.Rect(8 * GRID_SIZE, 0, WIDTH - 8 * GRID_SIZE, HEIGHT)
    pygame.draw.rect(screen, PANEL_BG, panel_rect)

    lines = []
    if stats is None:
        lines.append("Lancement du machine learning...")
    else:
        lines.append("Optimisation en cours")
        lines.append(f"Itération : {stats.iteration}")
        lines.append(f"Sigma : {stats.sigma:.3f}")
        lines.append(f"Score meilleur : {stats.best_score:.2f}")
        lines.append("Poids optimaux :")
        for key, value in stats.best_weights.items():
            lines.append(f"  {key}: {value:.2f}")
        lines.append("Dernier duel :")
        lines.append(f"  Score candidat : {stats.last_score:.2f}")
        lines.append("  Heuristique testée :")
        for key, value in stats.last_candidate.items():
            lines.append(f"    {key}: {value:.2f}")

    for i, text in enumerate(lines):
        surface = font.render(text, True, TEXT_COLOR)
        screen.blit(surface, (panel_rect.x + 10, 10 + i * 22))


def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Board Game Preview")
    clock = pygame.time.Clock()

    board = Board()  # Initialize the game board
    font = pygame.font.SysFont("Arial", 18)

    stats_store = OptimizationStatsStore()
    stop_event = threading.Event()
    opt_thread = threading.Thread(
        target=optimization_loop, args=(stats_store, stop_event), daemon=True
    )
    opt_thread.start()
    running = True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        screen.fill(BLACK)
        draw_board(screen, board)
        draw_stats_panel(screen, font, stats_store.get())
        pygame.display.flip()
        clock.tick(FPS)

    stop_event.set()
    opt_thread.join()
    pygame.quit()


if __name__ == "__main__":
    main()
