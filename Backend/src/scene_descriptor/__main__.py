"""
Scene Descriptor - Application Entry Point

Run with: python -m scene_descriptor [options]
"""

import argparse
import asyncio
import logging
import ssl
import sys
from pathlib import Path

from aiohttp import web

from .config import settings
from .models import get_model_manager
from .api import setup_routes, setup_cors, get_middlewares
from .webrtc import close_all_connections
from .utils.logging import setup_logging, get_logger


def parse_args() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Scene Descriptor - Real-time video captioning server"
    )
    parser.add_argument(
        "--host",
        default=settings.host,
        help=f"Host for HTTP server (default: {settings.host})"
    )
    parser.add_argument(
        "--port",
        type=int,
        default=settings.port,
        help=f"Port for HTTP server (default: {settings.port})"
    )
    parser.add_argument(
        "--cert-file",
        help="SSL certificate file (for HTTPS)"
    )
    parser.add_argument(
        "--key-file",
        help="SSL key file (for HTTPS)"
    )
    parser.add_argument(
        "--model-dir",
        type=Path,
        default=settings.model_dir,
        help=f"Directory containing ML models (default: {settings.model_dir})"
    )
    parser.add_argument(
        "--log-level",
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        default=settings.log_level,
        help=f"Logging level (default: {settings.log_level})"
    )
    parser.add_argument(
        "--log-dir",
        type=Path,
        default=settings.log_dir,
        help=f"Directory for log files (default: {settings.log_dir})"
    )
    parser.add_argument(
        "-v", "--verbose",
        action="count",
        default=0,
        help="Increase verbosity (-v for DEBUG)"
    )
    parser.add_argument(
        "--no-log-file",
        action="store_true",
        help="Disable file logging"
    )

    return parser.parse_args()


async def on_shutdown(app: web.Application) -> None:
    """Cleanup on application shutdown."""
    logger = get_logger(__name__)
    logger.info("Shutting down...")
    await close_all_connections()
    logger.info("Shutdown complete")


def create_app() -> web.Application:
    """Create and configure the aiohttp application."""
    middlewares = get_middlewares()
    app = web.Application(middlewares=middlewares)

    # Set up routes
    setup_routes(app)

    # Set up CORS
    setup_cors(app)

    # Register shutdown handler
    app.on_shutdown.append(on_shutdown)

    return app


def main() -> int:
    """Main entry point."""
    args = parse_args()

    # Determine log level
    log_level = args.log_level
    if args.verbose:
        log_level = "DEBUG"

    # Set up logging
    log_dir = None if args.no_log_file else args.log_dir
    setup_logging(
        log_level=log_level,
        log_dir=log_dir,
        console_output=True
    )

    logger = get_logger(__name__)
    logger.info("=" * 60)
    logger.info("Scene Descriptor - Starting")
    logger.info("=" * 60)

    # Initialize ML models
    logger.info("Initializing ML models...")
    try:
        model_manager = get_model_manager()
        model_manager.initialize(args.model_dir)
        logger.info(f"Models initialized successfully on {model_manager.device}")
    except Exception as e:
        logger.critical(f"Failed to initialize models: {e}", exc_info=True)
        return 1

    # Set up SSL if certificates provided
    ssl_context = None
    if args.cert_file:
        if not args.key_file:
            logger.error("SSL key file required when using certificate")
            return 1
        ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        ssl_context.load_cert_chain(args.cert_file, args.key_file)
        logger.info("SSL enabled")

    # Create and run application
    app = create_app()

    logger.info(f"Starting server on {args.host}:{args.port}")
    logger.info("Press Ctrl+C to stop")

    try:
        web.run_app(
            app,
            host=args.host,
            port=args.port,
            ssl_context=ssl_context,
            access_log=None  # We have our own logging middleware
        )
    except KeyboardInterrupt:
        logger.info("Received interrupt signal")
    except Exception as e:
        logger.critical(f"Server error: {e}", exc_info=True)
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
