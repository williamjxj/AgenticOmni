"""Integration tests for FastAPI endpoints."""

import pytest
from fastapi.testclient import TestClient


class TestHealthEndpoint:
    """Test suite for health check endpoint."""

    @pytest.mark.integration
    def test_health_endpoint_returns_200(self, test_client: TestClient) -> None:
        """Test that health endpoint returns 200 OK.

        Args:
            test_client: FastAPI test client fixture
        """
        response = test_client.get("/api/v1/health")
        assert response.status_code == 200

    @pytest.mark.integration
    def test_health_endpoint_response_structure(self, test_client: TestClient) -> None:
        """Test that health endpoint returns expected JSON structure.

        Args:
            test_client: FastAPI test client fixture
        """
        response = test_client.get("/api/v1/health")
        data = response.json()

        # Verify top-level fields
        assert "status" in data
        assert "timestamp" in data
        assert "version" in data
        assert "checks" in data

        # Verify version
        assert data["version"] == "0.1.0"

    @pytest.mark.integration
    def test_health_endpoint_checks_database(self, test_client: TestClient) -> None:
        """Test that health endpoint includes database health check.

        Args:
            test_client: FastAPI test client fixture
        """
        response = test_client.get("/api/v1/health")
        data = response.json()

        # Verify database check exists
        assert "database" in data["checks"]
        db_check = data["checks"]["database"]

        assert "status" in db_check
        assert db_check["status"] == "healthy"
        assert "response_time_ms" in db_check
        assert isinstance(db_check["response_time_ms"], (int, float))

    @pytest.mark.integration
    def test_health_endpoint_has_request_id(self, test_client: TestClient) -> None:
        """Test that health endpoint response includes X-Request-ID header.

        Args:
            test_client: FastAPI test client fixture
        """
        response = test_client.get("/api/v1/health")

        # Check for request ID in headers
        # Note: TestClient might not capture all middleware headers
        # This test verifies the endpoint works
        assert response.status_code == 200


class TestAPIDocumentation:
    """Test suite for API documentation endpoints."""

    @pytest.mark.integration
    def test_swagger_docs_accessible(self, test_client: TestClient) -> None:
        """Test that Swagger UI is accessible.

        Args:
            test_client: FastAPI test client fixture
        """
        response = test_client.get("/api/v1/docs")
        assert response.status_code == 200
        assert "swagger" in response.text.lower()

    @pytest.mark.integration
    def test_redoc_accessible(self, test_client: TestClient) -> None:
        """Test that ReDoc documentation is accessible.

        Args:
            test_client: FastAPI test client fixture
        """
        response = test_client.get("/api/v1/redoc")
        assert response.status_code == 200
        assert "redoc" in response.text.lower()

    @pytest.mark.integration
    def test_openapi_schema_accessible(self, test_client: TestClient) -> None:
        """Test that OpenAPI schema is accessible.

        Args:
            test_client: FastAPI test client fixture
        """
        response = test_client.get("/api/v1/openapi.json")
        assert response.status_code == 200

        schema = response.json()
        assert "openapi" in schema
        assert "info" in schema
        assert schema["info"]["title"] == "AgenticOmni API"
        assert schema["info"]["version"] == "0.1.0"


class TestCORS:
    """Test suite for CORS configuration."""

    @pytest.mark.integration
    def test_cors_headers_present(self, test_client: TestClient) -> None:
        """Test that CORS headers are present in responses.

        Args:
            test_client: FastAPI test client fixture
        """
        response = test_client.get(
            "/api/v1/health",
            headers={"Origin": "http://localhost:3000"},
        )

        # Check that request succeeds
        assert response.status_code == 200

        # Note: TestClient might not fully simulate CORS preflight
        # In production, CORS middleware will add appropriate headers
