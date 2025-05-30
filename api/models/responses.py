"""
Response models for the Agent API.

This module defines Pydantic models for API responses.
"""

from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field


# Configure datetime serialization for all models
class BaseResponseModel(BaseModel):
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class ExecutionStatus(str, Enum):
    """Possible execution statuses for agent tasks."""
    PENDING = "pending"
    RUNNING = "running" 
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class AgentInfo(BaseResponseModel):
    """Information about an available agent."""
    
    id: str = Field(..., description="Unique agent identifier")
    name: str = Field(..., description="Human-readable agent name")
    description: str = Field(..., description="Agent description")
    category: str = Field(..., description="Agent category")
    available: bool = Field(..., description="Whether agent is available for execution")
    requirements_met: bool = Field(..., description="Whether all agent requirements are configured")
    missing_requirements: List[str] = Field(default_factory=list, description="List of missing requirements")
    default_parameters: Dict[str, Any] = Field(default_factory=dict, description="Default parameters for the agent")
    timeout_seconds: int = Field(..., description="Maximum execution time in seconds")


class AgentExecutionResponse(BaseResponseModel):
    """Response for agent execution requests."""
    
    execution_id: str = Field(..., description="Unique execution identifier")
    agent_id: str = Field(..., description="Agent that was executed")
    status: ExecutionStatus = Field(..., description="Current execution status")
    created_at: datetime = Field(..., description="When the execution was started")
    completed_at: Optional[datetime] = Field(default=None, description="When the execution completed")
    result: Optional[str] = Field(default=None, description="Execution result (for completed executions)")
    error_message: Optional[str] = Field(default=None, description="Error message (for failed executions)")
    parameters: Dict[str, Any] = Field(default_factory=dict, description="Parameters used for execution")
    duration_seconds: Optional[float] = Field(default=None, description="Execution duration in seconds")


class AgentListResponse(BaseResponseModel):
    """Response for listing available agents."""
    
    agents: List[AgentInfo] = Field(..., description="List of available agents")
    total_count: int = Field(..., description="Total number of agents")
    available_count: int = Field(..., description="Number of available agents")


class AgentStatusResponse(BaseResponseModel):
    """Response for checking agent execution status."""
    
    execution_id: str = Field(..., description="Execution identifier")
    agent_id: str = Field(..., description="Agent identifier")
    status: ExecutionStatus = Field(..., description="Current execution status")
    created_at: datetime = Field(..., description="When the execution was started")
    updated_at: datetime = Field(..., description="When the status was last updated")
    completed_at: Optional[datetime] = Field(default=None, description="When the execution completed")
    progress: Optional[Dict[str, Any]] = Field(default=None, description="Execution progress information")
    result: Optional[str] = Field(default=None, description="Execution result (for completed executions)")
    error_message: Optional[str] = Field(default=None, description="Error message (for failed executions)")
    duration_seconds: Optional[float] = Field(default=None, description="Execution duration in seconds")


class HealthCheckResponse(BaseResponseModel):
    """Response for health check endpoints."""
    
    status: str = Field(..., description="Service status", example="healthy")
    timestamp: datetime = Field(..., description="Health check timestamp")
    version: str = Field(..., description="API version")
    uptime_seconds: float = Field(..., description="Service uptime in seconds")
    checks: Dict[str, bool] = Field(default_factory=dict, description="Individual health checks")


class ErrorResponse(BaseResponseModel):
    """Standard error response model."""
    
    error: str = Field(..., description="Error type")
    message: str = Field(..., description="Human-readable error message")
    details: Optional[Dict[str, Any]] = Field(default=None, description="Additional error details")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Error timestamp")
    request_id: Optional[str] = Field(default=None, description="Request identifier for tracking")


class MetricsResponse(BaseResponseModel):
    """Response for metrics endpoints."""
    
    total_executions: int = Field(..., description="Total number of agent executions")
    successful_executions: int = Field(..., description="Number of successful executions")
    failed_executions: int = Field(..., description="Number of failed executions")
    average_duration_seconds: float = Field(..., description="Average execution duration")
    executions_per_agent: Dict[str, int] = Field(default_factory=dict, description="Execution count per agent")
    recent_executions: List[AgentExecutionResponse] = Field(default_factory=list, description="Recent executions")
    uptime_seconds: float = Field(..., description="Service uptime")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Metrics timestamp") 