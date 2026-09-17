"""Tests for gundi_core.events.integrations."""

import json
import uuid

import pydantic
import pytest

from gundi_core.events import (
    FilteredObservation,
    ObservationFiltered,
    ObservationFilterReason,
)


@pytest.fixture
def gundi_id():
    return uuid.UUID("3f2504e0-4f89-41d3-9a0c-0305e82c3301")


@pytest.fixture
def provider_id():
    return uuid.UUID("6ba7b810-9dad-11d1-80b4-00c04fd430c8")


@pytest.fixture
def destination_id():
    return uuid.UUID("6ba7b811-9dad-11d1-80b4-00c04fd430c8")


@pytest.fixture
def filtered_observation(gundi_id, provider_id, destination_id):
    return FilteredObservation(
        gundi_id=gundi_id,
        data_provider_id=provider_id,
        destination_id=destination_id,
        external_source_id="collar-001",
        filtered_by="device_whitelist",
    )


def test_observation_filtered_round_trips(
    filtered_observation, gundi_id, provider_id, destination_id
):
    event = ObservationFiltered(payload=filtered_observation)

    rebuilt = ObservationFiltered.parse_obj(json.loads(event.json()))

    assert rebuilt.payload.external_source_id == "collar-001"
    assert rebuilt.payload.filtered_by == "device_whitelist"
    assert str(rebuilt.payload.gundi_id) == str(gundi_id)
    assert str(rebuilt.payload.data_provider_id) == str(provider_id)
    assert str(rebuilt.payload.destination_id) == str(destination_id)


def test_observation_filtered_carries_its_event_type(filtered_observation):
    # event_type is derived from the class name and is what consumers switch on, so a
    # rename is a silent break on the wire.
    serialized = json.loads(ObservationFiltered(payload=filtered_observation).json())

    assert serialized["event_type"] == "ObservationFiltered"


def test_observation_filtered_defaults_to_schema_version_v1(filtered_observation):
    # cdip-routing and the ER dispatcher discard messages whose schema_version does not
    # match what they expect.
    event = ObservationFiltered(payload=filtered_observation)

    assert event.schema_version == "v1"
    assert json.loads(event.json())["schema_version"] == "v1"


def test_observation_filtered_autogenerates_its_envelope(filtered_observation):
    event = ObservationFiltered(payload=filtered_observation)

    assert event.event_id is not None
    assert event.timestamp is not None


def test_observation_filtered_pins_its_schema_version(filtered_observation):
    # Not merely defaulted: the consumer discards an event whose schema_version it does
    # not recognise, and the pipeline is forward-only, so the trace record is lost.
    with pytest.raises(pydantic.ValidationError):
        ObservationFiltered(payload=filtered_observation, schema_version="v2")


def test_observation_filtered_requires_a_payload():
    with pytest.raises(pydantic.ValidationError):
        ObservationFiltered()


def test_filtered_observation_rejects_an_unusable_id():
    with pytest.raises(pydantic.ValidationError):
        FilteredObservation(gundi_id=["not", "an", "id"])


@pytest.mark.parametrize(
    "missing", ["gundi_id", "data_provider_id", "destination_id"]
)
def test_filtered_observation_requires_every_identity_field(
    missing, gundi_id, provider_id, destination_id
):
    # An event the consumer cannot match to a trace row is acknowledged and discarded,
    # and nothing replays it — so an absent id must fail at construction, in the
    # publisher, rather than travel as a well-formed event that identifies nothing.
    fields = {
        "gundi_id": gundi_id,
        "data_provider_id": provider_id,
        "destination_id": destination_id,
    }
    del fields[missing]

    with pytest.raises(pydantic.ValidationError):
        FilteredObservation(**fields)


def test_filtered_observation_tolerates_absent_optionals(
    gundi_id, provider_id, destination_id
):
    # An attachment or an update has a parent; a plain observation does not.
    payload = FilteredObservation(
        gundi_id=gundi_id, data_provider_id=provider_id, destination_id=destination_id
    )

    assert payload.related_to is None
    assert payload.external_source_id is None
    assert payload.filtered_by is None


def test_filtered_observation_keeps_the_parent_reference(
    gundi_id, provider_id, destination_id
):
    parent = uuid.UUID("7c9e6679-7425-40de-944b-e07fc1f90ae7")
    payload = FilteredObservation(
        gundi_id=gundi_id,
        data_provider_id=provider_id,
        destination_id=destination_id,
        related_to=parent,
    )

    rebuilt = FilteredObservation.parse_obj(json.loads(payload.json()))

    assert str(rebuilt.related_to) == str(parent)


def test_filter_reason_constants_match_the_wire_values():
    # The consumer stores these verbatim; renaming one silently stops matching.
    assert ObservationFilterReason.DEVICE_WHITELIST.value == "device_whitelist"
    assert ObservationFilterReason.DEVICE_BLACKLIST.value == "device_blacklist"


def test_filtered_by_accepts_a_reason_the_package_does_not_know(
    gundi_id, provider_id, destination_id
):
    # Room for filter kinds beyond the device lists. Rejecting an unknown value here
    # would discard the event rather than record the drop.
    payload = FilteredObservation(
        gundi_id=gundi_id,
        data_provider_id=provider_id,
        destination_id=destination_id,
        filtered_by="geoboundary",
    )

    assert payload.filtered_by == "geoboundary"


def test_filtered_by_is_bounded_by_the_consumers_column(
    gundi_id, provider_id, destination_id
):
    # A reason too long to store is not a leniency case: the consumer could not persist
    # it under any circumstance, so it fails here, in the publisher, rather than as a
    # database error after the drop has already happened.
    with pytest.raises(pydantic.ValidationError):
        FilteredObservation(
            gundi_id=gundi_id,
            data_provider_id=provider_id,
            destination_id=destination_id,
            filtered_by="d" * 33,
        )


@pytest.mark.parametrize("reason", list(ObservationFilterReason))
def test_every_known_reason_fits_that_column(
    reason, gundi_id, provider_id, destination_id
):
    # Guards the other direction: adding a reason whose name overflows the column is
    # caught here rather than the first time it is published.
    payload = FilteredObservation(
        gundi_id=gundi_id,
        data_provider_id=provider_id,
        destination_id=destination_id,
        filtered_by=reason.value,
    )

    assert payload.filtered_by == reason.value
