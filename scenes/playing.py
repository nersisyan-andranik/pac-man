from typing import TYPE_CHECKING
import pygame
from constants import Screen, WIDTH, HEIGHT, WEST, SOUTH, EAST, NORTH, BLUE, RED, ORANGE, CYAN, PINK, GhostColor
from display.draw_game import draw_game
from display.utils import sanitize_levels
from maze_adapter import generate_maze
from scenes.base import Scene
import random
import math
from collections import deque


if TYPE_CHECKING:
    from game import Game


class PlayingScene(Scene):
    def __init__(self, game: Game) -> None:
        super().__init__(game)
        self.audio = self.game.audio
        self.pac_points_data : list[tuple[int, int]] = []
        self.super_points_data : list[tuple[int, int]] = []
        self.paused = False
        self.maze = None
        self.center_of_maze = None
        self.cell_size = None
        self.maze_start_point = None
        self.pacman_direction = "left"
        self.pacman_moving = False
        self.mouth_timer = 0.0
        self.mouth_angle = 30
        self.pacman_current_cords = None
        self.walls_locations = None
        self.ghost_start_positions : list[tuple[int, int]] = []
        self.edible = False
        self.pacman_start = False

        self.ghost_move_timer = 0.0
        self.ghost_move_interval = 0.60

        self.pacman_move_timer = 0.0
        self.pacman_move_interval = 0.20

        self.timer = 0.0
        self.edible_time = 0.0
        self.ghost = None

        self.intro_playing = False
        self.current_music = None

        self.pacman_dying = False
        self.time_finished = False

        self.muted = False

        self.cheat_state = {
            "cheat_mode": False,
            "invincible": False,
            "freeze_ghosts": False,
            "double_speed": False,
            "open_cheat_modal": False
        }
        self.rects = {
            "cheat_mode": None,
            "invincible": None,
            "freeze_ghosts": None,
            "double_speed": None,
            "extra_life": None,
            "extra_time": None,
            "skip_level": None,
            "close": None,
            "config_button": None,
            "muted": None
        }

    def get_ghost_target(self, ghost: dict) -> tuple[int, int]:

        pac_row, pac_col = self.pacman_current_cords
        strategy = ghost["strategy"]

        directions = {
            "up": (-1, 0),
            "down": (1, 0),
            "left": (0, -1),
            "right": (0, 1)
        }

        dr, dc = directions[self.pacman_direction]

        if strategy == "blinky":
            return (pac_row, pac_col)

        if strategy == "pinky":
            return (
                pac_row + dr * 4,
                pac_col + dc * 4
            )

        if strategy == "inky":
            red_row, red_col = self.ghost[0]["position"]

            target_row = pac_row + dr * 2
            target_col = pac_col + dc * 2

            return (
                2 * target_row - red_row,
                2 * target_col - red_col
            )

        if strategy == "clyde":
            ghost_row, ghost_col = ghost["position"]

            distance = (
                    abs(ghost_row - pac_row)
                    + abs(ghost_col - pac_col)
            )

            if distance > 8:
                return (pac_row, pac_col)

            return (self.maze.height - 1, 0)

        return (pac_row, pac_col)

    def get_valid_neighbors(self, position: tuple[int, int]) -> list[tuple[int, int]]:

        row, col = position
        directions = [
            (-1, 0, NORTH),
            (0, 1, EAST),
            (1, 0, SOUTH),
            (0, -1, WEST)
        ]

        neighbors = []

        for dr, dc, wall in directions:
            nr = row + dr
            nc = col + dc

            if not (
                    0 <= nr < self.maze.height
                    and 0 <= nc < self.maze.width
            ):
                continue

            if self.maze.cells[row][col] & wall:
                continue

            neighbors.append((nr, nc))

        return neighbors

    def find_short_path(self, start: tuple[int, int], goal: tuple[int, int]) -> list[tuple[int, int]]:

        directions = [
            (-1, 0, NORTH),
            (0, 1, EAST),
            (1, 0, SOUTH),
            (0, -1, WEST)
        ]

        previous = {start: None}
        queue = deque([start])

        best = start

        def distance(position):
            return (
                    (position[0] - goal[0]) ** 2
                    + (position[1] - goal[1]) ** 2
            )

        while queue:
            row, col = queue.popleft()

            if distance((row, col)) < distance(best):
                best = (row, col)

            if (row, col) == goal:
                best = goal
                break

            for dr, dc, wall in directions:
                next_row = row + dr
                next_col = col + dc
                position = (next_row, next_col)

                if not (
                        0 <= next_row < self.maze.height
                        and 0 <= next_col < self.maze.width
                ):
                    continue

                if self.maze.cells[row][col] & wall:
                    continue

                if position in previous:
                    continue

                previous[position] = (row, col)
                queue.append(position)

        path = []
        current = best

        while current is not None:
            path.append(current)
            current = previous[current]

        return path[::-1]

    def get_distance(self, pos1: tuple[int, int], pos2: tuple[int, int]) -> int:
        return (
                abs(pos1[0] - pos2[0])
                + abs(pos1[1] - pos2[1])
        )

    def get_escape_position(self, ghost: dict) -> tuple[int, int]:

        current = ghost["position"]
        pacman = self.pacman_current_cords

        neighbors = self.get_valid_neighbors(current)

        if not neighbors:
            return current

        previous = ghost.get("previous_position")

        # Avoid reversing direction when possible
        options = [
            pos for pos in neighbors
            if pos != previous
        ]

        if not options:
            options = neighbors

        # 70% escape / 30% random
        if random.random() < 0.7:
            return max(
                options,
                key=lambda pos: self.get_distance(pos, pacman)
            )

        return random.choice(options)

    def move_ghosts(self) -> None:
        if self.cheat_state["freeze_ghosts"]:
            return
        from collections import Counter

        positions = [
            ghost["position"]
            for ghost in self.ghost
        ]

        counts = Counter(positions)
        reserved = {
            ghost["position"]
            for ghost in self.ghost
            if ghost["frozen"]
        }

        next_positions = []
        indices = [
            i for i, ghost in enumerate(self.ghost)
            if not ghost["frozen"]
        ]

        indices.sort(
            key=lambda i: counts[self.ghost[i]["position"]] > 1,
            reverse=True
        )

        for index in indices:
            ghost = self.ghost[index]
            current = ghost["position"]

            if self.edible:
                preferred = self.get_escape_position(ghost)
            else:
                goal = self.get_ghost_target(ghost)
                path = self.find_short_path(current, goal)
                preferred = path[1] if len(path) > 1 else current

            neighbors = self.get_valid_neighbors(current)

            free_neighbors = [
                pos for pos in neighbors
                if pos not in positions
                   and pos not in reserved
            ]

            if preferred not in positions and preferred not in reserved:
                next_pos = preferred

            elif free_neighbors:
                if self.edible:
                    next_pos = max(
                        free_neighbors,
                        key=lambda pos: self.get_distance(
                            pos, self.pacman_current_cords
                        )
                    )
                else:
                    next_pos = min(
                        free_neighbors,
                        key=lambda pos: (
                                (pos[0] - goal[0]) ** 2
                                + (pos[1] - goal[1]) ** 2
                        )
                    )
            else:
                next_pos = preferred

            next_positions.append((index, next_pos))
            reserved.add(next_pos)

        for index, position in next_positions:
            self.ghost[index]["position"] = position

    def get_maze_center(self) -> tuple[int, int]:
        center_row = self.maze.height // 2
        center_col = self.maze.width // 2

        valid_cells = []

        for row in range(self.maze.height):
            for col in range(self.maze.width):
                position = (row, col)

                # Exclude completely closed cells
                if len(self.get_valid_neighbors(position)) < 2:
                    continue

                valid_cells.append(position)

        if not valid_cells:
            raise ValueError("No valid center found")

        return min(
            valid_cells,
            key=lambda pos: (
                    abs(pos[0] - center_row)
                    + abs(pos[1] - center_col)
            )
        )

    def generate_points(self) -> None:
        maze = self.maze

        corners = [
            (0, 0),
            (0, maze.width - 1),
            (maze.height - 1, 0),
            (maze.height - 1, maze.width - 1),
        ]

        center_of_maze = self.get_maze_center()

        available_cells = [
            (row_index, col_index)
            for row_index, row in enumerate(maze.cells)
            for col_index, cell in enumerate(row)
            if cell != 15
               and (row_index, col_index) not in corners
               and (row_index, col_index) != center_of_maze
        ]

        count = round(len(available_cells) * 0.6)

        self.pac_points_data = random.sample(
            available_cells, k=count
        )
        self.super_points_data = corners
        self.center_of_maze = center_of_maze
        self.pacman_current_cords = center_of_maze

    def update_movement_speed(self) -> None:
        level = self.game.current_level

        if level == 1:
            self.pacman_move_interval = 0.20
            self.ghost_move_interval = 0.60

        elif level <= 3:
            self.pacman_move_interval = 0.18
            self.ghost_move_interval = 0.55

        elif level <= 6:
            self.pacman_move_interval = 0.16
            self.ghost_move_interval = 0.50

        else:
            self.pacman_move_interval = 0.14
            self.ghost_move_interval = 0.40

    def load_level(self) -> None:
        seed = 42 if self.game.current_level == 0 else 0
        self.update_movement_speed()
        self.game.level_max_time = 90
        self.mouth_timer = 0.0
        self.mouth_angle = 30
        self.ghost_move_timer = 0.0
        self.timer = 0.0
        self.edible = False
        self.edible_time = 0.0
        self.pacman_direction = "left"
        self.pacman_start = False

        self.game.levels = sanitize_levels(self.game.levels, WIDTH, HEIGHT)
        level = self.game.levels[self.game.current_level]
        self.maze = generate_maze(level["width"], level["height"], seed=seed)
        self.generate_points()
        self.ghost_start_positions = [
            (0, 0),
            (0, self.maze.width - 1),
            (self.maze.height - 1, 0),
            (self.maze.height - 1, self.maze.width - 1),
        ]
        self.ghost = [
            {
                "position": self.super_points_data[0],
                "previous_position": None,
                "color": RED,
                "original_color": RED,
                "strategy": "blinky",
                "frozen": False,
            },
            {
                "position": self.super_points_data[1],
                "previous_position": None,
                "color": ORANGE,
                "original_color": ORANGE,
                "strategy": "clyde",
                "frozen": False
            },
            {
                "position": self.super_points_data[2],
                "previous_position": None,
                "color": CYAN,
                "original_color": CYAN,
                "strategy": "inky",
                "frozen": False
            },
            {
                "position": self.super_points_data[3],
                "previous_position": None,
                "color": PINK,
                "original_color": PINK,
                "strategy": "pinky",
                "frozen": False
            }
        ]
        self.wall_checker()

    def on_enter(self) -> None:
        """Start a new game."""
        self.game.lives = 3
        self.game.score = 0
        self.game.current_level = 0
        self.game.all_complete = False
        self.pacman_move_timer = 0.0

        for key in self.cheat_state:
            self.cheat_state[key] = False

        self.game.levels = sanitize_levels(
            self.game.levels, WIDTH, HEIGHT
        )
        self.load_level()

        self.pacman_dying = False
        self.intro_playing = True
        self.pacman_start = False

        self.audio.play_intro()

    def wall_checker(self) -> None:
        row, col = self.pacman_current_cords
        cell = self.maze.cells[row][col]
        walls_locations: list[str] = []

        if cell & NORTH:
            walls_locations.append("up")
        if cell & EAST:
            walls_locations.append("right")
        if cell & SOUTH:
            walls_locations.append("down")
        if cell & WEST:
            walls_locations.append("left")
        self.walls_locations = walls_locations

    def calculate_score(self) -> None:
        if self.pacman_current_cords in self.pac_points_data:
            self.game.score += self.game.points_per_pacgum
            self.pac_points_data.remove(self.pacman_current_cords)
            self.audio.play_effect("eat")

        elif self.pacman_current_cords in self.super_points_data:
            self.game.score += self.game.points_per_super_pacgum
            self.super_points_data.remove(self.pacman_current_cords)
            self.audio.play_effect("eat")
            if self.cheat_state["freeze_ghosts"]:
                return

            for item in self.ghost:
                if not item["frozen"]:
                    item["color"] = BLUE
            self.edible = True
            self.edible_time = 0.0

    def lives_manager(self) -> None:
        if self.cheat_state["invincible"]:
            return

        if self.cheat_state["freeze_ghosts"]:
            return

        for index, ghost in enumerate(self.ghost):

            if ghost["position"] != self.pacman_current_cords:
                continue

            if ghost["frozen"]:
                continue

            if self.edible:
                self.game.score += self.game.points_per_ghost
                self.audio.play_effect("eat_ghost")
                ghost["position"] = self.ghost_start_positions[index]
                ghost["previous_position"] = None
                ghost["frozen"] = True
                ghost["color"] = ghost["original_color"]
                return
            else:
                self.pacman_dying = True
                self.pacman_start = False
                self.audio.stop_all()
                self.audio.play_effect("death")
                return

    def time_manager(self) -> None:
        self.game.level_max_time -= 1
        if self.game.level_max_time == 0:
            self.time_finished = True
            self.pacman_start = False
            self.audio.stop_all()
            self.audio.play_music("time_finished", loops=1)

    def complete_level(self, force: bool = False) -> bool:
        if not force and (
                self.pac_points_data or self.super_points_data
        ):
            return False
        next_level = self.game.current_level + 1

        if next_level >= len(self.game.levels):
            pygame.mixer.music.stop()
            self.game.all_complete = True
            self.game.change_scene(Screen.GAME_OVER)
            self.cheat_state["open_cheat_modal"] = False
            return True

        self.game.current_level = next_level
        self.load_level()

        return True

    def move_pacman(self) -> None:
        directions = {
            "up": (-1, 0),
            "down": (1, 0),
            "left": (0, -1),
            "right": (0, 1)
        }

        self.wall_checker()

        if self.pacman_direction not in self.walls_locations:
            row, col = self.pacman_current_cords
            self.pacman_current_cords = (row + directions[self.pacman_direction][0], col + directions[self.pacman_direction][1])
            # self.pacman_moving = True

    def reset_pacman_position(self) -> None:
        self.pacman_current_cords = self.center_of_maze
        self.pacman_direction = "left"
        self.pacman_start = False
        self.mouth_timer = 0.0
        self.mouth_angle = 30

        for ghost_index, item in enumerate(self.ghost):
            item["position"] = self.ghost_start_positions[ghost_index]
            item["previous_position"] = None
            item["frozen"] = False
            item["color"] = item["original_color"]

        self.ghost_move_timer = 0.0
        self.edible = False
        self.edible_time = 0.0
        self.wall_checker()

    def handle_event(self, event: pygame.event.Event) -> None:

        if event.type == self.audio.INTRO_FINISHED:
            if not self.intro_playing:
                return
            self.intro_playing = False
            self.pacman_start = True
            self.audio.update_ghost_music(self.edible)
            return

        if event.type == self.audio.DEATH_FINISHED:
            if not self.pacman_dying:
                return

            self.pacman_dying = False
            self.game.lives -= 1

            if self.game.lives <= 0:
                self.audio.stop_all()
                self.game.change_scene(Screen.GAME_OVER)
            else:
                self.reset_pacman_position()
                self.audio.update_ghost_music(self.edible)

            return

        if event.type == self.audio.TIME_FINISHED:
            if not self.time_finished:
                return
            self.time_finished = False
            self.game.change_scene(Screen.GAME_OVER)
            return


        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:

                rect = getattr(self, "rects", None)["config_button"]
                if rect is not None and rect.collidepoint(event.pos):
                    # self.cheat_state["cheat_mode"] = not self.cheat_state["cheat_mode"]
                    self.cheat_state["open_cheat_modal"] = not self.cheat_state["open_cheat_modal"]


                rect = getattr(self, "rects", None)["invincible"]
                if rect is not None and rect.collidepoint(event.pos):
                    self.cheat_state["invincible"] = not self.cheat_state["invincible"]

                rect = getattr(self, "rects", None)["freeze_ghosts"]
                if rect is not None and rect.collidepoint(event.pos):
                    self.cheat_state["freeze_ghosts"] = not self.cheat_state["freeze_ghosts"]
                    if self.cheat_state["freeze_ghosts"]:
                        self.audio.stop_all()
                    else:
                        self.audio.update_ghost_music(self.edible)

                rect = getattr(self, "rects", None)["double_speed"]
                if rect is not None and rect.collidepoint(event.pos):
                    self.cheat_state["double_speed"] = not self.cheat_state["double_speed"]
                    self.pacman_move_interval = (
                        0.1 if self.cheat_state["double_speed"] else 0.2
                    )

                rect = getattr(self, "rects", None)["extra_life"]
                if rect is not None and rect.collidepoint(event.pos):
                    self.game.lives += 1

                rect = getattr(self, "rects", None)["extra_time"]
                if rect is not None and rect.collidepoint(event.pos):
                    self.game.level_max_time += 60

                rect = getattr(self, "rects", None)["skip_level"]
                if rect is not None and rect.collidepoint(event.pos):
                    self.intro_playing = False
                    self.complete_level(force=True)

                rect = getattr(self, "rects", None)["close"]
                if rect is not None and rect.collidepoint(event.pos):
                    self.audio.resume()
                    self.cheat_state["open_cheat_modal"] = not self.cheat_state["open_cheat_modal"]

                rect = getattr(self, "rects", None)["muted"]
                if rect is not None and rect.collidepoint(event.pos):
                    self.audio.set_muted(not self.audio.muted)

            return

        if event.type != pygame.KEYDOWN:
            return
        if event.key == pygame.K_ESCAPE:
            self.audio.stop_all()
            self.game.change_scene(Screen.GAME_OVER)
            self.cheat_state["open_cheat_modal"] = False
            return

        if event.key == pygame.K_p:
            self.audio.pause()
            self.game.change_scene(Screen.GAME_PAUSED)
            self.cheat_state["open_cheat_modal"] = False
            return

        directions = {
            pygame.K_UP: "up",
            pygame.K_DOWN: "down",
            pygame.K_LEFT: "left",
            pygame.K_RIGHT: "right",
            pygame.K_w: "up",
            pygame.K_s: "down",
            pygame.K_a: "left",
            pygame.K_d: "right",
        }

        if event.key in directions:
            self.pacman_start = True
            direction = directions[event.key]
            self.pacman_direction = direction

    def update(self, dt: float) -> None:
        if self.intro_playing or self.pacman_dying or self.time_finished:
            return

        if not self.cheat_state["freeze_ghosts"]:
            self.audio.update_ghost_music(self.edible)

        if self.cheat_state["open_cheat_modal"]:
            return

        self.wall_checker()
        if self.complete_level():
            return

        self.timer += dt
        if self.timer >= 1.0:
            self.timer -= 1.0
            self.time_manager()

        if self.edible:
            self.edible_time += dt
            if self.edible_time >= 10.0:
                self.edible_time -= 10.0
                self.edible = False
                for _index, _ghost in enumerate(self.ghost):
                    _ghost["frozen"] = False
                    _ghost["color"] = list(GhostColor)[_index].value

        self.pacman_move_timer += dt
        if self.pacman_move_timer >= self.pacman_move_interval:
            self.pacman_move_timer -= self.pacman_move_interval
            if self.pacman_start:
                self.move_pacman()
                self.calculate_score()
                self.lives_manager()

        self.ghost_move_timer += dt
        if self.ghost_move_timer >= self.ghost_move_interval:
            self.ghost_move_timer -= self.ghost_move_interval
            self.move_ghosts()
            self.lives_manager()

        if self.pacman_start:
            self.mouth_timer += dt

            self.mouth_angle = (
                    22 + 22 * math.sin(self.mouth_timer * 12)
            )

    def draw(self, screen: pygame.Surface) -> None:
        draw_game(screen, self)
