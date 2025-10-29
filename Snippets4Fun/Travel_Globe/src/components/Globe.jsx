import { useEffect, useMemo, useRef, useState } from 'react';
import { useFrame } from '@react-three/fiber';
import { AdditiveBlending, Color, LinearFilter, SRGBColorSpace, TextureLoader } from 'three';
import Atmosphere from './Atmosphere.jsx';
import Markers from './Markers.jsx';
import { TEXTURE_SOURCES } from '../config/textureSources.js';

function useTextureSafe(url) {
  const [texture, setTexture] = useState(null);

  useEffect(() => {
    if (!url) {
      setTexture(null);
      return undefined;
    }

    let mounted = true;
    const loader = new TextureLoader();
    loader.setCrossOrigin('anonymous');

    const handleLoad = (loadedTexture) => {
      if (!mounted) return;
      loadedTexture.colorSpace = SRGBColorSpace;
      loadedTexture.minFilter = LinearFilter;
      loadedTexture.magFilter = LinearFilter;
      loadedTexture.needsUpdate = true;
      setTexture(loadedTexture);
    };

    const handleError = () => {
      if (mounted) setTexture(null);
    };

    loader.load(url, handleLoad, undefined, handleError);

    return () => {
      mounted = false;
    };
  }, [url]);

  return texture;
}

export default function Globe({ lightingMode = 'day', markers = [], selected, onSelectMarker }) {
  const groupRef = useRef();
  const cloudsRef = useRef();

  const dayTexture = useTextureSafe(TEXTURE_SOURCES.day);
  const nightTexture = useTextureSafe(TEXTURE_SOURCES.night);
  const cloudsTexture = useTextureSafe(TEXTURE_SOURCES.clouds);

  const materialProps = useMemo(() => {
    const baseColor = lightingMode === 'night' ? '#0a1631' : '#8fc6ff';
    const emissiveColor = lightingMode === 'night' ? new Color('#1a2f6d') : new Color('#000000');

    return {
      color: baseColor,
      map: lightingMode === 'night' ? nightTexture ?? dayTexture : dayTexture ?? null,
      emissive: emissiveColor,
      emissiveMap: lightingMode === 'night' ? nightTexture ?? null : null,
      emissiveIntensity: lightingMode === 'night' ? 0.45 : 0.05,
      roughness: 0.8,
      metalness: 0.1
    };
  }, [dayTexture, nightTexture, lightingMode]);

  useFrame((_, delta) => {
    if (groupRef.current) {
      groupRef.current.rotation.y += delta * 0.2;
    }

    if (cloudsRef.current) {
      cloudsRef.current.rotation.y += delta * 0.08;
    }
  });

  return (
    <group ref={groupRef} scale={2} position={[0, -0.2, 0]}>
      <mesh>
        <sphereGeometry args={[1, 128, 128]} />
        <meshStandardMaterial attach="material" {...materialProps} />
      </mesh>

      {cloudsTexture ? (
        <mesh ref={cloudsRef} scale={1.01} renderOrder={1}>
          <sphereGeometry args={[1, 128, 128]} />
          <meshBasicMaterial
            map={cloudsTexture}
            transparent
            opacity={0.25}
            depthWrite={false}
            blending={AdditiveBlending}
          />
        </mesh>
      ) : null}

      <Atmosphere />

      <Markers markers={markers} selected={selected} onSelect={onSelectMarker} />
    </group>
  );
}
