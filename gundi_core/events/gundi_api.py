from gundi_core.schemas.v2 import (
    Observation,
    Event,
    Attachment,
    EventUpdate,
    TextMessage
)
from .core import SystemEventBaseModel

# Events published by the portal


class EventReceived(SystemEventBaseModel):
    payload: Event


class EventUpdateReceived(SystemEventBaseModel):
    payload: EventUpdate


class AttachmentReceived(SystemEventBaseModel):
    payload: Attachment


class ObservationReceived(SystemEventBaseModel):
    payload: Observation


class TextMessageReceived(SystemEventBaseModel):
    payload: TextMessage
