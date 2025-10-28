import { OrbitControls } from '@react-three/drei';

function CameraController() {
  return (
    <OrbitControls
      enablePan={false}
      enableZoom
      zoomSpeed={0.6}
      minDistance={4.2}
      maxDistance={9}
      minPolarAngle={Math.PI / 3.2}
      maxPolarAngle={(Math.PI / 2) * 1.35}
      enableDamping
      dampingFactor={0.12}
      rotateSpeed={0.45}
      autoRotate
      autoRotateSpeed={0.25}
    />
  );
}

export default CameraController;
