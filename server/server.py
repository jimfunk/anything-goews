"""
Anything GOEWS model generator
"""

from pathlib import Path
from sanic import Sanic, response
from sanic_ext import Extend, openapi
import time
from collections import defaultdict
import logging

from server.api import api_bp


logger = logging.getLogger("sanic")


top_dir = (Path(__file__) / "../..").resolve()
frontend_dir = top_dir / "frontend"
dist_dir = top_dir / "frontend" / "dist"
# Ensure directories exist
dist_dir.mkdir(parents=True, exist_ok=True)

# Rate limiting configuration
RATE_LIMIT_REQUESTS = 60  # requests per window
RATE_LIMIT_WINDOW = 60  # seconds
MAX_TRACKED_IPS = 10000
request_counts = defaultdict(list)


app = Sanic("AnythingGOEWS")
Extend(app)

app.config.OPENAPI_URI = "/docs/openapi.json"
app.config.OPENAPI_INFO_TITLE = "Anything GOEWS API"
app.config.OPENAPI_INFO_VERSION = "1.0.0"
app.config.OPENAPI_INFO_DESCRIPTION = "Add GOEWS mounting plates to any 3D model"

# Serve static files from dist folder (production build)
# Falls back to frontend folder for development
static_dir = dist_dir if dist_dir.exists() else frontend_dir
if (static_dir / "assets").exists():
    app.static("/assets/", static_dir / "assets", name="assets")

@app.middleware("request")
async def rate_limit_middleware(request):
    """Rate limiting middleware to prevent API abuse."""
    client_ip = request.ip
    current_time = time.time()

    # Clean old entries
    request_counts[client_ip] = [
        t for t in request_counts[client_ip]
        if current_time - t < RATE_LIMIT_WINDOW
    ]

    # Check rate limit
    if len(request_counts[client_ip]) >= RATE_LIMIT_REQUESTS:
        logger.warning(f"Rate limit exceeded for IP {client_ip}")
        return response.json(
            {"error": f"Rate limit exceeded. Max {RATE_LIMIT_REQUESTS} requests per {RATE_LIMIT_WINDOW} seconds."},
            status=429
        )

    # Cap tracked IPs to prevent unbounded memory growth
    if len(request_counts) > MAX_TRACKED_IPS:
        cutoff = current_time - RATE_LIMIT_WINDOW
        stale_ips = [
            ip for ip, times in request_counts.items()
            if not times or max(times) < cutoff
        ]
        for ip in stale_ips:
            del request_counts[ip]

    # Record this request
    request_counts[client_ip].append(current_time)



@app.route("/")
@openapi.summary("Main application")
@openapi.description("This is the main page that returns the frontend application.")
async def main(request):
    # Serve from dist folder if it exists (production), otherwise from frontend folder
    index_file = dist_dir / "index.html"
    if not index_file.exists():
        index_file = frontend_dir / "index.html"
    return await response.file(index_file)


# Get the API calls loaded
import server.parts.anything

# Register the blueprint after routes are added
app.blueprint(api_bp)


if __name__ == "__main__":
    app.run(host="::1", port=8000, debug=True)
