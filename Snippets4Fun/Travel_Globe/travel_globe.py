"""Luxurious travel inspiration globe with cinematic rendering.

This concept demo uses pygame to render a glossy, animated world sphere with
layered lighting, drifting clouds, and interactive destination hotspots. The
visual approach leans into premium travel brand vibes: glowing atmosphere,
city-light sparkle on the night side, and day/night split previews for each
featured destination.
"""

from __future__ import annotations

import math
import random
from dataclasses import dataclass
from typing import Dict, List, Tuple

import numpy as np
import pygame

# ---------------------------------------------------------------------------
# Screen & layout constants
# ---------------------------------------------------------------------------
WIDTH, HEIGHT = 1200, 720
GLOBE_CENTER = (460, 360)
GLOBE_RADIUS = 260
PANEL_RECT = pygame.Rect(750, 60, 380, 600)
BACKGROUND_TOP = (6, 12, 30)
BACKGROUND_BOTTOM = (10, 20, 45)
PRIMARY_TEXT = (245, 248, 255)
SECONDARY_TEXT = (180, 190, 210)
ACCENT_COLOR = (135, 190, 255)

MAP_WIDTH, MAP_HEIGHT = 1024, 512

pygame.init()
pygame.display.set_caption("WanderWorld Luxe Concept")
pygame.font.init()
TITLE_FONT = pygame.font.SysFont("Poppins", 42)
LABEL_FONT = pygame.font.SysFont("Poppins", 24)
SMALL_FONT = pygame.font.SysFont("Poppins", 18)
TINY_FONT = pygame.font.SysFont("Poppins", 14)


# ---------------------------------------------------------------------------
# Helper data structures
# ---------------------------------------------------------------------------
@dataclass
class Destination:
    key: str
    name: str
    summary: str
    latitude: float
    longitude: float
    palette: Tuple[Tuple[int, int, int], Tuple[int, int, int]]
    highlights: Tuple[str, str]

    screen_pos: Tuple[int, int] | None = None
    surface_depth: float = 0.0

    def marker_rect(self) -> pygame.Rect | None:
        if self.screen_pos is None:
            return None
        size = 28 * (0.6 + 0.4 * self.surface_depth)
        x, y = self.screen_pos
        return pygame.Rect(int(x - size / 2), int(y - size / 2), int(size), int(size))


DESTINATIONS: Dict[str, Destination] = {
    "tokyo": Destination(
        key="tokyo",
        name="Tokyo, Japan",
        summary="Neon nights sliding into tranquil dawn shrines and sky-high lounges.",
        latitude=35.6762,
        longitude=139.6503,
        palette=((255, 210, 140), (122, 35, 160)),
        highlights=("48hr cityscapes", "Midnight ramen"),
    ),
    "reykjavik": Destination(
        key="reykjavik",
        name="Reykjavík, Iceland",
        summary="Pastel mornings, shimmering glaciers and aurora-dusted nights.",
        latitude=64.1466,
        longitude=-21.9426,
        palette=((162, 218, 255), (50, 90, 150)),
        highlights=("Sky lagoon", "Aurora suites"),
    ),
    "cape_town": Destination(
        key="cape_town",
        name="Cape Town, South Africa",
        summary="Atlantic breezes, Table Mountain sunrise, and lantern-lit vineyard dinners.",
        latitude=-33.9249,
        longitude=18.4241,
        palette=((255, 182, 120), (18, 44, 94)),
        highlights=("Sunrise hikes", "Evening wine route"),
    ),
    "cusco": Destination(
        key="cusco",
        name="Cusco, Peru",
        summary="High-altitude golden hours that melt into cosmic Andean skies.",
        latitude=-13.5319,
        longitude=-71.9675,
        palette=((255, 205, 150), (88, 52, 130)),
        highlights=("Sacred Valley", "Stargazing domes"),
    ),
    "queenstown": Destination(
        key="queenstown",
        name="Queenstown, New Zealand",
        summary="Glacial lakes, alpine heli-picnics, and bonfire-lit shoreline nights.",
        latitude=-45.0312,
        longitude=168.6626,
        palette=((198, 240, 255), (30, 52, 120)),
        highlights=("Midnight gondola", "Lakeside glamping"),
    ),
}


# ---------------------------------------------------------------------------
# Map construction utilities
# ---------------------------------------------------------------------------
def lonlat_to_mapxy(lon: float, lat: float) -> Tuple[int, int]:
    x = (lon + 180.0) / 360.0 * MAP_WIDTH
    y = (90.0 - lat) / 180.0 * MAP_HEIGHT
    return int(x) % MAP_WIDTH, max(0, min(MAP_HEIGHT - 1, int(y)))


def spherical_to_cartesian(lat: float, lon: float) -> Tuple[float, float, float]:
    cos_lat = math.cos(lat)
    return (
        math.sin(lon) * cos_lat,
        math.sin(lat),
        math.cos(lon) * cos_lat,
    )

# Simplified but aesthetically pleasing polygon outlines for continents.
# Coordinates are (longitude, latitude) pairs sampled to provide a crisp silhouette
# once rasterised to the equirectangular texture.
CONTINENT_POLYGONS: List[Tuple[List[Tuple[float, float]], Tuple[int, int, int]]] = [
    # North America
    (
        [
            (-168, 72), (-140, 70), (-120, 66), (-103, 70), (-95, 73), (-75, 72),
            (-65, 60), (-75, 48), (-95, 43), (-107, 37), (-111, 32), (-117, 28),
            (-124, 24), (-129, 25), (-135, 30), (-140, 35), (-150, 40), (-159, 52),
            (-164, 60), (-168, 66),
        ],
        (120, 188, 126),
    ),
    # South America
    (
        [
            (-82, 12), (-79, 2), (-76, -4), (-74, -10), (-68, -18), (-64, -25),
            (-62, -32), (-60, -40), (-62, -48), (-66, -54), (-70, -56), (-76, -48),
            (-80, -34), (-82, -18), (-84, -4), (-82, 8),
        ],
        (118, 174, 110),
    ),
    # Europe & Asia
    (
        [
            (-10, 72), (5, 68), (20, 66), (38, 70), (60, 76), (85, 72), (102, 66),
            (112, 58), (120, 56), (130, 52), (142, 46), (150, 40), (154, 32),
            (160, 20), (166, 8), (172, 0), (174, -8), (170, -18), (160, -24),
            (148, -30), (134, -34), (120, -36), (110, -32), (102, -20), (95, -10),
            (82, -4), (72, -6), (62, -8), (50, -4), (42, 4), (35, 10), (30, 18),
            (24, 30), (18, 40), (12, 48), (5, 54), (-4, 58), (-12, 64), (-10, 70),
        ],
        (136, 194, 138),
    ),
    # Africa
    (
        [
            (15, 34), (28, 30), (36, 24), (40, 16), (42, 6), (40, -4), (36, -12),
            (34, -20), (30, -28), (24, -32), (20, -36), (18, -42), (15, -48),
            (12, -52), (8, -30), (0, -20), (-6, -10), (-10, 0), (-8, 12), (-4, 20),
            (0, 26), (6, 30), (10, 34),
        ],
        (126, 182, 122),
    ),
    # Australia
    (
        [
            (112, -12), (116, -20), (120, -26), (128, -32), (136, -36), (146, -38),
            (153, -34), (152, -24), (148, -16), (142, -10), (135, -10), (125, -12),
            (118, -16), (112, -12),
        ],
        (152, 198, 152),
    ),
    # Greenland
    (
        [
            (-50, 84), (-42, 80), (-40, 76), (-44, 72), (-50, 70), (-58, 72),
            (-60, 78), (-54, 82), (-50, 84),
        ],
        (150, 208, 150),
    ),
    # Madagascar
    (
        [
            (49, -12), (50, -20), (49, -24), (47, -26), (45, -22), (44, -16),
            (45, -10), (47, -8), (49, -12),
        ],
        (132, 184, 130),
    ),
]


CITY_LIGHTS: List[Tuple[str, float, float, float]] = [
    ("Tokyo", 35.6762, 139.6503, 1.0),
    ("Seoul", 37.5665, 126.9780, 0.8),
    ("Singapore", 1.3521, 103.8198, 0.9),
    ("Sydney", -33.8688, 151.2093, 0.7),
    ("Dubai", 25.2048, 55.2708, 1.0),
    ("Paris", 48.8566, 2.3522, 0.9),
    ("London", 51.5072, -0.1276, 0.9),
    ("New York", 40.7128, -74.0060, 1.0),
    ("Los Angeles", 34.0522, -118.2437, 0.8),
    ("Mexico City", 19.4326, -99.1332, 0.7),
    ("São Paulo", -23.5505, -46.6333, 0.7),
    ("Buenos Aires", -34.6037, -58.3816, 0.6),
    ("Johannesburg", -26.2041, 28.0473, 0.6),
    ("Cairo", 30.0444, 31.2357, 0.7),
]


# ---------------------------------------------------------------------------
# Asset generation
# ---------------------------------------------------------------------------
def blend_color(color: Tuple[int, int, int], factor: float, target: Tuple[int, int, int]) -> Tuple[int, int, int]:
    return tuple(
        int(max(0, min(255, c + (target[i] - c) * factor))) for i, c in enumerate(color)
    )


def generate_ocean_surface() -> pygame.Surface:
    surface = pygame.Surface((MAP_WIDTH, MAP_HEIGHT))
    top = np.array([18, 68, 120], dtype=float)
    bottom = np.array([4, 28, 70], dtype=float)
    for y in range(MAP_HEIGHT):
        t = y / (MAP_HEIGHT - 1)
        color = (top * (1 - t) + bottom * t).astype(int)
        pygame.draw.line(surface, color, (0, y), (MAP_WIDTH, y))
    # Add subtle vertical light beams
    overlay = pygame.Surface((MAP_WIDTH, MAP_HEIGHT), pygame.SRCALPHA)
    for i in range(20):
        center = random.randint(0, MAP_WIDTH)
        width = random.randint(60, 180)
        alpha = random.randint(18, 28)
        pygame.draw.rect(overlay, (80, 160, 220, alpha), pygame.Rect(center - width // 2, 0, width, MAP_HEIGHT))
    surface.blit(overlay, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)
    return surface


def generate_continent_surface() -> Tuple[pygame.Surface, pygame.Surface]:
    land_surface = pygame.Surface((MAP_WIDTH, MAP_HEIGHT), pygame.SRCALPHA)
    mask_surface = pygame.Surface((MAP_WIDTH, MAP_HEIGHT), pygame.SRCALPHA)
    for polygon, base_color in CONTINENT_POLYGONS:
        points = [lonlat_to_mapxy(lon, lat) for lon, lat in polygon]
        pygame.draw.polygon(land_surface, (*base_color, 235), points)
        outline_color = blend_color(base_color, 0.35, (255, 255, 255))
        pygame.draw.lines(land_surface, outline_color, True, points, 3)
        pygame.draw.polygon(mask_surface, (255, 255, 255, 255), points)
    return land_surface, mask_surface


def generate_cloud_surface(seed: int = 42) -> pygame.Surface:
    random.seed(seed)
    cloud_surface = pygame.Surface((MAP_WIDTH, MAP_HEIGHT), pygame.SRCALPHA)
    for _ in range(380):
        w = random.randint(140, 280)
        h = random.randint(60, 150)
        x = random.randint(-40, MAP_WIDTH + 40)
        y = random.randint(-40, MAP_HEIGHT + 40)
        alpha = random.randint(25, 70)
        color = (255, 255, 255, alpha)
        pygame.draw.ellipse(cloud_surface, color, pygame.Rect(x, y, w, h))
    # Apply soft blur via smoothscale hack
    small = pygame.transform.smoothscale(cloud_surface, (MAP_WIDTH // 2, MAP_HEIGHT // 2))
    blurred = pygame.transform.smoothscale(small, (MAP_WIDTH, MAP_HEIGHT))
    return blurred


def generate_starfield() -> pygame.Surface:
    surface = pygame.Surface((WIDTH, HEIGHT))
    surface.fill(BACKGROUND_BOTTOM)
    for y in range(HEIGHT):
        t = y / (HEIGHT - 1)
        color = [
            int(BACKGROUND_TOP[i] * (1 - t) + BACKGROUND_BOTTOM[i] * t) for i in range(3)
        ]
        pygame.draw.line(surface, color, (0, y), (WIDTH, y))

    star_layer = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    random.seed(7)
    for _ in range(400):
        x = random.randint(0, WIDTH - 1)
        y = random.randint(0, HEIGHT // 2)
        brightness = random.randint(180, 240)
        size = random.choice([1, 1, 1, 2])
        pygame.draw.circle(star_layer, (brightness, brightness, brightness, 220), (x, y), size)
    surface.blit(star_layer, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)
    return surface


# ---------------------------------------------------------------------------
# Globe renderer
# ---------------------------------------------------------------------------
class GlobeRenderer:
    def __init__(self) -> None:
        self.ocean_surface = generate_ocean_surface()
        self.land_surface, land_mask_surface = generate_continent_surface()
        self.map_surface = self.ocean_surface.copy()
        self.map_surface.blit(self.land_surface, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)
        self.cloud_surface = generate_cloud_surface()

        self.map_pixels = pygame.surfarray.array3d(self.map_surface).astype(np.float32)
        self.land_alpha = pygame.surfarray.array_alpha(land_mask_surface).astype(np.float32) / 255.0
        self.cloud_alpha = pygame.surfarray.array_alpha(self.cloud_surface).astype(np.float32) / 255.0

        self.pixel_data: List[Tuple[int, int, float, float, Tuple[float, float, float]]] = []
        self._build_pixel_data()

        self.city_vectors = [
            (
                name,
                spherical_to_cartesian(math.radians(lat), math.radians(lon)),
                intensity,
            )
            for name, lat, lon, intensity in CITY_LIGHTS
        ]

    def _build_pixel_data(self) -> None:
        radius = GLOBE_RADIUS
        for y in range(radius * 2):
            for x in range(radius * 2):
                dx = x - radius
                dy = y - radius
                dist_sq = dx * dx + dy * dy
                if dist_sq <= radius * radius:
                    nx = dx / radius
                    ny = -dy / radius
                    nz = math.sqrt(max(0.0, 1.0 - nx * nx - ny * ny))
                    lat = math.asin(ny)
                    lon0 = math.atan2(nx, nz)
                    self.pixel_data.append((x, y, lat, lon0, (nx, ny, nz)))

    def render(self, rotation: float, sun_phase: float, cloud_offset: float) -> pygame.Surface:
        globe_surface = pygame.Surface((GLOBE_RADIUS * 2, GLOBE_RADIUS * 2), pygame.SRCALPHA)
        pixels = pygame.surfarray.pixels3d(globe_surface)
        alpha = pygame.surfarray.pixels_alpha(globe_surface)
        alpha[:, :] = 0

        sun_lat = math.radians(18) * math.sin(sun_phase * 0.5)
        sun_lon = sun_phase + rotation * 0.3
        sun_dir = spherical_to_cartesian(sun_lat, sun_lon)

        view_dir = (0.0, 0.0, 1.0)

        for px, py, lat, lon0, normal in self.pixel_data:
            lon = lon0 + rotation
            map_x = (lon / math.tau + 0.5) * MAP_WIDTH
            map_y = (0.5 - lat / math.pi) * MAP_HEIGHT

            base_color = sample_color(self.map_pixels, map_x, map_y)
            land = sample_scalar(self.land_alpha, map_x, map_y) > 0.1
            cloud_sample_x = map_x + cloud_offset * MAP_WIDTH
            cloud_alpha = sample_scalar(self.cloud_alpha, cloud_sample_x, map_y) * 0.55

            nx, ny, nz = normal
            sunlight = max(-1.0, min(1.0, nx * sun_dir[0] + ny * sun_dir[1] + nz * sun_dir[2]))

            color = np.array(base_color, dtype=float)
            ambient = 0.35

            if land:
                light = max(sunlight, 0.0)
                shaded = ambient + 0.75 * light
                color = color * shaded
                if sunlight < 0.0:
                    night_factor = min(1.0, -sunlight * 1.4)
                    color = color * 0.18 + np.array([40, 52, 90]) * (night_factor * 0.4)
                    glow = 0.0
                    for _, vec, intensity in self.city_vectors:
                        alignment = max(0.0, nx * vec[0] + ny * vec[1] + nz * vec[2])
                        glow += (alignment ** 25) * intensity
                    glow = min(glow, 1.5)
                    color += np.array([255, 190, 110]) * glow * night_factor
            else:
                light = ambient + 0.8 * max(sunlight, 0.0)
                color = color * (0.45 + 0.55 * light)
                if sunlight < 0.0:
                    color = color * 0.2 + np.array([20, 40, 70]) * (-sunlight * 0.4)

                # Specular glimmer on oceans
                if sunlight > 0.0:
                    reflect = (
                        2 * sunlight * nx - sun_dir[0],
                        2 * sunlight * ny - sun_dir[1],
                        2 * sunlight * nz - sun_dir[2],
                    )
                    spec = max(0.0, reflect[0] * view_dir[0] + reflect[1] * view_dir[1] + reflect[2] * view_dir[2])
                    specular = (spec ** 60) * 480
                    color += np.array([180, 200, 255]) * specular

            # Polar aurora accent on the night side
            lat_deg = math.degrees(lat)
            if sunlight < -0.2 and abs(lat_deg) > 55:
                aurora = min(1.0, (-sunlight - 0.2) * 1.6)
                aurora *= min(1.0, (abs(lat_deg) - 55) / 20)
                color = color * (1 - 0.3 * aurora) + np.array([60, 200, 160]) * aurora * 0.6

            if cloud_alpha > 0.01:
                cloud_light = ambient + 0.75 * max(sunlight, 0.0)
                if sunlight < 0.0:
                    cloud_color = np.array([170, 190, 220]) * (0.2 + -sunlight * 0.4)
                else:
                    cloud_color = np.array([255, 255, 255]) * (0.4 + 0.6 * cloud_light)
                color = color * (1 - cloud_alpha * 0.45) + cloud_color * (cloud_alpha * 0.45)

            # Glossy highlight toward camera
            center_weight = max(0.0, 1.0 - ((px - GLOBE_RADIUS) ** 2 + (py - GLOBE_RADIUS) ** 2) / (GLOBE_RADIUS ** 2))
            color += np.array([40, 60, 100]) * (center_weight ** 2 * 0.25)

            color = np.clip(color, 0, 255)
            pixels[px, py] = color
            alpha[px, py] = 255

        del pixels
        del alpha

        self._apply_atmosphere(globe_surface)
        self._apply_longitude_highlights(globe_surface, rotation)
        return globe_surface

    def _apply_atmosphere(self, surface: pygame.Surface) -> None:
        glow_surface = pygame.Surface((GLOBE_RADIUS * 2 + 40, GLOBE_RADIUS * 2 + 40), pygame.SRCALPHA)
        center = glow_surface.get_width() // 2
        for r in range(center, 0, -1):
            t = r / center
            alpha = int(120 * (1 - t) ** 1.8)
            color = (70, 140, 255, alpha)
            pygame.draw.circle(glow_surface, color, (center, center), r)
        surface.blit(glow_surface, (-20, -20), special_flags=pygame.BLEND_RGBA_ADD)

    def _apply_longitude_highlights(self, surface: pygame.Surface, rotation: float) -> None:
        overlay = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
        radius = GLOBE_RADIUS
        for i in range(12):
            angle = rotation + i * (math.tau / 12)
            x = radius + int(math.sin(angle) * radius * 0.92)
            color = (80, 160, 255, 40)
            pygame.draw.line(overlay, color, (x, 0), (x, radius * 2), 2)
        surface.blit(overlay, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)


def sample_color(array: np.ndarray, x: float, y: float) -> Tuple[float, float, float]:
    width, height = array.shape[:2]
    x %= width
    y = max(0.0, min(height - 1.001, y))
    x0 = int(math.floor(x))
    y0 = int(math.floor(y))
    x1 = (x0 + 1) % width
    y1 = min(height - 1, y0 + 1)
    tx = x - x0
    ty = y - y0

    c00 = array[x0, y0]
    c10 = array[x1, y0]
    c01 = array[x0, y1]
    c11 = array[x1, y1]

    top = c00 * (1 - tx) + c10 * tx
    bottom = c01 * (1 - tx) + c11 * tx
    return tuple((top * (1 - ty) + bottom * ty).tolist())


def sample_scalar(array: np.ndarray, x: float, y: float) -> float:
    width, height = array.shape[:2]
    x %= width
    y = max(0.0, min(height - 1.001, y))
    x0 = int(math.floor(x))
    y0 = int(math.floor(y))
    x1 = (x0 + 1) % width
    y1 = min(height - 1, y0 + 1)
    tx = x - x0
    ty = y - y0

    v00 = array[x0, y0]
    v10 = array[x1, y0]
    v01 = array[x0, y1]
    v11 = array[x1, y1]
    top = v00 * (1 - tx) + v10 * tx
    bottom = v01 * (1 - tx) + v11 * tx
    return float(top * (1 - ty) + bottom * ty)


# ---------------------------------------------------------------------------
# UI rendering helpers
# ---------------------------------------------------------------------------
def draw_panel(surface: pygame.Surface, selected: Destination | None) -> None:
    panel_surface = pygame.Surface(PANEL_RECT.size, pygame.SRCALPHA)
    panel_surface.fill((18, 26, 48))
    # Luxury gradient
    gradient = pygame.Surface(PANEL_RECT.size, pygame.SRCALPHA)
    for y in range(PANEL_RECT.height):
        t = y / PANEL_RECT.height
        color = (
            int(18 * (1 - t) + 8 * t),
            int(32 * (1 - t) + 18 * t),
            int(54 * (1 - t) + 32 * t),
            255,
        )
        pygame.draw.line(gradient, color, (0, y), (PANEL_RECT.width, y))
    panel_surface.blit(gradient, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)
    pygame.draw.rect(panel_surface, (80, 120, 200), panel_surface.get_rect(), 3, border_radius=28)

    title = TITLE_FONT.render("WanderWorld", True, PRIMARY_TEXT)
    tagline = SMALL_FONT.render("Curated Journeys · Day & Night", True, SECONDARY_TEXT)
    panel_surface.blit(title, (32, 32))
    panel_surface.blit(tagline, (36, 82))

    if selected is None:
        filler = [
            "Spin the globe", "and tap a radiant marker", "to reveal a", "bespoke inspiration." 
        ]
        for i, line in enumerate(filler):
            text = LABEL_FONT.render(line, True, SECONDARY_TEXT)
            panel_surface.blit(text, (36, 150 + i * 36))
    else:
        draw_destination_details(panel_surface, selected)

    surface.blit(panel_surface, PANEL_RECT.topleft)


def draw_destination_details(panel_surface: pygame.Surface, destination: Destination) -> None:
    header = LABEL_FONT.render(destination.name, True, PRIMARY_TEXT)
    panel_surface.blit(header, (36, 140))

    summary_lines = wrap_text(destination.summary, SMALL_FONT, PANEL_RECT.width - 72)
    for i, line in enumerate(summary_lines):
        text = SMALL_FONT.render(line, True, SECONDARY_TEXT)
        panel_surface.blit(text, (36, 190 + i * 26))

    highlight_rect = pygame.Rect(36, 280, PANEL_RECT.width - 72, 120)
    draw_day_night_card(panel_surface, highlight_rect, destination.palette, destination.highlights)

    note = TINY_FONT.render("Swipe up for bespoke itineraries", True, ACCENT_COLOR)
    panel_surface.blit(note, (highlight_rect.x, highlight_rect.bottom + 20))


def draw_day_night_card(surface: pygame.Surface, rect: pygame.Rect, palette: Tuple[Tuple[int, int, int], Tuple[int, int, int]], highlights: Tuple[str, str]) -> None:
    day_color, night_color = palette
    pygame.draw.rect(surface, day_color, rect, border_radius=22)
    night_rect = pygame.Rect(rect.x + rect.width // 2, rect.y, rect.width // 2, rect.height)
    pygame.draw.rect(surface, night_color, night_rect, border_radius=22)
    pygame.draw.rect(surface, (255, 255, 255), rect, width=2, border_radius=22)

    pygame.draw.circle(surface, (255, 248, 190), (rect.x + rect.width // 4, rect.centery), 26)
    pygame.draw.circle(surface, (200, 210, 255), (rect.right - rect.width // 4, rect.centery), 26)

    day_text = TINY_FONT.render(highlights[0], True, (40, 40, 60))
    night_text = TINY_FONT.render(highlights[1], True, (230, 230, 240))
    surface.blit(day_text, (rect.x + 24, rect.bottom - 40))
    surface.blit(night_text, (rect.right - night_text.get_width() - 24, rect.bottom - 40))


def wrap_text(text: str, font: pygame.font.Font, width: int) -> List[str]:
    words = text.split()
    lines: List[str] = []
    current = ""
    for word in words:
        attempt = (current + " " + word).strip()
        if font.size(attempt)[0] <= width:
            current = attempt
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


# ---------------------------------------------------------------------------
# Marker rendering & projection
# ---------------------------------------------------------------------------
def project_point(latitude: float, longitude: float, rotation: float) -> Tuple[Tuple[int, int], float] | None:
    lat_rad = math.radians(latitude)
    lon_rad = math.radians(longitude) + rotation
    x = math.sin(lon_rad) * math.cos(lat_rad)
    y = math.sin(lat_rad)
    z = math.cos(lon_rad) * math.cos(lat_rad)
    if z <= 0:
        return None
    screen_x = GLOBE_CENTER[0] + int(GLOBE_RADIUS * x)
    screen_y = GLOBE_CENTER[1] - int(GLOBE_RADIUS * y)
    depth = z
    return (screen_x, screen_y), depth


def update_destination_markers(rotation: float) -> Dict[str, pygame.Rect]:
    hitboxes: Dict[str, pygame.Rect] = {}
    for destination in DESTINATIONS.values():
        projection = project_point(destination.latitude, destination.longitude, rotation)
        if projection is None:
            destination.screen_pos = None
            destination.surface_depth = 0.0
            continue
        (x, y), depth = projection
        destination.screen_pos = (x, y)
        destination.surface_depth = depth
        size = max(18, int(22 * (0.6 + depth * 0.6)))
        rect = pygame.Rect(x - size // 2, y - size // 2, size, size)
        hitboxes[destination.key] = rect
    return hitboxes


def draw_destination_markers(surface: pygame.Surface, rotation: float, selected: Destination | None) -> None:
    for destination in DESTINATIONS.values():
        if destination.screen_pos is None:
            continue
        x, y = destination.screen_pos
        depth = destination.surface_depth
        base_alpha = int(150 + depth * 105)
        pulse = 8 + int(6 * math.sin(pygame.time.get_ticks() / 600 + depth * 4))
        glow_surface = pygame.Surface((pulse * 4, pulse * 4), pygame.SRCALPHA)
        pygame.draw.circle(glow_surface, (120, 180, 255, base_alpha), (pulse * 2, pulse * 2), pulse * 2)
        surface.blit(glow_surface, glow_surface.get_rect(center=(x, y)))

        marker_color = (255, 255, 255)
        if selected is destination:
            marker_color = ACCENT_COLOR
        pygame.draw.circle(surface, marker_color, (x, y), 8)
        pygame.draw.circle(surface, (20, 40, 80), (x, y), 8, 2)

        # Label if near front
        if depth > 0.65:
            label = TINY_FONT.render(destination.name, True, PRIMARY_TEXT)
            label_rect = label.get_rect(midtop=(x, y + 14))
            bg = pygame.Surface(label_rect.inflate(12, 8).size, pygame.SRCALPHA)
            pygame.draw.rect(bg, (12, 24, 54, 200), bg.get_rect(), border_radius=12)
            bg_rect = bg.get_rect(center=label_rect.center)
            surface.blit(bg, bg_rect)
            surface.blit(label, label_rect)


# ---------------------------------------------------------------------------
# Background embellishments
# ---------------------------------------------------------------------------
def draw_background(surface: pygame.Surface, starfield: pygame.Surface, rotation: float) -> None:
    surface.blit(starfield, (0, 0))
    # subtle horizon glow behind the globe
    gradient = pygame.Surface((GLOBE_RADIUS * 2 + 100, GLOBE_RADIUS * 2 + 100), pygame.SRCALPHA)
    center = (gradient.get_width() // 2, gradient.get_height() // 2 + 20)
    max_radius = gradient.get_width() // 2
    for r in range(max_radius, 0, -1):
        t = r / max_radius
        alpha = int(90 * (1 - t) ** 2.2)
        hue = (
            int(20 + 40 * (1 - t)),
            int(60 + 120 * (1 - t)),
            int(120 + 80 * (1 - t)),
            alpha,
        )
        pygame.draw.circle(gradient, hue, center, r)
    surface.blit(gradient, (GLOBE_CENTER[0] - gradient.get_width() // 2, GLOBE_CENTER[1] - gradient.get_height() // 2), special_flags=pygame.BLEND_RGBA_ADD)

    # orbiting particles
    orbit_surface = pygame.Surface((GLOBE_RADIUS * 2 + 20, GLOBE_RADIUS * 2 + 20), pygame.SRCALPHA)
    for i in range(40):
        angle = rotation * 0.5 + i * (math.tau / 40)
        radius = GLOBE_RADIUS + 18 + 6 * math.sin(pygame.time.get_ticks() / 900 + i)
        x = orbit_surface.get_width() // 2 + int(math.cos(angle) * radius)
        y = orbit_surface.get_height() // 2 + int(math.sin(angle) * radius * 0.3)
        pygame.draw.circle(orbit_surface, (90, 160, 255, 90), (x, y), 2)
    surface.blit(orbit_surface, (GLOBE_CENTER[0] - orbit_surface.get_width() // 2, GLOBE_CENTER[1] - orbit_surface.get_height() // 2))


# ---------------------------------------------------------------------------
# Main loop
# ---------------------------------------------------------------------------
def run() -> None:
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    clock = pygame.time.Clock()

    renderer = GlobeRenderer()
    starfield = generate_starfield()

    rotation = 0.0
    sun_phase = 0.0
    cloud_offset = 0.0
    selected: Destination | None = None
    hitboxes: Dict[str, pygame.Rect] = {}

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                for key, rect in hitboxes.items():
                    if rect.collidepoint(event.pos):
                        selected = DESTINATIONS[key]
                        break
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False

        rotation = (rotation + 0.0035 * clock.get_time()) % math.tau
        sun_phase = (sun_phase + 0.0022 * clock.get_time()) % math.tau
        cloud_offset = (cloud_offset + 0.00008 * clock.get_time()) % 1.0

        hitboxes = update_destination_markers(rotation)

        draw_background(screen, starfield, rotation)
        globe_surface = renderer.render(rotation, sun_phase, cloud_offset)
        screen.blit(globe_surface, (GLOBE_CENTER[0] - GLOBE_RADIUS, GLOBE_CENTER[1] - GLOBE_RADIUS))

        draw_destination_markers(screen, rotation, selected)
        draw_interactive_orbits(screen, selected, rotation)
        draw_panel(screen, selected)

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()


def draw_interactive_orbits(surface: pygame.Surface, selected: Destination | None, rotation: float) -> None:
    if selected is None or selected.screen_pos is None:
        return
    overlay = pygame.Surface((GLOBE_RADIUS * 2, GLOBE_RADIUS * 2), pygame.SRCALPHA)
    center = (GLOBE_RADIUS, GLOBE_RADIUS)
    base_angle = math.atan2(
        GLOBE_CENTER[1] - selected.screen_pos[1],
        selected.screen_pos[0] - GLOBE_CENTER[0],
    )
    for i in range(3):
        offset = i * 0.35
        angle = base_angle + math.sin(pygame.time.get_ticks() / 1200 + i) * 0.25
        arc_rect = pygame.Rect(0, 0, GLOBE_RADIUS * 2 - 20 - i * 16, GLOBE_RADIUS * 2 - 20 - i * 16)
        arc_rect.center = center
        start_angle = angle - 0.5 + offset
        end_angle = angle + 0.5 + offset
        pygame.draw.arc(overlay, (120, 190, 255, 140 - i * 30), arc_rect, start_angle, end_angle, 3)
    surface.blit(overlay, (GLOBE_CENTER[0] - GLOBE_RADIUS, GLOBE_CENTER[1] - GLOBE_RADIUS), special_flags=pygame.BLEND_RGBA_ADD)


if __name__ == "__main__":
    run()
