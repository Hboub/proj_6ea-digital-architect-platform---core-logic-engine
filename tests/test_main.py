"""
Unit tests for FastAPI application and health endpoints.
"""

import pytest
from fastapi.testclient import TestClient

from src.main import app


@pytest.fixture
def client() -> TestClient:
    """Create a test client for the FastAPI application."""
    return TestClient(app)


class TestApplicationCreation:
    """Test FastAPI application creation and configuration."""

    def test_app_exists(self) -> None:
        """Test that the FastAPI app is created."""
        assert app is not None
        assert app.title == "Digital Architect Platform - Core Logic Engine"

    def test_app_version(self) -> None:
        """Test that the app has the correct version."""
        assert app.version == "0.1.0"

    def test_app_has_routes(self) -> None:
        """Test that the app has registered routes."""
        routes = [route.path for route in app.routes]
        assert "/health" in routes
        assert "/ready" in routes


class TestHealthEndpoint:
    """Test health check endpoint."""

    def test_health_endpoint_returns_200(self, client: TestClient) -> None:
        """Test that health endpoint returns 200 status code."""
        response = client.get("/health")
        assert response.status_code == 200

    def test_health_endpoint_response_structure(
        self, client: TestClient
    ) -> None:
        """Test that health endpoint returns correct response structure."""
        response = client.get("/health")
        data = response.json()

        assert "status" in data
        assert "timestamp" in data
        assert "service" in data
        assert "version" in data

    def test_health_endpoint_status_value(self, client: TestClient) -> None:
        """Test that health endpoint returns healthy status."""
        response = client.get("/health")
        data = response.json()

        assert data["status"] == "healthy"

    def test_health_endpoint_service_name(self, client: TestClient) -> None:
        """Test that health endpoint returns correct service name."""
        response = client.get("/health")
        data = response.json()

        assert (
            data["service"]
            == "Digital Architect Platform - Core Logic Engine"
        )

    def test_health_endpoint_version(self, client: TestClient) -> None:
        """Test that health endpoint returns correct version."""
        response = client.get("/health")
        data = response.json()

        assert data["version"] == "0.1.0"


class TestReadinessEndpoint:
    """Test readiness check endpoint."""

    def test_readiness_endpoint_returns_200(self, client: TestClient) -> None:
        """Test that readiness endpoint returns 200 status code."""
        response = client.get("/ready")
        assert response.status_code == 200

    def test_readiness_endpoint_response_structure(
        self, client: TestClient
    ) -> None:
        """Test that readiness endpoint returns correct response structure."""
        response = client.get("/ready")
        data = response.json()

        assert "ready" in data
        assert "timestamp" in data
        assert "checks" in data

    def test_readiness_endpoint_ready_value(
        self, client: TestClient
    ) -> None:
        """Test that readiness endpoint returns ready status."""
        response = client.get("/ready")
        data = response.json()

        assert isinstance(data["ready"], bool)

    def test_readiness_endpoint_checks(self, client: TestClient) -> None:
        """Test that readiness endpoint includes dependency checks."""
        response = client.get("/ready")
        data = response.json()

        assert "checks" in data
        assert isinstance(data["checks"], dict)
        assert "database" in data["checks"]
        assert "vector_db" in data["checks"]


class TestMiddleware:
    """Test custom middleware functionality."""

    def test_request_id_header_present(self, client: TestClient) -> None:
        """Test that response includes X-Request-ID header."""
        response = client.get("/health")
        assert "X-Request-ID" in response.headers
        assert response.headers["X-Request-ID"]

    def test_process_time_header_present(self, client: TestClient) -> None:
        """Test that response includes X-Process-Time header."""
        response = client.get("/health")
        assert "X-Process-Time" in response.headers
        assert response.headers["X-Process-Time"]

    def test_process_time_is_numeric(self, client: TestClient) -> None:
        """Test that process time header contains numeric value."""
        response = client.get("/health")
        process_time = response.headers["X-Process-Time"]
        assert float(process_time) >= 0

    def test_cors_headers_present(self, client: TestClient) -> None:
        """Test that CORS headers are present in response."""
        response = client.options("/health")
        assert "access-control-allow-origin" in response.headers


class TestErrorHandling:
    """Test error handling middleware."""

    def test_404_for_unknown_route(self, client: TestClient) -> None:
        """Test that unknown routes return 404."""
        response = client.get("/unknown-route")
        assert response.status_code == 404

    def test_405_for_wrong_method(self, client: TestClient) -> None:
        """Test that wrong HTTP method returns 405."""
        response = client.post("/health")
        assert response.status_code == 405


class TestAsyncBehavior:
    """Test async endpoint behavior."""

    @pytest.mark.asyncio
    async def test_health_endpoint_is_async(self) -> None:
        """Test that health endpoint works with async client."""
        from httpx import AsyncClient

        async with AsyncClient(app=app, base_url="http://test") as ac:
            response = await ac.get("/health")
            assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_readiness_endpoint_is_async(self) -> None:
        """Test that readiness endpoint works with async client."""
        from httpx import AsyncClient

        async with AsyncClient(app=app, base_url="http://test") as ac:
            response = await ac.get("/ready")
            assert response.status_code == 200
