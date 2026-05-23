"""Reference-data schemas — types used by destination-system provisioning.

Stream records (observations, events, messages) carry slug values for
`event_type`, `subject_type`, `subject_subtype`, `category`. The destination
system (EarthRanger, SMART, etc.) must have rows provisioned that match
those slugs or it rejects the record on POST. The dispatcher layer reads
records, derives the set of `ReferenceDataItem`s a destination needs, and
calls a destination-specific adapter to create them if missing.

These schemas are the contract between cdip-routing's `ReferenceDataAdapter`
Protocol and the per-destination dispatcher implementations.

Phase 1 of the reference-data plan ships the lazy provisioning path inside
the dispatcher only. Phase 2 will add a `ReferenceDataDeclaration` payload
and a `ReferenceDataUpserted` system event so integrations can declare
their catalog up-front; those additions belong in this module too when
they land.
"""
from enum import Enum
from typing import Any, Dict, Optional, Union
from uuid import UUID

from pydantic import BaseModel, Field


class ReferenceDataKind(str, Enum):
    """The kind of reference-data row, used as a discriminator across destinations.

    Each destination's adapter maps the kind to the appropriate API:
    e.g. EarthRanger maps EVENT_TYPE → /activity/eventtypes/, SUBJECT_TYPE →
    /subjecttypes/, etc.
    """
    EVENT_TYPE = "event_type"
    SUBJECT_TYPE = "subject_type"
    SUBJECT_GROUP = "subject_group"
    CATEGORY = "category"


class ReferenceDataItem(BaseModel):
    """A single reference-data row a destination must have provisioned.

    `value` is the slug used inside stream records (e.g. an event's
    `event_type` field), and is the unique key the destination indexes on.

    `attributes` carries kind-specific fields. The adapter for each
    destination type knows which attributes it cares about; unknown
    attributes are ignored by the adapter. Typical contents per kind:
      - event_type:    display_name, default_priority, icon, color, category
      - subject_type:  display_name, default_group, icon
      - subject_group: display_name, members (list of subject ids)
      - category:      display_name, parent_category
    """
    kind: ReferenceDataKind = Field(
        ...,
        description="Discriminator selecting the destination-side resource type.",
    )
    value: str = Field(
        ...,
        title="Slug",
        description=(
            "Stable identifier used inside stream records (e.g. 'tracpoint_speeding'). "
            "Unique within (integration_id, kind)."
        ),
        min_length=1,
        max_length=255,
    )
    integration_id: Union[UUID, str] = Field(
        ...,
        title="Source Integration ID",
        description="The Gundi integration that declared (or emitted records referencing) this item.",
    )
    display_name: Optional[str] = Field(
        "",
        title="Display Name",
        description=(
            "Human-readable label shown in the destination UI. Adapter implementations "
            "may fall back to a humanized form of `value` when this is empty."
        ),
    )
    attributes: Dict[str, Any] = Field(
        default_factory=dict,
        description=(
            "Kind-specific fields (icon, color, default_priority, parent_category, "
            "subject group members, etc.). See class docstring for typical contents."
        ),
    )
