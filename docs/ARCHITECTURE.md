# SPAR Framework Architecture

The extracted framework should have one job: review whether a result deserves
the claim attached to it.

## Core Layers

### Layer A

Checks output against declared analytical anchors supplied by a domain adapter.

### Layer B

Checks whether report language and declared status stay within the adapter's
scope rules.

### Layer C

Checks implementation maturity and gap-state classification using registry
objects and emitted snapshots.

## Core Packages

- `core`
- `registry`
- `interfaces`
- `spar_domain_physics` as the first adapter seed package

## Out of Scope for Core

- physics-specific contracts
- TOE API routers
- TOE biological sidecars
- any domain-specific analytical source tables

## First Extraction Boundary

The first real split is now visible in code:

- `spar_framework`
  - generic result model
  - generic scoring model
  - generic review runtime
  - generic registry snapshot model
- `spar_domain_physics`
  - physics model seeds
  - physics gap seeds
  - physics analytical anchor table
  - initial Layer A adapter builder
  - initial Layer B deterministic scope checks
  - initial Layer C existence probes
  - runtime factory that wires the adapter into the generic kernel

The next extraction step is the TOE integration pass: replace TOE-local SPAR
wiring so it consumes `spar_framework` and `spar_domain_physics` instead of
duplicating core review logic.
