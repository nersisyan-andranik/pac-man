import pygame
from constants import Screen, HIGHSCORE_PATH, TOP_SCORES_LIMIT
from display.draw_menu import draw_menu
from score.load_top_scores import load_top_scores
from scenes.base import Scene


class MenuScene(Scene):
    def on_enter(self) -> None:
        self.top_scores = load_top_scores(HIGHSCORE_PATH, TOP_SCORES_LIMIT)

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type != pygame.KEYDOWN:
            return
        if event.key == pygame.K_ESCAPE:
            self.game.quit()
        elif event.key == pygame.K_RETURN:
            self.game.change_scene(Screen.INSTRUCTIONS)
        elif event.key == pygame.K_SPACE:
            self.game.change_scene(Screen.PLAYING)
        elif event.key == pygame.K_LMETA:          # debug shortcut
            self.game.change_scene(Screen.GAME_OVER)

    def draw(self, screen: pygame.Surface) -> None:
        draw_menu(screen, pygame, self.top_scores)