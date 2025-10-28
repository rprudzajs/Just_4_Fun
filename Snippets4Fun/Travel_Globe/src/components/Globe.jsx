import { extend, useFrame } from '@react-three/fiber';
import {
  CanvasTexture,
  LinearFilter,
  RepeatWrapping,
  ShaderMaterial,
  Texture,
  TextureLoader,
  Vector3,
  SRGBColorSpace
} from 'three';
import { useEffect, useMemo, useRef } from 'react';

import { TEXTURE_SOURCES } from '../config/textureSources';

const vertexShader = /* glsl */ `
  varying vec2 vUv;
  varying vec3 vNormal;
  varying vec3 vWorldPosition;

  void main() {
    vUv = uv;
    vec4 worldPosition = modelMatrix * vec4(position, 1.0);
    vWorldPosition = worldPosition.xyz;
    vNormal = normalize(normalMatrix * normal);
    gl_Position = projectionMatrix * viewMatrix * worldPosition;
  }
`;

const fragmentShader = /* glsl */ `
  precision mediump float;
  #extension GL_OES_standard_derivatives : enable;

  uniform sampler2D dayMap;
  uniform sampler2D nightMap;
  uniform sampler2D normalMap;
  uniform sampler2D specularMap;
  uniform vec3 lightDirection;
  uniform float nightBoost;
  uniform float specularStrength;
  uniform float glossiness;

  varying vec2 vUv;
  varying vec3 vNormal;
  varying vec3 vWorldPosition;

  void main() {
    vec3 nMap = texture2D(normalMap, vUv).rgb;
    nMap = normalize(nMap * 2.0 - 1.0);

    vec3 tangentX = normalize(dFdx(vWorldPosition));
    vec3 tangentY = normalize(dFdy(vWorldPosition));
    vec3 bumpedNormal = normalize(mat3(tangentX, tangentY, normalize(vNormal)) * nMap);

    vec3 lightDir = normalize(lightDirection);
    float diffuse = clamp(dot(bumpedNormal, lightDir), -1.0, 1.0);

    vec3 dayColor = texture2D(dayMap, vUv).rgb;
    vec3 nightColor = texture2D(nightMap, vUv).rgb * nightBoost;

    float blend = smoothstep(-0.35, 0.4, diffuse);
    vec3 baseColor = mix(nightColor, dayColor, blend);

    vec3 viewDir = normalize(cameraPosition - vWorldPosition);
    vec3 reflectDir = reflect(-lightDir, bumpedNormal);
    float spec = pow(max(dot(viewDir, reflectDir), 0.0), glossiness);
    float specMask = texture2D(specularMap, vUv).r;

    vec3 color = baseColor + specularStrength * spec * specMask * vec3(1.0);
    gl_FragColor = vec4(color, 1.0);
  }
`;

class LuxeGlobeMaterial extends ShaderMaterial {
  constructor(textures) {
    super({
      uniforms: {
        dayMap: { value: textures.day },
        nightMap: { value: textures.night },
        normalMap: { value: textures.normal },
        specularMap: { value: textures.specular },
        lightDirection: { value: new Vector3(1.0, 0.2, 1.0).normalize() },
        nightBoost: { value: 1.6 },
        specularStrength: { value: 0.75 },
        glossiness: { value: 35.0 }
      },
      vertexShader,
      fragmentShader,
      transparent: false
    });
  }
}

extend({ LuxeGlobeMaterial });

const UNIFORM_KEYS = {
  day: 'dayMap',
  night: 'nightMap',
  normal: 'normalMap',
  specular: 'specularMap'
};

const createCanvasTexture = (drawer) => {
  if (typeof document === 'undefined') {
    const texture = new Texture();
    texture.wrapS = RepeatWrapping;
    texture.wrapT = RepeatWrapping;
    texture.minFilter = LinearFilter;
    texture.magFilter = LinearFilter;
    texture.colorSpace = SRGBColorSpace;
    return texture;
  }

  const canvas = document.createElement('canvas');
  canvas.width = 1024;
  canvas.height = 512;
  const ctx = canvas.getContext('2d');

  drawer(ctx, canvas);

  const texture = new CanvasTexture(canvas);
  texture.wrapS = RepeatWrapping;
  texture.wrapT = RepeatWrapping;
  texture.anisotropy = 4;
  texture.minFilter = LinearFilter;
  texture.magFilter = LinearFilter;
  texture.colorSpace = SRGBColorSpace;
  texture.needsUpdate = true;
  return texture;
};

const createFallbackTextures = () => {
  const day = createCanvasTexture((ctx, canvas) => {
    const gradient = ctx.createLinearGradient(0, 0, canvas.width, canvas.height);
    gradient.addColorStop(0.0, '#0c2d57');
    gradient.addColorStop(0.5, '#126872');
    gradient.addColorStop(1.0, '#1b9aaa');
    ctx.fillStyle = gradient;
    ctx.fillRect(0, 0, canvas.width, canvas.height);

    ctx.globalAlpha = 0.65;
    ctx.fillStyle = '#7bc06f';
    ctx.beginPath();
    ctx.moveTo(canvas.width * 0.2, canvas.height * 0.4);
    ctx.bezierCurveTo(
      canvas.width * 0.35,
      canvas.height * 0.2,
      canvas.width * 0.45,
      canvas.height * 0.6,
      canvas.width * 0.32,
      canvas.height * 0.7
    );
    ctx.bezierCurveTo(
      canvas.width * 0.28,
      canvas.height * 0.8,
      canvas.width * 0.15,
      canvas.height * 0.7,
      canvas.width * 0.2,
      canvas.height * 0.4
    );
    ctx.fill();

    ctx.beginPath();
    ctx.moveTo(canvas.width * 0.65, canvas.height * 0.35);
    ctx.bezierCurveTo(
      canvas.width * 0.75,
      canvas.height * 0.25,
      canvas.width * 0.82,
      canvas.height * 0.4,
      canvas.width * 0.78,
      canvas.height * 0.5
    );
    ctx.bezierCurveTo(
      canvas.width * 0.72,
      canvas.height * 0.7,
      canvas.width * 0.6,
      canvas.height * 0.65,
      canvas.width * 0.62,
      canvas.height * 0.45
    );
    ctx.fill();

    ctx.globalAlpha = 0.2;
    ctx.fillStyle = '#ffffff';
    for (let i = 0; i < 60; i += 1) {
      const x = Math.random() * canvas.width;
      const y = Math.random() * canvas.height;
      const r = 2 + Math.random() * 3;
      const radial = ctx.createRadialGradient(x, y, 0, x, y, r);
      radial.addColorStop(0, 'rgba(255,255,255,0.45)');
      radial.addColorStop(1, 'rgba(255,255,255,0)');
      ctx.fillStyle = radial;
      ctx.beginPath();
      ctx.arc(x, y, r, 0, Math.PI * 2);
      ctx.fill();
    }
    ctx.globalAlpha = 1;
  });

  const night = createCanvasTexture((ctx, canvas) => {
    const gradient = ctx.createLinearGradient(0, 0, canvas.width, canvas.height);
    gradient.addColorStop(0.0, '#030712');
    gradient.addColorStop(0.5, '#0b1033');
    gradient.addColorStop(1.0, '#140f34');
    ctx.fillStyle = gradient;
    ctx.fillRect(0, 0, canvas.width, canvas.height);

    ctx.fillStyle = 'rgba(240,188,82,0.9)';
    for (let i = 0; i < 120; i += 1) {
      const x = Math.random() * canvas.width;
      const y = Math.random() * canvas.height;
      ctx.globalAlpha = 0.2 + Math.random() * 0.6;
      ctx.fillRect(x, y, 2, 2);
    }
    ctx.globalAlpha = 1;
  });

  const normal = createCanvasTexture((ctx, canvas) => {
    const gradient = ctx.createLinearGradient(0, 0, canvas.width, canvas.height);
    gradient.addColorStop(0.0, '#7f7fff');
    gradient.addColorStop(0.5, '#7fbfff');
    gradient.addColorStop(1.0, '#7fffff');
    ctx.fillStyle = gradient;
    ctx.fillRect(0, 0, canvas.width, canvas.height);
  });

  const specular = createCanvasTexture((ctx, canvas) => {
    const gradient = ctx.createLinearGradient(0, 0, canvas.width, canvas.height);
    gradient.addColorStop(0.0, 'rgba(20, 20, 30, 0.3)');
    gradient.addColorStop(0.6, 'rgba(40, 40, 60, 0.05)');
    gradient.addColorStop(1.0, 'rgba(250, 250, 250, 0.8)');
    ctx.fillStyle = gradient;
    ctx.fillRect(0, 0, canvas.width, canvas.height);
  });

  return { day, night, normal, specular };
};

const FALLBACK_TEXTURES = createFallbackTextures();

function Globe({ lightingMode }) {
  const globeRef = useRef();
  const materialRef = useRef();
  const loader = useMemo(() => {
    const textureLoader = new TextureLoader();
    textureLoader.setCrossOrigin('anonymous');
    return textureLoader;
  }, []);

  const material = useMemo(() => {
    const luxeMaterial = new LuxeGlobeMaterial(FALLBACK_TEXTURES);
    materialRef.current = luxeMaterial;
    return luxeMaterial;
  }, []);

  useEffect(() => {
    let cancelled = false;
    const entries = Object.entries(TEXTURE_SOURCES);

    entries.forEach(([key, url]) => {
      loader.load(
        url,
        (texture) => {
          if (cancelled) return;
          texture.wrapS = RepeatWrapping;
          texture.wrapT = RepeatWrapping;
          texture.anisotropy = 8;
          texture.minFilter = LinearFilter;
          texture.magFilter = LinearFilter;
          texture.colorSpace = SRGBColorSpace;
          texture.needsUpdate = true;

          const materialInstance = materialRef.current;
          if (materialInstance && UNIFORM_KEYS[key]) {
            materialInstance.uniforms[UNIFORM_KEYS[key]].value = texture;
          }
        },
        undefined,
        () => {
          console.warn(`Failed to load ${key} texture from ${url}. Falling back to procedural texture.`);
        }
      );
    });

    return () => {
      cancelled = true;
    };
  }, [loader]);

  useFrame((state, delta) => {
    if (!globeRef.current || !materialRef.current) return;

    globeRef.current.rotation.y += delta * 0.08;
    const orbit = state.clock.getElapsedTime() * 0.12;
    const target = new Vector3(Math.cos(orbit) * 0.8, 0.2, Math.sin(orbit) * 0.8);
    materialRef.current.uniforms.lightDirection.value.lerp(target.normalize(), 0.05);

    if (lightingMode === 'night') {
      materialRef.current.uniforms.nightBoost.value = 1.9;
      materialRef.current.uniforms.specularStrength.value = 0.55;
    } else {
      materialRef.current.uniforms.nightBoost.value = 1.4;
      materialRef.current.uniforms.specularStrength.value = 0.75;
    }
  });

  return (
    <group ref={globeRef} scale={2}>
      <mesh>
        <sphereGeometry args={[1, 256, 256]} />
        <primitive object={material} attach="material" />
      </mesh>
    </group>
  );
}

export default Globe;
