from typing import List, Optional, Dict, Any
from typing import Union
from uuid import UUID
from enum import Enum
from pydantic import BaseModel, Field, validator
from gundi_core.schemas.v2.gundi import LogLevel
from .core import SystemEventBaseModel


class IntegrationActionEvent(BaseModel):
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
    config_data: Optional[Dict[str, Any]] = Field(
        None,
        title="Configuration",
        description="A dictionary with the configuration used to execute the action",
    )


class ActionExecutionStarted(IntegrationActionEvent):
    pass


class ActionExecutionComplete(IntegrationActionEvent):
    result: Optional[Dict[str, Any]] = Field(
        None,
        title="Result",
        description="A dictionary with the result of the action execution.",
    )


class ActionExecutionFailed(IntegrationActionEvent):
    error: Optional[str] = Field(
        "",
        title="Error",
        description="A string with the error message of the action execution.",
    )
    error_traceback: Optional[str] = Field(
        "",
        title="Error Traceback",
        description="A string with the traceback of the error.",
    )
    request_verb: Optional[str] = Field(
        "",
        title="Request Verb",
        description="The HTTP verb of the request that caused the error.",
    )
    request_url: Optional[str] = Field(
        "",
        title="Request URL",
        description="The URL of the request that caused the error.",
    )
    request_data: Optional[str] = Field(
        "",
        title="Request Data",
        description="The data of the request that caused the error.",
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


class IntegrationWebhookEvent(BaseModel):
    integration_id: Union[UUID, str] = Field(
        None,
        title="Integration ID",
        description="The unique ID of the Integration.",
    )
    webhook_id: str = Field(
        None,
        title="Webhook Identifier",
        description="A string identifier of the webhook of the related integration.",
    )
    config_data: Optional[Dict[str, Any]] = Field(
        None,
        title="Configuration",
        description="A dictionary with the configuration used to process the webhook request",
    )


class WebhookExecutionStarted(IntegrationWebhookEvent):
    pass


class WebhookExecutionComplete(IntegrationWebhookEvent):
    result: Optional[Dict[str, Any]] = Field(
        None,
        title="Result",
        description="A dictionary with the result of the webhook execution.",
    )


class WebhookExecutionFailed(IntegrationWebhookEvent):
    error: Optional[str] = Field(
        "",
        title="Error",
        description="A string with the error message of the webhook execution.",
    )


class CustomActivityLog(IntegrationActionEvent):
    title: str = Field(
        "Custom Log",
        title="Title",
        description="A string with the title of the log.",
    )
    level: LogLevel = Field(
        LogLevel.INFO,
        title="Log Level",
        description="The level of the log.",
    )
    data: Optional[Dict[str, Any]] = Field(
        None,
        title="Extra Data",
        description="A dictionary with extra data to be logged.",
    )


class CustomWebhookLog(IntegrationWebhookEvent):
    title: str = Field(
        "Custom Log",
        title="Title",
        description="A string with the title of the log.",
    )
    level: LogLevel = Field(
        LogLevel.INFO,
        title="Log Level",
        description="The level of the log.",
    )
    data: Optional[Dict[str, Any]] = Field(
        None,
        title="Extra Data",
        description="A dictionary with extra data to be logged.",
    )


class IntegrationActionCustomLog(SystemEventBaseModel):
    payload: CustomActivityLog


class IntegrationActionStarted(SystemEventBaseModel):
    payload: ActionExecutionStarted


class IntegrationActionComplete(SystemEventBaseModel):
    payload: ActionExecutionComplete


class IntegrationActionFailed(SystemEventBaseModel):
    payload: ActionExecutionFailed


class IntegrationWebhookCustomLog(SystemEventBaseModel):
    payload: CustomWebhookLog


class IntegrationWebhookStarted(SystemEventBaseModel):
    payload: WebhookExecutionStarted


class IntegrationWebhookComplete(SystemEventBaseModel):
    payload: WebhookExecutionComplete


class IntegrationWebhookFailed(SystemEventBaseModel):
    payload: WebhookExecutionFailed


# Observation dropped for one destination, so the portal can mark the trace
# (GUNDI-5178). An event the consumer cannot match to a trace row is acked and
# DISCARDED against a forward-only pipeline, so the record is then lost for good —
# hence the required identity fields, and schema_version pinned like the batch envelopes.


class ObservationFilterReason(str, Enum):
    DEVICE_WHITELIST = "device_whitelist"
    DEVICE_BLACKLIST = "device_blacklist"


class FilteredObservation(BaseModel):
    gundi_id: Union[UUID, str] = Field(
        ...,
        title="Gundi ID",
        description="The unique ID of the observation that was dropped.",
    )
    related_to: Optional[Union[UUID, str]] = Field(
        None,
        title="Related To",
        description="The Gundi ID of the parent object, for updates and attachments.",
    )
    data_provider_id: Union[UUID, str] = Field(
        ...,
        title="Data Provider ID",
        description="The provider the observation came from.",
    )
    destination_id: Union[UUID, str] = Field(
        ...,
        title="Destination ID",
        description="The destination the observation was dropped for.",
    )
    external_source_id: Optional[str] = Field(
        None,
        title="External Source ID",
        description="The device ID the rule matched on.",
    )
    # Plain string so an unrecognised kind still records the drop, but bounded at the
    # consumer's column width, which a longer value could not fit under any circumstance.
    filtered_by: Optional[str] = Field(
        None,
        title="Filtered By",
        max_length=32,
        description="Which kind of rule dropped it; see ObservationFilterReason.",
    )


class ObservationFiltered(SystemEventBaseModel):
    # The trace's `filtered_at` is the envelope's `timestamp`; the payload does not repeat it.
    schema_version: str = Field("v1", const=True)
    payload: FilteredObservation
# Observation dropped because its transform raised or produced nothing, so the portal
# can mark the trace with has_error (GUNDI-5178 phase 3). Unlike a filtered drop this
# IS an error and belongs in connection health. Defined ahead of its publisher so it
# rides the same release as ObservationFiltered — coordinating releases is the
# expensive part, not the schema.


class FailedTransformation(BaseModel):
    gundi_id: Union[UUID, str] = Field(
        ...,
        title="Gundi ID",
        description="The unique ID of the observation whose transform failed.",
    )
    related_to: Optional[Union[UUID, str]] = Field(
        None,
        title="Related To",
        description="The Gundi ID of the parent object, for updates and attachments.",
    )
    data_provider_id: Union[UUID, str] = Field(
        ...,
        title="Data Provider ID",
        description="The provider the observation came from.",
    )
    destination_id: Union[UUID, str] = Field(
        ...,
        title="Destination ID",
        description="The destination whose transform failed.",
    )
    observation_type: Optional[str] = Field(
        None,
        title="Observation Type",
        description="Stream type of the dropped observation (ev/obv/...).",
    )
    error: str = Field(
        ...,
        title="Error",
        # The consumer writes this into GundiTrace.error, a varchar(500).
        max_length=500,
        description="Human-readable description of the failure.",
    )
    error_type: Optional[str] = Field(
        None,
        title="Error Type",
        description="The exception class name, when the failure was an exception.",
    )


class ObservationTransformationFailed(SystemEventBaseModel):
    schema_version: str = Field("v1", const=True)
    payload: FailedTransformation
