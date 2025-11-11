from flask import Flask, render_template
from scrape_data_from_a_website import WebScraper
from database_manager import DatabaseManager
from config import DB_CONFIG

app = Flask(__name__)

@app.cli.command("scrape")
def scrape_command():
    url = 'https://news.ycombinator.com/'
    scraper = WebScraper(url)

    html = scraper.fetch_html()
    if not html:
        app.logger.error("Scraper couldn't fetch HTML — aborting scrape.")
        return

    articles = scraper.parse_html(html)
    if not articles:
        app.logger.info("No articles parsed, nothing to insert.")
        return

    try:
        with DatabaseManager(**DB_CONFIG) as db:
            db.create_tables()
            if db.insert_or_update_news(articles):
                app.logger.info("Scrape completed and saved to DB.")
            else:
                app.logger.error("Insert/update returned False.")

    except RuntimeError as e:
        app.logger.error(f"DB connection failed: {e}")

@app.cli.command("create-tables")
def create_tables_command():
    with DatabaseManager(**DB_CONFIG) as db:
        db.create_tables()

@app.cli.command("clear-db")
def clear_db_command():
    with DatabaseManager(**DB_CONFIG) as db:
        db.clear_table()

@app.route('/')
def index():
    with DatabaseManager(**DB_CONFIG) as db:
        articles = db.load_news()
        return render_template('home.html', articles=articles)


if __name__ == '__main__':
    app.run(debug=True)