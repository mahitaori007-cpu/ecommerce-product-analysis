import streamlit as st
import pandas as pd
import plotly.express as px
from cassandra.cluster import Cluster

st.set_page_config(
    page_title="E-Commerce Sales Analytics",
    page_icon=None,
    layout="wide"
)

# ---------------- DATA CONNECTION ----------------
@st.cache_resource
def connect_cassandra():
    cluster = Cluster(["127.0.0.1"], port=9042)
    session = cluster.connect("ecommerce")
    return cluster, session


@st.cache_data(ttl=60)
def load_data():
    _, session = connect_cassandra()

    products = pd.DataFrame(
        [row._asdict() for row in session.execute("SELECT * FROM products_summary")]
    )
    countries = pd.DataFrame(
        [row._asdict() for row in session.execute("SELECT * FROM country_summary")]
    )
    monthly = pd.DataFrame(
        [row._asdict() for row in session.execute("SELECT * FROM monthly_summary")]
    )

    for frame in (products, countries, monthly):
        for column in ("total_revenue", "total_quantity", "average_price", "transactions"):
            if column in frame.columns:
                frame[column] = pd.to_numeric(frame[column], errors="coerce")

    return products, countries, monthly


# ---------------- THEME ----------------
if "night_mode" not in st.session_state:
    st.session_state["night_mode"] = True

night_mode = st.sidebar.toggle("Night mode", key="night_mode")

if night_mode:
    bg = "#0B0B0D"
    surface = "#171719"
    sidebar_bg = "#111113"
    text_color = "#F5F5F5"
    muted = "#B7B7BF"
    border = "#343438"
    accent = "#FF4D00"
    grid = "#38383D"
    template = "plotly_dark"
else:
    bg = "#F4F4F5"
    surface = "#FFFFFF"
    sidebar_bg = "#E9E9EB"
    text_color = "#202024"
    muted = "#55555F"
    border = "#D4D4D8"
    accent = "#F04B00"
    grid = "#DADAE0"
    template = "plotly_white"

st.markdown(
    f"""
    <style>
    :root {{
        --bg: {bg};
        --surface: {surface};
        --sidebar: {sidebar_bg};
        --text: {text_color};
        --muted: {muted};
        --border: {border};
        --accent: {accent};
    }}

    .stApp, [data-testid="stMain"] {{
        background: var(--bg);
        color: var(--text);
    }}

    [data-testid="stHeader"] {{
        background: var(--bg);
    }}

    section[data-testid="stSidebar"] {{
        background: var(--sidebar);
        border-right: 1px solid var(--border);
    }}

    section[data-testid="stSidebar"] * {{
        color: var(--text);
    }}

    h1, h2, h3, h4, p, label,
    [data-testid="stMarkdownContainer"] p {{
        color: var(--text);
    }}

    .main-title {{
        background: var(--surface);
        border: 1px solid var(--border);
        border-left: 5px solid var(--accent);
        border-radius: 12px;
        padding: 22px 26px;
        margin-bottom: 20px;
    }}

    .main-title h1 {{
        color: var(--text) !important;
        font-size: 30px;
        margin: 0 0 7px 0;
    }}

    .main-title p {{
        color: var(--muted) !important;
        font-size: 15px;
        margin: 0;
    }}

    div[data-testid="stMetric"] {{
        background: var(--surface);
        border: 1px solid var(--border);
        border-radius: 12px;
        padding: 17px 18px;
        transition: border-color 0.2s ease, transform 0.2s ease;
    }}

    div[data-testid="stMetric"]:hover {{
        border-color: var(--accent);
        transform: translateY(-2px);
    }}

    [data-testid="stMetricLabel"] {{
        color: var(--muted) !important;
    }}

    [data-testid="stMetricValue"] {{
        color: var(--text) !important;
    }}

    .section-note {{
        color: var(--muted);
        font-size: 13px;
        margin-top: -8px;
        margin-bottom: 12px;
    }}

    .stButton button, .stDownloadButton button {{
        background: var(--accent);
        color: #FFFFFF !important;
        border: 1px solid var(--accent);
        border-radius: 8px;
    }}

    .stButton button:hover, .stDownloadButton button:hover {{
        filter: brightness(0.92);
        color: #FFFFFF !important;
    }}

    div[data-testid="stDataFrame"] {{
        border: 1px solid var(--border);
        border-radius: 10px;
    }}

    hr {{
        border-color: var(--border);
    }}
    </style>
    """,
    unsafe_allow_html=True
)


# ---------------- CHART STYLE ----------------
def style_chart(fig, height=390):
    fig.update_layout(
        template=template,
        paper_bgcolor=surface,
        plot_bgcolor=surface,
        font=dict(
            family="Arial, sans-serif",
            size=13,
            color=text_color
        ),
        title_font=dict(size=17, color=text_color),
        legend_font=dict(color=text_color),
        margin=dict(l=18, r=18, t=35, b=25),
        height=height,
        transition_duration=300,
        coloraxis_colorbar=dict(
            tickfont=dict(color=text_color),
            title_font=dict(color=text_color)
        )
    )
    fig.update_xaxes(
        gridcolor=grid,
        linecolor=border,
        zerolinecolor=grid,
        tickfont=dict(color=text_color, size=12),
        title_font=dict(color=text_color, size=13),
        automargin=True
    )
    fig.update_yaxes(
        gridcolor=grid,
        linecolor=border,
        zerolinecolor=grid,
        tickfont=dict(color=text_color, size=12),
        title_font=dict(color=text_color, size=13),
        automargin=True
    )
    return fig


def orange_scale():
    return [[0, accent], [1, "#B8B8B8"]]


# ---------------- HEADER ----------------
st.markdown(
    """
    <div class="main-title">
        <h1>E-Commerce Sales Analytics</h1>
        <p>Explore revenue, product performance, country sales and monthly trends.</p>
    </div>
    """,
    unsafe_allow_html=True
)

try:
    products, countries, monthly = load_data()

    if products.empty or countries.empty or monthly.empty:
        st.warning(
            "One or more Cassandra summary tables are empty. "
            "Check that the CSV files were imported into Cassandra."
        )
        st.stop()

    expected = {
        "products": {"stock_code", "description", "total_revenue"},
        "countries": {"country", "total_revenue", "total_quantity"},
        "monthly": {"month", "total_revenue", "total_quantity"}
    }
    missing = []
    for name, frame in (
        ("products_summary", products),
        ("country_summary", countries),
        ("monthly_summary", monthly)
    ):
        absent = expected[
            "products" if name == "products_summary"
            else "countries" if name == "country_summary"
            else "monthly"
        ].difference(frame.columns)
        if absent:
            missing.append(f"{name}: {', '.join(sorted(absent))}")

    if missing:
        st.error("Some expected Cassandra columns are missing.")
        st.code("\n".join(missing))
        st.stop()

    # Sidebar navigation
    page = st.sidebar.radio(
        "Navigation",
        ["Overview", "Products", "Country Analysis", "Monthly Analysis", "About"]
    )

    # ---------------- OVERVIEW ----------------
    if page == "Overview":
        st.subheader("Business Overview")
        st.markdown(
            '<div class="section-note">Key figures calculated from the imported summary data.</div>',
            unsafe_allow_html=True
        )

        total_revenue = countries["total_revenue"].fillna(0).sum()
        total_quantity = countries["total_quantity"].fillna(0).sum()
        product_count = products["stock_code"].nunique()
        country_count = countries["country"].nunique()

        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Total Revenue", f"£{total_revenue:,.2f}")
        c2.metric("Quantity Sold", f"{total_quantity:,.0f}")
        c3.metric("Products", f"{product_count:,}")
        c4.metric("Countries", f"{country_count:,}")

        st.divider()

        left, right = st.columns(2)

        with left:
            st.subheader("Top Products by Revenue")
            st.markdown(
                '<div class="section-note">Highest-revenue products in the dataset.</div>',
                unsafe_allow_html=True
            )
            top_products = products.nlargest(10, "total_revenue").copy()
            top_products["product_label"] = top_products["description"].fillna(
                top_products["stock_code"].astype(str)
            ).astype(str).str.slice(0, 42)
            top_products = top_products.sort_values("total_revenue")

            fig = px.bar(
                top_products,
                x="total_revenue",
                y="product_label",
                orientation="h",
                color="total_revenue",
                color_continuous_scale=orange_scale(),
                hover_data={
                    "product_label": True,
                    "stock_code": True,
                    "total_revenue": ":,.2f",
                    "total_quantity": ":,.0f" if "total_quantity" in top_products else False
                },
                labels={
                    "total_revenue": "Revenue (£)",
                    "product_label": "Product",
                    "stock_code": "Stock code"
                }
            )
            fig.update_layout(
                showlegend=False,
                coloraxis_showscale=False,
                xaxis_title="Revenue (£)",
                yaxis_title=""
            )
            style_chart(fig, height=420)
            st.plotly_chart(fig, use_container_width=True)

        with right:
            st.subheader("Top Countries by Revenue")
            st.markdown(
                '<div class="section-note">Use the selector to compare all countries or exclude the largest market.</div>',
                unsafe_allow_html=True
            )
            exclude_uk = st.checkbox("Exclude United Kingdom to compare other countries")
            country_plot = countries.copy()
            if exclude_uk:
                country_plot = country_plot[
                    country_plot["country"].astype(str).str.lower() != "united kingdom"
                ]

            top_countries = country_plot.nlargest(10, "total_revenue").sort_values(
                "total_revenue"
            )
            fig = px.bar(
                top_countries,
                x="total_revenue",
                y="country",
                orientation="h",
                color="total_revenue",
                color_continuous_scale=orange_scale(),
                hover_data={"total_revenue": ":,.2f"},
                labels={"total_revenue": "Revenue (£)", "country": "Country"}
            )
            fig.update_layout(
                showlegend=False,
                coloraxis_showscale=False,
                xaxis_title="Revenue (£)",
                yaxis_title=""
            )
            style_chart(fig, height=420)
            st.plotly_chart(fig, use_container_width=True)

        st.divider()
        st.subheader("Monthly Revenue Trend")
        st.markdown(
            '<div class="section-note">Hover over the line to inspect revenue for each month.</div>',
            unsafe_allow_html=True
        )
        monthly_plot = monthly.copy()
        monthly_plot["month"] = monthly_plot["month"].astype(str)
        monthly_plot = monthly_plot.sort_values("month")

        fig = px.line(
            monthly_plot,
            x="month",
            y="total_revenue",
            markers=True,
            hover_data={"total_revenue": ":,.2f"},
            labels={"month": "Month", "total_revenue": "Revenue (£)"}
        )
        fig.update_traces(
            line=dict(color=accent, width=3),
            marker=dict(color=accent, size=8)
        )
        style_chart(fig, height=360)
        st.plotly_chart(fig, use_container_width=True)

    # ---------------- PRODUCTS ----------------
    elif page == "Products":
        st.subheader("Product Performance")
        st.markdown(
            '<div class="section-note">Search, rank and download the product summary.</div>',
            unsafe_allow_html=True
        )

        search = st.text_input(
            "Search by product description or stock code",
            placeholder="Type a product name or stock code"
        )
        sort_order = st.selectbox(
            "Sort products by",
            ["Highest revenue", "Lowest revenue", "Highest quantity"]
        )

        filtered = products.copy()
        if search:
            desc_match = filtered["description"].astype(str).str.contains(
                search, case=False, na=False
            )
            code_match = filtered["stock_code"].astype(str).str.contains(
                search, case=False, na=False
            )
            filtered = filtered[desc_match | code_match]

        if sort_order == "Highest revenue":
            filtered = filtered.sort_values("total_revenue", ascending=False)
        elif sort_order == "Lowest revenue":
            filtered = filtered.sort_values("total_revenue", ascending=True)
        elif "total_quantity" in filtered.columns:
            filtered = filtered.sort_values("total_quantity", ascending=False)

        st.write(f"Matching products: {len(filtered):,}")
        st.dataframe(filtered, use_container_width=True, hide_index=True)

        st.download_button(
            "Download Product Summary CSV",
            data=filtered.to_csv(index=False).encode("utf-8"),
            file_name="products_summary.csv",
            mime="text/csv"
        )

    # ---------------- COUNTRY ANALYSIS ----------------
    elif page == "Country Analysis":
        st.subheader("Country Sales Comparison")
        st.markdown(
            '<div class="section-note">Select one or more countries to compare their performance.</div>',
            unsafe_allow_html=True
        )

        available_countries = sorted(
            countries["country"].dropna().astype(str).unique().tolist()
        )
        selected = st.multiselect(
            "Countries",
            options=available_countries,
            default=available_countries[:5]
        )
        filtered = countries[countries["country"].astype(str).isin(selected)].copy()

        a, b = st.columns(2)
        a.metric("Selected Revenue", f"£{filtered['total_revenue'].fillna(0).sum():,.2f}")
        b.metric("Selected Quantity", f"{filtered['total_quantity'].fillna(0).sum():,.0f}")

        chart_data = filtered.sort_values("total_revenue")
        fig = px.bar(
            chart_data,
            x="total_revenue",
            y="country",
            orientation="h",
            color="total_revenue",
            color_continuous_scale=orange_scale(),
            hover_data={"total_revenue": ":,.2f"},
            labels={"total_revenue": "Revenue (£)", "country": "Country"}
        )
        fig.update_layout(
            showlegend=False,
            coloraxis_showscale=False,
            xaxis_title="Revenue (£)",
            yaxis_title=""
        )
        style_chart(fig, height=max(350, min(650, 38 * len(chart_data) + 100)))
        st.plotly_chart(fig, use_container_width=True)

        st.dataframe(
            filtered.sort_values("total_revenue", ascending=False),
            use_container_width=True,
            hide_index=True
        )
        st.download_button(
            "Download Country Summary CSV",
            data=filtered.to_csv(index=False).encode("utf-8"),
            file_name="country_summary.csv",
            mime="text/csv"
        )

    # ---------------- MONTHLY ANALYSIS ----------------
    elif page == "Monthly Analysis":
        st.subheader("Monthly Performance")
        st.markdown(
            '<div class="section-note">Compare monthly revenue and quantities from the summary table.</div>',
            unsafe_allow_html=True
        )

        monthly_plot = monthly.copy()
        monthly_plot["month"] = monthly_plot["month"].astype(str)
        monthly_plot = monthly_plot.sort_values("month")

        if len(monthly_plot) > 1:
            month_options = ["All months"] + monthly_plot["month"].tolist()
            month_choice = st.selectbox("Filter month", month_options)
            if month_choice != "All months":
                monthly_plot = monthly_plot[monthly_plot["month"] == month_choice]

        a, b = st.columns(2)
        a.metric("Revenue in View", f"£{monthly_plot['total_revenue'].fillna(0).sum():,.2f}")
        b.metric("Quantity in View", f"{monthly_plot['total_quantity'].fillna(0).sum():,.0f}")

        fig = px.bar(
            monthly_plot,
            x="month",
            y="total_revenue",
            color="total_revenue",
            color_continuous_scale=orange_scale(),
            hover_data={"total_revenue": ":,.2f"},
            labels={"month": "Month", "total_revenue": "Revenue (£)"}
        )
        fig.update_layout(
            showlegend=False,
            coloraxis_showscale=False,
            xaxis_title="Month",
            yaxis_title="Revenue (£)"
        )
        style_chart(fig, height=360)
        st.plotly_chart(fig, use_container_width=True)

        st.dataframe(monthly_plot, use_container_width=True, hide_index=True)
        st.download_button(
            "Download Monthly Summary CSV",
            data=monthly_plot.to_csv(index=False).encode("utf-8"),
            file_name="monthly_summary.csv",
            mime="text/csv"
        )

    # ---------------- ABOUT ----------------
    elif page == "About":
        st.subheader("Project Information")
        st.write(
            "This project analyzes online retail transactions and displays "
            "summarized business results in an interactive dashboard."
        )

        st.markdown("**Technologies used**")
        st.markdown(
            "- Apache Spark (PySpark) for data processing\n"
            "- Apache Cassandra for storing summary tables\n"
            "- Streamlit for the dashboard interface\n"
            "- Pandas for data handling\n"
            "- Plotly for interactive visualizations"
        )

        st.markdown("**Project objectives**")
        st.markdown(
            "- Identify products generating the most revenue\n"
            "- Compare sales across countries\n"
            "- Analyze monthly revenue trends\n"
            "- Search and filter product information\n"
            "- Download summary reports"
        )

except Exception as error:
    st.error("The dashboard could not load data from Cassandra.")
    st.write(
        "Confirm Cassandra is running and the ecommerce keyspace contains "
        "products_summary, country_summary and monthly_summary."
    )
    st.code(f"{type(error).__name__}: {error}")
