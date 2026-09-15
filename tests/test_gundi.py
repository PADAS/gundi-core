"""Tests for the routing-filter part of gundi_core.schemas.v2.gundi."""

import json
import uuid

import pydantic
import pytest

from gundi_core.schemas.v2 import Route, RouteFilter


@pytest.fixture
def destination_id():
    return "6ba7b811-9dad-11d1-80b4-00c04fd430c8"


@pytest.fixture
def provider_id():
    return "6ba7b810-9dad-11d1-80b4-00c04fd430c8"


@pytest.fixture
def route_payload(destination_id, provider_id):
    return {
        "id": str(uuid.UUID("3f2504e0-4f89-41d3-9a0c-0305e82c3301")),
        "name": "Lotek collars to Acme ER",
        "filters": {
            destination_id: {
                "type": "list",
                "mode": "whitelist",
                "enabled": True,
                "by_provider": {provider_id: ["collar-001", "collar-002"]},
            }
        },
    }


def test_route_parses_its_filters(route_payload, destination_id, provider_id):
    route = Route.parse_obj(route_payload)

    rule = route.filters[destination_id]
    assert rule.mode == "whitelist"
    assert rule.type == "list"
    assert rule.enabled is True
    assert rule.by_provider[provider_id] == ["collar-001", "collar-002"]


def test_route_filters_round_trip(route_payload, destination_id):
    route = Route.parse_obj(route_payload)

    rebuilt = Route.parse_obj(json.loads(route.json()))

    assert rebuilt.filters[destination_id].by_provider == (
        route.filters[destination_id].by_provider
    )


def test_route_without_filters_still_parses():
    # An old portal talking to a new consumer mid-rollout.
    route = Route.parse_obj({"id": str(uuid.uuid4()), "name": "No rules here"})

    assert route.filters == {}


def test_route_ignores_keys_it_does_not_know():
    # The property that lets the portal ship the filters block before this field existed:
    # an unknown key is dropped at parse time rather than raising.
    route = Route.parse_obj({"name": "Future route", "something_new": {"a": 1}})

    assert not hasattr(route, "something_new")


def test_filter_keeps_providers_apart(destination_id):
    # The reason the payload is grouped: external_id is unique only within a provider, so
    # the same device name under two providers must not collapse into one list.
    first = "6ba7b810-9dad-11d1-80b4-00c04fd430c8"
    second = "9f1c2d3e-0000-4000-8000-000000000001"
    route = Route.parse_obj(
        {
            "filters": {
                destination_id: {
                    "mode": "whitelist",
                    "by_provider": {first: ["C-100"], second: ["C-100"]},
                }
            }
        }
    )

    by_provider = route.filters[destination_id].by_provider
    assert by_provider[first] == ["C-100"]
    assert by_provider[second] == ["C-100"]
    assert len(by_provider) == 2


def test_filter_defaults(destination_id):
    route = Route.parse_obj({"filters": {destination_id: {"mode": "blacklist"}}})

    rule = route.filters[destination_id]
    assert rule.type == "list"
    assert rule.enabled is True
    assert rule.by_provider == {}


def test_disabled_filter_survives_the_wire(destination_id):
    # A disabled rule travels rather than being omitted, so an operator can switch one off
    # without the device list disappearing from routing's view.
    route = Route.parse_obj(
        {"filters": {destination_id: {"mode": "whitelist", "enabled": False}}}
    )

    rebuilt = Route.parse_obj(json.loads(route.json()))

    assert rebuilt.filters[destination_id].enabled is False


def test_empty_filters_block_is_valid():
    route = Route.parse_obj({"name": "Route with the block present but empty", "filters": {}})

    assert route.filters == {}


def test_filter_rejects_a_malformed_provider_map(destination_id):
    with pytest.raises(pydantic.ValidationError):
        Route.parse_obj(
            {"filters": {destination_id: {"mode": "whitelist", "by_provider": "collar-001"}}}
        )


def test_route_filter_can_be_built_directly(provider_id):
    rule = RouteFilter(mode="blacklist", by_provider={provider_id: ["qa-test-device"]})

    assert rule.type == "list"
    assert rule.by_provider[provider_id] == ["qa-test-device"]
