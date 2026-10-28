import json
import tempfile
import unittest
from pathlib import Path
from review_gate import require_reviewed, review_errors, validate_manifest

class ReviewGateTests(unittest.TestCase):
    def good(self):
        return {
            "id":"x","status":"approved",
            "human_reviewed_at":"2026-10-28T12:00:00Z",
            "human_reviewed_by":"owner",
            "human_prompt_or_notes":"Reviewed composition, text, uniqueness and commercial suitability."
        }

    def test_unreviewed_generated_item_is_blocked(self):
        item={"id":"x","status":"needs_human_review"}
        self.assertTrue(review_errors(item))
        with self.assertRaises(RuntimeError):
            require_reviewed(item)

    def test_all_review_fields_required(self):
        item=self.good()
        del item["human_prompt_or_notes"]
        self.assertIn("human_prompt_or_notes is required",review_errors(item))

    def test_explicit_review_passes(self):
        self.assertTrue(require_reviewed(self.good()))

    def test_manifest_validation(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/"m.json"
            p.write_text(json.dumps({"items":[self.good(),{"id":"bad","status":"approved"}]}))
            items,failures=validate_manifest(p)
            self.assertEqual(len(items),2)
            self.assertEqual(len(failures),1)

if __name__=="__main__":
    unittest.main()
