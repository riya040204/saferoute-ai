import {
  MapContainer,
  TileLayer,
  Polyline,
  Marker,
  Popup,
  useMap,
} from "react-leaflet";
import "leaflet/dist/leaflet.css";
import { useState, useEffect } from "react";
import "./App.css";
import L from "leaflet";

const startIcon = L.divIcon({
  className: "custom-marker start-marker",
  html: '<div class="marker-dot start-dot"></div>',
  iconSize: [16, 16],
  iconAnchor: [8, 8],
});

const endIcon = L.divIcon({
  className: "custom-marker end-marker",
  html: '<div class="marker-dot end-dot"></div>',
  iconSize: [16, 16],
  iconAnchor: [8, 8],
});

function RecenterMap({ position }) {
  const map = useMap();
  useEffect(() => {
    if (position) map.setView([position.lat, position.lng], 14);
  }, [position]);
  return null;
}

function useGeocodeSearch(query) {
  const [suggestions, setSuggestions] = useState([]);
  useEffect(() => {
    if (query.trim().length < 3) {
      setSuggestions([]);
      return;
    }
    const timer = setTimeout(async () => {
      try {
        const url = `https://nominatim.openstreetmap.org/search?format=json&q=${encodeURIComponent(query)}&countrycodes=in&limit=5`;
        const res = await fetch(url);
        setSuggestions(await res.json());
      } catch {
        setSuggestions([]);
      }
    }, 500);
    return () => clearTimeout(timer);
  }, [query]);
  return suggestions;
}

function App() {
  const [start, setStart] = useState(null);
  const [startQuery, setStartQuery] = useState("");
  const [end, setEnd] = useState(null);
  const [endQuery, setEndQuery] = useState("");
  const [routes, setRoutes] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [sidebarExpanded, setSidebarExpanded] = useState(true);
  const [explanation, setExplanation] = useState("");
  const [explaining, setExplaining] = useState(false);

  const startSuggestions = useGeocodeSearch(startQuery);
  const endSuggestions = useGeocodeSearch(endQuery);

  const useMyLocation = () => {
    if (!navigator.geolocation) {
      setError("Geolocation is not supported by your browser");
      return;
    }
    navigator.geolocation.getCurrentPosition(
      (position) => {
        setStart({
          lat: position.coords.latitude,
          lng: position.coords.longitude,
        });
        setStartQuery("Current location");
      },
      (err) => setError("Could not get your location: " + err.message),
    );
  };

  const selectStart = (place) => {
    setStart({ lat: parseFloat(place.lat), lng: parseFloat(place.lon) });
    setStartQuery(place.display_name);
  };

  const selectEnd = (place) => {
    setEnd({ lat: parseFloat(place.lat), lng: parseFloat(place.lon) });
    setEndQuery(place.display_name);
  };

  const fetchRoute = async () => {
    if (!start || !end) return;
    setLoading(true);
    setError(null);
    try {
      const url = `http://127.0.0.1:8000/route?start_lat=${start.lat}&start_lon=${start.lng}&end_lat=${end.lat}&end_lon=${end.lng}`;
      const response = await fetch(url);
      if (!response.ok) throw new Error("Failed to fetch route");
      const data = await response.json();
      setRoutes(data.routes);
      setLoading(false);

      setExplaining(true);
      fetch("http://127.0.0.1:8000/explain", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ routes: data.routes }),
      })
        .then((res) => res.json())
        .then((result) => setExplanation(result.explanation))
        .catch(() => setExplanation(""))
        .finally(() => setExplaining(false));

      data.routes.forEach(async (r, index) => {
        try {
          const controller = new AbortController();
          const timeoutId = setTimeout(() => controller.abort(), 12000);

          const lightingRes = await fetch("http://127.0.0.1:8000/lighting", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(r.geometry),
            signal: controller.signal,
          });
          clearTimeout(timeoutId);

          const lightingData = await lightingRes.json();
          setRoutes((prev) => {
            const updated = [...prev];
            if (updated[index])
              updated[index] = { ...updated[index], lighting: lightingData };
            return updated;
          });
        } catch (err) {
          setRoutes((prev) => {
            const updated = [...prev];
            if (updated[index]) {
              updated[index] = {
                ...updated[index],
                lighting: {
                  lit_percent: 0,
                  unlit_percent: 0,
                  unknown_percent: 100,
                  unavailable: true,
                },
              };
            }
            return updated;
          });
        }
      });
    } catch (err) {
      setError(err.message);
      setLoading(false);
    }
  };

  return (
    <div className="app-shell">
      <aside className={`sidebar ${sidebarExpanded ? "expanded" : ""}`}>
        <button
          className="mobile-toggle"
          onClick={() => setSidebarExpanded(!sidebarExpanded)}
        ></button>
        <div className="brand-block">
          <div className="brand">
            <span className="brand-dot"></span>
            <span className="brand-name">SafeRoute</span>
          </div>
          <p className="brand-tagline">Night safety routing</p>
        </div>

        <div className="trip-card">
          <div className="trip-rail">
            <span className="trip-dot start"></span>
            <span className="trip-line"></span>
            <span className="trip-dot end"></span>
          </div>

          <div className="trip-inputs">
            <div className="trip-input-row">
              <input
                type="text"
                value={startQuery}
                onChange={(e) => {
                  setStartQuery(e.target.value);
                  setStart(null);
                }}
                placeholder="Your location"
              />
              <button className="gps-toggle" onClick={useMyLocation}>
                GPS
              </button>
            </div>

            {startSuggestions.length > 0 && (
              <ul className="suggestions">
                {startSuggestions.map((place) => (
                  <li key={place.place_id} onClick={() => selectStart(place)}>
                    {place.display_name}
                  </li>
                ))}
              </ul>
            )}

            <div className="trip-input-row">
              <input
                type="text"
                value={endQuery}
                onChange={(e) => {
                  setEndQuery(e.target.value);
                  setEnd(null);
                }}
                placeholder="Where to?"
              />
            </div>

            {endSuggestions.length > 0 && (
              <ul className="suggestions">
                {endSuggestions.map((place) => (
                  <li key={place.place_id} onClick={() => selectEnd(place)}>
                    {place.display_name}
                  </li>
                ))}
              </ul>
            )}
          </div>
        </div>

        <div className="field-group">
          <span className="field-label">To</span>
          <div className="field-row">
            <input
              type="text"
              value={endQuery}
              onChange={(e) => {
                setEndQuery(e.target.value);
                setEnd(null);
              }}
              placeholder="Search destination..."
            />
          </div>
          {endSuggestions.length > 0 && (
            <ul className="suggestions">
              {endSuggestions.map((place) => (
                <li key={place.place_id} onClick={() => selectEnd(place)}>
                  {place.display_name}
                </li>
              ))}
            </ul>
          )}
        </div>

        <button
          className="primary-btn"
          onClick={fetchRoute}
          disabled={!start || !end || loading}
        >
          {loading ? "Finding routes..." : "Get Route"}
        </button>

        {!start && !end && (
          <div className="empty-state">
            <span className="empty-state-icon">🌙</span>
            <p>
              Set a starting point and destination to see safety-scored routes
              for your journey.
            </p>
          </div>
        )}
        {error && <p className="error-line">{error}</p>}
        {explaining && <p className="status-line">Analyzing routes...</p>}

        {explanation && (
          <div className="ai-explanation">
            <span className="field-label">AI Recommendation</span>
            <p>{explanation}</p>
          </div>
        )}

        {loading && (
          <div className="route-cards">
            <div className="skeleton-card">
              <div className="skeleton-line w-60"></div>
              <div className="skeleton-line w-100"></div>
            </div>
            <div className="skeleton-card">
              <div className="skeleton-line w-60"></div>
              <div className="skeleton-line w-100"></div>
            </div>
          </div>
        )}

        {routes.length > 0 && (
          <div className="route-cards">
            {routes.map((route, index) => {
              const lighting = route.lighting || {
                lit_percent: 0,
                unlit_percent: 0,
                unknown_percent: 100,
              };
              const minutes = Math.round(route.duration_seconds / 60);
              const km = (route.distance_meters / 1000).toFixed(1);
              return (
                <div
                  key={index}
                  className={`route-card ${index === 0 ? "primary" : ""}`}
                >
                  <div className="route-card-top">
                    <span className="route-card-time">{minutes} min</span>
                    <span className="route-card-distance">{km} km</span>
                  </div>
                  <div className="safety-bar">
                    <div
                      className="safety-bar-segment lit"
                      style={{ width: `${lighting.lit_percent}%` }}
                    ></div>
                    <div
                      className="safety-bar-segment unlit"
                      style={{ width: `${lighting.unlit_percent}%` }}
                    ></div>
                    <div
                      className="safety-bar-segment unknown"
                      style={{ width: `${lighting.unknown_percent}%` }}
                    ></div>
                  </div>
                  <div className="safety-legend">
                    {lighting.unavailable ? (
                      <span>Lighting data unavailable for this route</span>
                    ) : (
                      <>
                        <span>
                          <span
                            className="legend-dot"
                            style={{ background: "var(--lamp)" }}
                          ></span>
                          Lit {lighting.lit_percent}%
                        </span>
                        <span>
                          <span
                            className="legend-dot"
                            style={{ background: "var(--risk)" }}
                          ></span>
                          Unlit {lighting.unlit_percent}%
                        </span>
                      </>
                    )}
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </aside>

      <div className="map-area">
        <MapContainer
          center={[22.9734, 78.6569]}
          zoom={5}
          style={{ height: "100%", width: "100%" }}
        >
          <TileLayer
            url="https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png"
            attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors &copy; <a href="https://carto.com/attributions">CARTO</a>'
          />

          {start && <RecenterMap position={start} />}

          {start && (
            <Marker position={[start.lat, start.lng]} icon={startIcon}>
              <Popup>Start</Popup>
            </Marker>
          )}
          {end && (
            <Marker position={[end.lat, end.lng]} icon={endIcon}>
              <Popup>Destination</Popup>
            </Marker>
          )}

          {routes.map((route, index) => {
            const positions = route.geometry.coordinates.map(([lon, lat]) => [
              lat,
              lon,
            ]);
            return (
              <Polyline
                key={index}
                positions={positions}
                pathOptions={{
                  color: index === 0 ? "#FFB454" : "#8B95AC",
                  weight: index === 0 ? 5 : 3,
                  className:
                    index === 0 ? "route-glow-primary" : "route-glow-alt",
                }}
              />
            );
          })}
        </MapContainer>
      </div>
    </div>
  );
}

export default App;
