"""Pytest configuration and fixtures."""
import pytest


@pytest.fixture
def mock_cli_response():
    """Provide a mock CLI response for testing."""
    return "Hello from the mock CLI!"
