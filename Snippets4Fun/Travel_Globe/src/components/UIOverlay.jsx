import { motion } from 'framer-motion';
import { useMemo } from 'react';

const fadeIn = {
  initial: { opacity: 0, y: 24 },
  animate: { opacity: 1, y: 0 },
  transition: { duration: 0.7, ease: 'easeOut' }
};

function UIOverlay({ selected, markers, onSelectMarker, lightingMode, onLightingModeChange }) {
  const heroCopy = useMemo(
    () => [
      'Dream in Motion',
      'Curated journeys, luminous cities, cinematic horizons.'
    ],
    []
  );

  return (
    <div className="pointer-events-none absolute inset-0 flex flex-col justify-between p-12">
      <motion.header
        className="pointer-events-none flex flex-col gap-3"
        initial={fadeIn.initial}
        animate={fadeIn.animate}
        transition={{ ...fadeIn.transition, delay: 0.1 }}
      >
        <span className="text-sm uppercase tracking-[0.45em] text-white/60">Wanderworld Studio</span>
        <h1 className="font-display text-6xl font-semibold text-white drop-shadow-[0_20px_45px_rgba(23,34,70,0.55)]">
          {heroCopy[0]}
        </h1>
        <p className="max-w-xl text-lg text-white/70">{heroCopy[1]}</p>
      </motion.header>

      <motion.div
        className="pointer-events-auto ml-auto flex max-w-md flex-col gap-6 rounded-3xl border border-white/15 bg-white/10 p-8 backdrop-blur-2xl glass-shadow"
        initial={fadeIn.initial}
        animate={fadeIn.animate}
        transition={{ ...fadeIn.transition, delay: 0.25 }}
      >
        <div className="flex items-center justify-between">
          <div>
            <p className="text-xs uppercase tracking-[0.4em] text-white/60">Featured Journey</p>
            <h2 className="font-display text-3xl font-semibold text-white">{selected.name}</h2>
          </div>
          <div className="flex gap-2">
            {['day', 'night'].map((mode) => (
              <button
                key={mode}
                type="button"
                onClick={() => onLightingModeChange(mode)}
                className={`pointer-events-auto rounded-full border px-4 py-2 text-xs font-medium uppercase tracking-[0.2em] transition-colors duration-300 ${
                  lightingMode === mode
                    ? 'border-white/70 bg-white/20 text-white shadow-glass'
                    : 'border-white/20 bg-white/5 text-white/70 hover:border-white/40 hover:text-white'
                }`}
              >
                {mode === 'day' ? 'Day' : 'Night'}
              </button>
            ))}
          </div>
        </div>
        <p className="text-base text-white/70">{selected.tagline}</p>

        <div className="flex flex-wrap gap-3">
          {markers.map((marker) => (
            <button
              key={marker.id}
              type="button"
              onClick={() => onSelectMarker(marker)}
              className={`pointer-events-auto rounded-full border px-4 py-2 text-xs uppercase tracking-[0.25em] transition-all duration-300 ${
                selected.id === marker.id
                  ? 'border-white/60 bg-white/20 text-white shadow-luxe'
                  : 'border-white/10 bg-white/5 text-white/60 hover:border-white/40 hover:text-white'
              }`}
            >
              {marker.name}
            </button>
          ))}
        </div>
      </motion.div>
    </div>
  );
}

export default UIOverlay;
