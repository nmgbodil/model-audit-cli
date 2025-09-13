# This is a dummy file to testing type checking. Delete at the start of development
import time


def create_model(url: str) -> str:
    """Dummy function to create huggingface model."""
    time.sleep(2)
    return "Model created"


if __name__ == "__main__":
    create_model("https://github.com/nmgbodil/model-audit-cli")
