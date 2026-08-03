"""Tests for gundi_core.events.batches."""

import json
import uuid
from datetime import datetime, timezone

import pytest

from gundi_core.events import (
    ERObservationsBatch,
    ObservationsBatch,
    ObservationsBatchDelivered,
    ObservationsBatchDeliveryDetails,
    ObservationsBatchReceived,
    ObservationsBatchTransformedER,
    TransformedERObservationItem,
)
from gundi_core.schemas.v2 import ERObservation, Location, Observation


@pytest.fixture
def observations():
    return [
        Observation(
            gundi_id=str(uuid.uuid4()),
            data_provider_id="ddd0946d-15b0-4308-b93d-e0470b6d33b6",
            source_id=uuid.uuid4(),
            external_source_id=f"device-{i}",
            recorded_at=datetime(2026, 7, 1, 12, i, 0, tzinfo=timezone.utc),
            location=Location(lon=-122.0, lat=47.0),
        )
        for i in range(3)
    ]


@pytest.fixture
def er_items(observations):
    return [
        TransformedERObservationItem(
            gundi_id=obs.gundi_id,
            observation=ERObservation(
                manufacturer_id=obs.external_source_id,
                recorded_at=obs.recorded_at,
                location={"lon": obs.location.lon, "lat": obs.location.lat},
            ),
        )
        for obs in observations
    ]


def test_batch_received_round_trip(observations):
    event = ObservationsBatchReceived(
        payload=ObservationsBatch(
            data_provider_id="ddd0946d-15b0-4308-b93d-e0470b6d33b6",
            observations=observations,
        )
    )
    raw = json.loads(event.json())
    assert raw["event_type"] == "ObservationsBatchReceived"
    assert raw["schema_version"] == "v1"  # MUST stay v1: routing/dispatcher gates discard anything else
    rebuilt = ObservationsBatchReceived.parse_obj(raw)
    assert len(rebuilt.payload.observations) == 3
    assert rebuilt.payload.observations[0].external_source_id == "device-0"
    assert rebuilt.payload.batch_id  # auto-generated


def test_batch_transformed_er_round_trip(er_items):
    event = ObservationsBatchTransformedER(
        payload=ERObservationsBatch(
            batch_id=str(uuid.uuid4()),
            data_provider_id="ddd0946d-15b0-4308-b93d-e0470b6d33b6",
            destination_id="338225f3-91f9-4fe1-b013-353a229ce504",
            provider_key="gundi_movebank_abc123",
            items=er_items,
        )
    )
    raw = json.loads(event.json())
    assert raw["event_type"] == "ObservationsBatchTransformedER"
    assert raw["schema_version"] == "v1"
    rebuilt = ObservationsBatchTransformedER.parse_obj(raw)
    assert rebuilt.payload.provider_key == "gundi_movebank_abc123"
    assert len(rebuilt.payload.items) == 3
    assert str(rebuilt.payload.items[1].gundi_id) == str(er_items[1].gundi_id)


def test_batch_delivered_round_trip():
    gundi_ids = [str(uuid.uuid4()) for _ in range(3)]
    event = ObservationsBatchDelivered(
        payload=ObservationsBatchDeliveryDetails(
            batch_id=str(uuid.uuid4()),
            data_provider_id="ddd0946d-15b0-4308-b93d-e0470b6d33b6",
            destination_id="338225f3-91f9-4fe1-b013-353a229ce504",
            delivered_at=datetime(2026, 7, 29, 12, 0, 0, tzinfo=timezone.utc),
            gundi_ids=gundi_ids,
        )
    )
    raw = json.loads(event.json())
    assert raw["event_type"] == "ObservationsBatchDelivered"
    assert raw["schema_version"] == "v1"  # MUST stay v1: routing/dispatcher gates discard anything else
    rebuilt = ObservationsBatchDelivered.parse_obj(raw)
    assert [str(g) for g in rebuilt.payload.gundi_ids] == gundi_ids


def test_empty_observations_default_is_a_list():
    batch = ObservationsBatch(data_provider_id="ddd0946d-15b0-4308-b93d-e0470b6d33b6")
    assert batch.observations == []
    assert batch.observation_type == "obv"


def test_schema_version_is_pinned_to_v1():
    import pydantic

    for event_cls, payload in (
        (ObservationsBatchReceived, ObservationsBatch(data_provider_id="p1")),
        (
            ObservationsBatchTransformedER,
            ERObservationsBatch(data_provider_id="p1", destination_id="d1", provider_key="k"),
        ),
        (
            ObservationsBatchDelivered,
            ObservationsBatchDeliveryDetails(
                batch_id=str(uuid.uuid4()),
                data_provider_id="p1",
                destination_id="d1",
                delivered_at=datetime(2026, 7, 29, 12, 0, 0, tzinfo=timezone.utc),
            ),
        ),
    ):
        assert event_cls(payload=payload).schema_version == "v1"
        with pytest.raises(pydantic.ValidationError):
            event_cls(schema_version="v2", payload=payload)
