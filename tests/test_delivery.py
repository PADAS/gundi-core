"""Tests for gundi_core.events.delivery."""

import json
import uuid
from datetime import datetime, timezone

import pytest

from gundi_core.events import GundiDelivery, ProviderInfo
from gundi_core.schemas.v2 import (
    Attachment,
    Event,
    EventUpdate,
    Location,
    Observation,
    RouteConfiguration,
    StreamPrefixEnum,
    TextMessage,
)


@pytest.fixture
def provider_info():
    return ProviderInfo(
        provider_id=str(uuid.uuid4()),
        provider_type="telonics",
        provider_name="Telonics Push Provider",
        owner_id=str(uuid.uuid4()),
        owner_name="Wildlife Org A",
    )


@pytest.fixture
def observation():
    return Observation(
        source_id=uuid.uuid4(),
        external_source_id="device-42",
        source_name="Collar 42",
        type="tracking-device",
        recorded_at=datetime(2026, 6, 1, 12, 0, 0, tzinfo=timezone.utc),
        location=Location(lon=-122.0, lat=47.0),
    )


@pytest.fixture
def event():
    return Event(
        source_id=uuid.uuid4(),
        external_source_id="device-99",
        recorded_at=datetime(2026, 6, 1, 12, 0, 0, tzinfo=timezone.utc),
        location=Location(lon=-122.0, lat=47.0),
        title="Lion sighting",
        event_type="wildlife_sighting",
        event_details={"species": "lion", "count": 1},
    )


def test_delivery_with_observation_payload(provider_info, observation):
    delivery = GundiDelivery(payload=observation, provider=provider_info)
    assert isinstance(delivery.payload, Observation)
    assert delivery.payload.external_source_id == "device-42"
    assert delivery.event_type == "GundiDelivery"


def test_delivery_with_event_payload(provider_info, event):
    delivery = GundiDelivery(payload=event, provider=provider_info)
    assert isinstance(delivery.payload, Event)
    assert delivery.payload.title == "Lion sighting"


def test_delivery_serializes_payload_with_observation_type(provider_info, observation):
    delivery = GundiDelivery(payload=observation, provider=provider_info)
    data = delivery.dict()
    assert data["event_type"] == "GundiDelivery"
    assert data["payload"]["observation_type"] == StreamPrefixEnum.observation.value


def test_delivery_round_trips_observation(provider_info, observation):
    delivery = GundiDelivery(payload=observation, provider=provider_info)
    raw = json.loads(delivery.json())
    rebuilt = GundiDelivery.parse_obj(raw)
    assert isinstance(rebuilt.payload, Observation)
    assert rebuilt.payload.external_source_id == observation.external_source_id


def test_delivery_round_trips_event(provider_info, event):
    delivery = GundiDelivery(payload=event, provider=provider_info)
    raw = json.loads(delivery.json())
    rebuilt = GundiDelivery.parse_obj(raw)
    assert isinstance(rebuilt.payload, Event)
    assert rebuilt.payload.title == event.title


def test_delivery_discriminator_picks_correct_payload_type(provider_info):
    raw_event_update = {
        "payload": {
            "observation_type": StreamPrefixEnum.event_update.value,
            "source_id": str(uuid.uuid4()),
            "changes": {"status": "resolved"},
        },
        "provider": provider_info.dict(),
    }
    delivery = GundiDelivery.parse_obj(raw_event_update)
    assert isinstance(delivery.payload, EventUpdate)
    assert delivery.payload.changes == {"status": "resolved"}


def test_delivery_discriminator_handles_attachment(provider_info):
    raw_attachment = {
        "payload": {
            "observation_type": StreamPrefixEnum.attachment.value,
            "source_id": str(uuid.uuid4()),
            "file_path": "/tmp/image.jpg",
        },
        "provider": provider_info.dict(),
    }
    delivery = GundiDelivery.parse_obj(raw_attachment)
    assert isinstance(delivery.payload, Attachment)
    assert delivery.payload.file_path == "/tmp/image.jpg"


def test_delivery_discriminator_handles_text_message(provider_info):
    raw_text = {
        "payload": {
            "observation_type": StreamPrefixEnum.text_message.value,
            "source_id": str(uuid.uuid4()),
            "sender": "555-0100",
            "recipients": ["dispatch@example.com"],
            "text": "Need help at coordinates",
            "created_at": "2026-06-01T12:00:00+00:00",
        },
        "provider": provider_info.dict(),
    }
    delivery = GundiDelivery.parse_obj(raw_text)
    assert isinstance(delivery.payload, TextMessage)
    assert delivery.payload.sender == "555-0100"


def test_route_configuration_is_optional(provider_info, observation):
    delivery = GundiDelivery(payload=observation, provider=provider_info)
    assert delivery.route_configuration is None


def test_route_configuration_round_trips(provider_info, observation):
    route_config = RouteConfiguration(
        id=uuid.uuid4(),
        name="Test route config",
        data={"field_mappings": {"some-provider": {"obv": {}}}},
    )
    delivery = GundiDelivery(
        payload=observation,
        provider=provider_info,
        route_configuration=route_config,
    )
    raw = json.loads(delivery.json())
    rebuilt = GundiDelivery.parse_obj(raw)
    assert rebuilt.route_configuration is not None
    assert rebuilt.route_configuration.data == route_config.data


def test_provider_info_required_provider_id():
    with pytest.raises(Exception):
        ProviderInfo()


def test_provider_info_defaults():
    info = ProviderInfo(provider_id="abc")
    assert info.provider_type == ""
    assert info.provider_name == ""
    assert info.owner_id == ""
    assert info.owner_name == ""
