# Task scheduler for MTEJA AI
# Periodic jobs, follow-ups, campaign triggers, health checks
from apscheduler.schedulers.asyncio import AsyncIOScheduler
import logging

logger = logging.getLogger(__name__)

# Initialize background scheduler instance
scheduler = AsyncIOScheduler()


async def scheduled_email_poll_task():
  """Background task to poll unread customer support emails."""
  logger.info("Running scheduled background task: Polling incoming emails...")
  # Add email polling service call here when active


async def scheduled_campaign_dispatch_task():
  """Background task to check and dispatch scheduled broadcast campaigns."""
  logger.info("Running scheduled background task: Checking campaigns...")
  # Add campaign service dispatcher call here when active


def start_scheduler():
  """Start the background scheduler on FastAPI application startup."""
  if not scheduler.running:
    # Schedule email polling every 5 minutes
    scheduler.add_job(
        scheduled_email_poll_task, "interval", minutes=5, id="poll_emails"
    )

    # Schedule campaign checker every 15 minutes
    scheduler.add_job(
        scheduled_campaign_dispatch_task,
        "interval",
        minutes=15,
        id="dispatch_campaigns",
    )

    scheduler.start()
    logger.info("Background task scheduler started successfully.")


def shutdown_scheduler():
  """Shutdown the background scheduler gracefully on application shutdown."""
  if scheduler.running:
    scheduler.shutdown()
    logger.info("Background task scheduler shut down.")