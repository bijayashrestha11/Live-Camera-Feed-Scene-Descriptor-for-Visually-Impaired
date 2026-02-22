"""
API middleware for Scene Descriptor.

Provides CORS support and request logging.
"""

import time
from typing import Callable

import aiohttp_cors
from aiohttp import web

from ..utils.logging import get_logger

logger = get_logger(__name__)


def setup_cors(app: web.Application) -> aiohttp_cors.CorsConfig:
    """
    Set up CORS for the application.

    Allows cross-origin requests from any origin (for development).
    In production, this should be restricted.

    Args:
        app: The aiohttp application instance

    Returns:
        CORS configuration object
    """
    cors = aiohttp_cors.setup(app)

    # Configure CORS for all routes
    for route in list(app.router.routes()):
        cors.add(
            route,
            {
                "*": aiohttp_cors.ResourceOptions(
                    allow_credentials=True,
                    expose_headers="*",
                    allow_headers="*",
                    allow_methods="*",
                )
            }
        )

    logger.info("CORS configured for all routes")
    return cors


@web.middleware
async def logging_middleware(
    request: web.Request,
    handler: Callable
) -> web.Response:
    """
    Middleware for logging requests and responses.

    Args:
        request: The incoming request
        handler: The route handler

    Returns:
        The response from the handler
    """
    start_time = time.time()

    # Log request
    logger.info(f"Request: {request.method} {request.path}")
    logger.debug(f"Request headers: {dict(request.headers)}")

    try:
        response = await handler(request)

        # Log response
        duration = time.time() - start_time
        logger.info(
            f"Response: {response.status} "
            f"({duration:.3f}s) {request.method} {request.path}"
        )

        return response

    except web.HTTPException as e:
        duration = time.time() - start_time
        logger.warning(
            f"HTTP Exception: {e.status} "
            f"({duration:.3f}s) {request.method} {request.path}"
        )
        raise

    except Exception as e:
        duration = time.time() - start_time
        logger.error(
            f"Unhandled error: {e} "
            f"({duration:.3f}s) {request.method} {request.path}",
            exc_info=True
        )
        raise


@web.middleware
async def error_middleware(
    request: web.Request,
    handler: Callable
) -> web.Response:
    """
    Middleware for handling uncaught errors.

    Args:
        request: The incoming request
        handler: The route handler

    Returns:
        The response from the handler or an error response
    """
    try:
        return await handler(request)
    except web.HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unhandled error: {e}", exc_info=True)
        return web.json_response(
            {"error": "Internal server error"},
            status=500
        )


def get_middlewares() -> list:
    """
    Get the list of middlewares to use.

    Returns:
        List of middleware functions
    """
    return [
        error_middleware,
        logging_middleware,
    ]
