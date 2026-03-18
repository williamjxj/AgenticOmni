# FastAPI backend entrypoint for AgenticOmni PoC/MVP
from fastapi import FastAPI

app = FastAPI(title="AgenticOmni Backend PoC/MVP")

@app.get("/health")
def health():
    return {"status": "ok"}
