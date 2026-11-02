import unittest
from etsy_sales import aggregate_transactions,collect,money
class EtsySalesTests(unittest.TestCase):
 def test_money(self):
  self.assertEqual(money({"amount":1234,"divisor":100}),12.34)
 def test_dedup_and_mapping(self):
  rows=[{"transaction_id":11,"listing_id":55,"quantity":2,"price":{"amount":299,"divisor":100,"currency_code":"USD"}},{"transaction_id":11,"listing_id":55,"quantity":2,"price":{"amount":299,"divisor":100,"currency_code":"USD"}},{"transaction_id":12,"listing_id":99,"quantity":1,"price":{"amount":900,"divisor":100,"currency_code":"USD"}}]
  x=aggregate_transactions(rows,{"55":"botanical"})
  self.assertEqual(len(x),1);self.assertEqual(x[0]["units"],2);self.assertAlmostEqual(x[0]["revenue"],5.98)
 def test_paginated_sales(self):
  calls=[]
  def fake(url,headers):
   calls.append(url)
   if "offset=0" in url:return {"count":101,"results":[{"transaction_id":i+1,"listing_id":55,"quantity":1,"price":{"amount":100,"divisor":100,"currency_code":"USD"}} for i in range(100)]}
   return {"count":101,"results":[{"transaction_id":101,"listing_id":55,"quantity":1,"price":{"amount":100,"divisor":100,"currency_code":"USD"}}]}
  result=collect(123,"key:secret","token",{"55":"botanical"},fetch=fake)
  self.assertEqual(result[0]["orders"],101);self.assertEqual(len(calls),2)
if __name__=="__main__":unittest.main()
