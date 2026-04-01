"""
Worker process management for Pandarallel
"""
import multiprocessing
from concurrent.futures import ProcessPoolExecutor
import signal
import traceback
from typing import Callable, List, Any, Tuple, Optional

from .utils import safe_apply, serialize, deserialize


class WorkerTask:
    """Represents a task to be executed by a worker."""
    def __init__(self, func: Callable, args: tuple = (), kwargs: dict = None):
        self.func = func
        self.args = args
        self.kwargs = kwargs or {}
        # Pre-serialize function to catch errors early and ensure proper serialization
        self._func_bytes = serialize(func) if func is not None else None

    def __getstate__(self):
        """Serialize the task for pickling."""
        # Return state with serialized function bytes
        state = {
            'args': self.args,
            'kwargs': self.kwargs,
            '_func_bytes': self._func_bytes,
            # Don't include func in state - it will be reconstructed from _func_bytes
        }
        return state

    def __setstate__(self, state):
        """Deserialize the task."""
        self.args = state['args']
        self.kwargs = state.get('kwargs', {})
        self._func_bytes = state['_func_bytes']
        # Reconstruct function from serialized bytes
        if self._func_bytes is not None:
            self.func = deserialize(self._func_bytes)
        else:
            self.func = None

    def execute(self) -> Tuple[bool, Any, Optional[str]]:
        """Execute the task and return result or error."""
        # Ensure function is available
        if self.func is None and self._func_bytes is not None:
            self.func = deserialize(self._func_bytes)
        return safe_apply(self.func, *self.args, **self.kwargs)


class WorkerPool:
    """
    Manages a pool of worker processes.

    Can use either multiprocessing.Pool or ProcessPoolExecutor as backend.
    """
    def __init__(self, n_workers: int, use_executor: bool = True):
        """
        Initialize worker pool.

        Args:
            n_workers: Number of worker processes
            use_executor: Whether to use ProcessPoolExecutor (True) or multiprocessing.Pool (False)
        """
        self.n_workers = n_workers
        self.use_executor = use_executor
        self.pool = None
        self.executor = None
        self._initialized = False

    def initialize(self):
        """Initialize the worker pool."""
        if self._initialized:
            return

        # Ignore SIGINT in worker processes to allow graceful shutdown
        original_sigint = signal.signal(signal.SIGINT, signal.SIG_IGN)

        try:
            if self.use_executor:
                self.executor = ProcessPoolExecutor(max_workers=self.n_workers)
            else:
                self.pool = multiprocessing.Pool(processes=self.n_workers)
        finally:
            # Restore original signal handler
            signal.signal(signal.SIGINT, original_sigint)

        self._initialized = True

    def submit(self, func: Callable, *args, **kwargs) -> Any:
        """
        Submit a task to the worker pool.

        Args:
            func: Function to execute
            *args: Positional arguments
            **kwargs: Keyword arguments

        Returns:
            Any: Future or AsyncResult depending on backend
        """
        if not self._initialized:
            self.initialize()

        if self.use_executor:
            return self.executor.submit(func, *args, **kwargs)
        else:
            return self.pool.apply_async(func, args, kwargs)

    def map(self, func: Callable, iterable, chunksize: int = 1) -> List:
        """
        Map a function over an iterable using worker pool.

        Args:
            func: Function to apply
            iterable: Iterable of arguments
            chunksize: Size of chunks for distribution

        Returns:
            List: Results
        """
        if not self._initialized:
            self.initialize()

        if self.use_executor:
            # ProcessPoolExecutor.map doesn't support chunksize directly
            # We'll use submit for each item
            futures = [self.submit(func, item) for item in iterable]
            return [f.result() for f in futures]
        else:
            return self.pool.map(func, iterable, chunksize=chunksize)

    def starmap(self, func: Callable, iterable, chunksize: int = 1) -> List:
        """
        Like map but unpacks arguments from tuples.

        Args:
            func: Function to apply
            iterable: Iterable of argument tuples
            chunksize: Size of chunks for distribution

        Returns:
            List: Results
        """
        if not self._initialized:
            self.initialize()

        if self.use_executor:
            futures = [self.submit(func, *args) for args in iterable]
            return [f.result() for f in futures]
        else:
            return self.pool.starmap(func, iterable, chunksize=chunksize)

    def shutdown(self, wait: bool = True):
        """Shutdown the worker pool."""
        if self.executor is not None:
            self.executor.shutdown(wait=wait)
            self.executor = None

        if self.pool is not None:
            self.pool.close()
            if wait:
                self.pool.join()
            self.pool = None

        self._initialized = False

    def __enter__(self):
        """Context manager entry."""
        self.initialize()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.shutdown(wait=True)


class WorkerProcess(multiprocessing.Process):
    """
    Custom worker process that can handle tasks from a queue.
    """
    def __init__(self, task_queue: multiprocessing.Queue, result_queue: multiprocessing.Queue,
                 worker_id: int, progress_queue: Optional[multiprocessing.Queue] = None):
        """
        Initialize worker process.

        Args:
            task_queue: Queue to receive tasks from
            result_queue: Queue to send results to
            worker_id: Unique ID for this worker
            progress_queue: Optional queue for progress updates
        """
        super().__init__()
        self.task_queue = task_queue
        self.result_queue = result_queue
        self.worker_id = worker_id
        self.progress_queue = progress_queue
        self.daemon = True

    def run(self):
        """Main worker loop."""
        # Ignore SIGINT in worker processes
        signal.signal(signal.SIGINT, signal.SIG_IGN)

        while True:
            try:
                # Get task from queue
                task = self.task_queue.get()

                # Check for termination signal
                if task is None:
                    self.result_queue.put((self.worker_id, None, None))
                    break

                # Execute task
                success, result, error = task.execute()

                # Send result
                self.result_queue.put((self.worker_id, success, result, error))

                # Send progress update if progress queue exists
                if self.progress_queue is not None:
                    self.progress_queue.put(self.worker_id)

            except Exception:
                # Send error result
                error_msg = f"Worker {self.worker_id} failed: {traceback.format_exc()}"
                self.result_queue.put((self.worker_id, False, None, error_msg))
                break


def create_worker_pool(n_workers: int) -> WorkerPool:
    """
    Create a worker pool.

    Args:
        n_workers: Number of worker processes

    Returns:
        WorkerPool: Worker pool instance
    """
    return WorkerPool(n_workers, use_executor=True)


def execute_tasks_parallel(tasks: List[WorkerTask], n_workers: int) -> List[Tuple[bool, Any, Optional[str]]]:
    """
    Execute tasks in parallel using worker pool.

    Args:
        tasks: List of tasks to execute
        n_workers: Number of worker processes

    Returns:
        List[Tuple[bool, Any, Optional[str]]]: List of (success, result, error) tuples
    """
    with WorkerPool(n_workers) as pool:
        # Submit all tasks
        futures = []
        for task in tasks:
            future = pool.submit(task.execute)
            futures.append(future)

        # Collect results
        results = []
        for future in futures:
            try:
                result = future.result()
                results.append(result)
            except Exception as e:
                results.append((False, None, str(e)))

        return results