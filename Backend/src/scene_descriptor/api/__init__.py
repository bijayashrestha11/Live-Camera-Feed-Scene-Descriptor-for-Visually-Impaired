"""API module for Scene Descriptor."""

from .routes import setup_routes, get_route_info
from .handlers import offer_handler, change_model_handler, health_handler
from .middleware import setup_cors, logging_middleware, error_middleware, get_middlewares

__all__ = [
    "setup_routes",
    "get_route_info",
    "offer_handler",
    "change_model_handler",
    "health_handler",
    "setup_cors",
    "logging_middleware",
    "error_middleware",
    "get_middlewares",
]
