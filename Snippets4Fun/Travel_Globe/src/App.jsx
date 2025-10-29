import { useMemo, useState } from 'react';
import { Canvas } from '@react-three/fiber';
import { OrbitControls, Stars } from '@react-three/drei';
import Globe from './components/Globe.jsx';
import UIOverlay from './components/UIOverlay.jsx';

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
    <div className="relative min-h-screen w-full overflow-hidden bg-[#030923] text-white">
      <div className="absolute inset-0 -z-20 bg-[radial-gradient(circle_at_30%_15%,rgba(99,163,255,0.45),rgba(3,9,35,0.75)_55%),radial-gradient(circle_at_70%_85%,rgba(255,162,213,0.2),rgba(3,9,35,0.95)_65%)]" />

      <Canvas
        className="absolute inset-0 -z-10"
        camera={{ position: [0, 0, 6], fov: 45, near: 0.1, far: 100 }}
        dpr={[1, 2]}
        gl={{ antialias: true }}
      >
        <color attach="background" args={[0.01, 0.03, 0.09]} />
        <ambientLight intensity={lightingMode === 'day' ? 0.5 : 0.75} />
        <directionalLight
          position={[5, 3, 5]}
          intensity={lightingMode === 'day' ? 1.4 : 0.9}
          color={lightingMode === 'day' ? '#ffffff' : '#7cb7ff'}
        />
        <Globe
          lightingMode={lightingMode}
          markers={uiMarkers}
          selected={selected}
          onSelectMarker={setSelected}
        />
        <Stars radius={140} depth={40} count={4000} factor={4} saturation={0} fade speed={0.6} />
        <OrbitControls
          enablePan={false}
          enableZoom
          zoomSpeed={0.5}
          minDistance={4.2}
          maxDistance={9}
          enableDamping
          dampingFactor={0.12}
          autoRotate
          autoRotateSpeed={0.15}
        />
      </Canvas>

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
