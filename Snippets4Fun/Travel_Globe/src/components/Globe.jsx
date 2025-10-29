import { useFrame } from '@react-three/fiber';
import { Html } from '@react-three/drei';
import { useEffect, useMemo, useRef, useState } from 'react';
import {
  AdditiveBlending,
  BackSide,
  ClampToEdgeWrapping,
  Color,
  LinearFilter,
  MeshBasicMaterial,
  SRGBColorSpace,
  TextureLoader
} from 'three';

const DAY_TEXTURE = 'https://threejsfundamentals.org/threejs/resources/images/earth-day.jpg';
const NIGHT_TEXTURE = 'https://threejsfundamentals.org/threejs/resources/images/earth-night.jpg';
const CLOUD_TEXTURE = 'https://threejsfundamentals.org/threejs/resources/images/fair_clouds_4k.png';

const MARKER_RADIUS = 2.05;

function latLonToVector3(lat, lon, radius = MARKER_RADIUS) {
  const phi = (90 - lat) * (Math.PI / 180);
  const theta = (lon + 180) * (Math.PI / 180);

  const x = -radius * Math.sin(phi) * Math.cos(theta);
  const z = radius * Math.sin(phi) * Math.sin(theta);
  const y = radius * Math.cos(phi);

  return [x, y, z];
}

function useEarthTextures() {
  const [textures, setTextures] = useState({ day: null, night: null, clouds: null });

  useEffect(() => {
    let cancelled = false;
    const loader = new TextureLoader();
    loader.setCrossOrigin('anonymous');

    function configure(texture) {
      if (!texture) return texture;
      texture.wrapS = ClampToEdgeWrapping;
      texture.wrapT = ClampToEdgeWrapping;
      texture.minFilter = LinearFilter;
      texture.magFilter = LinearFilter;
      texture.colorSpace = SRGBColorSpace;
      texture.needsUpdate = true;
      return texture;
    }

    Promise.all([
      new Promise((resolve) => loader.load(DAY_TEXTURE, (t) => resolve(configure(t)), undefined, () => resolve(null))),
      new Promise((resolve) => loader.load(NIGHT_TEXTURE, (t) => resolve(configure(t)), undefined, () => resolve(null))),
      new Promise((resolve) => loader.load(CLOUD_TEXTURE, (t) => resolve(configure(t)), undefined, () => resolve(null)))
    ]).then(([day, night, clouds]) => {
      if (!cancelled) {
        setTextures({ day, night, clouds });
      }
    });

    return () => {
      cancelled = true;
    };
  }, []);

  return textures;
}

function Atmosphere() {
  const material = useMemo(
    () =>
      new MeshBasicMaterial({
        color: new Color('#6fb8ff'),
        transparent: true,
        opacity: 0.22,
        blending: AdditiveBlending,
        depthWrite: false
      }),
    []
  );

  return (
    <mesh scale={2.2} renderOrder={-1}>
      <sphereGeometry args={[1, 128, 128]} />
      <primitive object={material} side={BackSide} />
    </mesh>
  );
}

function Marker({ marker, isActive, onSelect }) {
  const position = useMemo(
    () => latLonToVector3(marker.coordinates.lat, marker.coordinates.lon),
    [marker.coordinates.lat, marker.coordinates.lon]
  );

  return (
    <group
      position={position}
      onClick={(event) => {
        event.stopPropagation();
        onSelect(marker);
      }}
      onPointerOver={() => {
        if (typeof document !== 'undefined') document.body.style.cursor = 'pointer';
      }}
      onPointerOut={() => {
        if (typeof document !== 'undefined') document.body.style.cursor = 'default';
      }}
    >
      <mesh scale={isActive ? 1.3 : 1}>
        <sphereGeometry args={[0.03, 32, 32]} />
        <meshBasicMaterial color={marker.color} toneMapped={false} />
      </mesh>
      <mesh scale={isActive ? 0.28 : 0.22}>
        <sphereGeometry args={[1, 32, 32]} />
        <meshBasicMaterial color={marker.color} transparent opacity={0.4} toneMapped={false} />
      </mesh>
      <Html distanceFactor={12} transform position={[0, 0.18, 0]}>
        <div
          className={`pointer-events-none rounded-full border px-4 py-1 text-xs font-medium uppercase tracking-[0.25em] ${
            isActive ? 'border-white/60 bg-white/20 text-white' : 'border-white/10 bg-white/5 text-white/70'
          }`}
        >
          {marker.name}
        </div>
      </Html>
    </group>
  );
}

export default function Globe({ lightingMode = 'day', markers = [], selected, onSelectMarker }) {
  const groupRef = useRef();
  const cloudsRef = useRef();
  const { day, night, clouds } = useEarthTextures();

  const materialProps = useMemo(() => {
    const baseColor = lightingMode === 'night' ? '#09152b' : '#9bd3ff';
    const emissive = lightingMode === 'night' ? '#1a2f6b' : '#000000';
    return {
      color: baseColor,
      map: lightingMode === 'night' ? night ?? day : day ?? null,
      emissive,
      emissiveMap: lightingMode === 'night' ? night ?? null : null,
      emissiveIntensity: lightingMode === 'night' ? 0.45 : 0.05,
      roughness: 0.85,
      metalness: 0.1
    };
  }, [day, night, lightingMode]);

  useFrame((_, delta) => {
    if (groupRef.current) {
      groupRef.current.rotation.y += delta * 0.2;
    }

    if (cloudsRef.current) {
      cloudsRef.current.rotation.y += delta * 0.1;
    }
  });

  return (
    <group ref={groupRef} scale={2.1} position={[0, -0.2, 0]}>
      <mesh>
        <sphereGeometry args={[1, 128, 128]} />
        <meshStandardMaterial attach="material" {...materialProps} />
      </mesh>

      {clouds ? (
        <mesh ref={cloudsRef} scale={1.01}>
          <sphereGeometry args={[1, 128, 128]} />
          <meshBasicMaterial map={clouds} transparent opacity={0.25} depthWrite={false} />
        </mesh>
      ) : null}

      <Atmosphere />

      <group>
        {markers.map((marker) => (
          <Marker
            key={marker.id}
            marker={marker}
            isActive={selected && selected.id === marker.id}
            onSelect={onSelectMarker}
          />
        ))}
      </group>
    </group>
  );
}
