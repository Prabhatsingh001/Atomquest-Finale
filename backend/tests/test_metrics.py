from fastapi.testclient import TestClient

def test_metrics_endpoint(client: TestClient):
    resp = client.get("/api/metrics")
    assert resp.status_code == 200
    content = resp.text
    
    # Check that our custom metrics appear in the output
    assert "atomquest_active_sessions" in content
    assert "atomquest_active_participants" in content
    assert "atomquest_websocket_connections" in content
    assert "atomquest_sessions_total" in content
    assert "atomquest_recordings_total" in content
    assert "atomquest_errors_total" in content
