#!/usr/bin/env python3
"""
NFL Relational Analysis - Truth/Distortion Integration
========================================================

Uses truth_distortion_unified.py to analyze player movement patterns
and identify relational structures in the field.

Key Applications:
1. Player Coupling Analysis: Which players move together? (high correlation)
2. Role-Based Clustering: Do roles form natural communities?
3. Feature Importance: Which features drive dimensional collapse?
4. Prediction Validation: Is our model capturing true relational structure?
"""

import numpy as np
import pandas as pd
from pathlib import Path
import sys
sys.path.append(str(Path(__file__).parent))

from truth_distortion_unified import (
    compute_meff,
    compute_rfi,
    classify_shape,
    map_to_lattice,
    compute_collapse_map,
    compute_residue_profile
)
from nfl_prediction_engine import DataLoader, RelationalFeatureEngine


class NFLRelationalAnalyzer:
    """
    Analyzes NFL tracking data through relational math lens.
    
    Treats each play as a relational system and applies truth/distortion
    analysis to understand player coupling and movement patterns.
    """
    
    def __init__(self, data_dir: Path):
        self.data_dir = data_dir
        self.loader = DataLoader(data_dir)
        self.feature_engine = RelationalFeatureEngine()
        
    def analyze_play_correlation(self, play_state) -> dict:
        """
        Analyze correlation structure of a single play.
        
        Returns M_eff, RFI, and collapse potential for player movements.
        """
        # Extract features for all players
        features = self.feature_engine.extract_features(play_state)
        
        # Build feature matrix (players x features)
        feature_cols = [
            'x', 'y', 'vx', 'vy', 's', 'a',
            'dist_to_ball', 'speed_toward_ball', 'angle_to_ball'
        ]
        X = features[feature_cols].values
        
        # Compute player-player correlation
        if X.shape[0] < 2:
            return {'status': 'degenerate', 'n_players': X.shape[0]}
        
        R = np.corrcoef(X)
        
        # Compute M_eff (dimensional collapse)
        meff_metrics = compute_meff(R, n_permutations=None)
        
        # Build adjacency from correlation (high correlation = edge)
        threshold = 0.5
        A = (np.abs(R) > threshold).astype(int)
        np.fill_diagonal(A, 0)
        
        # Compute RFI (relational topology)
        rfi_metrics = compute_rfi(A, weighted=False)
        
        # Classify shape
        shape_metrics = classify_shape(A, rfi_metrics, R)
        
        # Map to lattice
        lattice_map = map_to_lattice(meff_metrics, rfi_metrics, shape_metrics)
        
        return {
            'game_id': play_state.game_id,
            'play_id': play_state.play_id,
            'n_players': X.shape[0],
            'meff_min': meff_metrics['meff_min'],
            'collapse_ratio': meff_metrics['collapse_ratio'],
            'rfi': rfi_metrics['rfi'],
            'modularity_Q': rfi_metrics['modularity_Q'],
            'shape': shape_metrics['shape'],
            'lattice_position': lattice_map['lattice_position'],
            'collapse_potential': lattice_map['collapse_potential'],
            'top_eigenvalues': meff_metrics['top_10_eigenvalues'][:3],
            'status': 'computed'
        }
    
    def analyze_role_structure(self, input_df: pd.DataFrame) -> dict:
        """
        Analyze how roles cluster across all plays.
        
        Question: Do Passers, Receivers, and Coverage form distinct communities?
        """
        # Get last frame for all plays
        last_frames = input_df.groupby(['game_id', 'play_id', 'nfl_id']).last().reset_index()
        
        # Compute distance to ball for each player
        last_frames['dist_to_ball'] = np.sqrt(
            (last_frames['x'] - last_frames['ball_land_x'])**2 + 
            (last_frames['y'] - last_frames['ball_land_y'])**2
        )
        
        # Compute speed toward ball
        dx = last_frames['ball_land_x'] - last_frames['x']
        dy = last_frames['ball_land_y'] - last_frames['y']
        dist = np.sqrt(dx**2 + dy**2)
        vx = last_frames['s'] * np.cos(np.radians(last_frames['dir']))
        vy = last_frames['s'] * np.sin(np.radians(last_frames['dir']))
        last_frames['speed_toward_ball'] = (vx * dx + vy * dy) / (dist + 1e-6)
        
        # Group by role, compute mean features
        role_profiles = last_frames.groupby('player_role').agg({
            's': 'mean',
            'a': 'mean',
            'dist_to_ball': 'mean',
            'speed_toward_ball': 'mean',
            'x': 'std',  # Positional variance
            'y': 'std'
        }).fillna(0)
        
        # Compute role-role correlation
        R = np.corrcoef(role_profiles.values)
        
        # M_eff analysis
        meff_metrics = compute_meff(R, n_permutations=None)
        
        # Adjacency
        A = (np.abs(R) > 0.3).astype(int)
        np.fill_diagonal(A, 0)
        
        # RFI
        rfi_metrics = compute_rfi(A, weighted=False)
        
        # Collapse map (which roles drive the structure?)
        result_dir = Path('results/nfl_analysis')
        result_dir.mkdir(parents=True, exist_ok=True)
        collapse_map = compute_collapse_map(R, meff_metrics, str(result_dir), n_top=4)
        
        role_names = list(role_profiles.index)
        
        return {
            'roles': role_names,
            'n_roles': len(role_names),
            'meff_min': meff_metrics['meff_min'],
            'collapse_ratio': meff_metrics['collapse_ratio'],
            'rfi': rfi_metrics['rfi'],
            'modularity_Q': rfi_metrics['modularity_Q'],
            'correlation_matrix': R.tolist(),
            'role_profiles': role_profiles.to_dict(),
            'interpretation': self._interpret_role_structure(meff_metrics, rfi_metrics, role_names)
        }
    
    def _interpret_role_structure(self, meff_metrics, rfi_metrics, role_names):
        """Generate interpretation of role clustering."""
        collapse_ratio = meff_metrics['collapse_ratio']
        modularity = rfi_metrics['modularity_Q']
        
        if collapse_ratio < 0.3 and modularity > 0.4:
            return {
                'summary': "Roles form DISTINCT communities",
                'implication': "Role-specific models will work well - roles are separable",
                'recommendation': "Train separate predictors per role"
            }
        elif collapse_ratio < 0.5:
            return {
                'summary': "Roles are MODERATELY coupled",
                'implication': "Some shared behavior patterns across roles",
                'recommendation': "Use role embeddings + shared base model"
            }
        else:
            return {
                'summary': "Roles are HIGHLY entangled",
                'implication': "All players move similarly regardless of role",
                'recommendation': "Single unified model may suffice"
            }
    
    def analyze_feature_importance(self, play_state) -> dict:
        """
        Use collapse map to identify which features are most important.
        
        This tells us which features drive player movement patterns.
        """
        features = self.feature_engine.extract_features(play_state)
        
        feature_cols = [
            'dist_to_ball', 'speed_toward_ball', 'angle_to_ball',
            'dir_alignment_ball', 'accel_toward_ball',
            's', 'a', 'vx', 'vy',
            'nearest_player_dist', 'avg_k_nearest_dist'
        ]
        
        X = features[feature_cols].values
        
        if X.shape[0] < 2:
            return {'status': 'degenerate'}
        
        # Feature-feature correlation
        R = np.corrcoef(X.T)  # Transpose: features x features
        
        # M_eff
        meff_metrics = compute_meff(R, n_permutations=None)
        
        # Collapse map
        result_dir = Path('results/nfl_analysis')
        collapse_map = compute_collapse_map(R, meff_metrics, str(result_dir), n_top=5)
        
        if collapse_map.get('status') == 'computed':
            top_features = [feature_cols[i] for i in collapse_map['top_features'][:5]]
            scores = collapse_map['scores'][:5]
            
            return {
                'top_features': top_features,
                'collapse_scores': scores,
                'meff_min': meff_metrics['meff_min'],
                'interpretation': f"Top collapse driver: {top_features[0]} (drives {scores[0]/sum(scores)*100:.1f}% of structure)"
            }
        
        return {'status': 'failed'}
    
    def validate_predictions(self, predictions_df: pd.DataFrame, 
                            ground_truth_df: pd.DataFrame) -> dict:
        """
        Use truth/distortion framework to validate prediction quality.
        
        Question: Do our predictions preserve the relational structure?
        """
        # Merge predictions with ground truth
        merged = predictions_df.merge(
            ground_truth_df,
            on=['game_id', 'play_id', 'nfl_id', 'frame_id'],
            suffixes=('_pred', '_true')
        )
        
        # Compute error vectors
        errors = merged[['x_pred', 'y_pred']].values - merged[['x_true', 'y_true']].values
        
        # For each play, compute error correlation
        play_error_correlations = []
        
        for (game_id, play_id), play_group in merged.groupby(['game_id', 'play_id']):
            if len(play_group) < 2:
                continue
            
            # Error per player (aggregate over frames)
            player_errors = play_group.groupby('nfl_id')[['x_pred', 'y_pred', 'x_true', 'y_true']].agg('mean')
            error_vecs = player_errors[['x_pred', 'y_pred']].values - player_errors[['x_true', 'y_true']].values
            
            if len(error_vecs) < 2:
                continue
            
            # Error correlation matrix
            R_error = np.corrcoef(error_vecs)
            
            # Residue profile
            residue = compute_residue_profile(R_error)
            
            play_error_correlations.append({
                'game_id': game_id,
                'play_id': play_id,
                'residue_mean': residue['residue_mean'],
                'residue_level': residue['residue_level']
            })
        
        if not play_error_correlations:
            return {'status': 'insufficient_data'}
        
        error_df = pd.DataFrame(play_error_correlations)
        avg_residue = error_df['residue_mean'].mean()
        
        # Interpretation
        if avg_residue < 0.2:
            quality = "EXCELLENT"
            interpretation = "Errors are uncorrelated - model captures true structure"
        elif avg_residue < 0.4:
            quality = "GOOD"
            interpretation = "Low systematic bias - minor improvements possible"
        elif avg_residue < 0.6:
            quality = "MODERATE"
            interpretation = "Some systematic errors - check feature engineering"
        else:
            quality = "POOR"
            interpretation = "High error correlation - model missing relational patterns"
        
        return {
            'avg_error_residue': float(avg_residue),
            'quality': quality,
            'interpretation': interpretation,
            'recommendation': "Reduce residue by improving relational features" if avg_residue > 0.4 else "Model quality is sufficient"
        }


def main():
    """Run relational analysis on NFL data."""
    print("🔍 NFL Relational Analysis - Truth/Distortion Framework")
    print("=" * 60)
    
    data_dir = Path('data/nfl-big-data-bowl-2026-prediction')
    analyzer = NFLRelationalAnalyzer(data_dir)
    
    # Load sample data
    print("\n1. Loading data...")
    input_df, output_df = analyzer.loader.load_week(1)
    plays = analyzer.loader.get_all_plays(input_df)[:5]
    
    # Analyze individual plays
    print("\n2. Analyzing play-level relational structure...")
    play_analyses = []
    
    for game_id, play_id in plays:
        play_state = analyzer.loader.prepare_play_state(input_df, game_id, play_id)
        analysis = analyzer.analyze_play_correlation(play_state)
        play_analyses.append(analysis)
        
        print(f"\n   Play {game_id}-{play_id}:")
        print(f"   - Players: {analysis['n_players']}")
        print(f"   - M_eff: {analysis['meff_min']:.2f} (collapse ratio: {analysis['collapse_ratio']:.2%})")
        print(f"   - RFI: {analysis['rfi']:.3f}")
        print(f"   - Shape: {analysis['shape']}")
        print(f"   - Lattice: {analysis['lattice_position']}")
        print(f"   - Collapse Potential: {analysis['collapse_potential']}")
    
    # Analyze role structure
    print("\n3. Analyzing role-based clustering...")
    role_analysis = analyzer.analyze_role_structure(input_df)
    print(f"\n   Roles analyzed: {role_analysis['roles']}")
    print(f"   M_eff: {role_analysis['meff_min']:.2f}")
    print(f"   Collapse ratio: {role_analysis['collapse_ratio']:.2%}")
    print(f"   RFI: {role_analysis['rfi']:.3f}")
    print(f"\n   Interpretation:")
    print(f"   - {role_analysis['interpretation']['summary']}")
    print(f"   - {role_analysis['interpretation']['implication']}")
    print(f"   - Recommendation: {role_analysis['interpretation']['recommendation']}")
    
    # Feature importance
    print("\n4. Analyzing feature importance...")
    sample_play = analyzer.loader.prepare_play_state(input_df, plays[0][0], plays[0][1])
    feature_importance = analyzer.analyze_feature_importance(sample_play)
    
    if feature_importance.get('status') == 'computed' or 'top_features' in feature_importance:
        print(f"\n   Top features driving player movement:")
        for feat, score in zip(feature_importance['top_features'], feature_importance['collapse_scores']):
            print(f"   - {feat}: {score:.3f}")
        print(f"\n   {feature_importance['interpretation']}")
    
    # Save results
    output_dir = Path('results/nfl_analysis')
    output_dir.mkdir(parents=True, exist_ok=True)
    
    import json
    with open(output_dir / 'relational_analysis.json', 'w') as f:
        json.dump({
            'play_analyses': play_analyses,
            'role_analysis': role_analysis,
            'feature_importance': feature_importance
        }, f, indent=2)
    
    print(f"\n✓ Analysis complete! Results saved to {output_dir}/relational_analysis.json")
    
    print("\n" + "=" * 60)
    print("KEY INSIGHTS:")
    print("=" * 60)
    
    avg_collapse = np.mean([p['collapse_ratio'] for p in play_analyses])
    avg_rfi = np.mean([p['rfi'] for p in play_analyses])
    
    print(f"\n1. PLAY STRUCTURE:")
    print(f"   Average collapse ratio: {avg_collapse:.2%}")
    print(f"   Average RFI: {avg_rfi:.3f}")
    
    if avg_collapse < 0.3:
        print("   → Players move in LOW-dimensional subspace")
        print("   → Strong relational coupling detected")
        print("   → GNN/graph models will excel")
    elif avg_collapse < 0.6:
        print("   → MODERATE dimensional complexity")
        print("   → Mixed relational patterns")
        print("   → Ensemble approach recommended")
    else:
        print("   → HIGH-dimensional movement space")
        print("   → Weak relational coupling")
        print("   → Physics baseline may suffice")
    
    print(f"\n2. ROLE STRUCTURE:")
    print(f"   {role_analysis['interpretation']['summary']}")
    print(f"   → {role_analysis['interpretation']['recommendation']}")
    
    print(f"\n3. FEATURE DESIGN:")
    if 'dist_to_ball' in feature_importance.get('top_features', []):
        print("   ✓ Ball-relative features are PRIMARY")
    if 'speed_toward_ball' in feature_importance.get('top_features', []):
        print("   ✓ Velocity projections capture movement")
    if any('nearest' in f for f in feature_importance.get('top_features', [])):
        print("   ✓ Spatial clustering matters")
    
    print("\n" + "=" * 60)


if __name__ == '__main__':
    main()
