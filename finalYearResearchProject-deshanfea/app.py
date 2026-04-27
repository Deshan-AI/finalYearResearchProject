# app.py
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from src.api.routes import router
import uvicorn

# Create FastAPI app
app = FastAPI(
    title="Student Burnout Detection System",
    description="Automated early detection of student burnout using bio-signals",
    version="1.0.0"
)

# Mount static files
app.mount("/static", StaticFiles(directory="src/web/static"), name="static")

# Include API routes
app.include_router(router)

@app.get("/api/health")
async def health_check():
    return {"status": "healthy", "message": "System is running"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)