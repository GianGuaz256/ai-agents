"""
Agent management router.

This router handles all agent-related endpoints including listing agents,
executing agents, and monitoring execution status.
"""

from typing import List, Optional, Dict, Any
from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks, Query, Path
from fastapi.responses import JSONResponse

from ..models.requests import AgentExecutionRequest, NewsAgentRequest, AgentStatusRequest
from ..models.responses import (
    AgentListResponse, AgentExecutionResponse, AgentStatusResponse, 
    ErrorResponse, MetricsResponse, AgentInfo
)
from ..services import AgentManager
from ..core import get_logger, log_api_request, get_settings

router = APIRouter(prefix="/agents", tags=["agents"])
logger = get_logger("agents_router")

# Dependency injection for services
def get_agent_manager() -> AgentManager:
    """Get agent manager instance."""
    return AgentManager()


@router.get("/", response_model=AgentListResponse)
async def list_agents(
    available_only: bool = Query(True, description="Only return available agents"),
    category: Optional[str] = Query(None, description="Filter by agent category"),
    agent_manager: AgentManager = Depends(get_agent_manager)
) -> AgentListResponse:
    """
    List all available agents with their configuration and status.
    
    - **available_only**: If true, only returns agents with all requirements met
    - **category**: Filter agents by category (news, finance, research, etc.)
    """
    try:
        agents = agent_manager.list_agents(available_only=available_only)
        
        # Filter by category if specified
        if category:
            agents = [agent for agent in agents if agent.category == category.lower()]
        
        response = AgentListResponse(
            agents=agents,
            total_count=len(agents),
            available_count=sum(1 for agent in agents if agent.available)
        )
        
        logger.info(
            "Listed agents",
            total_count=response.total_count,
            available_count=response.available_count,
            category_filter=category
        )
        
        return response
        
    except Exception as e:
        logger.error(f"Error listing agents: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to list agents: {str(e)}"
        )


@router.get("/{agent_id}", response_model=AgentInfo)
async def get_agent_info(
    agent_id: str = Path(..., description="Agent ID to get information for"),
    agent_manager: AgentManager = Depends(get_agent_manager)
) -> AgentInfo:
    """
    Get detailed information about a specific agent.
    
    - **agent_id**: The unique identifier for the agent
    """
    try:
        agents = agent_manager.list_agents(available_only=False)
        agent = next((a for a in agents if a.id == agent_id), None)
        
        if not agent:
            raise HTTPException(
                status_code=404,
                detail=f"Agent '{agent_id}' not found"
            )
        
        logger.info(f"Retrieved agent info for {agent_id}")
        return agent
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting agent info for {agent_id}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get agent information: {str(e)}"
        )


@router.post("/execute", response_model=AgentExecutionResponse)
async def execute_agent(
    request: AgentExecutionRequest,
    background_tasks: BackgroundTasks,
    agent_manager: AgentManager = Depends(get_agent_manager)
) -> AgentExecutionResponse:
    """
    Execute an agent with the specified parameters.
    
    - **agent_id**: The agent to execute
    - **parameters**: Agent-specific parameters
    - **async_execution**: Whether to execute asynchronously (default: true)
    - **callback_url**: URL to call when execution completes (for async)
    """
    try:
        response = await agent_manager.execute_agent(
            agent_id=request.agent_id,
            parameters=request.parameters,
            async_execution=request.async_execution
        )
        
        logger.info(
            "Agent execution initiated",
            agent_id=request.agent_id,
            execution_id=response.execution_id,
            async_execution=request.async_execution
        )
        
        return response
        
    except ValueError as e:
        logger.warning(f"Invalid agent execution request: {str(e)}")
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error executing agent {request.agent_id}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to execute agent: {str(e)}"
        )


@router.get("/executions/{execution_id}", response_model=AgentStatusResponse)
async def get_execution_status(
    execution_id: str = Path(..., description="Execution ID to check status for"),
    agent_manager: AgentManager = Depends(get_agent_manager)
) -> AgentStatusResponse:
    """
    Get the status of an agent execution.
    
    - **execution_id**: The unique execution identifier returned when starting an execution
    """
    try:
        execution = agent_manager.get_execution_status(execution_id)
        
        if not execution:
            raise HTTPException(
                status_code=404,
                detail=f"Execution '{execution_id}' not found"
            )
        
        # Convert to status response format
        response = AgentStatusResponse(
            execution_id=execution.execution_id,
            agent_id=execution.agent_id,
            status=execution.status,
            created_at=execution.created_at,
            updated_at=execution.completed_at or execution.created_at,
            completed_at=execution.completed_at,
            result=execution.result,
            error_message=execution.error_message,
            duration_seconds=execution.duration_seconds
        )
        
        logger.info(
            "Retrieved execution status",
            execution_id=execution_id,
            status=execution.status.value
        )
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting execution status for {execution_id}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get execution status: {str(e)}"
        )


@router.post("/news/execute", response_model=AgentExecutionResponse)
async def execute_news_agent(
    request: NewsAgentRequest,
    async_execution: bool = Query(True, description="Execute asynchronously"),
    agent_manager: AgentManager = Depends(get_agent_manager)
) -> AgentExecutionResponse:
    """
    Execute the Enhanced Daily News Agent with specific parameters.
    
    - **topics**: List of topics to research (optional, uses defaults if not provided)
    - **max_articles_per_topic**: Maximum articles to research per topic (1-10)
    - **enable_telegram**: Whether to send results via Telegram
    - **async_execution**: Whether to execute asynchronously
    """
    try:
        # Execute as regular agent
        parameters = {
            "topics": request.topics or [
                "Bitcoin cryptocurrency",
                "Artificial Intelligence AI",
                "Politics elections", 
                "Finance markets"
            ],
            "max_articles_per_topic": request.max_articles_per_topic,
            "enable_telegram": request.enable_telegram
        }
        
        response = await agent_manager.execute_agent(
            agent_id="enhanced-daily-news",
            parameters=parameters,
            async_execution=async_execution
        )
        
        logger.info(
            "News agent execution initiated",
            execution_id=response.execution_id,
            topics=request.topics or "default",
            max_articles=request.max_articles_per_topic
        )
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error executing news agent: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to execute news agent: {str(e)}"
        )


@router.get("/metrics", response_model=MetricsResponse)
async def get_metrics(
    agent_manager: AgentManager = Depends(get_agent_manager)
) -> MetricsResponse:
    """
    Get comprehensive metrics about agent executions.
    
    Returns statistics about execution counts, success rates, performance, etc.
    """
    try:
        metrics = agent_manager.get_metrics()
        
        # Get recent executions for the response
        recent_executions = []
        executions_list = list(agent_manager.executions.items())
        for execution_id, context in executions_list[-10:]:
            recent_executions.append(AgentExecutionResponse(
                execution_id=context.execution_id,
                agent_id=context.agent_id,
                status=context.status,
                created_at=context.created_at,
                completed_at=context.completed_at,
                result=context.result,
                error_message=context.error_message,
                parameters=context.parameters,
                duration_seconds=context.duration_seconds
            ))
        
        response = MetricsResponse(
            total_executions=metrics["total_executions"],
            successful_executions=metrics["successful_executions"],
            failed_executions=metrics["failed_executions"],
            average_duration_seconds=metrics["average_duration_seconds"],
            executions_per_agent=metrics["executions_per_agent"],
            recent_executions=recent_executions,
            uptime_seconds=0  # Could implement uptime tracking
        )
        
        logger.info("Retrieved agent metrics")
        return response
        
    except Exception as e:
        logger.error(f"Error getting metrics: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get metrics: {str(e)}"
        )


@router.get("/schedule", tags=["scheduler"])
async def get_scheduled_jobs() -> Dict[str, Any]:
    """
    Get information about all scheduled agent jobs.
    
    Returns details about cron jobs, next execution times, and schedule status.
    """
    try:
        # Import here to avoid circular imports
        from ..main import scheduler_service
        
        if not scheduler_service:
            raise HTTPException(
                status_code=503,
                detail="Scheduler service not available"
            )
        
        jobs = scheduler_service.get_scheduled_jobs()
        
        response = {
            "scheduler_running": scheduler_service.is_running(),
            "total_jobs": len(jobs),
            "jobs": jobs,
            "timezone": "Europe/Rome (CET)"
        }
        
        logger.info("Retrieved scheduled jobs information")
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting scheduled jobs: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get scheduled jobs: {str(e)}"
        ) 