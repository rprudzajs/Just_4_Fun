# Wanderworld Luxe Globe (React Three Fiber)

A cinematic WebGL travel hero built with React Three Fiber, Drei, Postprocessing, and TailwindCSS. The experience mirrors luxury travel inspiration sites with a glassmorphism UI, soft bloom, and custom-shaded Earth.

## Getting Started

```bash
cd Snippets4Fun/Travel_Globe
npm install
npm run dev
```

The dev server runs on Vite and opens automatically on `http://localhost:5173`.

## High-Resolution Textures

The globe boots with procedural fallbacks while it streams premium textures from the [pmndrs/drei-assets](https://github.com/pmndrs/drei-assets) CDN. If you prefer to ship your own 2K NASA maps, update the URLs inside `src/config/textureSources.js` or replace them with local imports following the same keys:

- `day`
- `night`
- `normal`
- `specular`

## File Map

```
src/
  App.jsx              # Canvas layout, lighting controls, and overlay wiring
  components/
    Globe.jsx          # Custom shader material blending day/night + specular maps
    Atmosphere.jsx     # Additive rim-lit atmosphere shell
    Markers.jsx        # Destination markers with Html labels & framer-motion animations
    CameraController.jsx # OrbitControls wrapper with smooth focus easing
    Effects.jsx        # Bloom, tone mapping, and depth of field composer
    UIOverlay.jsx      # Tailwind glassmorphism interface with feature card & toggles
  config/textureSources.js # Remote / local texture source definitions
  styles/index.css     # Tailwind entrypoint + cinematic background gradients
```

## Features

- Glassy UI overlay with hero typography and animated featured journey card
- Custom GLSL-driven Earth shading with dynamic sunlight and city glow transitions
- Additive atmosphere halo, bloom, and depth of field for cinematic polish
- Interactive travel markers (Hyderabad, Cape Town, Oslo) with camera fly-to behavior
- Day/Night toggle that shifts lighting balance and specular styling

Enjoy crafting your Wanderlust Luxe journeys! ✨
