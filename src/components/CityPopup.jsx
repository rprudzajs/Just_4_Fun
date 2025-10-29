export default function CityPopup({ city, onClose }) {
    if (!city) return null
  
    return (
      <div className="absolute inset-0 z-[50] flex items-center justify-center bg-black/60 backdrop-blur-sm">
        <div className="bg-[#0a0e1a] border border-white/10 rounded-2xl p-8 max-w-md text-white shadow-2xl relative">
          <button
            onClick={onClose}
            className="absolute top-3 right-4 text-gray-400 hover:text-white text-xl"
          >
            ✕
          </button>
  
          <h2 className="text-3xl font-bold mb-3">{city.name}</h2>
          <p className="text-gray-300 mb-4">{city.tagline}</p>
          <p className="text-sm text-gray-400">
            Coordinates: {city.coordinates.lat}, {city.coordinates.lon}
          </p>
        </div>
      </div>
    )
  }
  