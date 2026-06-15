# app.py
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware
from src.api.routes import router

# Create FastAPI app
app = FastAPI(
    title="Student Burnout Detection System",
    description="Automated early detection of student burnout using bio-signals",
    version="1.0.0"
)

# ADD THIS LINE - Session middleware (required for login)
app.add_middleware(SessionMiddleware, secret_key="your-secret-key-change-this-in-production")

# Mount static files
app.mount("/static", StaticFiles(directory="src/web/static"), name="static")

# Include API routes
app.include_router(router)

@app.get("/api/health")
async def health_check():
    return {"status": "healthy", "message": "System is running"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)