# calendar_tools for MTEJA AI agents
# Controlled, audited tools that agents may call (no direct DB access)
import os
from langchain_core.tools import tool
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build


@tool
def book_appointment(
    title: str, start_iso: str, end_iso: str, attendee_email: str
) -> str:
  """Book a calendar appointment or support session for a customer.

  Args:
      title: The title of the appointment.
      start_iso: Start time in ISO format (e.g., '2026-06-05T09:00:00Z').
      end_iso: End time in ISO format (e.g., '2026-06-05T10:00:00Z').
      attendee_email: Customer's email address.
  """
  token = os.getenv("GOOGLE_CALENDAR_TOKEN")
  if not token:
    return "Error: Google Calendar token not configured."

  try:
    creds = Credentials(token=token)
    service = build("calendar", "v3", credentials=creds)

    event_body = {
        "summary": title,
        "start": {"dateTime": start_iso, "timeZone": "Africa/Dar_es_Salaam"},
        "end": {"dateTime": end_iso, "timeZone": "Africa/Dar_es_Salaam"},
        "attendees": [{"email": attendee_email}],
    }

    event = (
        service.events().insert(calendarId="primary", body=event_body).execute()
    )
    return (
        f"Appointment successfully booked! View event:"
        f" {event.get('htmlLink')}"
    )
  except Exception as e:
    return f"Failed to book appointment: {str(e)}"


@tool
def list_upcoming_appointments(max_results: int = 5) -> str:
  """List upcoming calendar appointments for staff availability checking."""
  token = os.getenv("GOOGLE_CALENDAR_TOKEN")
  if not token:
    return "Error: Google Calendar token not configured."

  try:
    creds = Credentials(token=token)
    service = build("calendar", "v3", credentials=creds)

    events_result = (
        service.events()
        .list(
            calendarId="primary",
            maxResults=max_results,
            singleEvents=True,
            orderBy="startTime",
        )
        .execute()
    )
    events = events_result.get("items", [])

    if not events:
      return "No upcoming appointments found."

    output = []
    for event in events:
      start = event["start"].get("dateTime", event["start"].get("date"))
      output.append(f"- {event.get('summary')} at {start}")

    return "\n".join(output)
  except Exception as e:
    return f"Failed to retrieve appointments: {str(e)}"


# Export tool list for agent binding
calendar_tools = [book_appointment, list_upcoming_appointments]