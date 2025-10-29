import React, { useRef } from 'react';
import { useFrame, useLoader } from '@react-three/fiber';
import * as THREE from 'three';
import { textureSources } from '../config/textureSources';

export default function Globe({ lightingMode }) {
  const globeRef = useRef();
  const cloudsRef = useRef();

  // Load textures
  const [dayTexture, nightTexture, cloudsTexture] = useLoader(THREE.TextureLoader, [
    textureSources.earthDayMap,
    textureSources.earthNightMap,
    textureSources.earthCloudsMap
  ]);

  useFrame(({ clock }) => {
    const elapsed = clock.getElapsedTime();
    globeRef.current.rotation.y = elapsed * 0.05;
    cloudsRef.current.rotation.y = elapsed * 0.06;
  });

  return (
    <group>
      {/* Earth */}
      <mesh ref={globeRef}>
        <sphereGeometry args={[1, 64, 64]} />
        <meshPhongMaterial
          map={lightingMode === 'day' ? dayTexture : nightTexture}
          shininess={10}
        />
      </mesh>

      {/* Clouds */}
      <mesh ref={cloudsRef}>
        <sphereGeometry args={[1.01, 64, 64]} />
        <meshPhongMaterial
          map={cloudsTexture}
          transparent
          opacity={0.4}
          depthWrite={false}
        />
      </mesh>
    </group>
  );
}
