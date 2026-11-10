"""Command-line entry point for Pac-Man."""

import sys
import pygame
from errors import MazeGenerationError
from game import Game
from json_parser import load_config


def main() -> int:
    """Load configuration and run the game with clean error messages."""
    config = load_config()

    try:
        Game(config).run()
    except (MazeGenerationError, pygame.error, OSError, ValueError) as error:
        print(f"Error: {error}", file=sys.stderr)
        sys.exit(1)
    return 0


if __name__ == "__main__":
    main()
