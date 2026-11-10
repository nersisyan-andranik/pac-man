import pygame
from constants import (
    Screen, HIGHSCORE_PATH, NAME_MAX_LENGTH, ALLOWED_CHARS,
)
from display.draw_game_over import draw_game_over
from score.save_score import save_score
from scenes.base import Scene


class GameOverScene(Scene):
    """Represent the GameOverScene component."""
    def on_enter(self) -> None:
        """Perform on enter.
        """
        self.player_name = ""

    def handle_event(self, event: pygame.event.Event) -> None:
        """Handle event.

        Args:
            event: Input for handle event.
        """
        if event.type != pygame.KEYDOWN:
            return

        if event.key == pygame.K_ESCAPE:
            self.game.change_scene(Screen.MENU)
        elif event.key == pygame.K_RETURN:
            name = " ".join(self.player_name.split())
            if name:
                save_score(HIGHSCORE_PATH, name, self.game.score)
            self.game.change_scene(Screen.MENU)
        elif event.key == pygame.K_BACKSPACE:
            self.player_name = self.player_name[:-1]
        elif (
            event.unicode
            and event.unicode in ALLOWED_CHARS
            and len(self.player_name) < NAME_MAX_LENGTH
        ):
            self.player_name += event.unicode

    def draw(self, screen: pygame.Surface) -> None:
        """Perform draw.

        Args:
            screen: Input for draw.
        """
        draw_game_over(
            screen, pygame, self.game.score,
            self.player_name, self.game.all_complete,
        )
