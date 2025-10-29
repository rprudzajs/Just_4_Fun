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
  MeshStandardMaterial,
  SRGBColorSpace,
  ShaderMaterial,
  TextureLoader
} from 'three';

import { TEXTURE_SOURCES } from '../config/textureSources';

const MARKER_RADIUS = 2.05;

function latLonToVector3(lat, lon, radius = MARKER_RADIUS) {
  const phi = (90 - lat) * (Math.PI / 180);
  const theta = (lon + 180) * (Math.PI / 180);

  const x = -radius * Math.sin(phi) * Math.cos(theta);
  const z = radius * Math.sin(phi) * Math.sin(theta);
  const y = radius * Math.cos(phi);

  return [x, y, z];
}

function loadTexture(loader, url) {
  return new Promise((resolve) => {
    if (!url) {
      resolve(null);
      return;
    }

    loader.load(
      url,
      (texture) => {
        texture.wrapS = ClampToEdgeWrapping;
        texture.wrapT = ClampToEdgeWrapping;
        texture.anisotropy = 8;
        texture.minFilter = LinearFilter;
        texture.magFilter = LinearFilter;
        texture.colorSpace = SRGBColorSpace;
        texture.needsUpdate = true;
        resolve(texture);
      },
      undefined,
      () => resolve(null)
    );
  });
}

function useEarthTextures() {
  const [textures, setTextures] = useState({ day: null, night: null, clouds: null });

  useEffect(() => {
    let cancelled = false;
    const loader = new TextureLoader();
    loader.setCrossOrigin('anonymous');

    async function fetchTextures() {
      const [day, night, clouds] = await Promise.all([
        loadTexture(loader, TEXTURE_SOURCES.day),
        loadTexture(loader, TEXTURE_SOURCES.night),
        loadTexture(loader, TEXTURE_SOURCES.clouds)
      ]);

      if (!cancelled) {
        setTextures({ day, night, clouds });
      }
    }

    fetchTextures();

    return () => {
      cancelled = true;
    };
  }, []);

  return textures;
}

function AtmosphereShell() {
  const materialRef = useRef();
  const fallbackMaterial = useMemo(() => new MeshBasicMaterial({ transparent: true, opacity: 0.18 }), []);

  useEffect(() => {
    materialRef.current = new ShaderMaterial({
      transparent: true,
      blending: AdditiveBlending,
      depthWrite: false,
      uniforms: {
        glowColor: { value: new Color('#6fb9ff') },
        intensity: { value: 0.65 },
        time: { value: 0 }
      },
      vertexShader: /* glsl */ `
        varying vec3 vNormal;
        void main() {
          vNormal = normalize(normalMatrix * normal);
          gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
        }
      `,
      fragmentShader: /* glsl */ `
        varying vec3 vNormal;
        uniform vec3 glowColor;
        uniform float intensity;
        uniform float time;

        void main() {
          float glow = pow(0.6 - dot(vNormal, vec3(0.0, 0.0, 1.0)), 3.0);
          float pulse = (sin(time * 0.3) * 0.5 + 0.5) * 0.2;
          gl_FragColor = vec4(glowColor * (glow * intensity + pulse), glow * 0.55);
        }
      `
    });

    return () => {
      if (materialRef.current) {
        materialRef.current.dispose();
        materialRef.current = null;
      }
    };
  }, []);

  useFrame((_, delta) => {
    if (materialRef.current) {
      materialRef.current.uniforms.time.value += delta;
    }
  });

  return (
    <mesh scale={2.2} renderOrder={-1}>
      <sphereGeometry args={[1, 128, 128]} />
      <primitive object={materialRef.current ?? fallbackMaterial} side={BackSide} />
    </mesh>
  );
}

function Marker({ marker, isActive, onSelect }) {
  const position = useMemo(
    () => latLonToVector3(marker.coordinates.lat, marker.coordinates.lon),
    [marker.coordinates.lat, marker.coordinates.lon]
  );

  const auraColor = useMemo(() => new Color(marker.color).convertSRGBToLinear(), [marker.color]);

  return (
    <group
      position={position}
      onClick={(event) => {
        event.stopPropagation();
        onSelect(marker);
      }}
      onPointerOver={() => {
        if (typeof document !== 'undefined') {
          document.body.style.cursor = 'pointer';
        }
      }}
      onPointerOut={() => {
        if (typeof document !== 'undefined') {
          document.body.style.cursor = 'default';
        }
      }}
    >
      <mesh scale={isActive ? 1.25 : 1}>
        <sphereGeometry args={[0.03, 32, 32]} />
        <meshBasicMaterial color={marker.color} toneMapped={false} />
      </mesh>
      <mesh scale={isActive ? 0.28 : 0.22}>
        <sphereGeometry args={[1, 32, 32]} />
        <meshBasicMaterial color={auraColor} transparent opacity={0.4} toneMapped={false} />
      </mesh>
      <Html distanceFactor={12} transform position={[0, 0.18, 0]}>
        <div
          className={`pointer-events-none rounded-full border px-4 py-1 text-xs font-medium uppercase tracking-[0.25em] ${
            isActive ? 'border-white/50 bg-white/20 text-white' : 'border-white/10 bg-white/5 text-white/70'
          }`}
        >
          {marker.name}
        </div>
      </Html>
    </group>
  );
}

function Globe({ lightingMode, markers, selected, onSelectMarker }) {
  const groupRef = useRef();
  const cloudsRef = useRef();
  const { day, night, clouds } = useEarthTextures();

  const earthMaterial = useMemo(() => {
    return new MeshStandardMaterial({
      color: '#0a1f35',
      roughness: 0.65,
      metalness: 0.25,
      emissive: new Color('#081831'),
      emissiveIntensity: 0.18
    });
  }, []);

  useEffect(() => {
    if (!earthMaterial) return;

    if (lightingMode === 'night') {
      earthMaterial.color = new Color('#050f21');
      earthMaterial.emissive = new Color('#0d1f4a');
      earthMaterial.emissiveIntensity = night ? 0.9 : 0.25;
      earthMaterial.map = night ?? day ?? null;
      earthMaterial.emissiveMap = night ?? null;
    } else {
      earthMaterial.color = new Color('#0a1f35');
      earthMaterial.emissive = new Color('#0b1d35');
      earthMaterial.emissiveIntensity = 0.18;
      earthMaterial.map = day ?? null;
      earthMaterial.emissiveMap = null;
    }

    earthMaterial.needsUpdate = true;
  }, [day, night, lightingMode, earthMaterial]);

  useFrame((_, delta) => {
    if (groupRef.current) {
      groupRef.current.rotation.y += delta * 0.06;
    }

    if (cloudsRef.current) {
      cloudsRef.current.rotation.y += delta * 0.02;
    }
  });

  return (
    <group ref={groupRef} scale={2} position={[0, -0.25, 0]}>
      <mesh>
        <sphereGeometry args={[1, 128, 128]} />
        <primitive object={earthMaterial} attach="material" />
      </mesh>

      {clouds ? (
        <mesh ref={cloudsRef} scale={1.01}>
          <sphereGeometry args={[1, 128, 128]} />
          <meshBasicMaterial map={clouds} transparent opacity={0.25} depthWrite={false} />
        </mesh>
      ) : null}

      <AtmosphereShell />

      <group>
        {markers.map((marker) => (
          <Marker key={marker.id} marker={marker} isActive={selected.id === marker.id} onSelect={onSelectMarker} />
        ))}
      </group>
    </group>
  );
}

export default Globe;
