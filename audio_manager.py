import pygame

from paths import asset_path


class AudioManager:
    """Represent the AudioManager component."""
    def __init__(self) -> None:
        """Initialize the instance.
        """
        self.INTRO_FINISHED = pygame.event.custom_type()
        self.DEATH_FINISHED = pygame.event.custom_type()
        self.TIME_FINISHED = pygame.event.custom_type()

        self.music_files = {
            "intro": asset_path("sounds/pacman_beginning.wav"),
            "normal": asset_path("sounds/ghost_normal_move.ogg"),
            "edible": asset_path("sounds/ghost_turn_to_blue.ogg"),
            "time_finished": asset_path("sounds/pacman_death.wav"),
        }

        self.sounds = {
            "eat": pygame.mixer.Sound(
                asset_path("sounds/eat.mp3")
            ),
            "eat_ghost": pygame.mixer.Sound(
                asset_path("sounds/pacman_eat_ghost.wav")
            ),
            "death": pygame.mixer.Sound(
                asset_path("sounds/pacman_death.wav")
            ),
        }

        pygame.mixer.set_num_channels(
            max(12, pygame.mixer.get_num_channels())
        )
        pygame.mixer.set_reserved(4)

        self.eat_channel = pygame.mixer.Channel(1)
        self.ghost_channel = pygame.mixer.Channel(2)
        self.death_channel = pygame.mixer.Channel(3)

        self.muted = False
        self.current_music: str | None = None

        self.death_channel.set_endevent(
            self.DEATH_FINISHED
        )

        pygame.mixer.music.set_volume(0.4)
        self.eat_channel.set_volume(0.4)
        self.ghost_channel.set_volume(0.6)
        self.death_channel.set_volume(1.0)

    def play_music(self, mode: str, loops: int = -1) -> None:
        """Perform play music.

        Args:
            mode: Input for play music.
            loops: Input for play music.
        """
        if self.current_music == mode:
            return

        pygame.mixer.music.set_endevent(pygame.NOEVENT)
        pygame.mixer.music.load(self.music_files[mode])

        if mode == "intro":
            pygame.mixer.music.set_endevent(
                self.INTRO_FINISHED
            )
        elif mode == "time_finished":
            pygame.mixer.music.set_endevent(
                self.TIME_FINISHED
            )

        pygame.mixer.music.play(loops)
        self.current_music = mode

    def play_intro(self) -> None:
        """Perform play intro.
        """
        self.play_music("intro", loops=0)

    def update_ghost_music(self, edible: bool) -> None:
        """Update ghost music.

        Args:
            edible: Input for update ghost music.
        """
        mode = "edible" if edible else "normal"
        self.play_music(mode)

    def play_effect(self, name: str) -> None:
        """Perform play effect.

        Args:
            name: Input for play effect.
        """
        if name == "eat":
            channel = pygame.mixer.find_channel()

            if channel is not None:
                channel.set_volume(
                    0.0 if self.muted else 0.4
                )
                channel.play(self.sounds["eat"])
        elif name == "eat_ghost":
            self.ghost_channel.play(
                self.sounds["eat_ghost"]
            )

        elif name == "death":
            pygame.mixer.music.set_endevent(pygame.NOEVENT)
            pygame.mixer.music.stop()

            self.ghost_channel.stop()
            self.current_music = None

            self.death_channel.set_endevent(
                self.DEATH_FINISHED
            )
            self.death_channel.play(
                self.sounds["death"]
            )

    def set_muted(self, muted: bool) -> None:
        """Set muted.

        Args:
            muted: Input for set muted.
        """
        self.muted = muted

        pygame.mixer.music.set_volume(
            0.0 if muted else 0.4
        )
        self.eat_channel.set_volume(
            0.0 if muted else 0.4
        )
        self.ghost_channel.set_volume(
            0.0 if muted else 0.6
        )
        self.death_channel.set_volume(
            0.0 if muted else 1.0
        )

        volume = 0.0 if muted else 0.4

        for index in range(
            4, pygame.mixer.get_num_channels()
        ):
            pygame.mixer.Channel(index).set_volume(volume)

    def pause(self) -> None:
        """Perform pause.
        """
        pygame.mixer.music.pause()
        pygame.mixer.pause()

    def resume(self) -> None:
        """Perform resume.
        """
        pygame.mixer.music.unpause()
        pygame.mixer.unpause()

    def stop_all(self) -> None:
        """Perform stop all.
        """
        pygame.mixer.music.set_endevent(pygame.NOEVENT)
        self.death_channel.set_endevent(pygame.NOEVENT)

        pygame.mixer.music.stop()
        pygame.mixer.stop()

        self.current_music = None
