from constants import (MARGIN_TOP, FONT_LINE_SIZE, MIN_CELL_SIZE,
                       YELLOW, WHITE, NORTH, EAST, SOUTH, WEST, BLUE, WALL_WIDTH, PINK, RED, ORANGE, CYAN)
import math
import pygame

from display.draw_cheat_mode import draw_toggle, draw_cheat_menu, draw_neon_button
from display.utils import load_icon
from paths import asset_path


def compute_cell_size(screen, scene, margin_x=15, margin_bottom=15) -> int:
    """Largest cell size (in pixels) so the whole maze fits below `top`."""
    available_w = screen.get_width() - 2 * margin_x
    available_h = screen.get_height() - scene.maze_start_point - margin_bottom
    return max(MIN_CELL_SIZE, min(available_w // scene.maze.width, available_h // scene.maze.height))

def draw_stats(screen, scene) -> int:
    """stats: list of (label, value). Label in yellow above, value in white below."""

    stats = [
        ("SCORE", scene.game.score),
        ("LIVES", scene.game.lives),
        ("LEVEL", f"LEVEL: {scene.game.current_level + 1} / {len(scene.game.levels)}"),
        ("TIME", scene.game.level_max_time),
        ("CHEAT_MODE", None )

    ]
    column_width = screen.get_width() / len(stats)
    font = pygame.font.Font(None, FONT_LINE_SIZE)

    for index, (label, value) in enumerate(stats):
        center_x = round(column_width * (index + 0.5))

        label_surface = font.render(label, True, YELLOW)
        label_rect = label_surface.get_rect(top=MARGIN_TOP, centerx=center_x)
        screen.blit(label_surface, label_rect)

        if value is not None:
            value_surface = font.render(str(value), True, WHITE)
            screen.blit(value_surface, value_surface.get_rect(top=label_rect.bottom + 4, centerx=center_x))
        else:
            small_font = pygame.font.Font(None, 20)
            draw_neon_button(screen, center_x - 50, (label_rect.bottom + 4),"Open Config", small_font, width=125, height=30)
            scene.rects["config_button"] = draw_neon_button(screen, center_x - 50, (label_rect.bottom + 4),"Open Config", small_font, width=125, height=30)

    return MARGIN_TOP + font.get_linesize() + font.get_linesize() + 4

def draw_maze(screen, scene) -> int:

    ox = (screen.get_width() - scene.maze.width * scene.cell_size) // 2    # centered
    oy = scene.maze_start_point

    for row_index, row in enumerate(scene.maze.cells):
        for col_index, cell in enumerate(row):
            left = ox + col_index * scene.cell_size
            top = oy + row_index * scene.cell_size
            right = left + scene.cell_size
            bottom = top + scene.cell_size

            if cell & NORTH:
                pygame.draw.line(screen, BLUE, (left, top), (right, top), WALL_WIDTH)
            if cell & EAST:
                pygame.draw.line(screen, BLUE, (right, top), (right, bottom), WALL_WIDTH)
            if cell & SOUTH:
                pygame.draw.line(screen, BLUE, (left, bottom), (right, bottom), WALL_WIDTH)
            if cell & WEST:
                pygame.draw.line(screen, BLUE, (left, top), (left, bottom), WALL_WIDTH)
    return oy + scene.maze.height * scene.cell_size

def draw_points(screen, scene) -> None:
    ox = (screen.get_width() - scene.maze.width * scene.cell_size) // 2
    oy = scene.maze_start_point

    for row_index, col_index in scene.pac_points_data:
        point_x = ox + col_index * scene.cell_size + scene.cell_size // 2
        point_y = oy + row_index * scene.cell_size + scene.cell_size // 2

        pygame.draw.circle(
            screen,
            WHITE,
            (point_x, point_y),
            3
        )

    for row_index, col_index in scene.super_points_data:
        point_x = ox + col_index * scene.cell_size + scene.cell_size // 2
        point_y = oy + row_index * scene.cell_size + scene.cell_size // 2

        pygame.draw.circle(
            screen,
            WHITE,
            (point_x, point_y),
            8,
        )

def draw_pacman(screen: pygame.Surface, scene) -> None:

    directions = {
        "right": 0,
        "down": 90,
        "left": 180,
        "up": 270,
    }

    facing = directions[scene.pacman_direction]

    x = (((screen.get_width() - scene.maze.width * scene.cell_size) // 2)
          + scene.pacman_current_cords[1] * scene.cell_size + scene.cell_size // 2)
    y = scene.maze_start_point + scene.pacman_current_cords[0] * scene.cell_size + scene.cell_size // 2

    points = [(x, y)]

    start = facing + scene.mouth_angle
    end = facing + 360 - scene.mouth_angle

    for angle in range(int(start), int(end) + 1, 3):
        rad = math.radians(angle)

        px = x + (scene.cell_size // 2 - 6) * math.cos(rad)
        py = y + (scene.cell_size // 2 - 6) * math.sin(rad)

        points.append((px, py))

    pygame.draw.polygon(screen, (255, 255, 0), points)

def draw_ghost(screen: pygame.Surface, scene, position: tuple[int, int], color: tuple[int, int, int]) -> None:

    ox = (screen.get_width() - scene.maze.width * scene.cell_size) // 2
    row, col = position
    x = ox + col * scene.cell_size + scene.cell_size // 2
    y = scene.maze_start_point + row * scene.cell_size + scene.cell_size // 2

    radius = MIN_CELL_SIZE // 2

    pygame.draw.circle(
        screen,
        color,
        (x, y),
        radius
    )

    pygame.draw.rect(
        screen,
        color,
        (x - radius, y, MIN_CELL_SIZE, radius)
    )

    points = [
        (x - radius, y + radius),
        (x - radius // 2, y + radius // 2),
        (x, y + radius),
        (x + radius // 2, y + radius // 2),
        (x + radius, y + radius)
    ]

    pygame.draw.polygon(screen, color, points)

    eyeradius = max(2, MIN_CELL_SIZE // 7)

    pygame.draw.circle(
        screen, "white",
        (x - radius // 2, y),
        eyeradius
    )

    pygame.draw.circle(
        screen, "white",
        (x + radius // 2, y),
        eyeradius
    )

    pupilradius = max(1, eyeradius // 2)

    pygame.draw.circle(
        screen, "blue",
        (x - radius // 2 + 2, y),
        pupilradius
    )

    pygame.draw.circle(
        screen, "blue",
        (x + radius // 2 + 2, y),
        pupilradius
    )

def draw_game(screen, scene) -> None:
    y = draw_stats(screen, scene)
    scene.maze_start_point = y + MARGIN_TOP
    scene.cell_size = compute_cell_size(screen, scene)
    draw_maze(screen, scene)
    draw_points(screen, scene)
    draw_pacman(screen, scene)
    for item in scene.ghost:
        draw_ghost(screen, scene, item["position"], item["color"])

    if scene.cheat_state["open_cheat_modal"]:
        scene.game.audio.pause()
        draw_cheat_menu(screen, scene)

    volume_icon = load_icon(asset_path("icons/volume.png"))
    volume_x_icon = load_icon(asset_path("icons/volume-x.png"))

    if volume_icon is not None and volume_x_icon is not None:
        icon = volume_x_icon if scene.audio.muted else volume_icon
        icon_rect = icon.get_rect(
            bottomleft=(15, screen.get_height() - 15)
        )
        screen.blit(icon, icon_rect)
        scene.rects["muted"] = icon_rect

