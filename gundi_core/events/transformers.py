from gundi_core.schemas.v2 import (
    EREvent, ERObservation, EREventUpdate, ERAttachment,
    SMARTCompositeRequest, SMARTUpdateRequest,
    WPSWatchImage, WPSWatchImageMetadata
)
from .core import SystemEventBaseModel


# Events published by the transformer service


# Earth Ranger
class EventTransformedER(SystemEventBaseModel):
    payload: EREvent


class EventUpdateTransformedER(SystemEventBaseModel):
    payload: EREventUpdate


class AttachmentTransformedER(SystemEventBaseModel):
    payload: ERAttachment


class ObservationTransformedER(SystemEventBaseModel):
    payload: ERObservation


# SMART
class EventTransformedSMART(SystemEventBaseModel):
    payload: SMARTCompositeRequest


class EventUpdateTransformedSMART(SystemEventBaseModel):
    payload: SMARTUpdateRequest


# WPS Watch
class EventTransformedWPSWatch(SystemEventBaseModel):
    payload: WPSWatchImageMetadata


class AttachmentTransformedWPSWatch(SystemEventBaseModel):
    payload: WPSWatchImage

