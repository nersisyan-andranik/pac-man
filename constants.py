from enum import Enum, auto
from pathlib import Path
import string

NORTH = 1
EAST = 2
SOUTH = 4
WEST = 8

MIN_CELL_SIZE = 30
MIN_MAZE_WIDTH = 9
MIN_MAZE_HEIGHT = 7
HUD_HEIGHT = 100
MAZE_MARGIN = 20
DEFAULT_LEVEL_SIZE = (21, 15)
WALL_WIDTH = 2

BASE_DIR = Path(__file__).parent
HIGHSCORE_PATH = BASE_DIR / "highscore.json"

WIDTH = 1300
HEIGHT = 800
FPS = 60

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
YELLOW = (255, 255, 0)
BLUE = (0, 0, 255)
RED = (255, 0, 0)
PINK = (255, 184, 255)
CYAN = (0, 255, 255)
ORANGE = (255, 184, 82)
MARGIN_TOP = 20

PLAYER_SPEED = 4
TOP_SCORES_LIMIT = 10

FONT_TITLE_SIZE = 50
FONT_SUBTITLE_SIZE = 40
FONT_LINE_SIZE = 35

GAP_AFTER_TITLE = 40
GAP_BETWEEN_LINES = 10
GAP_SECTION = 40


NAME_MAX_LENGTH = 10
INPUT_BOX_WIDTH = 400
INPUT_BOX_HEIGHT = 50
INPUT_BOX_PADDING = 12


MENU_LINES = [
    "Press SPACE to play",
    "Press ENTER to read the instructions",
    "Press ESC to exit",
]

COMMAND_LINES = [
    "Use the ARROW KEYS to move Pac-Man",
    "UP - move up",
    "DOWN - move down",
    "LEFT - move left",
    "RIGHT - move right",
    "P - Pause / Resume"
]

RULES_LINES = [
    "Eat all the dots scattered around the maze.",
    "Avoid the ghosts: if one touches you, you lose a life.",
    "Eat every dot in the maze to win the level!",
]
INPUT_LINES = [
    "Insert your name that press ENTER to save",
    "(Alphanumeric  characters only)"
]


ALLOWED_CHARS = string.ascii_letters + string.digits + " "

DEFAULTS = {
    "highscore_filename": "highscore.json",
    "lives": 3,
    "pacgum": 42,
    "points_per_pacgum": 10,
    "points_per_super_pacgum": 50,
    "points_per_ghost": 200,
    "seed": 42,
    "level_max_time": 90,
    "level": [
        {"width": 1100, "height": 800}
    ],
}

EXPECTED_TYPES: dict[str, type | tuple[type, ...]] = {
    "highscore_filename": str,
    "lives": int,
    "pacgum": int,
    "points_per_pacgum": int,
    "points_per_super_pacgum": int,
    "points_per_ghost": int,
    "seed": int,
    "level_max_time": (int, float),
    "level": list,
}

LEVEL_EXPECTED_TYPES: dict[str, type | tuple[type, ...]] = {
    "width": int,
    "height": int,
}

PAUSED_SCREEN_COMMANDS = [
    "ENTER - Resume",
    "ESC - Return to Main Menu",
]

REQUIRED_LEVEL_KEYS = ("width", "height")


class Screen(Enum):
    """Represent the Screen component."""
    MENU = auto()
    PLAYING = auto()
    GAME_OVER = auto()
    INSTRUCTIONS = auto()
    GAME_PAUSED = auto()


class Direction(Enum):
    """Represent the Direction component."""
    UP = (0, -1)
    DOWN = (0, 1)
    LEFT = (-1, 0)
    RIGHT = (1, 0)


class GhostColor(Enum):
    """Represent the GhostColor component."""
    BLINKY = RED
    CLYDE = ORANGE
    INKY = CYAN
    PINKY = PINK
