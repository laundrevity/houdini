from abc import ABC, abstractmethod


class ITool(ABC):
    @abstractmethod
    def execute():
        ...
