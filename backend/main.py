# backend/main.py
"""
Quantoryx — FastAPI Backend Application Entry Point.

This module initializes the FastAPI application, maps CORS policies,
attaches request middleware, binds exception handlers, and configures Swagger,
OpenAPI, and ReDoc documentation systems.
"""

import os
import sys
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

# Guarantee the root directory is on the python search path.
# This prevents relative import lookup failures when starting the backend service.
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

import config
from utils.logging_config import get_logger
from backend.api.endpoints import router as core_router
from backend.middleware.logging_middleware import QuantoryxLoggingMiddleware

# Initialize centralized logger
logger = get_logger("backend.main")

# Initialize FastAPI instance with enterprise documentation settings
app = FastAPI(
    title=f"{config.SYSTEM_NAME} Quantitative Trading Research API",
    description=(
        f"Production-ready backend API service for the {config.SYSTEM_NAME} trading engine.\n\n"
        "Provides REST interfaces for market-regime detection, walk-forward validation, "
        "hyper-parameter optimization, cognitive AI strategy selection, paper-trading execution, "
        "and unified dashboard metrics visualization."
    ),
    version=config.VERSION,
    docs_url="/docs",      # Interactive Swagger UI endpoint
    redoc_url="/redoc",    # Interactive ReDoc UI endpoint
    openapi_url="/openapi.json"
)

# =====================================================================
# CORS MIDDLEWARE POLICY
# =====================================================================
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Broad permission policy; tighten in high-security environments
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# =====================================================================
# CUSTOM LOGGING MIDDLEWARE
# =====================================================================
app.add_middleware(QuantoryxLoggingMiddleware)

# =====================================================================
# GLOBAL EXCEPTION HANDLERS
# =====================================================================

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """
    Standardizes unhandled application crashes into structured JSON responses.
    """
    logger.critical(
        "Unhandled exception triggered during request %s %s: %s",
        request.method, request.url.path, str(exc),
        exc_info=True
    )
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "InternalServerError",
            "message": "An unexpected error occurred processing your request.",
            "detail": str(exc) if os.environ.get("QUANTORYX_LOG_LEVEL") == "DEBUG" else "Contact system administrator."
        }
    )


@app.exception_handler(ValueError)
async def value_error_exception_handler(request: Request, exc: ValueError):
    """
    Standardizes bad value violations into clean bad-request responses.
    """
    logger.warning(
        "Request bad value exception on %s %s: %s",
        request.method, request.url.path, str(exc)
    )
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={
            "error": "BadRequest",
            "message": "The request parameters are structurally invalid.",
            "detail": str(exc)
        }
    )


# =====================================================================
# APP LIFE-CYCLE EVENTS
# =====================================================================

@app.on_event("startup")
async def startup_event():
    """Triggers workspace initialization during system startup."""
    logger.info("Initializing %s API service workspace directories...", config.SYSTEM_NAME)
    try:
        from utils.path_manager import PathManager
        PathManager.initialize_workspace()
        logger.info("%s API service successfully initialized and operational.", config.SYSTEM_NAME)
        logger.info("  - Swagger Documentation: http://127.0.0.1:8000/docs")
        logger.info("  - ReDoc Documentation:   http://127.0.0.1:8000/redoc")
    except Exception as e:
        logger.critical("Workspace initialization failed on startup: %s", str(e), exc_info=True)


@app.on_event("shutdown")
async def shutdown_event():
    """Logs system shutdown cleanup operations."""
    logger.info("Shutting down %s API service. Cleaning runtime connections.", config.SYSTEM_NAME)


# =====================================================================
# ROUTER REGISTRATION
# =====================================================================
app.include_router(core_router, prefix="/api")


# Standard launch trigger for direct script execution
if __name__ == "__main__":
    import uvicorn
    # Start ASGI loop
    uvicorn.run("backend.main:app", host="127.0.0.1", port=8000, reload=True)
