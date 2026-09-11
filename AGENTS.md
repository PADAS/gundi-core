# AGENTS.md

This file provides guidance to coding agents (Claude Code and others) when working with code in this
repository.

## What this is

`gundi-core` is a **shared schema/contract library**, not a service. It has no runtime behaviour beyond
pydantic models: the platform-wide data schemas plus the system-event (EDA) envelopes exchanged over
Pub/Sub by the other Gundi repos — the portal (`cdip`), `cdip-routing`, the transformer, the dispatchers,
and the `gundi-integration-*` action runners. It is published to PyPI as `gundi-core` and pinned as a
dependency by all of them.

The practical consequence: **every change here is a wire-format change to already-deployed services.**
See "Compatibility rules" below before editing any model.

## Commands

Tooling is `uv` + `hatchling` (migrated off Poetry in `64b798c`).

```bash
uv sync                      # install project + dev group (pytest, pytest-asyncio)
uv run pytest -q             # full suite
uv run pytest tests/test_batches.py -q
uv run pytest tests/test_batches.py::test_schema_version_is_pinned_to_v1 -q
uv build                     # wheel + sdist
```

There is no linter or formatter configured, and no CI workflow for PRs — `release.yml` is the only
workflow and runs only on tags.

## Releasing

1. Bump `__version__` in `gundi_core/__init__.py` (hatchling reads the version from there).
2. Tag `vX.Y.Z` and push the tag.

`release.yml` runs the tests, then hard-fails unless the tag is **strictly** `vX.Y.Z` (pre-release
tags like `v1.2.3-rc1` are rejected) and matches `__version__` exactly. It publishes to PyPI via
Trusted Publishing/OIDC — no token — under the `pypi` GitHub environment.

## Architecture

### pydantic 1.x only

`pydantic>=1.7.3,<2` is a hard constraint: consumers run pydantic 1. Use v1 idioms — `@validator`,
`class Config`, `.dict()`/`.json()`/`.parse_obj()`, `Field(..., const=True)`. Do not introduce
`model_config`, `@field_validator`, or other v2 API.

### `schemas/` — two coexisting generations

- `schemas/v1.py` — legacy CDIP schemas (`Position`, `GeoEvent`, `CameraTrap`, `ERPatrol`, …).
  `schemas/__init__.py` star-imports v1 **for backward compatibility**, so `from gundi_core.schemas import X`
  yields the v1 name. v2 must be imported explicitly (`from gundi_core.schemas.v2 import X`).
- `schemas/v2/gundi.py` (~1100 lines) — the current platform-neutral core: the five payload types
  (`Observation`, `Event`, `EventUpdate`, `Attachment`, `TextMessage`), the integration/connection/route
  configuration models the portal serves, `GundiTrace`, and the dispatcher-side `DispatchedObservation`.
- `schemas/v2/{earthranger,smart,wpswatch,traptagger,inreach}.py` — per-destination payload shapes,
  i.e. what the transformer produces and each dispatcher POSTs to that third-party API.

Both generations define `StreamPrefixEnum` and `models_by_stream_type` with **different members**
(v1: `ps`/`ge`/`ct`/`er_event`…; v2: `obv`/`ev`/`evu`/`att`/`txt`). Always be explicit about which
module you are importing from.

Every v2 payload type carries `observation_type: str = Field(<prefix>, const=True)`. That const field
is the discriminator consumers rely on to identify a payload, and it is what makes `smart_union`
unions (e.g. `GundiDelivery.payload`) resolve to the right concrete class instead of first-match.

### `events/` — the EDA envelopes

`SystemEventBaseModel` (`events/core.py`) is the base for everything published on Pub/Sub. Two things
about it drive most decisions:

- `event_type` is **not a stored field** — it is a property returning `self.__class__.__name__`, injected
  into the output by the overridden `dict()`/`json()`. Consumers switch on that string, so **renaming an
  event class is a breaking wire change**, and the class name is the contract.
- `schema_version` defaults to `"v1"`; some events pin it with `const=True` (all of `batches.py`,
  plus `ObservationDeliveryFailed`/`ObservationUpdateFailed` at `"v2"`). Pinned values are gates:
  `cdip-routing` and the ER dispatcher **discard** messages whose `schema_version` doesn't match.

The modules map to producers along the pipeline:

| module | published by |
| --- | --- |
| `gundi_api.py` | the portal, on inbound data (`EventReceived`, `ObservationReceived`, …) |
| `gundi_configs.py` | the portal, on integration/action config changes |
| `transformers.py` | the transformer service, one event per (stream type × destination) |
| `dispatchers.py` | the dispatchers, on delivery success/failure |
| `integrations.py` | action runners and webhooks (execution started/complete/failed, custom logs) |
| `batches.py` | the batched observation path (see below) |
| `delivery.py` | `cdip-routing` → generic-model action runners |

`delivery.py`'s `GundiDelivery` is the envelope used when a destination integration sets
`additional.generic_model = true`: the runner receives an untransformed payload plus `ProviderInfo`
and `route_configuration`, and does the transformation itself. `ProviderInfo` is deliberately pure
identity — destination-specific values such as EarthRanger's `provider_key` are resolved by the runner
from `route_configuration`.

`commands/` mirrors the event envelopes (`SystemCommandBaseModel` subclasses `SystemEventBaseModel`);
the only difference is intent — a command asks for something to happen, e.g. `RunIntegrationAction`.

### Batch envelopes (`events/batches.py`)

A batch message carries observations sharing one data provider and stream type. The invariants are
documented in the module header and are load-bearing for the pipeline:

- Publishers emit only non-empty batches, but an empty batch must still **parse** (consumers treat it
  as a no-op) so a shrunk-to-zero envelope is never a hard failure.
- Stages may **split** or **shrink** a batch (drop items, regroup per destination) but must **never
  merge** — that is what keeps the pipeline free of buffers and flush timers.
- `ERObservationsBatch` is one `provider_key` per batch, because the ER sensors endpoint path embeds it.
- `ObservationsBatchDeliveryDetails` intentionally carries no `external_ids`: ER's bulk response has no
  reliable per-item IDs.

## Compatibility rules

Because every consumer pins a released version and old and new services run concurrently during rollout:

- **Additive only.** New fields must be `Optional` with a default. Do not rename or remove fields,
  enum members, or event/command classes — a rename is a silent break on the wire.
- Do not change a `const=True` field's value, and do not loosen/repurpose `schema_version` pins —
  downstream gates drop mismatches.
- New event types are added as new classes; new destination payloads as new modules under `schemas/v2/`.
- Tests in `tests/` are contract tests: they round-trip an event through `json()` → `parse_obj()` and
  assert on `event_type` and `schema_version`. New envelope events should get the same treatment.

## Comment and Response Rules (Strict)

### 🚫 WHAT NOT TO DO
- **No intros, no conclusions:** avoid phrases like "Here's the modified code" or "Hope this helps".
- **Do not narrate the past:** giving context on how the code used to look, or summarizing the changes you just made, is off limits.
- **Do not comment the obvious:** never explain what a standard line of code does when the syntax already says it.

### ✅ WHAT TO DO
- **Direct answers:** deliver the code or the technical solution immediately, with no preamble.
- **Critical comments only:** write a comment only when it flags a performance trade-off, a security risk, or business logic complex enough to be error-prone.
- **Absolute concision:** if code alone answers the question, add no prose around it.

In this repo that resolves to: the comments worth keeping are the ones documenting a **wire-format invariant**
(why a `const=True` value cannot move, why a batch may be split but never merged, why
`ObservationsBatchDeliveryDetails` carries no `external_ids`). The `events/batches.py` module header is the
reference for the only comment style that earns its place here.

## Mandatory Requirement: Unit Tests (pytest)

### ✅ WHAT TO DO
- **Tests with every change:** whenever you create, modify, or refactor a model, event, or command, add or update its tests.
- **Standard framework:** `pytest` (plus `pytest-asyncio` if async code ever appears), using `pytest.fixture` to build reusable payloads — see the existing `observations` / `er_items` / `provider_info` fixtures.
- **Location and naming:** under `tests/`, one file per source module prefixed `test_`, mirroring the `gundi_core/` layout (`events/batches.py` → `tests/test_batches.py`, `schemas/v2/earthranger.py` → `tests/test_earthranger.py`).
- **Serialization contract (required for every `SystemEventBaseModel`):** round-trip `json.loads(event.json())` → `parse_obj(...)`, asserting on `event_type` (the class name) and on `schema_version`. This is the test that catches an accidental rename before it breaks deployed consumers.
- **Edge cases, three families minimum:**
  1. *happy path* — full payload, intact round-trip.
  2. *invalid input* — `pytest.raises(pydantic.ValidationError)`, including an attempt to overwrite a `const=True` field (e.g. `schema_version="v2"` on an event pinned to `"v1"`).
  3. *boundary values* — optional fields absent, empty collections (an empty batch **must** parse), `None`, empty strings, autogenerated defaults (`batch_id`, `event_id`, `timestamp`).
- **Backward compatibility:** when adding a field, include a test that parses a dict *without* it — that simulates an old producer talking to a new consumer mid-rollout.
- **`smart_union` unions:** if you touch a payload `Union` (e.g. `GundiDelivery.payload`), test each member separately and assert `isinstance` against the resolved concrete class; a broken discriminator looks identical to a healthy one until it resolves to the wrong type.

### 🚫 WHAT NOT TO DO
- **Do not call a task done** without its test suite and a green `uv run pytest -q`.
- **Do not use stdlib `unittest`** unless told otherwise; prefer plain `pytest` syntax.
- **Do not leave mocks dangling:** patch external calls so tests stay deterministic. (In practice there should be none here: this is a pure model library, and a test needing network or a clock is a sign the design drifted — freeze explicit timestamps instead of using `datetime.now()`.)
- **Do not assert on `repr` or on serialized key order;** the contract is field names and values, not their arrangement.
