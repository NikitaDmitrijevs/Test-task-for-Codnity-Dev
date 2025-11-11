import pymysql
from pymysql import OperationalError, MySQLError
from typing import List, Dict, Optional
import logging
from contextlib import contextmanager
from datetime import datetime, date
from config import DB_CONFIG

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(levelname)s:%(name)s:%(message)s")


class DatabaseManager:

    def __init__(self, host: str, user: str, password: str, database: str):
        self.host = host
        self.user = user
        self.password = password
        self.database = database
        self.connection: Optional[pymysql.connections.Connection] = None

    def connect(self, debug: bool = False) -> bool:
        if debug:
            logger.setLevel(logging.DEBUG)

        if not all([self.host, self.user, self.password, self.database]):
            logger.error("DB connect failed: missing connection parameters.")
            return False

        try:
            self.connection = pymysql.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                database=self.database,
            )
            logger.debug("Successfully connected to DB")
            return True

        except OperationalError as e:
            logger.exception(f"Operational error connecting to DB: {e}")
            return False

        except MySQLError as e:
            logger.exception(f"MySQL error connecting to DB: {e}")
            return False

        except Exception as e:
            logger.exception(f"Unexpected error connecting to DB: {e}")
            return False

    def disconnect(self) -> None:

        try:
            if self.connection and self.connection.open:
                self.connection.close()
                logger.debug("DB connection closed.")

        except Exception:
            logger.exception("Error while disconnecting from DB.")

    def __enter__(self):
        ok = self.connect()

        if not ok:
            raise RuntimeError("Failed to connect to DB")
        return self

    def __exit__(self, exc_type, exc, tb):

        try:
            if exc_type:
                if self.connection:
                    self.connection.rollback()
                    logger.debug("Transaction rolled back due to exception.")
            else:
                if self.connection and self.connection.open:
                    self.connection.commit()
                    logger.debug("Transaction committed.")
        finally:
            self.disconnect()

    @contextmanager
    def cursor(self):
        if not self.connection:
            raise RuntimeError("No active DB connection")
        cur = self.connection.cursor()

        try:
            yield cur

        finally:
            cur.close()

    def create_tables(self) -> bool:

        sql = """
        CREATE TABLE IF NOT EXISTS news (
            id INT AUTO_INCREMENT PRIMARY KEY,
            title VARCHAR(255) NOT NULL,
            link VARCHAR(512) NOT NULL,
            points INT DEFAULT 0,
            date_created DATE,
            UNIQUE KEY uq_link (link)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
        """

        try:
            with self.cursor() as cur:
                cur.execute(sql)
            logger.info("Table has been successfully created.")
            return True

        except MySQLError:
            logger.exception("Error while creating table.")
            return False

    def insert_or_update_news(self, articles: List[Dict]) -> bool:

        if not articles:
            logger.info("No articles to insert.")
            return True

        insert_sql = """
        INSERT INTO news (title, link, points, date_created)
        VALUES (%s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE
            title = VALUES(title),
            points = VALUES(points),
            date_created = VALUES(date_created)
        """

        params = []
        for a in articles:
            points = a.get("points", 0)
            try:
                points = int(points)
            except (ValueError, TypeError):
                points = 0

            date_val = a.get("date_created")
            if isinstance(date_val, (datetime, date)):
                date_val = date_val.strftime("%Y-%m-%d")
            else:
                try:
                    date_obj = datetime.strptime(str(date_val), "%Y-%m-%d")
                    date_val = date_obj.strftime("%Y-%m-%d")
                except Exception:
                    date_val = None

            params.append((
                a.get("title"),
                a.get("link"),
                points,
                date_val
            ))

        try:
            with self.cursor() as cur:
                cur.executemany(insert_sql, params)
            logger.info("Inserted/Updated %d articles", len(params))
            return True

        except MySQLError:
            logger.exception("Error while inserting/updating news.")
            return False

    def clear_table(self) -> bool:

        try:
            with self.cursor() as cur:
                cur.execute("TRUNCATE TABLE news")
            logger.info("Table cleared successfully.")
            return True

        except MySQLError:
            logger.exception("Error while clearing table.")
            return False

    def load_news(self, limit: int = 100) -> List[Dict]:

        try:
            with self.cursor() as cur:
                cur.execute(
                    "SELECT id, title, link, points, DATE_FORMAT(date_created, '%%Y-%%m-%%d') "
                    "FROM news ORDER BY id DESC LIMIT %s",
                    (limit,)
                )
                rows = cur.fetchall()
                result = []
                for r in rows:
                    result.append({
                        "id": r[0],
                        "title": r[1],
                        "link": r[2],
                        "points": r[3],
                        "date_created": r[4]
                    })
                return result

        except MySQLError:
            logger.exception("Error while loading news.")
            return []

if __name__ == "__main__":

    db = DatabaseManager(**DB_CONFIG)
    db.connect(debug=True)
    db.create_tables()

    test_articles = [
        {
            "title": "Test News 1",
            "link": "https://example.com/1",
            "points": 42,
            "date_created": "2024-01-15"
        },
        {
            "title": "Test News 2",
            "link": "https://example.com/2",
            "points": 17,
            "date_created": "2024-01-20"
        }
    ]
    db.insert_or_update_news(test_articles)

    loaded = db.load_news(limit=10)
    print(loaded)

    db.clear_table()
    db.disconnect()



