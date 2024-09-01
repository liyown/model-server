"""
:keyword
    - Interface
    - Abstract Class
    - Abstract Method

:summary
    - Provide a common interface for a Model inference to be used in the EndPoint
    - This is an abstract class that will be inherited by the Model class
"""


from abc import ABC, abstractmethod
from typing import List, Dict


class BaseHandle(ABC):
    """
    Abstract class for the Model interface
    """

    @abstractmethod
    def initialize(self, **kwargs):
        """
        Initialize the model
        """
        pass

    @abstractmethod
    def preprocess(self, ctx: Dict):
        """
        Preprocess the input data
        """
        pass

    @abstractmethod
    def inference(self, ctx: Dict):
        """
        Perform inference on the data
        """
        pass

    @abstractmethod
    def postprocess(self, ctx: Dict):
        """
        Postprocess the output data
        """
        pass

