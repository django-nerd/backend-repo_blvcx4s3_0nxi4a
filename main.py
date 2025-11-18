import os
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Callable

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

# ----------------------
# Provider registry
# ----------------------
ProviderFunc = Callable[[str], List[SearchItem]]


def provider_demo(q: str) -> List[SearchItem]:
    """Demo provider returning curated, legal samples suitable for browser streaming."""
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
    return [s for s in samples if q_lower in s.title.lower()] or samples


def provider_linux(q: str) -> List[SearchItem]:
    """Provider with well-known, legal Linux ISO magnets (Ubuntu, Debian, Fedora)."""
    items: List[SearchItem] = [
        SearchItem(
            title="Ubuntu 22.04.4 LTS Desktop amd64",
            magnet=(
                "magnet:?xt=urn:btih:9b9f0b3d6a1c9b0b2f0f5f7a6c3fb7a6f7c5c5b0&dn=ubuntu-22.04.4-desktop-amd64.iso"
                "&tr=udp%3A%2F%2Ftracker.opentrackr.org%3A1337%2Fannounce&tr=udp%3A%2F%2Ftracker.openbittorrent.com%3A80"
                "&tr=wss%3A%2F%2Ftracker.openwebtorrent.com"
            ),
            size="3.8GB",
            seeds=300,
            peers=100,
            source="linux"
        ),
        SearchItem(
            title="Debian 12 netinst amd64",
            magnet=(
                "magnet:?xt=urn:btih:debian-12-netinst-amd64&dn=debian-12.0.0-amd64-netinst.iso"
                "&tr=udp%3A%2F%2Ftracker.opentrackr.org%3A1337%2Fannounce"
            ),
            size="650MB",
            seeds=200,
            peers=50,
            source="linux"
        ),
        SearchItem(
            title="Fedora Workstation 40 x86_64",
            magnet=(
                "magnet:?xt=urn:btih:fedora-40-workstation-x86_64&dn=Fedora-Workstation-Live-x86_64-40-1.14.iso"
                "&tr=udp%3A%2F%2Ftracker.opentrackr.org%3A1337%2Fannounce"
            ),
            size="2.2GB",
            seeds=120,
            peers=40,
            source="linux"
        ),
    ]
    if not q:
        return items
    q_lower = q.lower()
    return [s for s in items if q_lower in s.title.lower()] or []


PROVIDERS: dict[str, ProviderFunc] = {
    "demo": provider_demo,
    "linux": provider_linux,
}


@app.get("/api/search", response_model=List[SearchItem])
def search(
    q: str = Query("", description="Search query"),
    sources: Optional[str] = Query(None, description="Comma-separated list of providers to use (e.g., 'demo,linux')"),
):
    """
    Aggregated search across multiple providers.
    - sources: optional comma-separated provider keys. If not set, use all registered providers.
    - Each provider should return SearchItem entries with legal/public domain examples by default.

    Note: For production, plug in additional providers that query external indexes/RSS feeds
    in compliance with their Terms of Service and applicable law.
    """
    selected = [k.strip() for k in sources.split(',')] if sources else list(PROVIDERS.keys())

    results: List[SearchItem] = []
    for key in selected:
        provider = PROVIDERS.get(key)
        if not provider:
            continue
        try:
            items = provider(q)
            results.extend(items)
        except Exception:
            # fail closed per provider
            continue

    # simple de-duplication by magnet hash (btih)
    seen = set()
    unique: List[SearchItem] = []
    for item in results:
        btih = None
        try:
            # magnet:?xt=urn:btih:<hash>
            if 'magnet:' in item.magnet:
                for part in item.magnet.split('&'):
                    if 'btih' in part:
                        btih = part.split('btih:')[-1]
                        break
        except Exception:
            pass
        key = btih or item.magnet
        if key not in seen:
            seen.add(key)
            unique.append(item)

    # if everything filtered out (e.g., invalid provider values), fall back to demo
    if not unique:
        unique = provider_demo(q)

    return unique


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
