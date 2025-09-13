# This is a dummy test file for testing the netscore worker
import time

from model_audit_cli.dummy import create_model


class TestNetscore:
    """Testing class for the netscore worker."""

    def test_dummy(self) -> None:
        """Dummy test."""
        time.sleep(2)
        assert 1 == 1


def test_create_model() -> None:
    """Dummy test for create_model() function."""
    assert create_model("") == "Model created"
