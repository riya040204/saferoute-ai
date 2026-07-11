from fastapi import FastAPI

app = FastAPI(title="SafeRoute AI")

@app.get("/")
def read_root():
    return {"message": "SafeRoute AI backend is running 🚦"}

@app.get("/health")
def health_check():
    return {"status": "ok"}