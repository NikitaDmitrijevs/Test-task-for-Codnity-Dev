import requests
from bs4 import BeautifulSoup
from datetime import datetime
import logging

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(levelname)s:%(name)s:%(message)s")


class WebScraper:
    def __init__(self, url, timeout=5):
        self.url = url
        self.timeout = timeout

        self.headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/122.0 Safari/537.36"
            )
        }

    def fetch_html(self):
        try:
            response = requests.get(
                self.url,
                headers=self.headers,
                timeout=self.timeout
            )

            response.raise_for_status()
            logger.info(f"Connected: {self.url}")

            return response.text

        except requests.exceptions.RequestException as e:
            logger.error(f"HTTP request failed: {e}")
            return None

    def parse_html(self, html):
        if html is None:
            logger.error("Cannot parse: HTML is None")
            return []

        soup = BeautifulSoup(html, "html.parser")
        rows = soup.find_all("tr", class_="athing")

        results = []
        for row in rows:
            item = self.parse_row(row)
            if item:
                results.append(item)

        logger.info(f"Parsed {len(results)} news items")

        return results

    def parse_row(self, row):
        try:
            title_tag = row.find("span", class_="titleline").find("a")
            title = title_tag.text.strip()
            link = title_tag["href"]

            next_row = row.find_next_sibling("tr")
            if not next_row:
                return None

            points_raw = next_row.find("span", class_="score")
            points = int(points_raw.text.replace(" points", "")) if points_raw else 0

            age_span = next_row.find("span", class_="age")
            if age_span and "title" in age_span.attrs:
                date_created = self.normalize_date(age_span["title"])

            else:
                date_created = None

            return {
                "title": title,
                "link": link,
                "points": points,
                "date_created": date_created,
            }

        except Exception as e:
            logger.error(f"Failed to parse row: {e}")
            return None

    def normalize_date(self, raw_date):
        try:
            dt = datetime.strptime(raw_date.split()[0], "%Y-%m-%dT%H:%M:%S")
            return dt.date()

        except Exception as e:
            logger.error(f"Failed to parse date '{raw_date}': {e}")
            return None


if __name__ == "__main__":
    scraper = WebScraper("https://news.ycombinator.com/")
    html = scraper.fetch_html()
    data = scraper.parse_html(html)

    print(f"\nFound {len(data)} news:")
    for item in data:
        print(item)
