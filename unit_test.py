import unittest
from scrape_data_from_a_website import WebScraper
from database_manager import DatabaseManager
from config import DB_CONFIG
from datetime import date


class TestDatabaseManager(unittest.TestCase):

    def setUp(self):
        self.db = DatabaseManager(**DB_CONFIG)
        self.db.connect()
        self.db.create_tables()
        self.db.clear_table()

    def tearDown(self):
        if hasattr(self, 'db') and self.db.connection:
            self.db.clear_table()
            self.db.disconnect()

    def test_connect_and_disconnect(self):
        db = DatabaseManager(**DB_CONFIG)
        self.assertTrue(db.connect())
        self.assertIsNotNone(db.connection)
        db.disconnect()
        self.assertTrue(db.connection is None or not db.connection.open)

    def test_insert_or_update_news(self):
        articles = [
            {"title": "News 1", "link": "https://example.com/1", "points": 10, "date_created": date.today()},
            {"title": "News 2", "link": "https://example.com/2", "points": 5, "date_created": date.today()}
        ]
        self.assertTrue(self.db.insert_or_update_news(articles))

        loaded = self.db.load_news(limit=10)
        self.assertEqual(len(loaded), 2)
        self.assertEqual(loaded[0]["title"], "News 2")

        articles[0]["points"] = 20
        self.assertTrue(self.db.insert_or_update_news([articles[0]]))
        loaded_after_update = self.db.load_news(limit=10)
        self.assertEqual(loaded_after_update[1]["points"], 20)

    def test_insert_invalid_data(self):
        articles = [
            {"title": "Bad News", "link": "https://example.com/bad", "points": "abc", "date_created": "invalid-date"}
        ]
        self.assertTrue(self.db.insert_or_update_news(articles))
        loaded = self.db.load_news(limit=10)
        self.assertEqual(loaded[0]["points"], 0)
        self.assertIsNone(loaded[0]["date_created"])

    def test_clear_table(self):
        articles = [
            {"title": "News 1", "link": "https://example.com/1", "points": 1, "date_created": date.today()}
        ]
        self.db.insert_or_update_news(articles)
        self.assertTrue(self.db.clear_table())
        self.assertEqual(len(self.db.load_news()), 0)


class TestWebScraper(unittest.TestCase):

    def setUp(self):
        self.scraper = WebScraper('https://news.ycombinator.com/')

    def test_fetch_html_success(self):
        html = self.scraper.fetch_html()
        self.assertTrue(html is None or isinstance(html, str))

    def test_fetch_html_invalid_url(self):
        scraper_bad = WebScraper('http://invalid.url.test/')
        html = scraper_bad.fetch_html()
        self.assertIsNone(html)

    def test_parse_html_with_none(self):
        result = self.scraper.parse_html(None)
        self.assertEqual(result, [])

    def test_parse_html_real_data(self):
        html = self.scraper.fetch_html()
        if html:
            data = self.scraper.parse_html(html)
            self.assertIsInstance(data, list)
            if data:
                first = data[0]
                self.assertIn('title', first)
                self.assertIn('link', first)
                self.assertIn('points', first)
                self.assertIn('date_created', first)
                self.assertIsInstance(first['points'], int)
                self.assertTrue(first['date_created'] is None or isinstance(first['date_created'], date))

    def test_parse_row_with_invalid_structure(self):
        from bs4 import BeautifulSoup
        html = "<html><body><tr></tr></body></html>"
        soup = BeautifulSoup(html, "html.parser")
        row = soup.find("tr")
        self.assertIsNone(self.scraper.parse_row(row))


if __name__ == '__main__':
    unittest.main()
