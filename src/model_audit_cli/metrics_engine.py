from typing import Any, Optional


def run_metrics(
    context: dict[str, Any], include: Optional[list[str]] = None
) -> dict[str, Any]:
    """Dummy metrics calculator."""
    result = {
        **{name: 1.0 for name in (include or ["ramp_up_time", "bus_factor"])},
        **context,
    }
    return result


def flatten_to_ndjson(results: dict[str, Any]) -> dict[str, Any]:
    """Dummy flatten to ndjson format."""
    return {name: val for name, val in results.items()}
