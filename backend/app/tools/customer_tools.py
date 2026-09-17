# customer_tools for MTEJA AI agents
# Controlled, audited tools that agents may call (no direct DB access)
from langchain_core.tools import tool


@tool
def create_customer_profile(name: str, phone: str, email: str) -> str:
  """Register a new customer profile in the MtejaAI database.

  Args:
      name: Full name of the customer or student.
      phone: Phone number with country code.
      email: Email address.
  """
  # In production, integrate with database session or internal service
  return (
      f"Customer {name} ({phone}) has been successfully registered in the system."
  )


@tool
def get_customer_summary(customer_id: int) -> str:
  """Retrieve customer summary and past interaction history.

  Args:
      customer_id: The unique database ID of the customer.
  """
  return f"Customer #{customer_id} summary: 3 previous resolved inquiries, active status."


# Export customer tools for agent binding
customer_tools = [create_customer_profile, get_customer_summary]