from typing import Optional

from pydantic import BaseModel

from model_audit_cli.resources.code_resource import CodeResource
from model_audit_cli.resources.dataset_resource import DataResource
from model_audit_cli.resources.model_resource import ModelResource


class Model(BaseModel):
    """Represents a machine learning model with associated dataset and code resources.

    Attributes:
        dataset (DataResource): The dataset resource associated with the model.
        model (ModelResource): The model resource containing model-specific information.
        code (Optional[CodeResource]): The code resource associated with the model.
    """

    dataset: DataResource
    model: ModelResource
    code: Optional[CodeResource] = None
