# Background task definitions for MTEJA AI
# Async jobs: AI processing, message delivery, analytics, retries
import asyncio
import logging
from app.services.client import SMSClient, EmailClient

logger = logging.getLogger(__name__)


async def background_send_message_task(
    channel: str, recipient: str, content: str, subject: str = "Notification"
):
  """Background task to dispatch messages asynchronously without blocking API responses."""
  try:
    logger.info(f"Starting background task: sending {channel} to {recipient}")

    if channel == "sms":
      await SMSClient.send_sms_reply(recipient, content)
    elif channel == "email":
      EmailClient.send_email_reply(recipient, subject, content)
    else:
      logger.warning(f"Unsupported background task channel: {channel}")

  except Exception as e:
    logger.error(f"Error in background message task: {str(e)}")


def run_background_task(coroutine):
  """Helper wrapper to schedule coroutines in the background event loop."""
  try:
    loop = asyncio.get_event_loop()
    if loop.is_running():
      asyncio.create_task(coroutine)
    else:
      asyncio.run(coroutine)
  except Exception as e:
    logger.error(f"Failed to run background task: {str(e)}")