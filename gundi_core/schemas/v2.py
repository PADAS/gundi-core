from typing import List, Optional, Dict, Any
from typing import Union
from uuid import UUID
from datetime import datetime, timezone
from pydantic import BaseModel, Field, validator
from enum import Enum
from .v1 import ERLocation


class StreamPrefixEnum(str, Enum):
    observation = "obv"
    observation_update = "obvu"
    event = "ev"
    event_update = "evu"
    attachment = "att"


class Location(BaseModel):
    lat: float = Field(..., ge=-90.0, le=90.0, title="Latitude in decimal degrees")
    lon: float = Field(..., ge=-180.0, le=360.0, title="Longitude in decimal degrees")
    alt: float = Field(0.0, title="Altitude in meters.")
    hdop: Optional[int] = None
    vdop: Optional[int] = None


class GundiBaseModel(BaseModel):
    gundi_id: Union[UUID, str] = Field(
        None,
        title="Gundi ID",
        description="A unique object ID generated by gundi.",
    )
    related_to: Optional[Union[UUID, str]] = Field(
        None,
        title="Related Object - Gundi ID",
        description="The Gundi ID of the related object",
    )
    owner: str = "na"
    data_provider_id: Optional[Union[UUID, str]] = Field(
        None,
        title="Provider ID",
        description="The unique ID of the Integration providing the data.",
    )
    annotations: Optional[Dict[str, Any]] = Field(
        None,
        title="Annotations",
        description="A dictionary of extra data that will be passed to destination systems.",
    )


class Observation(GundiBaseModel):
    source_id: Optional[Union[UUID, str]] = Field(
        None,
        example="bc14b256-dec0-4363-831d-39d0d2d85d50",
        description="A unique identifier of the source associated with this data.",
    )
    external_source_id: Optional[str] = Field(
        "None",
        example="901870234",
        description="The manufacturer provided ID for the Source associated with this data (a.k.a. device).",
    )
    source_name: Optional[str] = Field(
        None,
        title="An optional, human-friendly name for the associated source.",
        example="Security Vehicle A",
    )
    type: Optional[str] = Field(
        "tracking-device",
        title="Type identifier for the associated source.",
        example="tracking-device",
    )
    subject_type: Optional[str] = Field(
        None,
        title="Type identifier for the subjected associated to the source.",
        example="giraffe",
    )
    recorded_at: datetime = Field(
        ...,
        title="Timestamp for the data, preferably in ISO format.",
        example="2021-03-21 12:01:02-0700",
    )
    location: Location
    additional: Optional[Dict[str, Any]] = Field(
        None,
        title="Additional Data",
        description="A dictionary of extra data that will be passed to destination systems.",
    )
    observation_type: str = Field(StreamPrefixEnum.observation.value, const=True)

    @validator("recorded_at")
    def clean_recorded_at(cls, val):
        if not val.tzinfo:
            val = val.replace(tzinfo=timezone.utc)
        return val

    class Config:
        title = "Observation"

        schema_extra = {
            "example": {
                "source_id": "bc14b256-dec0-4363-831d-39d0d2d85d50",
                "external_source_id": "901870234",
                "source_name": "Logistics Truck A",
                "type": "tracking-device",
                "recorded_at": "2021-03-27 11:15:00+0200",
                "location": {"lon": 35.43902, "lat": -1.59083},
                "additional": {
                    "voltage": "7.4",
                    "fuel_level": 71,
                    "speed": "41 kph",
                },
            }
        }


class Event(GundiBaseModel):
    source_id: Optional[Union[UUID, str]] = Field(
        None,
        title="Source ID",
        description="An unique Source ID generated by Gundi.",
    )
    external_source_id: Optional[str] = Field(
        "none",
        example="901870234",
        description="The manufacturer provided ID for the Source associated with this data (a.k.a. device).",
    )
    recorded_at: Optional[datetime] = Field(
        ...,
        title="Timestamp for the data, preferrably in ISO format.",
        example="2021-03-21 12:01:02-0700",
    )
    location: Optional[Location]
    title: Optional[str] = Field(
        None,
        title="Event title",
        description="Human-friendly title for this Event",
    )
    event_type: Optional[str] = Field(
        None, title="Event Type",
        description="Identifies the type of this Event"
    )

    event_details: Optional[Dict[str, Any]] = Field(
        None,
        title="Event Details",
        description="A dictionary containing details of this GeoEvent.",
    )
    geometry: Optional[Dict[str, Any]] = Field(
        None,
        title="Event Geometry",
        description="A dictionary containing details of this GeoEvent geoJSON.",
    )
    observation_type: str = Field(StreamPrefixEnum.event.value, const=True)

    @validator("recorded_at", allow_reuse=True)
    def clean_recorded_at(cls, val):

        if not val.tzinfo:
            val = val.replace(tzinfo=timezone.utc)
        return val


class EventUpdate(GundiBaseModel):
    source_id: Optional[Union[UUID, str]] = Field(
        None,
        title="Source ID",
        description="An unique Source ID generated by Gundi.",
    )
    external_source_id: Optional[str] = Field(
        "none",
        example="901870234",
        description="The manufacturer provided ID for the Source associated with this data (a.k.a. device).",
    )
    changes: Optional[Dict[str, Any]] = Field(
        None,
        title="Event Updates",
        description="A dictionary containing the changes made to the event.",
    )
    observation_type: str = Field(StreamPrefixEnum.event_update.value, const=True)


class Attachment(GundiBaseModel):
    source_id: Optional[Union[UUID, str]] = Field(
        None,
        title="Source ID",
        description="An unique Source ID generated by Gundi.",
    )
    external_source_id: Optional[str] = Field(
        "none",
        example="901870234",
        description="The manufacturer provided ID for the Source associated with this data (a.k.a. device).",
    )
    file_path: str
    observation_type: str = Field(StreamPrefixEnum.attachment.value, const=True)
    annotations: Optional[Dict[str, Any]] = Field(
        None,
        title="Annotations",
        description="A dictionary of extra data that will be passed to destination systems.",
    )


class Organization(BaseModel):
    id: Union[UUID, str] = Field(
        None,
        title="Organization ID",
        description="Id of the organization owning the connection",
    )
    name: Optional[str] = Field(
        "",
        example="Wild Conservation Organization X",
        description="Name of the organization owning this connection",
    )
    description: Optional[str] = Field(
        "",
        example="An organization in X dedicated to protect YZ..",
        description="Description of the organization owning this connection",
    )


class ConnectionIntegrationType(BaseModel):
    id: Union[UUID, str] = Field(
        None,
        title="Integration Type ID",
        description="Id of an integration in Gundi",
    )
    name: Optional[str] = Field(
        "",
        example="EarthRanger",
        description="Name of the third-party system or technology",
    )
    value: Optional[str] = Field(
        "",
        example="earth_ranger",
        description="Natural key for the technology type",
        min_length=2,
        max_length=200,
        regex="^[a-z0-9_]+$",
    )


class ConnectionIntegrationOwner(BaseModel):
    id: Union[UUID, str] = Field(
        None,
        title="Organization ID",
        description="Id of the organization owning the connection",
    )
    name: Optional[str] = Field(
        "",
        example="Wild Conservation Organization X",
        description="Name of the organization owning this connection",
    )


class ConnectionIntegration(BaseModel):
    id: Union[UUID, str] = Field(
        None,
        title="Integration ID",
        description="Id of an integration associated to the connection",
    )
    name: Optional[str] = Field(
        "",
        example="X Data Provider for Y Reserve",
        description="Connection name (Data Provider)",
    )
    type: Optional[ConnectionIntegrationType]
    owner: Optional[ConnectionIntegrationOwner]
    base_url: Optional[str] = Field(
        "",
        example="https://easterisland.pamdas.org/",
        description="Base URL of the third party system associated with this integration.",
    )
    status: Optional[str] = Field(
        "unknown",
        example="healthy",
        description="Computed status representing if the integration is working properly or not",
    )


class ConnectionRoute(BaseModel):
    id: Union[UUID, str] = Field(
        None,
        title="Route ID",
        description="Id of a route associated to the connection",
    )
    name: Optional[str] = Field(
        "",
        example="X Animal collars to Y",
        description="Route name",
    )


class Connection(BaseModel):
    id: Union[UUID, str] = Field(
        None,
        title="Connection ID",
        description="Id of the connection",
    )
    provider: ConnectionIntegration
    destinations: Optional[List[ConnectionIntegration]]
    routing_rules: Optional[List[ConnectionRoute]]
    default_route: Optional[ConnectionRoute]
    owner: Optional[Organization]
    status: Optional[str] = Field(
        "unknown",
        example="healthy",
        description="Aggregate status representing if the connection is working properly or not",
    )


class RouteConfiguration(BaseModel):
    id: Union[UUID, str] = Field(
        None,
        title="Route Configuration ID",
        description="Id of the configuration associated with the route",
    )
    name: Optional[str] = Field(
        "",
        example="Event Type Mappings",
        description="A descriptive name for the configuration",
    )
    data: Optional[Dict[str, Any]] = {}


class Route(BaseModel):
    id: Union[UUID, str] = Field(
        None,
        title="Route ID",
        description="Id of the route",
    )
    name: Optional[str] = Field(
        "",
        example="X Route for Y",
        description="Route name",
    )
    owner: Optional[Union[UUID, str]]
    data_providers: Optional[List[ConnectionIntegration]]
    destinations: Optional[List[ConnectionIntegration]]
    configuration: Optional[RouteConfiguration]
    additional: Optional[Dict[str, Any]] = {}


class IntegrationAction(BaseModel):
    id: Union[UUID, str] = Field(
        None,
        title="Integration Action ID",
        description="Id of an integration in Gundi",
    )
    type: Optional[str] = Field(
        "",
        example="pull",
        description="Free text to allow grouping and filtering actions",
    )
    name: Optional[str] = Field(
        "",
        example="Pull Events",
        description="A human-readable name for the action",
    )
    value: Optional[str] = Field(
        "",
        example="pull_events",
        description="Short text id for the action, to be used programmatically",
        min_length=2,
        max_length=200,
        regex="^[a-z0-9_]+$",
    )
    description: Optional[str] = Field(
        "",
        example="Pull Events from X system",
        description="Description of the action",
    )
    action_schema: Optional[Dict[str, Any]] = Field(
        {},
        alias="schema",
        example="{}",
        description="Schema definition of any configuration required for this action, in jsonschema format.",
    )


class IntegrationActionSummary(BaseModel):
    id: Union[UUID, str] = Field(
        None,
        title="Integration Action ID",
        description="Id of an integration in Gundi",
    )
    type: Optional[str] = Field(
        "",
        example="pull",
        description="Free text to allow grouping and filtering actions",
    )
    name: Optional[str] = Field(
        "",
        example="Pull Events",
        description="A human-readable name for the action",
    )
    value: Optional[str] = Field(
        "",
        example="pull_events",
        description="Short text id for the action, to be used programmatically",
        min_length=2,
        max_length=200,
        regex="^[a-z0-9_]+$",
    )

class IntegrationWebhook(BaseModel):
    id: Union[UUID, str] = Field(
        None,
        title="Integration Webhook ID",
        description="Id of an webhook in Gundi",
    )
    name: Optional[str] = Field(
        "",
        example="Generic Webhook",
        description="A human-readable name for the webhook",
    )
    value: Optional[str] = Field(
        "",
        example="generic_webhook",
        description="Short text id for the webhook, to be used programmatically",
        min_length=2,
        max_length=200,
        regex="^[a-z0-9_]+$",
    )
    description: Optional[str] = Field(
        "",
        example="Generic Webhook for all events",
        description="Description of the webhook",
    )
    webhook_schema: Optional[Dict[str, Any]] = Field(
        {},
        alias="schema",
        example="""
        {
            "type": "object",
            "title": "Generic JSON Transformation Config",
            "required": [
                "json_schema",
                "output_type",
                "jq_filter"
            ],
            "properties": {
                "json_schema": {
                    "type": "object",
                    "title": "Webhook Data JSON Schema",
                    "description": "Define the schema of the webhook data as json schema.",
                },
                "jq_filter": {
                    "type": "string",
                    "title": "JQ Transformation Filter",
                    "default": ".",
                    "example": "{source: .deviceId,source_name: .name, type: .deviceType, recorded_at: (.trackPoint.time / 1000 | todateiso8601), location: {lat: .trackPoint.point.x, lon: .trackPoint.point.y},additional: {teamId: .teamId}}",
                    "description": "JQ filter to transform JSON data."
                },
                "output_type": {
                    "type": "string",
                    "title": "Output Type",
                    "description": "Output type for the transformed data: 'obv' or 'ev'"
                }
            }
        }
        """,
        description="Schema definition of any configuration required for this webhook, in jsonschema format.",
    )

class IntegrationWebhookSummary(BaseModel):
    id: Union[UUID, str] = Field(
        None,
        title="Integration Webhook ID",
        description="Id of an webhook in Gundi",
    )
    name: Optional[str] = Field(
        "",
        example="Generic Webhook",
        description="A human-readable name for the webhook",
    )
    value: Optional[str] = Field(
        "",
        example="generic_webhook",
        description="Short text id for the webhook, to be used programmatically",
        min_length=2,
        max_length=200,
        regex="^[a-z0-9_]+$",
    )

class IntegrationType(BaseModel):
    id: Union[UUID, str] = Field(
        None,
        title="Integration Type ID",
        description="Id of an integration in Gundi",
    )
    name: Optional[str] = Field(
        "",
        example="EarthRanger",
        description="Name of the third-party system or technology",
    )
    value: Optional[str] = Field(
        "",
        example="earth_ranger",
        description="Natural key for the technology type",
        min_length=2,
        max_length=200,
        regex="^[a-z0-9_]+$",
    )
    description: Optional[str] = Field(
        "",
        example="EarthRanger is a software solution for wildlife monitoring and protection in real-time.",
        description="Description of the third-party system or technology",
    )
    actions: Optional[List[IntegrationAction]]
    webhook: Optional[IntegrationWebhook]


class IntegrationActionConfiguration(BaseModel):
    id: Union[UUID, str] = Field(
        None,
        title="Configuration ID",
        description="Id of the configuration",
    )
    integration: Union[UUID, str] = Field(
        None,
        title="Integration ID",
        description="Id of the integration that this configuration is for",
    )
    action: IntegrationActionSummary
    data: Optional[Dict[str, Any]] = {}


class WebhookConfiguration(BaseModel):
    id: Union[UUID, str] = Field(
        None,
        title="Configuration ID",
        description="Id of the configuration",
    )
    integration: Union[UUID, str] = Field(
        None,
        title="Integration ID",
        description="Id of the integration that this configuration is for",
    )
    webhook: IntegrationWebhookSummary
    data: Optional[Dict[str, Any]] = {}


class Integration(BaseModel):
    id: Union[UUID, str] = Field(
        None,
        title="Integration ID",
        description="Id of an integration in Gundi",
    )
    name: Optional[str] = Field(
        "",
        example="X Data Provider for Y Reserve",
        description="Route name",
    )
    type: IntegrationType
    base_url: Optional[str] = Field(
        "",
        example="https://easterisland.pamdas.org/",
        description="Base URL of the third party system associated with this integration.",
    )
    enabled: Optional[bool] = Field(
        True,
        example="true",
        description="Enable/Disable this integration",
    )
    owner: Organization
    configurations: Optional[List[IntegrationActionConfiguration]]
    webhook_configuration: Optional[WebhookConfiguration]
    default_route: Optional[ConnectionRoute]
    additional: Optional[Dict[str, Any]] = {}
    status: Optional[Dict[str, Any]] = Field(  # ToDo: Review once Activity/Monitoring is implemented
        {},
        example="{}",
        description="A json object with detailed information about the integration health status",
    )


# Earth Ranger Supported Actions & Configuration Schemas
class EarthRangerActions(str, Enum):
    AUTHENTICATE = "auth"
    PUSH_EVENT = "push_event"
    # ToDo. Add more as we support them


class ERAuthActionConfig(BaseModel):
    username: Optional[str] = Field(
        "",
        example="user@pamdas.org",
        description="Username used to authenticate against Earth Ranger API",
    )
    password: Optional[str] = Field(
        "",
        example="passwd1234abc",
        description="Password used to authenticate against Earth Ranger API",
    )
    token: Optional[str] = Field(
        "",
        example="1b4c1e9c-5ee0-44db-c7f1-177ede2f854a",
        description="Token used to authenticate against Earth Ranger API",
    )


class ERPushEventActionConfig(BaseModel):
    event_type: Optional[str] = Field(
        "",
        example="animal_sighting",
        description="Event type to be applied to event sent to Earth Ranger (Optional).",
    )


# Movebank Supported Actions & Configuration Schemas
class MovebankActions(str, Enum):
    AUTHENTICATE = "auth"
    PERMISSIONS = "permissions"
    PUSH_OBSERVATIONS = "push_observations"
    # ToDo. Add more as we support them


class MBAuthActionConfig(BaseModel):
    username: str = Field(
        example="movebankadminuser",
        description="Username used to authenticate against Movebank API",
    )
    password: str = Field(
        example="passwd1234abc",
        description="Password used to authenticate against Movebank API",
    )


class MBUserPermission(BaseModel):
    username: str = Field(
        alias="login",
        example="movebankuser",
        description="Username used to login in Movebank",
    )
    tag_id: str = Field(
        alias="tag",
        example="awt.1320894.cc53b809784e406db9cfd8dcbc624985",
        description="Tag ID, to grant the user access to its data.",
    )

    class Config:
        allow_population_by_field_name = True


class MBPermissionsActionConfig(BaseModel):
    study: str = Field(
        "gundi",
        example="gundi",
        description="Name of the movebank study",
    )
    default_movebank_usernames: List[str] = Field(
        default_factory=list,
        description="Movebank usernames allowed to access this study"
    )
    permissions: Optional[List[MBUserPermission]]


class MBPushObservationsActionConfig(BaseModel):
    feed: str = Field(
        "gundi/earthranger",
        example="gundi/earthranger",
        description="Name of the movebank feed",
    )

# SMART Supported Actions & Configuration Schemas
class SMARTActions(str, Enum):
    AUTHENTICATE = "auth"
    PUSH_EVENTS = "push_events"
    # ToDo. Add more as we support them


class SMARTAuthActionConfig(BaseModel):
    login: str = Field(
        example="smartuser",
        description="Username used to authenticate against SMART Connect server",
    )
    password: str = Field(
        example="passwd1234abc",
        description="Password used to authenticate against SMART Connect server",
    )
    version: Optional[str] = "7.5"

# SMART Connect Outbound configuration models.
class SMARTCategoryPair(BaseModel):
    event_type: str
    category_path: str

class SMARTOptionMap(BaseModel):
    from_key: str
    to_key: str

class SMARTAttributeMapper(BaseModel):
    from_key: str
    to_key: str
    type: Optional[str] = "string"
    options_map: Optional[List[SMARTOptionMap]]
    default_option: Optional[str]
    event_types: Optional[List[str]]


class SMARTTransformationRules(BaseModel):
    category_map: Optional[List[SMARTCategoryPair]] = []
    attribute_map: Optional[List[SMARTAttributeMapper]] = []


class SMARTPushEventActionConfig(BaseModel):
    ca_uuid: Optional[UUID]
    ca_uuids: Optional[List[UUID]]
    configurable_models_enabled: Optional[List[UUID]]
    configurable_models_lists: Optional[dict]
    transformation_rules: Optional[SMARTTransformationRules]
    timezone: Optional[str]


class GundiTrace(BaseModel):
    object_id: Union[UUID, str] = Field(
        None,
        title="Gundi ID",
        description="A unique object ID generated by gundi.",
    )
    object_type: Optional[str] = Field(
        "",
        title="Object type",
        example="ev",
        description="Steam type such as event, observation, etc.",
    )
    related_to: Optional[Union[UUID, str]] = Field(
        None,
        title="Related Object ID",
        description="The Gundi ID of the related object",
    )
    data_provider: Optional[Union[UUID, str]] = Field(
        None,
        title="Provider ID",
        description="The unique ID of the Integration providing the data.",
    )
    destination: Optional[Union[UUID, str]] = Field(
        None,
        title="Destination ID",
        description="The unique ID of the Integration with the destination system.",
    )
    delivered_at: Optional[datetime] = Field(
        ...,
        title="ISO Timestamp",
        description="The date and time when the observation was sent to the destination system.",
        example="2023-06-23T12:01:02-0700",
    )
    external_id: Optional[Union[UUID, str]] = Field(
        None,
        example="901870234",
        description="The ID provided by the external system after sending the observation",
    )
    created_at: Optional[datetime] = Field(
        ...,
        title="ISO Timestamp",
        description="The date and time when the trace of the observation was recorded in the portal db.",
        example="2023-06-23T12:01:02-0700",
    )
    updated_at: Optional[datetime] = Field(
        ...,
        title="ISO Timestamp",
        description="The date and time when the trace of the observation was updated in the portal db.",
        example="2023-06-23T12:01:02-0700",
    )


# Models used by the Dispatchers to emit system events
class DispatchedObservation(BaseModel):
    gundi_id: Union[UUID, str] = Field(
        None,
        title="Gundi ID",
        description="A unique object ID generated by gundi.",
    )
    related_to: Optional[Union[UUID, str]] = Field(
        None,
        title="Related Object - Gundi ID",
        description="The Gundi ID of the related object",
    )
    external_id: Optional[Union[UUID, str]] = Field(
        None,
        example="901870234",
        description="The ID provided by the external system after sending the observation",
    )
    data_provider_id: Optional[Union[UUID, str]] = Field(
        None,
        title="Provider ID",
        description="The unique ID of the Integration providing the data.",
    )
    destination_id: Optional[Union[UUID, str]] = Field(
        None,
        title="Destination ID",
        description="The unique ID of the Integration with the destination system.",
    )
    delivered_at: Optional[datetime] = Field(
        ...,
        title="ISO Timestamp",
        description="The date and time when the observation was sent to the destination system.",
        example="2023-06-23T12:01:02-0700",
    )


class ERAttachment(GundiBaseModel):
    file_path: str


class EREventUpdate(GundiBaseModel):
    changes: Optional[Dict[str, Any]] = Field(
        None,
        title="ER Event Updates",
        description="A dictionary containing the changes made to the ER event.",
    )


models_by_stream_type = {
    StreamPrefixEnum.observation: Observation,
    StreamPrefixEnum.event: Event,
    StreamPrefixEnum.attachment: Attachment,
}

