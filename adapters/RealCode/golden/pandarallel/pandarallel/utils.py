"""
Utility functions for Pandarallel
"""
import traceback
import pickle
import functools
from typing import Any, Callable, List, Tuple, Optional
import warnings

try:
    import pandas as pd
    PANDAS_AVAILABLE = True
except ImportError:
    PANDAS_AVAILABLE = False
    pd = None

try:
    import dill
    DILL_AVAILABLE = True
except ImportError:
    DILL_AVAILABLE = False
    dill = None
    warnings.warn(
        "dill is not installed. Some functions may not serialize properly. "
        "Install with: pip install dill",
        ImportWarning
    )


def serialize(obj: Any) -> bytes:
    """
    Serialize an object using dill if available, otherwise pickle.

    Args:
        obj: Object to serialize

    Returns:
        bytes: Serialized object

    Raises:
        pickle.PicklingError: If object cannot be serialized
    """
    try:
        if DILL_AVAILABLE:
            return dill.dumps(obj, protocol=pickle.HIGHEST_PROTOCOL)
        else:
            return pickle.dumps(obj, protocol=pickle.HIGHEST_PROTOCOL)
    except Exception as e:
        raise pickle.PicklingError(f"Failed to serialize object: {e}")


def deserialize(data: bytes) -> Any:
    """
    Deserialize an object using dill if available, otherwise pickle.

    Args:
        data: Serialized data

    Returns:
        Any: Deserialized object

    Raises:
        pickle.UnpicklingError: If data cannot be deserialized
    """
    try:
        if DILL_AVAILABLE:
            return dill.loads(data)
        else:
            return pickle.loads(data)
    except Exception as e:
        raise pickle.UnpicklingError(f"Failed to deserialize object: {e}")


def chunk_data(data, n_chunks: int) -> List:
    """
    Split data into roughly equal chunks.

    Args:
        data: List, Series, or DataFrame to split
        n_chunks: Number of chunks to create

    Returns:
        List: List of chunks
    """
    if hasattr(data, '__len__'):
        length = len(data)
        chunk_size = max(1, length // n_chunks)
        chunks = []
        for i in range(n_chunks):
            start = i * chunk_size
            if i == n_chunks - 1:
                end = length  # Last chunk gets remainder
            else:
                end = start + chunk_size
            chunks.append(data[start:end])
        return chunks
    else:
        # For non-indexable data, just wrap in list
        return [data] * n_chunks


def safe_apply(func: Callable, *args, **kwargs) -> Tuple[bool, Any, Optional[str]]:
    """
    Safely apply a function and capture any exceptions.

    Args:
        func: Function to apply
        *args: Positional arguments
        **kwargs: Keyword arguments

    Returns:
        Tuple[bool, Any, Optional[str]]:
            success flag, result or None, error message or None
    """
    try:
        result = func(*args, **kwargs)
        return True, result, None
    except Exception as e:
        error_msg = f"{type(e).__name__}: {str(e)}\n{traceback.format_exc()}"
        return False, None, error_msg


def format_exception(e: Exception) -> str:
    """
    Format an exception for display.

    Args:
        e: Exception to format

    Returns:
        str: Formatted exception string
    """
    return f"{type(e).__name__}: {str(e)}"


def is_notebook() -> bool:
    """
    Check if running in a Jupyter notebook.

    Returns:
        bool: True if running in a notebook
    """
    try:
        from IPython import get_ipython
        ip = get_ipython()
        if ip is None:
            return False
        return 'IPKernelApp' in ip.config
    except ImportError:
        return False


def get_memory_usage() -> float:
    """
    Get current process memory usage in MB.

    Returns:
        float: Memory usage in MB, or 0.0 if psutil not available
    """
    try:
        import psutil
        process = psutil.Process()
        return process.memory_info().rss / 1024 / 1024
    except ImportError:
        return 0.0


def deprecation_warning(message: str):
    """
    Issue a deprecation warning.

    Args:
        message: Warning message
    """
    warnings.warn(message, DeprecationWarning, stacklevel=3)


def timeit(func: Callable) -> Callable:
    """
    Decorator to time function execution.

    Args:
        func: Function to time

    Returns:
        Callable: Wrapped function
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        import time
        start = time.time()
        result = func(*args, **kwargs)
        end = time.time()
        print(f"{func.__name__} took {end - start:.2f} seconds")
        return result
    return wrapper


def get_dataframe_applymap_name() -> str:
    """
    Get the name of the DataFrame element-wise apply method.

    Returns:
        str: 'applymap' for pandas < 2.0, 'map' for pandas >= 2.0
    """
    if not PANDAS_AVAILABLE:
        return 'applymap'  # Default

    import pandas as pd
    # Use version heuristic first (pandas >= 2.0 uses map)
    if hasattr(pd, '__version__'):
        try:
            major_version = int(pd.__version__.split('.')[0])
            if major_version >= 2:
                return 'map'
        except:
            pass

    # Fallback to attribute detection
    test_df = pd.DataFrame({'A': [1, 2]})
    if hasattr(test_df, 'applymap') and callable(getattr(test_df, 'applymap')):
        return 'applymap'
    elif hasattr(test_df, 'map') and callable(getattr(test_df, 'map')):
        return 'map'

    return 'applymap'  # Default


def dataframe_applymap(df, func, *args, **kwargs):
    """
    Apply function element-wise to DataFrame, handling pandas version differences.

    Args:
        df: DataFrame
        func: Function to apply element-wise
        *args: Additional arguments
        **kwargs: Additional keyword arguments

    Returns:
        Result of applying func element-wise
    """
    method_name = get_dataframe_applymap_name()
    try:
        method = getattr(df, method_name)
        return method(func, *args, **kwargs)
    except AttributeError:
        # Fallback to the other method name
        alt_name = 'map' if method_name == 'applymap' else 'applymap'
        if hasattr(df, alt_name) and callable(getattr(df, alt_name)):
            method = getattr(df, alt_name)
            return method(func, *args, **kwargs)
        else:
            raise AttributeError("DataFrame has neither 'applymap' nor 'map' method")