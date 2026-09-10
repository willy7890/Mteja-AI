from abc import ABC, abstractmethod
from typing import Any


class BaseTool(ABC):

    name: str
    description: str

    @abstractmethod
    async def run(self, **kwargs) -> Any:
        
        pass