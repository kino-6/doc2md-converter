"""Pytest configuration and shared fixtures."""

import pytest
from hypothesis import settings, Verbosity

# Configure Hypothesis
settings.register_profile("default", max_examples=100, deadline=None)
settings.register_profile("ci", max_examples=1000, deadline=None)
settings.register_profile("dev", max_examples=10, verbosity=Verbosity.verbose)
settings.load_profile("default")


@pytest.fixture
def temp_dir(tmp_path):
    """Provide a temporary directory for test files."""
    return tmp_path
