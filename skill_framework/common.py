from pydantic import BaseModel, ConfigDict

class FrameworkBaseModel(BaseModel):
    model_config = ConfigDict(use_attribute_docstrings=True)