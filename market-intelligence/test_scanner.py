import csv,tempfile,unittest
from pathlib import Path
from scanner import init,ingest,rank
class Tests(unittest.TestCase):
 def setUp(self):
  self.temp=tempfile.TemporaryDirectory();self.db=init(":memory:")
 def tearDown(self):self.db.close();self.temp.cleanup()
 def load(self,kind,fields,rows):
  p=Path(self.temp.name)/"data.csv"
  with p.open("w",newline="") as f:
   w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(rows)
  ingest(self.db,p,kind)
 def test_no_fake_demand(self):
  self.load("observations",["keyword","source","searches","competition"],[dict(keyword="test",source="other",searches=5000,competition=2)])
  self.assertIsNone(next(x for x in rank(self.db) if x["keyword"]=="test")["score"])
 def test_verified(self):
  self.load("observations",["keyword","source","searches","competition"],[dict(keyword="test",source="etsy_insights",searches=500,competition=200)])
  self.assertGreater(next(x for x in rank(self.db) if x["keyword"]=="test")["score"],0)
 def test_invalid_funnel(self):
  with self.assertRaises(ValueError):
   self.load("performance",["keyword","impressions","clicks","orders"],[dict(keyword="test",impressions=1,clicks=2,orders=0)])
 def test_negative_trend(self):
  self.load("observations",["keyword","source","searches","competition","trend"],[dict(keyword="test",source="etsy_insights",searches=500,competition=200,trend=-35)])
  self.assertIsNotNone(next(x for x in rank(self.db) if x["keyword"]=="test")["score"])
 def test_old_data_not_verified(self):
  self.load("observations",["keyword","source","observed_at","searches","competition"],[dict(keyword="test",source="etsy_insights",observed_at="2020-01-01",searches=500,competition=200)])
  self.assertIsNone(next(x for x in rank(self.db) if x["keyword"]=="test")["score"])
 def test_profit(self):
  self.load("performance",["keyword","impressions","clicks","orders","revenue","fees"],[dict(keyword="test",impressions=100,clicks=10,orders=2,revenue=7,fees=3)])
  self.assertEqual(next(x for x in rank(self.db) if x["keyword"]=="test")["net_revenue"],4)
if __name__=="__main__":unittest.main()
