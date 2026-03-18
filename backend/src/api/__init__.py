from fastapi import FastAPI
from backend.src.api.routes import api_router

app = FastAPI()

# Mount all API routes
app.include_router(api_router)

# Add middleware, error handlers, etc. here as needed
