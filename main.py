import os
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional

app = FastAPI(title="Torrent Streamer API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class SearchItem(BaseModel):
    title: str
    magnet: str
    size: Optional[str] = None
    seeds: Optional[int] = 0
    peers: Optional[int] = 0
    source: Optional[str] = None

@app.get("/")
def read_root():
    return {"message": "Torrent Streamer Backend is running"}

@app.get("/api/hello")
def hello():
    return {"message": "Hello from the backend API!"}

@app.get("/test")
def test_database():
    """Test endpoint to check if database is available and accessible"""
    response = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": None,
        "database_name": None,
        "connection_status": "Not Connected",
        "collections": []
    }
    
    try:
        # Try to import database module
        from database import db
        
        if db is not None:
            response["database"] = "✅ Available"
            response["database_url"] = "✅ Configured"
            response["database_name"] = db.name if hasattr(db, 'name') else "✅ Connected"
            response["connection_status"] = "Connected"
            
            # Try to list collections to verify connectivity
            try:
                collections = db.list_collection_names()
                response["collections"] = collections[:10]  # Show first 10 collections
                response["database"] = "✅ Connected & Working"
            except Exception as e:
                response["database"] = f"⚠️  Connected but Error: {str(e)[:50]}"
        else:
            response["database"] = "⚠️  Available but not initialized"
            
    except ImportError:
        response["database"] = "❌ Database module not found (run enable-database first)"
    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:50]}"
    
    # Check environment variables
    import os
    response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
    response["database_name"] = "✅ Set" if os.getenv("DATABASE_NAME") else "❌ Not Set"
    
    return response

@app.get("/api/search", response_model=List[SearchItem])
def search(q: str = Query("", description="Search query")):
    """
    Simple demo search that returns a curated set of legal sample torrents
    suitable for testing streaming in the browser. Replace or extend this
    with a real search index or external provider in production.
    """
    samples: List[SearchItem] = [
        SearchItem(
            title="Big Buck Bunny 720p (WebTorrent demo)",
            magnet=(
                "magnet:?xt=urn:btih:08ada5a7a6183aae1e09d831df6748d566095a10&dn=Big+Buck+Bunny+%5B2008%5D+720p&tr=udp%3A%2F%2Ftracker.openbittorrent.com%3A80"
                "&tr=udp%3A%2F%2Ftracker.opentrackr.org%3A1337%2Fannounce&tr=wss%3A%2F%2Ftracker.openwebtorrent.com"
                "&tr=wss%3A%2F%2Ftracker.btorrent.xyz&tr=wss%3A%2F%2Ftracker.fastcast.nz"
            ),
            size="700MB",
            seeds=500,
            peers=200,
            source="demo"
        ),
        SearchItem(
            title="Sintel 720p (WebTorrent demo)",
            magnet=(
                "magnet:?xt=urn:btih:37d6f9393bd39f2f9d07c9f0e2b4f0de7b0ed2f5&dn=Sintel+%5B2010%5D+720p"
                "&tr=udp%3A%2F%2Ftracker.opentrackr.org%3A1337%2Fannounce&tr=wss%3A%2F%2Ftracker.openwebtorrent.com"
                "&tr=wss%3A%2F%2Ftracker.btorrent.xyz&tr=wss%3A%2F%2Ftracker.fastcast.nz"
            ),
            size="600MB",
            seeds=200,
            peers=80,
            source="demo"
        ),
        SearchItem(
            title="Tears of Steel 720p (WebTorrent demo)",
            magnet=(
                "magnet:?xt=urn:btih:4a5e1e4b5b816d05f4a8f2b5756fa0fe58f3dcb5&dn=Tears+of+Steel+%5B2012%5D+720p"
                "&tr=udp%3A%2F%2Ftracker.opentrackr.org%3A1337%2Fannounce&tr=wss%3A%2F%2Ftracker.openwebtorrent.com"
                "&tr=wss%3A%2F%2Ftracker.btorrent.xyz&tr=wss%3A%2F%2Ftracker.fastcast.nz"
            ),
            size="900MB",
            seeds=120,
            peers=60,
            source="demo"
        ),
    ]

    if not q:
        return samples

    q_lower = q.lower()
    filtered = [s for s in samples if q_lower in s.title.lower()]
    return filtered or samples


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
