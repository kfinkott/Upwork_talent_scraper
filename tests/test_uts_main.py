#kevin fink
#kevin@shorecode.org
#test_uts_main.py
#October 18 2023

import uts_main as utsm
from unittest import TestCase
from selenium import webdriver

class TestTalentScraper(TestCase):
    def setUp(self):
        self.ts = utsm.TalentScraper()
    def test_set_url(self):
        tvalue01 = 'http://www.test.com'
        self.ts.set_url(tvalue01)
        self.assertEqual(self.ts.url, tvalue01)
    def test_get_url(self):
        tvalue01 = 'http://www.test.com'
        self.ts.url = tvalue01
        test01 = self.ts.get_url()
        self.assertEqual(test01, tvalue01)
    def test_set_query(self):
        tvalue01 = 'test query'
        self.ts.set_query(tvalue01)
        test01 = self.ts.query
        self.assertEqual(test01, tvalue01)
    def test_get_query(self):
        tvalue01 = 'test query'
        self.ts.query = tvalue01
        test01 = self.ts.get_query()
        self.assertEqual(tvalue01, test01)
    def test_get_proxies(self):
        test01 = self.ts.get_proxies()
        self.assertIsInstance(test01, list)
        self.assertIsNotNone(test01)
        self.assertGreater(len(test01), 0)
    def test_get_page_contents(self):
        self.url = 'https://www.google.com'
        test01 = self.ts.get_page_content()
        self.assertIsInstance(test01, webdriver.Firefox())
    def test_find_all_query(self):
        test01 = self.ts.find_all_query()
        self.assertIsInstance(test01, list)
        self.assertIsInstance(test01[0], list)
        self.assertIsInstance(test01[1], bool)
    def test_next_page(self):
        self.ts.original_url = 'fuckyou'
        test01 = self.ts.next_page()
        test02 = self.ts.next_page()
        test03 = self.ts.next_page()
        self.assertEqual(test01, 'fuckyou&page=2')
        self.assertEqual(test02, 'fuckyou&page=3')
        self.assertEqual(test03, 'fuckyou&page=4')
    def test_add_page_result(self):
        self.ts.result_list = [1,2,3]
        self.ts.final_result = []
        self.ts.add_page_result()
        self.assertEqual(self.ts.final_result, [1,2,3])
    def test_get_final_result(self):
        self.ts.final_result = 'test'
        test01 = self.ts.get_final_result()
        self.assertEqual(test01, 'test')
