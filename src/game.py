"""Compatibility wrapper re-exporting the main game components."""

from .board import Board
from .cpu import CPUPlayer
from .moves import Move, MoveState
from .optimization import fitness, optimize, perturb, play_match, random_weights

__all__ = [
    "Board",
    "CPUPlayer",
    "Move",
    "MoveState",
    "fitness",
    "optimize",
    "perturb",
    "play_match",
    "random_weights",
]


if __name__ == "__main__":
    optimize()
