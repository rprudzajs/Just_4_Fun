"""Interactive travel inspiration globe demo.

This playful prototype uses pygame to render a stylised globe that rotates
between day and night. Tapping a country marker reveals a split day/night
preview card so you can imagine what the destination looks like at different
moments. It is intentionally lightweight so it can serve as a concept sketch
for a mobile travel experience.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Dict, List, Tuple

import pygame

# Screen layout constants
WIDTH, HEIGHT = 960, 600
GLOBE_CENTER = (360, 320)
GLOBE_RADIUS = 220
PANEL_RECT = pygame.Rect(640, 40, 280, 520)
DAY_COLOR = (80, 180, 255)
NIGHT_COLOR = (20, 30, 80)
TEXT_COLOR = (240, 240, 240)
BACKGROUND_COLOR = (10, 15, 35)
HORIZON_COLOR = (0, 90, 140)
MOON_COLOR = (235, 235, 210)

pygame.init()
pygame.display.set_caption("WanderWorld Concept")
FONT = pygame.font.SysFont("Poppins", 24)
SMALL_FONT = pygame.font.SysFont("Poppins", 18)
TINY_FONT = pygame.font.SysFont("Poppins", 14)


@dataclass
class Destination:
    name: str
    summary: str
    position: Tuple[int, int]
    palette: Tuple[Tuple[int, int, int], Tuple[int, int, int]]

    def marker_rect(self) -> pygame.Rect:
        """Return a rect centred on the marker position for hit-testing."""
        size = 16
        x, y = self.position
        return pygame.Rect(x - size // 2, y - size // 2, size, size)


DESTINATIONS: Dict[str, Destination] = {
    "Tokyo": Destination(
        name="Tokyo, Japan",
        summary="Neon nights, dawn markets, and moonlit cityscapes.",
        position=(GLOBE_CENTER[0] + 110, GLOBE_CENTER[1] - 40),
        palette=((255, 200, 90), (140, 40, 160)),
    ),
    "Reykjavik": Destination(
        name="Reykjavík, Iceland",
        summary="Aurora skies fade into soft summer daylight.",
        position=(GLOBE_CENTER[0] - 120, GLOBE_CENTER[1] - 60),
        palette=((150, 210, 255), (60, 100, 160)),
    ),
    "CapeTown": Destination(
        name="Cape Town, South Africa",
        summary="Sunrise surf meets lantern-lit evenings.",
        position=(GLOBE_CENTER[0] + 30, GLOBE_CENTER[1] + 130),
        palette=((255, 170, 120), (20, 50, 90)),
    ),
    "Cusco": Destination(
        name="Cusco, Peru",
        summary="Golden temples shimmer under cosmic skies.",
        position=(GLOBE_CENTER[0] - 160, GLOBE_CENTER[1] + 30),
        palette=((255, 210, 130), (80, 40, 120)),
    ),
}


def draw_background(surface: pygame.Surface, cycle_angle: float) -> None:
    surface.fill(BACKGROUND_COLOR)

    # Subtle gradient horizon behind the globe
    gradient = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    for y in range(HEIGHT):
        ratio = y / HEIGHT
        color = (
            int(HORIZON_COLOR[0] * (1 - ratio) + BACKGROUND_COLOR[0] * ratio),
            int(HORIZON_COLOR[1] * (1 - ratio) + BACKGROUND_COLOR[1] * ratio),
            int(HORIZON_COLOR[2] * (1 - ratio) + BACKGROUND_COLOR[2] * ratio),
            120,
        )
        pygame.draw.line(gradient, color, (0, y), (WIDTH, y))
    surface.blit(gradient, (0, 0))

    # Draw a moon that arcs across the sky
    moon_x = int(150 + math.cos(cycle_angle / 2) * 120)
    moon_y = int(140 + math.sin(cycle_angle / 2) * 40)
    pygame.draw.circle(surface, MOON_COLOR, (moon_x, moon_y), 32)


def draw_globe(surface: pygame.Surface, cycle_angle: float, selected: Destination | None) -> None:
    globe_surface = pygame.Surface((GLOBE_RADIUS * 2, GLOBE_RADIUS * 2), pygame.SRCALPHA)

    # Base ocean colour
    pygame.draw.circle(globe_surface, (25, 90, 160), (GLOBE_RADIUS, GLOBE_RADIUS), GLOBE_RADIUS)

    # Simplified continents using ellipses for a whimsical look
    continents: List[Tuple[Tuple[int, int, int], pygame.Rect]] = [
        ((50, 170, 90), pygame.Rect(110, 80, 150, 110)),  # Eurasia
        ((50, 140, 80), pygame.Rect(60, 210, 120, 140)),  # Africa
        ((60, 160, 80), pygame.Rect(10, 140, 120, 90)),   # Americas
        ((80, 190, 100), pygame.Rect(200, 200, 100, 60)),  # Australia
    ]
    for color, rect in continents:
        pygame.draw.ellipse(globe_surface, color, rect)

    # Day/night terminator overlay rotates with the cycle angle
    overlay = pygame.Surface((GLOBE_RADIUS * 2, GLOBE_RADIUS * 2), pygame.SRCALPHA)
    for x in range(GLOBE_RADIUS * 2):
        for y in range(GLOBE_RADIUS * 2):
            dx = x - GLOBE_RADIUS
            dy = y - GLOBE_RADIUS
            if dx * dx + dy * dy <= GLOBE_RADIUS * GLOBE_RADIUS:
                angle = math.atan2(dy, dx) + math.pi
                shade = (math.cos(angle - cycle_angle) + 1) / 2
                color = (
                    int(DAY_COLOR[0] * shade + NIGHT_COLOR[0] * (1 - shade)),
                    int(DAY_COLOR[1] * shade + NIGHT_COLOR[1] * (1 - shade)),
                    int(DAY_COLOR[2] * shade + NIGHT_COLOR[2] * (1 - shade)),
                    140,
                )
                overlay.set_at((x, y), color)
    globe_surface.blit(overlay, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)

    surface.blit(globe_surface, (GLOBE_CENTER[0] - GLOBE_RADIUS, GLOBE_CENTER[1] - GLOBE_RADIUS))

    # Draw destination markers
    for destination in DESTINATIONS.values():
        color = (255, 240, 200) if destination is selected else (255, 130, 80)
        pygame.draw.circle(surface, color, destination.position, 8)
        pygame.draw.circle(surface, (0, 0, 0), destination.position, 8, 2)


def draw_panel(surface: pygame.Surface, selected: Destination | None) -> None:
    pygame.draw.rect(surface, (25, 35, 60), PANEL_RECT, border_radius=18)
    pygame.draw.rect(surface, (70, 90, 140), PANEL_RECT, width=3, border_radius=18)

    header = FONT.render("Dream Destination", True, TEXT_COLOR)
    surface.blit(header, (PANEL_RECT.x + 24, PANEL_RECT.y + 20))

    if selected is None:
        hint_lines = [
            "Tap a marker to split", "day & night views",
            "and imagine your", "next journey!",
        ]
        for i, line in enumerate(hint_lines):
            text = SMALL_FONT.render(line, True, TEXT_COLOR)
            surface.blit(text, (PANEL_RECT.x + 32, PANEL_RECT.y + 100 + i * 28))
        return

    name_text = SMALL_FONT.render(selected.name, True, TEXT_COLOR)
    surface.blit(name_text, (PANEL_RECT.x + 24, PANEL_RECT.y + 80))

    summary_lines = wrap_text(selected.summary, SMALL_FONT, PANEL_RECT.width - 48)
    for i, line in enumerate(summary_lines):
        text = TINY_FONT.render(line, True, TEXT_COLOR)
        surface.blit(text, (PANEL_RECT.x + 24, PANEL_RECT.y + 120 + i * 20))

    preview_rect = pygame.Rect(PANEL_RECT.x + 40, PANEL_RECT.y + 240, 200, 200)
    draw_day_night_preview(surface, preview_rect, selected.palette)


def draw_day_night_preview(surface: pygame.Surface, rect: pygame.Rect, palette: Tuple[Tuple[int, int, int], Tuple[int, int, int]]) -> None:
    day_color, night_color = palette
    pygame.draw.rect(surface, day_color, rect)
    pygame.draw.rect(surface, night_color, rect.inflate(-rect.width // 2, 0))
    pygame.draw.line(surface, TEXT_COLOR, rect.midtop, rect.midbottom, 3)

    sun_pos = (rect.x + rect.width // 4, rect.centery)
    moon_pos = (rect.right - rect.width // 4, rect.centery)
    pygame.draw.circle(surface, (255, 245, 180), sun_pos, 18)
    pygame.draw.circle(surface, (210, 210, 255), moon_pos, 18)

    caption = TINY_FONT.render("Day / Night Moodboard", True, TEXT_COLOR)
    caption_pos = (rect.centerx - caption.get_width() // 2, rect.bottom + 16)
    surface.blit(caption, caption_pos)


def wrap_text(text: str, font: pygame.font.Font, width: int) -> List[str]:
    words = text.split()
    lines: List[str] = []
    current = ""
    for word in words:
        test_line = f"{current} {word}".strip()
        if font.size(test_line)[0] <= width:
            current = test_line
        else:
            lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


def detect_hover(mouse_pos: Tuple[int, int]) -> Destination | None:
    for destination in DESTINATIONS.values():
        if destination.marker_rect().collidepoint(mouse_pos):
            return destination
    return None


def run() -> None:
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    clock = pygame.time.Clock()

    cycle_angle = 0.0
    selected: Destination | None = None

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                hovered = detect_hover(event.pos)
                if hovered:
                    selected = hovered

        cycle_angle = (cycle_angle + 0.01) % (math.tau)

        draw_background(screen, cycle_angle)
        draw_globe(screen, cycle_angle, selected)
        draw_panel(screen, selected)

        hover = detect_hover(pygame.mouse.get_pos())
        if hover and hover is not selected:
            name = TINY_FONT.render(hover.name, True, TEXT_COLOR)
            screen.blit(name, (hover.position[0] - name.get_width() // 2, hover.position[1] - 30))

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()


if __name__ == "__main__":
    run()
