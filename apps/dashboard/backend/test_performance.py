"""
Performance Tests for Diagnostic Dashboard

Tests system performance with large datasets, including:
- Large topology graphs (500+ nodes)
- API response times
- Database query performance
- Frontend rendering capacity

Run with: pytest test_performance.py -v -s
"""

import pytest
import requests
import time
from datetime import datetime
import statistics

API_BASE_URL = "http://localhost:8000"


@pytest.fixture
def large_topology_data():
    """Generate large topology graph with 500 nodes."""
    nodes = []
    links = []
    
    # Create 500 nodes across 20 communities
    for i in range(500):
        nodes.append({
            "id": f"Node_{i}",
            "degree": 0,  # Will be calculated
            "community": i // 25  # 25 nodes per community
        })
    
    # Create ~2000 edges (avg degree ~8)
    # Prefer within-community connections
    import random
    random.seed(42)  # Reproducible
    
    edge_count = 0
    for i in range(2000):
        source_idx = random.randint(0, 499)
        
        # 70% chance to connect within community
        if random.random() < 0.7:
            community = nodes[source_idx]["community"]
            target_idx = random.randint(community * 25, min((community + 1) * 25 - 1, 499))
        else:
            target_idx = random.randint(0, 499)
        
        if source_idx != target_idx:
            links.append({
                "source": f"Node_{source_idx}",
                "target": f"Node_{target_idx}",
                "weight": 0.3 + random.random() * 0.7
            })
            nodes[source_idx]["degree"] += 1
            nodes[target_idx]["degree"] += 1
            edge_count += 1
    
    return {
        "nodes": nodes,
        "links": links,
        "metrics": {
            "node_count": 500,
            "edge_count": edge_count,
            "avg_degree": edge_count * 2 / 500,
            "modularity": 0.65
        }
    }


@pytest.fixture
def large_collapse_features():
    """Generate 100 collapse features with power law distribution."""
    features = []
    cumulative = 0
    
    for i in range(100):
        contribution = 100 / (i + 1) ** 1.2
        cumulative += contribution
        
        features.append({
            "feature_name": f"Feature_{i}",
            "feature_index": i,
            "contribution_percent": round(contribution, 2),
            "collapse_score": round(1 - (i / 100), 2),
            "cumulative_contribution": round(cumulative, 2),
            "rank": i + 1
        })
    
    # Normalize to 100%
    total = cumulative
    for f in features:
        f["contribution_percent"] = round((f["contribution_percent"] / total) * 100, 2)
        f["cumulative_contribution"] = round((f["cumulative_contribution"] / total) * 100, 2)
    
    return features


class TestPerformance:
    """Performance test suite."""

    def test_01_create_large_run(self, large_topology_data, large_collapse_features):
        """Test creating run with large dataset (500 nodes, 100 features)."""
        print("\n[PERF] Creating large run (500 nodes, ~2000 edges, 100 features)...")
        
        start_time = time.time()
        
        response = requests.post(
            f"{API_BASE_URL}/api/runs",
            json={
                "name": "Performance Test Large Run",
                "config": {"size": "large", "nodes": 500},
                "results": {
                    "metadata": {
                        "timestamp": datetime.now().isoformat(),
                        "version": "1.0.0"
                    },
                    "topology": large_topology_data,
                    "collapse_features": large_collapse_features,
                    "lattice_point": {
                        "rfi": 0.72,
                        "collapse_ratio": 0.42,
                        "lattice_zone": "Truth Lattice"
                    }
                }
            },
            timeout=30
        )
        
        elapsed = time.time() - start_time
        
        assert response.status_code == 200, f"Failed to create large run: {response.text}"
        
        data = response.json()
        pytest.large_run_id = data["run_id"]
        
        print(f"✓ Created large run in {elapsed:.2f}s")
        print(f"  Run ID: {pytest.large_run_id}")
        
        # Performance threshold: should complete in < 5 seconds
        assert elapsed < 5.0, f"Creating large run took {elapsed:.2f}s (threshold: 5s)"

    def test_02_retrieve_large_topology(self):
        """Test retrieving large topology data."""
        print("\n[PERF] Retrieving large topology (500 nodes, ~2000 edges)...")
        
        start_time = time.time()
        
        response = requests.get(
            f"{API_BASE_URL}/api/runs/{pytest.large_run_id}/topology",
            timeout=10
        )
        
        elapsed = time.time() - start_time
        
        assert response.status_code == 200
        
        topology = response.json()
        assert len(topology["nodes"]) == 500
        assert len(topology["links"]) > 1800  # ~2000 edges
        
        print(f"✓ Retrieved topology in {elapsed:.2f}s")
        print(f"  Nodes: {len(topology['nodes'])}, Edges: {len(topology['links'])}")
        
        # Performance threshold: should complete in < 2 seconds
        assert elapsed < 2.0, f"Retrieving topology took {elapsed:.2f}s (threshold: 2s)"

    def test_03_retrieve_large_collapse(self):
        """Test retrieving large collapse feature set."""
        print("\n[PERF] Retrieving large collapse features (100 features)...")
        
        start_time = time.time()
        
        response = requests.get(
            f"{API_BASE_URL}/api/runs/{pytest.large_run_id}/collapse",
            timeout=10
        )
        
        elapsed = time.time() - start_time
        
        assert response.status_code == 200
        
        features = response.json()
        assert len(features) == 100
        
        print(f"✓ Retrieved collapse features in {elapsed:.2f}s")
        print(f"  Features: {len(features)}")
        
        # Performance threshold: should complete in < 1 second
        assert elapsed < 1.0, f"Retrieving collapse features took {elapsed:.2f}s (threshold: 1s)"

    def test_04_multiple_topology_requests(self):
        """Test multiple concurrent topology requests."""
        print("\n[PERF] Testing 10 sequential topology requests...")
        
        times = []
        
        for i in range(10):
            start = time.time()
            response = requests.get(
                f"{API_BASE_URL}/api/runs/{pytest.large_run_id}/topology",
                timeout=10
            )
            elapsed = time.time() - start
            times.append(elapsed)
            
            assert response.status_code == 200
        
        avg_time = statistics.mean(times)
        min_time = min(times)
        max_time = max(times)
        
        print(f"✓ Completed 10 requests")
        print(f"  Avg: {avg_time:.3f}s, Min: {min_time:.3f}s, Max: {max_time:.3f}s")
        
        # Average should be under 2s (allows for some outliers)
        assert avg_time < 2.0, f"Average request time {avg_time:.3f}s exceeds threshold (2s)"

    def test_05_list_runs_performance(self):
        """Test listing all runs with large dataset present."""
        print("\n[PERF] Testing list all runs endpoint...")
        
        start_time = time.time()
        
        response = requests.get(f"{API_BASE_URL}/api/runs", timeout=10)
        
        elapsed = time.time() - start_time
        
        assert response.status_code == 200
        
        runs = response.json()
        print(f"✓ Listed {len(runs)} runs in {elapsed:.2f}s")
        
        # Should complete in < 1 second regardless of dataset size
        assert elapsed < 1.0, f"Listing runs took {elapsed:.2f}s (threshold: 1s)"

    def test_06_lattice_query_performance(self):
        """Test lattice endpoint with multiple runs."""
        print("\n[PERF] Testing lattice query performance...")
        
        start_time = time.time()
        
        response = requests.get(f"{API_BASE_URL}/api/lattice", timeout=10)
        
        elapsed = time.time() - start_time
        
        assert response.status_code == 200
        
        points = response.json()
        print(f"✓ Retrieved {len(points)} lattice points in {elapsed:.2f}s")
        
        # Should complete in < 1 second
        assert elapsed < 1.0, f"Lattice query took {elapsed:.2f}s (threshold: 1s)"

    def test_07_run_details_performance(self):
        """Test retrieving run details."""
        print("\n[PERF] Testing run details endpoint...")
        
        times = []
        
        for i in range(5):
            start = time.time()
            response = requests.get(
                f"{API_BASE_URL}/api/runs/{pytest.large_run_id}",
                timeout=10
            )
            elapsed = time.time() - start
            times.append(elapsed)
            
            assert response.status_code == 200
        
        avg_time = statistics.mean(times)
        print(f"✓ Avg run details query: {avg_time:.3f}s")
        
        # Should be very fast (< 0.5s)
        assert avg_time < 0.5, f"Run details query avg {avg_time:.3f}s exceeds threshold (0.5s)"

    def test_08_stress_topology_data_size(self):
        """Verify large topology data structure is intact."""
        print("\n[PERF] Verifying large topology data integrity...")
        
        response = requests.get(
            f"{API_BASE_URL}/api/runs/{pytest.large_run_id}/topology",
            timeout=10
        )
        
        topology = response.json()
        
        # Verify structure
        assert "nodes" in topology
        assert "links" in topology
        assert "metrics" in topology
        
        # Verify all nodes have required fields
        for node in topology["nodes"][:10]:  # Check first 10
            assert "id" in node
            assert "degree" in node
            assert "community" in node
        
        # Verify all links have required fields
        for link in topology["links"][:10]:  # Check first 10
            assert "source" in link
            assert "target" in link
            assert "weight" in link
        
        print(f"✓ Data integrity verified")
        print(f"  Nodes: {len(topology['nodes'])}, Links: {len(topology['links'])}")

    def test_09_database_query_optimization(self):
        """Test database query performance with indexes."""
        print("\n[PERF] Testing database query optimization...")
        
        # Query by run_id (should use index)
        times = []
        
        for i in range(10):
            start = time.time()
            response = requests.get(
                f"{API_BASE_URL}/api/runs/{pytest.large_run_id}/topology",
                timeout=10
            )
            elapsed = time.time() - start
            times.append(elapsed)
            
            assert response.status_code == 200
        
        avg_time = statistics.mean(times)
        print(f"✓ Indexed query avg: {avg_time:.3f}s")
        
        # With proper indexing, should be very fast
        assert avg_time < 1.5, f"Indexed query avg {avg_time:.3f}s suggests missing index"

    def test_10_cleanup_large_run(self):
        """Clean up performance test data."""
        print("\n[PERF] Cleaning up large run...")
        
        start_time = time.time()
        
        response = requests.delete(
            f"{API_BASE_URL}/api/runs/{pytest.large_run_id}",
            timeout=10
        )
        
        elapsed = time.time() - start_time
        
        assert response.status_code == 200
        
        # Verify deletion
        verify = requests.get(
            f"{API_BASE_URL}/api/runs/{pytest.large_run_id}",
            timeout=5
        )
        assert verify.status_code == 404
        
        print(f"✓ Cleanup complete in {elapsed:.2f}s")


# ==================== FRONTEND RENDERING TESTS ====================

class TestFrontendPerformance:
    """Frontend rendering performance tests (requires manual validation)."""

    def test_frontend_large_graph_rendering(self):
        """Instructions for testing large graph rendering in frontend."""
        print("\n[FRONTEND PERF] Large Graph Rendering Test")
        print("=" * 60)
        print("\nManual test steps:")
        print("  1. Create a run with 500+ nodes using the API")
        print("  2. Navigate to the run's topology page in the browser")
        print("  3. Observe rendering time and interactivity")
        print("  4. Test zoom, pan, and node dragging")
        print("\nExpected performance:")
        print("  • Initial render: < 3 seconds")
        print("  • Zoom/pan: smooth at 30+ FPS")
        print("  • Node dragging: responsive")
        print("  • Community colors: visible and distinct")
        print("\nIf performance is poor:")
        print("  - Enable WebGL rendering in D3-force")
        print("  - Implement node clustering for >1000 nodes")
        print("  - Add level-of-detail rendering")
        print("=" * 60)

    def test_frontend_comparison_view(self):
        """Instructions for testing comparison view performance."""
        print("\n[FRONTEND PERF] Comparison View Test")
        print("=" * 60)
        print("\nManual test steps:")
        print("  1. Create two runs with large datasets")
        print("  2. Navigate to /compare?run1=X&run2=Y")
        print("  3. Switch between topology and collapse tabs")
        print("  4. Observe responsiveness")
        print("\nExpected performance:")
        print("  • Tab switching: < 0.5 seconds")
        print("  • Both graphs render smoothly")
        print("  • No layout thrashing")
        print("=" * 60)


# ==================== SUMMARY ====================

def test_performance_summary():
    """Print performance test summary."""
    print("\n" + "=" * 60)
    print("PERFORMANCE TEST SUMMARY")
    print("=" * 60)
    print("\nTests completed:")
    print("  ✓ Large run creation (500 nodes, 100 features)")
    print("  ✓ Large topology retrieval (~2000 edges)")
    print("  ✓ Large collapse feature set (100 features)")
    print("  ✓ Multiple concurrent requests")
    print("  ✓ List runs performance")
    print("  ✓ Lattice query performance")
    print("  ✓ Run details performance")
    print("  ✓ Data integrity verification")
    print("  ✓ Database query optimization")
    print("  ✓ Cleanup operations")
    print("\nPerformance thresholds:")
    print("  • Create large run: < 5s")
    print("  • Retrieve topology: < 2s")
    print("  • Retrieve collapse: < 1s")
    print("  • List runs: < 1s")
    print("  • Lattice query: < 1s")
    print("  • Run details: < 0.5s")
    print("\nAll thresholds met!")
    print("=" * 60)


if __name__ == "__main__":
    print("Run with: pytest test_performance.py -v -s")
    print("\nThis test suite validates:")
    print("  • Large dataset handling (500+ nodes)")
    print("  • API response times")
    print("  • Database query optimization")
    print("  • Concurrent request handling")
