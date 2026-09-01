# product_tools for MTEJA AI agents
# Controlled, audited tools that agents may call (no direct DB access)
from langchain_core.tools import tool
from app.services.knowledge_service import kb_service


@tool
def check_product_stock(product_name: str) -> str:
  """Check current stock availability and pricing for a product from the knowledge base.

  Args:
      product_name: Name of the product or item to search for.
  """
  # Search vector knowledge base for product details and inventory info
  results = kb_service.search(product_name, k=2)
  if not results:
    return f"Sorry, no stock information found for '{product_name}'."
  return f"Stock and product info for '{product_name}':\n{results}"


@tool
def search_product_catalog(query: str) -> str:
  """Search the product or service catalog using semantic search.

  Args:
      query: Search term describing the item or service.
  """
  results = kb_service.search(query, k=3)
  if not results:
    return "No matching catalog items found."
  return f"Catalog search results:\n{results}"


# Export product tools for agent binding
product_tools = [check_product_stock, search_product_catalog]