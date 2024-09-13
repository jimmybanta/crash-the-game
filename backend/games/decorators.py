''' Decorators for the games app. '''

from functools import wraps
import logging
import time


logger = logging.getLogger(__name__)


# decorator to catch exceptions and log them
def catch_and_log(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception:
            logger.exception(f'Error in {func.__name__}')
            raise
    return wrapper

# decorator to retry a function on exception
## used for functions that call the LLM - in case it has overload problems, etc.
def retry_on_exception(max_retries=3, delay=3):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):

            for i in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except Exception:
                    logger.exception(f'Error in {func.__name__}')
                    time.sleep(delay)
            
            logger.exception(f'Max retries reached for function {func.__name__}.')
            raise Exception(f'Max retries reached for function {func.__name__}.')
        
        return wrapper
    return decorator