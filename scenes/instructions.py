import pygame
from constants import Screen
from display.draw_instraction import draw_instructions
from scenes.base import Scene


class InstructionsScene(Scene):
    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN or event.key == pygame.K_ESCAPE:
                self.game.change_scene(Screen.MENU)


    def draw(self, screen: pygame.Surface) -> None:
        draw_instructions(screen, pygame)