


import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import re

sns.set(style="whitegrid")

# nltk and wordcloud are optional extras - the script still runs the core
# EDA + a simple rule-based sentiment fallback if they aren't installed.
try:
    from nltk.sentiment.vader import SentimentIntensityAnalyzer
    from nltk.corpus import stopwords
    NLTK_AVAILABLE = True
    stop_words = set(stopwords.words("english"))
except (ImportError, LookupError):
    NLTK_AVAILABLE = False
    stop_words = {"the", "a", "an", "is", "it", "this", "and", "to", "of",
                  "in", "for", "on", "was", "with", "as", "at", "i", "my"}

try:
    from wordcloud import WordCloud
    WORDCLOUD_AVAILABLE = True
except ImportError:
    WORDCLOUD_AVAILABLE = False

# ---------------------------------------------------------
# 1. LOAD DATA
# ---------------------------------------------------------
df = pd.read_csv("Reviews.csv")
print("Shape:", df.shape)
print(df.head())

# Keep only the columns we need
df = df[["Score", "Summary", "Text"]].dropna()

# ---------------------------------------------------------
# 2. CLEAN TEXT
# ---------------------------------------------------------
def clean_text(text):
    text = str(text).lower()
    text = re.sub(r"<.*?>", " ", text)          # remove HTML tags
    text = re.sub(r"[^a-z\s]", " ", text)        # keep only letters
    text = re.sub(r"\s+", " ", text).strip()
    words = [w for w in text.split() if w not in stop_words]
    return " ".join(words)

df["clean_text"] = df["Text"].apply(clean_text)
df["review_length"] = df["clean_text"].apply(lambda x: len(x.split()))

# ---------------------------------------------------------
# 3. EDA
# ---------------------------------------------------------
# 3a. Rating distribution
plt.figure(figsize=(6, 4))
sns.countplot(x="Score", data=df, palette="viridis")
plt.title("Distribution of Star Ratings")
plt.xlabel("Rating")
plt.ylabel("Count")
plt.tight_layout()
plt.savefig("rating_distribution.png")
plt.close()

# 3b. Review length vs rating
plt.figure(figsize=(6, 4))
sns.boxplot(x="Score", y="review_length", data=df, palette="coolwarm")
plt.title("Review Length by Star Rating")
plt.tight_layout()
plt.savefig("length_vs_rating.png")
plt.close()

# ---------------------------------------------------------
# 4. SENTIMENT ANALYSIS (VADER, with a simple fallback if nltk isn't installed)
# ---------------------------------------------------------
POSITIVE_WORDS = {"love", "great", "excellent", "amazing", "happy", "best",
                   "perfect", "fantastic", "satisfied", "impressed", "good"}
NEGATIVE_WORDS = {"disappointed", "terrible", "waste", "awful", "poor",
                   "worst", "useless", "regret", "bad", "broke", "damaged"}

if NLTK_AVAILABLE:
    sia = SentimentIntensityAnalyzer()

    def get_sentiment(text):
        score = sia.polarity_scores(text)["compound"]
        if score >= 0.05:
            return "Positive"
        elif score <= -0.05:
            return "Negative"
        else:
            return "Neutral"
else:
    def get_sentiment(text):
        words = set(text.split())
        pos_hits = len(words & POSITIVE_WORDS)
        neg_hits = len(words & NEGATIVE_WORDS)
        if pos_hits > neg_hits:
            return "Positive"
        elif neg_hits > pos_hits:
            return "Negative"
        else:
            return "Neutral"

df["sentiment"] = df["clean_text"].apply(get_sentiment)

print("\nSentiment counts:")
print(df["sentiment"].value_counts())

# 4a. Sentiment distribution plot
plt.figure(figsize=(6, 4))
sns.countplot(x="sentiment", data=df, order=["Positive", "Neutral", "Negative"],
              palette="Set2")
plt.title("Sentiment Distribution")
plt.tight_layout()
plt.savefig("sentiment_distribution.png")
plt.close()

# 4b. Compare sentiment vs actual star rating (sanity check)
plt.figure(figsize=(7, 5))
sns.countplot(x="Score", hue="sentiment", data=df, palette="Set1")
plt.title("Sentiment vs Star Rating")
plt.tight_layout()
plt.savefig("sentiment_vs_rating.png")
plt.close()

# ---------------------------------------------------------
# 5. WORD CLOUDS PER SENTIMENT (skipped automatically if wordcloud isn't installed)
# ---------------------------------------------------------
if WORDCLOUD_AVAILABLE:
    for label in ["Positive", "Negative"]:
        text_blob = " ".join(df[df["sentiment"] == label]["clean_text"].tolist())
        wc = WordCloud(width=800, height=400, background_color="white").generate(text_blob)
        plt.figure(figsize=(10, 5))
        plt.imshow(wc, interpolation="bilinear")
        plt.axis("off")
        plt.title(f"Most Common Words - {label} Reviews")
        plt.tight_layout()
        plt.savefig(f"wordcloud_{label.lower()}.png")
        plt.close()
else:
    print("Note: wordcloud not installed - skipping word cloud images. "
          "Run 'pip install wordcloud' to enable them.")

# ---------------------------------------------------------
# 6. SAVE FINAL DATASET
# ---------------------------------------------------------
df.to_csv("amazon_reviews_with_sentiment.csv", index=False)
print("\nDone! Charts saved as PNG files, results saved to amazon_reviews_with_sentiment.csv")
