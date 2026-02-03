from abc import ABC, abstractmethod

class data_loader(ABC):
    @abstractmethod
    def load_file(self, filepath):
        pass
    @abstractmethod
    def validate_file(self, filepath):
        pass