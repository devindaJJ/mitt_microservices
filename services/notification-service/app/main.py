from fastapi import FastAPI
try:
    from .routers import notifications
except ImportError:
    from routers import notifications

app = FastAPI(
    title="Notification Service",
    description="Sends email and SMS alerts for hotel booking events",
    version="1.0.0",
    docs_url="/docs",
    openapi_url="/openapi.json"
)

app.include_router(notifications.router, prefix="/notifications", tags=["Notifications"])

@app.get("/health", tags=["Health"])
def health_check():
    return {"service": "Notification Service", "status": "running", "port": 8005}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8005)
