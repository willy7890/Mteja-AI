# Structured logging configuration for MTEJA AI
# JSON logs, correlation IDs, audit-friendly format
import logging
import sys


def setup_logging():
  """Configure structured console logging for the MtejaAI backend application."""
  log_level = logging.INFO

  # Create root logger
  logger = logging.getLogger()
  logger.setLevel(log_level)

  # Prevent duplicate handlers if called multiple times
  if logger.hasHandlers():
    logger.handlers.clear()

  # Console Handler
  console_handler = logging.StreamHandler(sys.stdout)
  console_handler.setLevel(log_level)

  # Formatter with timestamp, level, name, and message
  formatter = logging.Formatter(
      "[%(asctime)s] [%(levelname)s] [%(name)s]: %(message)s",
      datefmt="%Y-%m-%d %H:%M:%S",
  )
  console_handler.setFormatter(formatter)
  logger.addHandler(console_handler)

  # Set third-party loggers to warning to keep console clean
  logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
  logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)

  return logger


# Initialize default logger instance
logger = setup_logging()