# messaging_tools for MTEJA AI agents
# Controlled, audited tools that agents may call (no direct DB access)
from langchain_core.tools import tool
from app.services.client import SMSClient, EmailClient, WhatsAppClient


@tool
async def send_sms_message(phone_number: str, message_text: str) -> str:
  """Send an SMS text message to a customer via Africa's Talking.

  Args:
      phone_number: Customer phone number.
      message_text: The message body to transmit.
  """
  success = await SMSClient.send_sms_reply(phone_number, message_text)
  if success:
    return f"SMS successfully sent to {phone_number}."
  return f"Failed to send SMS to {phone_number}."


@tool
def send_email_message(recipient_email: str, subject: str, body: str) -> str:
  """Send an email message to a customer.

  Args:
      recipient_email: Customer email address.
      subject: Subject line of the email.
      body: Plain text email body.
  """
  success = EmailClient.send_email_reply(recipient_email, subject, body)
  if success:
    return f"Email successfully sent to {recipient_email}."
  return f"Failed to send email to {recipient_email}."


@tool
async def send_whatsapp_message(phone_number: str, message_text: str) -> str:
  """Send a WhatsApp message to a customer via Cloud API.

  Args:
      phone_number: Customer WhatsApp phone number.
      message_text: The message content.
  """
  success = await WhatsAppClient.send_whatsapp_reply(phone_number, message_text)
  if success:
    return f"WhatsApp message successfully sent to {phone_number}."
  return f"Failed to send WhatsApp message to {phone_number}."


# Export messaging tools for agent binding
messaging_tools = [
    send_sms_message,
    send_email_message,
    send_whatsapp_message,
]