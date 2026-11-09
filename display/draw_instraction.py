from constants import (
    WHITE, YELLOW, MARGIN_TOP, RULES_LINES,
    FONT_TITLE_SIZE, FONT_SUBTITLE_SIZE, FONT_LINE_SIZE,
    GAP_AFTER_TITLE, GAP_BETWEEN_LINES, GAP_SECTION, COMMAND_LINES,
)
from display.utils import draw_centered


def draw_instructions(screen, pygame) -> None:
    fonts = {
        "title": pygame.font.Font(None, FONT_TITLE_SIZE),
        "commands": pygame.font.Font(None, FONT_SUBTITLE_SIZE),
        "rules": pygame.font.Font(None, FONT_LINE_SIZE),
    }

    y = MARGIN_TOP
    y = draw_centered(screen, "Instructions", fonts["title"], YELLOW, y)
    y += GAP_AFTER_TITLE

    for line in COMMAND_LINES:
        y = draw_centered(screen, line, fonts["commands"], WHITE, y)
        y += GAP_BETWEEN_LINES

    y += GAP_SECTION
    for line in RULES_LINES:
        y = draw_centered(screen, line, fonts["rules"], WHITE, y)
        y += GAP_BETWEEN_LINES

    y += GAP_SECTION
    y = draw_centered(screen, "Push ENTER to come back to the main menu", fonts["title"], YELLOW, y)
    y += GAP_BETWEEN_LINES

