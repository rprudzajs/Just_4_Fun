import { useMemo } from 'react';
import { AdditiveBlending, BackSide, Color, MeshBasicMaterial } from 'three';

function Atmosphere({ radius = 2.08, color = '#74baff', opacity = 0.25 }) {
  const material = useMemo(
    () =>
      new MeshBasicMaterial({
        color: new Color(color),
        transparent: true,
        opacity,
        blending: AdditiveBlending,
        depthWrite: false
      }),
    [color, opacity]
  );

  return (
    <mesh scale={radius} renderOrder={-1}>
      <sphereGeometry args={[1, 96, 96]} />
      <primitive object={material} attach="material" side={BackSide} />
    </mesh>
  );
}

export default Atmosphere;
