import sys, json
from pathlib import Path
from src.metrics_engine import run_metrics, flatten_to_ndjson

def main(path: str) -> None:
    urls = Path(path).read_text().splitlines()
    for url in urls:
        if not url.strip() or url.startswith("#"):
            continue
        record = {"name": url, "category": "MODEL"}
        results = run_metrics({"url": url})
        record.update(flatten_to_ndjson(results))
        print(json.dumps(record))

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python -m src.evaluator <url_file>", file=sys.stderr)
        sys.exit(2)
    main(sys.argv[1])
