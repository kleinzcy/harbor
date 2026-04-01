#!/usr/bin/env python
"""Simple test of pandarallel functionality."""
import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import pandas as pd
import pandarallel


def main():
    print("Testing Pandarallel...")

    # Initialize with debug verbosity
    pandarallel.initialize(verbose=2, progress_bar=False)

    # Create test data
    df = pd.DataFrame({
        'A': range(100),
        'B': range(100, 200),
        'C': range(200, 300)
    })

    series = pd.Series(range(100))

    print(f"DataFrame shape: {df.shape}")
    print(f"Series length: {len(series)}")

    # Test 1: DataFrame apply (axis=0)
    print("\n1. Testing DataFrame.apply (axis=0)...")
    result_parallel = df.parallel_apply(lambda x: x.sum(), axis=0)
    result_serial = df.apply(lambda x: x.sum(), axis=0)
    print(f"   Parallel type: {type(result_parallel)}")
    print(f"   Serial type:   {type(result_serial)}")
    print(f"   Parallel shape: {result_parallel.shape if hasattr(result_parallel, 'shape') else 'N/A'}")
    print(f"   Serial shape:   {result_serial.shape if hasattr(result_serial, 'shape') else 'N/A'}")
    # Try to print values based on type
    if isinstance(result_parallel, pd.Series):
        print(f"   Parallel values: {result_parallel.tolist()[:3]}...")
        print(f"   Serial values:   {result_serial.tolist()[:3]}...")
    elif isinstance(result_parallel, pd.DataFrame):
        print(f"   Parallel columns: {result_parallel.columns.tolist()}")
        if isinstance(result_serial, pd.DataFrame):
            print(f"   Serial columns:   {result_serial.columns.tolist()}")
        else:
            print("   Serial is Series, no columns")
    print(f"   Match:    {result_parallel.equals(result_serial)}")

    # Test 2: DataFrame apply (axis=1)
    print("\n2. Testing DataFrame.apply (axis=1)...")
    result_parallel = df.parallel_apply(lambda x: x.sum(), axis=1)
    result_serial = df.apply(lambda x: x.sum(), axis=1)
    print(f"   Parallel shape: {result_parallel.shape}")
    print(f"   Serial shape:   {result_serial.shape}")
    print(f"   Match:          {result_parallel.equals(result_serial)}")

    # Test 3: Series apply
    print("\n3. Testing Series.apply...")
    result_parallel = series.parallel_apply(lambda x: x**2)
    result_serial = series.apply(lambda x: x**2)
    print(f"   Parallel first 5: {result_parallel.tolist()[:5]}")
    print(f"   Serial first 5:   {result_serial.tolist()[:5]}")
    print(f"   Match:            {result_parallel.equals(result_serial)}")

    # Test 4: Series map
    print("\n4. Testing Series.map...")
    result_parallel = series.parallel_map(lambda x: x + 100)
    result_serial = series.map(lambda x: x + 100)
    print(f"   Parallel first 5: {result_parallel.tolist()[:5]}")
    print(f"   Serial first 5:   {result_serial.tolist()[:5]}")
    print(f"   Match:            {result_parallel.equals(result_serial)}")

    # Test 5: GroupBy apply
    print("\n5. Testing GroupBy.apply...")
    df['group'] = ['A', 'B'] * 50
    result_parallel = df.groupby('group').parallel_apply(lambda g: g.sum())
    result_serial = df.groupby('group').apply(lambda g: g.sum())
    print(f"   Parallel shape: {result_parallel.shape}")
    print(f"   Serial shape:   {result_serial.shape}")
    print(f"   Parallel columns: {result_parallel.columns.tolist() if hasattr(result_parallel, 'columns') else 'N/A'}")
    print(f"   Serial columns:   {result_serial.columns.tolist() if hasattr(result_serial, 'columns') else 'N/A'}")
    print(f"   Parallel index: {result_parallel.index.tolist() if hasattr(result_parallel, 'index') else 'N/A'}")
    print(f"   Serial index:   {result_serial.index.tolist() if hasattr(result_serial, 'index') else 'N/A'}")
    print(f"   Match:          {result_parallel.equals(result_serial)}")

    print("\nAll tests completed!")


if __name__ == "__main__":
    main()