import os
import logging
import pathlib
import tempfile
import shutil

# import your setup_logging function
from logger import setup_logging  # <-- replace 'your_module' with the actual filename (no .py)

def run_test(log_level: str, with_file: bool):
    """Run a single logging test with given LOG_LEVEL and optional log file."""
    print(f"\n=== Test: LOG_LEVEL={log_level}, LOG_FILE={'set' if with_file else 'unset'} ===")

    # temp log file (if needed)
    tempdir = tempfile.mkdtemp()
    logfile = os.path.join(tempdir, "test.log") if with_file else None

    # configure environment
    os.environ["LOG_LEVEL"] = log_level
    if logfile:
        os.environ["LOG_FILE"] = logfile
    else:
        os.environ.pop("LOG_FILE", None)

    # set up logging
    setup_logging()
    logger = logging.getLogger("test_logger")

    # emit logs
    logger.debug("This is a DEBUG message")
    logger.info("This is an INFO message")
    logger.critical("This is a CRITICAL message")

    # check file contents if applicable
    if logfile:
        if pathlib.Path(logfile).exists():
            print(f"→ Log file created at: {logfile}")
            with open(logfile, "r", encoding="utf-8") as f:
                print("Contents:\n" + f.read())
        else:
            print("→ No log file was created")
    else:
        print("→ No log file expected")

    # cleanup
    shutil.rmtree(tempdir)


if __name__ == "__main__":
    # Run a matrix of tests
    for lvl in ["0", "1", "2"]:
        run_test(lvl, with_file=True)
        run_test(lvl, with_file=False)
