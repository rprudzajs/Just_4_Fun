import { useMemo } from 'react';
import { Color } from 'three';
import { Html } from '@react-three/drei';
import { motion } from 'framer-motion';

const EARTH_RADIUS = 2;

function latLonToVector3(lat, lon, radius = EARTH_RADIUS) {
  const phi = (90 - lat) * (Math.PI / 180);
  const theta = (lon + 180) * (Math.PI / 180);

  const x = -radius * Math.sin(phi) * Math.cos(theta);
  const z = radius * Math.sin(phi) * Math.sin(theta);
  const y = radius * Math.cos(phi);

  return [x, y, z];
}

function Marker({ marker, isActive, onSelect }) {
  const position = useMemo(
    () => latLonToVector3(marker.coordinates.lat, marker.coordinates.lon),
    [marker.coordinates.lat, marker.coordinates.lon]
  );

  const aura = useMemo(() => new Color(marker.color).convertSRGBToLinear(), [marker.color]);

  return (
    <group
      position={position}
      onClick={() => onSelect(marker)}
      onPointerOver={() => (document.body.style.cursor = 'pointer')}
      onPointerOut={() => (document.body.style.cursor = 'default')}
    >
      <mesh scale={isActive ? 1.2 : 1}>
        <sphereGeometry args={[0.02, 32, 32]} />
        <meshBasicMaterial color={marker.color} toneMapped={false} />
      </mesh>
      <mesh scale={isActive ? 0.22 : 0.18}>
        <sphereGeometry args={[1, 32, 32]} />
        <meshBasicMaterial color={aura} transparent opacity={0.45} toneMapped={false} />
      </mesh>
      <Html distanceFactor={12} transform position={[0, 0.15, 0]}>
        <motion.div
          initial={{ opacity: 0, y: 6 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.4, ease: 'easeOut' }}
          className={`pointer-events-none rounded-full border border-white/10 px-4 py-1 text-xs font-medium uppercase tracking-[0.3em] ${
            isActive ? 'bg-white/20 text-white' : 'bg-white/10 text-white/70'
          }`}
        >
          {marker.name}
        </motion.div>
      </Html>
    </group>
  );
}

function Markers({ markers, selected, onSelect }) {
  return (
    <group>
      {markers.map((marker) => (
        <Marker key={marker.id} marker={marker} isActive={selected.id === marker.id} onSelect={onSelect} />
      ))}
    </group>
  );
}

export default Markers;
