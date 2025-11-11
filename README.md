# Web Scraper App

A Python web scraper that fetches news articles from [Hacker News](https://news.ycombinator.com/) and stores them in a MySQL database. The app uses **Flask** for a simple web interface to display the latest news, and it supports CLI commands to manage scraping and database operations.

---

## Features

- Scrape news articles (title, link, points, date) from Hacker News
- Store data in MySQL database
- Automatically insert or update existing articles
- Flask web interface to display news
- CLI commands to manage operations:
  - Scrape news
  - Create database tables
  - Clear the database
- Unit tests for both scraper and database

---

## Requirements

- Python 3.10+
- MySQL server
- Python packages
---

## Setup

### 1. Clone the repository

```bash
git clone https://github.com/NikitaDmitrijevs/Test-task-for-Codnity-Dev.git
```

### 2. Install Python packages

Create a virtual environment and install dependencies:

```bash
python -m venv venv
```

**On Windows:**
```powershell
venv\Scripts\Activate.ps1
```

**Install requirements:**
```bash
pip install -r requirements.txt
```

### 3. Configure the database

Create a MySQL database and user, then add the connection info to `config.py`:

```python
DB_CONFIG = {
    "host": "127.0.0.1",
    "user": "YOUR_USER",
    "password": "YOUR_PASSWORD",
    "database": "YOUR_DB"
}
```

### 4. Initialize the database

Create the required tables:

```bash
flask create-tables
```

---

## Usage

### Flask CLI Commands

The app provides several Flask CLI commands for managing the scraper and database:

#### Create database tables
```bash
flask create-tables
```

#### Clear all data from the database
```bash
flask clear-db
```

#### Scrape Hacker News articles
```bash
flask scrape
```

### Start the Web Interface

Run the Flask application:

```bash
python app.py
```

Then open your browser and navigate to:
```
http://127.0.0.1:5000
```

The web interface will display the latest news articles from Hacker News.
