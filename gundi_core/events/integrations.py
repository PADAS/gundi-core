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


class ObservationFilterReason(str, Enum):
    DEVICE_WHITELIST = "device_whitelist"
    DEVICE_BLACKLIST = "device_blacklist"


class FilteredObservation(BaseModel):
    # The three identity fields are required. The consumer stamps the drop onto an
    # existing trace row found by these values, and an event it cannot match is
    # acknowledged and discarded; the pipeline is forward-only, so that trace record is
    # not recoverable. Better for the publisher to fail loudly at construction than to
    # emit an event that silently identifies nothing.
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
        description=(
            "The destination the observation was dropped for. A rule covers one "
            "destination, so the same observation may still be delivered elsewhere."
        ),
    )
    external_source_id: Optional[str] = Field(
        None,
        title="External Source ID",
        description="The device ID the rule matched on.",
    )
    # Left as a plain string rather than enum-typed: the consumer's column has room for
    # filter kinds beyond the two below, and rejecting an unknown *value* at parse time
    # would discard the event rather than record the drop. Publishers should use
    # ObservationFilterReason.
    #
    # Bounded at the consumer's column width even so. Leniency is only worth having where
    # the value could still be stored, and a longer one could not be under any
    # circumstance — so accepting it here buys nothing and merely moves the failure from
    # a ValidationError in the publisher to a database error in the consumer, by which
    # point the drop has already happened and the trace record is gone either way.
    filtered_by: Optional[str] = Field(
        None,
        title="Filtered By",
        max_length=32,
        description=(
            "Which kind of rule dropped it; see ObservationFilterReason. Bounded by the "
            "32-character column the consumer stores it in."
        ),
    )


class ObservationFiltered(SystemEventBaseModel):
    # Pinned to v1: the consumer discards events whose schema_version it does not
    # recognise, and the pipeline is forward-only, so the trace record would be lost.
    # The trace's `filtered_at` comes from the envelope's `timestamp`; the payload does not
    # repeat it.
    schema_version: str = Field("v1", const=True)
    payload: FilteredObservation
