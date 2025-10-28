"""Cinematic travel globe concept rendered with pygame."""
from __future__ import annotations

import math
import random
from dataclasses import dataclass
from typing import Dict, List, Tuple

import numpy as np
import pygame


# ---------------------------------------------------------------------------
# Global configuration and colours
# ---------------------------------------------------------------------------
WIDTH, HEIGHT = 1280, 760
GLOBE_CENTER = (500, 400)
GLOBE_RADIUS = 260
FPS = 60

BG_TOP = (10, 18, 36)
BG_BOTTOM = (3, 6, 18)

HALO_COLOR = (120, 180, 255)
INNER_OCEAN = (82, 162, 220)
OUTER_OCEAN = (8, 24, 58)

CLOUD_COLOR = (255, 255, 255, 42)
NIGHT_TINT = (8, 12, 32, 120)
SPECULAR_COLOR = (210, 230, 255, 120)

CARD_FILL = (255, 255, 255, 38)
CARD_BORDER = (255, 255, 255, 90)
SHADOW_COLOR = (0, 0, 0, 80)


pygame.init()
pygame.display.set_caption("Wanderlust Luxe Globe")
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()

pygame.font.init()
TITLE_FONT = pygame.font.SysFont("Poppins", 44)
LABEL_FONT = pygame.font.SysFont("Poppins", 22)
SMALL_FONT = pygame.font.SysFont("Poppins", 18)
MONO_FONT = pygame.font.SysFont("Poppins", 16)
SERIF_FONT = pygame.font.SysFont("Playfair Display", 56)


# ---------------------------------------------------------------------------
# Data structures
# ---------------------------------------------------------------------------
@dataclass
class Marker:
    name: str
    description: str
    latitude: float
    longitude: float
    palette: Tuple[int, int, int]


MARKERS: List[Marker] = [
    Marker(
        "Hyderabad",
        "Regal dawn skylines meeting cutting-edge waterfront nights.",
        17.3850,
        78.4867,
        (255, 210, 150),
    ),
    Marker(
        "Reykjavík",
        "Aurora-kissed glaciers and geothermal midnight dips.",
        64.1466,
        -21.9426,
        (170, 220, 255),
    ),
    Marker(
        "Cape Town",
        "Sunrise ridgelines sliding into candlelit vineyard feasts.",
        -33.9249,
        18.4241,
        (255, 190, 140),
    ),
]


# ---------------------------------------------------------------------------
# Utility functions for surface generation
# ---------------------------------------------------------------------------
def create_vertical_gradient(size: Tuple[int, int], top: Tuple[int, int, int], bottom: Tuple[int, int, int]) -> pygame.Surface:
    width, height = size
    array = np.zeros((height, width, 3), dtype=np.uint8)
    for y in range(height):
        t = y / max(height - 1, 1)
        color = [int(top[i] * (1 - t) + bottom[i] * t) for i in range(3)]
        array[y, :, :] = color
    surface = pygame.Surface(size)
    pygame.surfarray.blit_array(surface, array.transpose((1, 0, 2)))
    return surface.convert()


def create_radial_gradient(diameter: int, inner: Tuple[int, int, int], outer: Tuple[int, int, int]) -> pygame.Surface:
    radius = diameter / 2
    y_indices, x_indices = np.indices((diameter, diameter))
    dx = x_indices - radius + 0.5
    dy = y_indices - radius + 0.5
    distance = np.sqrt(dx * dx + dy * dy)
    norm = np.clip(distance / radius, 0, 1)

    gradient = np.zeros((diameter, diameter, 4), dtype=np.uint8)
    for i in range(3):
        gradient[:, :, i] = (inner[i] * (1 - norm) + outer[i] * norm).astype(np.uint8)
    alpha = (1 - np.clip(norm, 0, 1)) * 255
    gradient[:, :, 3] = np.clip(alpha, 0, 255)

    surface = pygame.Surface((diameter, diameter), pygame.SRCALPHA)
    pygame.surfarray.blit_array(surface, gradient.transpose((1, 0, 2)))
    return surface.convert_alpha()


def create_halo(radius: int) -> pygame.Surface:
    diameter = radius * 2
    halo = pygame.Surface((diameter, diameter), pygame.SRCALPHA)
    y_indices, x_indices = np.indices((diameter, diameter))
    dx = x_indices - radius + 0.5
    dy = y_indices - radius + 0.5
    distance = np.sqrt(dx * dx + dy * dy)
    norm = np.clip(distance / radius, 0, 1)
    alpha = (1 - norm) ** 2 * 220
    halo_array = np.zeros((diameter, diameter, 4), dtype=np.uint8)
    halo_array[:, :, 0] = HALO_COLOR[0]
    halo_array[:, :, 1] = HALO_COLOR[1]
    halo_array[:, :, 2] = HALO_COLOR[2]
    halo_array[:, :, 3] = np.clip(alpha, 0, 255).astype(np.uint8)
    pygame.surfarray.blit_array(halo, halo_array.transpose((1, 0, 2)))
    return halo.convert_alpha()


def create_horizontal_mask(width: int, height: int, left_color: Tuple[int, int, int, int], right_color: Tuple[int, int, int, int]) -> pygame.Surface:
    mask = pygame.Surface((width, height), pygame.SRCALPHA)
    gradient = np.zeros((height, width, 4), dtype=np.uint8)
    for x in range(width):
        t = x / max(width - 1, 1)
        for i in range(4):
            gradient[:, x, i] = int(left_color[i] * (1 - t) + right_color[i] * t)
    pygame.surfarray.blit_array(mask, gradient.transpose((1, 0, 2)))
    return mask.convert_alpha()


def create_cloud_texture(width: int, height: int) -> pygame.Surface:
    texture = pygame.Surface((width, height), pygame.SRCALPHA)
    for _ in range(90):
        radius = random.randint(40, 120)
        x = random.randint(-radius, width + radius)
        y = random.randint(-radius, height + radius)
        circle = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
        pygame.draw.circle(circle, (255, 255, 255, random.randint(18, 40)), (radius, radius), radius)
        circle = pygame.transform.smoothscale(circle, (radius * 2, radius * 2))
        texture.blit(circle, (x - radius, y - radius), special_flags=pygame.BLEND_RGBA_ADD)
    return texture.convert_alpha()


def create_land_texture(width: int, height: int) -> pygame.Surface:
    texture = pygame.Surface((width, height), pygame.SRCALPHA)
    y_indices, x_indices = np.indices((height, width))
    lon = (x_indices / width) * math.tau
    lat = (y_indices / height) * math.pi - math.pi / 2
    pattern = (
        0.6 * np.sin(2 * lon) * np.cos(lat * 1.2)
        + 0.3 * np.sin(3.5 * lon + 0.5)
        + 0.2 * np.cos(1.5 * lon - 1.0) * np.cos(lat * 0.8)
    )
    pattern = (pattern - pattern.min()) / (pattern.max() - pattern.min())
    intensity = (pattern ** 1.4) * 120
    land = np.zeros((height, width, 4), dtype=np.uint8)
    land[:, :, 0] = (190 + intensity / 3).astype(np.uint8)
    land[:, :, 1] = (210 + intensity / 2).astype(np.uint8)
    land[:, :, 2] = (170 + intensity / 4).astype(np.uint8)
    land[:, :, 3] = (70 + intensity).astype(np.uint8)
    pygame.surfarray.blit_array(texture, land.transpose((1, 0, 2)))
    return texture.convert_alpha()


def create_particles(count: int) -> List[Dict[str, float]]:
    particles: List[Dict[str, float]] = []
    for _ in range(count):
        particles.append(
            {
                "x": random.uniform(0, WIDTH),
                "y": random.uniform(0, HEIGHT),
                "speed": random.uniform(6, 18),
                "radius": random.uniform(1.2, 2.6),
                "alpha": random.randint(120, 220),
            }
        )
    return particles


# ---------------------------------------------------------------------------
# Pre-rendered assets
# ---------------------------------------------------------------------------
background = create_vertical_gradient((WIDTH, HEIGHT), BG_TOP, BG_BOTTOM)
base_globe = create_radial_gradient(GLOBE_RADIUS * 2, INNER_OCEAN, OUTER_OCEAN)
halo_surface = create_halo(int(GLOBE_RADIUS * 1.32))
night_gradient = create_horizontal_mask(GLOBE_RADIUS * 4, GLOBE_RADIUS * 2, (0, 0, 0, 0), NIGHT_TINT)
specular_band = create_horizontal_mask(GLOBE_RADIUS * 4, GLOBE_RADIUS * 2, (0, 0, 0, 0), SPECULAR_COLOR)
cloud_texture = create_cloud_texture(GLOBE_RADIUS * 4, GLOBE_RADIUS * 2)
land_texture = create_land_texture(GLOBE_RADIUS * 4, GLOBE_RADIUS * 2)

globe_mask = pygame.Surface((GLOBE_RADIUS * 2, GLOBE_RADIUS * 2), pygame.SRCALPHA)
pygame.draw.circle(globe_mask, (255, 255, 255, 255), (GLOBE_RADIUS, GLOBE_RADIUS), GLOBE_RADIUS)

globe_mask = globe_mask.convert_alpha()
particles = create_particles(80)
particle_layer = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA).convert_alpha()


# ---------------------------------------------------------------------------
# State variables
# ---------------------------------------------------------------------------
rotation_angle = 0.0
rotation_velocity = 0.0
cloud_scroll = 0.0

marker_hitboxes: Dict[str, pygame.Rect] = {}
selected_marker = MARKERS[0].name
day_mode = True

dragging = False
day_button_rect = pygame.Rect(0, 0, 0, 0)
night_button_rect = pygame.Rect(0, 0, 0, 0)


# ---------------------------------------------------------------------------
# Core rendering helpers
# ---------------------------------------------------------------------------
def project_markers() -> List[Tuple[Marker, Tuple[int, int], float]]:
    projected: List[Tuple[Marker, Tuple[int, int], float]] = []
    for marker in MARKERS:
        lat_rad = math.radians(marker.latitude)
        lon_rad = math.radians(marker.longitude) + rotation_angle
        x = math.cos(lat_rad) * math.sin(lon_rad)
        y = math.sin(lat_rad)
        z = math.cos(lat_rad) * math.cos(lon_rad)
        if z <= 0:
            continue
        screen_x = int(GLOBE_CENTER[0] + x * GLOBE_RADIUS * 0.9)
        screen_y = int(GLOBE_CENTER[1] - y * GLOBE_RADIUS * 0.9)
        projected.append((marker, (screen_x, screen_y), z))
    projected.sort(key=lambda item: item[2])
    return projected


def draw_particles(surface: pygame.Surface, delta: float) -> None:
    for particle in particles:
        particle["y"] += particle["speed"] * delta * 0.4
        if particle["y"] > HEIGHT:
            particle["y"] = -10
            particle["x"] = random.uniform(0, WIDTH)
    particle_layer.fill((0, 0, 0, 0))
    for particle in particles:
        pygame.draw.circle(
            particle_layer,
            (255, 255, 255, particle["alpha"]),
            (int(particle["x"]), int(particle["y"])),
            int(particle["radius"]),
        )
    surface.blit(particle_layer, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)


def draw_globe(surface: pygame.Surface) -> None:
    diameter = GLOBE_RADIUS * 2
    globe_surface = base_globe.copy()

    shift = int((rotation_angle % math.tau) / math.tau * land_texture.get_width())
    for offset in (-land_texture.get_width(), 0):
        globe_surface.blit(land_texture, (offset - shift, 0), special_flags=pygame.BLEND_RGBA_ADD)

    cloud_surface = pygame.Surface((diameter, diameter), pygame.SRCALPHA)
    cloud_width = cloud_texture.get_width()
    cloud_shift = int(((cloud_scroll - (rotation_angle / math.tau)) % 1.0) * cloud_width)
    for offset in (-cloud_width, 0):
        cloud_surface.blit(cloud_texture, (offset - cloud_shift, 0), special_flags=pygame.BLEND_RGBA_ADD)
    globe_surface.blit(cloud_surface, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)

    night_offset = int(((math.sin(rotation_angle) * 0.5) + 0.5) * diameter)
    globe_surface.blit(night_gradient, (night_offset - diameter * 2, 0))

    specular_offset = int(((math.cos(rotation_angle) * 0.5) + 0.5) * diameter)
    globe_surface.blit(specular_band, (specular_offset - diameter * 2, 0), special_flags=pygame.BLEND_RGBA_ADD)

    globe_surface.blit(globe_mask, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)

    halo_pos = (GLOBE_CENTER[0] - halo_surface.get_width() // 2, GLOBE_CENTER[1] - halo_surface.get_height() // 2)
    surface.blit(halo_surface, halo_pos, special_flags=pygame.BLEND_RGBA_ADD)

    globe_pos = (GLOBE_CENTER[0] - GLOBE_RADIUS, GLOBE_CENTER[1] - GLOBE_RADIUS)
    surface.blit(globe_surface, globe_pos)


def draw_markers(surface: pygame.Surface) -> None:
    marker_hitboxes.clear()
    projected = project_markers()
    for marker, (x, y), depth in projected:
        aura_radius = int(14 + depth * 16)
        aura_surface = pygame.Surface((aura_radius * 4, aura_radius * 4), pygame.SRCALPHA)
        pygame.draw.circle(
            aura_surface,
            (marker.palette[0], marker.palette[1], marker.palette[2], 28),
            (aura_radius * 2, aura_radius * 2),
            aura_radius * 2,
        )
        pygame.draw.circle(
            aura_surface,
            (255, 255, 255, 220),
            (aura_radius * 2, aura_radius * 2),
            max(4, aura_radius // 2),
        )
        aura_surface = pygame.transform.smoothscale(aura_surface, (aura_radius * 2, aura_radius * 2))
        surface.blit(
            aura_surface,
            (x - aura_surface.get_width() // 2, y - aura_surface.get_height() // 2),
            special_flags=pygame.BLEND_RGBA_ADD,
        )
        rect = pygame.Rect(
            x - aura_surface.get_width() // 2,
            y - aura_surface.get_height() // 2,
            aura_surface.get_width(),
            aura_surface.get_height(),
        )
        marker_hitboxes[marker.name] = rect


def draw_button(surface: pygame.Surface, rect: pygame.Rect, text: str, active: bool) -> None:
    button_surface = pygame.Surface(rect.size, pygame.SRCALPHA)
    alpha = 90 if active else 45
    button_surface.fill((255, 255, 255, alpha))
    pygame.draw.rect(button_surface, (255, 255, 255, 160 if active else 100), button_surface.get_rect(), border_radius=18, width=1)
    button_surface = pygame.transform.smoothscale(button_surface, rect.size)
    surface.blit(button_surface, rect.topleft)
    label = LABEL_FONT.render(text, True, (255, 255, 255))
    surface.blit(label, (rect.x + (rect.width - label.get_width()) // 2, rect.y + (rect.height - label.get_height()) // 2))


def draw_ui(surface: pygame.Surface) -> None:
    nav_rect = pygame.Rect(70, 36, WIDTH - 140, 70)
    nav_surface = pygame.Surface(nav_rect.size, pygame.SRCALPHA)
    pygame.draw.rect(nav_surface, SHADOW_COLOR, nav_surface.get_rect(), border_radius=28)
    glass = pygame.Surface(nav_rect.size, pygame.SRCALPHA)
    glass.fill(CARD_FILL)
    pygame.draw.rect(glass, (255, 255, 255, 80), glass.get_rect(), width=1, border_radius=28)
    nav_surface.blit(glass, (0, 0))
    nav_surface = pygame.transform.smoothscale(nav_surface, nav_rect.size)
    surface.blit(nav_surface, nav_rect.topleft)

    title = TITLE_FONT.render("Wanderworld Studio", True, (255, 255, 255))
    surface.blit(title, (nav_rect.x + 40, nav_rect.y + 18))

    hero_text = SERIF_FONT.render("Dream in Motion", True, (255, 255, 255))
    surface.blit(hero_text, (70, 140))
    sub_text = LABEL_FONT.render("Curated journeys for daydreamers and night seekers.", True, (200, 212, 232))
    surface.blit(sub_text, (70, 210))

    panel_rect = pygame.Rect(WIDTH - 360, 160, 300, 420)
    panel_surface = pygame.Surface(panel_rect.size, pygame.SRCALPHA)
    pygame.draw.rect(panel_surface, SHADOW_COLOR, panel_surface.get_rect(), border_radius=26)
    blur_panel = pygame.Surface(panel_rect.size, pygame.SRCALPHA)
    fill_alpha = 64 if day_mode else 92
    blur_panel.fill((255, 255, 255, fill_alpha))
    pygame.draw.rect(blur_panel, CARD_BORDER, blur_panel.get_rect(), width=1, border_radius=26)
    panel_surface.blit(blur_panel, (0, 0))
    panel_surface = pygame.transform.smoothscale(panel_surface, panel_rect.size)
    surface.blit(panel_surface, panel_rect.topleft)

    header = LABEL_FONT.render("Featured Journey", True, (235, 240, 250))
    surface.blit(header, (panel_rect.x + 28, panel_rect.y + 26))

    marker = next(m for m in MARKERS if m.name == selected_marker)
    city_title = TITLE_FONT.render(marker.name, True, marker.palette)
    surface.blit(city_title, (panel_rect.x + 28, panel_rect.y + 80))

    def render_paragraph(text: str, start_y: int) -> int:
        words = text.split()
        lines: List[str] = []
        line = ""
        for word in words:
            test = (line + " " + word).strip()
            if SMALL_FONT.size(test)[0] > panel_rect.width - 60:
                lines.append(line)
                line = word
            else:
                line = test
        if line:
            lines.append(line)
        y = start_y
        for line_text in lines:
            label = SMALL_FONT.render(line_text, True, (220, 230, 240))
            surface.blit(label, (panel_rect.x + 28, y))
            y += 26
        return y

    paragraph_bottom = render_paragraph(marker.description, panel_rect.y + 150)

    journey_stats = [
        ("Daybreak", "Sunrise panoramas"),
        ("Afterglow", "Skyline cocktails"),
    ]
    for i, (heading, copy) in enumerate(journey_stats):
        heading_surface = SMALL_FONT.render(heading, True, (255, 255, 255))
        copy_surface = MONO_FONT.render(copy, True, (200, 210, 224))
        surface.blit(heading_surface, (panel_rect.x + 28, paragraph_bottom + 14 + i * 48))
        surface.blit(copy_surface, (panel_rect.x + 28, paragraph_bottom + 40 + i * 48))

    global day_button_rect, night_button_rect
    day_button_rect = pygame.Rect(panel_rect.x + 28, panel_rect.bottom - 80, 110, 46)
    night_button_rect = pygame.Rect(panel_rect.x + 156, panel_rect.bottom - 80, 110, 46)
    draw_button(surface, day_button_rect, "Day", day_mode)
    draw_button(surface, night_button_rect, "Night", not day_mode)


# ---------------------------------------------------------------------------
# Input and update handling
# ---------------------------------------------------------------------------
def handle_input() -> bool:
    global dragging, rotation_velocity, selected_marker, day_mode, rotation_angle
    global day_button_rect, night_button_rect
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            return False
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            return False
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if day_button_rect.collidepoint(event.pos):
                day_mode = True
                continue
            if night_button_rect.collidepoint(event.pos):
                day_mode = False
                continue
            for name, rect in marker_hitboxes.items():
                if rect.collidepoint(event.pos):
                    selected_marker = name
                    break
            else:
                dragging = True
                rotation_velocity = 0.0
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            dragging = False
        elif event.type == pygame.MOUSEMOTION and dragging:
            dx = event.rel[0]
            rotation_angle_delta = dx * 0.004
            globals()["rotation_angle"] += rotation_angle_delta
            rotation_velocity = dx * 0.0025
    return True


def update_state(delta: float) -> None:
    global rotation_angle, rotation_velocity, cloud_scroll
    rotation_angle += rotation_velocity * delta * FPS
    rotation_angle %= math.tau
    rotation_velocity *= 0.92 ** (delta * FPS)
    cloud_scroll = (cloud_scroll + delta * 0.08) % 1.0


# ---------------------------------------------------------------------------
# Main application loop
# ---------------------------------------------------------------------------
def main() -> None:
    running = True
    while running:
        delta = clock.tick(FPS) / 1000.0
        running = handle_input()
        update_state(delta)

        frame = background.copy()
        draw_particles(frame, delta)
        draw_globe(frame)
        draw_markers(frame)
        draw_ui(frame)

        screen.blit(frame, (0, 0))
        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()
