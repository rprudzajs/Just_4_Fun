import { useEffect, useRef } from 'react';
import { OrbitControls } from '@react-three/drei';
import { useFrame, useThree } from '@react-three/fiber';
import { Vector3 } from 'three';

const MARKER_RADIUS = 2;

function latLonToVector3(lat, lon, radius = MARKER_RADIUS) {
  const phi = (90 - lat) * (Math.PI / 180);
  const theta = (lon + 180) * (Math.PI / 180);

  const x = -radius * Math.sin(phi) * Math.cos(theta);
  const z = radius * Math.sin(phi) * Math.sin(theta);
  const y = radius * Math.cos(phi);

  return new Vector3(x, y, z);
}

function CameraController({ focusMarker }) {
  const controlsRef = useRef();
  const { camera } = useThree();
  const targetPosition = useRef(new Vector3(0, 0, 0));
  const desiredPosition = useRef(camera.position.clone());

  useEffect(() => {
    if (!focusMarker) return;
    const focusPoint = latLonToVector3(focusMarker.coordinates.lat, focusMarker.coordinates.lon, 1.8);
    targetPosition.current.copy(focusPoint);
    const offset = focusPoint.clone().normalize().multiplyScalar(2.8);
    desiredPosition.current.copy(offset.add(new Vector3(0.1, 0.1, 0.1)));
  }, [focusMarker]);

  useFrame(() => {
    if (!controlsRef.current) return;
    camera.position.lerp(desiredPosition.current, 0.04);
    controlsRef.current.target.lerp(targetPosition.current, 0.08);
    controlsRef.current.update();
  });

  return (
    <OrbitControls
      ref={controlsRef}
      enablePan={false}
      minPolarAngle={Math.PI / 2.8}
      maxPolarAngle={(Math.PI / 2) * 1.25}
      enableZoom
      zoomSpeed={0.6}
      rotateSpeed={0.6}
      dampingFactor={0.15}
      enableDamping
      autoRotate
      autoRotateSpeed={0.4}
    />
  );
}

export default CameraController;
