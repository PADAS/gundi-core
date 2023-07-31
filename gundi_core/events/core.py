import json
import uuid
from typing import List, Optional, Dict, Any
from datetime import datetime, timezone
from pydantic import BaseModel, Field, validator


class SystemEventBaseModel(BaseModel):
    event_id: uuid.UUID = Field(default_factory=uuid.uuid4)
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        title="ISO Timestamp",
        description="The date and time when the event was created.",
        example="2023-06-23T12:01:02-0700",
    )
    schema_version: Optional[str] = Field(
        "v1",
        example="v1",
        description="Event schema version",
    )
    payload: Optional[Any] = Field(
        {},
        example="{}",
        description="Event payload. This can be overwritten in more specific events",
    )

    def dict(self, *args, **kwargs):
        # Add the event_type field with the class name
        json_dict = super().dict(*args, **kwargs)
        json_dict["event_type"] = self.__class__.__name__
        return json_dict
