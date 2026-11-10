from constants import (
    WHITE, MARGIN_TOP,
    FONT_TITLE_SIZE, FONT_SUBTITLE_SIZE,
    GAP_AFTER_TITLE, GAP_BETWEEN_LINES, GAP_SECTION, INPUT_LINES, YELLOW,
    INPUT_BOX_WIDTH, INPUT_BOX_HEIGHT, INPUT_BOX_PADDING
)
from display.utils import draw_centered
import pygame
from types import ModuleType


def get_congratulation_message(score: int) -> str:
    """Get congratulation message.

    Args:
        score: Input for get congratulation message.

    Returns:
        The result of get congratulation message.
    """
    if score >= 10000:
        return "LEGENDARY! You are a Pac-Man Master!"
    elif score >= 5000:
        return "AMAZING! Outstanding performance!"
    elif score >= 2000:
        return "EXCELLENT! You did a great job!"
    elif score >= 1000:
        return "GREAT JOB! Keep it up!"
    elif score >= 500:
        return "WELL DONE! Nice effort!"
    else:
        return "GOOD TRY! Keep practicing!"


def draw_game_over(
    screen: pygame.Surface, pygame: ModuleType, score: int = 0,
    player_name: str = "Anonymous", all_complete: bool = False
) -> None:
    """Draw game over on the screen.

    Args:
        screen: Input for draw game over.
        pygame: Input for draw game over.
        score: Input for draw game over.
        player_name: Input for draw game over.
        all_complete: Input for draw game over.
    """
    fonts = {
        "title": pygame.font.Font(None, FONT_TITLE_SIZE),
        "input": pygame.font.Font(None, FONT_SUBTITLE_SIZE),
    }
    title = "VICTORY" if all_complete else "GAME OVER"
    y = MARGIN_TOP
    y = draw_centered(screen, title, fonts["title"], WHITE, y)
    y += GAP_AFTER_TITLE

    y = draw_centered(screen, f"Score:  {score}", fonts["input"], WHITE, y)
    y += GAP_BETWEEN_LINES

    if all_complete:
        message = get_congratulation_message(score)
        y = draw_centered(
            screen, message,
            fonts["input"], YELLOW, y
        )
        y += GAP_SECTION

    for line in INPUT_LINES:
        y = draw_centered(screen, line, fonts["input"], WHITE, y)
        y += GAP_BETWEEN_LINES

    box = pygame.Rect(200, 200, INPUT_BOX_WIDTH, INPUT_BOX_HEIGHT)
    box.midtop = (screen.get_width() // 2, y)
    pygame.draw.rect(screen, YELLOW, box, 2)

    cursor = "|" if (pygame.time.get_ticks() // 500) % 2 == 0 else ""
    text = fonts["input"].render(player_name + cursor, True, WHITE)
    screen.blit(
        text, text.get_rect(
            left=box.left + INPUT_BOX_PADDING, centery=box.centery
        ),
    )
    y = box.bottom

    y += GAP_SECTION
    y = draw_centered(
        screen, "Or press the ESC key to exit without saving",
        fonts["input"], WHITE, y,
    )
