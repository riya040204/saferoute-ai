from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from app.routing import get_route
from app.lighting import get_lighting_data
from app.ai_explain import generate_route_explanation, generate_chat_reply

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
def route(start_lat: float, start_lon: float, end_lat: float, end_lon: float, profile: str = "driving"):
    try:
        routes = get_route(start_lat, start_lon, end_lat, end_lon, profile)
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


@app.post("/explain")
def explain(payload: dict):
    try:
        routes = payload.get("routes", [])
        explanation = generate_route_explanation(routes)
        return {"explanation": explanation}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/chat")
def chat(payload: dict):
    try:
        routes = payload.get("routes", [])
        history = payload.get("history", [])
        question = payload.get("question", "")
        reply = generate_chat_reply(routes, history, question)
        return {"reply": reply}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))