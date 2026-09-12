from __future__ import annotations

import io
import json
import unittest
from contextlib import redirect_stdout

from cortex_runtime.canonical_service_status import main
from tests.runtime.runtime_test_support import assert_schema_valid


class CanonicalServiceStatusCliTests(unittest.TestCase):
    def test_cli_entrypoint_emits_canonical_schema_valid_json(self) -> None:
        # This is exactly the invocation Forge_Command spawns as a subprocess
        # (python -m cortex_runtime.canonical_service_status) -- no HTTP
        # surface, matching Cortex's CLI/file-producer-only design.
        output = io.StringIO()
        with redirect_stdout(output):
            exit_code = main([])

        result = json.loads(output.getvalue())
        assert_schema_valid(self, result, schema_name="forge_local_runtime/service-status.schema.json")
        self.assertEqual(result["service_id"], "cortex")
        self.assertEqual(exit_code, 0 if result["state"] == "ready" else 1)


if __name__ == "__main__":
    unittest.main()
