from gundi_core.schemas.v2 import DispatchedObservation, UpdatedObservation, CustomDispatcherLog
from .core import SystemEventBaseModel

# Events emmited by dispatchers

class ObservationDelivered(SystemEventBaseModel):
    payload: DispatchedObservation


class ObservationDeliveryFailed(SystemEventBaseModel):
    payload: DispatchedObservation


class ObservationUpdated(SystemEventBaseModel):
    payload: UpdatedObservation


class ObservationUpdateFailed(SystemEventBaseModel):
    payload: UpdatedObservation


class DispatcherCustomLog(SystemEventBaseModel):
    payload: CustomDispatcherLog



