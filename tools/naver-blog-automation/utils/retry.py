import time
import functools
import logging

from config.settings import MAX_RETRIES, RETRY_BACKOFF_BASE

logger = logging.getLogger(__name__)


def retry(max_attempts=MAX_RETRIES, backoff_base=RETRY_BACKOFF_BASE, exceptions=(Exception,)):
    """Exponential backoff retry decorator."""
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            for attempt in range(1, max_attempts + 1):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    if attempt < max_attempts:
                        delay = backoff_base ** attempt
                        logger.warning(
                            f"[Retry {attempt}/{max_attempts}] {func.__name__} "
                            f"failed: {e}. Retrying in {delay}s..."
                        )
                        time.sleep(delay)
                    else:
                        logger.error(
                            f"[Retry {attempt}/{max_attempts}] {func.__name__} "
                            f"failed permanently: {e}"
                        )
            raise last_exception
        return wrapper
    return decorator
