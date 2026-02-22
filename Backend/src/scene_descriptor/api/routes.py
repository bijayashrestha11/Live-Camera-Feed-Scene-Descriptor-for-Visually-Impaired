"""
API route definitions for Scene Descriptor.

Sets up all HTTP routes for the application.
"""

from aiohttp import web

from .handlers import offer_handler, change_model_handler, health_handler
from ..utils.logging import get_logger

logger = get_logger(__name__)


def setup_routes(app: web.Application) -> None:
    """
    Set up all API routes.

    Args:
        app: The aiohttp application instance
    """
    # WebRTC signaling
    app.router.add_post("/offer", offer_handler)

    # Model management
    app.router.add_post("/change_model", change_model_handler)

    # Health check
    app.router.add_get("/health", health_handler)

    logger.info("API routes configured")


def get_route_info() -> list:
    """
    Get information about available routes.

    Returns:
        List of route information dictionaries
    """
    return [
        {
            "method": "POST",
            "path": "/offer",
            "description": "WebRTC signaling - accepts SDP offer, returns answer"
        },
        {
            "method": "POST",
            "path": "/change_model",
            "description": "Switch between ML models (git, pulchowk)"
        },
        {
            "method": "GET",
            "path": "/health",
            "description": "Health check endpoint"
        }
    ]
