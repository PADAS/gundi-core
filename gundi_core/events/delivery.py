from typing import Optional, Union

from pydantic import BaseModel, Field

from gundi_core.schemas.v2 import (
    Attachment,
    Event,
    EventUpdate,
    Observation,
    RouteConfiguration,
    TextMessage,
)
from .core import SystemEventBaseModel


GundiPayload = Union[Observation, Event, EventUpdate, Attachment, TextMessage]


class ProviderInfo(BaseModel):
    """Provider identity attached to a GundiDelivery.

    Pure identity — does NOT carry destination-specific metadata such as
    EarthRanger's provider_key. Runners that need such values resolve them
    from the route_configuration on their own.
    """

    provider_id: str = Field(
        ...,
        description="UUID of the inbound provider integration.",
    )
    provider_type: str = Field(
        "",
        example="earth_ranger",
        description="Natural key for the provider's technology type.",
    )
    provider_name: str = Field(
        "",
        description="Human-friendly provider name.",
    )
    owner_id: str = Field(
        "",
        description="UUID of the organization owning the provider integration.",
    )
    owner_name: str = Field(
        "",
        description="Name of the organization owning the provider integration.",
    )


class GundiDelivery(SystemEventBaseModel):
    """A generic delivery envelope published by cdip-routing to an action runner.

    Used when a destination integration has additional.generic_model = true.
    The runner is responsible for transforming the payload to its destination's
    schema and delivering it.
    """

    payload: GundiPayload
    route_configuration: Optional[RouteConfiguration] = None
    provider: ProviderInfo

    class Config:
        # Smart-union picks the best-fitting type from GundiPayload rather than
        # left-to-right first-match. The const observation_type field on each
        # payload type then uniquely identifies the correct concrete class.
        smart_union = True
