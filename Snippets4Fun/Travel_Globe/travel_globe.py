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
WIDTH, HEIGHT = 1280, 760
GLOBE_CENTER = (500, 400)
GLOBE_RADIUS = 280
FEATURE_PANEL_RECT = pygame.Rect(860, 130, 360, 520)
NAV_BAR_HEIGHT = 88
BACKGROUND_TOP = (8, 18, 44)
BACKGROUND_BOTTOM = (6, 12, 30)
PRIMARY_TEXT = (245, 248, 255)
SECONDARY_TEXT = (182, 194, 214)
ACCENT_COLOR = (140, 198, 255)

MAP_WIDTH, MAP_HEIGHT = 2048, 1024

pygame.init()
pygame.display.set_caption("WanderWorld Luxe Concept")
pygame.font.init()
TITLE_FONT = pygame.font.SysFont("Poppins", 42)
LABEL_FONT = pygame.font.SysFont("Poppins", 26)
SMALL_FONT = pygame.font.SysFont("Poppins", 18)
TINY_FONT = pygame.font.SysFont("Poppins", 14)
NAV_FONT = pygame.font.SysFont("Poppins", 20)
BUTTON_FONT = pygame.font.SysFont("Poppins", 22)
DISPLAY_FONT = pygame.font.SysFont("Playfair Display", 108)
OVERLAY_FONT = pygame.font.SysFont("Poppins", 54)


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
    "hyderabad": Destination(
        key="hyderabad",
        name="Hyderabad, India",
        summary=(
            "Discover the tech-meets-tradition culture of Hyderabad, where regal"
            " palaces glow beside futuristic riverfront skylines."
        ),
        latitude=17.3850,
        longitude=78.4867,
        palette=((255, 216, 150), (20, 38, 96)),
        highlights=("Heritage mornings", "Skyline nights"),
    ),
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


def fractal_noise(
    width: int,
    height: int,
    *,
    octaves: int = 5,
    persistence: float = 0.55,
    seed: int = 0,
) -> np.ndarray:
    rng = np.random.RandomState(seed)
    noise = np.zeros((width, height), dtype=np.float32)
    amplitude = 1.0
    total_amplitude = 0.0

    base_resolution = 32
    for octave in range(octaves):
        res_w = min(width, base_resolution * (2 ** octave))
        res_h = min(height, base_resolution * (2 ** octave))
        res_w = max(2, res_w)
        res_h = max(2, res_h)

        random_values = rng.rand(res_w, res_h).astype(np.float32)
        rgb = np.repeat(random_values[:, :, None] * 255.0, 3, axis=2).astype(np.uint8)
        small_surface = pygame.surfarray.make_surface(rgb)
        scaled = pygame.transform.smoothscale(small_surface, (width, height))
        scaled_array = (
            pygame.surfarray.array3d(scaled).astype(np.float32)[:, :, 0] / 255.0
        )

        noise += scaled_array * amplitude
        total_amplitude += amplitude
        amplitude *= persistence

    if total_amplitude == 0:
        return noise
    noise /= total_amplitude
    return noise


def soft_blur(surface: pygame.Surface, factor: float = 0.35, passes: int = 2) -> pygame.Surface:
    width, height = surface.get_size()
    working = surface.copy()
    for _ in range(passes):
        scaled = pygame.transform.smoothscale(
            working,
            (
                max(2, int(width * factor)),
                max(2, int(height * factor)),
            ),
        )
        working = pygame.transform.smoothscale(scaled, (width, height))
    return working


def generate_ocean_surface() -> Tuple[pygame.Surface, np.ndarray]:
    gradient = np.zeros((MAP_WIDTH, MAP_HEIGHT, 3), dtype=np.float32)
    top = np.array([18, 70, 128], dtype=np.float32)
    bottom = np.array([4, 26, 64], dtype=np.float32)
    latitudes = np.linspace(0.0, 1.0, MAP_HEIGHT, dtype=np.float32)
    gradient[:] = (top * (1 - latitudes)[:, None]) + (bottom * latitudes[:, None])

    depth_noise = fractal_noise(
        MAP_WIDTH,
        MAP_HEIGHT,
        octaves=6,
        persistence=0.6,
        seed=11,
    )
    ripple_noise = fractal_noise(
        MAP_WIDTH,
        MAP_HEIGHT,
        octaves=4,
        persistence=0.55,
        seed=23,
    )

    gradient += (depth_noise[:, :, None] - 0.5) * 90.0
    gradient += (ripple_noise[:, :, None] - 0.5) * 35.0

    longitude = np.linspace(-1.0, 1.0, MAP_WIDTH, dtype=np.float32)[:, None]
    gradient += ((1.0 - longitude**2) * 28.0)[:, None]

    gradient = np.clip(gradient, 0, 255).astype(np.uint8)
    ocean_surface = pygame.Surface((MAP_WIDTH, MAP_HEIGHT))
    pygame.surfarray.blit_array(ocean_surface, gradient)

    caustics = pygame.Surface((MAP_WIDTH, MAP_HEIGHT), pygame.SRCALPHA)
    for i in range(28):
        center = random.randint(0, MAP_WIDTH)
        width = random.randint(80, 220)
        alpha = random.randint(12, 26)
        pygame.draw.rect(
            caustics,
            (120, 200, 255, alpha),
            pygame.Rect(center - width // 2, 0, width, MAP_HEIGHT),
        )
    caustics = soft_blur(caustics, factor=0.18, passes=2)
    ocean_surface.blit(caustics, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)

    return ocean_surface, depth_noise


def generate_continent_surface() -> Tuple[pygame.Surface, pygame.Surface, np.ndarray]:
    land_surface = pygame.Surface((MAP_WIDTH, MAP_HEIGHT), pygame.SRCALPHA)
    mask_surface = pygame.Surface((MAP_WIDTH, MAP_HEIGHT), pygame.SRCALPHA)
    for polygon, base_color in CONTINENT_POLYGONS:
        points = [lonlat_to_mapxy(lon, lat) for lon, lat in polygon]
        pygame.draw.polygon(land_surface, (*base_color, 240), points)
        outline_color = blend_color(base_color, 0.4, (255, 255, 255))
        pygame.draw.lines(land_surface, outline_color, True, points, 2)
        pygame.draw.polygon(mask_surface, (255, 255, 255, 255), points)

    height_map = fractal_noise(
        MAP_WIDTH,
        MAP_HEIGHT,
        octaves=6,
        persistence=0.58,
        seed=37,
    )

    land_pixels = pygame.surfarray.pixels3d(land_surface)
    land_array = land_pixels.astype(np.float32)
    alpha_pixels = pygame.surfarray.pixels_alpha(land_surface).astype(np.float32) / 255.0

    shade = (height_map[:, :, None] - 0.5) * 120.0
    lat_falloff = np.linspace(0.8, 1.2, MAP_HEIGHT, dtype=np.float32)
    shade *= lat_falloff[None, :, None]
    land_array += shade

    coast_mask = soft_blur(mask_surface, factor=0.1, passes=2)
    coast_alpha = pygame.surfarray.array_alpha(coast_mask).astype(np.float32) / 255.0
    coast_highlight = np.clip(coast_alpha - alpha_pixels, 0.0, 1.0)
    land_array += coast_highlight[:, :, None] * np.array([80, 120, 160], dtype=np.float32)

    land_array = np.clip(land_array, 0, 255).astype(np.uint8)
    land_pixels[:, :, :] = land_array
    del land_pixels

    alpha_view = pygame.surfarray.pixels_alpha(land_surface)
    alpha_view[:, :] = (alpha_pixels * 255).astype(np.uint8)
    del alpha_view

    return land_surface, mask_surface, height_map


def generate_cloud_surface(seed: int = 42) -> pygame.Surface:
    random.seed(seed)
    cloud_surface = pygame.Surface((MAP_WIDTH, MAP_HEIGHT), pygame.SRCALPHA)
    for _ in range(560):
        w = random.randint(180, 360)
        h = random.randint(70, 190)
        x = random.randint(-80, MAP_WIDTH + 80)
        y = random.randint(-80, MAP_HEIGHT + 80)
        alpha = random.randint(22, 65)
        color = (255, 255, 255, alpha)
        pygame.draw.ellipse(cloud_surface, color, pygame.Rect(x, y, w, h))
    noise = fractal_noise(
        MAP_WIDTH,
        MAP_HEIGHT,
        octaves=5,
        persistence=0.65,
        seed=seed + 7,
    )
    noise_surface = pygame.Surface((MAP_WIDTH, MAP_HEIGHT), pygame.SRCALPHA)
    noise_pixels = (np.clip((noise - 0.4) * 255.0 * 1.4, 0, 255)).astype(np.uint8)
    alpha_overlay = np.repeat(noise_pixels[:, :, None], 3, axis=2)
    pygame.surfarray.blit_array(noise_surface, alpha_overlay)
    noise_surface.set_alpha(110)
    cloud_surface.blit(noise_surface, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)

    blurred = soft_blur(cloud_surface, factor=0.22, passes=2)
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
        self.ocean_surface, self.ocean_variation = generate_ocean_surface()
        (
            self.land_surface,
            land_mask_surface,
            self.elevation_map,
        ) = generate_continent_surface()
        self.map_surface = self.ocean_surface.copy()
        self.map_surface.blit(self.land_surface, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)
        self.cloud_surface = generate_cloud_surface()

        self.map_pixels = pygame.surfarray.array3d(self.map_surface).astype(np.float32)
        self.land_alpha = pygame.surfarray.array_alpha(land_mask_surface).astype(np.float32) / 255.0
        self.elevation_map = self.elevation_map.astype(np.float32)
        self.ocean_variation = self.ocean_variation.astype(np.float32)
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
            elevation = sample_scalar(self.elevation_map, map_x, map_y)
            ocean_detail = sample_scalar(self.ocean_variation, map_x, map_y)
            cloud_sample_x = map_x + cloud_offset * MAP_WIDTH
            cloud_alpha = sample_scalar(self.cloud_alpha, cloud_sample_x, map_y) * 0.55

            nx, ny, nz = normal
            sunlight = max(-1.0, min(1.0, nx * sun_dir[0] + ny * sun_dir[1] + nz * sun_dir[2]))
            fresnel = max(0.0, 1.0 - nz)
            view_alignment = max(0.0, nz)

            color = np.array(base_color, dtype=float)
            ambient = 0.35

            if land:
                light = max(sunlight, 0.0)
                relief = 0.55 + 0.45 * elevation
                shaded = (ambient * 0.9 + 0.95 * light * relief)
                color = color * shaded
                golden = np.array([255, 190, 120]) * (light ** 0.35) * 0.35
                color += golden * relief
                if sunlight < 0.0:
                    night_factor = min(1.0, -sunlight * 1.4)
                    color = color * 0.18 + np.array([40, 52, 90]) * (night_factor * 0.4)
                    glow = 0.0
                    for _, vec, intensity in self.city_vectors:
                        alignment = max(0.0, nx * vec[0] + ny * vec[1] + nz * vec[2])
                        glow += (alignment ** 30) * intensity
                    glow = min(glow, 1.8)
                    color += np.array([255, 200, 150]) * glow * night_factor
                else:
                    dusk = (1.0 - view_alignment) ** 3
                    dusk_tone = np.array([255, 160, 140]) * dusk * 0.6
                    color += dusk_tone
            else:
                light = ambient + 0.8 * max(sunlight, 0.0)
                depth_tint = 0.55 + 0.45 * ocean_detail
                color = color * (0.42 + 0.58 * light * depth_tint)
                if sunlight < 0.0:
                    color = color * 0.24 + np.array([16, 40, 72]) * (-sunlight * 0.45)

                # Specular glimmer on oceans
                if sunlight > 0.0:
                    reflect = (
                        2 * sunlight * nx - sun_dir[0],
                        2 * sunlight * ny - sun_dir[1],
                        2 * sunlight * nz - sun_dir[2],
                    )
                    spec = max(0.0, reflect[0] * view_dir[0] + reflect[1] * view_dir[1] + reflect[2] * view_dir[2])
                    specular = (spec ** 80) * 520
                    color += np.array([190, 220, 255]) * specular * (0.6 + 0.4 * depth_tint)

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
                    cloud_color = np.array([255, 255, 255]) * (0.35 + 0.65 * cloud_light)
                color = color * (1 - cloud_alpha * 0.45) + cloud_color * (cloud_alpha * 0.45)

            # Glossy highlight toward camera
            center_weight = max(0.0, 1.0 - ((px - GLOBE_RADIUS) ** 2 + (py - GLOBE_RADIUS) ** 2) / (GLOBE_RADIUS ** 2))
            atmosphere = np.array([90, 140, 255]) * (fresnel ** 2) * 0.35
            color += atmosphere
            color += np.array([36, 56, 110]) * (center_weight ** 2 * 0.22)

            color = np.clip(color, 0, 255)
            pixels[px, py] = color
            alpha[px, py] = 255

        del pixels
        del alpha

        self._apply_atmosphere(globe_surface)
        self._apply_longitude_highlights(globe_surface, rotation)
        return globe_surface

    def _apply_atmosphere(self, surface: pygame.Surface) -> None:
        bloom = soft_blur(surface, factor=0.32, passes=1)
        bloom.fill((130, 190, 255, 255), special_flags=pygame.BLEND_RGBA_MULT)
        surface.blit(bloom, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)

        glow_surface = pygame.Surface((GLOBE_RADIUS * 2 + 48, GLOBE_RADIUS * 2 + 48), pygame.SRCALPHA)
        center = glow_surface.get_width() // 2
        for r in range(center, 0, -1):
            t = r / center
            alpha = int(140 * (1 - t) ** 1.9)
            color = (70, 150, 255, alpha)
            pygame.draw.circle(glow_surface, color, (center, center), r)
        surface.blit(glow_surface, (-24, -24), special_flags=pygame.BLEND_RGBA_ADD)

        rim = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
        center_point = (GLOBE_RADIUS, GLOBE_RADIUS)
        for i in range(42):
            radius = GLOBE_RADIUS - i
            alpha_value = max(0, 130 - i * 3)
            pygame.draw.circle(rim, (90, 170, 255, alpha_value), center_point, radius, width=2)
        surface.blit(rim, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)

    def _apply_longitude_highlights(self, surface: pygame.Surface, rotation: float) -> None:
        overlay = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
        radius = GLOBE_RADIUS
        for i in range(16):
            angle = rotation + i * (math.tau / 16)
            x = radius + int(math.sin(angle) * radius * 0.94)
            beam = pygame.Surface((6, radius * 2), pygame.SRCALPHA)
            for y in range(radius * 2):
                t = abs((y - radius) / radius)
                alpha = max(0, 110 - int(t * 110))
                pygame.draw.line(beam, (120, 200, 255, alpha // 2), (0, y), (5, y))
            beam = soft_blur(beam, factor=0.45, passes=1)
            overlay.blit(beam, (x - 3, 0), special_flags=pygame.BLEND_RGBA_ADD)
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
def draw_feature_panel(surface: pygame.Surface, selected: Destination | None) -> None:
    destination = selected or DESTINATIONS["hyderabad"]
    panel_surface = pygame.Surface(FEATURE_PANEL_RECT.size, pygame.SRCALPHA)
    panel_rect = panel_surface.get_rect()

    gradient = pygame.Surface(panel_rect.size, pygame.SRCALPHA)
    top_color = (22, 36, 72, 255)
    bottom_color = (10, 18, 40, 255)
    for y in range(panel_rect.height):
        t = y / max(1, panel_rect.height - 1)
        color = (
            int(top_color[0] * (1 - t) + bottom_color[0] * t),
            int(top_color[1] * (1 - t) + bottom_color[1] * t),
            int(top_color[2] * (1 - t) + bottom_color[2] * t),
            255,
        )
        pygame.draw.line(gradient, color, (0, y), (panel_rect.width, y))
    panel_surface.blit(gradient, (0, 0))

    vignette = pygame.Surface(panel_rect.size, pygame.SRCALPHA)
    for r in range(0, panel_rect.width // 2, 4):
        alpha = max(0, 120 - int(r * 0.45))
        pygame.draw.circle(
            vignette,
            (30, 60, 140, alpha),
            (panel_rect.width // 2, panel_rect.height // 2),
            panel_rect.width // 2 - r,
        )
    panel_surface.blit(vignette, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)

    pygame.draw.rect(
        panel_surface,
        (70, 112, 210),
        panel_rect,
        width=2,
        border_radius=32,
    )

    badge = TINY_FONT.render("FEATURE JOURNEY", True, ACCENT_COLOR)
    panel_surface.blit(badge, (36, 36))

    title = LABEL_FONT.render(destination.name, True, PRIMARY_TEXT)
    panel_surface.blit(title, (36, 70))

    summary_lines = wrap_text(destination.summary, SMALL_FONT, panel_rect.width - 72)
    for i, line in enumerate(summary_lines[:4]):
        text = SMALL_FONT.render(line, True, SECONDARY_TEXT)
        panel_surface.blit(text, (36, 122 + i * 26))

    preview_rect = pygame.Rect(36, 220, panel_rect.width - 72, 200)
    draw_split_preview(panel_surface, preview_rect, destination.palette, destination.highlights)

    itinerary = SMALL_FONT.render("Open curated plan", True, PRIMARY_TEXT)
    button_rect = pygame.Rect(36, panel_rect.height - 96, panel_rect.width - 72, 56)
    draw_button(panel_surface, button_rect, itinerary)

    surface.blit(panel_surface, FEATURE_PANEL_RECT.topleft)


def draw_split_preview(
    surface: pygame.Surface,
    rect: pygame.Rect,
    palette: Tuple[Tuple[int, int, int], Tuple[int, int, int]],
    highlights: Tuple[str, str],
) -> None:
    day_color, night_color = palette
    preview = pygame.Surface(rect.size, pygame.SRCALPHA)
    day_rect = pygame.Rect(0, 0, rect.width // 2 + 4, rect.height)
    night_rect = pygame.Rect(rect.width // 2 - 4, 0, rect.width // 2 + 4, rect.height)

    pygame.draw.rect(preview, day_color, day_rect, border_radius=28)
    pygame.draw.rect(preview, night_color, night_rect, border_radius=28)

    gloss = pygame.Surface(rect.size, pygame.SRCALPHA)
    for y in range(rect.height):
        t = y / max(1, rect.height - 1)
        alpha = int(120 * (1 - t) ** 2)
        pygame.draw.line(gloss, (255, 255, 255, alpha), (0, y), (rect.width, y))
    preview.blit(gloss, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)

    divider = pygame.Surface((4, rect.height), pygame.SRCALPHA)
    pygame.draw.rect(divider, (255, 255, 255, 80), divider.get_rect(), border_radius=2)
    preview.blit(divider, (rect.width // 2 - 2, 0))

    sun = pygame.Surface((64, 64), pygame.SRCALPHA)
    pygame.draw.circle(sun, (255, 238, 190, 230), (32, 32), 28)
    pygame.draw.circle(sun, (255, 255, 255, 100), (24, 28), 18)
    preview.blit(sun, (rect.width // 4 - 32, 32))

    moon = pygame.Surface((64, 64), pygame.SRCALPHA)
    pygame.draw.circle(moon, (190, 200, 255, 230), (32, 32), 28)
    pygame.draw.circle(moon, (255, 255, 255, 160), (22, 28), 12)
    pygame.draw.circle(moon, (120, 160, 255, 200), (38, 38), 18)
    preview.blit(moon, (rect.width * 3 // 4 - 32, 32))

    day_text = TINY_FONT.render(highlights[0], True, (32, 34, 56))
    night_text = TINY_FONT.render(highlights[1], True, (220, 226, 248))
    preview.blit(day_text, (36, rect.height - 56))
    preview.blit(night_text, (rect.width - night_text.get_width() - 36, rect.height - 56))

    preview_shadow = pygame.Surface((rect.width + 12, rect.height + 12), pygame.SRCALPHA)
    pygame.draw.ellipse(preview_shadow, (0, 0, 0, 80), preview_shadow.get_rect())
    surface.blit(preview_shadow, (rect.x - 6, rect.bottom - 24))
    surface.blit(preview, rect.topleft)


def draw_button(surface: pygame.Surface, rect: pygame.Rect, label_surface: pygame.Surface) -> None:
    button = pygame.Surface(rect.size, pygame.SRCALPHA)
    for y in range(rect.height):
        t = y / max(1, rect.height - 1)
        color = (
            int(30 * (1 - t) + 90 * t),
            int(60 * (1 - t) + 130 * t),
            int(120 * (1 - t) + 190 * t),
            255,
        )
        pygame.draw.line(button, color, (0, y), (rect.width, y))

    highlight = pygame.Surface(rect.size, pygame.SRCALPHA)
    pygame.draw.rect(highlight, (255, 255, 255, 60), highlight.get_rect(), border_radius=26)
    button.blit(highlight, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)
    pygame.draw.rect(button, (255, 255, 255, 90), button.get_rect(), width=2, border_radius=26)

    button.blit(
        label_surface,
        label_surface.get_rect(center=(rect.width // 2 - 12, rect.height // 2)),
    )
    pygame.draw.circle(button, (255, 255, 255), (rect.width - 48, rect.height // 2), 16, width=2)
    arrow = [(rect.width - 56, rect.height // 2), (rect.width - 46, rect.height // 2 - 6), (rect.width - 46, rect.height // 2 + 6)]
    pygame.draw.polygon(button, PRIMARY_TEXT, arrow)

    surface.blit(button, rect.topleft)


def draw_navigation_bar(surface: pygame.Surface) -> None:
    nav_surface = pygame.Surface((WIDTH, NAV_BAR_HEIGHT), pygame.SRCALPHA)
    gradient = pygame.Surface(nav_surface.get_size(), pygame.SRCALPHA)
    for x in range(WIDTH):
        t = x / max(1, WIDTH - 1)
        color = (
            int(12 + 18 * t),
            int(28 + 24 * t),
            int(52 + 40 * t),
            230,
        )
        pygame.draw.line(gradient, color, (x, 0), (x, NAV_BAR_HEIGHT))
    nav_surface.blit(gradient, (0, 0))

    glass = pygame.Surface(nav_surface.get_size(), pygame.SRCALPHA)
    pygame.draw.rect(glass, (255, 255, 255, 28), glass.get_rect(), border_radius=28)
    nav_surface.blit(glass, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)

    brand = TITLE_FONT.render("Wanderlust", True, PRIMARY_TEXT)
    nav_surface.blit(brand, (44, NAV_BAR_HEIGHT // 2 - brand.get_height() // 2))

    items = ["Discover", "Journeys", "Experiences", "Journal"]
    start_x = 240
    for idx, item in enumerate(items):
        label = NAV_FONT.render(item, True, PRIMARY_TEXT if idx == 0 else SECONDARY_TEXT)
        pos = (start_x + idx * 150, NAV_BAR_HEIGHT // 2 - label.get_height() // 2)
        nav_surface.blit(label, pos)
        if idx == 0:
            underline = pygame.Surface((label.get_width() + 16, 6), pygame.SRCALPHA)
            pygame.draw.rect(underline, (140, 198, 255, 160), underline.get_rect(), border_radius=3)
            nav_surface.blit(underline, (pos[0] - 8, NAV_BAR_HEIGHT - 18))

    button_rect = pygame.Rect(WIDTH - 220, 20, 160, NAV_BAR_HEIGHT - 40)
    button_surface = pygame.Surface(button_rect.size, pygame.SRCALPHA)
    for y in range(button_rect.height):
        t = y / max(1, button_rect.height - 1)
        color = (
            int(40 * (1 - t) + 90 * t),
            int(80 * (1 - t) + 150 * t),
            int(140 * (1 - t) + 210 * t),
            255,
        )
        pygame.draw.line(button_surface, color, (0, y), (button_rect.width, y))
    pygame.draw.rect(button_surface, (255, 255, 255, 100), button_surface.get_rect(), width=2, border_radius=22)
    cta = NAV_FONT.render("Plan a Trip", True, PRIMARY_TEXT)
    button_surface.blit(cta, cta.get_rect(center=(button_rect.width // 2, button_rect.height // 2)))
    nav_surface.blit(button_surface, button_rect.topleft)

    surface.blit(nav_surface, (0, 0))

    shadow = pygame.Surface((WIDTH, 20), pygame.SRCALPHA)
    for y in range(20):
        alpha = max(0, 70 - y * 6)
        pygame.draw.line(shadow, (0, 0, 0, alpha), (0, y), (WIDTH, y))
    surface.blit(shadow, (0, NAV_BAR_HEIGHT - 4))


def draw_globe_callout(surface: pygame.Surface, selected: Destination | None) -> None:
    callout_width = 260
    callout_height = 132
    x = GLOBE_CENTER[0] - GLOBE_RADIUS + 60
    y = max(NAV_BAR_HEIGHT + 24, GLOBE_CENTER[1] - GLOBE_RADIUS - 10)
    callout_rect = pygame.Rect(x, y, callout_width, callout_height)

    callout = pygame.Surface((callout_width, callout_height), pygame.SRCALPHA)
    for i in range(callout_height):
        t = i / max(1, callout_height - 1)
        color = (
            int(30 * (1 - t) + 18 * t),
            int(54 * (1 - t) + 32 * t),
            int(96 * (1 - t) + 48 * t),
            220,
        )
        pygame.draw.line(callout, color, (0, i), (callout_width, i))
    pygame.draw.rect(callout, (255, 255, 255, 80), callout.get_rect(), width=2, border_radius=24)

    title = SMALL_FONT.render("Explore the globe", True, PRIMARY_TEXT)
    copy_lines = [
        "Drag to spin the sphere.",
        "Tap the haloed markers",
        "to reveal day & night moods.",
    ]
    callout.blit(title, (20, 20))
    for idx, line in enumerate(copy_lines):
        text = TINY_FONT.render(line, True, SECONDARY_TEXT)
        callout.blit(text, (20, 50 + idx * 22))

    pointer = pygame.Surface((44, 40), pygame.SRCALPHA)
    pygame.draw.polygon(
        pointer,
        (40, 72, 120, 220),
        [(0, 12), (32, 0), (32, 22)],
    )
    surface.blit(pointer, (callout_rect.right - 6, callout_rect.centery - 10))
    surface.blit(callout, callout_rect.topleft)

    if selected:
        sublabel = TINY_FONT.render(f"Featured: {selected.name}", True, ACCENT_COLOR)
        surface.blit(sublabel, (callout_rect.x, callout_rect.bottom + 12))


def draw_showcase_typography(surface: pygame.Surface) -> None:
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)

    codex = DISPLAY_FONT.render("Codex", True, PRIMARY_TEXT)
    codex.set_alpha(55)
    overlay.blit(codex, (60, HEIGHT // 2 - 140))

    subtitle = OVERLAY_FONT.render("Front-end code", True, PRIMARY_TEXT)
    subtitle.set_alpha(65)
    overlay.blit(subtitle, (480, HEIGHT - 180))

    surface.blit(overlay, (0, 0))


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

    aurora_sheet = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    pygame.draw.ellipse(
        aurora_sheet,
        (60, 140, 220, 60),
        pygame.Rect(-120, HEIGHT // 2, WIDTH + 240, HEIGHT),
    )
    pygame.draw.ellipse(
        aurora_sheet,
        (120, 200, 255, 45),
        pygame.Rect(WIDTH // 2 - 160, HEIGHT // 2 - 220, WIDTH, HEIGHT),
    )
    surface.blit(aurora_sheet, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)

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
    selected: Destination | None = DESTINATIONS["hyderabad"]
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
        draw_navigation_bar(screen)
        globe_surface = renderer.render(rotation, sun_phase, cloud_offset)
        screen.blit(globe_surface, (GLOBE_CENTER[0] - GLOBE_RADIUS, GLOBE_CENTER[1] - GLOBE_RADIUS))

        draw_destination_markers(screen, rotation, selected)
        draw_interactive_orbits(screen, selected, rotation)
        draw_globe_callout(screen, selected)
        draw_feature_panel(screen, selected)
        draw_showcase_typography(screen)

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
