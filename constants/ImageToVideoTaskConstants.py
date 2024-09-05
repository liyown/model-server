from enum import Enum


class TaskStatus(Enum):
    PENDING = 0
    PROCESSING = 1
    COMPLETED = 2
    FAILED = 3