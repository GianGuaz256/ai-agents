"""
Personal Agent Team API

Production-ready FastAPI application for managing and executing AI agents.
Built following Agno's best practices for scalable agentic systems.
"""

import time
import uuid
from contextlib import asynccontextmanager
from datetime import datetime
from typing import Dict, Any

import uvicorn
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse, FileResponse, Response
from fastapi.staticfiles import StaticFiles
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.openapi.utils import get_openapi

# Import core configuration and services
from .core import configure_logging, get_settings, get_logger, log_api_request, log_system_event
from .routers import agents, health
from .models.responses import ErrorResponse
from .services import AgentManager, SchedulerService

# Configure logging before anything else
configure_logging()
logger = get_logger("main")

# Global agent manager instance
agent_manager = None
scheduler_service = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager.
    
    Handles startup and shutdown events for the FastAPI application.
    Following Agno's patterns for production deployment.
    """
    global agent_manager, scheduler_service
    
    # Startup
    logger.info("Starting Personal Agent Team API")
    settings = get_settings()
    
    # Initialize services
    agent_manager = AgentManager()
    scheduler_service = SchedulerService()
    
    # Connect services
    scheduler_service.set_agent_manager(agent_manager)
    
    # Start scheduler
    await scheduler_service.start()
    
    # Log startup
    log_system_event(
        event_type="startup",
        message="API server started with scheduler",
        version=settings.app_version,
        environment="production" if not settings.debug else "development"
    )
    
    yield
    
    # Shutdown
    logger.info("Shutting down Personal Agent Team API")
    
    # Cleanup services
    if scheduler_service:
        await scheduler_service.stop()
    
    if agent_manager:
        agent_manager.shutdown()
    
    log_system_event(
        event_type="shutdown",
        message="API server shut down"
    )


# Create FastAPI application
def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    settings = get_settings()
    
    app = FastAPI(
        title=settings.app_name,
        description=settings.app_description,
        version=settings.app_version,
        debug=settings.debug,
        lifespan=lifespan,
        docs_url="/docs" if settings.debug else None,  # Disable in production
        redoc_url="/redoc" if settings.debug else None,
    )
    
    # Add security middleware
    if not settings.debug:
        app.add_middleware(
            TrustedHostMiddleware,
            allowed_hosts=["*"]  # Configure properly for production
        )
    
    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"] if settings.debug else [],  # Configure properly for production
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Request logging middleware
    @app.middleware("http")
    async def log_requests(request: Request, call_next):
        """Log all HTTP requests with timing and status codes."""
        start_time = time.time()
        request_id = str(uuid.uuid4())
        
        # Add request ID to request state
        request.state.request_id = request_id
        
        try:
            response = await call_next(request)
            duration_ms = (time.time() - start_time) * 1000
            
            # Log the request
            log_api_request(
                method=request.method,
                path=request.url.path,
                status_code=response.status_code,
                duration_ms=duration_ms,
                request_id=request_id
            )
            
            # Add request ID to response headers
            response.headers["X-Request-ID"] = request_id
            
            return response
            
        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            
            # Log the error
            log_api_request(
                method=request.method,
                path=request.url.path,
                status_code=500,
                duration_ms=duration_ms,
                request_id=request_id,
                error=str(e)
            )
            
            # Return structured error response
            error_response = ErrorResponse(
                error="internal_server_error",
                message="An internal server error occurred",
                request_id=request_id
            )
            return JSONResponse(
                status_code=500,
                content=error_response.model_dump(mode='json'),
                headers={"X-Request-ID": request_id}
            )
    
    # Global exception handler
    @app.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, exc: HTTPException):
        """Handle HTTP exceptions with structured error responses."""
        request_id = getattr(request.state, "request_id", str(uuid.uuid4()))
        
        error_response = ErrorResponse(
            error=f"http_{exc.status_code}",
            message=exc.detail,
            request_id=request_id
        )
        
        return JSONResponse(
            status_code=exc.status_code,
            content=error_response.model_dump(mode='json'),
            headers={"X-Request-ID": request_id}
        )
    
    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception):
        """Handle general exceptions with structured error responses."""
        request_id = getattr(request.state, "request_id", str(uuid.uuid4()))
        
        logger.error(
            "Unhandled exception",
            error=str(exc),
            request_id=request_id,
            path=request.url.path,
            method=request.method
        )
        
        error_response = ErrorResponse(
            error="internal_server_error",
            message="An unexpected error occurred",
            request_id=request_id
        )
        
        return JSONResponse(
            status_code=500,
            content=error_response.model_dump(mode='json'),
            headers={"X-Request-ID": request_id}
        )
    
    # Include routers
    app.include_router(health.router)
    app.include_router(agents.router)
    
    # Root endpoint
    @app.get("/", tags=["root"])
    async def root() -> Dict[str, Any]:
        """Root endpoint with API information."""
        return {
            "name": settings.app_name,
            "version": settings.app_version,
            "description": settings.app_description,
            "status": "operational",
            "timestamp": datetime.utcnow().isoformat(),
            "endpoints": {
                "health": "/health",
                "agents": "/agents",
                "docs": "/docs" if settings.debug else "disabled",
                "metrics": "/agents/metrics"
            }
        }
    
    # Favicon endpoint
    @app.get("/favicon.ico", include_in_schema=False)
    @app.head("/favicon.ico", include_in_schema=False)
    async def favicon():
        """Return favicon to prevent 404 errors."""
        # Return a simple 1x1 transparent PNG as favicon
        favicon_data = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15\xc4\x89\x00\x00\x00\rIDATx\x9cc\xf8\x0f\x00\x00\x01\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00'
        return Response(content=favicon_data, media_type="image/x-icon")
    
    # Custom OpenAPI schema
    def custom_openapi():
        if app.openapi_schema:
            return app.openapi_schema
        
        openapi_schema = get_openapi(
            title=settings.app_name,
            version=settings.app_version,
            description=settings.app_description,
            routes=app.routes,
        )
        
        # Add custom info
        openapi_schema["info"]["contact"] = {
            "name": "Personal Agent Team",
            "url": "https://github.com/your-repo"
        }
        
        openapi_schema["info"]["license"] = {
            "name": "MIT",
            "url": "https://opensource.org/licenses/MIT"
        }
        
        app.openapi_schema = openapi_schema
        return app.openapi_schema
    
    app.openapi = custom_openapi
    
    return app


# Create the application instance
app = create_app()


# Development server entry point
if __name__ == "__main__":
    settings = get_settings()
    
    uvicorn.run(
        "api.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.reload,
        workers=1,  # Single worker for development
        log_level=settings.log_level.lower(),
        access_log=True
    ) 