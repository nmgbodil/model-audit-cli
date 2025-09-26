# Model-Audit-CLI

A lightweight CLI for managing and evaluating Hugging Face models: fetch metadata, run local checks, and compute metrics with reproducible outputs and CI-friendly reports.

## Dependency Management
---

To install all dependencies run the following command

```
pip install -e ".[dev]"
```
---
## Contributing & CI Requirements

Our CI runs on **Python 3.11 and 3.12** and enforces these gates. Please run them locally before pushing or opening a PR.

1) **Formatting (Black)**  
Check only (no edits):
```bash
black --check .
```
Auto-format:
```bash
black .
```

2) **Import Sorting (isort)**  
Check only:
```bash
isort --check-only --diff .
```
Auto-fix:
```bash
isort .
```

3) **Linting (Flake8 + Docstrings)**
```bash
flake8 .
```

4) **Type Checks (mypy)**
```bash
mypy
```

5) **Tests + Coverage (unit tests)**  
CI expects all tests to pass and **≥ 80%** code coverage over `src/`.

Optional HTML report (human-friendly):
```bash
pytest --cov=src --cov-report=html:tests/_htmlcov
# open tests/_htmlcov/index.html
```

---

## Pre-commit (recommended)

We use **pre-commit** so formatting/linting/type checks run automatically on commit.

**One-time setup:**
```bash
pip install -e ".[dev]"
pre-commit install
pre-commit run --all-files   # baseline the repo once
```

THe phase-1 `run` script that serves as the CLI entrypoint for the project.  
It currently supports three commands required by the specification:

 `./run install`  
  Installs project dependencies and exits with code 0 on success.

 `./run test`  
  Runs the pytest test suite, generates JUnit + coverage XML reports, and prints a summary
  of passed/failed test cases and code coverage percentage.

 `./run urls.txt`  
  Reads a list of URLs and evaluates each. For now, metrics return
  placeholder values, formatted as NDJSON lines. 

| **Metric**                  | **Operationalization** |
|------------------------------|-------------------------|
| **Size**                     | Check total size of model weight files (`pytorch_model.bin`, `tf_model.h5`, etc.) and map to device compatibility (Raspberry Pi, Jetson Nano, Desktop, AWS). Example: `<100MB` = good for Pi (score near 1), `>1GB` = poor (score near 0). **Justification**: Deployability depends on size. |
| **License**                  | Parse the model’s README for the “License” section (using Hugging Face API or raw repo files). Score = 1 if license is clear and compatible with LGPLv2.1, lower if unclear, 0 if incompatible/missing. **Justification**: License compatibility is a hard requirement for ACME. |
| **Ramp-Up Time**             | Count availability of README length, example code/notebooks, and Hugging Face “likes/stars” (API). More documentation/examples = higher score. **Calculation**: `0.4·(README content) + 0.35·(Examples/Notebooks) + 0.25·(HuggingFace Likes)`. **Justification**: The most important factors are README content and usable examples; HF likes serve as an additional signal of reliability. |
| **Bus Factor**               | From GitHub API (or Hugging Face metadata), measure number of distinct contributors + recency of commits. Score high if ≥3 active contributors, low if only 1. **Justification**: Reduces risk of abandonment. |
| **Available Dataset & Code** | Check if README links to dataset(s) and code repo. Score = 1 if both dataset + code are provided, 0.5 if one is missing, 0 if none. **Justification**: Reproducibility requires dataset + code. |
| **Dataset Quality**          | Pull the dataset card and `dataset_info.json`, then assign binary/graded subscores for: size/counts, features/schema, splits, example instance, license clarity, intended use and limitations, collection/annotation process, languages, citation, and maintainer/versioning. Also fetch `lastModified` from the HF API and compute a recency subscore `exp(-ln(2) * days_since/365)`. Finally, `dataset_quality = weighted sum of subscores`. |
| **Code Quality**             | Use flake8 and mypy on linked code repo (if Python). Score based on number of lint/type errors per 1,000 lines. Lower errors = higher score. **Justification**: Maintainability and reliability. |
| **Performance Claims**       | Check README for benchmarks/evaluations (keywords: accuracy, F1, BLEU, etc.). Score high if benchmark results are reported + linked to dataset. Score low if no claims or unverifiable claims. **Justification**: ACME wants evidence of performance. |
| **Net Score**                | Define NetScore as a weighted sum of all metrics, normalized to [0,1]. Example: `NetScore = 0.2·License + 0.15·RampUpTime + 0.15·BusFactor + 0.1·AvailableDatasetAndCode + 0.1·DatasetQuality + 0.1·CodeQuality + 0.1·PerformanceClaims + 0.1·Size`. Weights should reflect Sarah’s concerns (license clarity, ramp-up time, quality). |


## Contributors
* [Noddie Mgbodille](https://github.com/nmgbodil)
* [Will Ott](https://github.com/willott29)
* [Trevor Ju](https://github.com/teajuw)
* [Anna Stark](https://github.com/annastarky)
