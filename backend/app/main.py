from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from app.routing import get_route
from app.lighting import get_lighting_data

app = FastAPI(title="SafeRoute AI")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "SafeRoute AI backend is running 🚦"}

@app.get("/health")
def health_check():
    return {"status": "ok"}

@app.get("/route")
def route(start_lat: float, start_lon: float, end_lat: float, end_lon: float):
    try:
        routes = get_route(start_lat, start_lon, end_lat, end_lon)
        return {"routes": routes}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/lighting")
def lighting(geometry: dict):
    try:
        coordinates = geometry.get("coordinates", [])
        result = get_lighting_data(coordinates)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))