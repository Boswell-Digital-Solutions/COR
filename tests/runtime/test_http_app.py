from __future__ import annotations

import unittest

from fastapi.testclient import TestClient

from cortex_runtime.http_app import app
from tests.runtime.runtime_test_support import assert_schema_valid


class HttpAppTests(unittest.TestCase):
    def setUp(self) -> None:
        self.client = TestClient(app)

    def test_service_status_route_returns_canonical_schema_valid_envelope(self) -> None:
        response = self.client.get("/health/service-status")
        self.assertEqual(response.status_code, 200)
        body = response.json()
        assert_schema_valid(self, body, schema_name="forge_local_runtime/service-status.schema.json")
        self.assertEqual(body["service_id"], "cortex")
        self.assertEqual(body["service_class"], "file_intelligence")

    def test_app_exposes_exactly_one_route(self) -> None:
        # CONTROL_SURFACE.md: bounded by design -- adding a second route is a
        # new decision, not an extension of this one. FastAPI auto-adds
        # /openapi.json, /docs, /redoc, /docs/oauth2-redirect; only one route
        # is application-defined.
        auto_routes = {"/openapi.json", "/docs", "/redoc", "/docs/oauth2-redirect"}
        app_routes = [r.path for r in app.routes if r.path not in auto_routes]
        self.assertEqual(app_routes, ["/health/service-status"])
