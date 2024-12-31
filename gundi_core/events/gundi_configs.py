import pydantic
from gundi_core.schemas.v2 import IntegrationSummary, IntegrationActionConfiguration, ConfigChanges
from .core import SystemEventBaseModel

# Events published by the portal on config changes


class IntegrationCreated(SystemEventBaseModel):
    payload: IntegrationSummary


class IntegrationUpdated(SystemEventBaseModel):
    payload: ConfigChanges


class IntegrationDeleted(SystemEventBaseModel):
    payload: IntegrationSummary


class ActionConfigCreated(SystemEventBaseModel):
    payload: IntegrationActionConfiguration

class ActionConfigUpdated(SystemEventBaseModel):
    payload: ConfigChanges

class ActionConfigDeleted(SystemEventBaseModel):
    payload: IntegrationActionConfiguration
