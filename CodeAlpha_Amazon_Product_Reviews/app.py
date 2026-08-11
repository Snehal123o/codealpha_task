

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import re

sns.set(style="whitegrid")

st.set_page_config(page_title="Amazon Reviews Sentiment Dashboard", layout="wide")

st.title("📦 Amazon Product Reviews — Sentiment Analysis Dashboard")
st.caption("CodeAlpha Data Analytics Internship — Task 2 (EDA) + Task 4 (Sentiment Analysis)")

# ---------------------------------------------------------
# LOAD DATA
# ---------------------------------------------------------
@st.cache_data
def load_data():
    df = pd.read_csv("Reviews.csv")
    df = df[["Score", "Summary", "Text", "ProductCategory"]].dropna()

    def clean_text(text):
        text = str(text).lower()
        text = re.sub(r"<.*?>", " ", text)
        text = re.sub(r"[^a-z\s]", " ", text)
        text = re.sub(r"\s+", " ", text).strip()
        return text

    df["clean_text"] = df["Text"].apply(clean_text)
    df["review_length"] = df["clean_text"].apply(lambda x: len(x.split()))

    POSITIVE_WORDS = {"love", "great", "excellent", "amazing", "happy", "best",
                       "perfect", "fantastic", "satisfied", "impressed", "good"}
    NEGATIVE_WORDS = {"disappointed", "terrible", "waste", "awful", "poor",
                       "worst", "useless", "regret", "bad", "broke", "damaged"}

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
    return df

df = load_data()

# ---------------------------------------------------------
# SIDEBAR FILTERS
# ---------------------------------------------------------
st.sidebar.header("Filters")
categories = st.sidebar.multiselect(
    "Product Category",
    options=sorted(df["ProductCategory"].unique()),
    default=sorted(df["ProductCategory"].unique())
)
ratings = st.sidebar.multiselect(
    "Star Rating",
    options=sorted(df["Score"].unique()),
    default=sorted(df["Score"].unique())
)

filtered_df = df[df["ProductCategory"].isin(categories) & df["Score"].isin(ratings)]

# ---------------------------------------------------------
# TOP METRICS
# ---------------------------------------------------------
col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Reviews", len(filtered_df))
col2.metric("Positive %", f"{(filtered_df['sentiment']=='Positive').mean()*100:.1f}%")
col3.metric("Negative %", f"{(filtered_df['sentiment']=='Negative').mean()*100:.1f}%")
col4.metric("Avg Rating", f"{filtered_df['Score'].mean():.2f} ⭐")

st.divider()

# ---------------------------------------------------------
# CHARTS
# ---------------------------------------------------------
c1, c2 = st.columns(2)

with c1:
    st.subheader("Rating Distribution")
    fig, ax = plt.subplots(figsize=(5, 4))
    sns.countplot(x="Score", data=filtered_df, palette="viridis", ax=ax)
    st.pyplot(fig)

with c2:
    st.subheader("Sentiment Distribution")
    fig, ax = plt.subplots(figsize=(5, 4))
    sns.countplot(x="sentiment", data=filtered_df,
                  order=["Positive", "Neutral", "Negative"], palette="Set2", ax=ax)
    st.pyplot(fig)

c3, c4 = st.columns(2)

with c3:
    st.subheader("Review Length by Rating")
    fig, ax = plt.subplots(figsize=(5, 4))
    sns.boxplot(x="Score", y="review_length", data=filtered_df, palette="coolwarm", ax=ax)
    st.pyplot(fig)

with c4:
    st.subheader("Sentiment vs Star Rating")
    fig, ax = plt.subplots(figsize=(5, 4))
    sns.countplot(x="Score", hue="sentiment", data=filtered_df, palette="Set1", ax=ax)
    st.pyplot(fig)

st.divider()

# ---------------------------------------------------------
# DATA TABLE
# ---------------------------------------------------------
st.subheader("Filtered Reviews")
st.dataframe(filtered_df[["ProductCategory", "Score", "Summary", "sentiment"]], use_container_width=True)
