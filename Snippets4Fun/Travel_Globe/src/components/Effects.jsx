import { EffectComposer, Bloom, DepthOfField, ToneMapping } from '@react-three/postprocessing';
import { BlendFunction, ToneMappingMode } from 'postprocessing';

function Effects() {
  return (
    <EffectComposer>
      <Bloom
        mipmapBlur
        intensity={1.2}
        luminanceThreshold={0.85}
        luminanceSmoothing={0.2}
        blendFunction={BlendFunction.SCREEN}
      />
      <DepthOfField focusDistance={0.01} focalLength={0.25} bokehScale={4.5} height={480} />
      <ToneMapping mode={ToneMappingMode.ACES_FILMIC} />
    </EffectComposer>
  );
}

export default Effects;
