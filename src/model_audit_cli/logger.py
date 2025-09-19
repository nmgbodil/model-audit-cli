import logging, os, pathlib, sys
_LEVEL_MAP = { "0": logging.CRITICAL+1, "1": logging.INFO, "2": logging.DEBUG }

def setup_logging() -> None:
    path = os.environ.get("LOG_FILE")
    level = _LEVEL_MAP.get(os.environ.get("LOG_LEVEL", "0"), logging.CRITICAL+1)

    # silent by default
    logging.getLogger().handlers.clear()
    logging.getLogger().setLevel(level)

    if path and level <= logging.DEBUG:  # write only if a file is set and not silent
        pathlib.Path(path).parent.mkdir(parents=True, exist_ok=True)
        fh = logging.FileHandler(path, encoding="utf-8")
        fh.setLevel(level)
        fh.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(name)s: %(message)s"))
        logging.getLogger().addHandler(fh)
