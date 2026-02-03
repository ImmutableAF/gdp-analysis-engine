from abc import ABC, abstractmethod
class statistics_calculator(ABC):
    @abstractmethod
    def calculate(self, data):
        pass