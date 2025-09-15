from model_audit_cli.evaluator import main


def test_smoke() -> None:
    """Dummy test."""
    main("urls.txt")
    assert 1 + 1 == 2
