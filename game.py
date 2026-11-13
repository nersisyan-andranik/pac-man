import pygame
from typing import Any
from audio_manager import AudioManager
from constants import FPS, BLACK, Screen, HEIGHT, WIDTH
from scenes.base import Scene
from scenes.game_over import GameOverScene
from scenes.instructions import InstructionsScene
from scenes.menu import MenuScene
from scenes.paused import PausedScene
from scenes.playing import PlayingScene


class Game:
    """Represent the Game component."""
    def __init__(self, config: dict[str, Any]) -> None:
        """Initialize the instance.

        Args:
            config: Input for   init  .
        """
        pygame.init()
        self.current_level = 0
        self.levels = config["level"]
        self.lives = config["lives"]
        self.pacgum = config["pacgum"]
        self.points_per_pacgum = config["points_per_pacgum"]
        self.points_per_super_pacgum = config["points_per_super_pacgum"]
        self.points_per_ghost = config["points_per_ghost"]
        self.seed = config["seed"]
        self.level_max_time = config["level_max_time"]
        self.highscore_filename = config["highscore_filename"]
        self.clock = pygame.time.Clock()
        self.running = True
        self.audio = AudioManager()
        self.scenes: dict[Screen, Scene] = {
            Screen.MENU: MenuScene(self),
            Screen.INSTRUCTIONS: InstructionsScene(self),
            Screen.PLAYING: PlayingScene(self),
            Screen.GAME_OVER: GameOverScene(self),
            Screen.GAME_PAUSED: PausedScene(self),
        }
        self.scene = self.scenes[Screen.MENU]
        self.scene.on_enter()
        self.score = 0
        self.all_complete = False

        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Pac-Man")

    def change_scene(
            self,
            screen_id: Screen,
            resume: bool = False
    ) -> None:
        """Perform change scene.

        Args:
            screen_id: Input for change scene.
            resume: Input for change scene.
        """
        self.scene = self.scenes[screen_id]
        if not resume:
            self.scene.on_enter()

    def quit(self) -> None:
        """Perform quit.
        """
        self.running = False

    def run(self) -> None:
        """Perform run.
        """
        while self.running:
            dt = self.clock.tick(FPS) / 1000
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.quit()
                else:
                    self.scene.handle_event(event)

            self.scene.update(dt)
            self.screen.fill(BLACK)
            self.scene.draw(self.screen)
            pygame.display.flip()

        pygame.quit()
