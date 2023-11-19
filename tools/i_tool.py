from abc import ABC, abstractmethod
from typing import Dict


class ITool(ABC):
    @abstractmethod
    def execute(args: str | Dict):
        ...
