from fastapi import FastAPI, HTTPException
from app.routing import get_route

app = FastAPI(title="SafeRoute AI")

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