# SPAR Framework -- MICA Playbook v1.0.0

**Project ID**: spar-framework
**Mode**: protocol_evolution
**mica_spec**: 0.2.2
**Archive**: memory/spar-framework.mica.v1.0.0.json
**Invocation pattern**: readme_protocol

## Role Declaration

The AI operates as **SPAR Framework Architect**.

## Identity

SPAR is a deterministic admissibility-review framework.

It reviews three things:

- anchor consistency
- interpretation scope
- maturity / gap-state alignment

The core package is domain-agnostic. Domain adapters provide analytical anchors,
scope rules, and registry seed data.

The first adapter package is `spar_domain_physics`. It keeps the physics
contract surface out of the framework core now that the standalone extraction
is complete.

## Current Goal

Maintain the standalone review kernel and keep the physics adapter as the first
proof case without re-coupling TOE-specific contracts into the framework core.

The next milestone is to extend the adapter surface without diluting the core
contract boundary:

- `spar_framework`
- `spar_domain_physics`
- `scientific-model` adapters that keep their domain contracts outside the core

## Design Constraints

- keep snapshot emission first-class
- keep scoring explicit
- no free-form LLM judge in the core
- do not market the framework as a universal truth engine
