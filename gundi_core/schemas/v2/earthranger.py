from typing import Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field
from .. import v1 as schemas_v1


class EREventLocation(BaseModel):
    longitude: float = Field(..., title="Longitude in decimal degrees")
    latitude: float = Field(..., title="Latitude in decimal degrees")


class EREvent(BaseModel):
    title: str = Field(
        None,
        title="GeoEvent title",
        description="Human-friendly title for this GeoEvent",
    )
    event_type: str = Field(
        None, title="GeoEvent Type", description="Identifies the type of this GeoEvent"
    )
    time: datetime = Field(
        ...,
        title="Timestamp for the data, preferrably in ISO format.",
        example="2021-03-21 12:01:02-0700",
    )
    location: Optional[EREventLocation]
    event_details: Optional[Dict[str, Any]] = Field(
        None,
        title="Additional Data",
        description="A dictionary of extra data that will be passed to destination systems.",
    )
    geometry: Optional[Dict[str, Any]] = Field( # geojson???
        None,
        title="GeoEvent Geometry",
        description="A dictionary containing details of this GeoEvent geoJSON.",
    )
    state: Optional[schemas_v1.EREventState]

    class Config:
        extra = "allow"  # To allow adding extra fields with field mappings


class ERAttachment(BaseModel):
    file_path: str

    class Config:
        extra = "allow"  # To allow adding extra fields with field mappings


class ERObservationLocation(BaseModel):
    lon: float = Field(..., title="Longitude in decimal degrees")
    lat: float = Field(..., title="Latitude in decimal degrees")


class ERObservation(BaseModel):
    manufacturer_id: Optional[str] = Field(
        "none",
        example="901870234",
        description="A unique identifier of the device associated with this data.",
    )
    source_type: Optional[str] = Field(
        "tracking-device",
        title="Type identifier for the associated device.",
        example="gps-radio",
    )
    subject_name: Optional[str] = Field(
        None,
        title="An optional, human-friendly name for the subject.",
        example="Security Vehicle A",
    )
    subject_type: Optional[str] = Field(
        None,
        title="Type identifier for the subject associated to this observation.",
        example="vehicle",
    )
    subject_subtype: Optional[str] = Field(
        None,
        title="Suntype identifier for the subject associated to this observation.",
        example="car",
    )
    recorded_at: datetime = Field(
        ...,
        title="Timestamp for the data, preferrably in ISO format.",
        example="2021-03-21 12:01:02-0700",
    )
    location: Optional[ERObservationLocation]
    additional: Optional[Dict[str, Any]] = Field(
        None,
        title="Additional Data",
        description="A dictionary of extra data that will be passed to destination systems.",
    )

    class Config:
        extra = "allow"  # To allow adding extra fields with field mappings


class EREventUpdate(BaseModel):
    changes: Optional[Dict[str, Any]] = Field(
        None,
        title="ER Event Updates",
        description="A dictionary containing the changes made to the ER event.",
    )

    class Config:
        extra = "allow"  # To allow adding extra fields with field mappings


class ERMessage(BaseModel):
    # Text messages sent to Earthranger
    message_type: str = Field(
        "inbox",
        title="Message Type",
        description="Type of the message, e.g., 'inbox'.",
    )
    text: Optional[str] = Field(
        "",
        title="Message Text",
        description="The content of the message.",
    )
    message_time: datetime = Field(
        ...,
        title="Message Timestamp",
        description="Timestamp when the message was sent or received.",
    )
    device_location: Optional[ERObservationLocation] = Field(
        None,
        title="Device Location",
        description="Location of the device when the message was sent or received.",
    )
    additional: Optional[Dict[str, Any]] = Field(
        default_factory=dict,
        title="Additional Data",
        description="A dictionary of extra data that will be passed to ER.",
    )