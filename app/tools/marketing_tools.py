from typing import Any
from app.tools.base_tool import BaseTool


class GetCampaignIdeasTool(BaseTool):
    name = "get_campaign_ideas"
    description = "Generates marketing campaign ideas"

    async def run(self, **kwargs) -> Any:
        product = kwargs.get("product", "")
        audience = kwargs.get("audience", "")

        return {
            "ideas": [
                f"Facebook Ads campaign for {product}",
                f"Email campaign targeting {audience}",
                f"Content marketing about {product}"
            ]
        }


class CreateMarketingMessageTool(BaseTool):
    name = "create_marketing_message"
    description = "Creates a marketing message"

    async def run(self, **kwargs) -> Any:
        product = kwargs.get("product", "")
        tone = kwargs.get("tone", "professional")

        return {
            "message": f"A {tone} marketing message about {product} has been created."
        }


MARKETING_TOOLS = [
    GetCampaignIdeasTool(),
    CreateMarketingMessageTool(),
]