"""
Inter-process communication for Pandarallel
"""
import os
import sys
import tempfile
import mmap
import multiprocessing
from typing import Any, Optional
import warnings

from .utils import serialize, deserialize


class IPCBase:
    """Base class for IPC mechanisms."""
    def send(self, data: Any, destination: Optional[int] = None):
        """Send data to destination (or broadcast if None)."""
        raise NotImplementedError

    def receive(self, source: Optional[int] = None) -> Any:
        """Receive data from source (or any source if None)."""
        raise NotImplementedError

    def close(self):
        """Clean up resources."""
        pass


class PipeIPC(IPCBase):
    """
    IPC using multiprocessing pipes.

    Simple but may be slower for large data due to pickling overhead.
    """
    def __init__(self, num_workers: int):
        """
        Initialize pipe IPC.

        Args:
            num_workers: Number of worker processes
        """
        self.num_workers = num_workers
        self.pipes = []

        # Create pipes: main process gets all worker connections
        for _ in range(num_workers):
            parent_conn, child_conn = multiprocessing.Pipe()
            self.pipes.append(parent_conn)

        self.worker_connections = [child_conn for _, child_conn in self.pipes]

    def get_worker_conn(self, worker_id: int):
        """Get connection for a specific worker."""
        if worker_id < 0 or worker_id >= self.num_workers:
            raise ValueError(f"Invalid worker_id: {worker_id}")
        return self.worker_connections[worker_id]

    def send(self, data: Any, destination: Optional[int] = None):
        """Send data to destination worker."""
        if destination is None:
            # Broadcast to all workers
            for conn in self.pipes:
                conn.send(data)
        else:
            self.pipes[destination].send(data)

    def receive(self, source: Optional[int] = None) -> Any:
        """Receive data from source worker."""
        if source is None:
            # Receive from any worker (non-blocking poll all)
            for conn in self.pipes:
                if conn.poll():
                    return conn.recv()
            # If none ready, block on first
            return self.pipes[0].recv()
        else:
            return self.pipes[source].recv()

    def close(self):
        """Close all pipes."""
        for conn in self.pipes:
            conn.close()
        self.pipes.clear()
        self.worker_connections.clear()


class SharedMemoryIPC(IPCBase):
    """
    IPC using shared memory (/dev/shm memory-mapped files).

    Faster for large data, but only available on Linux/Unix systems.
    """
    def __init__(self, num_workers: int, shm_dir: Optional[str] = None):
        """
        Initialize shared memory IPC.

        Args:
            num_workers: Number of worker processes
            shm_dir: Shared memory directory (default: /dev/shm)
        """
        self.num_workers = num_workers
        self.shm_dir = shm_dir or "/dev/shm"
        self.temp_dir = None
        self.use_temp_dir = False

        # Check if shm_dir exists and is writable
        if not os.path.exists(self.shm_dir):
            warnings.warn(
                f"Shared memory directory {self.shm_dir} not found. "
                "Falling back to temporary directory.",
                UserWarning
            )
            self.use_temp_dir = True
            self.temp_dir = tempfile.mkdtemp(prefix="pandarallel_shm_")
            self.shm_dir = self.temp_dir

        self.shm_files = []
        self.shm_regions = []

        # Create shared memory regions for each worker
        for i in range(num_workers):
            shm_path = os.path.join(self.shm_dir, f"pandarallel_shm_{os.getpid()}_{i}")
            self.shm_files.append(shm_path)

            # Create initial file with some space (will be resized as needed)
            with open(shm_path, "wb") as f:
                f.write(b"\x00" * 1024)  # 1KB initial

    def _write_to_shm(self, shm_path: str, data: bytes):
        """Write data to shared memory file."""
        data_len = len(data)

        # Resize file if needed
        file_size = os.path.getsize(shm_path)
        if file_size < data_len:
            with open(shm_path, "r+b") as f:
                f.truncate(data_len)

        # Write data
        with open(shm_path, "r+b") as f:
            mm = mmap.mmap(f.fileno(), data_len)
            mm.write(data)
            mm.close()

    def _read_from_shm(self, shm_path: str) -> bytes:
        """Read data from shared memory file."""
        file_size = os.path.getsize(shm_path)
        with open(shm_path, "rb") as f:
            mm = mmap.mmap(f.fileno(), file_size, access=mmap.ACCESS_READ)
            data = mm.read()
            mm.close()
        return data

    def send(self, data: Any, destination: Optional[int] = None):
        """Send data to destination worker via shared memory."""
        serialized = serialize(data)

        if destination is None:
            # Broadcast to all workers
            for i in range(self.num_workers):
                self._write_to_shm(self.shm_files[i], serialized)
        else:
            self._write_to_shm(self.shm_files[destination], serialized)

    def receive(self, source: Optional[int] = None) -> Any:
        """Receive data from source worker via shared memory."""
        if source is None:
            # Try each worker in order
            for i in range(self.num_workers):
                try:
                    data = self._read_from_shm(self.shm_files[i])
                    if data and data != b"\x00" * len(data):
                        return deserialize(data)
                except Exception:
                    continue
            # If none have data, return None
            return None
        else:
            data = self._read_from_shm(self.shm_files[source])
            return deserialize(data)

    def close(self):
        """Clean up shared memory files."""
        for shm_file in self.shm_files:
            try:
                if os.path.exists(shm_file):
                    os.unlink(shm_file)
            except Exception:
                pass

        if self.temp_dir and os.path.exists(self.temp_dir):
            try:
                os.rmdir(self.temp_dir)
            except Exception:
                pass

        self.shm_files.clear()
        self.shm_regions.clear()


class QueueIPC(IPCBase):
    """
    IPC using multiprocessing queues.

    Good balance of simplicity and performance.
    """
    def __init__(self, num_workers: int):
        """
        Initialize queue IPC.

        Args:
            num_workers: Number of worker processes
        """
        self.num_workers = num_workers
        self.queues = []

        # Create queues for each worker
        for _ in range(num_workers):
            queue = multiprocessing.Queue()
            self.queues.append(queue)

    def send(self, data: Any, destination: Optional[int] = None):
        """Send data to destination worker queue."""
        if destination is None:
            # Broadcast to all workers
            for queue in self.queues:
                queue.put(data)
        else:
            self.queues[destination].put(data)

    def receive(self, source: Optional[int] = None) -> Any:
        """Receive data from source worker queue."""
        if source is None:
            # Receive from any worker (non-blocking poll all)
            for queue in self.queues:
                if not queue.empty():
                    return queue.get()
            # If none ready, block on first
            return self.queues[0].get()
        else:
            return self.queues[source].get()

    def close(self):
        """Close all queues."""
        for queue in self.queues:
            queue.close()
            queue.join_thread()
        self.queues.clear()


def create_ipc(num_workers: int, use_memory_fs: bool = False) -> IPCBase:
    """
    Create appropriate IPC mechanism based on platform and configuration.

    Args:
        num_workers: Number of worker processes
        use_memory_fs: Whether to use memory file system

    Returns:
        IPCBase: IPC instance
    """
    if use_memory_fs and sys.platform != "win32":
        try:
            return SharedMemoryIPC(num_workers)
        except Exception as e:
            warnings.warn(
                f"Failed to create shared memory IPC: {e}. "
                "Falling back to queue IPC.",
                UserWarning
            )
            return QueueIPC(num_workers)
    else:
        # Default to queue IPC for Windows or when memory FS is disabled
        return QueueIPC(num_workers)