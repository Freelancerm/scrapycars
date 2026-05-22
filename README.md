# BMW UK Approved Used Cars Scraper

A Scrapy project that scrapes used car listings from the BMW UK website and stores the data in a SQLite database.

## Prerequisites

- Python 3.10+
- SQLite3

## Setup and Run Instructions

Follow these commands in your terminal to set up the environment and run the scraper:

### 1. Create a virtual environment
```bash
python3 -m venv .venv
```

### 2. Activate the virtual environment
- **On macOS/Linux:**
  ```bash
  source .venv/bin/activate
  ```
- **On Windows:**
  ```bash
  .venv\Scripts\activate
  ```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Run the spider
This will crawl the first 5 pages and save the data to `bmw_cars.db`.
```bash
scrapy crawl bmw_api
```

### 5. Verify the results
You can check the collected data using the following SQLite commands:

- **View all records:**
  ```bash
  sqlite3 bmw_cars.db "SELECT * from car_listings;"
  ```

- **Count total records:**
  ```bash
  sqlite3 bmw_cars.db "SELECT count(*) from car_listings;"
  ```

## Features
- **Multi-page crawling:** Scrapes the first 5 result pages.
- **Deep extraction:** Navigates to individual vehicle pages for full specifications.
- **User-Agent Rotation:** Randomizes browser identity for each request to avoid blocking.
- **Data Validation & Cleaning:** Ensures required fields are present and normalizes data (e.g., lowercase fuel types, integer mileage).
- **Duplicate Handling:** Prevents duplicate entries based on the registration plate.
