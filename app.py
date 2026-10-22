
from pathlib import Path
import pandas as pd
import plotly.express as px
import streamlit as st

st.set_page_config(
    page_title="E-Commerce Product Analysis",
    page_icon=" ",
    layout="wide"
)

DATA = Path(__file__).parent / "data"
ORANGE = "#F28C28"

if "dark" not in st.session_state:
    st.session_state.dark = True

with st.sidebar:
    st.title("E-Commerce Analytics")
    st.toggle("Night mode", key="dark")
    page = st.radio(
        "NAVIGATION",
        ["Home", "Overview", "Products",
         "Country Analysis", "Monthly Analysis", "About"]
    )

dark = st.session_state.dark
bg = "#111315" if dark else "#F5F7FA"
panel = "#1B1F22" if dark else "#FFFFFF"
fg = "#FFFFFF" if dark else "#20252B"
grid = "#454B50" if dark else "#DDE2E8"

st.markdown(f"""
<style>
.stApp {{background:{bg}; color:{fg};}}
[data-testid="stSidebar"] {{background:{panel};}}
.block-container {{padding-top:2rem;}}
div[data-testid="stMetric"] {{
background:{panel}; border:1px solid {grid};
padding:16px; border-radius:12px;
}}
.hero {{
background:{panel}; border:1px solid {ORANGE};
border-radius:18px; padding:35px; margin-bottom:20px;
}}
</style>
""", unsafe_allow_html=True)

@st.cache_data
def load_csv(filename):
    return pd.read_csv(DATA / filename)

def clean_columns(df):
    df = df.copy()
    df.columns = [
        str(c).strip().lower().replace(" ", "_")
        for c in df.columns
    ]
    aliases = {
        "stockcode": "stock_code",
        "product": "description",
        "product_name": "description",
        "revenue": "total_revenue",
        "sales": "total_revenue",
        "quantity": "total_quantity",
        "qty": "total_quantity",
        "country_name": "country",
        "invoicemonth": "month",
        "invoice_month": "month",
        "month_name": "month",
        "avg_price": "average_price",
        "transaction_count": "transactions"
    }
    return df.rename(
        columns={c: aliases[c] for c in df.columns if c in aliases}
    )

products = clean_columns(load_csv("products_summary.csv"))
countries = clean_columns(load_csv("country_summary.csv"))
monthly = clean_columns(load_csv("monthly_summary.csv"))

for df in [products, countries, monthly]:
    for col in ["total_revenue", "total_quantity",
                "average_price", "transactions"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

def chart(fig, height=420):
    fig.update_layout(
        height=height,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor=panel,
        font_color=fg,
        margin=dict(l=15, r=15, t=55, b=20)
    )
    fig.update_xaxes(gridcolor=grid)
    fig.update_yaxes(gridcolor=grid)
    return fig

def money(n):
    return f"£{n:,.2f}"

if page == "Home":
    st.markdown("""
    <div class="hero">
    <h4 style="color:#F28C28">E-COMMERCE INTELLIGENCE</h4>
    <h1>Smarter Insights.<br>Stronger Decisions.</h1>
    <p>Explore product performance, country sales and monthly
    revenue trends through interactive analytics.</p>
    </div>
    """, unsafe_allow_html=True)

    a, b, c = st.columns(3)
    a.metric("Products analysed", len(products))
    b.metric("Countries analysed", len(countries))
    c.metric("Months analysed", len(monthly))

    st.subheader("Explore your data")
    st.write("Choose Overview, Products, Country Analysis or "
             "Monthly Analysis from the navigation menu.")

elif page == "Overview":
    st.title("Business Overview")

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Total revenue", money(
        products["total_revenue"].sum()
        if "total_revenue" in products else 0))
    m2.metric("Quantity sold", f"{products['total_quantity'].sum():,.0f}"
        if "total_quantity" in products else "N/A")
    m3.metric("Products", len(products))
    m4.metric("Countries", len(countries))

    if {"description", "total_revenue"}.issubset(products.columns):
        top = products.nlargest(10, "total_revenue").sort_values(
            "total_revenue")
        fig = px.bar(top, x="total_revenue", y="description",
            orientation="h", title="Top 10 Products by Revenue",
            color_discrete_sequence=[ORANGE])
        st.plotly_chart(chart(fig, 480), use_container_width=True)

    if {"country", "total_revenue"}.issubset(countries.columns):
        top = countries.nlargest(10, "total_revenue").sort_values(
            "total_revenue")
        fig = px.bar(top, x="total_revenue", y="country",
            orientation="h", title="Top 10 Countries by Revenue",
            color_discrete_sequence=[ORANGE])
        st.plotly_chart(chart(fig, 450), use_container_width=True)

    if {"month", "total_revenue"}.issubset(monthly.columns):
        fig = px.line(monthly.sort_values("month"), x="month",
            y="total_revenue", markers=True,
            title="Monthly Revenue Trend",
            color_discrete_sequence=[ORANGE])
        st.plotly_chart(chart(fig), use_container_width=True)

elif page == "Products":
    st.title("Product Analysis")
    if "description" not in products.columns:
        st.error("Could not find the product description column.")
        st.stop()

    search = st.text_input("Search products")
    view = products.copy()
    if search:
        mask = view["description"].astype(str).str.contains(
            search, case=False, na=False)
        if "stock_code" in view.columns:
            mask |= view["stock_code"].astype(str).str.contains(
                search, case=False, na=False)
        view = view[mask]

    options = [c for c in [
        "total_revenue", "total_quantity", "transactions",
        "average_price", "description"
    ] if c in view.columns]

    if options:
        sort_by = st.selectbox("Sort products by", options)
        view = view.sort_values(
            sort_by, ascending=(sort_by == "description"))

    st.dataframe(view, use_container_width=True, hide_index=True)
    st.download_button("Download product CSV",
        view.to_csv(index=False).encode("utf-8"),
        "products.csv", "text/csv")

elif page == "Country Analysis":
    st.title("Country Analysis")
    if "country" not in countries.columns:
        st.error("Could not find the country column.")
        st.stop()

    names = sorted(countries["country"].dropna().astype(str).unique())
    selected = st.multiselect(
        "Select countries", names, default=names[:min(10, len(names))])
    view = countries[countries["country"].astype(str).isin(selected)]

    if "total_revenue" in view.columns:
        fig = px.bar(view.sort_values("total_revenue"),
            x="total_revenue", y="country", orientation="h",
            title="Revenue by Country",
            color_discrete_sequence=[ORANGE])
        st.plotly_chart(chart(fig, max(420, 30 * len(view))),
            use_container_width=True)

    st.dataframe(view, use_container_width=True, hide_index=True)
    st.download_button("Download country CSV",
        view.to_csv(index=False).encode("utf-8"),
        "countries.csv", "text/csv")

elif page == "Monthly Analysis":
    st.title("Monthly Analysis")
    if "month" not in monthly.columns:
        st.error("Could not find the month column.")
        st.stop()

    view = monthly.sort_values("month").copy()
    if "total_revenue" in view.columns:
        fig = px.line(view, x="month", y="total_revenue",
            markers=True, title="Monthly Revenue",
            color_discrete_sequence=[ORANGE])
        st.plotly_chart(chart(fig), use_container_width=True)

    if "total_quantity" in view.columns:
        fig = px.bar(view, x="month", y="total_quantity",
            title="Monthly Quantity Sold",
            color_discrete_sequence=[ORANGE])
        st.plotly_chart(chart(fig), use_container_width=True)

    st.dataframe(view, use_container_width=True, hide_index=True)
    st.download_button("Download monthly CSV",
        view.to_csv(index=False).encode("utf-8"),
        "monthly.csv", "text/csv")

else:
    st.title("About this project")
    st.write("""
    This project explores online retail transactions through product,
    country and monthly summaries.

    **Technologies:** Python, Pandas, Plotly, Streamlit,
    Apache Spark and Cassandra in the local data workflow.

    The hosted dashboard reads CSV summaries committed to GitHub.
    It does not connect to Cassandra on a personal computer.
    """)
