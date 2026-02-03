from abc import ABC, abstractmethod
class visualizer(ABC):
    @abstractmethod
    def draw_chart(self, data, chart_type, title):
        pass
    @abstractmethod
    def save_chart(self, filepath):
        pass