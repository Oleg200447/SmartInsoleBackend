"""FastAPI application entry point for Smart Insole Backend"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import CORS_ORIGINS, BACKEND_HOST, BACKEND_PORT
from app.database import init_db
from app.routers.session import router as session_router

# Create FastAPI application
app = FastAPI(
    title="Smart Insole API",
    description="Backend API for Smart Insole demo application. Provides endpoints for sensor data retrieval, signal processing, step detection, pressure heatmap generation, and activity classification.",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(session_router)


@app.on_event("startup")
async def startup_event():
    """Initialize database on startup."""
    init_db()
    print(f"Smart Insole Backend started on {BACKEND_HOST}:{BACKEND_PORT}")
    print(f"API documentation available at http://localhost:{BACKEND_PORT}/docs")


@app.get("/", tags=["Root"])
async def root():
    """Root endpoint with API information."""
    return {
        "name": "Smart Insole API",
        "version": "0.1.0",
        "docs": "/docs",
        "health": "/health",
        "endpoints": {
            "session_data": "/api/session/data",
            "processed_data": "/api/session/processed",
            "steps_analysis": "/api/analysis/steps",
            "heatmap": "/api/analysis/heatmap",
            "classification": "/api/analysis/classification",
        }
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=BACKEND_HOST,
        port=BACKEND_PORT,
        reload=True
    )
