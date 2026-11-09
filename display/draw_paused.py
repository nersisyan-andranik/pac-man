from constants import (
    WHITE, YELLOW, MARGIN_TOP,
    FONT_TITLE_SIZE, FONT_SUBTITLE_SIZE, FONT_LINE_SIZE,
    GAP_AFTER_TITLE, GAP_BETWEEN_LINES, GAP_SECTION, PAUSED_SCREEN_COMMANDS,
)
from display.utils import draw_centered


def draw_paused(screen, pygame) -> None:
    fonts = {
        "title": pygame.font.Font(None, FONT_TITLE_SIZE),
        "menu": pygame.font.Font(None, FONT_SUBTITLE_SIZE),
        "score": pygame.font.Font(None, FONT_LINE_SIZE),
    }

    y = MARGIN_TOP
    y = draw_centered(screen, "Pac-Man", fonts["title"], YELLOW, y)
    y += GAP_AFTER_TITLE

    y += GAP_SECTION
    y = draw_centered(screen, "PAUSED", fonts["title"], WHITE, y)
    y += GAP_AFTER_TITLE

    y += GAP_SECTION
    y = draw_centered(screen, "Game progress is saved while you paused", fonts["menu"], WHITE, y)
    y += GAP_AFTER_TITLE

    for line in PAUSED_SCREEN_COMMANDS:
        y = draw_centered(screen, line, fonts["menu"], WHITE, y)
        y += GAP_BETWEEN_LINES
