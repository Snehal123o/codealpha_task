

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

sns.set(style="whitegrid")

st.set_page_config(page_title="Book Listings Dashboard", layout="wide")

st.title("📚 Book Listings — Web Scraping & EDA Dashboard")
st.caption("CodeAlpha Data Analytics Internship — Task 1 (Web Scraping) + Task 2 (EDA)")

# ---------------------------------------------------------
# LOAD DATA
# ---------------------------------------------------------
@st.cache_data
def load_data():
    df = pd.read_csv("books_dataset.csv")
    df["in_stock"] = df["availability"].str.contains("In stock")
    df = df.dropna(subset=["rating"])
    return df

df = load_data()

# ---------------------------------------------------------
# SIDEBAR FILTERS
# ---------------------------------------------------------
st.sidebar.header("Filters")
genres = st.sidebar.multiselect(
    "Genre",
    options=sorted(df["genre"].unique()),
    default=sorted(df["genre"].unique())
)
ratings = st.sidebar.multiselect(
    "Rating",
    options=sorted(df["rating"].unique()),
    default=sorted(df["rating"].unique())
)
price_range = st.sidebar.slider(
    "Price Range (£)",
    float(df["price_gbp"].min()), float(df["price_gbp"].max()),
    (float(df["price_gbp"].min()), float(df["price_gbp"].max()))
)

filtered_df = df[
    df["genre"].isin(genres) &
    df["rating"].isin(ratings) &
    df["price_gbp"].between(price_range[0], price_range[1])
]

# ---------------------------------------------------------
# TOP METRICS
# ---------------------------------------------------------
col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Books", len(filtered_df))
col2.metric("Avg Price", f"£{filtered_df['price_gbp'].mean():.2f}")
col3.metric("Avg Rating", f"{filtered_df['rating'].mean():.2f} ⭐")
col4.metric("In Stock %", f"{filtered_df['in_stock'].mean()*100:.1f}%")

st.divider()

# ---------------------------------------------------------
# CHARTS
# ---------------------------------------------------------
c1, c2 = st.columns(2)

with c1:
    st.subheader("Price Distribution")
    fig, ax = plt.subplots(figsize=(5, 4))
    sns.histplot(filtered_df["price_gbp"], bins=20, kde=True, color="steelblue", ax=ax)
    st.pyplot(fig)

with c2:
    st.subheader("Rating Distribution")
    fig, ax = plt.subplots(figsize=(5, 4))
    sns.countplot(x="rating", data=filtered_df, palette="magma", ax=ax)
    st.pyplot(fig)

c3, c4 = st.columns(2)

with c3:
    st.subheader("Price by Rating")
    fig, ax = plt.subplots(figsize=(5, 4))
    sns.boxplot(x="rating", y="price_gbp", data=filtered_df, palette="coolwarm", ax=ax)
    st.pyplot(fig)

with c4:
    st.subheader("Books by Genre")
    fig, ax = plt.subplots(figsize=(5, 4))
    filtered_df["genre"].value_counts().plot(kind="barh", color="seagreen", ax=ax)
    ax.set_xlabel("Count")
    st.pyplot(fig)

st.divider()

# ---------------------------------------------------------
# DATA TABLE
# ---------------------------------------------------------
st.subheader("Filtered Books")
st.dataframe(filtered_df[["title", "genre", "price_gbp", "rating", "availability"]],
             use_container_width=True)
