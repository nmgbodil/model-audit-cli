# This is a dummy test file for testing the netscore worker
import time

import pytest

from model_audit_cli.dummy import create_model


@pytest.mark.unit
class TestNetscore:
    """Testing class for the netscore worker."""

    def test_dummy(self) -> None:
        """Dummy test."""
        time.sleep(2)
        assert 1 == 1


@pytest.mark.unit
def test_create_model() -> None:
    """Dummy test for create_model() function."""
    assert create_model("") == "Model created"
