"""
Scheduler service for automated agent execution.

This module handles scheduled execution of agents using APScheduler.
"""

import asyncio
from datetime import datetime
from typing import Optional
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.jobstores.memory import MemoryJobStore
from apscheduler.executors.asyncio import AsyncIOExecutor

from ..core import get_logger, get_settings, log_system_event
from .agent_manager import AgentManager


class SchedulerService:
    """Service for scheduling automated agent executions."""
    
    def __init__(self):
        self.logger = get_logger("scheduler")
        self.settings = get_settings()
        self.agent_manager: Optional[AgentManager] = None
        
        # Configure scheduler
        jobstores = {
            'default': MemoryJobStore()
        }
        executors = {
            'default': AsyncIOExecutor()
        }
        job_defaults = {
            'coalesce': False,
            'max_instances': 1
        }
        
        self.scheduler = AsyncIOScheduler(
            jobstores=jobstores,
            executors=executors,
            job_defaults=job_defaults,
            timezone='Europe/Rome'  # CET timezone
        )
        
    def set_agent_manager(self, agent_manager: AgentManager):
        """Set the agent manager instance."""
        self.agent_manager = agent_manager
        
    async def start(self):
        """Start the scheduler and add default jobs."""
        self.logger.info("Starting scheduler service")
        
        # Add scheduled jobs
        await self._add_daily_news_jobs()
        
        # Start the scheduler
        self.scheduler.start()
        
        log_system_event(
            event_type="scheduler_started",
            message="Scheduler service started successfully"
        )
        
    async def stop(self):
        """Stop the scheduler."""
        self.logger.info("Stopping scheduler service")
        self.scheduler.shutdown()
        
        log_system_event(
            event_type="scheduler_stopped",
            message="Scheduler service stopped"
        )
    
    async def _add_daily_news_jobs(self):
        """Add scheduled jobs for daily news agent."""
        agent_id = "enhanced-daily-news"
        
        # Morning job at 9:00 AM CET
        self.scheduler.add_job(
            func=self._run_daily_news_agent,
            trigger=CronTrigger(hour=9, minute=0, timezone='Europe/Rome'),
            id=f"{agent_id}_morning",
            name="Daily News Agent - Morning",
            replace_existing=True
        )
        
        # Afternoon job at 3:10 PM CET  
        self.scheduler.add_job(
            func=self._run_daily_news_agent,
            trigger=CronTrigger(hour=15, minute=0, timezone='Europe/Rome'),
            id=f"{agent_id}_afternoon", 
            name="Daily News Agent - Afternoon",
            replace_existing=True
        )
        
        self.logger.info(
            "Scheduled daily news agent",
            jobs=["9:00 AM CET", "3:00 PM CET"]
        )
    
    async def _run_daily_news_agent(self):
        """Execute the enhanced daily news agent."""
        if not self.agent_manager:
            self.logger.error("Agent manager not available for scheduled execution")
            return
            
        try:
            self.logger.info("Starting scheduled execution of daily news agent")
            
            # Default parameters for the news agent
            parameters = {
                "topics": [
                    "Bitcoin cryptocurrency",
                    "Artificial Intelligence AI",
                    "Politics elections",
                    "Finance markets"
                ],
                "max_articles_per_topic": 3,
                "scheduled": True,
                "execution_time": datetime.now().isoformat()
            }
            
            # Execute the agent
            execution_result = await self.agent_manager.execute_agent(
                agent_id="enhanced-daily-news",
                parameters=parameters
            )
            
            self.logger.info(
                "Scheduled daily news agent execution completed",
                execution_id=execution_result.execution_id,
                status=execution_result.status
            )
            
            log_system_event(
                event_type="scheduled_execution_completed",
                message="Daily news agent executed successfully",
                agent_id="enhanced-daily-news",
                execution_id=execution_result.execution_id
            )
            
        except Exception as e:
            self.logger.error(
                "Scheduled daily news agent execution failed",
                error=str(e),
                error_type=type(e).__name__
            )
            
            log_system_event(
                event_type="scheduled_execution_failed", 
                message=f"Daily news agent execution failed: {str(e)}",
                agent_id="enhanced-daily-news",
                error=str(e)
            )
    
    def get_scheduled_jobs(self) -> list:
        """Get list of all scheduled jobs."""
        jobs = []
        for job in self.scheduler.get_jobs():
            jobs.append({
                "id": job.id,
                "name": job.name,
                "next_run_time": job.next_run_time.isoformat() if job.next_run_time else None,
                "trigger": str(job.trigger)
            })
        return jobs
    
    def is_running(self) -> bool:
        """Check if scheduler is running."""
        return self.scheduler.running 