from gundi_core.schemas.v2 import Observation, Event, Attachment, ObservationUpdate, EventUpdate
from .core import SystemEventBaseModel


# Events emmited by the portal


class EventReceived(SystemEventBaseModel):
    payload: Event


class EventUpdateReceived(SystemEventBaseModel):
    payload: EventUpdate


class AttachmentReceived(SystemEventBaseModel):
    payload: Attachment


class ObservationReceived(SystemEventBaseModel):
    payload: Observation


class ObservationUpdateReceived(SystemEventBaseModel):
    payload: ObservationUpdate
