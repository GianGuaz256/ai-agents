"""
Agent Manager Service

This service handles agent execution, management, and status tracking
for the production API. It provides a scalable way to manage multiple
agents following Agno's best practices.
"""

import asyncio
import uuid
import importlib
import sys
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Callable
from concurrent.futures import ThreadPoolExecutor, Future
from dataclasses import dataclass

from ..core import get_settings, AgentConfig, get_logger, log_agent_execution
from ..models.responses import ExecutionStatus, AgentInfo, AgentExecutionResponse


@dataclass
class ExecutionContext:
    """Context for an agent execution."""
    execution_id: str
    agent_id: str
    parameters: Dict[str, Any]
    created_at: datetime
    status: ExecutionStatus
    future: Optional[Future] = None
    result: Optional[str] = None
    error_message: Optional[str] = None
    completed_at: Optional[datetime] = None
    duration_seconds: Optional[float] = None


class AgentManager:
    """Manages agent execution and lifecycle in a production environment."""
    
    def __init__(self):
        self.settings = get_settings()
        self.logger = get_logger("agent_manager")
        self.executor = ThreadPoolExecutor(max_workers=self.settings.max_concurrent_agents)
        self.executions: Dict[str, ExecutionContext] = {}
        self._setup_agent_paths()
    
    def _setup_agent_paths(self):
        """Setup Python path to include agents directory."""
        # Add the project root to Python path so we can import agents
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        if project_root not in sys.path:
            sys.path.insert(0, project_root)
        
        self.logger.info("Agent paths configured", project_root=project_root)
    
    def list_agents(self, available_only: bool = True) -> List[AgentInfo]:
        """List all available agents with their configuration."""
        agents = []
        
        for agent_id, config in AgentConfig.AVAILABLE_AGENTS.items():
            # Check if agent requirements are met
            missing_requirements = AgentConfig.validate_agent_requirements(agent_id, self.settings)
            requirements_met = len(missing_requirements) == 0
            available = requirements_met
            
            # Skip unavailable agents if requested
            if available_only and not available:
                continue
            
            agent_info = AgentInfo(
                id=agent_id,
                name=config["name"],
                description=config["description"],
                category=self._get_agent_category(agent_id),
                available=available,
                requirements_met=requirements_met,
                missing_requirements=missing_requirements,
                default_parameters=self._get_default_parameters(agent_id),
                timeout_seconds=config.get("timeout_seconds", 300)
            )
            agents.append(agent_info)
        
        self.logger.info("Listed agents", total_count=len(agents), available_only=available_only)
        return agents
    
    def _get_agent_category(self, agent_id: str) -> str:
        """Get category for an agent based on its ID."""
        if "news" in agent_id:
            return "news"
        elif "finance" in agent_id:
            return "finance"
        elif "research" in agent_id:
            return "research"
        else:
            return "general"
    
    def _get_default_parameters(self, agent_id: str) -> Dict[str, Any]:
        """Get default parameters for an agent."""
        config = AgentConfig.get_agent_config(agent_id)
        if not config:
            return {}
        
        defaults = {}
        if "default_topics" in config:
            defaults["topics"] = config["default_topics"]
        if "max_articles_per_topic" in config:
            defaults["max_articles_per_topic"] = config["max_articles_per_topic"]
        
        return defaults
    
    async def execute_agent(
        self,
        agent_id: str,
        parameters: Dict[str, Any],
        async_execution: bool = True
    ) -> AgentExecutionResponse:
        """Execute an agent with the given parameters."""
        # Validate agent exists and requirements are met
        agent_config = AgentConfig.get_agent_config(agent_id)
        if not agent_config:
            raise ValueError(f"Agent '{agent_id}' not found")
        
        missing_requirements = AgentConfig.validate_agent_requirements(agent_id, self.settings)
        if missing_requirements:
            raise ValueError(f"Agent requirements not met: {', '.join(missing_requirements)}")
        
        # Create execution context
        execution_id = str(uuid.uuid4())
        context = ExecutionContext(
            execution_id=execution_id,
            agent_id=agent_id,
            parameters=parameters,
            created_at=datetime.utcnow(),
            status=ExecutionStatus.PENDING
        )
        
        self.executions[execution_id] = context
        
        log_agent_execution(
            agent_id=agent_id,
            execution_id=execution_id,
            status="started",
            parameters=parameters
        )
        
        if async_execution:
            # Submit to thread pool for async execution
            context.future = self.executor.submit(self._execute_agent_sync, context)
            context.status = ExecutionStatus.RUNNING
            
            # Return immediately for async execution
            return AgentExecutionResponse(
                execution_id=execution_id,
                agent_id=agent_id,
                status=context.status,
                created_at=context.created_at,
                parameters=parameters
            )
        else:
            # Execute synchronously
            await self._execute_agent_async(context)
            return self._context_to_response(context)
    
    def _execute_agent_sync(self, context: ExecutionContext) -> None:
        """Execute an agent synchronously in a thread."""
        try:
            context.status = ExecutionStatus.RUNNING
            start_time = datetime.utcnow()
            
            # Import and execute the agent
            result = self._run_agent_function(context.agent_id, context.parameters)
            
            # Update context with success
            context.status = ExecutionStatus.COMPLETED
            context.result = result
            context.completed_at = datetime.utcnow()
            context.duration_seconds = (context.completed_at - start_time).total_seconds()
            
            log_agent_execution(
                agent_id=context.agent_id,
                execution_id=context.execution_id,
                status="completed",
                duration_seconds=context.duration_seconds
            )
            
        except Exception as e:
            # Update context with error
            context.status = ExecutionStatus.FAILED
            context.error_message = str(e)
            context.completed_at = datetime.utcnow()
            context.duration_seconds = (context.completed_at - context.created_at).total_seconds()
            
            log_agent_execution(
                agent_id=context.agent_id,
                execution_id=context.execution_id,
                status="failed",
                duration_seconds=context.duration_seconds,
                error_message=context.error_message
            )
            
            self.logger.error(
                "Agent execution failed",
                agent_id=context.agent_id,
                execution_id=context.execution_id,
                error=str(e)
            )
    
    async def _execute_agent_async(self, context: ExecutionContext) -> None:
        """Execute an agent asynchronously."""
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(self.executor, self._execute_agent_sync, context)
    
    def _run_agent_function(self, agent_id: str, parameters: Dict[str, Any]) -> str:
        """Import and run the agent function."""
        agent_config = AgentConfig.get_agent_config(agent_id)
        if not agent_config:
            raise ValueError(f"Agent '{agent_id}' configuration not found")
        
        module_path = agent_config["module_path"]
        function_name = agent_config["function_name"]
        
        try:
            # Import the agent module
            module = importlib.import_module(module_path)
            
            # Get the agent function
            agent_function = getattr(module, function_name)
            
            # Prepare parameters based on agent type
            if agent_id == "enhanced-daily-news":
                # Special handling for news agent
                topics = parameters.get("topics")
                max_articles = parameters.get("max_articles_per_topic", 3)
                
                # Call the news agent function
                result = agent_function(topics=topics, max_articles_per_topic=max_articles)
            else:
                # Generic agent execution
                result = agent_function(**parameters)
            
            return result or "Agent executed successfully"
            
        except ImportError as e:
            raise RuntimeError(f"Failed to import agent module '{module_path}': {e}")
        except AttributeError as e:
            raise RuntimeError(f"Agent function '{function_name}' not found in module '{module_path}': {e}")
        except Exception as e:
            raise RuntimeError(f"Agent execution failed: {e}")
    
    def get_execution_status(self, execution_id: str) -> Optional[AgentExecutionResponse]:
        """Get the status of an agent execution."""
        context = self.executions.get(execution_id)
        if not context:
            return None
        
        # Check if future is complete
        if context.future and context.future.done():
            if context.status not in [ExecutionStatus.COMPLETED, ExecutionStatus.FAILED]:
                # Update status from completed future
                try:
                    context.future.result()  # This will raise if there was an exception
                except Exception:
                    pass  # Status should already be updated by _execute_agent_sync
        
        return self._context_to_response(context)
    
    def _context_to_response(self, context: ExecutionContext) -> AgentExecutionResponse:
        """Convert execution context to response model."""
        return AgentExecutionResponse(
            execution_id=context.execution_id,
            agent_id=context.agent_id,
            status=context.status,
            created_at=context.created_at,
            completed_at=context.completed_at,
            result=context.result,
            error_message=context.error_message,
            parameters=context.parameters,
            duration_seconds=context.duration_seconds
        )
    
    def cleanup_old_executions(self, max_age_hours: int = 24) -> int:
        """Clean up old execution records."""
        cutoff_time = datetime.utcnow() - timedelta(hours=max_age_hours)
        removed_count = 0
        
        execution_ids_to_remove = []
        for execution_id, context in self.executions.items():
            if context.created_at < cutoff_time:
                execution_ids_to_remove.append(execution_id)
        
        for execution_id in execution_ids_to_remove:
            del self.executions[execution_id]
            removed_count += 1
        
        if removed_count > 0:
            self.logger.info(f"Cleaned up {removed_count} old execution records")
        
        return removed_count
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get agent execution metrics."""
        total_executions = len(self.executions)
        successful_executions = sum(1 for ctx in self.executions.values() if ctx.status == ExecutionStatus.COMPLETED)
        failed_executions = sum(1 for ctx in self.executions.values() if ctx.status == ExecutionStatus.FAILED)
        
        # Calculate average duration for completed executions
        completed_durations = [ctx.duration_seconds for ctx in self.executions.values() 
                             if ctx.duration_seconds is not None]
        avg_duration = sum(completed_durations) / len(completed_durations) if completed_durations else 0
        
        # Count executions per agent
        executions_per_agent = {}
        for ctx in self.executions.values():
            executions_per_agent[ctx.agent_id] = executions_per_agent.get(ctx.agent_id, 0) + 1
        
        return {
            "total_executions": total_executions,
            "successful_executions": successful_executions,
            "failed_executions": failed_executions,
            "average_duration_seconds": avg_duration,
            "executions_per_agent": executions_per_agent
        }
    
    def shutdown(self):
        """Shutdown the agent manager and cleanup resources."""
        self.logger.info("Shutting down agent manager")
        self.executor.shutdown(wait=True) 