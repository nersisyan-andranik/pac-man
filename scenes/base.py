from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

import pygame

if TYPE_CHECKING:
    from game import Game


class Scene(ABC):
    """One screen of the game (menu, playing, game over...)."""

    def __init__(self, game: Game) -> None:
        """Initialize the instance.

        Args:
            game: Input for   init  .
        """
        self.game = game

    def on_enter(self) -> None:
        """Called every time this scene becomes the active one."""

    @abstractmethod
    def handle_event(self, event: pygame.event.Event) -> None:
        """React to one pygame event."""

    def update(self, dt: float) -> None:
        """Update the logic. dt = seconds since the last frame."""

    @abstractmethod
    def draw(self, screen: pygame.Surface) -> None:
        """Draw the scene."""
