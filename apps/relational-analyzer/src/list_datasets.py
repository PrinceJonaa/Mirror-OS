#!/usr/bin/env python3
"""
List and describe all available datasets in the data/ directory.
Usage: python list_datasets.py
"""

import os
import pandas as pd
from pathlib import Path

DATA_DIR = Path(__file__).parent / "data"

def get_file_size(path):
    """Get human-readable file size."""
    size = os.path.getsize(path)
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size < 1024.0:
            return f"{size:.1f} {unit}"
        size /= 1024.0
    return f"{size:.1f} TB"

def analyze_csv(filepath):
    """Quick analysis of CSV file."""
    try:
        df = pd.read_csv(filepath, nrows=1000, low_memory=False)
        total_rows = sum(1 for _ in open(filepath)) - 1  # Subtract header
        
        numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
        object_cols = df.select_dtypes(include=['object']).columns.tolist()
        
        return {
            'rows': total_rows,
            'cols': len(df.columns),
            'numeric': len(numeric_cols),
            'categorical': len(object_cols),
            'shape': (total_rows, len(df.columns))
        }
    except Exception as e:
        return {'error': str(e)}

def main():
    print("=" * 80)
    print("AVAILABLE DATASETS")
    print("=" * 80)
    
    if not DATA_DIR.exists():
        print(f"\n⚠️  Data directory not found: {DATA_DIR}")
        return
    
    csv_files = sorted(DATA_DIR.glob("*.csv"))
    
    if not csv_files:
        print("\n📭 No CSV files found in data/ directory")
        print(f"\nPlace your data files in: {DATA_DIR}")
        return
    
    print(f"\nFound {len(csv_files)} dataset(s):\n")
    
    for i, filepath in enumerate(csv_files, 1):
        filename = filepath.name
        size = get_file_size(filepath)
        
        print(f"{i}. {filename}")
        print(f"   Path: {filepath}")
        print(f"   Size: {size}")
        
        info = analyze_csv(filepath)
        if 'error' in info:
            print(f"   ⚠️  Error reading file: {info['error']}")
        else:
            print(f"   Shape: {info['shape'][0]:,} rows × {info['shape'][1]} columns")
            print(f"   Numeric: {info['numeric']} | Categorical: {info['categorical']}")
        print()
    
    print("=" * 80)
    print("USAGE")
    print("=" * 80)
    print("\nTo analyze a dataset, run:")
    print("  python truth_distortion_unified.py --data data/FILENAME.csv --type auto --out results/ANALYSIS_NAME")
    print("\nExample:")
    print("  python truth_distortion_unified.py --data data/Report_Card_Discipline_for_2022-23.csv --type tabular --out results/discipline_study")
    print()

if __name__ == "__main__":
    main()
