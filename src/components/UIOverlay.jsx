export default function UIOverlay({
  selected,
  markers,
  onSelectMarker,
  lightingMode,
  onLightingModeChange
}) {
  return (
    <div className="absolute bottom-10 right-10 z-[40] bg-white/5 border border-white/10 rounded-2xl backdrop-blur-md p-6 text-white w-[320px]">
      <p className="text-xs uppercase tracking-[0.2em] text-gray-400 mb-2">
        Featured Journey
      </p>

      <h2 className="text-2xl font-semibold mb-1">{selected.name}</h2>
      <p className="text-sm text-gray-300 mb-4">{selected.tagline}</p>

      <div className="flex gap-2 mb-4">
        <button
          className={`px-3 py-1 text-xs rounded-full border ${
            lightingMode === 'day'
              ? 'bg-white text-black border-white'
              : 'border-white/40 text-white/80 hover:border-white/80'
          }`}
          onClick={() => onLightingModeChange('day')}
        >
          Day
        </button>
        <button
          className={`px-3 py-1 text-xs rounded-full border ${
            lightingMode === 'night'
              ? 'bg-white text-black border-white'
              : 'border-white/40 text-white/80 hover:border-white/80'
          }`}
          onClick={() => onLightingModeChange('night')}
        >
          Night
        </button>
      </div>

      <div className="flex flex-wrap gap-2">
        {markers.map((m) => (
          <button
            key={m.id}
            className={`px-3 py-1 text-xs rounded-full border transition-all ${
              selected.id === m.id
                ? 'bg-white text-black border-white'
                : 'border-white/30 text-white/70 hover:border-white/60'
            }`}
            onClick={() => onSelectMarker(m)}
          >
            {m.name}
          </button>
        ))}
      </div>
    </div>
  )
}
