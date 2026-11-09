import pygame
from display.utils import load_icon
from paths import asset_path


def draw_cheat_menu(screen, scene):
    cheat_icons = {
        "invincible": asset_path("icons/shield-ban.png"),
        "freeze_ghosts": asset_path("icons/snowflake.png"),
        "double_speed": asset_path("icons/gauge.png"),
        "extra_life": asset_path("icons/heart.png"),
        "extra_time": asset_path("icons/clock-plus.png"),
        "skip_level": asset_path("icons/square-chevrons-right.png"),
        "close": asset_path("icons/square-letter-x.png"),
    }

    width, height = screen.get_size()
    overlay = pygame.Surface((width, height), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 170))
    screen.blit(overlay, (0, 0))

    menu = pygame.Rect(0, 0, 650, 420)
    menu.center = (width // 2, height // 2)

    pygame.draw.rect(
        screen, (10, 18, 40), menu, border_radius=14
    )
    pygame.draw.rect(
        screen, (0, 200, 255), menu,
        width=3, border_radius=14
    )

    font = pygame.font.Font(None, 34)
    small_font = pygame.font.Font(None, 26)
    title = font.render("CHEAT MODE", True, (255, 255, 0))

    title_rect = title.get_rect(
        centerx=menu.centerx,
        y=menu.y + 25
    )
    screen.blit(title, title_rect)

    close_icon = load_icon(cheat_icons["close"])

    if close_icon is not None:
        close_icon_rect = close_icon.get_rect(
            topright = (menu.right - 15, menu.top + 15)
        )
        screen.blit(close_icon, close_icon_rect)
        scene.rects["close"] = close_icon_rect

    options = [
        ("1", "Invincibility", "invincible", "toggle"),
        ("2", "Freeze Ghosts", "freeze_ghosts", "toggle"),
        ("3", "Double Speed", "double_speed", "toggle"),
        ("4", "Add Extra Life", "extra_life", "action", "+1 Life"),
        ("5", "Add Extra Time", "extra_time", "action", "+60s"),
        ("6", "Skip Level", "skip_level", "action", "Skip"),
    ]

    for index, option in enumerate(options):
        key, name, identifier, kind, *extra = option
        y = menu.y + 90 + index * 52
        icon = load_icon(cheat_icons[identifier])

        if icon is not None:
            icon_rect = icon.get_rect(
                midleft=(menu.x + 45, y + 20)
            )
            screen.blit(icon, icon_rect)

        # Left-side label
        label = small_font.render(
            f" {name}",
            True,
            (255, 255, 255)
        )
        screen.blit(label, (menu.x + 90, y + 10))

        if kind == "toggle":
            state = scene.cheat_state[identifier]
            rect = draw_toggle(
                screen,
                menu.right - 110,
                y + 5,
                state
            )
            scene.rects[identifier] = rect
        elif kind == "action":
            button_text = extra[0]
            rect = draw_neon_button(
                screen,
                menu.right - 155,
                y,
                button_text,
                small_font,
                width=125,
                height=40
            )
            scene.rects[identifier] = rect


def draw_neon_button(screen, x, y, text, font, width=125, height=44):
    rect = pygame.Rect(x, y, width, height)

    pygame.draw.rect(
        screen,
        (5, 20, 40),
        rect,
        border_radius=12
    )

    glow = pygame.Surface(
        (width + 24, height + 24),
        pygame.SRCALPHA
    )

    for i in range(8, 0, -1):
        glow_rect = pygame.Rect(
            12 - i,
            12 - i,
            width + i * 2,
            height + i * 2
        )

        pygame.draw.rect(
            glow,
            (0, 200, 255, 7),
            glow_rect,
            width=2,
            border_radius=12 + i
        )

    screen.blit(glow, (x - 12, y - 12))

    pygame.draw.rect(
        screen,
        (0, 210, 255),
        rect,
        width=2,
        border_radius=12
    )

    text_surface = font.render(
        text,
        True,
        (50, 225, 255)
    )

    text_rect = text_surface.get_rect(
        center=rect.center
    )

    screen.blit(text_surface, text_rect)

    return rect

def draw_toggle(
    screen: pygame.Surface,
    x: int,
    y: int,
    enabled: bool,
) -> pygame.Rect:

    width = 60
    height = 30

    rect = pygame.Rect(x, y, width, height)

    # Background color
    color = (
        (34, 197, 94) if enabled
        else (100, 100, 100)
    )

    pygame.draw.rect(
        screen,
        color,
        rect,
        border_radius=height // 2
    )

    radius = 12

    circle_x = (
        rect.right - radius - 3
        if enabled
        else rect.left + radius + 3
    )

    circle_y = rect.centery

    pygame.draw.circle(
        screen,
        (255, 255, 255),
        (circle_x, circle_y),
        radius
    )

    return rect
