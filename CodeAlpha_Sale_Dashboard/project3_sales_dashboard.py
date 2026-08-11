

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

sns.set(style="whitegrid")

# Interactive Plotly dashboard is optional - only runs if plotly is installed
try:
    import plotly.express as px
    PLOTLY_AVAILABLE = True
except ImportError:
    PLOTLY_AVAILABLE = False
    print("Note: plotly not installed - skipping interactive HTML dashboards. "
          "Run 'pip install plotly' to enable them.")

# ---------------------------------------------------------
# 1. LOAD DATA
# ---------------------------------------------------------
df = pd.read_csv("Superstore.csv")
df["Order Date"] = pd.to_datetime(df["Order Date"])
df["Year"] = df["Order Date"].dt.year
df["Month"] = df["Order Date"].dt.month_name()

print("Shape:", df.shape)
print(df.head())

# ---------------------------------------------------------
# 2. EDA
# ---------------------------------------------------------
print("\nSales summary:")
print(df["Sales"].describe())

print("\nTotal sales by region:")
print(df.groupby("Region")["Sales"].sum().sort_values(ascending=False))

# ---------------------------------------------------------
# 3. STATIC VISUALIZATIONS (Matplotlib / Seaborn)
# ---------------------------------------------------------

# 3a. Sales trend over time
monthly_sales = df.groupby(df["Order Date"].dt.to_period("M"))["Sales"].sum()
plt.figure(figsize=(12, 5))
monthly_sales.plot(kind="line", marker="o", color="teal")
plt.title("Monthly Sales Trend")
plt.ylabel("Total Sales ($)")
plt.xlabel("Month")
plt.tight_layout()
plt.savefig("monthly_sales_trend.png")
plt.close()

# 3b. Sales by category
plt.figure(figsize=(7, 4))
sns.barplot(x="Category", y="Sales", data=df, estimator=sum, errorbar=None,
            palette="viridis")
plt.title("Total Sales by Category")
plt.tight_layout()
plt.savefig("sales_by_category.png")
plt.close()

# 3c. Sales by region (bar)
plt.figure(figsize=(7, 4))
sns.barplot(x="Region", y="Sales", data=df, estimator=sum, errorbar=None,
            palette="magma")
plt.title("Total Sales by Region")
plt.tight_layout()
plt.savefig("sales_by_region.png")
plt.close()

# 3d. Top 10 sub-categories by profit
top_profit = df.groupby("Sub-Category")["Profit"].sum().sort_values(ascending=False).head(10)
plt.figure(figsize=(8, 5))
sns.barplot(x=top_profit.values, y=top_profit.index, palette="crest")
plt.title("Top 10 Sub-Categories by Profit")
plt.xlabel("Total Profit ($)")
plt.tight_layout()
plt.savefig("top_profit_subcategories.png")
plt.close()

# 3e. Sales vs Profit scatter (discount impact)
plt.figure(figsize=(7, 5))
sns.scatterplot(x="Discount", y="Profit", data=df, hue="Category", alpha=0.6)
plt.title("Discount Impact on Profit")
plt.tight_layout()
plt.savefig("discount_vs_profit.png")
plt.close()

# ---------------------------------------------------------
# 4. INTERACTIVE DASHBOARD (Plotly) - saved as standalone HTML
# ---------------------------------------------------------
if PLOTLY_AVAILABLE:
    fig1 = px.line(monthly_sales.reset_index().astype({"Order Date": str}),
                   x="Order Date", y="Sales", title="Monthly Sales Trend (Interactive)")

    fig2 = px.bar(df.groupby("Region", as_index=False)["Sales"].sum(),
                  x="Region", y="Sales", title="Sales by Region (Interactive)",
                  color="Region")

    fig3 = px.treemap(df, path=["Category", "Sub-Category"], values="Sales",
                       title="Sales Breakdown by Category / Sub-Category")

    fig1.write_html("dashboard_sales_trend.html")
    fig2.write_html("dashboard_sales_by_region.html")
    fig3.write_html("dashboard_sales_treemap.html")
    print("\nInteractive HTML dashboards saved - open the .html files in a browser.")

print("\nDone! Static PNG charts saved in this folder.")
