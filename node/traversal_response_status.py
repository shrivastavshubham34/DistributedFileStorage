from enum import Enum


class TraversalResponseStatus(Enum):
    """
    Enum for traversal response status
    """
    FOUND = 0
    FORWARDED = 1
    NOT_FOUND = 2
