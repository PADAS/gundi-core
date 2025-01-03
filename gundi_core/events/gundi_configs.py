import pydantic
from gundi_core.schemas.v2 import (
    IntegrationSummary,
    IntegrationActionConfiguration,
    IntegrationConfigChanges,
    ActionConfigChanges,
    IntegrationDeletionDetails,
    ActionConfigDeletionDetails,
)
from .core import SystemEventBaseModel

# Events published by the portal on config changes


class IntegrationCreated(SystemEventBaseModel):
    payload: IntegrationSummary

class IntegrationUpdated(SystemEventBaseModel):
    payload: IntegrationConfigChanges

class IntegrationDeleted(SystemEventBaseModel):
    payload: IntegrationDeletionDetails


class ActionConfigCreated(SystemEventBaseModel):
    payload: IntegrationActionConfiguration

class ActionConfigUpdated(SystemEventBaseModel):
    payload: ActionConfigChanges

class ActionConfigDeleted(SystemEventBaseModel):
    payload: ActionConfigDeletionDetails
