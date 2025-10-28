# Wanderworld Luxe Globe (React Three Fiber)

A cinematic WebGL travel hero built with React Three Fiber, Drei, Postprocessing, and TailwindCSS. The experience mirrors luxury travel inspiration sites with a glassmorphism UI, soft bloom, and custom-shaded Earth.

## Getting Started

```bash
cd Snippets4Fun/Travel_Globe
npm install
npm run dev
```

The dev server runs on Vite and opens automatically on `http://localhost:5173`.

### Detailed setup checklist

1. Install the [Active LTS release of Node.js](https://nodejs.org/en/download/) (v18+ recommended) which ships with `npm`.
2. From a terminal, navigate into this snippet's folder and install dependencies:
   ```bash
   cd Snippets4Fun/Travel_Globe
   npm install
   ```
   > If you are working behind a proxy or an offline sandbox, allowlist the npm registry so packages like `@react-three/drei` and `@react-three/postprocessing` can be fetched.
3. Launch the development server:
   ```bash
   npm run dev
   ```
4. Open the URL printed in the console (default `http://localhost:5173`) to explore the cinematic globe.

To ship a production build, run `npm run build` and serve the generated files from `dist/` using any static host.

## High-Resolution Textures

The globe boots with procedural fallbacks while it streams premium textures from the [pmndrs/drei-assets](https://github.com/pmndrs/drei-assets) CDN. If you prefer to ship your own 2K NASA maps, update the URLs inside `src/config/textureSources.js` or replace them with local imports following the same keys:

- `day`
- `night`
- `normal`
- `clouds`

## File Map

```
src/
  App.jsx              # Canvas layout, lighting controls, and overlay wiring
  components/
    Globe.jsx          # Physically-based Earth material with day/night blending and cloud layer
    Atmosphere.jsx     # Additive rim-lit atmosphere shell
    Markers.jsx        # Destination markers with Html labels & framer-motion animations
    CameraController.jsx # OrbitControls wrapper with cinematic damping + autorotation
    Effects.jsx        # Bloom, tone mapping, and depth of field composer
    UIOverlay.jsx      # Tailwind glassmorphism interface with feature card & toggles
  config/textureSources.js # Remote / local texture source definitions
  styles/index.css     # Tailwind entrypoint + cinematic background gradients
```

## Features

- Glassy UI overlay with hero typography and animated featured journey card
- Physically-lit Earth shading with dynamic sunlight, emissive night glow, and cloud parallax
- Additive atmosphere halo, bloom, and depth of field for cinematic polish
- Interactive travel markers (Hyderabad, Cape Town, Oslo) that orbit with the globe
- Day/Night toggle that swaps texture mood and rebalances lighting

Enjoy crafting your Wanderlust Luxe journeys! ✨
