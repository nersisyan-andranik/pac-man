import sys
import pygame
from constants import (
    MIN_CELL_SIZE, MIN_MAZE_WIDTH, MIN_MAZE_HEIGHT,
    HUD_HEIGHT, MAZE_MARGIN, DEFAULT_LEVEL_SIZE,
)
from pathlib import Path


def load_icon(
    path: Path | str,
    size: tuple[int, int] = (36, 36),
) -> pygame.Surface | None:
    """Load icon.

    Args:
        path: Input for load icon.
        size: Input for load icon.
    """
    image = pygame.image.load(path)
    return pygame.transform.smoothscale(image, size)


def draw_centered(
    screen: pygame.Surface,
    text: str,
    font: pygame.font.Font,
    color: pygame.Color | str | tuple[int, int, int],
    y: int,
) -> int:
    """Draw text centered horizontally with its top at y. Return its bottom."""
    surface = font.render(text, True, color)
    rect = surface.get_rect(top=y, centerx=screen.get_width() // 2)
    screen.blit(surface, rect)
    return rect.bottom


def maze_limits(window_w: int, window_h: int) -> tuple[int, int]:
    """Return the largest maze fitting the minimum cell size."""
    max_w = (window_w - 2 * MAZE_MARGIN) // MIN_CELL_SIZE
    max_h = (window_h - HUD_HEIGHT - MAZE_MARGIN) // MIN_CELL_SIZE
    return max_w, max_h


def _as_int(value: object, default: int) -> int:
    """Perform  as int.

    Args:
        value: Input for  as int.
        default: Input for  as int.

    Returns:
        The result of  as int.
    """
    if isinstance(value, int) and not isinstance(value, bool):
        return value
    return default


def sanitize_levels(
    raw_levels: object, window_w: int, window_h: int
) -> list[dict[str, int]]:
    """Return valid level dimensions clamped to the window."""
    if not isinstance(raw_levels, list) or not raw_levels:
        print(
            "config: 'levels' missing or empty, using defaults",
            file=sys.stderr,
        )
        raw_levels = [{} for _ in range(10)]

    max_w, max_h = maze_limits(window_w, window_h)
    levels: list[dict[str, int]] = []
    for index, item in enumerate(raw_levels, start=1):
        data = item if isinstance(item, dict) else {}
        width = _as_int(data.get("width"), DEFAULT_LEVEL_SIZE[0])
        height = _as_int(data.get("height"), DEFAULT_LEVEL_SIZE[1])

        new_w = min(max(width, MIN_MAZE_WIDTH), max_w)
        new_h = min(max(height, MIN_MAZE_HEIGHT), max_h)
        if (new_w, new_h) != (width, height):
            print(f"config: level {index} size {width}x{height} not allowed, "
                  f"using {new_w}x{new_h}", file=sys.stderr)
        levels.append({"width": new_w, "height": new_h})
    return levels
