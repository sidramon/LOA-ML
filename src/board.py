"""Game board implementation and related utilities."""

import random

from moves import Move, MoveState

DEFAULT_START = [
    [0, 2, 2, 2, 2, 2, 2, 0],
    [4, 0, 0, 0, 0, 0, 0, 4],
    [4, 0, 0, 0, 0, 0, 0, 4],
    [4, 0, 0, 0, 0, 0, 0, 4],
    [4, 0, 0, 0, 0, 0, 0, 4],
    [4, 0, 0, 0, 0, 0, 0, 4],
    [4, 0, 0, 0, 0, 0, 0, 4],
    [0, 2, 2, 2, 2, 2, 2, 0],
]


class Board:
    ZOBRIST_TABLE = [[[0] * 3 for _ in range(8)] for _ in range(8)]
    RANDOM = random.Random(137)

    for y in range(8):
        for x in range(8):
            for p in range(3):
                ZOBRIST_TABLE[y][x][p] = RANDOM.getrandbits(64)

    def __init__(self, initialBoard=None):
        if initialBoard is None:
            initialBoard = DEFAULT_START

        self.board = [row[:] for row in initialBoard]
        self.history = []
        self.historyIndex = -1
        self.countPlayer2 = 0
        self.countPlayer4 = 0
        self.recalcPieceCounts()

    def recalcPieceCounts(self):
        self.countPlayer2 = 0
        self.countPlayer4 = 0
        for y in range(8):
            for x in range(8):
                v = self.board[y][x]
                if v == 2:
                    self.countPlayer2 += 1
                elif v == 4:
                    self.countPlayer4 += 1

    def getPieceCount(self, player):
        return self.countPlayer2 if player == 2 else self.countPlayer4

    def get_all_possible_moves(self, playerPiece):
        moves = []
        opponentPiece = 4 if playerPiece == 2 else 2

        dx = [-1, -1, -1, 0, 0, 1, 1, 1]
        dy = [-1, 0, 1, -1, 1, -1, 0, 1]

        for y in range(8):
            for x in range(8):
                if self.board[y][x] != playerPiece:
                    continue
                for d in range(8):
                    count = self.countPiecesInLine(x, y, dx[d], dy[d])
                    nx = x + dx[d] * count
                    ny = y + dy[d] * count
                    if not self.isInsideBoard(nx, ny):
                        continue
                    if self.board[ny][nx] == playerPiece:
                        continue
                    if self.isBlocked(x, y, nx, ny, dx[d], dy[d], opponentPiece):
                        continue
                    moves.append(Move(y, x, ny, nx))
        return moves

    def countPiecesInLine(self, x, y, dx, dy):
        count = 0
        nx, ny = x, y
        while self.isInsideBoard(nx, ny):
            if self.board[ny][nx] != 0:
                count += 1
            nx += dx
            ny += dy
        nx, ny = x - dx, y - dy
        while self.isInsideBoard(nx, ny):
            if self.board[ny][nx] != 0:
                count += 1
            nx -= dx
            ny -= dy
        return count

    def isBlocked(self, x, y, nx, ny, dx, dy, opponentPiece):
        cx = x + dx
        cy = y + dy
        while cx != nx or cy != ny:
            if not self.isInsideBoard(cx, cy):
                break
            if self.board[cy][cx] == opponentPiece:
                return True
            cx += dx
            cy += dy
        return False

    def isInsideBoard(self, x, y):
        return 0 <= x < 8 and 0 <= y < 8

    def is_game_over(self):
        return (
            self.countPlayer2 == 0
            or self.countPlayer4 == 0
            or self.isWinningState(2)
            or self.isWinningState(4)
        )

    def get_winner(self):
        player2_win = self.isWinningState(2)
        player4_win = self.isWinningState(4)

        if player2_win and not player4_win:
            return 2
        if player4_win and not player2_win:
            return 4
        if self.countPlayer2 == 0:
            return 4
        if self.countPlayer4 == 0:
            return 2
        return None

    def make_move(self, move):
        fr = move.fr
        fc = move.fc
        tr = move.tr
        tc = move.tc

        if not self.isInsideBoard(fc, fr) or not self.isInsideBoard(tc, tr):
            raise ValueError("Move hors plateau")

        piece = self.board[fr][fc]
        if piece == 0:
            raise ValueError("Aucune pièce à déplacer")

        captured = self.board[tr][tc]

        if self.historyIndex + 1 < len(self.history):
            self.history = self.history[: self.historyIndex + 1]

        st = MoveState(fr, fc, tr, tc, piece, captured)
        self.history.append(st)
        self.historyIndex += 1

        self.board[tr][tc] = piece
        self.board[fr][fc] = 0

        if captured == 2:
            self.countPlayer2 -= 1
        elif captured == 4:
            self.countPlayer4 -= 1

    def undo_move(self):
        if self.historyIndex < 0:
            return
        st = self.history[self.historyIndex]
        self.historyIndex -= 1

        self.board[st.fromRow][st.fromCol] = st.movedPiece
        self.board[st.toRow][st.toCol] = st.capturedPiece

        if st.capturedPiece == 2:
            self.countPlayer2 += 1
        elif st.capturedPiece == 4:
            self.countPlayer4 += 1

    def get_zobrist_hash(self):
        h = 0
        for y in range(8):
            for x in range(8):
                piece = self.board[y][x]
                idx = 0
                if piece == 2:
                    idx = 1
                elif piece == 4:
                    idx = 2
                h ^= Board.ZOBRIST_TABLE[y][x][idx]
        return h

    def isWinningState(self, player):
        target = player
        visited = [[False] * 8 for _ in range(8)]
        grid = self.board

        total = 0
        start = None

        for r in range(8):
            for c in range(8):
                if grid[r][c] == target:
                    total += 1
                    if start is None:
                        start = (r, c)

        if total == 0:
            return False

        stack = [start]
        visited[start[0]][start[1]] = True
        connected = 0

        dr = [-1, -1, -1, 0, 0, 1, 1, 1]
        dc = [-1, 0, 1, -1, 1, -1, 0, 1]

        while stack:
            r, c = stack.pop()
            connected += 1

            for i in range(8):
                nr = r + dr[i]
                nc = c + dc[i]
                if 0 <= nr < 8 and 0 <= nc < 8:
                    if grid[nr][nc] == target and not visited[nr][nc]:
                        visited[nr][nc] = True
                        stack.append((nr, nc))

        return connected == total

    def evaluate_features(self, player):
        return {
            "grouping": self.evaluateGrouping(player),
            "enemy_sep": self.evaluateEnemySeparation(player),
            "connection": self.evaluateConnectionPotential(player),
            "mobility": self.evaluateMobility(player),
        }

    def evaluateEnemySeparation(self, player):
        grid = self.board
        size = 8
        opponent = 4 if player == 2 else 2
        isolated = 0

        for y in range(size):
            for x in range(size):
                if grid[y][x] == opponent:
                    near = False
                    for dy in range(-1, 2):
                        for dx in range(-1, 2):
                            if dx != 0 or dy != 0:
                                ny = y + dy
                                nx = x + dx
                                if (
                                    0 <= ny < size
                                    and 0 <= nx < size
                                    and grid[ny][nx] == opponent
                                ):
                                    near = True
                    if not near:
                        isolated += 1

        score = min(100, isolated * 10)
        return score

    def evaluateGrouping(self, player):
        grid = self.board
        pieces = []

        for r in range(8):
            for c in range(8):
                if grid[r][c] == player:
                    pieces.append((r, c))

        n = len(pieces)
        if n <= 1:
            return 100

        sumSq = 0
        pairs = 0

        for i in range(n):
            r1, c1 = pieces[i]
            for j in range(i + 1, n):
                r2, c2 = pieces[j]
                dx = r1 - r2
                dy = c1 - c2
                sumSq += dx * dx + dy * dy
                pairs += 1

        avg = sumSq / pairs
        score = int(100 - avg * 1.5)
        return max(0, min(100, score))

    def evaluateConnectionPotential(self, player):
        grid = self.board
        pieces = [
            (r, c) for r in range(8) for c in range(8) if grid[r][c] == player
        ]

        if len(pieces) <= 1:
            return 100

        vis = [[False] * 8 for _ in range(8)]
        groups = []

        def dfs(r, c, out):
            vis[r][c] = True
            out.append((r, c))
            dr = [-1, -1, -1, 0, 0, 1, 1, 1]
            dc = [-1, 0, 1, -1, 1, -1, 0, 1]
            for i in range(8):
                nr = r + dr[i]
                nc = c + dc[i]
                if 0 <= nr < 8 and 0 <= nc < 8:
                    if not vis[nr][nc] and grid[nr][nc] == player:
                        dfs(nr, nc, out)

        for r, c in pieces:
            if not vis[r][c]:
                g = []
                dfs(r, c, g)
                groups.append(g)

        if len(groups) == 1:
            return 100

        mainGroup = max(groups, key=len)

        totalDist = 0
        for g in groups:
            if g is mainGroup:
                continue
            for r, c in g:
                best = 999
                for mr, mc in mainGroup:
                    dist = max(abs(r - mr), abs(c - mc))
                    if dist < best:
                        best = dist
                totalDist += best

        score = 100 - totalDist * 8
        return max(0, min(100, score))

    def evaluateMobility(self, player):
        playerMoves = len(self.get_all_possible_moves(player))
        opponent = 4 if player == 2 else 2
        opponentMoves = len(self.get_all_possible_moves(opponent))

        diff = playerMoves - opponentMoves
        score = diff * 10 + 50
        return max(0, min(100, score))
