"""Tests for the routing-filter part of gundi_core.schemas.v2.gundi."""

import json
import uuid

import pydantic
import pytest

from gundi_core.schemas.v2 import (
    Route,
    RouteFilter,
    RouteFilterMode,
    RouteFilterType,
)


@pytest.fixture
def destination_id():
    return "6ba7b811-9dad-11d1-80b4-00c04fd430c8"


@pytest.fixture
def provider_id():
    return "6ba7b810-9dad-11d1-80b4-00c04fd430c8"


@pytest.fixture
def unrelated_id():
    """An id no fixture payload mentions, for the lookup-misses cases."""
    return uuid.UUID("11111111-2222-3333-4444-555555555555")


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
    route = Route.parse_obj({"id": "7c9f4f2e-0000-4000-8000-000000000001", "name": "No rules here"})

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


def test_filter_constants_match_the_wire_values():
    # Both sides compare against these; renaming one silently stops matching.
    assert RouteFilterType.LIST.value == "list"
    assert RouteFilterMode.WHITELIST.value == "whitelist"
    assert RouteFilterMode.BLACKLIST.value == "blacklist"


def test_filter_lookup_works_with_the_uuids_a_consumer_actually_holds(route_payload):
    # The trap this closes: `filters` keys arrive as JSON strings, while the ids a
    # consumer reads off the same payload parse into UUID objects — `destinations[i].id`
    # is `Union[UUID, str]`. A plain `filters.get(destination.id)` therefore misses, and
    # because absence of a rule means "allow", the whitelist silently never applies.
    destination_id = list(route_payload["filters"].keys())[0]
    provider_id = list(
        route_payload["filters"][destination_id]["by_provider"].keys()
    )[0]
    payload = dict(route_payload)
    payload["destinations"] = [{"id": destination_id, "name": "Acme ER"}]
    payload["data_providers"] = [{"id": provider_id, "name": "Lotek"}]
    route = Route.parse_obj(payload)

    destination, provider = route.destinations[0], route.data_providers[0]
    assert isinstance(destination.id, uuid.UUID)
    assert isinstance(provider.id, uuid.UUID)

    rule = route.filter_for(destination.id)
    assert rule is not None
    assert rule.ids_for(provider.id) == ["collar-001", "collar-002"]


def test_filter_lookup_also_accepts_plain_strings(route_payload, destination_id, provider_id):
    route = Route.parse_obj(route_payload)

    assert route.filter_for(destination_id).ids_for(provider_id) == [
        "collar-001",
        "collar-002",
    ]


def test_lookup_of_an_unruled_destination_is_none(route_payload, unrelated_id):
    # Absence means allow: a rule on one destination must not restrict any other.
    route = Route.parse_obj(route_payload)

    assert route.filter_for(unrelated_id) is None
    assert route.filter_for(None) is None


def test_lookup_of_an_unnamed_provider_is_none(route_payload, destination_id, unrelated_id):
    # A rule only affects the providers it names. None is not the same as an empty list.
    rule = Route.parse_obj(route_payload).filter_for(destination_id)

    assert rule.ids_for(unrelated_id) is None
    assert rule.ids_for(None) is None


def test_null_filters_block_reads_as_empty(unrelated_id):
    # Enforcement is fail-open, but a None surviving here would make the consumer's
    # `filters.get(...)` raise AttributeError inside the destination fan-out — an
    # exception, not the allow path.
    route = Route.parse_obj({"name": "Nulls from the portal", "filters": None})

    assert route.filters == {}
    assert route.filter_for(unrelated_id) is None


def test_null_by_provider_reads_as_empty(destination_id, unrelated_id):
    route = Route.parse_obj(
        {"filters": {destination_id: {"mode": "whitelist", "by_provider": None}}}
    )

    rule = route.filters[destination_id]
    assert rule.by_provider == {}
    assert rule.ids_for(unrelated_id) is None


def test_uuid_keys_survive_direct_construction(destination_id, provider_id):
    # Building a Route in Python (tests, fixtures, the portal's own code) with UUID keys
    # used to raise "str type expected" before the keys were normalized.
    route = Route(
        filters={
            uuid.UUID(destination_id): RouteFilter(
                mode=RouteFilterMode.WHITELIST.value,
                by_provider={uuid.UUID(provider_id): ["collar-001"]},
            )
        }
    )

    assert route.filter_for(destination_id).ids_for(provider_id) == ["collar-001"]


def test_an_unrecognised_mode_still_parses(destination_id):
    # Fail-open depends on this: an enum-typed field would raise here and cost the
    # consumer the whole route payload, every other destination's rules included.
    route = Route.parse_obj(
        {"filters": {destination_id: {"mode": "allowlist", "type": "geoboundary"}}}
    )

    rule = route.filters[destination_id]
    assert rule.mode == "allowlist"
    assert rule.type == "geoboundary"


def test_a_disabled_rule_is_left_falsy_when_null(destination_id):
    # Deliberately not coerced to the True default: a null must disable the rule (allow),
    # never enable it, or a malformed payload would start dropping data.
    route = Route.parse_obj(
        {"filters": {destination_id: {"mode": "whitelist", "enabled": None}}}
    )

    assert not route.filters[destination_id].enabled


def test_a_list_rule_is_recognised_as_one(route_payload, destination_id):
    assert Route.parse_obj(route_payload).filter_for(destination_id).is_device_list()


def test_a_rule_of_another_type_is_not_a_device_list(destination_id, provider_id):
    # The gap this closes: every rule type carries a `mode`, so a geographic rule
    # occupying the destination's slot is not self-evidently inert. Without the type
    # check a consumer would read its `by_provider` as a device list and drop whatever
    # that happened to contain — fail-open covers an unrecognised value, not one type's
    # semantics applied to another.
    route = Route.parse_obj(
        {
            "filters": {
                destination_id: {
                    "type": "geoboundary",
                    "mode": "whitelist",
                    "by_provider": {provider_id: ["collar-001"]},
                }
            }
        }
    )

    rule = route.filter_for(destination_id)
    assert rule.mode == RouteFilterMode.WHITELIST.value
    assert not rule.is_device_list()


def test_a_rule_with_no_type_at_all_is_not_a_device_list(destination_id):
    # An explicit null is not the default. Nothing should read list semantics out of a
    # rule that never claimed to be one.
    route = Route.parse_obj(
        {"filters": {destination_id: {"type": None, "mode": "whitelist"}}}
    )

    assert not route.filter_for(destination_id).is_device_list()


def test_one_rule_per_destination(destination_id, provider_id):
    # The shape's known limitation, pinned so a future change to it is deliberate: the
    # block holds a single rule per arrow, while the portal's model permits one per type.
    route = Route.parse_obj(
        {
            "filters": {
                destination_id: {
                    "type": "list",
                    "mode": "whitelist",
                    "by_provider": {provider_id: ["collar-001"]},
                }
            }
        }
    )

    assert isinstance(route.filters[destination_id], RouteFilter)
