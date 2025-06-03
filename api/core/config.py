"""
Core configuration management for the Agent API.

This module handles all configuration settings for the production API,
following Agno's best practices for scalable agentic systems.
"""

import os
from typing import Any, Dict, List, Optional
from pydantic_settings import BaseSettings
from pydantic import validator
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings with environment variable support."""
    
    # API Configuration
    app_name: str = "Personal Agent Team API"
    app_version: str = "1.0.0"
    app_description: str = "Production API for managing and executing AI agents"
    debug: bool = False
    
    # Server Configuration
    host: str = "0.0.0.0"
    port: int = 8000
    reload: bool = False
    workers: int = 1
    
    # Database Configuration
    database_url: str = "postgresql://postgres:postgres@localhost:5432/agent_api"
    database_echo: bool = False
    
    # Agent Configuration
    openai_api_key: Optional[str] = None
    anthropic_api_key: Optional[str] = None
    firecrawl_api_key: Optional[str] = None
    apify_api_token: Optional[str] = None
    telegram_bot_token: Optional[str] = None
    telegram_chat_id: Optional[str] = None
    
    # Google Services Configuration
    google_calendar_credentials: Optional[str] = None
    google_api_key: Optional[str] = None
    
    # GitHub Configuration
    github_token: Optional[str] = None
    
    # Environment Configuration
    environment: str = "development"
    
    # Model Configuration
    model_name: str = "gpt-4"
    temperature: float = 0.7
    max_tokens: int = 2000
    
    # Notification Configuration
    notification_driver: Optional[str] = None
    
    # Monitoring and Logging
    log_level: str = "INFO"
    enable_metrics: bool = True
    
    # Agent Execution Limits
    max_concurrent_agents: int = 3
    agent_timeout_seconds: int = 600
    max_articles_per_topic: int = 3
    
    @validator("log_level")
    def validate_log_level(cls, v):
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if v.upper() not in valid_levels:
            raise ValueError(f"Invalid log level. Must be one of: {valid_levels}")
        return v.upper()
    
    @validator("workers")
    def validate_workers(cls, v):
        if v < 1:
            raise ValueError("Workers must be at least 1")
        return v
    
    @validator("max_concurrent_agents")
    def validate_max_concurrent_agents(cls, v):
        if v < 1:
            raise ValueError("Max concurrent agents must be at least 1")
        return v
    
    class Config:
        # Look for .env file in the main project directory (parent of api/)
        env_file = "../.env"
        env_file_encoding = "utf-8"
        case_sensitive = False


class AgentConfig:
    """Configuration for individual agent types."""
    
    AVAILABLE_AGENTS = {
        "enhanced-daily-news": {
            "name": "Enhanced Daily News Agent",
            "description": "Comprehensive news research and summarization with Telegram delivery",
            "module_path": "agents.enhanced-daily-news.agent",
            "function_name": "run_daily_news_research",
            "default_topics": [
                "Bitcoin cryptocurrency",
                "Artificial Intelligence AI", 
                "Politics elections",
                "Finance markets"
            ],
            "max_articles_per_topic": 3,
            "timeout_seconds": 600,
            "requires_telegram": False,
            "requires_firecrawl": False
        },
        "github-trending": {
            "name": "GitHub Trending Repositories Agent",
            "description": "Fetches top 10 trending GitHub repositories from the last week using Agno GitHub tools",
            "module_path": "agents.github-trending.agent",
            "function_name": "run_github_trending_agent",
            "default_parameters": {
                "days_back": 7,
                "max_repos": 10,
                "send_telegram": True
            },
            "timeout_seconds": 300,
            "requires_telegram": False,
            "requires_github": True
        }
        # Future agents can be added here
        # "agent-name": {
        #     "name": "Agent Display Name",
        #     "description": "Agent description",
        #     "module_path": "agents.agent-name.agent",
        #     "function_name": "run_agent_function",
        #     "timeout_seconds": 300,
        #     "requires_telegram": True,
        #     "requires_firecrawl": True
        # }
    }
    
    @classmethod
    def get_agent_config(cls, agent_id: str) -> Optional[Dict[str, Any]]:
        """Get configuration for a specific agent."""
        return cls.AVAILABLE_AGENTS.get(agent_id)
    
    @classmethod
    def list_available_agents(cls) -> List[str]:
        """List all available agent IDs."""
        return list(cls.AVAILABLE_AGENTS.keys())
    
    @classmethod
    def validate_agent_requirements(cls, agent_id: str, settings: Settings) -> List[str]:
        """Validate that agent requirements are met."""
        agent_config = cls.get_agent_config(agent_id)
        if not agent_config:
            return [f"Agent '{agent_id}' not found"]
        
        missing_requirements = []
        
        # Check OpenAI API key (required for all agents)
        if not settings.openai_api_key:
            missing_requirements.append("OPENAI_API_KEY is required")
        
        # Check Telegram requirements
        if agent_config.get("requires_telegram", False):
            if not settings.telegram_bot_token:
                missing_requirements.append("TELEGRAM_BOT_TOKEN is required for this agent")
            if not settings.telegram_chat_id:
                missing_requirements.append("TELEGRAM_CHAT_ID is required for this agent")
        
        # Check Firecrawl requirements
        if agent_config.get("requires_firecrawl", False):
            if not settings.firecrawl_api_key:
                missing_requirements.append("FIRECRAWL_API_KEY is required for this agent")
        
        # Check GitHub requirements
        if agent_config.get("requires_github", False):
            if not settings.github_token:
                missing_requirements.append("GITHUB_TOKEN is recommended for this agent (higher rate limits)")
        
        return missing_requirements


@lru_cache()
def get_settings() -> Settings:
    """Get cached application settings."""
    return Settings()


def get_database_url() -> str:
    """Get database URL with fallback for different environments."""
    settings = get_settings()
    return settings.database_url 