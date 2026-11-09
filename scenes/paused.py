import pygame
from constants import Screen
from display.draw_paused import draw_paused
from scenes.base import Scene


class PausedScene(Scene):

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type != pygame.KEYDOWN:
            return
        if event.key == pygame.K_ESCAPE:
            self.game.change_scene(Screen.MENU)
        elif event.key == pygame.K_RETURN or event.key == pygame.K_p:
            self.game.audio.resume()
            self.game.change_scene(Screen.PLAYING, resume=True)


    def draw(self, screen: pygame.Surface) -> None:
        draw_paused(screen, pygame)