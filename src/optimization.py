"""Weight optimization loop for the AI player."""

import random

from board import Board
from cpu import CPUPlayer


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


def optimize():
    best = random_weights()
    best_score = fitness(best)

    print("Début de la recherche ML")
    print(best, "=>", best_score)

    sigma = 0.4

    try:
        while True:
            candidate = perturb(best, sigma)
            score = fitness(candidate)

            if score > best_score:
                best, best_score = candidate, score
                print("\nNOUVEAU MEILLEUR :", best, "score =", best_score)

            sigma = max(0.05, sigma * 0.999)

    except KeyboardInterrupt:
        print("\n=== ARRET ===")
        print("Meilleurs poids trouvés :")
        print(best)
        print("Score :", best_score)


if __name__ == "__main__":
    optimize()
