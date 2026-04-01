"""
Progress bar management for Pandarallel
"""
import sys
import threading
import time

from .utils import is_notebook


class ProgressBarManager:
    """
    Manages progress bar display for parallel operations.

    Supports both terminal and Jupyter notebook environments.
    """
    def __init__(self, total: int, desc: str = "Processing", disable: bool = False):
        """
        Initialize progress bar manager.

        Args:
            total: Total number of tasks
            desc: Description to display
            disable: Whether to disable progress bar
        """
        self.total = total
        self.desc = desc
        self.disable = disable
        self.current = 0
        self.lock = threading.Lock()
        self.start_time = None
        self.bar = None

        if not self.disable:
            self._init_progress_bar()

    def _init_progress_bar(self):
        """Initialize the appropriate progress bar based on environment."""
        if is_notebook():
            self._init_notebook_bar()
        else:
            self._init_terminal_bar()

    def _init_notebook_bar(self):
        """Initialize Jupyter notebook progress bar."""
        try:
            from tqdm.notebook import tqdm
            self.bar = tqdm(total=self.total, desc=self.desc, leave=False)
        except ImportError:
            # Fall back to terminal tqdm
            self._init_terminal_bar()

    def _init_terminal_bar(self):
        """Initialize terminal progress bar."""
        try:
            from tqdm import tqdm
            self.bar = tqdm(total=self.total, desc=self.desc, leave=False,
                           file=sys.stdout, bar_format="{desc}: {percentage:3.0f}%|{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}]")
        except ImportError:
            # tqdm not available, use simple text updates
            self.bar = None
            print(f"{self.desc}: 0/{self.total}")

    def update(self, n: int = 1):
        """
        Update progress by n tasks.

        Args:
            n: Number of tasks completed
        """
        if self.disable:
            return

        with self.lock:
            self.current += n
            if self.bar is not None:
                self.bar.update(n)
            elif self.current % max(1, self.total // 10) == 0 or self.current == self.total:
                # Simple text update for every ~10% progress
                print(f"{self.desc}: {self.current}/{self.total}")

    def close(self):
        """Close the progress bar."""
        if self.bar is not None:
            self.bar.close()
            self.bar = None
        elif not self.disable and self.current == self.total:
            print(f"{self.desc}: Completed {self.total}/{self.total}")

    def __enter__(self):
        """Context manager entry."""
        self.start_time = time.time()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()
        if not self.disable and self.start_time is not None:
            elapsed = time.time() - self.start_time
            if exc_type is None:
                print(f"Completed in {elapsed:.2f}s")

    def get_progress(self) -> float:
        """
        Get current progress as fraction.

        Returns:
            float: Progress from 0.0 to 1.0
        """
        return self.current / self.total if self.total > 0 else 0.0


class ProgressAggregator:
    """
    Aggregates progress from multiple workers.
    """
    def __init__(self, total_workers: int, total_tasks: int, desc: str = "Processing", disable: bool = False):
        """
        Initialize progress aggregator.

        Args:
            total_workers: Number of workers
            total_tasks: Total number of tasks
            desc: Description to display
            disable: Whether to disable progress bar
        """
        self.total_workers = total_workers
        self.total_tasks = total_tasks
        self.desc = desc
        self.disable = disable

        self.worker_progress = [0] * total_workers
        self.lock = threading.Lock()
        self.bar = None

        if not self.disable:
            self._init_progress_bar()

    def _init_progress_bar(self):
        """Initialize progress bar."""
        try:
            from tqdm import tqdm
            self.bar = tqdm(total=self.total_tasks, desc=self.desc, leave=False)
        except ImportError:
            self.bar = None

    def update_worker(self, worker_id: int, completed: int):
        """
        Update progress for a specific worker.

        Args:
            worker_id: Worker ID (0-indexed)
            completed: Number of tasks completed by this worker
        """
        if self.disable:
            return

        with self.lock:
            if worker_id < 0 or worker_id >= self.total_workers:
                return

            delta = completed - self.worker_progress[worker_id]
            self.worker_progress[worker_id] = completed

            if self.bar is not None and delta > 0:
                self.bar.update(delta)

    def get_total_progress(self) -> int:
        """
        Get total number of completed tasks.

        Returns:
            int: Total completed tasks
        """
        with self.lock:
            return sum(self.worker_progress)

    def close(self):
        """Close the progress bar."""
        if self.bar is not None:
            self.bar.close()
            self.bar = None

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()


def create_progress_bar(total: int, desc: str = "Processing", disable: bool = False) -> ProgressBarManager:
    """
    Create a progress bar manager.

    Args:
        total: Total number of tasks
        desc: Description to display
        disable: Whether to disable progress bar

    Returns:
        ProgressBarManager: Progress bar instance
    """
    return ProgressBarManager(total, desc, disable)