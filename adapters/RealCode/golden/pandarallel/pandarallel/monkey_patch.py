"""
Monkey patch pandas objects to add parallel methods.
"""
import pandas as pd
import warnings

from pandas.core.window.rolling import RollingGroupby
from pandas.core.window.expanding import ExpandingGroupby

from .config import _config
from .core import ParallelEngine


def patch_dataframe():
    """Add parallel methods to DataFrame."""
    if hasattr(pd.DataFrame, '_pandarallel_patched'):
        return

    original_apply = pd.DataFrame.apply
    # Handle pandas version differences: applymap was renamed to map in pandas 2.0+
    if hasattr(pd.DataFrame, 'applymap'):
        original_applymap = pd.DataFrame.applymap
        applymap_name = 'applymap'
    else:
        original_applymap = pd.DataFrame.map
        applymap_name = 'map'

    def parallel_apply(self, func, axis=0, *args, **kwargs):
        """Parallel version of DataFrame.apply."""
        if not _config.is_initialized:
            warnings.warn(
                "Pandarallel not initialized. Call pandarallel.initialize() first. "
                "Falling back to serial apply.",
                UserWarning
            )
            return original_apply(self, func, axis=axis, *args, **kwargs)

        engine = ParallelEngine()
        return engine.apply(self, func, axis=axis, *args, **kwargs)

    def parallel_applymap(self, func, *args, **kwargs):
        """Parallel version of DataFrame.applymap."""
        if not _config.is_initialized:
            warnings.warn(
                "Pandarallel not initialized. Call pandarallel.initialize() first. "
                "Falling back to serial applymap.",
                UserWarning
            )
            return original_applymap(self, func, *args, **kwargs)

        engine = ParallelEngine()
        return engine.applymap(self, func, *args, **kwargs)

    # Add methods to DataFrame
    pd.DataFrame.parallel_apply = parallel_apply
    pd.DataFrame.parallel_applymap = parallel_applymap

    # Mark as patched
    pd.DataFrame._pandarallel_patched = True


def patch_series():
    """Add parallel methods to Series."""
    if hasattr(pd.Series, '_pandarallel_patched'):
        return

    original_apply = pd.Series.apply
    original_map = pd.Series.map

    def parallel_apply(self, func, *args, **kwargs):
        """Parallel version of Series.apply."""
        if not _config.is_initialized:
            warnings.warn(
                "Pandarallel not initialized. Call pandarallel.initialize() first. "
                "Falling back to serial apply.",
                UserWarning
            )
            return original_apply(self, func, *args, **kwargs)

        engine = ParallelEngine()
        return engine.apply(self, func, axis=0, *args, **kwargs)

    def parallel_map(self, func, *args, **kwargs):
        """Parallel version of Series.map."""
        if not _config.is_initialized:
            warnings.warn(
                "Pandarallel not initialized. Call pandarallel.initialize() first. "
                "Falling back to serial map.",
                UserWarning
            )
            return original_map(self, func, *args, **kwargs)

        engine = ParallelEngine()
        return engine.map(self, func, *args, **kwargs)

    # Add methods to Series
    pd.Series.parallel_apply = parallel_apply
    pd.Series.parallel_map = parallel_map

    # Mark as patched
    pd.Series._pandarallel_patched = True


def patch_groupby():
    """Add parallel methods to GroupBy objects."""
    if hasattr(pd.core.groupby.DataFrameGroupBy, '_pandarallel_patched'):
        return

    original_groupby_apply = pd.core.groupby.DataFrameGroupBy.apply

    def parallel_groupby_apply(self, func, *args, **kwargs):
        """Parallel version of GroupBy.apply."""
        if not _config.is_initialized:
            warnings.warn(
                "Pandarallel not initialized. Call pandarallel.initialize() first. "
                "Falling back to serial groupby apply.",
                UserWarning
            )
            return original_groupby_apply(self, func, *args, **kwargs)

        # Get the original DataFrame and grouping columns
        # In pandas GroupBy objects:
        # - self.obj: the original DataFrame/Series
        # - self.grouper.keys: grouping column names (for DataFrameGroupBy)
        # - self.keys: alternative way to get grouping columns
        try:
            obj = self.obj
            # Try different ways to get grouping columns based on pandas version
            if hasattr(self, 'grouper') and hasattr(self.grouper, 'keys'):
                group_cols = self.grouper.keys
            elif hasattr(self, 'keys'):
                group_cols = self.keys
            else:
                # Fallback: try to get from groupby object attributes
                group_cols = self._groupby.keys if hasattr(self, '_groupby') else []
        except AttributeError:
            # Fall back to serial apply if we can't extract needed information
            warnings.warn(
                "Could not extract GroupBy information for parallel processing. "
                "Falling back to serial groupby apply.",
                UserWarning
            )
            return original_groupby_apply(self, func, *args, **kwargs)

        engine = ParallelEngine()
        return engine.groupby_apply(obj, group_cols, func, *args, **kwargs)

    # Add methods to GroupBy classes
    pd.core.groupby.DataFrameGroupBy.parallel_apply = parallel_groupby_apply
    pd.core.groupby.SeriesGroupBy.parallel_apply = parallel_groupby_apply

    # Mark as patched
    pd.core.groupby.DataFrameGroupBy._pandarallel_patched = True
    pd.core.groupby.SeriesGroupBy._pandarallel_patched = True


def patch_rolling_expanding():
    """Add parallel methods to Rolling and Expanding objects."""
    # Note: These are more complex due to window overlap
    # For MVP, we'll implement basic stubs

    # Rolling
    if not hasattr(pd.core.window.Rolling, '_pandarallel_patched'):
        original_rolling_apply = pd.core.window.Rolling.apply

        def parallel_rolling_apply(self, func, *args, **kwargs):
            """Parallel version of Rolling.apply (stub)."""
            if not _config.is_initialized:
                warnings.warn(
                    "Pandarallel not initialized. Call pandarallel.initialize() first. "
                    "Falling back to serial rolling apply.",
                    UserWarning
                )
                return original_rolling_apply(self, func, *args, **kwargs)

            # RollingGroupby inherits Rolling but carries a DataFrame + group keys.
            # ParallelEngine.rolling_apply only handles Series; using it here corrupts
            # the MultiIndex and breaks correctness — defer to pandas.
            if isinstance(self, RollingGroupby):
                return original_rolling_apply(self, func, *args, **kwargs)

            warnings.warn(
                "Parallel rolling apply is limited in this version. "
                "Using single worker implementation.",
                UserWarning
            )
            engine = ParallelEngine()
            return engine.rolling_apply(self._selected_obj, self.window, func, *args, **kwargs)

        pd.core.window.Rolling.parallel_apply = parallel_rolling_apply
        pd.core.window.Rolling._pandarallel_patched = True

    # Expanding
    if not hasattr(pd.core.window.Expanding, '_pandarallel_patched'):
        original_expanding_apply = pd.core.window.Expanding.apply

        def parallel_expanding_apply(self, func, *args, **kwargs):
            """Parallel version of Expanding.apply (stub)."""
            if not _config.is_initialized:
                warnings.warn(
                    "Pandarallel not initialized. Call pandarallel.initialize() first. "
                    "Falling back to serial expanding apply.",
                    UserWarning
                )
                return original_expanding_apply(self, func, *args, **kwargs)

            # Same as RollingGroupby: grouped expanding must stay on pandas' path.
            if isinstance(self, ExpandingGroupby):
                return original_expanding_apply(self, func, *args, **kwargs)

            warnings.warn(
                "Parallel expanding apply is limited in this version. "
                "Using single worker implementation.",
                UserWarning
            )
            engine = ParallelEngine()
            return engine.expanding_apply(self._selected_obj, func, *args, **kwargs)

        pd.core.window.Expanding.parallel_apply = parallel_expanding_apply
        pd.core.window.Expanding._pandarallel_patched = True


def patch_all():
    """Apply all monkey patches."""
    patch_dataframe()
    patch_series()
    patch_groupby()
    patch_rolling_expanding()

    if _config.verbose >= 1:
        print("Pandarallel: All pandas objects patched with parallel methods")


def unpatch_all():
    """Remove all monkey patches."""
    # DataFrame
    if hasattr(pd.DataFrame, '_pandarallel_patched'):
        delattr(pd.DataFrame, 'parallel_apply')
        delattr(pd.DataFrame, 'parallel_applymap')
        delattr(pd.DataFrame, '_pandarallel_patched')

    # Series
    if hasattr(pd.Series, '_pandarallel_patched'):
        delattr(pd.Series, 'parallel_apply')
        delattr(pd.Series, 'parallel_map')
        delattr(pd.Series, '_pandarallel_patched')

    # GroupBy
    if hasattr(pd.core.groupby.DataFrameGroupBy, '_pandarallel_patched'):
        delattr(pd.core.groupby.DataFrameGroupBy, 'parallel_apply')
        delattr(pd.core.groupby.DataFrameGroupBy, '_pandarallel_patched')
    if hasattr(pd.core.groupby.SeriesGroupBy, '_pandarallel_patched'):
        delattr(pd.core.groupby.SeriesGroupBy, 'parallel_apply')
        delattr(pd.core.groupby.SeriesGroupBy, '_pandarallel_patched')

    # Rolling
    if hasattr(pd.core.window.Rolling, '_pandarallel_patched'):
        delattr(pd.core.window.Rolling, 'parallel_apply')
        delattr(pd.core.window.Rolling, '_pandarallel_patched')

    # Expanding
    if hasattr(pd.core.window.Expanding, '_pandarallel_patched'):
        delattr(pd.core.window.Expanding, 'parallel_apply')
        delattr(pd.core.window.Expanding, '_pandarallel_patched')

    if _config.verbose >= 1:
        print("Pandarallel: All patches removed")