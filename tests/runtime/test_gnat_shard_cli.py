from __future__ import annotations

import contextlib
import copy
import io
import json
import tempfile
import unittest
import unittest.mock
from pathlib import Path

from cortex_runtime.gnats import GnatSourceInput, plan_gnat_run
from cortex_runtime.gnats.shard_cli import main
from tests.runtime.runtime_test_support import ROOT, assert_schema_valid, capture_cli_result


GNAT_FIXTURE_DIR = ROOT / "tests/runtime/fixtures/gnats/text-batch-small"
MARKDOWN_FIXTURE = GNAT_FIXTURE_DIR / "chapter-01.md"
TEXT_FIXTURE = GNAT_FIXTURE_DIR / "note-plain.txt"
EMPTY_TEXT_FIXTURE = ROOT / "tests/runtime/fixtures/sample-empty.txt"


def _write_shard_json(shard, directory: Path) -> Path:
    shard_path = directory / f"{shard.shard_id}.json"
    shard_path.write_text(json.dumps(shard.to_contract()), encoding="utf-8")
    return shard_path


class GnatShardCliRuntimeTests(unittest.TestCase):
    def test_cli_runs_a_markdown_shard_and_prints_a_complete_receipt(self) -> None:
        plan = plan_gnat_run(
            [GnatSourceInput(MARKDOWN_FIXTURE, media_type="text/markdown", source_ref="chapter-01")],
            request_id="gnat-shard-cli-markdown",
        )
        shard = plan.shards[0]

        with tempfile.TemporaryDirectory() as tmpdir:
            shard_path = _write_shard_json(shard, Path(tmpdir))
            exit_code, receipt = capture_cli_result(
                main, [str(shard_path), "--local-path", str(shard.local_path)]
            )

        self.assertEqual(exit_code, 0)
        assert_schema_valid(self, receipt, schema_name="gnat-worker-receipt.schema.json")
        self.assertEqual(receipt["state"], "complete")
        self.assertEqual(receipt["shard_id"], shard.shard_id)
        self.assertEqual(receipt["worker_type"], "markdown_syntax")

    def test_cli_runs_a_plain_text_shard_and_prints_a_complete_receipt(self) -> None:
        plan = plan_gnat_run(
            [GnatSourceInput(TEXT_FIXTURE, media_type="text/plain", source_ref="note-plain")],
            request_id="gnat-shard-cli-plain-text",
        )
        shard = plan.shards[0]

        with tempfile.TemporaryDirectory() as tmpdir:
            shard_path = _write_shard_json(shard, Path(tmpdir))
            exit_code, receipt = capture_cli_result(
                main, [str(shard_path), "--local-path", str(shard.local_path)]
            )

        self.assertEqual(exit_code, 0)
        assert_schema_valid(self, receipt, schema_name="gnat-worker-receipt.schema.json")
        self.assertEqual(receipt["state"], "complete")
        self.assertEqual(receipt["worker_type"], "plain_text_syntax")

    def test_cli_reads_shard_json_from_stdin(self) -> None:
        plan = plan_gnat_run(
            [GnatSourceInput(MARKDOWN_FIXTURE, media_type="text/markdown", source_ref="chapter-01")],
            request_id="gnat-shard-cli-stdin",
        )
        shard = plan.shards[0]

        stdout = io.StringIO()
        with unittest.mock.patch("sys.stdin", io.StringIO(json.dumps(shard.to_contract()))):
            with contextlib.redirect_stdout(stdout):
                exit_code = main(["-", "--local-path", str(shard.local_path)])

        self.assertEqual(exit_code, 0)
        receipt = json.loads(stdout.getvalue())
        assert_schema_valid(self, receipt, schema_name="gnat-worker-receipt.schema.json")
        self.assertEqual(receipt["state"], "complete")

    def test_cli_rejects_a_worker_type_outside_the_proving_slice(self) -> None:
        plan = plan_gnat_run(
            [GnatSourceInput(MARKDOWN_FIXTURE, media_type="text/markdown", source_ref="chapter-01")],
            request_id="gnat-shard-cli-out-of-slice",
        )
        shard_contract = copy.deepcopy(plan.shards[0].to_contract())
        shard_contract["worker_type"] = "pdf_text_syntax"

        with tempfile.TemporaryDirectory() as tmpdir:
            shard_path = Path(tmpdir) / "out-of-slice.json"
            shard_path.write_text(json.dumps(shard_contract), encoding="utf-8")

            stderr = io.StringIO()
            with contextlib.redirect_stderr(stderr):
                exit_code = main([str(shard_path), "--local-path", str(plan.shards[0].local_path)])

        self.assertEqual(exit_code, 1)
        self.assertIn("DECISIONS/0018", stderr.getvalue())
        self.assertIn("pdf_text_syntax", stderr.getvalue())

    def test_cli_rejects_malformed_shard_json(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            shard_path = Path(tmpdir) / "malformed.json"
            shard_path.write_text("{not valid json", encoding="utf-8")

            stderr = io.StringIO()
            with contextlib.redirect_stderr(stderr):
                exit_code = main([str(shard_path), "--local-path", str(Path(tmpdir) / "unused.txt")])

        self.assertEqual(exit_code, 1)
        self.assertTrue(stderr.getvalue().startswith("error:"))

    def test_cli_reports_a_denied_shard_with_nonzero_exit_but_a_full_receipt(self) -> None:
        plan = plan_gnat_run(
            [GnatSourceInput(EMPTY_TEXT_FIXTURE, media_type="text/plain", source_ref="empty-text")],
            request_id="gnat-shard-cli-denied",
        )
        shard = plan.shards[0]

        with tempfile.TemporaryDirectory() as tmpdir:
            shard_path = _write_shard_json(shard, Path(tmpdir))
            exit_code, receipt = capture_cli_result(
                main, [str(shard_path), "--local-path", str(shard.local_path)]
            )

        self.assertEqual(exit_code, 1)
        assert_schema_valid(self, receipt, schema_name="gnat-worker-receipt.schema.json")
        self.assertEqual(receipt["state"], "denied")


if __name__ == "__main__":
    unittest.main()
