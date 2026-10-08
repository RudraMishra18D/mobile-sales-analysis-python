import streamlit as st
import pandas as pd
import plotly.express as px

# =========================================================
# PAGE SETTINGS
# =========================================================

st.set_page_config(
    page_title="Mobile Sales Dashboard",
    page_icon="📱",
    layout="wide"
)

# =========================================================
# LOAD EXCEL DATA
# =========================================================

@st.cache_data
def load_data():

    file_path = "Data/Mobile Sales Data.xlsx"

    df = pd.read_excel(file_path)

    # Revenue
    df["Revenue"] = df["Units Sold"] * df["Price Per Unit"]

    # Create Date
    df["Date"] = pd.to_datetime(
        dict(
            year=df["Year"],
            month=df["Month"],
            day=df["Day"]
        ),
        errors="coerce"
    )

    return df


# Load data
df = load_data()


# =========================================================
# TITLE
# =========================================================

st.title("📱 Mobile Sales Dashboard")

st.markdown(
    "### Interactive Mobile Sales Analysis"
)

st.divider()


# =========================================================
# SIDEBAR FILTERS
# =========================================================

st.sidebar.header("🔎 Dashboard Filters")

# Year
years = sorted(df["Year"].dropna().unique())

selected_years = st.sidebar.multiselect(
    "📅 Select Year",
    years,
    default=years
)

# Brand
brands = sorted(df["Brand"].dropna().unique())

selected_brands = st.sidebar.multiselect(
    "🏷️ Select Brand",
    brands,
    default=brands
)

# City
cities = sorted(df["City"].dropna().unique())

selected_cities = st.sidebar.multiselect(
    "🏙️ Select City",
    cities,
    default=cities
)

# Payment
payments = sorted(df["Payment Method"].dropna().unique())

selected_payments = st.sidebar.multiselect(
    "💳 Payment Method",
    payments,
    default=payments
)


# =========================================================
# FILTER DATA
# =========================================================

filtered_df = df[
    (df["Year"].isin(selected_years))
    &
    (df["Brand"].isin(selected_brands))
    &
    (df["City"].isin(selected_cities))
    &
    (df["Payment Method"].isin(selected_payments))
].copy()


# =========================================================
# CHECK EMPTY DATA
# =========================================================

if filtered_df.empty:

    st.warning(
        "⚠️ No data available for the selected filters."
    )

    st.stop()


# =========================================================
# KPI CALCULATIONS
# =========================================================

total_revenue = filtered_df["Revenue"].sum()

total_units = filtered_df["Units Sold"].sum()

total_transactions = filtered_df["Transaction ID"].nunique()

average_order_value = (
    total_revenue / total_transactions
    if total_transactions > 0
    else 0
)

average_rating = filtered_df["Customer Ratings"].mean()


# =========================================================
# KPI CARDS
# =========================================================

st.subheader("📊 Key Performance Indicators")

col1, col2, col3, col4, col5 = st.columns(5)

col1.metric(
    "💰 Total Revenue",
    f"₹{total_revenue:,.0f}"
)

col2.metric(
    "📦 Units Sold",
    f"{total_units:,.0f}"
)

col3.metric(
    "🧾 Transactions",
    f"{total_transactions:,}"
)

col4.metric(
    "🛒 Avg Order Value",
    f"₹{average_order_value:,.0f}"
)

col5.metric(
    "⭐ Avg Rating",
    f"{average_rating:.2f}/5"
)


st.divider()


# =========================================================
# REVENUE TREND
# =========================================================

st.subheader("📈 Revenue Trend")

daily_sales = (
    filtered_df
    .groupby("Date", as_index=False)["Revenue"]
    .sum()
    .sort_values("Date")
)

fig_revenue = px.line(
    daily_sales,
    x="Date",
    y="Revenue",
    markers=True,
    title="Revenue Over Time"
)

fig_revenue.update_layout(
    xaxis_title="Date",
    yaxis_title="Revenue (₹)",
    hovermode="x unified"
)

st.plotly_chart(
    fig_revenue,
    use_container_width=True
)


# =========================================================
# BRAND + CITY
# =========================================================

col1, col2 = st.columns(2)


# ---------------- BRAND ----------------

with col1:

    st.subheader("🏷️ Revenue by Brand")

    brand_sales = (
        filtered_df
        .groupby("Brand", as_index=False)
        .agg(
            Revenue=("Revenue", "sum"),
            Units=("Units Sold", "sum")
        )
        .sort_values(
            "Revenue",
            ascending=False
        )
    )

    fig_brand = px.bar(
        brand_sales,
        x="Brand",
        y="Revenue",
        text_auto=".2s",
        color="Brand",
        title="Brand-wise Revenue"
    )

    fig_brand.update_layout(
        showlegend=False,
        xaxis_title="Brand",
        yaxis_title="Revenue (₹)"
    )

    st.plotly_chart(
        fig_brand,
        use_container_width=True
    )


# ---------------- CITY ----------------

with col2:

    st.subheader("🏙️ Top Cities")

    city_sales = (
        filtered_df
        .groupby("City", as_index=False)["Revenue"]
        .sum()
        .sort_values(
            "Revenue",
            ascending=False
        )
        .head(10)
    )

    fig_city = px.bar(
        city_sales.sort_values("Revenue"),
        x="Revenue",
        y="City",
        orientation="h",
        text_auto=".2s",
        color="Revenue",
        title="Top 10 Cities by Revenue"
    )

    fig_city.update_layout(
        xaxis_title="Revenue (₹)",
        yaxis_title="City"
    )

    st.plotly_chart(
        fig_city,
        use_container_width=True
    )


# =========================================================
# PAYMENT + MOBILE MODELS
# =========================================================

col1, col2 = st.columns(2)


# ---------------- PAYMENT METHOD ----------------

with col1:

    st.subheader("💳 Payment Methods")

    payment_sales = (
        filtered_df
        .groupby("Payment Method")
        .agg(
            Transactions=("Transaction ID", "nunique"),
            Revenue=("Revenue", "sum")
        )
        .reset_index()
    )

    fig_payment = px.pie(
        payment_sales,
        names="Payment Method",
        values="Transactions",
        hole=0.45,
        title="Transactions by Payment Method"
    )

    st.plotly_chart(
        fig_payment,
        use_container_width=True
    )


# ---------------- MOBILE MODELS ----------------

with col2:

    st.subheader("📱 Top Mobile Models")

    model_sales = (
        filtered_df
        .groupby("Mobile Model", as_index=False)["Units Sold"]
        .sum()
        .sort_values(
            "Units Sold",
            ascending=False
        )
        .head(10)
    )

    fig_models = px.bar(
        model_sales.sort_values("Units Sold"),
        x="Units Sold",
        y="Mobile Model",
        orientation="h",
        text_auto=True,
        color="Units Sold",
        title="Top 10 Models by Units Sold"
    )

    fig_models.update_layout(
        xaxis_title="Units Sold",
        yaxis_title="Mobile Model"
    )

    st.plotly_chart(
        fig_models,
        use_container_width=True
    )


# =========================================================
# CUSTOMER RATINGS
# =========================================================

st.subheader("⭐ Customer Rating Analysis")

rating_data = (
    filtered_df
    .groupby("Customer Ratings")
    .agg(
        Customers=("Transaction ID", "nunique"),
        Revenue=("Revenue", "sum")
    )
    .reset_index()
    .sort_values("Customer Ratings")
)

fig_rating = px.bar(
    rating_data,
    x="Customer Ratings",
    y="Customers",
    text_auto=True,
    color="Customer Ratings",
    title="Customer Rating Distribution"
)

fig_rating.update_layout(
    xaxis_title="Customer Rating",
    yaxis_title="Number of Customers"
)

st.plotly_chart(
    fig_rating,
    use_container_width=True
)


# =========================================================
# AGE ANALYSIS
# =========================================================

st.subheader("👥 Customer Age Analysis")

age_bins = [
    0,
    18,
    25,
    35,
    45,
    55,
    65,
    100
]

age_labels = [
    "<18",
    "18-25",
    "26-35",
    "36-45",
    "46-55",
    "56-65",
    "65+"
]

age_df = filtered_df.copy()

age_df["Age Group"] = pd.cut(
    age_df["Customer Age"],
    bins=age_bins,
    labels=age_labels,
    include_lowest=True
)

age_sales = (
    age_df
    .groupby(
        "Age Group",
        observed=False
    )
    .agg(
        Customers=("Transaction ID", "nunique"),
        Revenue=("Revenue", "sum")
    )
    .reset_index()
)

fig_age = px.bar(
    age_sales,
    x="Age Group",
    y="Revenue",
    text_auto=".2s",
    color="Age Group",
    title="Revenue by Customer Age Group"
)

fig_age.update_layout(
    xaxis_title="Age Group",
    yaxis_title="Revenue (₹)",
    showlegend=False
)

st.plotly_chart(
    fig_age,
    use_container_width=True
)


# =========================================================
# TOP PERFORMING MODELS TABLE
# =========================================================

st.subheader("🏆 Top Performing Mobile Models")

top_models = (
    filtered_df
    .groupby(
        ["Brand", "Mobile Model"],
        as_index=False
    )
    .agg(
        Units_Sold=("Units Sold", "sum"),
        Revenue=("Revenue", "sum"),
        Avg_Rating=("Customer Ratings", "mean")
    )
    .sort_values(
        "Revenue",
        ascending=False
    )
    .head(15)
)

top_models["Revenue"] = top_models["Revenue"].round(0)

top_models["Avg_Rating"] = (
    top_models["Avg_Rating"]
    .round(2)
)

st.dataframe(
    top_models,
    use_container_width=True,
    hide_index=True
)


# =========================================================
# FILTERED DATA
# =========================================================

with st.expander("📄 View Complete Filtered Data"):

    st.dataframe(
        filtered_df,
        use_container_width=True,
        hide_index=True
    )


# =========================================================
# FOOTER
# =========================================================

st.divider()

st.success(
    "🎉 Mobile Sales Dashboard loaded successfully!"
)

st.caption(
    "Built with Python • Streamlit • Pandas • Plotly"
)