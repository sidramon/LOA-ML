# Board AI Pygame

This project implements a board game AI using Python and Pygame. The AI utilizes a minimax algorithm with alpha-beta pruning to make decisions, and the game state is visually represented in real-time using Pygame.

## Project Structure

```
board-ai-pygame
├── src
│   ├── ml.py               # Main game logic and AI implementation
│   ├── preview_pygame.py   # Real-time graphical preview using Pygame
│   └── __init__.py         # Package initialization
├── tests
│   └── test_ml.py          # Unit tests for game logic
├── requirements.txt         # Project dependencies
├── .gitignore               # Files to ignore in version control
└── README.md                # Project documentation
```

## Installation

To set up the project, ensure you have Python installed on your machine. Then, clone the repository and install the required dependencies:

```bash
git clone <repository-url>
cd board-ai-pygame
pip install -r requirements.txt
```

## Usage

To run the game and see the AI in action, execute the following command:

```bash
python src/preview_pygame.py
```

This will open a Pygame window displaying the game board and pieces. You can interact with the game using your mouse or keyboard as specified in the game controls.

## Features

- **Game Logic**: The core game mechanics are implemented in `ml.py`, including move generation and evaluation.
- **AI Player**: The AI uses a minimax algorithm with alpha-beta pruning to make optimal moves.
- **Real-time Preview**: The game state is visually represented in real-time using Pygame, allowing for an interactive experience.

## Testing

Unit tests for the game logic can be found in the `tests/test_ml.py` file. To run the tests, use the following command:

```bash
pytest tests/test_ml.py
```

## Contributing

Contributions are welcome! Please open an issue or submit a pull request for any enhancements or bug fixes.

## License

This project is licensed under the MIT License. See the LICENSE file for more details.