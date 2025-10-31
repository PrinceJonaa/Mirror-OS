#!/usr/bin/env python3
"""
NFL Advanced Model - GNN-Based Relational Predictor
===================================================

Graph Neural Network that models player-player and player-ball relationships.

Architecture:
1. Node features: Each player = node with (position, velocity, acceleration, role)
2. Edges: Spatial connectivity (k-NN) + role-based links
3. Global context: Ball landing point
4. Temporal decoder: Predicts trajectory autoregressively

Can be trained using research/training/training.py framework.
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
from torch_geometric.nn import GCNConv, global_mean_pool
from torch_geometric.data import Data, Batch
import numpy as np
import pandas as pd
from typing import List, Tuple
from dataclasses import dataclass


@dataclass
class GNNConfig:
    """Configuration for GNN model."""
    node_feature_dim: int = 32  # After embedding
    hidden_dim: int = 128
    num_gnn_layers: int = 3
    num_lstm_layers: int = 2
    output_frames: int = 25  # Max frames to predict
    k_neighbors: int = 5  # For spatial graph construction
    dropout: float = 0.1
    

class PlayerGraphBuilder:
    """Constructs graph representation of field state."""
    
    def __init__(self, k_neighbors: int = 5):
        self.k_neighbors = k_neighbors
        
    def build_graph(self, play_features: pd.DataFrame, 
                   ball_x: float, ball_y: float) -> Data:
        """
        Build PyTorch Geometric graph from play state.
        
        Returns:
            Data object with:
            - x: node features [num_players, feature_dim]
            - edge_index: edges [2, num_edges]
            - global_attr: [ball_x, ball_y]
            - y: target trajectories (if training)
        """
        # Node features
        feature_cols = [
            'x', 'y', 'vx', 'vy', 'ax', 'ay', 's', 'a',
            'dist_to_ball', 'angle_to_ball', 'speed_toward_ball',
            'dir_alignment_ball', 'role_encoded', 'is_offense'
        ]
        
        node_features = play_features[feature_cols].values.astype(np.float32)
        node_features = torch.from_numpy(node_features)
        
        # Build spatial edges (k-NN)
        positions = play_features[['x', 'y']].values
        edge_index = self._build_knn_edges(positions)
        
        # Global features (ball)
        global_attr = torch.tensor([ball_x, ball_y], dtype=torch.float32)
        
        # Create graph
        data = Data(
            x=node_features,
            edge_index=edge_index,
            global_attr=global_attr
        )
        
        return data
    
    def _build_knn_edges(self, positions: np.ndarray) -> torch.Tensor:
        """Build k-nearest neighbor edges."""
        n = len(positions)
        k = min(self.k_neighbors, n - 1)
        
        # Compute pairwise distances
        dist_matrix = np.sqrt(
            ((positions[:, None, :] - positions[None, :, :]) ** 2).sum(axis=2)
        )
        
        # For each node, find k nearest neighbors
        edges = []
        for i in range(n):
            # Set self distance to inf
            dist_matrix[i, i] = np.inf
            
            # Get k nearest
            nearest_k = np.argsort(dist_matrix[i])[:k]
            
            # Add edges (bidirectional)
            for j in nearest_k:
                edges.append([i, j])
                edges.append([j, i])
        
        if len(edges) == 0:
            # Fallback: fully connected if no edges
            edges = [[i, j] for i in range(n) for j in range(n) if i != j]
        
        edge_index = torch.tensor(edges, dtype=torch.long).t().contiguous()
        
        return edge_index


class GNNEncoder(nn.Module):
    """Graph Neural Network encoder for relational field."""
    
    def __init__(self, config: GNNConfig):
        super().__init__()
        self.config = config
        
        # Input projection
        self.input_proj = nn.Linear(14, config.node_feature_dim)  # 14 input features
        
        # GNN layers
        self.gnn_layers = nn.ModuleList([
            GCNConv(config.node_feature_dim if i == 0 else config.hidden_dim,
                   config.hidden_dim)
            for i in range(config.num_gnn_layers)
        ])
        
        # Global context integration
        self.global_proj = nn.Linear(2, config.hidden_dim)  # Ball features
        
        # Layer norms
        self.layer_norms = nn.ModuleList([
            nn.LayerNorm(config.hidden_dim)
            for _ in range(config.num_gnn_layers)
        ])
        
        self.dropout = nn.Dropout(config.dropout)
        
    def forward(self, x: torch.Tensor, edge_index: torch.Tensor, 
                global_attr: torch.Tensor, batch: torch.Tensor = None):
        """
        Args:
            x: node features [num_nodes, 14]
            edge_index: edges [2, num_edges]
            global_attr: global features [batch_size, 2] or [2]
            batch: batch assignment [num_nodes]
        
        Returns:
            node_embeddings: [num_nodes, hidden_dim]
        """
        # Project input features
        h = self.input_proj(x)
        
        # Apply GNN layers
        for i, (gnn, norm) in enumerate(zip(self.gnn_layers, self.layer_norms)):
            h_new = gnn(h, edge_index)
            h_new = norm(h_new)
            h_new = F.relu(h_new)
            h_new = self.dropout(h_new)
            
            # Residual connection (if dims match)
            if h.shape[-1] == h_new.shape[-1]:
                h = h + h_new
            else:
                h = h_new
        
        # Integrate global context (ball)
        if global_attr.dim() == 1:
            global_attr = global_attr.unsqueeze(0)
        
        global_emb = self.global_proj(global_attr)  # [batch_size, hidden_dim]
        
        # Broadcast global to all nodes
        if batch is not None:
            # Expand global based on batch assignment
            global_expanded = global_emb[batch]  # [num_nodes, hidden_dim]
        else:
            # Single graph
            global_expanded = global_emb.expand(h.shape[0], -1)
        
        # Combine node embeddings with global context
        h = h + global_expanded
        
        return h


class TrajectoryDecoder(nn.Module):
    """LSTM-based decoder for trajectory prediction."""
    
    def __init__(self, config: GNNConfig):
        super().__init__()
        self.config = config
        
        # LSTM for temporal modeling
        self.lstm = nn.LSTM(
            input_size=config.hidden_dim,
            hidden_size=config.hidden_dim,
            num_layers=config.num_lstm_layers,
            batch_first=True,
            dropout=config.dropout if config.num_lstm_layers > 1 else 0
        )
        
        # Output projection (x, y)
        self.output_proj = nn.Linear(config.hidden_dim, 2)
        
    def forward(self, node_embeddings: torch.Tensor, n_frames: int):
        """
        Args:
            node_embeddings: [num_nodes, hidden_dim]
            n_frames: number of frames to predict
        
        Returns:
            trajectories: [num_nodes, n_frames, 2]
        """
        batch_size = node_embeddings.shape[0]
        
        # Expand embeddings for sequence
        # Use embedding as initial hidden state
        h_init = node_embeddings.unsqueeze(0).repeat(self.config.num_lstm_layers, 1, 1)
        c_init = torch.zeros_like(h_init)
        
        # Autoregressive decoding
        trajectories = []
        hidden = (h_init, c_init)
        
        # Initial input (use node embedding)
        lstm_input = node_embeddings.unsqueeze(1)  # [batch, 1, hidden]
        
        for t in range(n_frames):
            # LSTM step
            lstm_out, hidden = self.lstm(lstm_input, hidden)
            
            # Project to (x, y)
            pos = self.output_proj(lstm_out.squeeze(1))  # [batch, 2]
            trajectories.append(pos)
            
            # Use output as next input (teacher forcing disabled for inference)
            lstm_input = lstm_out
        
        # Stack trajectories
        trajectories = torch.stack(trajectories, dim=1)  # [batch, n_frames, 2]
        
        return trajectories


class RelationalGNN(nn.Module):
    """Complete GNN model for player trajectory prediction."""
    
    def __init__(self, config: GNNConfig):
        super().__init__()
        self.config = config
        self.encoder = GNNEncoder(config)
        self.decoder = TrajectoryDecoder(config)
        
    def forward(self, data: Data, n_frames: int = None):
        """
        Args:
            data: PyTorch Geometric Data object
            n_frames: number of frames to predict (if None, use config default)
        
        Returns:
            trajectories: [num_nodes, n_frames, 2]
        """
        if n_frames is None:
            n_frames = self.config.output_frames
        
        # Encode graph
        node_embeddings = self.encoder(
            data.x, 
            data.edge_index, 
            data.global_attr,
            batch=data.batch if hasattr(data, 'batch') else None
        )
        
        # Decode trajectories
        trajectories = self.decoder(node_embeddings, n_frames)
        
        return trajectories


class TrainingDataset(torch.utils.data.Dataset):
    """Dataset for training GNN model."""
    
    def __init__(self, input_df: pd.DataFrame, output_df: pd.DataFrame,
                 feature_engine, graph_builder: PlayerGraphBuilder):
        self.input_df = input_df
        self.output_df = output_df
        self.feature_engine = feature_engine
        self.graph_builder = graph_builder
        
        # Get unique plays
        self.plays = list(input_df[['game_id', 'play_id']].drop_duplicates().itertuples(index=False, name=None))
        
    def __len__(self):
        return len(self.plays)
    
    def __getitem__(self, idx):
        game_id, play_id = self.plays[idx]
        
        # Get input data
        play_input = self.input_df[
            (self.input_df['game_id'] == game_id) & 
            (self.input_df['play_id'] == play_id)
        ]
        
        # Get last frame (state at throw)
        last_frames = play_input.groupby('nfl_id').last().reset_index()
        
        # Extract features
        features = self.feature_engine.extract_features_simple(last_frames)
        
        # Build graph
        ball_x = last_frames['ball_land_x'].iloc[0]
        ball_y = last_frames['ball_land_y'].iloc[0]
        graph = self.graph_builder.build_graph(features, ball_x, ball_y)
        
        # Get ground truth trajectories
        play_output = self.output_df[
            (self.output_df['game_id'] == game_id) & 
            (self.output_df['play_id'] == play_id)
        ]
        
        # Organize by player and frame
        trajectories = []
        for nfl_id in last_frames['nfl_id']:
            player_traj = play_output[play_output['nfl_id'] == nfl_id].sort_values('frame_id')
            traj_coords = player_traj[['x', 'y']].values
            
            # Pad to max length
            max_frames = 50  # Reasonable max
            if len(traj_coords) < max_frames:
                padding = np.zeros((max_frames - len(traj_coords), 2))
                traj_coords = np.vstack([traj_coords, padding])
            else:
                traj_coords = traj_coords[:max_frames]
            
            trajectories.append(traj_coords)
        
        graph.y = torch.from_numpy(np.array(trajectories)).float()
        graph.n_frames_actual = torch.tensor([
            len(play_output[play_output['nfl_id'] == nfl_id]) 
            for nfl_id in last_frames['nfl_id']
        ], dtype=torch.long)
        
        return graph


def train_model(model, train_loader, val_loader, config, device='cpu', epochs=10):
    """Training loop for GNN model."""
    model = model.to(device)
    optimizer = torch.optim.AdamW(model.parameters(), lr=1e-3, weight_decay=1e-5)
    scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(optimizer, epochs)
    
    best_val_loss = float('inf')
    
    for epoch in range(epochs):
        # Train
        model.train()
        train_loss = 0
        
        for batch in train_loader:
            batch = batch.to(device)
            optimizer.zero_grad()
            
            # Forward
            pred = model(batch, n_frames=batch.y.shape[1])
            
            # Loss (only on actual frames, not padding)
            loss = 0
            for i in range(len(batch.n_frames_actual)):
                n_frames = batch.n_frames_actual[i]
                loss += F.mse_loss(pred[i, :n_frames], batch.y[i, :n_frames])
            
            loss = loss / len(batch.n_frames_actual)
            
            # Backward
            loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
            optimizer.step()
            
            train_loss += loss.item()
        
        train_loss /= len(train_loader)
        
        # Validate
        model.eval()
        val_loss = 0
        
        with torch.no_grad():
            for batch in val_loader:
                batch = batch.to(device)
                pred = model(batch, n_frames=batch.y.shape[1])
                
                loss = 0
                for i in range(len(batch.n_frames_actual)):
                    n_frames = batch.n_frames_actual[i]
                    loss += F.mse_loss(pred[i, :n_frames], batch.y[i, :n_frames])
                
                loss = loss / len(batch.n_frames_actual)
                val_loss += loss.item()
        
        val_loss /= len(val_loader)
        
        # Scheduler
        scheduler.step()
        
        # Logging
        print(f"Epoch {epoch+1}/{epochs} - Train Loss: {train_loss:.4f}, Val Loss: {val_loss:.4f}")
        
        # Save best
        if val_loss < best_val_loss:
            best_val_loss = val_loss
            torch.save(model.state_dict(), 'results/nfl_analysis/best_gnn_model.pt')
            print(f"  → Saved best model (val_loss={val_loss:.4f})")
    
    return model


if __name__ == '__main__':
    print("🧠 Relational GNN Model - Architecture Definition")
    print("=" * 60)
    print("\nModel components:")
    print("  ✓ PlayerGraphBuilder: Converts field state to graph")
    print("  ✓ GNNEncoder: Learns relational embeddings")
    print("  ✓ TrajectoryDecoder: Predicts movement sequences")
    print("  ✓ RelationalGNN: End-to-end model")
    print("\nTo train:")
    print("  python nfl_train_gnn.py")
    print("\nFor advanced training with research/training/training.py:")
    print("  - Import RelationalGNN")
    print("  - Use TrainingDataset")
    print("  - Apply advanced techniques from training.py")
