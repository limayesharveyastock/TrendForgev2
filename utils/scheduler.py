"""
utils/scheduler.py
==================

Centralized task scheduler for TrendForge.

Features
--------
✓ Interval jobs
✓ Daily jobs
✓ Cron jobs
✓ One-time jobs
✓ Background scheduler
✓ Job management
✓ Thread-safe
✓ Logging
✓ Graceful shutdown

Dependencies
------------
pip install apscheduler

Used by
-------
- scanner_engine
- news_service
- corporate_action_service
- notification_manager
- report_generator
- portfolio_manager
- ai_engine
"""

from __future__ import annotations

import atexit
from datetime import datetime
from typing import Callable, Dict, List, Optional

from apscheduler.executors.pool import ThreadPoolExecutor
from apscheduler.jobstores.memory import MemoryJobStore
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.date import DateTrigger
from apscheduler.triggers.interval import IntervalTrigger

from utils.logger import LoggerManager

logger = LoggerManager.get_logger(__name__)


class SchedulerManager:

    _instance = None

    def __new__(cls):

        if cls._instance is None:

            cls._instance = super().__new__(cls)

        return cls._instance

    ###############################################################

    def __init__(self):

        if hasattr(self, "_initialized"):
            return

        self.scheduler = BackgroundScheduler(

            jobstores={
                "default": MemoryJobStore()
            },

            executors={
                "default": ThreadPoolExecutor(20)
            },

            job_defaults={
                "coalesce": False,
                "max_instances": 3,
                "misfire_grace_time": 60
            }

        )

        self.scheduler.start()

        atexit.register(self.shutdown)

        self._initialized = True

        logger.info("Scheduler started.")

    ###############################################################
    # Interval Jobs
    ###############################################################

    def every_seconds(
        self,
        seconds: int,
        func: Callable,
        job_id: str,
        *args,
        **kwargs
    ):

        self.scheduler.add_job(

            func,

            trigger=IntervalTrigger(
                seconds=seconds
            ),

            args=args,

            kwargs=kwargs,

            id=job_id,

            replace_existing=True

        )

        logger.info("Added interval job %s", job_id)

    ###############################################################

    def every_minutes(
        self,
        minutes: int,
        func: Callable,
        job_id: str,
        *args,
        **kwargs
    ):

        self.scheduler.add_job(

            func,

            trigger=IntervalTrigger(
                minutes=minutes
            ),

            args=args,

            kwargs=kwargs,

            id=job_id,

            replace_existing=True

        )

    ###############################################################

    def every_hours(
        self,
        hours: int,
        func: Callable,
        job_id: str,
        *args,
        **kwargs
    ):

        self.scheduler.add_job(

            func,

            trigger=IntervalTrigger(
                hours=hours
            ),

            args=args,

            kwargs=kwargs,

            id=job_id,

            replace_existing=True

        )

    ###############################################################
    # Daily Job
    ###############################################################

    def daily(
        self,
        hour: int,
        minute: int,
        func: Callable,
        job_id: str,
        *args,
        **kwargs
    ):

        self.scheduler.add_job(

            func,

            trigger=CronTrigger(
                hour=hour,
                minute=minute
            ),

            args=args,

            kwargs=kwargs,

            id=job_id,

            replace_existing=True

        )

    ###############################################################
    # Weekly Job
    ###############################################################

    def weekly(
        self,
        day_of_week: str,
        hour: int,
        minute: int,
        func: Callable,
        job_id: str,
        *args,
        **kwargs
    ):

        self.scheduler.add_job(

            func,

            trigger=CronTrigger(

                day_of_week=day_of_week,

                hour=hour,

                minute=minute

            ),

            args=args,

            kwargs=kwargs,

            id=job_id,

            replace_existing=True

        )

    ###############################################################
    # Monthly Job
    ###############################################################

    def monthly(
        self,
        day: int,
        hour: int,
        minute: int,
        func: Callable,
        job_id: str,
        *args,
        **kwargs
    ):

        self.scheduler.add_job(

            func,

            trigger=CronTrigger(

                day=day,

                hour=hour,

                minute=minute

            ),

            args=args,

            kwargs=kwargs,

            id=job_id,

            replace_existing=True

        )

    ###############################################################
    # Cron
    ###############################################################

    def cron(
        self,
        expression: Dict,
        func: Callable,
        job_id: str,
        *args,
        **kwargs
    ):

        self.scheduler.add_job(

            func,

            trigger=CronTrigger(
                **expression
            ),

            args=args,

            kwargs=kwargs,

            id=job_id,

            replace_existing=True

        )

    ###############################################################
    # Run Once
    ###############################################################

    def once(
        self,
        run_time: datetime,
        func: Callable,
        job_id: str,
        *args,
        **kwargs
    ):

        self.scheduler.add_job(

            func,

            trigger=DateTrigger(
                run_date=run_time
            ),

            args=args,

            kwargs=kwargs,

            id=job_id,

            replace_existing=True

        )

    ###############################################################
    # Manual Execution
    ###############################################################

    def run_now(
        self,
        func: Callable,
        *args,
        **kwargs
    ):

        logger.info(
            "Running %s immediately.",
            func.__name__
        )

        return func(*args, **kwargs)

    ###############################################################
    # Remove Job
    ###############################################################

    def remove(self, job_id: str):

        try:

            self.scheduler.remove_job(job_id)

            logger.info(
                "Removed job %s",
                job_id
            )

        except Exception:

            logger.warning(
                "Job %s not found.",
                job_id
            )

    ###############################################################
    # Pause / Resume
    ###############################################################

    def pause(self, job_id):

        self.scheduler.pause_job(job_id)

    def resume(self, job_id):

        self.scheduler.resume_job(job_id)

    ###############################################################
    # Job Information
    ###############################################################

    def jobs(self):

        return self.scheduler.get_jobs()

    def exists(self, job_id):

        return self.scheduler.get_job(job_id) is not None

    ###############################################################
    # Shutdown
    ###############################################################

    def shutdown(self):

        if self.scheduler.running:

            logger.info("Stopping scheduler...")

            self.scheduler.shutdown(wait=False)

    ###############################################################
    # Default TrendForge Jobs
    ###############################################################

    def register_default_jobs(
        self,
        scanner_engine=None,
        news_service=None,
        corporate_service=None,
        report_service=None,
        portfolio_manager=None
    ):
        """
        Register common TrendForge background jobs.
        Pass only the services you use.
        """

        if scanner_engine:

            self.every_minutes(
                1,
                scanner_engine.scan_market,
                "market_scan"
            )

        if news_service:

            self.every_minutes(
                10,
                news_service.refresh,
                "news_refresh"
            )

        if corporate_service:

            self.every_hours(
                6,
                corporate_service.refresh,
                "corporate_refresh"
            )

        if portfolio_manager:

            self.every_minutes(
                5,
                portfolio_manager.refresh,
                "portfolio_refresh"
            )

        if report_service:

            self.daily(
                18,
                30,
                report_service.generate_daily_report,
                "daily_report"
            )


###################################################################
# Singleton Instance
###################################################################

scheduler = SchedulerManager()