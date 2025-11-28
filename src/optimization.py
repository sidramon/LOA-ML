"""Weight optimization loop for the AI player."""

from dataclasses import dataclass
import random
from typing import Dict

from board import Board
from cpu import CPUPlayer


@dataclass
class OptimizationStats:
    """Represents the current status of the optimization loop."""

    best_weights: Dict[str, float]
    best_score: float
    iteration: int
    sigma: float
    last_candidate: Dict[str, float]
    last_score: float
    improved: bool


def random_weights():
    return {
        "grouping": random.uniform(0, 2),
        "connection": random.uniform(0, 2),
        "enemy_sep": random.uniform(0, 2),
        "mobility": random.uniform(0, 2),
    }


def perturb(weights, sigma=0.2):
    return {
        k: max(0, weights[k] + random.gauss(0, sigma))
        for k in weights
    }


def play_match(wA, wB):
    board = Board()

    pA = CPUPlayer(2, wA)
    pB = CPUPlayer(4, wB)

    current = 2

    for _ in range(200):
        if board.is_game_over():
            w = board.get_winner()
            if w == 2:
                return +1
            if w == 4:
                return -1
            return 0

        player = pA if current == 2 else pB
        mv = player.play(board, depth=2)
        if mv is None:
            return 0

        board.make_move(mv)
        current = 4 if current == 2 else 2

    return 0


def fitness(weights):
    baseline = {
        "grouping": 1,
        "connection": 1,
        "enemy_sep": 1,
        "mobility": 1,
    }
    score = 0
    for _ in range(2):
        score += play_match(weights, baseline)
    for _ in range(2):
        score -= play_match(baseline, weights)
    return score


class OptimizationRunner:
    """Utility to step through the stochastic search in a controlled way."""

    def __init__(self, sigma: float = 0.4):
        self.best = random_weights()
        self.best_score = fitness(self.best)
        self.sigma = sigma
        self.iteration = 0
        self.last_candidate = self.best
        self.last_score = self.best_score

    def step(self) -> OptimizationStats:
        """Performs a single optimization step and returns the updated stats."""

        candidate = perturb(self.best, self.sigma)
        score = fitness(candidate)

        self.iteration += 1
        self.last_candidate = candidate
        self.last_score = score

        improved = False
        if score > self.best_score:
            self.best, self.best_score = candidate, score
            improved = True

        self.sigma = max(0.05, self.sigma * 0.999)

        return OptimizationStats(
            best_weights=self.best,
            best_score=self.best_score,
            iteration=self.iteration,
            sigma=self.sigma,
            last_candidate=self.last_candidate,
            last_score=self.last_score,
            improved=improved,
        )


def optimize():
    runner = OptimizationRunner()

    print("Début de la recherche ML")
    print(runner.best, "=>", runner.best_score)

    try:
        while True:
            stats = runner.step()
            if stats.improved:
                print("\nNOUVEAU MEILLEUR :", stats.best_weights, "score =", stats.best_score)

    except KeyboardInterrupt:
        print("\n=== ARRET ===")
        print("Meilleurs poids trouvés :")
        print(runner.best)
        print("Score :", runner.best_score)


if __name__ == "__main__":
    optimize()
