import json
import uuid
from datetime import datetime, date
from typing import List, Any, Optional, Union
from pydantic import BaseModel, Field, parse_obj_as, validator


SMARTCONNECT_DATFORMAT = '%Y-%m-%dT%H:%M:%S'


class CategoryAttribute(BaseModel):
    key: str
    is_active: bool = Field(alias="isactive", default=True)


class Category(BaseModel):
    path: str
    hkeyPath: Optional[str]
    display: str
    is_multiple: Optional[bool] = Field(alias="ismultiple", default=False)
    is_active: Optional[bool] = Field(alias="isactive", default=True)
    attributes: Optional[List[CategoryAttribute]]


class AttributeOption(BaseModel):
    key: str
    display: str
    is_active: Optional[bool] = Field(alias="isActive", default=True)


class Attribute(BaseModel):
    key: str
    type: str
    isrequired: Optional[bool] = False
    display: str
    options: Optional[List[AttributeOption]]


class TransformationRule(BaseModel):
    match_pattern: dict
    transforms: dict


class SmartObservation(BaseModel):
    observationUuid: Optional[str]
    category: str
    attributes: dict

    validator("observationUuid")

    def clean_observationUuid(cls, val):
        # TODO: Redress to make observationUuid a UUID field.
        if val == 'None':
            return None
        return val


class SmartObservationGroup(BaseModel):
    observations: List[SmartObservation]


class Geometry(BaseModel):
    coordinates: List[float] = Field(..., max_item=2, min_items=2)


class File(BaseModel):
    filename: str
    data: str
    signatureType: Optional[str]


class SmartAttributes(BaseModel):
    observationGroups: Optional[List[SmartObservationGroup]]
    patrolUuid: Optional[str]
    patrolLegUuid: Optional[str]
    patrolId: Optional[str]
    incidentId: Optional[str]
    incidentUuid: Optional[str]
    team: Optional[str]
    objective: Optional[str]
    comment: Optional[str]
    isArmed: Optional[str]
    transportType: Optional[str]
    mandate: Optional[str]
    number: Optional[int]
    members: Optional[List[str]]
    leader: Optional[str]
    attachments: Optional[List[File]]


class Properties(BaseModel):
    dateTime: Optional[datetime]
    smartDataType: str
    smartFeatureType: str
    smartAttributes: Optional[Union[SmartObservation, SmartAttributes]]

    class Config:
        smart_union = True
        json_encoders = {
            datetime: lambda v: v.strftime(SMARTCONNECT_DATFORMAT)
        }


class SMARTRequest(BaseModel):
    type: str = 'Feature'
    geometry: Optional[Geometry]
    properties: Properties


class Waypoint(BaseModel):
    attachments: List[Any]  # test what is contained here
    conservation_area_uuid: str
    date: date
    id: str
    client_uuid: Optional[str]
    last_modified: datetime
    observation_groups: List[Any]  # test
    raw_x: float
    raw_y: float
    source: str
    time: str


class PatrolLeg(BaseModel):
    client_uuid: str
    end_date: date
    id: str
    mandate: dict
    members: List[dict]
    start_date = date
    type: dict
    uuid: str


class Patrol(BaseModel):
    armed: bool
    attributes: Optional[List[Any]]  # Need to test what values are in here
    client_uuid: str
    comment: str
    conservation_area: dict
    end_date: date
    id: str
    start_date: date
    team: Optional[dict]
    uuid: str


class SMARTResponseProperties(BaseModel):
    fid: str
    patrol: Optional[Patrol]
    patrol_leg: Optional[PatrolLeg]
    waypoint: Optional[Waypoint]


class SMARTResponse(BaseModel):
    type: str = 'Feature'
    geometry: Geometry
    properties: SMARTResponseProperties


class Names(BaseModel):
    name: str
    locale: Optional[str]


class ListOptions(BaseModel):
    id: str
    names: List[Names]


class PatrolMetaData(BaseModel):
    id: str
    names: List[Names]
    requiredWhen: Optional[str] = 'False'
    listOptions: Optional[List[ListOptions]] = None
    type: str


class PatrolDataModel(BaseModel):
    patrolMetadata: List[PatrolMetaData]


class ConservationArea(BaseModel):
    label: str
    status: str
    version: Optional[uuid.UUID]
    revision: int
    description: Optional[str]
    designation: Optional[str]
    organization: Optional[str]
    pointOfContact: Optional[str]
    location: Optional[str]
    owner: Optional[str]
    caBoundaryJson: Optional[str] = Field(None, description='A string containing GeoJSON')
    administrativeAreasJson: Optional[Any]
    uuid: uuid.UUID


class SmartConnectApiInfo(BaseModel):
    build_date: str = Field(None, alias='build-date')
    build_version: str = Field(None, alias='build-version')
    db_last_updated: str = Field(None, alias='db-last-updated')
    file_store_version: str = Field(None, alias='file-store-version')
    db_version: str = Field(None, alias='db-version')


class SMARTCompositeRequest(BaseModel):
    ca_uuid: str
    patrol_requests: Optional[List[SMARTRequest]] = []
    waypoint_requests: Optional[List[SMARTRequest]] = []
    track_point_requests: Optional[List[SMARTRequest]] = []


class SMARTUpdateRequest(BaseModel):
    ca_uuid: str
    waypoint_requests: Optional[List[SMARTRequest]] = []  # Only waypoints / incidents can be updated for now
