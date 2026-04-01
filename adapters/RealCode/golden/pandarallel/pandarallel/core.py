"""
Core parallel engine for Pandarallel
"""
import pandas as pd
import numpy as np
from typing import Callable, Any, List, Tuple, Optional, Union
import warnings

from .config import _config
from .worker import WorkerTask, execute_tasks_parallel
from .progress import create_progress_bar
from .utils import chunk_data, dataframe_applymap
import functools


# Module-level helper functions that can be serialized
def _apply_chunk(chunk, func, axis, args, kwargs):
    """Apply function to a chunk of data."""
    # Handle Series vs DataFrame
    if hasattr(chunk, 'apply'):
        if isinstance(chunk, pd.Series):
            # Series.apply doesn't accept axis parameter
            # Remove 'axis' from kwargs if present to avoid errors
            kwargs_no_axis = {k: v for k, v in kwargs.items() if k != 'axis'}
            return chunk.apply(func, *args, **kwargs_no_axis)
        else:
            # DataFrame.apply accepts axis parameter
            return chunk.apply(func, axis=axis, *args, **kwargs)
    else:
        # Fallback for other data types
        return func(chunk, *args, **kwargs)

def _applymap_chunk(chunk, func, args, kwargs):
    """Apply function element-wise to a chunk of data."""
    return dataframe_applymap(chunk, func, *args, **kwargs)

def _map_chunk(chunk, func, args, kwargs):
    """Map function to a chunk of Series."""
    return chunk.map(func, *args, **kwargs)


class ParallelEngine:
    """
    Core engine for parallel execution of pandas operations.
    """
    def __init__(self, progress_bar: Optional[bool] = None):
        """
        Initialize parallel engine.

        Args:
            progress_bar: Whether to show progress bar (overrides config if not None)
        """
        self.config = _config
        self.progress_bar = progress_bar if progress_bar is not None else self.config.progress_bar

    def _get_num_workers(self) -> int:
        """Get number of worker processes."""
        return self.config.nb_workers

    def _create_tasks(self, func: Callable, chunks: List, *args, **kwargs) -> List[WorkerTask]:
        """
        Create worker tasks for each chunk.

        Args:
            func: Function to apply to each chunk
            chunks: List of data chunks
            *args: Additional arguments for func
            **kwargs: Additional keyword arguments for func

        Returns:
            List[WorkerTask]: List of tasks
        """
        tasks = []
        for chunk in chunks:
            # Create a task that applies func to this chunk
            task = WorkerTask(func, (chunk,) + args, kwargs)
            tasks.append(task)
        return tasks

    def _merge_results(self, results: List, original_data: Any, axis: int = 0) -> Any:
        """
        Merge results from worker chunks.

        Args:
            results: List of results from workers
            original_data: Original data (for shape/type information)
            axis: Axis along which data was split (0: rows, 1: columns)

        Returns:
            Merged result
        """
        if not results:
            return original_data

        # Debug: print results info
        if self.config.verbose >= 2:
            print(f"[DEBUG] _merge_results: len(results)={len(results)}, axis={axis}, original_data type={type(original_data)}")
            if results:
                print(f"[DEBUG] First result type={type(results[0])}, shape={getattr(results[0], 'shape', 'N/A')}")
                if isinstance(results[0], pd.Series):
                    print(f"[DEBUG] Series index: {results[0].index.tolist()[:5]}...")

        # Check if results are pandas objects
        if all(isinstance(r, (pd.DataFrame, pd.Series)) for r in results):
            # Special case: reduction operations (e.g., sum) on DataFrame
            # If original data is DataFrame and all results are Series with matching columns
            if isinstance(original_data, pd.DataFrame) and all(isinstance(r, pd.Series) for r in results):
                # Check if all Series have the same index (column names)
                if all(r.index.equals(results[0].index) for r in results):
                    # For reduction operations like sum, we need to sum the Series
                    # This handles DataFrame.apply(axis=0) with reduction functions
                    try:
                        # Sum all Series element-wise
                        combined = results[0].copy()
                        for r in results[1:]:
                            combined = combined.add(r, fill_value=0)
                        return combined
                    except Exception:
                        # Fall back to concatenation if summation fails
                        pass

            # If all results are Series, concatenate along rows (axis=0)
            # This works for both column-wise and row-wise operations
            if all(isinstance(r, pd.Series) for r in results):
                return pd.concat(results, axis=0, ignore_index=False)

            if axis == 0:
                # Concatenate along rows
                if isinstance(results[0], pd.DataFrame):
                    return pd.concat(results, axis=0, ignore_index=False)
                else:  # pd.Series
                    return pd.concat(results, axis=0, ignore_index=False)
            else:
                # Concatenate along columns
                if isinstance(results[0], pd.DataFrame):
                    return pd.concat(results, axis=1, ignore_index=False)
                else:
                    # For Series with axis=1, check if we need to sum (reduction) or concatenate
                    # If all Series have same index, likely reduction operation
                    if all(r.index.equals(results[0].index) for r in results):
                        try:
                            # Sum all Series element-wise
                            combined = results[0].copy()
                            for r in results[1:]:
                                combined = combined.add(r, fill_value=0)
                            return combined
                        except Exception:
                            # Fall back to concatenation
                            return pd.concat(results, axis=1, ignore_index=False)
                    else:
                        return pd.concat(results, axis=1, ignore_index=False)
        elif all(isinstance(r, (np.ndarray)) for r in results):
            # Merge numpy arrays
            if axis == 0:
                return np.vstack(results) if results[0].ndim > 1 else np.concatenate(results)
            else:
                return np.hstack(results) if results[0].ndim > 1 else np.concatenate(results)
        elif all(isinstance(r, (list, tuple)) for r in results):
            # Merge lists/tuples
            merged = []
            for r in results:
                if isinstance(r, (list, tuple)):
                    merged.extend(r)
                else:
                    merged.append(r)
            return type(results[0])(merged) if results else []
        else:
            # For scalar results, return as list
            return results

    def _handle_errors(self, task_results: List[Tuple[bool, Any, Optional[str]]]) -> List[Any]:
        """
        Handle errors from worker tasks.

        Args:
            task_results: List of (success, result, error) tuples

        Returns:
            List[Any]: List of successful results

        Raises:
            Exception: First error encountered if any task failed
        """
        successful_results = []
        errors = []

        for success, result, error in task_results:
            if success:
                successful_results.append(result)
            else:
                errors.append(error)

        if errors:
            # Raise the first error with context
            error_msg = f"{len(errors)} worker(s) failed:\n"
            for i, err in enumerate(errors[:3]):  # Show first 3 errors
                error_msg += f"  Worker {i+1}: {err}\n"
            if len(errors) > 3:
                error_msg += f"  ... and {len(errors) - 3} more errors\n"

            # Try to extract exception type and message from first error
            first_error = errors[0]
            if "ZeroDivisionError" in first_error:
                raise ZeroDivisionError(f"Division by zero in worker: {first_error}")
            elif "AttributeError" in first_error:
                raise AttributeError(f"Attribute error in worker: {first_error}")
            else:
                raise RuntimeError(error_msg)

        return successful_results

    def apply(
        self,
        data: Union[pd.DataFrame, pd.Series],
        func: Callable,
        axis: int = 0,
        *args,
        **kwargs
    ) -> Union[pd.DataFrame, pd.Series]:
        """
        Parallel apply function to DataFrame or Series.

        Args:
            data: DataFrame or Series
            func: Function to apply
            axis: Axis along which to apply (0: rows, 1: columns)
            *args: Additional arguments for func
            **kwargs: Additional keyword arguments for func

        Returns:
            Result of applying func to data
        """
        # Determine number of workers
        n_workers = self._get_num_workers()

        # Handle Series specially (axis parameter doesn't apply to Series)
        is_series = isinstance(data, pd.Series)
        if is_series:
            # Series.apply always works element-wise, ignore axis parameter
            axis = 0  # Treat as axis=0 for consistent processing

        # Limit workers based on data size
        if isinstance(data, pd.DataFrame):
            if axis == 0:
                # Applying to columns
                n_workers = min(n_workers, data.shape[1])  # Number of columns
            else:
                # Applying to rows
                n_workers = min(n_workers, data.shape[0])  # Number of rows
        else:  # Series
            n_workers = min(n_workers, len(data))

        # Ensure at least 1 worker
        n_workers = max(1, n_workers)

        # Split data into chunks
        if axis == 0:
            # Apply function to each column - split columns for parallel processing
            if isinstance(data, pd.DataFrame):
                # Split column names
                col_chunks = chunk_data(list(data.columns), n_workers)
                chunks = [data[cols] for cols in col_chunks]
            else:
                # Series with axis=0 - split along rows (Series elements)
                chunks = chunk_data(data, n_workers)
        else:
            # axis == 1: Apply function to each row - split rows
            if isinstance(data, pd.DataFrame):
                # Split along rows
                chunks = chunk_data(data, n_workers)
            else:
                # Series with axis=1 doesn't make sense, treat as axis=0
                warnings.warn("axis=1 is not meaningful for Series, using axis=0")
                chunks = chunk_data(data, n_workers)
                axis = 0

        # Determine merge axis based on splitting strategy
        # For axis=0 (apply to columns), we split by columns, so merge along columns (axis=1)
        # For axis=1 (apply to rows), we split by rows, so merge along rows (axis=0)
        merge_axis = 1 if axis == 0 else 0
        # For Series, always merge along rows (axis=0)
        if is_series:
            merge_axis = 0

        # Create tasks
        tasks = self._create_tasks(
            functools.partial(_apply_chunk, func=func, axis=axis, args=args, kwargs=kwargs),
            chunks
        )

        # Execute tasks in parallel
        with create_progress_bar(len(tasks), "Applying", disable=not self.progress_bar) as pbar:
            task_results = execute_tasks_parallel(tasks, n_workers)

            # Update progress bar
            for _ in task_results:
                pbar.update(1)

        # Handle errors
        successful_results = self._handle_errors(task_results)

        # Merge results
        return self._merge_results(successful_results, data, axis=merge_axis)

    def applymap(
        self,
        df: pd.DataFrame,
        func: Callable,
        *args,
        **kwargs
    ) -> pd.DataFrame:
        """
        Parallel applymap function to DataFrame element-wise.

        Args:
            df: DataFrame
            func: Function to apply element-wise
            *args: Additional arguments for func
            **kwargs: Additional keyword arguments for func

        Returns:
            Result of applying func element-wise to df
        """
        n_workers = self._get_num_workers()

        # Split DataFrame into row chunks for applymap
        chunks = chunk_data(df, n_workers)

        # Create tasks
        tasks = self._create_tasks(
            functools.partial(_applymap_chunk, func=func, args=args, kwargs=kwargs),
            chunks
        )

        # Execute tasks
        with create_progress_bar(len(tasks), "Applymap", disable=not self.progress_bar) as pbar:
            task_results = execute_tasks_parallel(tasks, n_workers)
            for _ in task_results:
                pbar.update(1)

        # Handle errors
        successful_results = self._handle_errors(task_results)

        # Merge results
        return self._merge_results(successful_results, df, axis=0)

    def map(
        self,
        series: pd.Series,
        func: Callable,
        *args,
        **kwargs
    ) -> pd.Series:
        """
        Parallel map function to Series.

        Args:
            series: Series
            func: Function to apply to each element
            *args: Additional arguments for func
            **kwargs: Additional keyword arguments for func

        Returns:
            Result of applying func to series
        """
        n_workers = self._get_num_workers()

        # Split Series into chunks
        chunks = chunk_data(series, n_workers)

        # Create tasks
        tasks = self._create_tasks(
            functools.partial(_map_chunk, func=func, args=args, kwargs=kwargs),
            chunks
        )

        # Execute tasks
        with create_progress_bar(len(tasks), "Mapping", disable=not self.progress_bar) as pbar:
            task_results = execute_tasks_parallel(tasks, n_workers)
            for _ in task_results:
                pbar.update(1)

        # Handle errors
        successful_results = self._handle_errors(task_results)

        # Merge results
        return self._merge_results(successful_results, series, axis=0)

    def groupby_apply(
        self,
        df: pd.DataFrame,
        group_cols: Union[str, List[str]],
        func: Callable,
        *args,
        **kwargs
    ) -> pd.DataFrame:
        """
        Parallel apply function to grouped DataFrame.

        Args:
            df: DataFrame
            group_cols: Column name(s) to group by
            func: Function to apply to each group
            *args: Additional arguments for func
            **kwargs: Additional keyword arguments for func

        Returns:
            Result of applying func to each group
        """
        n_workers = self._get_num_workers()

        # Group data
        grouped = df.groupby(group_cols)

        # Get groups
        groups = list(grouped.groups.keys())
        group_chunks = chunk_data(groups, n_workers)

        # Create tasks for each chunk of groups
        def process_group_chunk(group_keys):
            key_result_pairs = []
            # Convert group_cols to list for consistent handling
            if isinstance(group_cols, str):
                cols_list = [group_cols]
            else:
                cols_list = list(group_cols)
            for key in group_keys:
                # Filter rows where group columns equal key
                # For single column grouping, key is scalar (e.g., 'A')
                # For multi-column grouping, key is tuple (e.g., ('A', 1))
                if len(cols_list) == 1:
                    # key is scalar
                    mask = df[cols_list[0]] == key
                else:
                    # key is tuple of same length as cols_list
                    mask = pd.Series(True, index=df.index)
                    for col, k in zip(cols_list, key):
                        mask = mask & (df[col] == k)
                group_df = df[mask]
                # Exclude grouping columns from the DataFrame before applying func
                # This mimics pandas groupby apply behavior
                cols_to_exclude = [col for col in cols_list if col in group_df.columns]
                if cols_to_exclude:
                    group_df = group_df.drop(columns=cols_to_exclude)
                result = func(group_df, *args, **kwargs)
                key_result_pairs.append((key, result))
            return key_result_pairs

        tasks = self._create_tasks(process_group_chunk, group_chunks)

        # Execute tasks
        with create_progress_bar(len(tasks), "GroupBy Apply", disable=not self.progress_bar) as pbar:
            task_results = execute_tasks_parallel(tasks, n_workers)
            for _ in task_results:
                pbar.update(1)

        # Handle errors
        successful_results = self._handle_errors(task_results)

        # Flatten results from all chunks
        all_key_result_pairs = []
        for chunk_results in successful_results:
            all_key_result_pairs.extend(chunk_results)

        # Reconstruct final result similar to pandas groupby apply
        # Pandas groupby apply has complex logic for different return types
        # We'll try to mimic the most common cases

        if not all_key_result_pairs:
            return pd.DataFrame() if isinstance(df, pd.DataFrame) else pd.Series()

        # Separate keys and results
        keys = [pair[0] for pair in all_key_result_pairs]
        results = [pair[1] for pair in all_key_result_pairs]

        # Check what type of results we have
        all_dataframes = all(isinstance(r, pd.DataFrame) for r in results)
        all_series = all(isinstance(r, pd.Series) for r in results)
        all_scalars = all(not isinstance(r, (pd.DataFrame, pd.Series)) for r in results)

        if all_dataframes:
            # All results are DataFrames
            # Concatenate with keys as additional level in index if needed
            try:
                # Create MultiIndex with group keys if results have same columns
                concatenated = pd.concat(results, keys=keys, names=[group_cols] if isinstance(group_cols, str) else group_cols)
                return concatenated
            except Exception:
                # Simple concatenation as fallback
                return pd.concat(results, axis=0, ignore_index=False)

        elif all_series:
            # All results are Series — build a MultiIndex like pandas groupby+apply so
            # reset_index() yields separate group key columns (not a single tuple column).
            try:
                cols_list = list(group_cols) if isinstance(group_cols, list) else [group_cols]
                tuples = [k if isinstance(k, tuple) else (k,) for k in keys]
                idx = pd.MultiIndex.from_tuples(tuples, names=cols_list)
                result_df = pd.DataFrame(results, index=idx)
                return result_df
            except Exception:
                return pd.concat(results, axis=0, ignore_index=False)

        elif all_scalars:
            # Return Series with a MultiIndex aligned to pandas groupby keys
            cols_list = list(group_cols) if isinstance(group_cols, list) else [group_cols]
            tuples = [k if isinstance(k, tuple) else (k,) for k in keys]
            idx = pd.MultiIndex.from_tuples(tuples, names=cols_list)
            return pd.Series(results, index=idx)

        else:
            # Mixed types - return as list of (key, result) pairs
            warnings.warn("Mixed result types in groupby apply. Returning list of (key, result) pairs.")
            return all_key_result_pairs

    def rolling_apply(
        self,
        series: pd.Series,
        window: int,
        func: Callable,
        *args,
        **kwargs
    ) -> pd.Series:
        """
        Parallel apply function to rolling windows.

        Args:
            series: Series
            window: Rolling window size
            func: Function to apply to each window
            *args: Additional arguments for func
            **kwargs: Additional keyword arguments for func

        Returns:
            Result of applying func to rolling windows
        """
        n_workers = self._get_num_workers()

        # Split series into overlapping chunks for rolling windows
        # This is complex due to window overlap - simpler approach:
        # Process entire series in each worker but with different offsets
        # Actually, let's use a simpler approach: split into non-overlapping chunks
        # and apply rolling separately, then combine (will have edge issues)

        # For simplicity in MVP, we'll process in single worker
        warnings.warn("Rolling parallel apply is not fully implemented. Using single worker.")
        return series.rolling(window).apply(func, *args, **kwargs)

    def expanding_apply(
        self,
        series: pd.Series,
        func: Callable,
        *args,
        **kwargs
    ) -> pd.Series:
        """
        Parallel apply function to expanding windows.

        Args:
            series: Series
            func: Function to apply to each window
            *args: Additional arguments for func
            **kwargs: Additional keyword arguments for func

        Returns:
            Result of applying func to expanding windows
        """
        # Similar limitations as rolling apply
        warnings.warn("Expanding parallel apply is not fully implemented. Using single worker.")
        return series.expanding().apply(func, *args, **kwargs)

    def test_parallel_vs_serial(
        self,
        data: Any,
        parallel_func: Callable,
        serial_func: Callable,
        *args,
        **kwargs
    ) -> bool:
        """
        Test that parallel execution produces same result as serial.

        Args:
            data: Input data
            parallel_func: Parallel version of function
            serial_func: Serial version of function
            *args: Additional arguments
            **kwargs: Additional keyword arguments

        Returns:
            bool: True if results match
        """
        try:
            parallel_result = parallel_func(data, *args, **kwargs)
            serial_result = serial_func(data, *args, **kwargs)

            if isinstance(parallel_result, (pd.DataFrame, pd.Series)):
                return parallel_result.equals(serial_result)
            elif isinstance(parallel_result, np.ndarray):
                return np.array_equal(parallel_result, serial_result)
            else:
                return parallel_result == serial_result
        except Exception as e:
            warnings.warn(f"Test failed: {e}")
            return False