"""Core move-related data structures for the game logic."""

class Move:
    """Represents a move from one coordinate to another."""

    def __init__(self, fr, fc, tr, tc):
        self.fr = fr
        self.fc = fc
        self.tr = tr
        self.tc = tc


class MoveState:
    """Snapshot of a move to support undo/redo operations."""

    def __init__(self, fr, fc, tr, tc, moved, captured):
        self.fromRow = fr
        self.fromCol = fc
        self.toRow = tr
        self.toCol = tc
        self.movedPiece = moved
        self.capturedPiece = captured
