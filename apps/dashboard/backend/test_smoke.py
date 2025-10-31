"""
Smoke tests for diagnostic dashboard API endpoints.

Tests basic functionality of all 11 API endpoints to ensure
the system is operational. These are integration tests that
require a running PostgreSQL database.

Run with: pytest test_smoke.py -v
"""

import pytest
from fastapi.testclient import TestClient
from datetime import datetime
import json
from main import app

client = TestClient(app)


# ==================== FIXTURES ====================

@pytest.fixture
def sample_diagnostic_results():
    """Sample diagnostic results for testing."""
    return {
        "metadata": {
            "timestamp": datetime.now().isoformat(),
            "version": "1.0.0"
        },
        "topology": {
            "nodes": [
                {"id": "A", "degree": 3, "community": 0},
                {"id": "B", "degree": 2, "community": 0},
                {"id": "C", "degree": 2, "community": 1}
            ],
            "links": [
                {"source": "A", "target": "B", "weight": 0.8},
                {"source": "B", "target": "C", "weight": 0.6}
            ],
            "metrics": {
                "node_count": 3,
                "edge_count": 2,
                "avg_degree": 2.33,
                "modularity": 0.45
            }
        },
        "collapse_features": [
            {
                "feature_name": "Feature_0",
                "feature_index": 0,
                "contribution_percent": 45.2,
                "collapse_score": 0.92,
                "cumulative_contribution": 45.2,
                "rank": 1
            },
            {
                "feature_name": "Feature_1",
                "feature_index": 1,
                "contribution_percent": 30.1,
                "collapse_score": 0.78,
                "cumulative_contribution": 75.3,
                "rank": 2
            }
        ],
        "lattice_point": {
            "rfi": 0.75,
            "collapse_ratio": 0.35,
            "lattice_zone": "Truth Lattice"
        }
    }


@pytest.fixture
def created_run_id(sample_diagnostic_results):
    """Fixture that creates a test run and returns its ID."""
    response = client.post(
        "/api/runs",
        json={
            "name": "Smoke Test Run",
            "config": {"test": True},
            "results": sample_diagnostic_results
        }
    )
    assert response.status_code == 200
    run_id = response.json()["run_id"]
    yield run_id
    # Cleanup: delete the test run
    client.delete(f"/api/runs/{run_id}")


# ==================== HEALTH CHECK ====================

def test_health_check():
    """Test GET /health endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "database" in data
    assert "version" in data


# ==================== RUN MANAGEMENT ====================

def test_list_runs_empty():
    """Test GET /api/runs when no runs exist (or returns list)."""
    response = client.get("/api/runs")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_create_run(sample_diagnostic_results):
    """Test POST /api/runs to create a new diagnostic run."""
    response = client.post(
        "/api/runs",
        json={
            "name": "Test Create Run",
            "config": {"param": "value"},
            "results": sample_diagnostic_results
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert "run_id" in data
    assert data["name"] == "Test Create Run"
    
    # Cleanup
    run_id = data["run_id"]
    client.delete(f"/api/runs/{run_id}")


def test_get_run_details(created_run_id):
    """Test GET /api/runs/{run_id} to retrieve run details."""
    response = client.get(f"/api/runs/{created_run_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["run_id"] == created_run_id
    assert data["name"] == "Smoke Test Run"
    assert data["status"] == "completed"


def test_get_run_not_found():
    """Test GET /api/runs/{run_id} with non-existent ID."""
    response = client.get("/api/runs/nonexistent-id-12345")
    assert response.status_code == 404


def test_delete_run():
    """Test DELETE /api/runs/{run_id}."""
    # Create a run to delete
    response = client.post(
        "/api/runs",
        json={
            "name": "Run to Delete",
            "config": {},
            "results": {
                "metadata": {"timestamp": datetime.now().isoformat()},
                "topology": {"nodes": [], "links": [], "metrics": {}},
                "collapse_features": [],
                "lattice_point": {"rfi": 0.5, "collapse_ratio": 0.5, "lattice_zone": "Unknown"}
            }
        }
    )
    run_id = response.json()["run_id"]
    
    # Delete it
    delete_response = client.delete(f"/api/runs/{run_id}")
    assert delete_response.status_code == 200
    
    # Verify it's gone
    get_response = client.get(f"/api/runs/{run_id}")
    assert get_response.status_code == 404


# ==================== DIAGNOSTIC RESULTS ====================

def test_get_results(created_run_id):
    """Test GET /api/runs/{run_id}/results."""
    response = client.get(f"/api/runs/{created_run_id}/results")
    assert response.status_code == 200
    data = response.json()
    assert "metadata" in data
    assert "topology" in data or "collapse_features" in data or "lattice_point" in data


def test_get_results_not_found():
    """Test GET /api/runs/{run_id}/results with non-existent ID."""
    response = client.get("/api/runs/nonexistent-id-12345/results")
    assert response.status_code == 404


# ==================== TOPOLOGY DATA ====================

def test_get_topology(created_run_id):
    """Test GET /api/runs/{run_id}/topology."""
    response = client.get(f"/api/runs/{created_run_id}/topology")
    assert response.status_code == 200
    data = response.json()
    assert "nodes" in data
    assert "links" in data
    assert isinstance(data["nodes"], list)
    assert isinstance(data["links"], list)


def test_get_topology_not_found():
    """Test GET /api/runs/{run_id}/topology with non-existent ID."""
    response = client.get("/api/runs/nonexistent-id-12345/topology")
    assert response.status_code == 404


# ==================== COLLAPSE FEATURES ====================

def test_get_collapse(created_run_id):
    """Test GET /api/runs/{run_id}/collapse."""
    response = client.get(f"/api/runs/{created_run_id}/collapse")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    if len(data) > 0:
        feature = data[0]
        assert "feature_name" in feature
        assert "contribution_percent" in feature
        assert "collapse_score" in feature


def test_get_collapse_not_found():
    """Test GET /api/runs/{run_id}/collapse with non-existent ID."""
    response = client.get("/api/runs/nonexistent-id-12345/collapse")
    assert response.status_code == 404


# ==================== LATTICE POINTS ====================

def test_get_lattice_all():
    """Test GET /api/lattice to retrieve all runs' lattice points."""
    response = client.get("/api/lattice")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


def test_get_lattice_single_run(created_run_id):
    """Test GET /api/lattice with run_id query parameter."""
    response = client.get(f"/api/lattice?run_id={created_run_id}")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    if len(data) > 0:
        point = data[0]
        assert "run_id" in point
        assert "rfi" in point
        assert "collapse_ratio" in point
        assert point["run_id"] == created_run_id


# ==================== DATA VALIDATION ====================

def test_topology_data_structure(created_run_id):
    """Test that topology data has correct structure."""
    response = client.get(f"/api/runs/{created_run_id}/topology")
    data = response.json()
    
    # Check nodes
    for node in data["nodes"]:
        assert "id" in node
        assert "degree" in node
        assert "community" in node
    
    # Check links
    for link in data["links"]:
        assert "source" in link
        assert "target" in link
        assert "weight" in link


def test_collapse_data_structure(created_run_id):
    """Test that collapse feature data has correct structure."""
    response = client.get(f"/api/runs/{created_run_id}/collapse")
    data = response.json()
    
    for feature in data:
        assert "feature_name" in feature
        assert "feature_index" in feature
        assert "contribution_percent" in feature
        assert "collapse_score" in feature
        assert "rank" in feature


def test_lattice_data_structure(created_run_id):
    """Test that lattice point data has correct structure."""
    response = client.get(f"/api/lattice?run_id={created_run_id}")
    data = response.json()
    
    assert len(data) > 0
    point = data[0]
    assert "run_id" in point
    assert "rfi" in point
    assert "collapse_ratio" in point
    assert 0 <= point["rfi"] <= 1
    assert 0 <= point["collapse_ratio"] <= 1


# ==================== ERROR HANDLING ====================

def test_create_run_invalid_data():
    """Test POST /api/runs with invalid data."""
    response = client.post(
        "/api/runs",
        json={"invalid": "data"}
    )
    # Should return 422 (validation error) or 400 (bad request)
    assert response.status_code in [400, 422]


def test_delete_nonexistent_run():
    """Test DELETE /api/runs/{run_id} with non-existent ID."""
    response = client.delete("/api/runs/nonexistent-id-12345")
    assert response.status_code == 404


# ==================== SUMMARY ====================

if __name__ == "__main__":
    print("Run with: pytest test_smoke.py -v")
    print("\nThis test suite covers:")
    print("  ✓ Health check endpoint")
    print("  ✓ Run management (list, create, get, delete)")
    print("  ✓ Diagnostic results retrieval")
    print("  ✓ Topology data endpoints")
    print("  ✓ Collapse feature endpoints")
    print("  ✓ Lattice point endpoints")
    print("  ✓ Data structure validation")
    print("  ✓ Error handling")
