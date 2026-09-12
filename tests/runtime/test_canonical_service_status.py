from __future__ import annotations

import unittest

from cortex_runtime.canonical_service_status import (
    _CANONICAL_ALLOWED_KEYS,
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
        # narrower shape.
        own = emit_service_status()
        canonical = build_canonical_service_status_envelope()
        self.assertEqual(canonical["service_id"], own["service_id"])
        self.assertEqual(canonical["service_class"], own["service_class"])
        self.assertEqual(canonical["state"], own["state"])
        self.assertEqual(canonical["readiness_summary"], own["readiness_summary"])
        self.assertEqual(canonical["operator_visible_message"], own["operator_visible_message"])
        self.assertEqual(canonical.get("degraded_subtype"), own.get("degraded_subtype"))
