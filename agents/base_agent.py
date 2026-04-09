from abc import ABC, abstractmethod

class BaseAgent(ABC):
    def __init__(self, name):
        self.name = name

    @abstractmethod
    def execute(self, data):
        pass

    def log(self, message):
        print(f"[{self.name}] {message}")