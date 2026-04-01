"""
Configuration management for Pandarallel
"""
import os
import sys
import warnings
from typing import Optional
import multiprocessing

try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False
    psutil = None

# Import monkey_patch here to avoid circular imports
# We'll import it inside initialize function when needed


class PandarallelConfig:
    """
    Singleton configuration class for Pandarallel.

    Manages global settings: number of workers, progress bar display,
    memory file system usage, and verbosity.
    """
    _instance = None
    _initialized = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(PandarallelConfig, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if not self._initialized:
            self._nb_workers = None
            self._progress_bar = True
            self._verbose = 1
            self._use_memory_fs = None  # None means auto-detect
            self._is_initialized = False
            self._memory_fs_available = self._check_memory_fs()
            self._initialized = True

    def _check_memory_fs(self) -> bool:
        """
        Check if memory file system (/dev/shm) is available.

        Returns:
            bool: True if memory file system is available and writable
        """
        if sys.platform == "win32":
            return False

        shm_path = "/dev/shm"
        if not os.path.exists(shm_path):
            return False

        try:
            # Try to create a test file
            test_file = os.path.join(shm_path, f".pandarallel_test_{os.getpid()}")
            with open(test_file, "w") as f:
                f.write("test")
            os.unlink(test_file)
            return True
        except (OSError, IOError):
            return False

    def _get_default_workers(self) -> int:
        """
        Get default number of workers based on physical CPU cores.

        Returns:
            int: Number of physical CPU cores, falls back to logical cores
        """
        if PSUTIL_AVAILABLE:
            try:
                return psutil.cpu_count(logical=False) or psutil.cpu_count(logical=True) or 1
            except Exception:
                pass

        # Fallback to multiprocessing
        try:
            return multiprocessing.cpu_count()
        except Exception:
            return 1

    @property
    def nb_workers(self) -> int:
        """Get number of worker processes."""
        if self._nb_workers is None:
            return self._get_default_workers()
        return self._nb_workers

    @nb_workers.setter
    def nb_workers(self, value: Optional[int]):
        """Set number of worker processes."""
        if value is not None:
            if not isinstance(value, int):
                raise TypeError("nb_workers must be an integer")
            if value < 1:
                raise ValueError("nb_workers must be at least 1")
            max_workers = self._get_default_workers() * 2  # Reasonable upper bound
            if value > max_workers:
                warnings.warn(
                    f"nb_workers={value} exceeds recommended maximum of {max_workers}. "
                    "This may degrade performance.",
                    UserWarning
                )
        self._nb_workers = value

    @property
    def progress_bar(self) -> bool:
        """Get progress bar setting."""
        return self._progress_bar

    @progress_bar.setter
    def progress_bar(self, value: bool):
        """Set progress bar setting."""
        if not isinstance(value, bool):
            raise TypeError("progress_bar must be a boolean")
        self._progress_bar = value

    @property
    def verbose(self) -> int:
        """Get verbosity level."""
        return self._verbose

    @verbose.setter
    def verbose(self, value: int):
        """Set verbosity level (0: silent, 1: info, 2: debug)."""
        if not isinstance(value, int):
            raise TypeError("verbose must be an integer")
        if value < 0 or value > 2:
            raise ValueError("verbose must be 0, 1, or 2")
        self._verbose = value

    @property
    def use_memory_fs(self) -> bool:
        """Get memory file system usage setting."""
        if self._use_memory_fs is None:
            return self._memory_fs_available
        return self._use_memory_fs

    @use_memory_fs.setter
    def use_memory_fs(self, value: Optional[bool]):
        """Set memory file system usage setting."""
        if value is not None and not isinstance(value, bool):
            raise TypeError("use_memory_fs must be a boolean or None")

        if value is True and not self._memory_fs_available:
            warnings.warn(
                "Memory file system (/dev/shm) is not available. "
                "Falling back to pipes.",
                UserWarning
            )
            value = False

        self._use_memory_fs = value

    @property
    def is_initialized(self) -> bool:
        """Check if pandarallel has been initialized."""
        return self._is_initialized

    @is_initialized.setter
    def is_initialized(self, value: bool):
        """Set initialization status."""
        self._is_initialized = value

    def get_info(self) -> dict:
        """
        Get current configuration as dictionary.

        Returns:
            dict: Configuration information
        """
        return {
            "nb_workers": self.nb_workers,
            "progress_bar": self.progress_bar,
            "verbose": self.verbose,
            "use_memory_fs": self.use_memory_fs,
            "memory_fs_available": self._memory_fs_available,
            "is_initialized": self.is_initialized,
        }

    def reset(self):
        """Reset configuration to default values."""
        self._nb_workers = None
        self._progress_bar = True
        self._verbose = 1
        self._use_memory_fs = None
        self._is_initialized = False


# Global configuration instance
_config = PandarallelConfig()


def initialize(
    nb_workers: Optional[int] = None,
    progress_bar: bool = True,
    verbose: int = 1,
    use_memory_fs: Optional[bool] = None,
):
    """
    Initialize Pandarallel with custom configuration.

    Args:
        nb_workers: Number of worker processes. If None, uses physical CPU cores.
        progress_bar: Whether to display progress bars.
        verbose: Verbosity level (0: silent, 1: info, 2: debug).
        use_memory_fs: Whether to use memory file system (/dev/shm) for IPC.
                       If None, auto-detects based on availability.

    Returns:
        PandarallelConfig: The configuration instance
    """
    config = _config

    # Set multiprocessing start method for compatibility
    # On macOS and Windows, spawn is default, but fork is more compatible with Python modules
    # We'll try to use fork if available, otherwise use spawn
    try:
        multiprocessing.set_start_method('fork', force=True)
        if verbose >= 2:
            print("Set multiprocessing start method to 'fork'")
    except ValueError:
        # fork method not available (e.g., on Windows)
        if verbose >= 2:
            print("Using default multiprocessing start method")

    # Apply settings
    config.nb_workers = nb_workers
    config.progress_bar = progress_bar
    config.verbose = verbose
    config.use_memory_fs = use_memory_fs
    config.is_initialized = True

    # Apply monkey patches
    from .monkey_patch import patch_all
    patch_all()

    if verbose >= 1:
        info = config.get_info()
        print(f"Pandarallel initialized with {info['nb_workers']} workers")
        if info['use_memory_fs']:
            print("Using memory file system (/dev/shm) for IPC")
        else:
            print("Using pipes for IPC")

    return config