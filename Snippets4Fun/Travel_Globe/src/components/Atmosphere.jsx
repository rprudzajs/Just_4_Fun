import { useMemo } from 'react';
import { AdditiveBlending, BackSide, ShaderMaterial, Color } from 'three';
import { extend, useFrame } from '@react-three/fiber';

class AtmosphereMaterial extends ShaderMaterial {
  constructor() {
    super({
      transparent: true,
      blending: AdditiveBlending,
      depthWrite: false,
      uniforms: {
        glowColor: { value: new Color('#7bcfff') },
        intensity: { value: 0.8 },
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
          float pulse = (sin(time * 0.35) * 0.5 + 0.5) * 0.15;
          gl_FragColor = vec4(glowColor * (glow * intensity + pulse), (glow * 0.6));
        }
      `
    });
  }
}

extend({ AtmosphereMaterial });

function Atmosphere() {
  const material = useMemo(() => new AtmosphereMaterial(), []);

  useFrame((_, delta) => {
    material.uniforms.time.value += delta;
  });

  return (
    <mesh scale={1.06}>
      <sphereGeometry args={[2, 128, 128]} />
      <atmosphereMaterial attach="material" side={BackSide} />
    </mesh>
  );
}

export default Atmosphere;
