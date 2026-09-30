from app.agents.supervisor import Supervisor
from app.services.telegram_service import format_telegram_reply


def test_supervisor_routes_support_messages():
    supervisor = Supervisor()

    assert supervisor.route("I have a problem with my order") == "support_agent"


def test_format_telegram_reply_uses_human_readable_tool_result():
    result = {
        "agent": "sales_agent",
        "action": "get_product_price",
        "result": {
            "product": "product",
            "price": "Contact us for current pricing",
        },
    }

    assert format_telegram_reply(result) == (
        "Price for product: Contact us for current pricing"
    )