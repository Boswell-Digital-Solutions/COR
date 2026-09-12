from __future__ import annotations

import unittest
from unittest.mock import patch

from cortex_runtime.canonical_service_status import (
    _CANONICAL_ALLOWED_KEYS,
    _DEGRADED_SUBTYPE_TO_CANONICAL,
    CanonicalServiceStatusError,
    build_canonical_service_status_envelope,
)
from cortex_runtime.service_status import emit_service_status
from tests.runtime.runtime_test_support import assert_schema_valid


class CanonicalServiceStatusTests(unittest.TestCase):
    def test_projected_envelope_is_canonical_schema_valid(self) -> None:
        envelope = build_canonical_service_status_envelope()
        assert_schema_valid(
            self,
            envelope,
            schema_name="forge_local_runtime/service-status.schema.json",
        )

    def test_projection_carries_only_canonical_allowed_keys(self) -> None:
        # COR's own richer envelope (runtime_surface_summary/watcher_summary/
        # gnat_summary) must never leak into the canonical projection -- the
        # canonical schema is additionalProperties: false and doesn't define them.
        envelope = build_canonical_service_status_envelope()
        self.assertTrue(set(envelope.keys()).issubset(_CANONICAL_ALLOWED_KEYS))
        self.assertNotIn("runtime_surface_summary", envelope)
        self.assertNotIn("watcher_summary", envelope)
        self.assertNotIn("gnat_summary", envelope)

    def test_projection_reflects_the_same_real_state_as_the_own_envelope(self) -> None:
        # Never a fabricated or divergent value -- same underlying truth,
        # narrower shape. degraded_subtype is checked separately below since
        # its VALUE is remapped, not passed through verbatim.
        own = emit_service_status()
        canonical = build_canonical_service_status_envelope()
        self.assertEqual(canonical["service_id"], own["service_id"])
        self.assertEqual(canonical["service_class"], own["service_class"])
        self.assertEqual(canonical["state"], own["state"])
        self.assertEqual(canonical["readiness_summary"], own["readiness_summary"])
        self.assertEqual(canonical["operator_visible_message"], own["operator_visible_message"])

    def _own_degraded_dependency_unavailable_envelope(self) -> dict[str, object]:
        # A real shape emit_service_status() produces today
        # (service_status.py's only degraded_subtype-setting branch,
        # "missing_slices"), reproduced directly rather than via indirect
        # mocking of slice-counting internals -- that path also runs through
        # COR's OWN schema validation and safe-fallback logic, which has its
        # own environment-dependent branches unrelated to what this test
        # covers (the canonical remapping).
        own = emit_service_status()
        degraded = dict(own)
        degraded["state"] = "degraded"
        degraded["degraded_subtype"] = "dependency_unavailable"
        degraded["readiness_summary"] = {"readiness_class": "degraded", "summary": "test"}
        return degraded

    def test_degraded_dependency_unavailable_is_remapped_to_canonical_name(self) -> None:
        # Regression test for the real CI failure this mapping fixes: COR's own
        # degraded_subtype vocabulary is a DIFFERENT enum than the canonical
        # one (shared key, different values).
        own_degraded = self._own_degraded_dependency_unavailable_envelope()
        with patch(
            "cortex_runtime.canonical_service_status.emit_service_status",
            return_value=own_degraded,
        ):
            canonical = build_canonical_service_status_envelope()

        self.assertEqual(canonical["state"], "degraded")
        self.assertEqual(
            canonical["degraded_subtype"],
            _DEGRADED_SUBTYPE_TO_CANONICAL["dependency_unavailable"],
        )
        assert_schema_valid(
            self,
            canonical,
            schema_name="forge_local_runtime/service-status.schema.json",
        )

    def test_unmapped_degraded_subtype_fails_closed_rather_than_forwarding(self) -> None:
        own_degraded = self._own_degraded_dependency_unavailable_envelope()
        with patch("cortex_runtime.canonical_service_status._DEGRADED_SUBTYPE_TO_CANONICAL", {}):
            with patch(
                "cortex_runtime.canonical_service_status.emit_service_status",
                return_value=own_degraded,
            ):
                with self.assertRaises(CanonicalServiceStatusError):
                    build_canonical_service_status_envelope()
