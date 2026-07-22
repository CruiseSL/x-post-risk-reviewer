import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "moderate_posts.py"


def run_runner(*args: str, stdin: str | None = None) -> dict:
    completed = subprocess.run(
        [sys.executable, str(SCRIPT), *args, "--output", "-"],
        input=stdin,
        text=True,
        capture_output=True,
        check=True,
        cwd=ROOT,
    )
    return json.loads(completed.stdout)


class ModeratePostsTest(unittest.TestCase):
    def test_benign_text_passes_without_fake_open_source_usage(self) -> None:
        result = run_runner(
            "--text",
            "One missing layer in current AI Agent implementations is durable context.",
        )

        post = result["posts"][0]
        execution = result["detector_execution"]
        self.assertEqual(post["decision_hint"], "PASS")
        self.assertEqual(post["flags"], [])
        self.assertEqual(len(post["detector_trace"]["rules_evaluated"]), 14)
        self.assertEqual(execution["open_source_components_used"], [])
        self.assertEqual(execution["project_authored_components_used"], ["builtin-rules"])

    def test_targeted_threat_has_traceable_rule(self) -> None:
        result = run_runner("--text", "I will kill you @target")

        post = result["posts"][0]
        self.assertEqual(post["decision_hint"], "STOP")
        self.assertEqual(post["flags"][0]["rule_id"], "builtin.violence.targeted_threat_en")
        self.assertEqual(post["flags"][0]["rule_source"], "project_authored")
        self.assertIn("kill you", post["flags"][0]["evidence"])

    def test_duplicate_batch_reports_batch_rule(self) -> None:
        records = [
            {"id": "one", "text": "The same launch announcement with enough text for duplicate matching."},
            {"id": "two", "text": "The same launch announcement with enough text for duplicate matching."},
        ]
        with tempfile.TemporaryDirectory() as temp_dir:
            input_path = Path(temp_dir) / "posts.json"
            input_path.write_text(json.dumps(records), encoding="utf-8")
            result = run_runner("--input", str(input_path))

        self.assertEqual(result["batch_signals"]["exact_duplicate_groups"], [["one", "two"]])
        for post in result["posts"]:
            self.assertEqual(post["decision_hint"], "STOP")
            self.assertIn("builtin.authenticity.exact_duplicate", post["detector_trace"]["matched_rule_ids"])

    def test_stdin_input_is_supported(self) -> None:
        result = run_runner("--stdin", stdin="A plain text post with no link or media.")
        self.assertEqual(result["metadata"]["input_source"], "stdin")
        self.assertEqual(result["posts"][0]["decision_hint"], "PASS")

    def test_registry_and_tool_versions_match(self) -> None:
        result = run_runner("--text", "Version check")
        self.assertEqual(result["metadata"]["tool_version"], "0.2.0")
        self.assertEqual(result["metadata"]["detector_registry_version"], "0.2.0")
        self.assertEqual(result["metadata"]["policy_snapshot_reviewed_at"], "2026-07-22")


if __name__ == "__main__":
    unittest.main()
