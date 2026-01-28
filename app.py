"""
Main entry point for the Championship Finals API
Run with: uvicorn app:app --reload
"""
import os
from src.api import app

if __name__ == "__main__":
    import uvicorn
    
    # Detect environment
    is_production = os.environ.get("RENDER") is not None  # Render sets this env var
    # Alternative: is_production = os.environ.get("ENV") == "production"
    
    port = int(os.environ.get("PORT", 8000))
    
    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=port,
        reload=not is_production  # Auto-reload only in development
    )
