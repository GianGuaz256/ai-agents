"""
News Service

Specialized service for the Enhanced Daily News Agent.
Provides business logic and utilities specific to news operations.
"""

from typing import List, Optional, Dict, Any
from datetime import datetime

from ..core import get_settings, get_logger
from ..models.requests import NewsAgentRequest
from ..models.responses import AgentExecutionResponse
from .agent_manager import AgentManager


class NewsService:
    """Service for handling Enhanced Daily News Agent operations."""
    
    def __init__(self, agent_manager: AgentManager):
        self.agent_manager = agent_manager
        self.settings = get_settings()
        self.logger = get_logger("news_service")
    
    async def execute_news_research(
        self,
        request: NewsAgentRequest,
        async_execution: bool = True
    ) -> AgentExecutionResponse:
        """Execute news research with specific business logic."""
        
        # Prepare parameters for the news agent
        parameters = {}
        
        # Set topics - use provided topics or agent defaults
        if request.topics:
            parameters["topics"] = request.topics
            self.logger.info(f"Using custom topics: {request.topics}")
        else:
            # Will use agent's default topics
            self.logger.info("Using default topics from agent configuration")
        
        # Set article limits
        if request.max_articles_per_topic:
            parameters["max_articles_per_topic"] = request.max_articles_per_topic
        
        # Handle Telegram settings
        if request.enable_telegram is not None:
            # This would require modifying the agent to accept telegram parameter
            # For now, it uses environment variables
            self.logger.info(f"Telegram delivery requested: {request.enable_telegram}")
        
        # Execute the agent
        try:
            response = await self.agent_manager.execute_agent(
                agent_id="enhanced-daily-news",
                parameters=parameters,
                async_execution=async_execution
            )
            
            self.logger.info(
                "News research initiated",
                execution_id=response.execution_id,
                topics=parameters.get("topics", "default"),
                max_articles=parameters.get("max_articles_per_topic", 3)
            )
            
            return response
            
        except Exception as e:
            self.logger.error(f"Failed to execute news research: {str(e)}")
            raise
    
    def get_default_topics(self) -> List[str]:
        """Get the default topics for news research."""
        from ..core.config import AgentConfig
        config = AgentConfig.get_agent_config("enhanced-daily-news")
        return config.get("default_topics", []) if config else []
    
    def validate_topics(self, topics: List[str]) -> Dict[str, Any]:
        """Validate and analyze provided topics."""
        validation_result = {
            "valid": True,
            "issues": [],
            "suggestions": []
        }
        
        if not topics:
            validation_result["valid"] = False
            validation_result["issues"].append("Topics list cannot be empty")
            return validation_result
        
        if len(topics) > 10:
            validation_result["valid"] = False
            validation_result["issues"].append("Maximum 10 topics allowed")
        
        # Check for very short topics
        short_topics = [topic for topic in topics if len(topic.strip()) < 3]
        if short_topics:
            validation_result["issues"].append(f"Topics too short: {short_topics}")
            validation_result["suggestions"].append("Use more descriptive topic names (at least 3 characters)")
        
        # Check for very long topics
        long_topics = [topic for topic in topics if len(topic.strip()) > 100]
        if long_topics:
            validation_result["issues"].append("Some topics are too long")
            validation_result["suggestions"].append("Keep topic descriptions under 100 characters")
        
        # Suggest improvements for common patterns
        crypto_keywords = ["btc", "crypto", "bitcoin", "ethereum"]
        ai_keywords = ["ai", "artificial intelligence", "machine learning", "ml"]
        
        has_crypto = any(keyword in topic.lower() for topic in topics for keyword in crypto_keywords)
        has_ai = any(keyword in topic.lower() for topic in topics for keyword in ai_keywords)
        
        if not has_crypto:
            validation_result["suggestions"].append("Consider adding cryptocurrency/Bitcoin topics for comprehensive coverage")
        
        if not has_ai:
            validation_result["suggestions"].append("Consider adding AI/technology topics for comprehensive coverage")
        
        return validation_result
    
    def get_execution_summary(self, execution_id: str) -> Optional[Dict[str, Any]]:
        """Get a summary of a news research execution."""
        execution = self.agent_manager.get_execution_status(execution_id)
        if not execution:
            return None
        
        summary = {
            "execution_id": execution.execution_id,
            "status": execution.status,
            "created_at": execution.created_at,
            "completed_at": execution.completed_at,
            "duration_seconds": execution.duration_seconds,
            "topics_researched": execution.parameters.get("topics", "default"),
            "max_articles_per_topic": execution.parameters.get("max_articles_per_topic", 3),
            "result_available": execution.result is not None,
            "error_occurred": execution.error_message is not None
        }
        
        # Add result length if available
        if execution.result:
            summary["result_length"] = len(execution.result)
            summary["result_preview"] = execution.result[:200] + "..." if len(execution.result) > 200 else execution.result
        
        # Add error info if available
        if execution.error_message:
            summary["error_message"] = execution.error_message
        
        return summary
    
    def get_news_metrics(self) -> Dict[str, Any]:
        """Get metrics specific to news agent executions."""
        all_metrics = self.agent_manager.get_metrics()
        
        # Filter for news agent only
        news_executions = [
            ctx for ctx in self.agent_manager.executions.values()
            if ctx.agent_id == "enhanced-daily-news"
        ]
        
        if not news_executions:
            return {
                "total_news_executions": 0,
                "successful_news_executions": 0,
                "failed_news_executions": 0,
                "average_duration_seconds": 0,
                "most_common_topics": [],
                "recent_executions": []
            }
        
        successful = sum(1 for ctx in news_executions if ctx.status.value == "completed")
        failed = sum(1 for ctx in news_executions if ctx.status.value == "failed")
        
        # Calculate average duration for completed news executions
        completed_durations = [
            ctx.duration_seconds for ctx in news_executions
            if ctx.duration_seconds is not None and ctx.status.value == "completed"
        ]
        avg_duration = sum(completed_durations) / len(completed_durations) if completed_durations else 0
        
        # Analyze most common topics
        topic_counts = {}
        for ctx in news_executions:
            topics = ctx.parameters.get("topics", [])
            if isinstance(topics, list):
                for topic in topics:
                    topic_counts[topic] = topic_counts.get(topic, 0) + 1
        
        most_common_topics = sorted(topic_counts.items(), key=lambda x: x[1], reverse=True)[:5]
        
        # Get recent executions
        recent_executions = sorted(
            news_executions,
            key=lambda ctx: ctx.created_at,
            reverse=True
        )[:5]
        
        recent_execution_summaries = [
            {
                "execution_id": ctx.execution_id,
                "status": ctx.status.value,
                "created_at": ctx.created_at.isoformat(),
                "duration_seconds": ctx.duration_seconds,
                "topics": ctx.parameters.get("topics", "default")
            }
            for ctx in recent_executions
        ]
        
        return {
            "total_news_executions": len(news_executions),
            "successful_news_executions": successful,
            "failed_news_executions": failed,
            "average_duration_seconds": round(avg_duration, 2),
            "most_common_topics": most_common_topics,
            "recent_executions": recent_execution_summaries
        } 