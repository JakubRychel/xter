class UserBusy(Exception):
    """Exception raised when user is being processed by another worker."""

class EmbeddingBusy(Exception):
    """Exception raised when posts are being currently embedded."""

class NoJobsToProcess(Exception):
    """Exception raised when the redis job queue is empty."""