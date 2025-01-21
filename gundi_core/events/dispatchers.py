from typing import Optional
from pydantic import BaseModel, Field
from gundi_core.schemas.v2 import DispatchedObservation, UpdatedObservation, CustomDispatcherLog
from .core import SystemEventBaseModel


class DispatcherErrorDetails(BaseModel):
    error: str = Field(
        "",
        title="Error",
        description="A human-readable string describing the error.",
    )
    error_traceback: Optional[str] = Field(
        "",
        title="Error Traceback",
        description="A string with the traceback of the error.",
    )
    server_response_status: Optional[int] = Field(
        None,
        title="Server Response Status",
        description="The status code of the server response.",
    )
    server_response_body: Optional[str] = Field(
        "",
        title="Server Response",
        description="The response from the server as text.",
    )


class DeliveryErrorDetails(DispatcherErrorDetails):
    observation: Optional[DispatchedObservation] = Field(
        None,
        title="Observation",
        description="The observation that caused the error.",
    )


class UpdateErrorDetails(DispatcherErrorDetails):
    observation: Optional[UpdatedObservation] = Field(
        None,
        title="Observation",
        description="The observation that caused the error.",
    )


# Events emmited by dispatchers

class ObservationDelivered(SystemEventBaseModel):
    payload: DispatchedObservation


class ObservationDeliveryFailed(SystemEventBaseModel):
    schema_version: str = Field("v2", const=True)
    payload: DeliveryErrorDetails


class ObservationUpdated(SystemEventBaseModel):
    payload: UpdatedObservation


class ObservationUpdateFailed(SystemEventBaseModel):
    schema_version: str = Field("v2", const=True)
    payload: UpdateErrorDetails


class DispatcherCustomLog(SystemEventBaseModel):
    payload: CustomDispatcherLog



