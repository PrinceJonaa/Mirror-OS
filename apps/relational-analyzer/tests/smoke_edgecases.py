import os
import json
import numpy as np
import pandas as pd
from pathlib import Path

# Adjust import path to allow running directly
import sys
ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT / 'tools' / 'relational_math'))

import importlib.util
spec = importlib.util.spec_from_file_location('td', str(ROOT / 'tools' / 'relational_math' / 'truth_distortion_unified.py'))
if spec is None or spec.loader is None:
    raise ImportError('Unable to load truth_distortion_unified module spec')
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

OUT = ROOT / 'tests' / 'out'
OUT.mkdir(parents=True, exist_ok=True)


def write_csv(path: Path, arr):
    df = pd.DataFrame(arr)
    df.to_csv(path, index=False)


def test_empty_csv():
    p = OUT / 'empty.csv'
    p.write_text('')
    try:
        mod.run_unified_diagnostic(str(p), data_type='auto', out_dir=str(OUT / 'empty_out'), skip_visuals=True)
        print('ERROR: expected failure for empty CSV')
    except ValueError as e:
        assert 'empty' in str(e).lower()
        print('OK: empty CSV raised ValueError')


def test_tabular_no_numeric():
    p = OUT / 'nonumeric.csv'
    pd.DataFrame({'a':['x','y'], 'b':['c','d']}).to_csv(p, index=False)
    try:
        mod.run_unified_diagnostic(str(p), data_type='tabular', out_dir=str(OUT / 'nonumeric_out'), skip_visuals=True)
        print('ERROR: expected failure for non-numeric tabular')
    except ValueError as e:
        assert 'no numeric' in str(e).lower()
        print('OK: non-numeric tabular raised ValueError')


def test_identity_corr():
    R = np.eye(10)
    p = OUT / 'identity.csv'
    write_csv(p, R)
    rep = mod.run_unified_diagnostic(str(p), data_type='corr', out_dir=str(OUT / 'identity_out'), skip_visuals=True)
    assert rep['shape']['shape'] == 'Identity'
    print('OK: identity correlation recognized')


def test_star_graph_edgelist():
    # Star graph with 6 nodes (0 center)
    edges = np.array([[0,i] for i in range(1,6)])
    p = OUT / 'star.csv'
    write_csv(p, edges)
    rep = mod.run_unified_diagnostic(str(p), data_type='edgelist', out_dir=str(OUT / 'star_out'), skip_visuals=True)
    assert rep['shape']['shape'] in ['Star','Core-Periphery','Intermediate']
    print('OK: edgelist processed (shape:', rep['shape']['shape'], ')')


def test_large_null_skip():
    # Opt-in to avoid heavy computation by default
    if os.environ.get('TDD_LARGE', '0') != '1':
        print('SKIP: large null-skip test (set TDD_LARGE=1 to run)')
        return
    R = np.eye(6000)
    res = mod.compute_meff(R, n_permutations=100)
    assert res.get('null_permutations_skipped', False) is True
    print('OK: null permutations skipped for large m')


if __name__ == '__main__':
    test_empty_csv()
    test_tabular_no_numeric()
    test_identity_corr()
    test_star_graph_edgelist()
    test_large_null_skip()
    print('\nAll smoke tests ran.')
