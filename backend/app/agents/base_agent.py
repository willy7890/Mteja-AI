from typing import Any, List
from app.tools.base_tool import BaseTool


class BaseAgent:
    

    def __init__(self, name: str, tools: List[BaseTool]):
        self.name = name
        self.tools = {tool.name: tool for tool in tools}

    def get_available_tools(self) -> List[str]:
        """Return list of tool names this agent can use"""
        return list(self.tools.keys())

    async def call_tool(self, tool_name: str, **kwargs) -> Any:
        """
        Call a tool by name.
        Only tools that belong to this agent are allowed.
        """
        if tool_name not in self.tools:
            return {
                "error": f"Tool '{tool_name}' is not allowed for {self.name}"
            }

        tool = self.tools[tool_name]
        result = await tool.run(**kwargs)
        return result