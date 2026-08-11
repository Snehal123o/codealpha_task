# Retail Sales — Data Visualization Dashboard

## 📌 CodeAlpha Data Analytics Internship
This project was completed as part of the CodeAlpha Data Analytics Internship, covering:
- **Task 2:** Exploratory Data Analysis (EDA)
- **Task 3:** Data Visualization

## 📖 Overview
This project analyzes retail sales transaction data to uncover trends across time, region, category, and profitability, and presents the findings through both static charts and an interactive dashboard.

## 🗂️ Dataset
`Superstore.csv` — contains retail sales transactions with the following columns:
- `Order ID`, `Order Date`
- `Region`, `Segment`
- `Category`, `Sub-Category`
- `Sales`, `Quantity`, `Discount`, `Profit`

## ⚙️ Tech Stack
- Python
- Pandas
- Matplotlib, Seaborn
- Plotly (optional, for interactive dashboard)

## 🚀 How to Run
```bash
# 1. Install dependencies
pip install pandas matplotlib seaborn

# Optional, for interactive HTML dashboard
pip install plotly

# 2. Run the script
python project3_sales_dashboard.py
```

## 📊 What It Does
1. **EDA** — summarizes overall sales statistics and breaks down total sales by region.
2. **Visualization** — builds charts for monthly sales trends, sales by category/region, top profitable sub-categories, and the impact of discounts on profit.
3. **Interactive Dashboard** (if Plotly installed) — generates standalone HTML dashboards for sales trends, regional sales, and a category/sub-category treemap.

## 📁 Output Files
Running the script generates:
- `monthly_sales_trend.png` — line chart of sales over time
- `sales_by_category.png` — bar chart of total sales per category
- `sales_by_region.png` — bar chart of total sales per region
- `top_profit_subcategories.png` — top 10 most profitable sub-categories
- `discount_vs_profit.png` — scatter plot showing how discounts affect profit
- `dashboard_sales_trend.html`, `dashboard_sales_by_region.html`, `dashboard_sales_treemap.html` — interactive dashboards (open directly in a browser)

## 💡 Key Insights
- Sales are fairly evenly distributed across regions, with the West and South showing slightly higher totals.
- Higher discounts are associated with reduced (and sometimes negative) profit margins, highlighting a discounting risk.
- A small set of sub-categories account for a disproportionate share of total profit.

## 🔗 Author
Completed as part of the CodeAlpha Data Analytics Internship.
