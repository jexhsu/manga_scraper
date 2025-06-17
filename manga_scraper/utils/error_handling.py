# manga_scraper/utils/error_handling.py
import asyncio
import logging
from functools import wraps
from scrapy.exceptions import IgnoreRequest
from playwright.async_api import Error as PlaywrightError

logger = logging.getLogger(__name__)

class RetryableError(Exception):
    """Base class for retryable errors"""
    pass

class NonRetryableError(Exception):
    """Errors that shouldn't be retried"""
    pass

def classify_error(error):
    """Classify errors into retryable/non-retryable categories"""
    error_str = str(error).lower()
    
    # Connection-related errors (retryable)
    connection_errors = [
        'err_connection_closed',
        'err_connection_reset',
        'err_connection_refused',
        'err_timed_out',
        'timeout',
        'gateway timeout'
    ]
    
    if any(err in error_str for err in connection_errors):
        return RetryableError(f"Connection error: {error}")
    
    # Non-retryable errors
    non_retryable = [
        '404 not found',
        '403 forbidden',
        '401 unauthorized'
    ]
    if any(err in error_str for err in non_retryable):
        return NonRetryableError(f"Non-retryable error: {error}")
    
    return RetryableError(f"Unknown error (default retry): {error}")

def retry_on_failure(max_retries=3, delay=1):
    """Decorator for retry logic"""
    def decorator(func):
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            retry_count = kwargs.pop('retry_count', 0)
            try:
                return await func(*args, **kwargs)
            except Exception as e:
                classified = classify_error(e)
                if isinstance(classified, NonRetryableError) or retry_count >= max_retries:
                    logger.error(f"Max retries reached or non-retryable error: {e}")
                    raise IgnoreRequest from e
                
                logger.warning(f"Retry {retry_count + 1}/{max_retries} for error: {e}")
                kwargs['retry_count'] = retry_count + 1
                return await async_wrapper(*args, **kwargs)
        
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            retry_count = kwargs.pop('retry_count', 0)
            try:
                return func(*args, **kwargs)
            except Exception as e:
                classified = classify_error(e)
                if isinstance(classified, NonRetryableError) or retry_count >= max_retries:
                    logger.error(f"Max retries reached or non-retryable error: {e}")
                    raise IgnoreRequest from e
                
                logger.warning(f"Retry {retry_count + 1}/{max_retries} for error: {e}")
                kwargs['retry_count'] = retry_count + 1
                return sync_wrapper(*args, **kwargs)
        
        return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper
    return decorator