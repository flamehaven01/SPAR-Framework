"""Adapter interfaces for standalone SPAR."""

from __future__ import annotations

from typing import Any, Protocol

from .result_types import CheckResult


class LayerABuilder(Protocol):
    def __call__(
        self,
        *,
        subject: Any,
        source: str,
        gate: str,
        params: dict[str, Any],
    ) -> list[CheckResult]: ...


class LayerBBuilder(Protocol):
    def __call__(
        self,
        *,
        subject: Any,
        source: str,
        gate: str,
        report_text: str,
    ) -> list[CheckResult]: ...


class LayerCBuilder(Protocol):
    def __call__(
        self,
        *,
        subject: Any,
        source: str,
        gate: str,
        params: dict[str, Any],
    ) -> list[CheckResult]: ...


class RegistrySnapshotBuilder(Protocol):
    def __call__(self) -> dict[str, Any] | None: ...


class SlopChecker(Protocol):
    def __call__(self, report_text: str) -> tuple[int, list[str]]: ...
