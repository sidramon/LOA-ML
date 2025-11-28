import unittest
from src.ml import Board, Move

class TestBoard(unittest.TestCase):

    def setUp(self):
        self.board = Board()

    def test_initial_board_setup(self):
        expected_board = [
            [0, 2, 2, 2, 2, 2, 2, 0],
            [4, 0, 0, 0, 0, 0, 0, 4],
            [4, 0, 0, 0, 0, 0, 0, 4],
            [4, 0, 0, 0, 0, 0, 0, 4],
            [4, 0, 0, 0, 0, 0, 0, 4],
            [4, 0, 0, 0, 0, 0, 0, 4],
            [4, 0, 0, 0, 0, 0, 0, 4],
            [0, 2, 2, 2, 2, 2, 2, 0],
        ]
        self.assertEqual(self.board.board, expected_board)

    def test_get_all_possible_moves(self):
        moves = self.board.get_all_possible_moves(2)
        self.assertGreater(len(moves), 0)

    def test_make_move(self):
        move = Move(1, 0, 2, 0)  # Move from (1, 0) to (2, 0)
        self.board.make_move(move)
        self.assertEqual(self.board.board[2][0], 2)
        self.assertEqual(self.board.board[1][0], 0)

    def test_undo_move(self):
        move = Move(1, 0, 2, 0)
        self.board.make_move(move)
        self.board.undo_move()
        self.assertEqual(self.board.board[1][0], 4)
        self.assertEqual(self.board.board[2][0], 0)

    def test_is_game_over(self):
        self.assertFalse(self.board.is_game_over())
        # Simulate a game over condition
        self.board.countPlayer2 = 0
        self.assertTrue(self.board.is_game_over())

    def test_get_winner(self):
        self.board.countPlayer2 = 0
        self.assertEqual(self.board.get_winner(), 4)
        self.board.countPlayer4 = 0
        self.assertEqual(self.board.get_winner(), 2)

if __name__ == '__main__':
    unittest.main()