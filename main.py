from fastapi import FastAPI
try:
    from .routers import payments
except ImportError:
    from routers import payments

app = FastAPI(
    title="Payment Service",
    description="Processes hotel payments and generates invoices",
    version="1.0.0",
    docs_url="/docs",
    openapi_url="/openapi.json"
)

app.include_router(payments.router, prefix="/payments", tags=["Payments"])

@app.get("/health", tags=["Health"])
def health_check():
    return {"service": "Payment Service", "status": "running", "port": 8004}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8004)
