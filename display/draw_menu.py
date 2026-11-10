from constants import (
    WHITE, YELLOW, MARGIN_TOP,
    FONT_TITLE_SIZE, FONT_SUBTITLE_SIZE, FONT_LINE_SIZE,
    GAP_AFTER_TITLE, GAP_BETWEEN_LINES, GAP_SECTION, MENU_LINES,
)
from display.utils import draw_centered
import pygame
from types import ModuleType


def draw_menu(
    screen: pygame.Surface,
    pygame: ModuleType,
    top_scores: list[str],
) -> None:
    """Draw menu on the screen.

    Args:
        screen: Input for draw menu.
        pygame: Input for draw menu.
        top_scores: Input for draw menu.
    """
    fonts = {
        "title": pygame.font.Font(None, FONT_TITLE_SIZE),
        "menu": pygame.font.Font(None, FONT_SUBTITLE_SIZE),
        "score": pygame.font.Font(None, FONT_LINE_SIZE),
    }

    y = MARGIN_TOP
    y = draw_centered(
        screen, "Pac-Man", fonts["title"], YELLOW, y
    )
    y += GAP_AFTER_TITLE

    for line in MENU_LINES:
        y = draw_centered(
            screen, line, fonts["menu"], WHITE, y
        )
        y += GAP_BETWEEN_LINES

    y += GAP_SECTION
    y = draw_centered(
        screen, "Highscores", fonts["title"], YELLOW, y
    )
    y += GAP_BETWEEN_LINES

    if not top_scores:
        draw_centered(
            screen, "No scores yet", fonts["score"], WHITE, y
        )
        return

    for line in top_scores:
        y = draw_centered(
            screen, line, fonts["score"], WHITE, y
        )
        y += GAP_BETWEEN_LINES
