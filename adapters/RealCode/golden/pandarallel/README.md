# Pandarallel

Simple and efficient parallelization tool for pandas.

## Overview

Pandarallel provides drop-in parallel replacements for common pandas operations, allowing you to speed up data processing tasks without manual multiprocessing boilerplate. Just replace `.apply()` with `.parallel_apply()` and let Pandarallel handle the rest.

## Features

- **Parallel DataFrame operations**: `.parallel_apply()`, `.parallel_applymap()`
- **Parallel Series operations**: `.parallel_apply()`, `.parallel_map()`
- **Parallel GroupBy operations**: `.parallel_apply()` on grouped data
- **Parallel window operations**: `.parallel_apply()` on rolling and expanding windows (limited support)
- **Automatic CPU detection**: Uses all available CPU cores by default
- **Memory optimization**: Uses shared memory (`/dev/shm`) when available for faster IPC
- **Progress bars**: Real-time progress tracking with `tqdm`
- **Cross-platform**: Works on Windows, Linux, and macOS
- **Error handling**: Exceptions in user functions are properly propagated

## Installation

```bash
pip install -r requirements.txt
```

Or install in development mode:

```bash
pip install -e .
```

## Quick Start

```python
import pandas as pd
import pandarallel

# Initialize pandarallel (required before use)
pandarallel.initialize()

# Create a sample DataFrame
df = pd.DataFrame({'A': range(1000), 'B': range(1000, 2000)})

# Serial version (uses single core)
result_serial = df.apply(lambda x: x.sum(), axis=1)

# Parallel version (uses all available cores)
result_parallel = df.parallel_apply(lambda x: x.sum(), axis=1)

# Results are identical
print(result_serial.equals(result_parallel))  # True
```

## Configuration

Customize Pandarallel behavior during initialization:

```python
pandarallel.initialize(
    nb_workers=4,           # Number of worker processes
    progress_bar=True,      # Show progress bars
    verbose=1,              # Verbosity level (0, 1, or 2)
    use_memory_fs=True      # Use shared memory if available
)
```

### Parameters

- `nb_workers`: Number of worker processes (default: number of physical CPU cores)
- `progress_bar`: Whether to display progress bars (default: True)
- `verbose`: Verbosity level: 0 (silent), 1 (info), 2 (debug) (default: 1)
- `use_memory_fs`: Use memory file system (`/dev/shm`) for IPC (default: auto-detect)

## Available Methods

### DataFrame
- `df.parallel_apply(func, axis=0, *args, **kwargs)`
- `df.parallel_applymap(func, *args, **kwargs)`

### Series
- `series.parallel_apply(func, *args, **kwargs)`
- `series.parallel_map(func, *args, **kwargs)`

### GroupBy
- `df.groupby(cols).parallel_apply(func, *args, **kwargs)`
- `series.groupby(cols).parallel_apply(func, *args, **kwargs)`

### Rolling/Expanding (limited)
- `series.rolling(window).parallel_apply(func, *args, **kwargs)`
- `series.expanding().parallel_apply(func, *args, **kwargs)`

## Examples

### Basic DataFrame Apply
```python
df = pd.DataFrame({'A': range(10000), 'B': range(10000, 20000)})

# Apply a function to each row
def process_row(row):
    return row['A'] * 2 + row['B']

result = df.parallel_apply(process_row, axis=1)
```

### Element-wise Operations
```python
# Apply function to every element
df = pd.DataFrame(np.random.randn(1000, 100))
result = df.parallel_applymap(lambda x: x**2 + 1)
```

### GroupBy Operations
```python
df = pd.DataFrame({
    'group': ['A', 'B', 'A', 'B', 'A', 'B'],
    'value': [1, 2, 3, 4, 5, 6]
})

# Apply function to each group
def group_summary(group):
    return pd.Series({
        'mean': group['value'].mean(),
        'sum': group['value'].sum(),
        'count': len(group)
    })

result = df.groupby('group').parallel_apply(group_summary)
```

### Series Operations
```python
series = pd.Series(range(10000))

# Apply function to each element
result = series.parallel_apply(lambda x: x**2)

# Map values
result = series.parallel_map(lambda x: f"value_{x}")
```

## Testing

Run the full test suite:

```bash
cd tests
bash test.sh
```

Or run individual test files:

```bash
python tests/test_runner.py --test-file tests/test_cases/feature1_core_operations.json
```

Test outputs are written to `tests/stdout/` with naming convention:
`{filename.stem}@{case_index.zfill(3)}.txt`

## How It Works

1. **Data Chunking**: Input data is split into chunks based on number of workers
2. **Process Pool**: Worker processes are created using `multiprocessing.Pool`
3. **Task Distribution**: Each chunk is processed by a separate worker
4. **Result Aggregation**: Results from workers are combined in correct order
5. **IPC Optimization**: Uses shared memory on Linux/Unix for faster data transfer

## Limitations

- **Rolling/Expanding windows**: Parallel implementation is limited due to window overlap
- **Large memory usage**: Each worker gets a copy of the function and its environment
- **Picklable functions**: Functions must be serializable with `pickle` or `dill`
- **Global state**: Changes to global variables in workers won't propagate back

## Performance Tips

1. **Use vectorized operations** when possible (they're faster than any parallel apply)
2. **Set appropriate chunk size**: Very small chunks may have overhead
3. **Disable progress bar** for maximum speed: `progress_bar=False`
4. **Use shared memory** on Linux systems for large data transfers

## License

MIT

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.