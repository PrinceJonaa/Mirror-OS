#!/usr/bin/env python3
"""
NFL Player Movement Prediction - Relational Dynamics Engine
============================================================

Predicts player trajectories during pass plays using relational field theory.

Core Philosophy:
- Players don't move independently → they're coupled in a relational field
- Ball landing point creates an attractor that influences all movements
- Roles define relational constraints (Passer-Receiver-Coverage triangle)
- Movement = Physics + Role Pattern + Relational Coupling

Architecture:
1. Feature Engineering: Extract relational features from field state
2. Physics Baseline: Kinematic equations with ball attraction
3. ML Enhancement: Learn residuals from baseline with role-specific models
4. Ensemble: Combine physics + learned patterns

Evaluation: RMSE = sqrt(0.5 * (MSE_x + MSE_y))
"""

import numpy as np
import pandas as pd
from pathlib import Path
from typing import Tuple, Dict, List
from dataclasses import dataclass
import warnings
warnings.filterwarnings('ignore')


@dataclass
class PlayState:
    """Represents the state of a play at throw moment."""
    game_id: int
    play_id: int
    players: pd.DataFrame  # Player states at t=0
    ball_land_x: float
    ball_land_y: float
    play_direction: str
    n_frames_to_predict: Dict[int, int]  # nfl_id -> num_frames
    

class RelationalFeatureEngine:
    """
    Extracts relational features from field state.
    
    Features computed:
    - Ball-relative: distance, angle, speed toward ball
    - Spatial: player clustering, nearest teammates/opponents
    - Kinematic: velocity, acceleration projections
    - Role: embeddings and historical patterns
    """
    
    def __init__(self):
        self.role_encoder = {
            'Passer': 0,
            'Targeted Receiver': 1,
            'Defensive Coverage': 2,
            'Other Route Runner': 3
        }
        
    def extract_features(self, play_state: PlayState) -> pd.DataFrame:
        """Extract all relational features for a play."""
        df = play_state.players.copy()
        
        # 1. Ball-relative features
        df = self._add_ball_features(df, play_state.ball_land_x, play_state.ball_land_y)
        
        # 2. Velocity features
        df = self._add_velocity_features(df)
        
        # 3. Role encoding
        df['role_encoded'] = df['player_role'].map(self.role_encoder).fillna(3)
        
        # 4. Side encoding
        df['is_offense'] = (df['player_side'] == 'Offense').astype(int)
        
        # 5. Spatial features (player-player)
        df = self._add_spatial_features(df)
        
        return df
    
    def _add_ball_features(self, df: pd.DataFrame, ball_x: float, ball_y: float) -> pd.DataFrame:
        """Add features relative to ball landing point."""
        # Distance to ball
        dx = ball_x - df['x']
        dy = ball_y - df['y']
        df['dist_to_ball'] = np.sqrt(dx**2 + dy**2)
        
        # Angle to ball (radians)
        df['angle_to_ball'] = np.arctan2(dy, dx)
        
        # Speed toward ball (projection of velocity onto ball direction)
        vx = df['s'] * np.cos(np.radians(df['dir']))
        vy = df['s'] * np.sin(np.radians(df['dir']))
        df['speed_toward_ball'] = (vx * dx + vy * dy) / (df['dist_to_ball'] + 1e-6)
        
        # Acceleration toward ball
        ax = df['a'] * np.cos(np.radians(df['dir']))
        ay = df['a'] * np.sin(np.radians(df['dir']))
        df['accel_toward_ball'] = (ax * dx + ay * dy) / (df['dist_to_ball'] + 1e-6)
        
        # Alignment: how aligned is player's direction with ball direction?
        df['dir_alignment_ball'] = np.cos(df['angle_to_ball'] - np.radians(df['dir']))
        
        return df
    
    def _add_velocity_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add velocity/acceleration component features."""
        # Velocity components
        df['vx'] = df['s'] * np.cos(np.radians(df['dir']))
        df['vy'] = df['s'] * np.sin(np.radians(df['dir']))
        
        # Acceleration components
        df['ax'] = df['a'] * np.cos(np.radians(df['dir']))
        df['ay'] = df['a'] * np.sin(np.radians(df['dir']))
        
        # Angular features
        df['orientation_rad'] = np.radians(df['o'])
        df['direction_rad'] = np.radians(df['dir'])
        
        return df
    
    def _add_spatial_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add player-player spatial features."""
        positions = df[['x', 'y']].values
        
        # Compute pairwise distances
        n = len(df)
        if n > 1:
            # Distance matrix
            dist_matrix = np.sqrt(
                ((positions[:, None, :] - positions[None, :, :]) ** 2).sum(axis=2)
            )
            
            # Mask self (diagonal)
            np.fill_diagonal(dist_matrix, np.inf)
            
            # Nearest neighbor distance
            df['nearest_player_dist'] = dist_matrix.min(axis=1)
            
            # Average distance to k nearest (k=3 or all if fewer)
            k = min(3, n - 1)
            if k > 0:
                k_nearest = np.partition(dist_matrix, k-1, axis=1)[:, :k]
                df['avg_k_nearest_dist'] = k_nearest.mean(axis=1)
            else:
                df['avg_k_nearest_dist'] = 0
        else:
            df['nearest_player_dist'] = 0
            df['avg_k_nearest_dist'] = 0
        
        return df


class PhysicsBaseline:
    """
    Physics-based trajectory prediction with ball attraction.
    
    Model: x(t) = x0 + v0*t + 0.5*a*t^2 + attraction_to_ball
    
    Parameters tuned per role.
    """
    
    def __init__(self):
        # Role-specific attraction strengths (tunable)
        self.attraction_params = {
            'Passer': 0.01,  # Minimal attraction
            'Targeted Receiver': 0.5,  # Strong attraction
            'Defensive Coverage': 0.3,  # Moderate attraction
            'Other Route Runner': 0.2  # Weak attraction
        }
        
        # Maximum acceleration (m/s^2 -> yards/s^2, ~10m/s^2 = 10.9 yards/s^2)
        self.max_accel = 10.0
        
    def predict_trajectory(self, player_state: pd.Series, n_frames: int, 
                          ball_x: float, ball_y: float) -> np.ndarray:
        """
        Predict trajectory for single player.
        
        Returns: array of shape (n_frames, 2) with (x, y) positions
        """
        role = player_state['player_role']
        attraction = self.attraction_params.get(role, 0.2)
        
        # Initial state
        x0, y0 = player_state['x'], player_state['y']
        vx0, vy0 = player_state['vx'], player_state['vy']
        
        # Time step (10 frames per second)
        dt = 0.1
        
        trajectory = np.zeros((n_frames, 2))
        x, y = x0, y0
        vx, vy = vx0, vy0
        
        for t in range(n_frames):
            # Compute attraction force toward ball
            dx_ball = ball_x - x
            dy_ball = ball_y - y
            dist_ball = np.sqrt(dx_ball**2 + dy_ball**2) + 1e-6
            
            # Acceleration from attraction (proportional to distance, role-weighted)
            ax = attraction * dx_ball / dist_ball
            ay = attraction * dy_ball / dist_ball
            
            # Clip acceleration to realistic bounds
            a_mag = np.sqrt(ax**2 + ay**2)
            if a_mag > self.max_accel:
                ax = ax * self.max_accel / a_mag
                ay = ay * self.max_accel / a_mag
            
            # Update velocity
            vx += ax * dt
            vy += ay * dt
            
            # Clip speed (max ~12 yards/s)
            speed = np.sqrt(vx**2 + vy**2)
            max_speed = 12.0
            if speed > max_speed:
                vx = vx * max_speed / speed
                vy = vy * max_speed / speed
            
            # Update position
            x += vx * dt
            y += vy * dt
            
            # Clip to field bounds
            x = np.clip(x, 0, 120)
            y = np.clip(y, 0, 53.3)
            
            trajectory[t] = [x, y]
        
        return trajectory
    
    def predict_play(self, play_state: PlayState, features: pd.DataFrame) -> pd.DataFrame:
        """Predict all players for a play."""
        predictions = []
        
        for _, player in features.iterrows():
            nfl_id = player['nfl_id']
            n_frames = play_state.n_frames_to_predict.get(nfl_id, 0)
            
            if n_frames > 0:
                traj = self.predict_trajectory(
                    player, n_frames, 
                    play_state.ball_land_x, play_state.ball_land_y
                )
                
                for frame_idx in range(n_frames):
                    predictions.append({
                        'game_id': play_state.game_id,
                        'play_id': play_state.play_id,
                        'nfl_id': nfl_id,
                        'frame_id': frame_idx + 1,
                        'x': traj[frame_idx, 0],
                        'y': traj[frame_idx, 1]
                    })
        
        return pd.DataFrame(predictions)


class DataLoader:
    """Loads and prepares NFL tracking data."""
    
    def __init__(self, data_dir: Path):
        self.data_dir = data_dir
        self.train_dir = data_dir / 'train'
        
    def load_week(self, week: int) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """Load input and output data for a specific week."""
        input_file = self.train_dir / f'input_2023_w{week:02d}.csv'
        output_file = self.train_dir / f'output_2023_w{week:02d}.csv'
        
        input_df = pd.read_csv(input_file)
        output_df = pd.read_csv(output_file)
        
        return input_df, output_df
    
    def prepare_play_state(self, input_df: pd.DataFrame, 
                          game_id: int, play_id: int) -> PlayState:
        """Extract PlayState for a specific play."""
        play_data = input_df[
            (input_df['game_id'] == game_id) & 
            (input_df['play_id'] == play_id)
        ]
        
        # Get last frame for each player (state at throw moment)
        last_frames = play_data.groupby('nfl_id').last().reset_index()
        
        # Extract frame counts
        n_frames_dict = dict(zip(
            last_frames['nfl_id'], 
            last_frames['num_frames_output']
        ))
        
        return PlayState(
            game_id=game_id,
            play_id=play_id,
            players=last_frames,
            ball_land_x=last_frames['ball_land_x'].iloc[0],
            ball_land_y=last_frames['ball_land_y'].iloc[0],
            play_direction=last_frames['play_direction'].iloc[0],
            n_frames_to_predict=n_frames_dict
        )
    
    def get_all_plays(self, input_df: pd.DataFrame) -> List[Tuple[int, int]]:
        """Get list of (game_id, play_id) tuples."""
        return list(input_df[['game_id', 'play_id']].drop_duplicates().itertuples(index=False, name=None))


def compute_rmse(predictions: pd.DataFrame, ground_truth: pd.DataFrame) -> float:
    """
    Compute RMSE as per competition metric.
    
    RMSE = sqrt(0.5 * (MSE_x + MSE_y))
    """
    # Merge on play/player/frame
    merged = predictions.merge(
        ground_truth,
        on=['game_id', 'play_id', 'nfl_id', 'frame_id'],
        suffixes=('_pred', '_true')
    )
    
    if len(merged) == 0:
        return float('inf')
    
    mse_x = ((merged['x_pred'] - merged['x_true']) ** 2).mean()
    mse_y = ((merged['y_pred'] - merged['y_true']) ** 2).mean()
    
    rmse = np.sqrt(0.5 * (mse_x + mse_y))
    
    return rmse


def main():
    """Run baseline prediction on sample data."""
    print("🏈 NFL Player Movement Prediction - Relational Engine")
    print("=" * 60)
    
    # Setup
    data_dir = Path('data/nfl-big-data-bowl-2026-prediction')
    output_dir = Path('results/nfl_analysis')
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Load data
    print("\n1. Loading data (Week 1)...")
    loader = DataLoader(data_dir)
    input_df, output_df = loader.load_week(1)
    print(f"   Loaded {len(input_df)} input rows, {len(output_df)} output rows")
    
    # Get sample plays (first 10 for testing)
    plays = loader.get_all_plays(input_df)[:10]
    print(f"   Processing {len(plays)} sample plays")
    
    # Initialize components
    print("\n2. Initializing prediction engine...")
    feature_engine = RelationalFeatureEngine()
    physics_model = PhysicsBaseline()
    
    # Process plays
    print("\n3. Predicting trajectories...")
    all_predictions = []
    
    for i, (game_id, play_id) in enumerate(plays):
        # Prepare play state
        play_state = loader.prepare_play_state(input_df, game_id, play_id)
        
        # Extract features
        features = feature_engine.extract_features(play_state)
        
        # Predict with physics baseline
        predictions = physics_model.predict_play(play_state, features)
        all_predictions.append(predictions)
        
        if (i + 1) % 5 == 0:
            print(f"   Processed {i + 1}/{len(plays)} plays")
    
    # Combine predictions
    all_predictions_df = pd.concat(all_predictions, ignore_index=True)
    
    # Evaluate
    print("\n4. Evaluating predictions...")
    
    # Filter ground truth to match our predictions
    eval_keys = all_predictions_df[['game_id', 'play_id', 'nfl_id', 'frame_id']]
    ground_truth_filtered = output_df.merge(
        eval_keys,
        on=['game_id', 'play_id', 'nfl_id', 'frame_id']
    )
    
    rmse = compute_rmse(all_predictions_df, ground_truth_filtered)
    print(f"   Physics Baseline RMSE: {rmse:.4f} yards")
    
    # Save predictions
    output_file = output_dir / 'baseline_predictions_sample.csv'
    all_predictions_df.to_csv(output_file, index=False)
    print(f"\n✓ Predictions saved to {output_file}")
    
    # Save feature analysis
    sample_features = feature_engine.extract_features(
        loader.prepare_play_state(input_df, plays[0][0], plays[0][1])
    )
    feature_file = output_dir / 'sample_features.csv'
    sample_features.to_csv(feature_file, index=False)
    print(f"✓ Sample features saved to {feature_file}")
    
    print("\n" + "=" * 60)
    print("Next steps:")
    print("  1. Run full evaluation on all weeks")
    print("  2. Train ML model to learn residuals from physics baseline")
    print("  3. Implement GNN/Transformer for relational coupling")
    print("  4. Ensemble models for final submission")


if __name__ == '__main__':
    main()
