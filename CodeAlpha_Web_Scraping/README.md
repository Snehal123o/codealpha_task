# Book Listings — Web Scraping & EDA

## 📌 CodeAlpha Data Analytics Internship
This project was completed as part of the CodeAlpha Data Analytics Internship, covering:
- **Task 1:** Web Scraping
- **Task 2:** Exploratory Data Analysis (EDA)

## 📖 Overview
This project scrapes book listing data (title, price, rating, availability) from [books.toscrape.com](https://books.toscrape.com) — a website built specifically for scraping practice — and performs exploratory analysis to uncover pricing and rating patterns.

## 🗂️ Dataset
`books_dataset.csv` — contains scraped book data with the following columns:
- `title` — book title
- `genre` — book genre/category
- `price_gbp` — price in GBP
- `rating` — star rating (1–5)
- `availability` — stock status text
- `in_stock` — boolean stock flag

## ⚙️ Tech Stack
- Python
- Requests, BeautifulSoup (web scraping)
- Pandas
- Matplotlib, Seaborn

## 🚀 How to Run
```bash
# 1. Install dependencies
pip install pandas matplotlib seaborn

# For live scraping (Task 1)
pip install requests beautifulsoup4

# 2. Run the script
python project2_scraping_eda.py
```

To scrape fresh live data instead of using the included dataset, open `project2_scraping_eda.py` and set:
```python
USE_LIVE_SCRAPE = True
```
then re-run the script (requires an internet connection).

## 📊 What It Does
1. **Web Scraping** — extracts book title, price, rating, and stock status from paginated listing pages using BeautifulSoup.
2. **Data Cleaning** — converts price and stock fields into usable numeric/boolean types.
3. **EDA** — analyzes price distribution, rating distribution, and tests whether higher-rated books tend to cost more.
4. **Visualization** — generates charts of price and rating patterns across the catalog.

## 📁 Output Files
Running the script generates:
- `price_distribution.png` — histogram of book prices
- `rating_distribution.png` — bar chart of book ratings
- `price_vs_rating.png` — boxplot testing price vs. rating relationship
- `books_by_genre.png` — count of books per genre
- `scraped_books.csv` — freshly scraped data (only if `USE_LIVE_SCRAPE = True`)

## 💡 Key Insights
- Price and rating show little to no correlation — higher ratings don't necessarily mean higher prices.
- The majority of listed books are in stock, with only a small fraction unavailable.

## 🔗 Author
Completed as part of the CodeAlpha Data Analytics Internship.
