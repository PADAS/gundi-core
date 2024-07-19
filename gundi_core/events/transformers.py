from gundi_core.schemas.v1 import EREvent, ERObservation
from gundi_core.schemas.v2 import EREventUpdate, ERAttachment
from .core import SystemEventBaseModel

# Events published by the transformer service


class EventTransformedER(SystemEventBaseModel):
    payload: EREvent


class EventUpdateTransformedER(SystemEventBaseModel):
    payload: EREventUpdate


class AttachmentTransformedER(SystemEventBaseModel):
    payload: ERAttachment


class ObservationTransformedER(SystemEventBaseModel):
    payload: ERObservation
