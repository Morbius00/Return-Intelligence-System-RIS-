"""
Simple startup script for the NLP API server.
Run this to start the FastAPI server.
"""
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

if __name__ == "__main__":
    import uvicorn
    
    print("=" * 60)
    print("  Starting NLP Return Reason Classifier API Server")
    print("=" * 60)
    print()
    print("  API will be available at: http://localhost:8000")
    print("  API Documentation: http://localhost:8000/docs")
    print()
    print("  Press CTRL+C to stop the server")
    print("=" * 60)
    print()
    
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
