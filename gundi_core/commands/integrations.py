from typing import Optional, Dict, Any, Union
from pydantic.fields import Field
from uuid import UUID

from .core import SystemCommandBaseModel


class RunIntegrationAction(SystemCommandBaseModel):
    integration_id: Union[UUID, str] = Field(
        None,
        title="Integration ID",
        description="The unique ID of the Integration.",
    )
    action_id: str = Field(
        None,
        title="Action Identifier",
        description="A string identifier of the action of the related integration.",
    )
    config_overrides: Optional[Dict[str, Any]] = Field(
        None,
        title="Configuration",
        description="A dictionary with the configuration used to execute the action",
    )
