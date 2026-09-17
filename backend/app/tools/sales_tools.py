from typing import Any
from app.tools.base_tool import BaseTool


class GetProductPriceTool(BaseTool):
    name = "get_product_price"
    description = "Returns the price of a product"

    async def run(self, **kwargs) -> Any:
        product = kwargs.get("product", "")

        return {
            "product": product,
            "price": "Contact us for current pricing",  # dummy for now
        }


class CreateOrderTool(BaseTool):
    name = "create_order"
    description = "Creates a new sales order for a customer"

    async def run(self, **kwargs) -> Any:
        customer_name = kwargs.get("customer_name", "")
        product = kwargs.get("product", "")

        return {
            "status": "order_created",
            "message": f"Order for {product} has been created for {customer_name}",
        }



SALES_TOOLS = [
    GetProductPriceTool(),
    CreateOrderTool(),
]