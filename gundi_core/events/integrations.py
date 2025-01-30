from typing import List, Optional, Dict, Any
from typing import Union
from uuid import UUID
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
