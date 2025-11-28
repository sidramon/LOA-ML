"""CPU player implementation using minimax with alpha-beta pruning."""

from board import Board


class CPUPlayer:
    def __init__(self, player, weights):
        self.player = player
        self.weights = weights
        self.last_best_move = None
        self.last_best_score = None

    def evaluate(self, board: Board):
        f = board.evaluate_features(self.player)
        return (
            f["grouping"] * self.weights["grouping"]
            + f["connection"] * self.weights["connection"]
            + f["enemy_sep"] * self.weights["enemy_sep"]
            + f["mobility"] * self.weights["mobility"]
        )

    def opponent(self):
        return 4 if self.player == 2 else 2

    def alphabeta(self, board: Board, depth, alpha, beta, maximizing):
        if depth == 0 or board.is_game_over():
            return self.evaluate(board)

        current = self.player if maximizing else self.opponent()
        moves = board.get_all_possible_moves(current)

        if not moves:
            return self.evaluate(board)

        if maximizing:
            best = -1e9
            for mv in moves:
                board.make_move(mv)
                val = self.alphabeta(board, depth - 1, alpha, beta, False)
                board.undo_move()
                if val > best:
                    best = val
                alpha = max(alpha, val)
                if beta <= alpha:
                    break
            return best
        else:
            best = 1e9
            for mv in moves:
                board.make_move(mv)
                val = self.alphabeta(board, depth - 1, alpha, beta, True)
                board.undo_move()
                if val < best:
                    best = val
                beta = min(beta, val)
                if beta <= alpha:
                    break
            return best

    def play(self, board: Board, depth=2):
        moves = board.get_all_possible_moves(self.player)
        if not moves:
            return None

        bestMove = None
        bestScore = -1e9

        for mv in moves:
            board.make_move(mv)
            score = self.alphabeta(board, depth - 1, -1e9, 1e9, False)
            board.undo_move()
            if score > bestScore:
                bestScore = score
                bestMove = mv

        self.last_best_move = bestMove
        self.last_best_score = bestScore
        return bestMove
