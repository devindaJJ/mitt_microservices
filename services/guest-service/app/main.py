from fastapi import FastAPI
try:
    from .routers import guests
except ImportError:
    from routers import guests

app = FastAPI(
    title="Guest Service",
    description="Manages hotel guest profiles and registration",
    version="1.0.0",
    docs_url="/docs",
    openapi_url="/openapi.json"
)

app.include_router(guests.router, prefix="/guests", tags=["Guests"])

@app.get("/health", tags=["Health"])
def health_check():
    return {"service": "Guest Service", "status": "running", "port": 8001}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
