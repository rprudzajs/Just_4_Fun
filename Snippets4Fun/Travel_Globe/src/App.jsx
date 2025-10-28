import { Suspense, useMemo, useRef, useState } from 'react';
import { Canvas, useFrame } from '@react-three/fiber';
import { Html, Stars } from '@react-three/drei';
import { motion, AnimatePresence } from 'framer-motion';
import { ACESFilmicToneMapping, SRGBColorSpace } from 'three';
import Globe from './components/Globe.jsx';
import Atmosphere from './components/Atmosphere.jsx';
import Markers from './components/Markers.jsx';
import CameraController from './components/CameraController.jsx';
import Effects from './components/Effects.jsx';
import UIOverlay from './components/UIOverlay.jsx';

function SceneContent({ lightingMode, markers, selected, onSelectMarker }) {
  const worldRef = useRef();

  useFrame((state, delta) => {
    if (!worldRef.current) return;
    worldRef.current.rotation.y += delta * 0.08;
    worldRef.current.rotation.x = Math.sin(state.clock.elapsedTime * 0.05) * 0.05;
  });

  return (
    <group ref={worldRef} position={[0, 0, 0]}>
      <Atmosphere />
      <Globe lightingMode={lightingMode} />
      <Markers markers={markers} selected={selected} onSelect={onSelectMarker} />
    </group>
  );
}

const markerData = [
  {
    id: 'hyderabad',
    name: 'Hyderabad',
    tagline: 'Regal dawn skylines meeting cutting-edge waterfront nights.',
    coordinates: { lat: 17.385, lon: 78.4867 },
    color: '#7bcfff'
  },
  {
    id: 'cape-town',
    name: 'Cape Town',
    tagline: 'Clifftop sunsets, wine country breezes, moonlit promenades.',
    coordinates: { lat: -33.9249, lon: 18.4241 },
    color: '#ffb8d2'
  },
  {
    id: 'oslo',
    name: 'Oslo',
    tagline: 'Nordic glow, fjord reflections, aurora-kissed evenings.',
    coordinates: { lat: 59.9139, lon: 10.7522 },
    color: '#9ef6ff'
  }
];

function App() {
  const [selected, setSelected] = useState(markerData[0]);
  const [lightingMode, setLightingMode] = useState('day');

  const uiMarkers = useMemo(() => markerData, []);

  return (
    <div className="relative h-full w-full overflow-hidden">
      <Canvas
        camera={{ position: [0, 0, 6], fov: 45, near: 0.1, far: 100 }}
        dpr={[1, 2]}
        gl={{ antialias: true, physicallyCorrectLights: true }}
        onCreated={({ gl }) => {
          gl.outputColorSpace = SRGBColorSpace;
          gl.toneMapping = ACESFilmicToneMapping;
          gl.toneMappingExposure = 1.1;
        }}
      >
        <color attach="background" args={[0.02, 0.04, 0.1]} />
        <Suspense
          fallback={
            <Html center>
              <div className="rounded-2xl border border-white/10 bg-white/5 px-6 py-4 text-sm uppercase tracking-[0.35em] text-white/60">
                Initializing Luxe Globe…
              </div>
            </Html>
          }
        >
          <SceneContent
            lightingMode={lightingMode}
            markers={uiMarkers}
            selected={selected}
            onSelectMarker={setSelected}
          />
          <Stars
            radius={120}
            depth={50}
            count={6000}
            factor={4}
            saturation={0}
            fade
            speed={0.6}
          />
          <Effects />
        </Suspense>
        <directionalLight
          position={[8, 4, 10]}
          intensity={1.4}
          color={lightingMode === 'day' ? '#ffffff' : '#91c4ff'}
        />
        <ambientLight intensity={lightingMode === 'day' ? 0.45 : 0.8} />
        <CameraController />
      </Canvas>

      <AnimatePresence>
        <motion.div
          className="pointer-events-none absolute inset-0"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          transition={{ duration: 0.8, ease: 'easeOut' }}
        >
          <div className="pointer-events-none absolute inset-0 bg-[radial-gradient(circle_at_25%_15%,rgba(76,137,255,0.22),transparent_55%)]" />
        </motion.div>
      </AnimatePresence>

      <UIOverlay
        selected={selected}
        markers={uiMarkers}
        onSelectMarker={setSelected}
        lightingMode={lightingMode}
        onLightingModeChange={setLightingMode}
      />
    </div>
  );
}

export default App;
