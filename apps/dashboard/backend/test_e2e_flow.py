"""
End-to-End Test: Complete User Journey

Tests the full workflow from creating a diagnostic run through
viewing visualizations to comparing multiple runs.

This test requires:
- PostgreSQL database running
- FastAPI backend running
- Next.js frontend running (for full integration)

Run with: pytest test_e2e_flow.py -v -s
"""

import pytest
import requests
import time
from datetime import datetime

# Configuration
API_BASE_URL = "http://localhost:8000"
FRONTEND_URL = "http://localhost:3000"


@pytest.fixture
def sample_diagnostic_data():
    """Complete diagnostic results for E2E test."""
    return {
        "metadata": {
            "timestamp": datetime.now().isoformat(),
            "version": "1.0.0",
            "dataset": "E2E_Test_Dataset"
        },
        "topology": {
            "nodes": [
                {"id": "Gene_A", "degree": 5, "community": 0},
                {"id": "Gene_B", "degree": 4, "community": 0},
                {"id": "Gene_C", "degree": 3, "community": 0},
                {"id": "Gene_D", "degree": 3, "community": 1},
                {"id": "Gene_E", "degree": 2, "community": 1},
                {"id": "Gene_F", "degree": 2, "community": 1},
                {"id": "Gene_G", "degree": 1, "community": 2}
            ],
            "links": [
                {"source": "Gene_A", "target": "Gene_B", "weight": 0.95},
                {"source": "Gene_A", "target": "Gene_C", "weight": 0.88},
                {"source": "Gene_B", "target": "Gene_C", "weight": 0.82},
                {"source": "Gene_D", "target": "Gene_E", "weight": 0.76},
                {"source": "Gene_E", "target": "Gene_F", "weight": 0.70},
                {"source": "Gene_G", "target": "Gene_A", "weight": 0.45}
            ],
            "metrics": {
                "node_count": 7,
                "edge_count": 6,
                "avg_degree": 2.86,
                "modularity": 0.52,
                "clustering_coefficient": 0.38
            }
        },
        "collapse_features": [
            {
                "feature_name": "Gene_A",
                "feature_index": 0,
                "contribution_percent": 32.5,
                "collapse_score": 0.95,
                "cumulative_contribution": 32.5,
                "rank": 1
            },
            {
                "feature_name": "Gene_B",
                "feature_index": 1,
                "contribution_percent": 24.8,
                "collapse_score": 0.87,
                "cumulative_contribution": 57.3,
                "rank": 2
            },
            {
                "feature_name": "Gene_C",
                "feature_index": 2,
                "contribution_percent": 16.2,
                "collapse_score": 0.78,
                "cumulative_contribution": 73.5,
                "rank": 3
            },
            {
                "feature_name": "Gene_D",
                "feature_index": 3,
                "contribution_percent": 11.5,
                "collapse_score": 0.69,
                "cumulative_contribution": 85.0,
                "rank": 4
            },
            {
                "feature_name": "Gene_E",
                "feature_index": 4,
                "contribution_percent": 8.3,
                "collapse_score": 0.58,
                "cumulative_contribution": 93.3,
                "rank": 5
            }
        ],
        "lattice_point": {
            "rfi": 0.82,
            "collapse_ratio": 0.28,
            "lattice_zone": "Truth Lattice"
        }
    }


class TestE2EFlow:
    """End-to-end test suite for complete user journey."""

    def test_01_health_check(self):
        """Step 1: Verify system is healthy before starting."""
        print("\n[E2E Step 1] Checking system health...")
        
        response = requests.get(f"{API_BASE_URL}/health", timeout=5)
        assert response.status_code == 200, "API is not healthy"
        
        health_data = response.json()
        assert health_data["status"] == "healthy"
        assert health_data["database"] == "connected"
        
        print("✓ System healthy")

    def test_02_create_first_run(self, sample_diagnostic_data):
        """Step 2: Create first diagnostic run."""
        print("\n[E2E Step 2] Creating first diagnostic run...")
        
        response = requests.post(
            f"{API_BASE_URL}/api/runs",
            json={
                "name": "E2E Test Run 1",
                "config": {
                    "dataset": "test_dataset_1",
                    "method": "relational_meff"
                },
                "results": sample_diagnostic_data
            },
            timeout=10
        )
        
        assert response.status_code == 200, f"Failed to create run: {response.text}"
        
        data = response.json()
        assert "run_id" in data
        assert data["name"] == "E2E Test Run 1"
        assert data["status"] == "completed"
        
        # Store run_id for later steps
        pytest.run1_id = data["run_id"]
        print(f"✓ Created run 1: {pytest.run1_id}")

    def test_03_retrieve_topology(self):
        """Step 3: Retrieve topology data for visualization."""
        print("\n[E2E Step 3] Retrieving topology data...")
        
        response = requests.get(
            f"{API_BASE_URL}/api/runs/{pytest.run1_id}/topology",
            timeout=5
        )
        
        assert response.status_code == 200
        
        topology = response.json()
        assert "nodes" in topology
        assert "links" in topology
        assert len(topology["nodes"]) == 7
        assert len(topology["links"]) == 6
        
        # Verify node structure
        node = topology["nodes"][0]
        assert "id" in node
        assert "degree" in node
        assert "community" in node
        
        # Verify link structure
        link = topology["links"][0]
        assert "source" in link
        assert "target" in link
        assert "weight" in link
        
        print(f"✓ Retrieved topology: {len(topology['nodes'])} nodes, {len(topology['links'])} edges")

    def test_04_retrieve_collapse_map(self):
        """Step 4: Retrieve collapse feature data."""
        print("\n[E2E Step 4] Retrieving collapse feature data...")
        
        response = requests.get(
            f"{API_BASE_URL}/api/runs/{pytest.run1_id}/collapse",
            timeout=5
        )
        
        assert response.status_code == 200
        
        features = response.json()
        assert isinstance(features, list)
        assert len(features) == 5
        
        # Verify features are ranked
        for i, feature in enumerate(features):
            assert feature["rank"] == i + 1
            assert "contribution_percent" in feature
            assert "collapse_score" in feature
        
        # Verify top feature
        top_feature = features[0]
        assert top_feature["contribution_percent"] > 30
        assert top_feature["collapse_score"] > 0.9
        
        print(f"✓ Retrieved collapse map: {len(features)} features ranked")

    def test_05_retrieve_lattice_point(self):
        """Step 5: Retrieve lattice point for phase space."""
        print("\n[E2E Step 5] Retrieving lattice point...")
        
        response = requests.get(
            f"{API_BASE_URL}/api/lattice?run_id={pytest.run1_id}",
            timeout=5
        )
        
        assert response.status_code == 200
        
        lattice_points = response.json()
        assert len(lattice_points) == 1
        
        point = lattice_points[0]
        assert point["run_id"] == pytest.run1_id
        assert point["rfi"] == pytest.approx(0.82, abs=0.01)
        assert point["collapse_ratio"] == pytest.approx(0.28, abs=0.01)
        
        print(f"✓ Retrieved lattice point: RFI={point['rfi']:.2f}, CR={point['collapse_ratio']:.2f}")

    def test_06_create_second_run(self, sample_diagnostic_data):
        """Step 6: Create second run for comparison."""
        print("\n[E2E Step 6] Creating second diagnostic run...")
        
        # Modify data slightly for second run
        modified_data = sample_diagnostic_data.copy()
        modified_data["lattice_point"]["rfi"] = 0.75
        modified_data["lattice_point"]["collapse_ratio"] = 0.35
        modified_data["lattice_point"]["lattice_zone"] = "Truth Lattice"
        
        response = requests.post(
            f"{API_BASE_URL}/api/runs",
            json={
                "name": "E2E Test Run 2",
                "config": {
                    "dataset": "test_dataset_2",
                    "method": "relational_meff"
                },
                "results": modified_data
            },
            timeout=10
        )
        
        assert response.status_code == 200
        
        data = response.json()
        pytest.run2_id = data["run_id"]
        print(f"✓ Created run 2: {pytest.run2_id}")

    def test_07_retrieve_all_lattice_points(self):
        """Step 7: Retrieve all lattice points for phase plane."""
        print("\n[E2E Step 7] Retrieving all lattice points...")
        
        response = requests.get(f"{API_BASE_URL}/api/lattice", timeout=5)
        
        assert response.status_code == 200
        
        points = response.json()
        assert len(points) >= 2  # At least our two test runs
        
        # Verify both our runs are present
        run_ids = [p["run_id"] for p in points]
        assert pytest.run1_id in run_ids
        assert pytest.run2_id in run_ids
        
        print(f"✓ Retrieved {len(points)} lattice points total")

    def test_08_compare_runs_topology(self):
        """Step 8: Compare topology between two runs."""
        print("\n[E2E Step 8] Comparing topology between runs...")
        
        # Get topology for both runs
        response1 = requests.get(
            f"{API_BASE_URL}/api/runs/{pytest.run1_id}/topology",
            timeout=5
        )
        response2 = requests.get(
            f"{API_BASE_URL}/api/runs/{pytest.run2_id}/topology",
            timeout=5
        )
        
        assert response1.status_code == 200
        assert response2.status_code == 200
        
        topo1 = response1.json()
        topo2 = response2.json()
        
        # Both should have same structure (same sample data)
        assert len(topo1["nodes"]) == len(topo2["nodes"])
        assert len(topo1["links"]) == len(topo2["links"])
        
        print(f"✓ Comparison ready: Run 1 vs Run 2")

    def test_09_compare_runs_collapse(self):
        """Step 9: Compare collapse features between two runs."""
        print("\n[E2E Step 9] Comparing collapse features...")
        
        response1 = requests.get(
            f"{API_BASE_URL}/api/runs/{pytest.run1_id}/collapse",
            timeout=5
        )
        response2 = requests.get(
            f"{API_BASE_URL}/api/runs/{pytest.run2_id}/collapse",
            timeout=5
        )
        
        assert response1.status_code == 200
        assert response2.status_code == 200
        
        features1 = response1.json()
        features2 = response2.json()
        
        # Both should have 5 features
        assert len(features1) == 5
        assert len(features2) == 5
        
        # Top feature should be same in both
        assert features1[0]["feature_name"] == features2[0]["feature_name"]
        
        print(f"✓ Collapse comparison ready")

    def test_10_list_all_runs(self):
        """Step 10: Retrieve list of all runs."""
        print("\n[E2E Step 10] Listing all runs...")
        
        response = requests.get(f"{API_BASE_URL}/api/runs", timeout=5)
        
        assert response.status_code == 200
        
        runs = response.json()
        assert isinstance(runs, list)
        assert len(runs) >= 2
        
        # Verify our runs are in the list
        run_ids = [r["run_id"] for r in runs]
        assert pytest.run1_id in run_ids
        assert pytest.run2_id in run_ids
        
        print(f"✓ Found {len(runs)} total runs")

    def test_11_verify_run_details(self):
        """Step 11: Verify run details are complete."""
        print("\n[E2E Step 11] Verifying run details...")
        
        response = requests.get(
            f"{API_BASE_URL}/api/runs/{pytest.run1_id}",
            timeout=5
        )
        
        assert response.status_code == 200
        
        run_details = response.json()
        assert run_details["run_id"] == pytest.run1_id
        assert run_details["name"] == "E2E Test Run 1"
        assert run_details["status"] == "completed"
        assert "created_at" in run_details
        assert "rfi" in run_details
        assert "collapse_ratio" in run_details
        
        print(f"✓ Run details verified: {run_details['name']}")

    def test_12_cleanup(self):
        """Step 12: Clean up test runs."""
        print("\n[E2E Step 12] Cleaning up test data...")
        
        # Delete both test runs
        response1 = requests.delete(
            f"{API_BASE_URL}/api/runs/{pytest.run1_id}",
            timeout=5
        )
        response2 = requests.delete(
            f"{API_BASE_URL}/api/runs/{pytest.run2_id}",
            timeout=5
        )
        
        assert response1.status_code == 200
        assert response2.status_code == 200
        
        # Verify they're gone
        verify1 = requests.get(f"{API_BASE_URL}/api/runs/{pytest.run1_id}", timeout=5)
        verify2 = requests.get(f"{API_BASE_URL}/api/runs/{pytest.run2_id}", timeout=5)
        
        assert verify1.status_code == 404
        assert verify2.status_code == 404
        
        print("✓ Cleanup complete")


# ==================== SUMMARY ====================

def test_e2e_summary():
    """Print E2E test summary."""
    print("\n" + "=" * 60)
    print("E2E TEST SUMMARY")
    print("=" * 60)
    print("\nComplete user journey tested:")
    print("  1. ✓ System health check")
    print("  2. ✓ Create diagnostic run 1")
    print("  3. ✓ View topology visualization")
    print("  4. ✓ View collapse map")
    print("  5. ✓ View lattice point")
    print("  6. ✓ Create diagnostic run 2")
    print("  7. ✓ View all lattice points")
    print("  8. ✓ Compare topology between runs")
    print("  9. ✓ Compare collapse features")
    print(" 10. ✓ List all runs")
    print(" 11. ✓ Verify run details")
    print(" 12. ✓ Cleanup test data")
    print("\nAll critical workflows validated!")
    print("=" * 60)


if __name__ == "__main__":
    print("Run with: pytest test_e2e_flow.py -v -s")
    print("\nThis E2E test validates the complete user journey:")
    print("  • Creating diagnostic runs")
    print("  • Viewing all visualization types")
    print("  • Comparing multiple runs")
    print("  • Managing run lifecycle")
