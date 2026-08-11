
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

sns.set(style="whitegrid")

st.set_page_config(page_title="Retail Sales Dashboard", layout="wide")

st.title("🛒 Retail Sales — Visualization Dashboard")
st.caption("CodeAlpha Data Analytics Internship — Task 2 (EDA) + Task 3 (Data Visualization)")

# ---------------------------------------------------------
# LOAD DATA
# ---------------------------------------------------------
@st.cache_data
def load_data():
    df = pd.read_csv("Superstore.csv")
    df["Order Date"] = pd.to_datetime(df["Order Date"])
    df["Year"] = df["Order Date"].dt.year
    df["Month"] = df["Order Date"].dt.to_period("M").astype(str)
    return df

df = load_data()

# ---------------------------------------------------------
# SIDEBAR FILTERS
# ---------------------------------------------------------
st.sidebar.header("Filters")
regions = st.sidebar.multiselect(
    "Region", options=sorted(df["Region"].unique()), default=sorted(df["Region"].unique())
)
categories = st.sidebar.multiselect(
    "Category", options=sorted(df["Category"].unique()), default=sorted(df["Category"].unique())
)
years = st.sidebar.multiselect(
    "Year", options=sorted(df["Year"].unique()), default=sorted(df["Year"].unique())
)

filtered_df = df[
    df["Region"].isin(regions) &
    df["Category"].isin(categories) &
    df["Year"].isin(years)
]

# ---------------------------------------------------------
# TOP METRICS
# ---------------------------------------------------------
col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Sales", f"${filtered_df['Sales'].sum():,.0f}")
col2.metric("Total Profit", f"${filtered_df['Profit'].sum():,.0f}")
col3.metric("Orders", len(filtered_df))
col4.metric("Avg Discount", f"{filtered_df['Discount'].mean()*100:.1f}%")

st.divider()

# ---------------------------------------------------------
# CHARTS
# ---------------------------------------------------------
st.subheader("Monthly Sales Trend")
monthly_sales = filtered_df.groupby("Month")["Sales"].sum().reset_index()
fig, ax = plt.subplots(figsize=(12, 4))
ax.plot(monthly_sales["Month"], monthly_sales["Sales"], marker="o", color="teal")
ax.set_xticks(range(0, len(monthly_sales), max(1, len(monthly_sales)//12)))
ax.set_xticklabels(monthly_sales["Month"][::max(1, len(monthly_sales)//12)], rotation=45)
ax.set_ylabel("Total Sales ($)")
st.pyplot(fig)

c1, c2 = st.columns(2)

with c1:
    st.subheader("Sales by Category")
    fig, ax = plt.subplots(figsize=(5, 4))
    sns.barplot(x="Category", y="Sales", data=filtered_df, estimator=sum, errorbar=None,
                palette="viridis", ax=ax)
    st.pyplot(fig)

with c2:
    st.subheader("Sales by Region")
    fig, ax = plt.subplots(figsize=(5, 4))
    sns.barplot(x="Region", y="Sales", data=filtered_df, estimator=sum, errorbar=None,
                palette="magma", ax=ax)
    st.pyplot(fig)

c3, c4 = st.columns(2)

with c3:
    st.subheader("Top 10 Sub-Categories by Profit")
    top_profit = filtered_df.groupby("Sub-Category")["Profit"].sum().sort_values(ascending=False).head(10)
    fig, ax = plt.subplots(figsize=(6, 5))
    sns.barplot(x=top_profit.values, y=top_profit.index, palette="crest", ax=ax)
    ax.set_xlabel("Total Profit ($)")
    st.pyplot(fig)

with c4:
    st.subheader("Discount Impact on Profit")
    fig, ax = plt.subplots(figsize=(6, 5))
    sns.scatterplot(x="Discount", y="Profit", data=filtered_df, hue="Category", alpha=0.6, ax=ax)
    st.pyplot(fig)

st.divider()

# ---------------------------------------------------------
# DATA TABLE
# ---------------------------------------------------------
st.subheader("Filtered Transactions")
st.dataframe(
    filtered_df[["Order ID", "Order Date", "Region", "Category", "Sub-Category",
                 "Sales", "Discount", "Profit"]],
    use_container_width=True
)
