"""
Request models for the Agent API.

This module defines Pydantic models for incoming API requests.
"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, validator


class AgentExecutionRequest(BaseModel):
    """Request model for executing an agent."""
    
    agent_id: str = Field(
        ..., 
        description="ID of the agent to execute",
        example="enhanced-daily-news"
    )
    
    parameters: Optional[Dict[str, Any]] = Field(
        default_factory=dict,
        description="Agent-specific parameters",
        example={
            "topics": ["Bitcoin", "AI", "Politics"],
            "max_articles_per_topic": 3
        }
    )
    
    async_execution: bool = Field(
        default=True,
        description="Whether to execute the agent asynchronously"
    )
    
    callback_url: Optional[str] = Field(
        default=None,
        description="URL to call when execution completes (for async execution)"
    )
    
    @validator("agent_id")
    def validate_agent_id(cls, v):
        if not v or not v.strip():
            raise ValueError("Agent ID cannot be empty")
        return v.strip().lower()


class NewsAgentRequest(BaseModel):
    """Specific request model for the Enhanced Daily News Agent."""
    
    topics: Optional[List[str]] = Field(
        default=None,
        description="List of topics to research. If not provided, uses default topics.",
        example=["Bitcoin cryptocurrency", "Artificial Intelligence", "US Politics"]
    )
    
    max_articles_per_topic: Optional[int] = Field(
        default=3,
        ge=1,
        le=10,
        description="Maximum number of articles to research per topic"
    )
    
    enable_telegram: Optional[bool] = Field(
        default=None,
        description="Whether to send results via Telegram. If not specified, uses environment configuration."
    )
    
    @validator("topics")
    def validate_topics(cls, v):
        if v is not None:
            if len(v) == 0:
                raise ValueError("Topics list cannot be empty if provided")
            if len(v) > 10:
                raise ValueError("Maximum 10 topics allowed")
            # Clean up topics
            return [topic.strip() for topic in v if topic.strip()]
        return v


class AgentStatusRequest(BaseModel):
    """Request model for checking agent execution status."""
    
    execution_id: str = Field(
        ...,
        description="Execution ID to check status for",
        example="123e4567-e89b-12d3-a456-426614174000"
    )


class AgentListRequest(BaseModel):
    """Request model for listing agents with optional filtering."""
    
    category: Optional[str] = Field(
        default=None,
        description="Filter agents by category",
        example="news"
    )
    
    available_only: bool = Field(
        default=True,
        description="Only return agents that have all required dependencies configured"
    ) 