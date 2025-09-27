from typing import Optional

from pydantic import BaseModel

from model_audit_cli.resources.code_resource import CodeResource
from model_audit_cli.resources.dataset_resource import DatasetResource
from model_audit_cli.resources.model_resource import ModelResource


class Model(BaseModel):
    """Represents a machine learning model with associated dataset and code resources.

    Attributes:
        model (ModelResource): The model resource containing model-specific information.
        dataset (Optional[DatasetResource]): The dataset resource associated with model.
        code (Optional[CodeResource]): The code resource associated with the model.
    """

    model: ModelResource
    dataset: Optional[DatasetResource] = None
    code: Optional[CodeResource] = None
