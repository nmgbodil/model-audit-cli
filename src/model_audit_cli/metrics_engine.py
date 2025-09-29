import os
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Any, Dict

from model_audit_cli.log import logger
from model_audit_cli.metrics.net_score import NetScore
from model_audit_cli.models import Model

from .metrics.base_metric import Metric
from .metrics.registry import ALL_METRICS

FORCE_SEQUENTIAL = os.environ.get("FORCE_SEQUENTIAL") == "1"


def _safe_run(metric: Metric, model: Model) -> Metric:
    start = time.perf_counter()
    try:
        logger.info(f"Computing metric: {metric.name}")
        metric.compute(model)
        logger.debug(f"Finished metric {metric.name} with value={metric.value}")
        return metric
    except Exception as e:
        metric.value = 0.0
        metric.latency_ms = int((time.perf_counter() - start) * 1000.0)
        metric.details = {"error": str(e)}
        logger.error(f"Error computing {metric.name}: {e}")
        return metric


def compute_all_metrics(
    model: Model, include: set[str] | None = None
) -> dict[str, Metric]:
    """Compute all metrics for the given model."""
    logger.info(
        "Starting metric computation for model: "
        f"{getattr(model.model, 'url', 'unknown')}"
    )
    results: dict[str, Metric] = {}
    metrics = [m for m in ALL_METRICS if include is None or m.name in include]

    if FORCE_SEQUENTIAL:
        for metric in metrics:
            results[metric.name] = _safe_run(metric, model)
    else:
        with ThreadPoolExecutor() as executor:
            futures = {
                executor.submit(_safe_run, metric, model): metric.name
                for metric in metrics
            }
            for future in as_completed(futures):
                metric = future.result()  # already Metric, no cast needed
                results[metric.name] = metric

    logger.info(
        "Finished metric computation for model: "
        f"{getattr(model.model, 'url', 'unknown')}"
    )
    return results


def flatten_to_ndjson(results: Dict[str, Metric]) -> Dict[str, Any]:
    """Convert Metric objects into NDJSON-style flat dict."""
    logger.info("Flattening results to NDJSON")
    start = time.perf_counter()

    net_score = NetScore()
    net_score.evaluate(list(results.values()))
    results[net_score.name] = net_score

    out: Dict[str, Any] = {}
    for metric in results.values():
        out[metric.name] = metric.value
        out[f"{metric.name}_latency"] = int(round(metric.latency_ms))

    logger.debug(f"NDJSON flattened output: {out}")
    logger.info(f"Flattening complete in {int((time.perf_counter() - start) * 1000)}ms")
    return out
