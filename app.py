from pathlib import Path
import pandas as pd
import plotly.express as px
import streamlit as st

st.set_page_config(
    page_title="E-Commerce Intelligence",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

DATA = Path(__file__).parent / "data"
ORANGE = "#F28C28"

if "dark" not in st.session_state:
    st.session_state.dark = True

if "page" not in st.session_state:
    st.session_state.page = "Home"


def go_to(page):
    st.session_state.page = page


# -------------------- THEME --------------------

with st.sidebar:
    st.markdown(
        f"<h2 style='color:{ORANGE};'>◈ E-COMMERCE</h2>",
        unsafe_allow_html=True
    )
    st.caption("PRODUCT INTELLIGENCE")

    st.toggle("Dark mode", key="dark")

    st.markdown("---")
    st.markdown("##### NAVIGATION")

    page = st.radio(
        "Navigate",
        [
            "Home",
            "Overview",
            "Products",
            "Country Analysis",
            "Monthly Analysis",
            "About"
        ],
        key="page",
        label_visibility="collapsed"
    )

    st.markdown("---")
    st.caption("RETAIL ANALYTICS")
    st.caption("Data-driven decisions.")


dark = st.session_state.dark

bg = "#101214" if dark else "#F4F6F8"
panel = "#191D20" if dark else "#FFFFFF"
fg = "#F4F5F6" if dark else "#20252B"
muted = "#A5ABB2" if dark else "#68717D"
grid = "#343A40" if dark else "#DDE2E8"
input_bg = "#22272B" if dark else "#FFFFFF"

st.markdown(f"""
<style>
:root {{
    --accent: {ORANGE};
    --background: {bg};
    --panel: {panel};
    --foreground: {fg};
    --muted: {muted};
    --border: {grid};
}}

.stApp {{
    background: var(--background);
    color: var(--foreground);
}}

[data-testid="stSidebar"] {{
    background: var(--panel);
    border-right: 1px solid var(--border);
}}

[data-testid="stSidebar"] h2 {{
    letter-spacing: -1px;
}}

.block-container {{
    padding-top: 2rem;
    padding-bottom: 3rem;
    max-width: 1450px;
}}

h1, h2, h3 {{
    color: var(--foreground);
    letter-spacing: -0.7px;
}}

p, label, .stMarkdown {{
    color: var(--foreground);
}}

.hero {{
    background:
        radial-gradient(
            circle at 90% 10%,
            rgba(242,140,40,0.15),
            transparent 38%
        ),
        var(--panel);
    border: 1px solid var(--border);
    border-radius: 22px;
    padding: 42px;
    margin: 10px 0 28px 0;
    animation: appear 0.7s ease-out;
}}

.eyebrow {{
    color: {ORANGE};
    font-size: 12px;
    font-weight: 800;
    letter-spacing: 3px;
    margin-bottom: 15px;
}}

.hero h1 {{
    font-size: clamp(34px, 5vw, 58px);
    font-weight: 800;
    line-height: 1.08;
    letter-spacing: -2px;
    margin: 0;
}}

.hero p {{
    color: var(--muted);
    font-size: 17px;
    line-height: 1.7;
    max-width: 650px;
    margin-top: 20px;
}}

.accent {{
    color: {ORANGE};
}}

.section-label {{
    color: {ORANGE};
    font-size: 11px;
    font-weight: 800;
    letter-spacing: 2px;
    margin-bottom: 8px;
}}

div[data-testid="stMetric"] {{
    background: var(--panel);
    border: 1px solid var(--border);
    padding: 21px;
    border-radius: 15px;
    transition: transform 0.22s ease, border-color 0.22s ease;
    animation: appear 0.55s ease-out;
}}

div[data-testid="stMetric"]:hover {{
    transform: translateY(-4px);
    border-color: {ORANGE};
}}

div[data-testid="stMetricLabel"] {{
    color: var(--muted);
}}

div[data-testid="stMetricValue"] {{
    color: var(--foreground);
    font-weight: 750;
}}

div.stButton > button {{
    border-radius: 10px;
    border: 1px solid var(--border);
    min-height: 43px;
    transition: all 0.2s ease;
    font-weight: 650;
}}

div.stButton > button:hover {{
    border-color: {ORANGE};
    color: {ORANGE};
    transform: translateY(-2px);
}}

div.stButton > button[kind="primary"] {{
    background: {ORANGE};
    color: #151515;
    border: 1px solid {ORANGE};
}}

div.stButton > button[kind="primary"]:hover {{
    background: #FFAA4D;
    color: #151515;
}}

div[data-baseweb="input"] input,
div[data-baseweb="select"] > div {{
    background: var(--panel);
    color: var(--foreground);
    border-color: var(--border);
}}

[data-testid="stDataFrame"] {{
    border: 1px solid var(--border);
    border-radius: 12px;
    overflow: hidden;
}}

hr {{
    border-color: var(--border);
}}

@keyframes appear {{
    from {{
        opacity: 0;
        transform: translateY(9px);
    }}
    to {{
        opacity: 1;
        transform: translateY(0);
    }}
}}

footer {{
    visibility: hidden;
}}

@media (max-width: 768px) {{
    .hero {{
        padding: 25px;
    }}
    .hero h1 {{
        letter-spacing: -1px;
    }}
    .block-container {{
        padding-top: 1rem;
    }}
}}
</style>
""", unsafe_allow_html=True)


# -------------------- DATA --------------------

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
        columns={
            c: aliases[c]
            for c in df.columns
            if c in aliases
        }
    )


products = clean_columns(load_csv("products_summary.csv"))
countries = clean_columns(load_csv("country_summary.csv"))
monthly = clean_columns(load_csv("monthly_summary.csv"))

for df in [products, countries, monthly]:
    for col in [
        "total_revenue",
        "total_quantity",
        "average_price",
        "transactions"
    ]:
        if col in df.columns:
            df[col] = pd.to_numeric(
                df[col], errors="coerce"
            ).fillna(0)


def money(value):
    return f"£{value:,.2f}"


def chart(fig, height=420):
    fig.update_layout(
        height=height,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor=panel,
        font=dict(color=fg, family="Arial"),
        margin=dict(l=15, r=20, t=65, b=25),
        title_font_size=18,
        hoverlabel=dict(
            bgcolor=panel,
            font_color=fg
        ),
        legend_title_text=""
    )

    fig.update_xaxes(
        gridcolor=grid,
        zerolinecolor=grid
    )
    fig.update_yaxes(
        gridcolor=grid,
        zerolinecolor=grid
    )

    return fig


def section_heading(eyebrow, title, description=None):
    st.markdown(
        f"<div class='section-label'>{eyebrow}</div>",
        unsafe_allow_html=True
    )
    st.title(title)

    if description:
        st.caption(description)


def download_csv(df, filename, label):
    st.download_button(
        label=label,
        data=df.to_csv(index=False).encode("utf-8"),
        file_name=filename,
        mime="text/csv",
        use_container_width=False
    )


# -------------------- HOME --------------------

if page == "Home":

    st.markdown("""
    <div class="hero">
        <div class="eyebrow">E-COMMERCE INTELLIGENCE / 01</div>
        <h1>Understand your data.<br>
        <span class="accent">Transform your decisions.</span></h1>
        <p>
        An interactive retail analytics experience for exploring
        product performance, market contribution and monthly sales.
        Turn historical transactions into meaningful business insights.
        </p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown(
        "<div class='section-label'>YOUR BUSINESS AT A GLANCE</div>",
        unsafe_allow_html=True
    )

    k1, k2, k3 = st.columns(3)

    k1.metric("Products analysed", f"{len(products):,}")
    k2.metric("Countries analysed", f"{len(countries):,}")
    k3.metric("Months analysed", f"{len(monthly):,}")

    st.markdown("<br>", unsafe_allow_html=True)
    st.subheader("Explore the platform")
    st.caption("Choose an area to start exploring your retail data.")

    a, b = st.columns(2)

    with a:
        st.markdown("### 01 / Business overview")
        st.write(
            "Explore revenue indicators, leading products, "
            "country performance and monthly trends."
        )
        st.button(
            "Open overview →",
            type="primary",
            use_container_width=True,
            on_click=go_to,
            args=("Overview",)
        )

        st.markdown("### 02 / Product intelligence")
        st.write(
            "Search products, sort performance metrics and "
            "identify high-revenue items."
        )
        st.button(
            "Explore products →",
            use_container_width=True,
            on_click=go_to,
            args=("Products",)
        )

    with b:
        st.markdown("### 03 / Market performance")
        st.write(
            "Compare country-level sales and investigate "
            "which markets contribute most revenue."
        )
        st.button(
            "Explore countries →",
            use_container_width=True,
            on_click=go_to,
            args=("Country Analysis",)
        )

        st.markdown("### 04 / Revenue over time")
        st.write(
            "Explore monthly revenue and quantity patterns "
            "using interactive charts."
        )
        st.button(
            "Explore monthly trends →",
            use_container_width=True,
            on_click=go_to,
            args=("Monthly Analysis",)
        )

    st.markdown("---")
    st.caption(
        "BUILT WITH PYTHON · PANDAS · PLOTLY · STREAMLIT"
    )


# -------------------- OVERVIEW --------------------

elif page == "Overview":

    section_heading(
        "BUSINESS INTELLIGENCE / 01",
        "Business overview",
        "A consolidated view of your retail performance."
    )

    revenue = (
        products["total_revenue"].sum()
        if "total_revenue" in products.columns else 0
    )

    quantity = (
        products["total_quantity"].sum()
        if "total_quantity" in products.columns else 0
    )

    transactions = (
        products["transactions"].sum()
        if "transactions" in products.columns else None
    )

    m1, m2, m3, m4 = st.columns(4)

    m1.metric("Total revenue", money(revenue))
    m2.metric("Quantity sold", f"{quantity:,.0f}")
    m3.metric("Products", f"{len(products):,}")
    m4.metric("Countries", f"{len(countries):,}")

    st.markdown("<br>", unsafe_allow_html=True)

    left, right = st.columns(2)

    with left:
        if {"description", "total_revenue"}.issubset(products.columns):
            count = st.slider(
                "Products to display",
                min_value=5,
                max_value=min(30, max(5, len(products))),
                value=min(10, max(5, len(products))),
                key="overview_top_products"
            )

            top = products.nlargest(
                min(count, len(products)), "total_revenue"
            ).sort_values("total_revenue")

            fig = px.bar(
                top,
                x="total_revenue",
                y="description",
                orientation="h",
                title="Leading products by revenue",
                labels={
                    "total_revenue": "Revenue (£)",
                    "description": "Product"
                },
                color_discrete_sequence=[ORANGE],
                hover_data=["total_revenue"]
            )

            st.plotly_chart(
                chart(fig, max(420, 25 * len(top))),
                use_container_width=True,
                key="overview_products_chart"
            )

    with right:
        if {"country", "total_revenue"}.issubset(countries.columns):
            top_countries = countries.nlargest(
                min(10, len(countries)), "total_revenue"
            ).sort_values("total_revenue")

            fig = px.bar(
                top_countries,
                x="total_revenue",
                y="country",
                orientation="h",
                title="Leading markets by revenue",
                labels={
                    "total_revenue": "Revenue (£)",
                    "country": "Country"
                },
                color_discrete_sequence=[ORANGE]
            )

            st.plotly_chart(
                chart(fig, max(420, 25 * len(top_countries))),
                use_container_width=True,
                key="overview_country_chart"
            )

    if {"month", "total_revenue"}.issubset(monthly.columns):
        fig = px.line(
            monthly.sort_values("month"),
            x="month",
            y="total_revenue",
            markers=True,
            title="Monthly revenue trend",
            labels={
                "month": "Month",
                "total_revenue": "Revenue (£)"
            },
            color_discrete_sequence=[ORANGE]
        )

        fig.update_traces(
            line_width=3,
            marker_size=8,
            fill="tozeroy",
            fillcolor="rgba(242,140,40,0.08)"
        )

        st.plotly_chart(
            chart(fig),
            use_container_width=True,
            key="overview_monthly_chart"
        )


# -------------------- PRODUCTS --------------------

elif page == "Products":

    section_heading(
        "PRODUCT INTELLIGENCE / 02",
        "Product analysis",
        "Search, compare and sort product performance."
    )

    if "description" not in products.columns:
        st.error("The product description column was not found.")
        st.stop()

    search = st.text_input(
        "Search by product name or stock code",
        placeholder="Start typing a product..."
    )

    view = products.copy()

    if search:
        mask = view["description"].astype(str).str.contains(
            search, case=False, na=False
        )

        if "stock_code" in view.columns:
            mask |= view["stock_code"].astype(str).str.contains(
                search, case=False, na=False
            )

        view = view[mask]

    available_sort = [
        c for c in [
            "total_revenue",
            "total_quantity",
            "transactions",
            "average_price",
            "description"
        ]
        if c in view.columns
    ]

    if available_sort:
        c1, c2 = st.columns([2, 1])

        with c1:
            sort_by = st.selectbox(
                "Sort results by",
                available_sort,
                format_func=lambda c: c.replace("_", " ").title()
            )

        with c2:
            order = st.selectbox(
                "Sort order",
                ["Highest first", "Lowest first"]
            )

        view = view.sort_values(
            sort_by,
            ascending=(
                order == "Lowest first"
                if sort_by != "description"
                else True
            )
        )

    p1, p2 = st.columns(2)
    p1.metric("Matching products", f"{len(view):,}")

    if "total_revenue" in view.columns:
        p2.metric(
            "Revenue in selection",
            money(view["total_revenue"].sum())
        )

    if "total_revenue" in view.columns:
        top = view.nlargest(
            min(15, len(view)), "total_revenue"
        ).sort_values("total_revenue")

        fig = px.bar(
            top,
            x="total_revenue",
            y="description",
            orientation="h",
            title="Revenue comparison",
            labels={
                "total_revenue": "Revenue (£)",
                "description": "Product"
            },
            color_discrete_sequence=[ORANGE]
        )

        st.plotly_chart(
            chart(fig, max(400, len(top) * 27)),
            use_container_width=True,
            key="products_revenue_chart"
        )

    st.subheader("Product records")
    st.dataframe(
        view,
        use_container_width=True,
        hide_index=True
    )

    download_csv(
        view,
        "products.csv",
        "Download filtered product data"
    )


# -------------------- COUNTRY ANALYSIS --------------------

elif page == "Country Analysis":

    section_heading(
        "MARKET INTELLIGENCE / 03",
        "Country analysis",
        "Compare retail revenue across markets."
    )

    if "country" not in countries.columns:
        st.error("The country column was not found.")
        st.stop()

    names = sorted(
        countries["country"].dropna().astype(str).unique()
    )

    selected = st.multiselect(
        "Choose countries to compare",
        names,
        default=names[:min(10, len(names))]
    )

    view = countries[
        countries["country"].astype(str).isin(selected)
    ].copy()

    c1, c2 = st.columns(2)

    c1.metric("Selected countries", f"{len(view):,}")

    selected_revenue = (
        view["total_revenue"].sum()
        if "total_revenue" in view.columns else 0
    )

    c2.metric("Selected revenue", money(selected_revenue))

    if not view.empty and "total_revenue" in view.columns:

        view = view.sort_values("total_revenue")

        fig = px.bar(
            view,
            x="total_revenue",
            y="country",
            orientation="h",
            title="Revenue by selected country",
            labels={
                "total_revenue": "Revenue (£)",
                "country": "Country"
            },
            color="total_revenue",
            color_continuous_scale=[
                "#6A3B18", ORANGE, "#FFC078"
            ]
        )

        st.plotly_chart(
            chart(fig, max(420, 30 * len(view))),
            use_container_width=True,
            key="country_revenue_chart"
        )

    elif view.empty:
        st.info("Select one or more countries to display results.")

    st.subheader("Country records")
    st.dataframe(
        view,
        use_container_width=True,
        hide_index=True
    )

    download_csv(
        view,
        "countries.csv",
        "Download selected country data"
    )


# -------------------- MONTHLY ANALYSIS --------------------

elif page == "Monthly Analysis":

    section_heading(
        "TIME-SERIES INTELLIGENCE / 04",
        "Monthly analysis",
        "Explore revenue and sales quantities over time."
    )

    if "month" not in monthly.columns:
        st.error("The month column was not found.")
        st.stop()

    view = monthly.sort_values("month").copy()

    if {"month", "total_revenue"}.issubset(view.columns):

        total = view["total_revenue"].sum()

        a, b = st.columns(2)
        a.metric("Revenue across displayed months", money(total))
        b.metric("Months available", f"{len(view):,}")

        fig = px.line(
            view,
            x="month",
            y="total_revenue",
            markers=True,
            title="Monthly revenue",
            labels={
                "month": "Month",
                "total_revenue": "Revenue (£)"
            },
            color_discrete_sequence=[ORANGE]
        )

        fig.update_traces(
            line_width=3,
            marker_size=8
        )

        st.plotly_chart(
            chart(fig),
            use_container_width=True,
            key="monthly_revenue_chart"
        )

    if {"month", "total_quantity"}.issubset(view.columns):

        fig = px.bar(
            view,
            x="month",
            y="total_quantity",
            title="Monthly quantity sold",
            labels={
                "month": "Month",
                "total_quantity": "Quantity"
            },
            color_discrete_sequence=[ORANGE]
        )

        st.plotly_chart(
            chart(fig),
            use_container_width=True,
            key="monthly_quantity_chart"
        )

    st.subheader("Monthly records")
    st.dataframe(
        view,
        use_container_width=True,
        hide_index=True
    )

    download_csv(
        view,
        "monthly.csv",
        "Download monthly data"
    )


# -------------------- ABOUT --------------------

elif page == "About":

    section_heading(
        "PROJECT INFORMATION / 05",
        "About the project",
        "Turning online retail transactions into useful insights."
    )

    st.markdown("""
    <div class="hero">
        <div class="eyebrow">PROJECT OVERVIEW</div>
        <h1>Retail data.<br>
        <span class="accent">Clearer decisions.</span></h1>
        <p>
        This project analyses historical online retail transactions
        to explore product performance, country-level revenue and
        monthly sales patterns.
        </p>
    </div>
    """, unsafe_allow_html=True)

    st.subheader("Technology stack")

    t1, t2 = st.columns(2)

    with t1:
        st.markdown("**Python & Pandas**")
        st.write("Data loading, transformation and analysis.")

        st.markdown("**Apache Spark / PySpark**")
        st.write("Scalable processing in the local data workflow.")

        st.markdown("**Apache Cassandra**")
        st.write("Storage of summary tables in the local workflow.")

    with t2:
        st.markdown("**Plotly**")
        st.write("Interactive charts and data visualisations.")

        st.markdown("**Streamlit**")
        st.write("Dashboard interface, navigation and filters.")

        st.markdown("**GitHub**")
        st.write("Version-controlled project files and CSV summaries.")

    st.info(
        "The hosted dashboard reads summary CSV files from the "
        "repository. It does not connect directly to Cassandra "
        "running on a personal computer."
    )

    st.markdown("---")
    st.caption(
        "E-COMMERCE PRODUCT ANALYSIS · DATA-DRIVEN RETAIL INSIGHTS"
    )
