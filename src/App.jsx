import React, { useMemo, useState } from 'react';
import { Canvas } from '@react-three/fiber';
import { OrbitControls } from '@react-three/drei';
import Globe from './components/Globe.jsx';
import UIOverlay from './components/UIOverlay.jsx';
import CityPopup from './components/CityPopup.jsx';

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

export default function App() {
  const [selected, setSelected] = useState(markerData[0]);
  const [lightingMode, setLightingMode] = useState('day');
  const [showPopup, setShowPopup] = useState(false);
  const uiMarkers = useMemo(() => markerData, []);

  const handleSelect = (m) => {
    setSelected(m);
    setShowPopup(true);
  };

  return (
    <div className="relative h-screen w-screen overflow-hidden text-white font-sans">
      {/* 🟣 Gradient background */}
      <div className="absolute inset-0 -z-20 bg-[radial-gradient(circle_at_25%_20%,rgba(120,162,255,0.4),rgba(3,9,35,0.9)_60%),radial-gradient(circle_at_80%_80%,rgba(255,162,213,0.25),rgba(3,9,35,1)_75%)]" />

      {/* 🌍 Globe Canvas */}
      <div className="absolute inset-0 z-[10]">
        <Canvas
          camera={{ position: [0, 0, 3], fov: 50 }}
          gl={{ antialias: true, alpha: true }}
        >
          <color attach="background" args={[0, 0, 0, 0]} /> {/* Transparent */}
          <ambientLight intensity={lightingMode === 'day' ? 0.6 : 0.9} />
          <directionalLight
            position={[5, 3, 5]}
            intensity={lightingMode === 'day' ? 1.4 : 0.9}
            color={lightingMode === 'day' ? '#ffffff' : '#7cb7ff'}
          />
          <Globe lightingMode={lightingMode} />
          <OrbitControls enableZoom={true} zoomSpeed={0.5} rotateSpeed={0.7} minDistance={1.5} maxDistance={5} />
        </Canvas>
      </div>

      {/* 🪶 Header */}
      <div className="absolute top-10 left-10 z-[30]">
        <h1 className="text-5xl font-bold tracking-tight mb-4">Dream in Motion</h1>
        <p className="text-lg text-gray-300 max-w-xl">
          Curated journeys, luminous cities, cinematic horizons.
        </p>
      </div>

      {/* 🧭 UI Overlay */}
      <UIOverlay
        selected={selected}
        markers={uiMarkers}
        onSelectMarker={handleSelect}
        lightingMode={lightingMode}
        onLightingModeChange={setLightingMode}
      />

      {/* 🪩 City Popup */}
      {showPopup && <CityPopup city={selected} onClose={() => setShowPopup(false)} />}
    </div>
  );
}