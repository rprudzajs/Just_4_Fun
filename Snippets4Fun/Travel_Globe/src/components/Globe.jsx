import { useFrame, useLoader } from '@react-three/fiber';
import { useEffect, useMemo, useRef } from 'react';
import { ClampToEdgeWrapping, Color, LinearFilter, SRGBColorSpace, TextureLoader } from 'three';

import { TEXTURE_SOURCES } from '../config/textureSources';

const TEXTURE_URLS = [
  TEXTURE_SOURCES.day,
  TEXTURE_SOURCES.night,
  TEXTURE_SOURCES.normal,
  TEXTURE_SOURCES.clouds
];

function prepareTexture(texture, { linear = false } = {}) {
  if (!texture) return texture;
  if (!linear) {
    texture.colorSpace = SRGBColorSpace;
  }
  texture.wrapS = ClampToEdgeWrapping;
  texture.wrapT = ClampToEdgeWrapping;
  texture.anisotropy = 8;
  texture.minFilter = LinearFilter;
  texture.magFilter = LinearFilter;
  texture.needsUpdate = true;
  return texture;
}

function Globe({ lightingMode }) {
  const globeMaterial = useRef();
  const cloudLayer = useRef();

  const [dayMap, nightMap, normalMap, cloudsMap] = useLoader(
    TextureLoader,
    TEXTURE_URLS,
    (loader) => loader.setCrossOrigin('anonymous')
  );

  useEffect(() => {
    prepareTexture(dayMap);
    prepareTexture(nightMap);
    prepareTexture(cloudsMap);
    prepareTexture(normalMap, { linear: true });
  }, [dayMap, nightMap, normalMap, cloudsMap]);

  const materialProps = useMemo(() => {
    const base = {
      normalMap,
      clearcoat: 0.45,
      clearcoatRoughness: 0.4,
      metalness: 0.25,
      roughness: 0.75,
      envMapIntensity: 1.1
    };

    if (lightingMode === 'night') {
      return {
        ...base,
        map: nightMap,
        emissive: new Color('#3355ff'),
        emissiveMap: nightMap,
        emissiveIntensity: 1.25,
        metalness: 0.35,
        roughness: 0.9
      };
    }

    return {
      ...base,
      map: dayMap,
      emissive: new Color('#0b1d35'),
      emissiveIntensity: 0.08,
      metalness: 0.2,
      roughness: 0.65
    };
  }, [dayMap, nightMap, lightingMode, normalMap]);

  useFrame((_, delta) => {
    if (cloudLayer.current) {
      cloudLayer.current.rotation.y += delta * 0.02;
    }

    if (globeMaterial.current && lightingMode === 'night') {
      const pulse = Math.sin(Date.now() * 0.0004) * 0.2 + 1.0;
      globeMaterial.current.emissiveIntensity = 1.05 + pulse * 0.2;
    }
  });

  return (
    <group scale={2}>
      <mesh castShadow receiveShadow>
        <sphereGeometry args={[1, 256, 256]} />
        <meshPhysicalMaterial ref={globeMaterial} attach="material" {...materialProps} />
      </mesh>

      {cloudsMap ? (
        <mesh ref={cloudLayer} scale={1.01} renderOrder={1}>
          <sphereGeometry args={[1, 256, 256]} />
          <meshStandardMaterial
            map={cloudsMap}
            transparent
            opacity={0.35}
            depthWrite={false}
            toneMapped={false}
          />
        </mesh>
      ) : null}
    </group>
  );
}

export default Globe;
