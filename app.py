from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st


# --------------------------------------------------
# PAGE CONFIGURATION
# --------------------------------------------------

st.set_page_config(
    page_title="E-Commerce Product Analysis",
    page_icon="📊",
    layout="wide"
)

DATA = Path(__file__).parent / "data"

ORANGE = "#F28C28"

# Orange gradient for categorical bar charts
ORANGE_SHADES = [
    "#B94E0B",
    "#C65D12",
    "#D97726",
    "#E87518",
    "#F28C28",
    "#F6A04D",
    "#FFAD55",
    "#FFC078",
    "#FFD0A0",
    "#E9944A",
]


# --------------------------------------------------
# THEME
# --------------------------------------------------

if "dark" not in st.session_state:
    st.session_state.dark = True

DARK = st.session_state.dark

BG = "#111315" if DARK else "#F5F6F8"
CARD = "#1C1F23" if DARK else "#FFFFFF"
FG = "#F5F5F5" if DARK else "#252525"
MUTED = "#B8BEC6" if DARK else "#606873"
GRID = "#383D43" if DARK else "#E1E5EA"

st.markdown(
    f"""
    <style>
    .stApp {{
        background-color: {BG};
        color: {FG};
    }}

    [data-testid="stSidebar"] {{
        background-color: {CARD};
    }}

    [data-testid="stSidebar"] * {{
        color: {FG};
    }}

    h1, h2, h3, h4 {{
        color: {FG};
    }}

    p, label, .stCaption {{
        color: {FG};
    }}

    [data-testid="stMetric"] {{
        background-color: {CARD};
        padding: 18px;
        border-radius: 12px;
        border: 1px solid {GRID};
        transition: transform 0.2s ease;
    }}

    [data-testid="stMetric"]:hover {{
        transform: translateY(-3px);
    }}

    [data-testid="stMetricLabel"] {{
        color: {MUTED};
    }}

    [data-testid="stMetricValue"] {{
        color: {ORANGE};
    }}

    div.stButton > button {{
        border-radius: 9px;
        border: 1px solid {ORANGE};
        min-height: 42px;
        font-weight: 600;
    }}

    div.stButton > button:hover {{
        border-color: #FFAD55;
        color: {ORANGE};
    }}

    .hero {{
        padding: 35px;
        border-radius: 18px;
        background: linear-gradient(
            120deg,
            #321B0D 0%,
            #71380F 45%,
            #F28C28 100%
        );
        color: white;
        margin-bottom: 25px;
    }}

    .hero h1 {{
        color: white;
        font-size: 36px;
        margin-bottom: 10px;
    }}

    .hero p {{
        color: #FFF0E0;
        font-size: 16px;
    }}

    .section-note {{
        color: {MUTED};
        font-size: 14px;
    }}

    </style>
    """,
    unsafe_allow_html=True
)


# --------------------------------------------------
# DATA CLEANING AND COLUMN NAMES
# --------------------------------------------------

def clean_columns(df):
    df.columns = (
        df.columns.astype(str)
        .str.strip()
        .str.lower()
        .str.replace(" ", "_")
        .str.replace("-", "_")
    )

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
        "transaction_count": "transactions",
    }

    df = df.rename(
        columns={
            col: aliases[col]
            for col in df.columns
            if col in aliases
        }
    )

    return df


def load_csv(filename):
    path = DATA / filename

    if not path.exists():
        st.error(f"Required data file not found: data/{filename}")
        st.stop()

    df = pd.read_csv(path)
    df = clean_columns(df)

    numeric_columns = [
        "total_revenue",
        "total_quantity",
        "average_price",
        "transactions",
    ]

    for col in numeric_columns:
        if col in df.columns:
            df[col] = pd.to_numeric(
                df[col], errors="coerce"
            ).fillna(0)

    return df


products = load_csv("products_summary.csv")
countries = load_csv("country_summary.csv")
monthly = load_csv("monthly_summary.csv")


# --------------------------------------------------
# HELPER FUNCTIONS
# --------------------------------------------------

def get_total(df, column):
    if column in df.columns:
        return df[column].sum()
    return 0


def money(value):
    return f"{value:,.2f}"


def chart(fig, height=420):
    """Apply readable colours to every Plotly chart."""

    dark = st.session_state.get("dark", True)

    bg = "#171717" if dark else "#FFFFFF"
    fg = "#F5F5F5" if dark else "#262626"
    grid = "#383838" if dark else "#E5E7EB"

    fig.update_layout(
        height=height,
        paper_bgcolor=bg,
        plot_bgcolor=bg,
        font=dict(
            color=fg,
            family="Arial"
        ),
        title_font=dict(color=fg),
        legend=dict(
            font=dict(color=fg),
            bgcolor="rgba(0,0,0,0)"
        ),
        margin=dict(l=20, r=20, t=65, b=35),
        hoverlabel=dict(
            bgcolor=bg,
            font_color=fg
        )
    )

    # Explicitly set tick labels, titles, and grid colours.
    # This prevents white text on a white background.

    fig.update_xaxes(
        color=fg,
        title_font=dict(color=fg),
        tickfont=dict(color=fg),
        gridcolor=grid,
        zerolinecolor=grid,
        linecolor=grid
    )

    fig.update_yaxes(
        color=fg,
        title_font=dict(color=fg),
        tickfont=dict(color=fg),
        gridcolor=grid,
        zerolinecolor=grid,
        linecolor=grid
    )

    st.plotly_chart(
        fig,
        use_container_width=True,
        theme=None
    )


def revenue_column(df):
    if "total_revenue" in df.columns:
        return "total_revenue"
    return None


def show_download(df, filename, label="Download CSV"):
    st.download_button(
        label=label,
        data=df.to_csv(index=False).encode("utf-8"),
        file_name=filename,
        mime="text/csv"
    )


def go_to(page_name):
    st.session_state.page = page_name


# --------------------------------------------------
# SIDEBAR NAVIGATION
# --------------------------------------------------

with st.sidebar:
    st.markdown(
        f"""
        <h2 style="color:{ORANGE};">
            E-Commerce Analytics
        </h2>
        <p style="color:{MUTED};">
            Product performance dashboard
        </p>
        """,
        unsafe_allow_html=True
    )

    st.toggle(
        "Night mode",
        key="dark"
    )

    st.divider()

    pages = [
        "Home",
        "Overview",
        "Products",
        "Country Analysis",
        "Monthly Analysis",
        "About",
    ]

    if "page" not in st.session_state:
        st.session_state.page = "Home"

    st.radio(
        "Navigation",
        pages,
        key="page"
    )

    st.divider()

    st.caption("Built with Python, PySpark, Cassandra and Streamlit")


page = st.session_state.page


# --------------------------------------------------
# HOME PAGE
# --------------------------------------------------

if page == "Home":

    st.markdown(
        """
        <div class="hero">
            <h1>Understand Your Data.<br>
            Transform Your Decisions.</h1>
            <p>
                Explore e-commerce performance through product insights,
                country-wise revenue, and monthly sales trends.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.subheader("Your Business at a Glance")

    col1, col2, col3 = st.columns(3)

    total_revenue = get_total(products, "total_revenue")
    total_quantity = get_total(products, "total_quantity")
    product_count = len(products)

    with col1:
        st.metric(
            "Total Revenue",
            money(total_revenue)
        )

    with col2:
        st.metric(
            "Units Sold",
            f"{total_quantity:,.0f}"
        )

    with col3:
        st.metric(
            "Products Analysed",
            f"{product_count:,}"
        )

    st.write("")

    st.subheader("Explore the Dashboard")

    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("Product Insights", use_container_width=True):
            go_to("Products")
            st.rerun()

    with col2:
        if st.button("Country Performance", use_container_width=True):
            go_to("Country Analysis")
            st.rerun()

    with col3:
        if st.button("Monthly Trends", use_container_width=True):
            go_to("Monthly Analysis")
            st.rerun()

    st.info(
        "Use the sidebar to explore the dashboard pages, "
        "filter results, and download summary data."
    )


# --------------------------------------------------
# OVERVIEW PAGE
# --------------------------------------------------

elif page == "Overview":

    st.title("Sales Overview")

    st.markdown(
        '<p class="section-note">A summary of overall e-commerce performance.</p>',
        unsafe_allow_html=True
    )

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            "Total Revenue",
            money(get_total(products, "total_revenue"))
        )

    with col2:
        st.metric(
            "Total Quantity",
            f"{get_total(products, 'total_quantity'):,.0f}"
        )

    with col3:
        st.metric(
            "Products",
            f"{len(products):,}"
        )

    with col4:
        st.metric(
            "Countries",
            f"{len(countries):,}"
        )

    st.divider()

    left, right = st.columns(2)

    with left:
        st.subheader("Top Products by Revenue")

        if {
            "description",
            "total_revenue"
        }.issubset(products.columns):

            top_n = st.slider(
                "Number of products",
                min_value=5,
                max_value=max(5, min(30, len(products))),
                value=max(5, min(10, len(products))),
                key="overview_top_n"
            )

            top_products = (
                products.nlargest(
                    min(top_n, len(products)),
                    "total_revenue"
                )
                .sort_values("total_revenue")
            )

            fig = px.bar(
                top_products,
                x="total_revenue",
                y="description",
                orientation="h",
                color="description",
                color_discrete_sequence=ORANGE_SHADES,
                title="Highest-Revenue Products"
            )

            fig.update_layout(
                showlegend=False,
                xaxis_title="Revenue",
                yaxis_title="Product"
            )

            chart(fig, height=480)

        else:
            st.warning(
                "The product summary needs description "
                "and total_revenue columns."
            )

    with right:
        st.subheader("Revenue by Country")

        if {
            "country",
            "total_revenue"
        }.issubset(countries.columns):

            top_countries = (
                countries.nlargest(
                    min(10, len(countries)),
                    "total_revenue"
                )
                .sort_values("total_revenue")
            )

            fig = px.bar(
                top_countries,
                x="total_revenue",
                y="country",
                orientation="h",
                color="country",
                color_discrete_sequence=ORANGE_SHADES,
                title="Top Countries by Revenue"
            )

            fig.update_layout(
                showlegend=False,
                xaxis_title="Revenue",
                yaxis_title="Country"
            )

            chart(fig, height=480)

        else:
            st.warning(
                "The country summary needs country "
                "and total_revenue columns."
            )

    st.divider()

    st.subheader("Monthly Revenue Trend")

    if {
        "month",
        "total_revenue"
    }.issubset(monthly.columns):

        fig = px.line(
            monthly,
            x="month",
            y="total_revenue",
            markers=True,
            title="Revenue Over Time",
            color_discrete_sequence=[ORANGE]
        )

        fig.update_traces(
            line=dict(width=3),
            marker=dict(size=8)
        )

        fig.update_layout(
            xaxis_title="Month",
            yaxis_title="Revenue"
        )

        chart(fig, height=380)

    else:
        st.warning(
            "The monthly summary needs month "
            "and total_revenue columns."
        )


# --------------------------------------------------
# PRODUCTS PAGE
# --------------------------------------------------

elif page == "Products":

    st.title("Product Analysis")

    st.write(
        "Search, sort, and explore individual product performance."
    )

    if "description" not in products.columns:
        st.error("The product summary has no description column.")

    else:
        search = st.text_input(
            "Search products",
            placeholder="Enter a product name or keyword..."
        )

        filtered = products.copy()

        filtered["description"] = (
            filtered["description"].fillna("").astype(str)
        )

        if search:
            filtered = filtered[
                filtered["description"].str.contains(
                    search,
                    case=False,
                    na=False
                )
            ]

        sort_options = [
            col for col in [
                "total_revenue",
                "total_quantity",
                "average_price",
                "transactions",
                "description",
            ]
            if col in filtered.columns
        ]

        if sort_options:
            default_index = (
                sort_options.index("total_revenue")
                if "total_revenue" in sort_options
                else 0
            )

            sort_by = st.selectbox(
                "Sort products by",
                sort_options,
                index=default_index
            )

            ascending = st.checkbox(
                "Sort in ascending order",
                value=False
            )

            filtered = filtered.sort_values(
                sort_by,
                ascending=ascending
            )

        st.metric("Matching Products", f"{len(filtered):,}")

        if {
            "description",
            "total_revenue"
        }.issubset(filtered.columns):

            top_products = filtered.head(15).sort_values(
                "total_revenue"
            )

            fig = px.bar(
                top_products,
                x="total_revenue",
                y="description",
                orientation="h",
                color="description",
                color_discrete_sequence=ORANGE_SHADES,
                title="Product Revenue Comparison"
            )

            fig.update_layout(
                showlegend=False,
                xaxis_title="Revenue",
                yaxis_title="Product"
            )

            chart(fig, height=500)

        st.subheader("Product Summary")

        st.dataframe(
            filtered,
            use_container_width=True,
            hide_index=True
        )

        show_download(
            filtered,
            "filtered_products.csv",
            "Download Product Data"
        )


# --------------------------------------------------
# COUNTRY ANALYSIS PAGE
# --------------------------------------------------

elif page == "Country Analysis":

    st.title("Country Analysis")

    st.write(
        "Compare revenue and sales performance across countries."
    )

    if "country" not in countries.columns:
        st.error("The country summary has no country column.")

    else:
        country_names = sorted(
            countries["country"]
            .dropna()
            .astype(str)
            .unique()
            .tolist()
        )

        selected_countries = st.multiselect(
            "Select countries",
            country_names,
            default=country_names[:10]
        )

        filtered_countries = countries[
            countries["country"].astype(str).isin(
                selected_countries
            )
        ].copy()

        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric(
                "Countries Selected",
                f"{len(filtered_countries):,}"
            )

        with col2:
            st.metric(
                "Total Revenue",
                money(
                    get_total(
                        filtered_countries,
                        "total_revenue"
                    )
                )
            )

        with col3:
            st.metric(
                "Total Quantity",
                f"{get_total(filtered_countries, 'total_quantity'):,.0f}"
            )

        if (
            not filtered_countries.empty
            and "total_revenue" in filtered_countries.columns
        ):

            chart_data = filtered_countries.sort_values(
                "total_revenue"
            )

            fig = px.bar(
                chart_data,
                x="total_revenue",
                y="country",
                orientation="h",
                color="country",
                color_discrete_sequence=ORANGE_SHADES,
                title="Revenue by Selected Country"
            )

            fig.update_layout(
                showlegend=False,
                xaxis_title="Revenue",
                yaxis_title="Country"
            )

            chart(
                fig,
                height=max(380, len(chart_data) * 32)
            )

        st.subheader("Country Summary")

        st.dataframe(
            filtered_countries,
            use_container_width=True,
            hide_index=True
        )

        show_download(
            filtered_countries,
            "country_analysis.csv",
            "Download Country Data"
        )


# --------------------------------------------------
# MONTHLY ANALYSIS PAGE
# --------------------------------------------------

elif page == "Monthly Analysis":

    st.title("Monthly Analysis")

    st.write(
        "Explore changes in revenue and sales quantity over time."
    )

    if "month" not in monthly.columns:
        st.error("The monthly summary has no month column.")

    else:
        col1, col2 = st.columns(2)

        with col1:
            st.metric(
                "Total Revenue",
                money(get_total(monthly, "total_revenue"))
            )

        with col2:
            st.metric(
                "Total Quantity",
                f"{get_total(monthly, 'total_quantity'):,.0f}"
            )

        if "total_revenue" in monthly.columns:

            fig = px.line(
                monthly,
                x="month",
                y="total_revenue",
                markers=True,
                title="Monthly Revenue Trend",
                color_discrete_sequence=[ORANGE]
            )

            fig.update_traces(
                line=dict(width=3),
                marker=dict(size=8)
            )

            fig.update_layout(
                xaxis_title="Month",
                yaxis_title="Revenue"
            )

            chart(fig, height=400)

        if "total_quantity" in monthly.columns:

            fig = px.bar(
                monthly,
                x="month",
                y="total_quantity",
                title="Monthly Sales Quantity",
                color="month",
                color_discrete_sequence=ORANGE_SHADES
            )

            fig.update_layout(
                showlegend=False,
                xaxis_title="Month",
                yaxis_title="Quantity"
            )

            chart(fig, height=400)

        st.subheader("Monthly Summary")

        st.dataframe(
            monthly,
            use_container_width=True,
            hide_index=True
        )

        show_download(
            monthly,
            "monthly_analysis.csv",
            "Download Monthly Data"
        )


# --------------------------------------------------
# ABOUT PAGE
# --------------------------------------------------

elif page == "About":

    st.title("About This Project")

    st.markdown(
        """
        ### E-Commerce Product Analysis

        This project analyses online retail sales data to discover
        useful business insights.

        ### Technologies Used

        - **Python:** Main programming language.
        - **PySpark:** Data processing and analysis.
        - **Cassandra:** NoSQL database storage.
        - **Pandas:** Loading and handling summary CSV files.
        - **Plotly:** Interactive charts and visualisations.
        - **Streamlit:** Interactive web dashboard.

        ### Key Features

        - Product revenue analysis
        - Country-wise sales comparison
        - Monthly revenue trends
        - Interactive filters and search
        - Downloadable summary data
        - Light and dark display modes

        ### Data Source

        This hosted dashboard reads pre-generated CSV summary files
        from the project's `data` folder. It does not connect directly
        to a Cassandra server.

        PySpark and Cassandra are part of the project's data-processing
        and storage workflow.
        """
    )

    st.divider()

    st.caption(
        "E-Commerce Product Analysis | Data-driven business insights"
    )
