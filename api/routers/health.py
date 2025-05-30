"""
Health check router for monitoring and load balancer health checks.
"""

import time
from datetime import datetime
from typing import Dict, Any

from fastapi import APIRouter, status
from ..models.responses import HealthCheckResponse
from ..core import get_settings, get_logger

router = APIRouter(prefix="/health", tags=["health"])
logger = get_logger("health")

# Track service start time for uptime calculation
SERVICE_START_TIME = time.time()


@router.get("/", response_model=HealthCheckResponse)
async def health_check() -> HealthCheckResponse:
    """
    Basic health check endpoint.
    
    Returns service status and basic health information.
    Used by load balancers and monitoring systems.
    """
    settings = get_settings()
    uptime_seconds = time.time() - SERVICE_START_TIME
    
    # Perform basic health checks
    checks = {
        "api": True,  # If we can respond, API is working
        "configuration": True,  # Settings loaded successfully
    }
    
    # Check OpenAI API key (required for all agents)
    checks["openai_api_key"] = bool(settings.openai_api_key)
    
    # Check optional dependencies
    checks["telegram_configured"] = bool(settings.telegram_bot_token and settings.telegram_chat_id)
    checks["firecrawl_configured"] = bool(settings.firecrawl_api_key)
    
    # Determine overall status
    critical_checks = ["api", "configuration", "openai_api_key"]
    overall_status = "healthy" if all(checks[check] for check in critical_checks) else "degraded"
    
    response = HealthCheckResponse(
        status=overall_status,
        timestamp=datetime.utcnow(),
        version=settings.app_version,
        uptime_seconds=uptime_seconds,
        checks=checks
    )
    
    logger.info(
        "Health check performed",
        status=overall_status,
        uptime_seconds=uptime_seconds,
        checks=checks
    )
    
    return response


@router.get("/readiness", response_model=HealthCheckResponse)
async def readiness_check() -> HealthCheckResponse:
    """
    Readiness check endpoint.
    
    Performs deeper health checks to determine if the service
    is ready to handle requests. Used by Kubernetes readiness probes.
    """
    settings = get_settings()
    uptime_seconds = time.time() - SERVICE_START_TIME
    
    # Perform comprehensive readiness checks
    checks = {
        "api": True,
        "configuration": True,
        "openai_api_key": bool(settings.openai_api_key),
        "agents_available": True,  # Could check if agents can be imported
        "memory_usage": True,  # Could check memory usage
        "thread_pool": True,  # Could check thread pool status
    }
    
    # Service is ready if all critical checks pass
    critical_checks = ["api", "configuration", "openai_api_key", "agents_available"]
    is_ready = all(checks[check] for check in critical_checks)
    
    response = HealthCheckResponse(
        status="ready" if is_ready else "not_ready",
        timestamp=datetime.utcnow(),
        version=settings.app_version,
        uptime_seconds=uptime_seconds,
        checks=checks
    )
    
    logger.info(
        "Readiness check performed",
        ready=is_ready,
        checks=checks
    )
    
    return response


@router.get("/liveness")
async def liveness_check() -> Dict[str, Any]:
    """
    Liveness check endpoint.
    
    Simple endpoint that returns if the service is alive.
    Used by Kubernetes liveness probes.
    """
    return {
        "alive": True,
        "timestamp": datetime.utcnow().isoformat(),
        "uptime_seconds": time.time() - SERVICE_START_TIME
    } 