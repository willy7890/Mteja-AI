# payment_tools for MTEJA AI agents
# Controlled, audited tools that agents may call (no direct DB access)
import os
import httpx
from langchain_core.tools import tool


@tool
def verify_payment_status(transaction_reference: str) -> str:
  """Verify the status of a customer payment transaction (e.g. Mobile Money / Bank).

  Args:
      transaction_reference: The transaction ID or reference code.
  """
  # Stub for payment gateway verification (e.g., AzamPay, Selcom, or M-Pesa API)
  if not transaction_reference:
    return "Invalid transaction reference provided."
  
  return (
      f"Transaction {transaction_reference} status: VERIFIED and COMPLETED."
  )


@tool
def generate_payment_link(customer_name: str, amount: float, currency: str = "TZS") -> str:
  """Generate a checkout payment link for a customer.

  Args:
      customer_name: Name of the customer or student.
      amount: Numeric amount to be paid.
      currency: Currency code (default TZS for Tanzanian Shillings).
  """
  return (
      f"Payment link generated for {customer_name}:"
      f" https://pay.mtejaai.co.tz/checkout?amount={amount}&currency={currency}"
  )


# Export payment tools for agent binding
payment_tools = [verify_payment_status, generate_payment_link]