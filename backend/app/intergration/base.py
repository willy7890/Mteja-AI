# Base integration adapter interface for MTEJA AI
# Defines common methods: authenticate, send_message, handle_webhook, normalize_event
from abc import ABC, abstractmethod


class BaseIntegration(ABC):
  """Abstract Base Class for all MtejaAI social media and communication integrations.

  Every channel client must inherit from this and implement `send_message`.
  """

  @abstractmethod
  async def send_message(self, recipient: str, text: str, **kwargs) -> bool:
    """Send an outbound message to a customer on this specific channel.

    Args:
        recipient: The phone number, email address, or platform user ID.
        text: The content of the message to send.
        **kwargs: Additional optional channel-specific parameters (e.g.,
          subject for email).

    Returns:
        bool: True if sent successfully, False otherwise.
    """
    pass