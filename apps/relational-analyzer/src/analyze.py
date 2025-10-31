#!/usr/bin/env python3
"""
Quick analysis launcher - analyze any dataset with sensible defaults.
Usage: python analyze.py DATASET_NAME [--full]
"""

import sys
import subprocess
from pathlib import Path

DATA_DIR = Path(__file__).parent / "data"
RESULTS_DIR = Path(__file__).parent / "results"

def find_dataset(name):
    """Find a dataset by partial name match."""
    csv_files = list(DATA_DIR.glob("*.csv"))
    
    # Exact match
    exact = [f for f in csv_files if f.stem.lower() == name.lower()]
    if exact:
        return exact[0]
    
    # Partial match
    partial = [f for f in csv_files if name.lower() in f.stem.lower()]
    if partial:
        return partial[0]
    
    return None

def main():
    if len(sys.argv) < 2:
        print("Usage: python analyze.py DATASET_NAME [OPTIONS]")
        print("\nAvailable datasets:")
        csv_files = sorted(DATA_DIR.glob("*.csv"))
        for f in csv_files:
            print(f"  - {f.stem}")
        print("\nExamples:")
        print("  python analyze.py discipline")
        print("  python analyze.py discipline_enriched --seed 42")
        sys.exit(1)
    
    dataset_name = sys.argv[1]
    extra_args = sys.argv[2:]
    
    # Find the dataset
    dataset_path = find_dataset(dataset_name)
    if not dataset_path:
        print(f"❌ Dataset not found: {dataset_name}")
        print("\nAvailable datasets:")
        csv_files = sorted(DATA_DIR.glob("*.csv"))
        for f in csv_files:
            print(f"  - {f.stem}")
        sys.exit(1)
    
    # Generate output directory name
    output_name = dataset_path.stem.replace("_", "-")
    output_dir = RESULTS_DIR / output_name
    
    # Build command
    cmd = [
        "python", "truth_distortion_unified.py",
        "--data", str(dataset_path),
        "--type", "auto",
        "--out", str(output_dir),
    ]
    
    # Add extra arguments
    cmd.extend(extra_args)
    
    print("=" * 80)
    print(f"📊 Analyzing: {dataset_path.name}")
    print(f"📁 Output: {output_dir}")
    print("=" * 80)
    print()
    
    # Run the analysis
    result = subprocess.run(cmd, cwd=Path(__file__).parent)
    
    if result.returncode == 0:
        print("\n" + "=" * 80)
        print("✅ Analysis complete!")
        print(f"📂 Results: {output_dir}/")
        print("=" * 80)
    else:
        print("\n❌ Analysis failed")
        sys.exit(1)

if __name__ == "__main__":
    main()
