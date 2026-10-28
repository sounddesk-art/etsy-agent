import importlib.util
import unittest
from pathlib import Path

spec=importlib.util.spec_from_file_location("r",Path(__file__).with_name("research_etsy_50.py"))
r=importlib.util.module_from_spec(spec); spec.loader.exec_module(r)

class EtsyResearchTests(unittest.TestCase):
    def test_candidate_is_never_auto_approved(self):
        row={"keyword":"wildflower wall art","series":"botanical-sun","product_type":"wall_art",
             "opportunity_score":80,"common_tags":[{"tag":"wildflower decor","count":3}],
             "common_terms":[],"competition_count":1000,"sample_top10_favorers":50,
             "recent_90d_in_top_sample":5,"score_basis":"test"}
        c=r.make_candidate(row,1)
        self.assertEqual(c["status"],"needs_human_review")
        self.assertFalse(c["etsy_upload_allowed"])
        self.assertIsNone(c["human_reviewed_at"])
        self.assertLessEqual(len(c["tags"]),13)
        self.assertTrue(all(len(x)<=20 for x in c["tags"]))

    def test_score_is_bounded(self):
        rows=[
          {"competition_count":10,"sample_top10_favorers":100,"recent_90d_in_top_sample":5},
          {"competition_count":10000,"sample_top10_favorers":10,"recent_90d_in_top_sample":1},
        ]
        r.score_rows(rows)
        self.assertTrue(all(0<=x["opportunity_score"]<=100 for x in rows))

if __name__=="__main__":
    unittest.main()
