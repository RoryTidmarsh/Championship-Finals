"""
Main entry point for the Championship Finals API
Run with: uvicorn app:app --reload
"""

from src.api import app

if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=8000,
        reload=True  # Auto-reload on file changes (dev only)
    )
