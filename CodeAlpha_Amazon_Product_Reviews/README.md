# Amazon Product Reviews — Sentiment Analysis & EDA

## 📌 CodeAlpha Data Analytics Internship
This project was completed as part of the CodeAlpha Data Analytics Internship, covering:
- **Task 2:** Exploratory Data Analysis (EDA)
- **Task 4:** Sentiment Analysis

## 📖 Overview
This project analyzes Amazon product reviews to understand customer sentiment and rating patterns. It cleans raw review text, explores the dataset structure, classifies each review as **Positive**, **Negative**, or **Neutral**, and visualizes the results.

## 🗂️ Dataset
`Reviews.csv` — contains product reviews with the following columns:
- `Score` — star rating (1–5)
- `Summary` — short review headline
- `Text` — full review text
- `ProductCategory` — product category

## ⚙️ Tech Stack
- Python
- Pandas, NumPy
- Matplotlib, Seaborn
- NLTK (VADER Sentiment Analyzer)
- WordCloud

## 🚀 How to Run
```bash
# 1. Install dependencies
pip install pandas numpy matplotlib seaborn

# Optional, for full sentiment analysis + word clouds
pip install nltk wordcloud
python -m nltk.downloader vader_lexicon stopwords

# 2. Run the script
python project1_sentiment_eda.py
```

## 📊 What It Does
1. **Data Cleaning** — removes HTML tags, punctuation, and stopwords from review text.
2. **EDA** — analyzes distribution of star ratings and review length by rating.
3. **Sentiment Classification** — uses NLTK's VADER to classify each review's compound sentiment score as Positive, Negative, or Neutral.
4. **Visualization** — generates charts comparing sentiment against actual star ratings, plus word clouds of the most common words in positive vs. negative reviews.

## 📁 Output Files
Running the script generates:
- `rating_distribution.png` — bar chart of star ratings
- `length_vs_rating.png` — boxplot of review length by rating
- `sentiment_distribution.png` — count of Positive/Negative/Neutral reviews
- `sentiment_vs_rating.png` — comparison of predicted sentiment vs. actual star rating
- `wordcloud_positive.png` / `wordcloud_negative.png` — most frequent words per sentiment
- `amazon_reviews_with_sentiment.csv` — final dataset with sentiment labels added

## 💡 Key Insights
- Most reviews with 4–5 star ratings were classified as Positive, validating the sentiment model against real ratings.
- Common words in positive reviews center on quality, value, and satisfaction; negative reviews center on disappointment, defects, and poor service.

## 🔗 Author
Completed as part of the CodeAlpha Data Analytics Internship.
