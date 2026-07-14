import {
  MapContainer,
  TileLayer,
  Polyline,
  Marker,
  Popup,
} from "react-leaflet";
import "leaflet/dist/leaflet.css";
import { useState } from "react";
import "./App.css";

function App() {
  const [routes, setRoutes] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  // Hardcoded test coordinates for now (Indore)
  const start = { lat: 22.7196, lon: 75.8577 };
  const end = { lat: 22.7532, lon: 75.8937 };

  const fetchRoute = async () => {
    setLoading(true);
    setError(null);
    try {
      const url = `http://127.0.0.1:8000/route?start_lat=${start.lat}&start_lon=${start.lon}&end_lat=${end.lat}&end_lon=${end.lon}`;
      const response = await fetch(url);
      if (!response.ok) throw new Error("Failed to fetch route");
      const data = await response.json();
      setRoutes(data.routes);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ height: "100vh", width: "100vw" }}>
      <div
        style={{
          position: "absolute",
          zIndex: 1000,
          top: 10,
          left: 10,
          background: "white",
          padding: "10px",
          borderRadius: "8px",
        }}
      >
        <button onClick={fetchRoute} disabled={loading}>
          {loading ? "Loading..." : "Get Route"}
        </button>
        {error && <p style={{ color: "red" }}>{error}</p>}
      </div>

      <MapContainer
        center={[start.lat, start.lon]}
        zoom={13}
        style={{ height: "100%", width: "100%" }}
      >
        <TileLayer
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
          attribution="&copy; OpenStreetMap contributors"
        />

        <Marker position={[start.lat, start.lon]}>
          <Popup>Start</Popup>
        </Marker>
        <Marker position={[end.lat, end.lon]}>
          <Popup>End</Popup>
        </Marker>

        {routes.map((route, index) => {
          // route.geometry.coordinates is [lon, lat] — Leaflet wants [lat, lon], so we flip them
          const positions = route.geometry.coordinates.map(([lon, lat]) => [
            lat,
            lon,
          ]);
          return (
            <Polyline
              key={index}
              positions={positions}
              color={index === 0 ? "blue" : "gray"}
            />
          );
        })}
      </MapContainer>
    </div>
  );
}

export default App;
