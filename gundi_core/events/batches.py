import uuid
from datetime import datetime
from typing import List, Union
from uuid import UUID

from pydantic import BaseModel, Field

from gundi_core.schemas.v2 import ERObservation, Observation, StreamPrefixEnum
from .core import SystemEventBaseModel


# Batch envelopes: a message carrying observations that share a data provider
# and stream type. Publishers only emit non-empty batches; an empty batch is
# still valid to PARSE (consumers treat it as a no-op) so a shrunk-to-zero
# envelope never turns into a hard failure. Pipeline stages may SPLIT or
# SHRINK a batch (drop items, regroup per destination) but must never MERGE
# batches — that invariant is what keeps the pipeline free of buffers and
# flush timers.
#
# IMPORTANT: these events are pinned to schema_version="v1" (const).
# cdip-routing and the ER dispatcher discard transformer events with any
# other schema_version.


class ObservationsBatch(BaseModel):
    batch_id: Union[UUID, str] = Field(default_factory=uuid.uuid4)
    data_provider_id: Union[UUID, str] = Field(
        ...,
        description="The provider Integration shared by every observation in the batch.",
    )
    # Named observation_type for consistency with the per-item payload
    # schemas (e.g. Observation.observation_type); the PubSub message
    # attribute carrying the same value is still named stream_type.
    observation_type: str = Field(StreamPrefixEnum.observation.value, const=True)
    observations: List[Observation] = Field(default_factory=list)


class ObservationsBatchReceived(SystemEventBaseModel):
    schema_version: str = Field("v1", const=True)
    payload: ObservationsBatch


class TransformedERObservationItem(BaseModel):
    gundi_id: Union[UUID, str] = Field(
        ...,
        description="Gundi ID of the source observation (per-item identity — "
                    "single-item messages carry this in PubSub attributes instead).",
    )
    observation: ERObservation


class ERObservationsBatch(BaseModel):
    batch_id: Union[UUID, str] = Field(default_factory=uuid.uuid4)
    data_provider_id: Union[UUID, str]
    destination_id: Union[UUID, str]
    provider_key: str = Field(
        ...,
        description="EarthRanger provider key shared by every item. The ER "
                    "sensors endpoint path embeds this, so one batch = one key.",
    )
    items: List[TransformedERObservationItem] = Field(default_factory=list)


class ObservationsBatchTransformedER(SystemEventBaseModel):
    schema_version: str = Field("v1", const=True)
    payload: ERObservationsBatch


class ObservationsBatchDeliveryDetails(BaseModel):
    batch_id: Union[UUID, str]
    data_provider_id: Union[UUID, str]
    destination_id: Union[UUID, str]
    delivered_at: datetime
    gundi_ids: List[Union[UUID, str]] = Field(default_factory=list)
    # No external_ids: ER's bulk sensors response has no reliable per-item IDs,
    # and nothing downstream depends on observation external_ids (unlike events).


class ObservationsBatchDelivered(SystemEventBaseModel):
    schema_version: str = Field("v1", const=True)
    payload: ObservationsBatchDeliveryDetails
