from abc import ABC, abstractmethod

class SyncOperation(ABC):
    """
    """
    
    def __init__(self):
        pass

    @abstractmethod
    def execute(self, triple_store):
        pass
