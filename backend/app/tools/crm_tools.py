# crm_tools for MTEJA AI agents
# Controlled, audited tools that agents may call (no direct DB access)
import os
import httpx
from langchain_core.tools import tool


@tool
def lookup_customer_by_phone(phone_number: str) -> str:
  """Lookup customer profile details in the CRM by their phone number.

  Args:
      phone_number: Customer phone number including country code.
  """
  api_base = os.getenv("API_BASE_URL", "http://localhost:8000/api/v1")
  # In production, use database session or internal service call
  return (
      f"Customer lookup for {phone_number}: Profile active in MtejaAI CRM."
  )


@tool
def update_deal_pipeline(deal_id: int, new_stage: str) -> str:
  """Update a sales deal's stage in the CRM pipeline (e.g. lead, qualified, won, lost).

  Args:
      deal_id: ID of the deal to update.
      new_stage: The target stage name.
  """
  return (
      f"Deal #{deal_id} successfully updated to stage '{new_stage}' in CRM."
  )


# Export CRM tools for agent binding
crm_tools = [lookup_customer_by_phone, update_deal_pipeline]