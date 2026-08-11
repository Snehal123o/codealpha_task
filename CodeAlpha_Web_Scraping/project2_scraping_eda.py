

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

sns.set(style="whitegrid")

USE_LIVE_SCRAPE = False   # set to True if you want to scrape fresh data yourself
DATA_FILE = "books_dataset.csv"

# ---------------------------------------------------------
# 1. WEB SCRAPING FUNCTION (Task 1) - run this yourself with internet access
# ---------------------------------------------------------
def scrape_books(num_pages=20):
    import requests
    from bs4 import BeautifulSoup
    import re
    import time

    BASE_URL = "https://books.toscrape.com/catalogue/page-{}.html"
    RATING_MAP = {"One": 1, "Two": 2, "Three": 3, "Four": 4, "Five": 5}
    records = []

    for page in range(1, num_pages + 1):
        url = BASE_URL.format(page)
        resp = requests.get(url)
        if resp.status_code != 200:
            break

        soup = BeautifulSoup(resp.text, "html.parser")
        articles = soup.find_all("article", class_="product_pod")

        for art in articles:
            title = art.h3.a["title"]
            price_text = art.find("p", class_="price_color").text
            price = float(re.sub(r"[^\d.]", "", price_text))
            availability = art.find("p", class_="instock availability").text.strip()
            rating_class = art.find("p", class_="star-rating")["class"][1]
            rating = RATING_MAP.get(rating_class, None)

            records.append({
                "title": title,
                "price_gbp": price,
                "availability": availability,
                "rating": rating
            })
        time.sleep(0.5)  # be polite to the server

    return pd.DataFrame(records)


# ---------------------------------------------------------
# 2. LOAD DATA - either scrape fresh or use the ready-made CSV
# ---------------------------------------------------------
if USE_LIVE_SCRAPE:
    print("Scraping books.toscrape.com ...")
    df = scrape_books(num_pages=20)
    df.to_csv("scraped_books.csv", index=False)
else:
    print(f"Loading ready-made dataset: {DATA_FILE}")
    df = pd.read_csv(DATA_FILE)

print(f"Loaded {len(df)} books")
print(df.head())

# ---------------------------------------------------------
# 3. CLEAN DATA
# ---------------------------------------------------------
df["in_stock"] = df["availability"].str.contains("In stock")
df = df.dropna(subset=["rating"])

# ---------------------------------------------------------
# 4. EDA (Task 2)
# ---------------------------------------------------------
print("\nBasic stats:")
print(df["price_gbp"].describe())

# 4a. Price distribution
plt.figure(figsize=(7, 4))
sns.histplot(df["price_gbp"], bins=20, kde=True, color="steelblue")
plt.title("Distribution of Book Prices (£)")
plt.tight_layout()
plt.savefig("price_distribution.png")
plt.close()

# 4b. Rating distribution
plt.figure(figsize=(6, 4))
sns.countplot(x="rating", data=df, palette="magma")
plt.title("Distribution of Book Ratings")
plt.tight_layout()
plt.savefig("rating_distribution.png")
plt.close()

# 4c. Price vs Rating (hypothesis: higher rated books cost more?)
plt.figure(figsize=(6, 4))
sns.boxplot(x="rating", y="price_gbp", data=df, palette="coolwarm")
plt.title("Price by Rating (Testing: Do higher-rated books cost more?)")
plt.tight_layout()
plt.savefig("price_vs_rating.png")
plt.close()

# 4d. Correlation check
corr = df[["price_gbp", "rating"]].corr()
print("\nCorrelation between price and rating:")
print(corr)

# 4e. Genre breakdown (only present if using the ready-made dataset)
if "genre" in df.columns:
    plt.figure(figsize=(8, 5))
    df["genre"].value_counts().plot(kind="barh", color="seagreen")
    plt.title("Number of Books by Genre")
    plt.xlabel("Count")
    plt.tight_layout()
    plt.savefig("books_by_genre.png")
    plt.close()

# 4f. Stock availability
print("\nIn-stock vs out-of-stock:")
print(df["in_stock"].value_counts())

print("\nDone! Charts saved as PNG files in this folder.")
