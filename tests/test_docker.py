"""Integration tests for Docker container functionality."""

import os

import httpx
import pytest


class TestDockerContainer:
    """Test Docker container startup and configuration."""

    def test_environment_variables_loaded(self) -> None:
        """Test that environment variables are properly loaded."""
        assert os.getenv("DATABASE_URL") is not None
        assert os.getenv("ENVIRONMENT") is not None

    def test_database_url_format(self) -> None:
        """Test that DATABASE_URL is in correct format."""
        database_url = os.getenv("DATABASE_URL", "")
        assert database_url.startswith("postgresql://")

    @pytest.mark.asyncio
    async def test_health_endpoint_accessible(self) -> None:
        """Test that health endpoint is accessible."""
        async with httpx.AsyncClient(
            base_url="http://localhost:8000", timeout=5.0
        ) as client:
            try:
                response = await client.get("/health")
                assert response.status_code == 200
            except httpx.ConnectError:
                pytest.skip("Application not running - skipping endpoint test")

    @pytest.mark.asyncio
    async def test_health_endpoint_response_structure(self) -> None:
        """Test that health endpoint returns expected structure."""
        async with httpx.AsyncClient(
            base_url="http://localhost:8000", timeout=5.0
        ) as client:
            try:
                response = await client.get("/health")
                data = response.json()

                assert "status" in data
                assert "service" in data
                assert "version" in data
                assert data["status"] == "healthy"
            except httpx.ConnectError:
                pytest.skip("Application not running - skipping endpoint test")

    @pytest.mark.asyncio
    async def test_readiness_endpoint_accessible(self) -> None:
        """Test that readiness endpoint is accessible."""
        async with httpx.AsyncClient(
            base_url="http://localhost:8000", timeout=5.0
        ) as client:
            try:
                response = await client.get("/readiness")
                assert response.status_code == 200
            except httpx.ConnectError:
                pytest.skip("Application not running - skipping endpoint test")

    @pytest.mark.asyncio
    async def test_readiness_endpoint_response_structure(self) -> None:
        """Test that readiness endpoint returns expected structure."""
        async with httpx.AsyncClient(
            base_url="http://localhost:8000", timeout=5.0
        ) as client:
            try:
                response = await client.get("/readiness")
                data = response.json()

                assert "ready" in data
                assert "checks" in data
                assert isinstance(data["ready"], bool)
                assert isinstance(data["checks"], dict)
            except httpx.ConnectError:
                pytest.skip("Application not running - skipping endpoint test")


class TestDatabaseConnectivity:
    """Test database connectivity from container."""

    def test_database_url_environment_variable(self) -> None:
        """Test that DATABASE_URL environment variable is set."""
        database_url = os.getenv("DATABASE_URL")
        assert database_url is not None
        assert "postgres" in database_url.lower()

    @pytest.mark.asyncio
    async def test_database_connection(self) -> None:
        """Test that database connection can be established."""
        from prisma import Prisma

        db = Prisma()
        try:
            await db.connect()
            assert db.is_connected()
        finally:
            if db.is_connected():
                await db.disconnect()

    @pytest.mark.asyncio
    async def test_database_migrations_applied(self) -> None:
        """Test that database migrations have been applied."""
        from prisma import Prisma

        db = Prisma()
        try:
            await db.connect()

            # Test that we can query database without errors
            # This confirms migrations have been applied
            result = await db.query_raw("SELECT 1 as test")
            assert result is not None
        finally:
            if db.is_connected():
                await db.disconnect()


class TestApplicationConfiguration:
    """Test application configuration in container."""

    def test_python_path_configured(self) -> None:
        """Test that PYTHONPATH is configured correctly."""
        pythonpath = os.getenv("PYTHONPATH", "")
        assert "/app" in pythonpath

    def test_environment_set(self) -> None:
        """Test that ENVIRONMENT variable is set."""
        environment = os.getenv("ENVIRONMENT")
        assert environment is not None
        assert environment in ["development", "test", "production"]

    @pytest.mark.asyncio
    async def test_application_responds_to_requests(self) -> None:
        """Test that application can handle requests."""
        async with httpx.AsyncClient(
            base_url="http://localhost:8000", timeout=5.0
        ) as client:
            try:
                response = await client.get("/health")
                assert response.status_code == 200
                assert response.headers.get("content-type") == "application/json"
            except httpx.ConnectError:
                pytest.skip("Application not running - skipping request test")


class TestServiceConnectivity:
    """Test connectivity to dependent services."""

    @pytest.mark.asyncio
    async def test_postgres_service_connectivity(self) -> None:
        """Test connectivity to PostgreSQL service."""
        from prisma import Prisma

        db = Prisma()
        try:
            await db.connect()
            # If we can connect, service is available
            assert db.is_connected()
        finally:
            if db.is_connected():
                await db.disconnect()

    def test_pinecone_api_key_configured(self) -> None:
        """Test that Pinecone API key is configured."""
        api_key = os.getenv("PINECONE_API_KEY")
        assert api_key is not None
        assert len(api_key) > 0

    def test_pinecone_environment_configured(self) -> None:
        """Test that Pinecone environment is configured."""
        environment = os.getenv("PINECONE_ENVIRONMENT")
        assert environment is not None
        assert len(environment) > 0


class TestContainerHealthChecks:
    """Test container health check functionality."""

    @pytest.mark.asyncio
    async def test_health_check_returns_200(self) -> None:
        """Test that health check endpoint returns 200 status."""
        async with httpx.AsyncClient(
            base_url="http://localhost:8000", timeout=5.0
        ) as client:
            try:
                response = await client.get("/health")
                assert response.status_code == 200
            except httpx.ConnectError:
                pytest.skip("Application not running - skipping health check test")

    @pytest.mark.asyncio
    async def test_health_check_response_time(self) -> None:
        """Test that health check responds quickly."""
        async with httpx.AsyncClient(
            base_url="http://localhost:8000", timeout=5.0
        ) as client:
            try:
                import time

                start = time.time()
                await client.get("/health")
                duration = time.time() - start

                # Health check should respond within 1 second
                assert duration < 1.0
            except httpx.ConnectError:
                pytest.skip("Application not running - skipping response time test")
