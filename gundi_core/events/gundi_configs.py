import pydantic
from gundi_core.schemas.v2 import (
    IntegrationSummary,
    IntegrationActionConfiguration,
    IntegrationConfigChanges,
    ActionConfigChanges,
    DeletionDetails
)
from .core import SystemEventBaseModel

# Events published by the portal on config changes


class IntegrationCreated(SystemEventBaseModel):
    payload: IntegrationSummary

class IntegrationUpdated(SystemEventBaseModel):
    payload: IntegrationConfigChanges

class IntegrationDeleted(SystemEventBaseModel):
    payload: DeletionDetails


class ActionConfigCreated(SystemEventBaseModel):
    payload: IntegrationActionConfiguration

class ActionConfigUpdated(SystemEventBaseModel):
    payload: ActionConfigChanges

class ActionConfigDeleted(SystemEventBaseModel):
    payload: DeletionDetails
