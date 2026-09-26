import streamlit as st
import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
import sqlite3


# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="Chennai Metro Analytics",
    page_icon="🚇",
    layout="wide",
    initial_sidebar_state="expanded"
)


# =========================================================
# CSS
# =========================================================

st.markdown("""
<style>

.main {
    background-color: #f5f7fa;
}

.block-container {
    padding-top: 1.5rem;
    padding-bottom: 2rem;
}

.dashboard-title {
    font-size: 36px;
    font-weight: 700;
    margin-bottom: 5px;
}

.dashboard-subtitle {
    font-size: 17px;
    color: #666;
    margin-bottom: 25px;
}

.section-title {
    font-size: 24px;
    font-weight: 650;
    margin-top: 15px;
    margin-bottom: 15px;
}

[data-testid="stMetric"] {
    background-color: white;
    border-radius: 12px;
    padding: 18px;
    border: 1px solid #e6e9ef;
    box-shadow: 0 2px 8px rgba(0,0,0,0.05);
}

[data-testid="stSidebar"] {
    border-right: 1px solid #e6e9ef;
}

.about-card {
    background-color: white;
    padding: 22px;
    border-radius: 14px;
    border: 1px solid #e6e9ef;
    margin-bottom: 18px;
}

</style>
""", unsafe_allow_html=True)


# =========================================================
# FILE PATHS
# =========================================================

BASE = "data/cmrl/"

STATION_FLOW_FILE = BASE + "cmrl_stationflow_daily.csv"
HOURLY_FILE = BASE + "cmrl_hourly_ridership.csv"
TICKET_FILE = BASE + "cmrl_ticket_mix.csv"
MONTHLY_FILE = BASE + "cmrl_system_monthly.csv"
SUMMARY_FILE = BASE + "cmrl_station_summary.csv"
STATIONS_FILE = BASE + "chennai_metro_stations.csv"
CATCHMENT_FILE = BASE + "chennai_station_catchment_features.csv"
PREDICTION_FILE = BASE + "chennai_metro_ridership_predictions.csv"


# =========================================================
# LOAD DATA
# =========================================================

@st.cache_data
def load_data():

    station_flow = pd.read_csv(
        STATION_FLOW_FILE
    )

    hourly = pd.read_csv(
        HOURLY_FILE
    )

    tickets = pd.read_csv(
        TICKET_FILE
    )

    monthly = pd.read_csv(
        MONTHLY_FILE
    )

    summary = pd.read_csv(
        SUMMARY_FILE
    )

    stations = pd.read_csv(
        STATIONS_FILE
    )

    catchment = pd.read_csv(
        CATCHMENT_FILE
    )

    predictions = pd.read_csv(
        PREDICTION_FILE
    )

    station_flow["date"] = pd.to_datetime(
        station_flow["date"]
    )

    hourly["date"] = pd.to_datetime(
        hourly["date"]
    )

    tickets["date"] = pd.to_datetime(
        tickets["date"]
    )

    return (
        station_flow,
        hourly,
        tickets,
        monthly,
        summary,
        stations,
        catchment,
        predictions
    )


(
    station_flow,
    hourly,
    tickets,
    monthly,
    summary,
    stations,
    catchment,
    predictions
) = load_data()


# =========================================================
# DATABASE
# =========================================================

conn = sqlite3.connect(
    "data/web_analytics.db",
    check_same_thread=False
)

cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS visits (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    page TEXT
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS route_searches (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    source TEXT,
    destination TEXT
)
""")

conn.commit()


# =========================================================
# CREATE METRO NETWORK
# =========================================================
#
# The station master contains station coordinates and
# line information but does not provide explicit
# source/destination passenger journeys.
#
# Therefore we create network connections between
# consecutive stations along each metro corridor using
# their geographic ordering.
#
# Passenger boardings remain station-level attributes.
# =========================================================

def create_metro_graph(stations_df):

    graph = nx.Graph()

    for _, row in stations_df.iterrows():

        graph.add_node(
            row["name"],
            station_id=row["station_id"],
            line=row["line"],
            phase=row["phase"],
            latitude=row["latitude"],
            longitude=row["longitude"]
        )

    # Connect consecutive stations within each line.
    # Coordinates are used to obtain an approximate
    # corridor order.

    for line in stations_df["line"].dropna().unique():

        line_df = stations_df[
            stations_df["line"] == line
        ].copy()

        if len(line_df) < 2:
            continue

        # PCA-like simple ordering using longitude/latitude.
        # The direction with the larger spread is used.

        lat_range = (
            line_df["latitude"].max()
            - line_df["latitude"].min()
        )

        lon_range = (
            line_df["longitude"].max()
            - line_df["longitude"].min()
        )

        if lon_range >= lat_range:

            line_df = line_df.sort_values(
                "longitude"
            )

        else:

            line_df = line_df.sort_values(
                "latitude"
            )

        rows = line_df.to_dict(
            "records"
        )

        for i in range(
            len(rows) - 1
        ):

            station_a = rows[i]["name"]
            station_b = rows[i + 1]["name"]

            if station_a != station_b:

                graph.add_edge(
                    station_a,
                    station_b,
                    line=line
                )

    return graph


G = create_metro_graph(
    stations
)


# =========================================================
# GLOBAL METRICS
# =========================================================

total_station_records = len(
    station_flow
)

total_boardings = station_flow[
    "boardings"
].sum()

number_of_stations = stations[
    "name"
].nunique()

number_of_lines = stations[
    "line"
].nunique()

number_of_days = station_flow[
    "date"
].nunique()

peak_hour_row = (
    hourly.groupby("hour")["boardings"]
    .sum()
    .reset_index()
    .sort_values(
        "boardings",
        ascending=False
    )
    .iloc[0]
)

peak_hour = int(
    peak_hour_row["hour"]
)

peak_hour_boardings = int(
    peak_hour_row["boardings"]
)


# =========================================================
# SIDEBAR
# =========================================================

st.sidebar.markdown(
    """
    <div style="font-size:24px;font-weight:700;">
    🚇 Chennai Metro Analytics
    </div>
    """,
    unsafe_allow_html=True
)

st.sidebar.caption(
    "Passenger Flow & Mobility Network Analytics"
)

st.sidebar.divider()

page = st.sidebar.radio(
    "Navigation",
    [
        "Dashboard",
        "Network",
        "Passenger Flow",
        "Station Analysis",
        "Peak Hour",
        "Web Analytics",
        "Predictions",
        "Ticket Analytics",
        "Reports",
        "Data Management",
        "About Project"
    ]
)

st.sidebar.divider()

st.sidebar.caption(
    f"Stations: {number_of_stations}"
)

st.sidebar.caption(
    f"Metro Lines: {number_of_lines}"
)

st.sidebar.caption(
    f"Observed Days: {number_of_days}"
)


# =========================================================
# LOG PAGE VISIT
# =========================================================

cursor.execute(
    "INSERT INTO visits (page) VALUES (?)",
    (page,)
)

conn.commit()


# =========================================================
# DASHBOARD
# =========================================================

if page == "Dashboard":

    st.markdown(
        '<div class="dashboard-title">'
        '🚇 Chennai Metro Analytics'
        '</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="dashboard-subtitle">'
        'Web-Based Chennai Metro Passenger Flow '
        'and Mobility Network Analytics'
        '</div>',
        unsafe_allow_html=True
    )

    st.divider()

    col1, col2, col3, col4 = st.columns(4)

    col1.metric(
        "🚉 Stations",
        number_of_stations
    )

    col2.metric(
        "🚇 Metro Lines",
        number_of_lines
    )

    col3.metric(
        "👥 Boarding Records",
        f"{total_station_records:,}"
    )

    col4.metric(
        "📅 Observed Days",
        number_of_days
    )

    st.divider()

    st.subheader(
        "📈 System-Wide Passenger Flow"
    )

    daily_flow = (
        station_flow
        .groupby("date")["boardings"]
        .sum()
    )

    st.line_chart(
        daily_flow,
        use_container_width=True
    )

    st.divider()

    col1, col2 = st.columns(2)

    with col1:

        st.subheader(
            "⏰ Hourly Passenger Flow"
        )

        hourly_flow = (
            hourly
            .groupby("hour")["boardings"]
            .sum()
        )

        st.line_chart(
            hourly_flow,
            use_container_width=True
        )

    with col2:

        st.subheader(
            "🚉 Station Passenger Flow"
        )

        station_totals = (
            station_flow
            .groupby("cmrl_name")["boardings"]
            .sum()
            .sort_values(
                ascending=False
            )
            .head(15)
        )

        st.bar_chart(
            station_totals,
            use_container_width=True
        )

    st.divider()

    st.subheader(
        "🔥 Peak Hour"
    )

    col1, col2 = st.columns(2)

    col1.metric(
        "Peak Hour",
        f"{peak_hour}:00"
    )

    col2.metric(
        "Total Boardings During Peak Hour",
        f"{peak_hour_boardings:,}"
    )

    st.info(
        "The passenger-flow dataset records station "
        "boardings rather than individual origin-destination "
        "journeys."
    )


# =========================================================
# NETWORK
# =========================================================

elif page == "Network":

    st.markdown(
        '<div class="dashboard-title">'
        '🕸️ Chennai Metro Network'
        '</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="dashboard-subtitle">'
        'Graph representation of Chennai Metro stations '
        'and corridor connections'
        '</div>',
        unsafe_allow_html=True
    )

    st.divider()

    col1, col2, col3, col4 = st.columns(4)

    col1.metric(
        "🚉 Nodes",
        G.number_of_nodes()
    )

    col2.metric(
        "🔗 Connections",
        G.number_of_edges()
    )

    col3.metric(
        "📐 Network Density",
        f"{nx.density(G):.3f}"
    )

    col4.metric(
        "📊 Average Degree",
        f"{sum(dict(G.degree()).values()) / G.number_of_nodes():.2f}"
    )

    st.divider()

    st.subheader(
        "📍 Station Centrality"
    )

    degree = nx.degree_centrality(G)

    betweenness = nx.betweenness_centrality(
        G
    )

    closeness = nx.closeness_centrality(
        G
    )

    network_table = pd.DataFrame({

        "Station": list(G.nodes()),

        "Degree Centrality": [
            round(degree[n], 4)
            for n in G.nodes()
        ],

        "Betweenness Centrality": [
            round(betweenness[n], 4)
            for n in G.nodes()
        ],

        "Closeness Centrality": [
            round(closeness[n], 4)
            for n in G.nodes()
        ]

    })

    station_flow_total = (
        station_flow
        .groupby("cmrl_name")["boardings"]
        .sum()
        .reset_index()
    )

    station_flow_total = (
        station_flow_total
        .rename(
            columns={
                "cmrl_name": "Station",
                "boardings": "Total Boardings"
            }
        )
    )

    network_table = network_table.merge(
        station_flow_total,
        on="Station",
        how="left"
    )

    network_table["Total Boardings"] = (
        network_table["Total Boardings"]
        .fillna(0)
        .astype(int)
    )

    st.dataframe(
        network_table.sort_values(
            "Degree Centrality",
            ascending=False
        ),
        use_container_width=True,
        hide_index=True
    )

    st.divider()

    st.subheader(
        "📈 Network Centrality"
    )

    centrality_chart = network_table.set_index(
        "Station"
    )[
        [
            "Degree Centrality",
            "Betweenness Centrality",
            "Closeness Centrality"
        ]
    ].sort_values(
        "Degree Centrality",
        ascending=False
    ).head(20)

    st.bar_chart(
        centrality_chart,
        use_container_width=True
    )

    st.divider()

    st.subheader(
        "🚇 Metro Line Structure"
    )

    line_counts = (
        stations
        .groupby("line")["name"]
        .count()
        .sort_values(
            ascending=False
        )
    )

    st.bar_chart(
        line_counts,
        use_container_width=True
    )

    st.divider()

    st.subheader(
        "🗺️ Station Coordinates"
    )

    map_data = stations[
        [
            "latitude",
            "longitude"
        ]
    ].dropna()

    map_data = map_data.rename(
        columns={
            "latitude": "lat",
            "longitude": "lon"
        }
    )

    st.map(
        map_data,
        use_container_width=True
    )

    st.divider()

    st.info(
        "Network connections are constructed from the "
        "station master and metro corridor ordering. "
        "The passenger-flow dataset itself contains "
        "station entries, not individual passenger "
        "origin-destination journeys."
    )


# =========================================================
# PASSENGER FLOW
# =========================================================

elif page == "Passenger Flow":

    st.markdown(
        '<div class="dashboard-title">'
        '📈 Passenger Flow Analysis'
        '</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="dashboard-subtitle">'
        'Analyze daily station-level passenger boardings'
        '</div>',
        unsafe_allow_html=True
    )

    st.divider()

    col1, col2, col3 = st.columns(3)

    min_date = station_flow["date"].min().date()
    max_date = station_flow["date"].max().date()

    with col1:

        date_range = st.date_input(
            "📅 Date Range",
            value=(min_date, max_date),
            min_value=min_date,
            max_value=max_date
        )

    with col2:

        selected_lines = st.multiselect(
            "🚇 Metro Line",
            sorted(
                station_flow["line"]
                .dropna()
                .unique()
            ),
            default=sorted(
                station_flow["line"]
                .dropna()
                .unique()
            )
        )

    with col3:

        station_options = sorted(
            station_flow["cmrl_name"]
            .dropna()
            .unique()
        )

        selected_stations = st.multiselect(
            "🚉 Stations",
            station_options,
            default=station_options
        )

    if isinstance(date_range, tuple):

        if len(date_range) == 2:

            start_date = pd.Timestamp(
                date_range[0]
            )

            end_date = pd.Timestamp(
                date_range[1]
            )

        else:

            start_date = pd.Timestamp(
                date_range[0]
            )

            end_date = start_date

    else:

        start_date = pd.Timestamp(
            date_range
        )

        end_date = start_date

    filtered = station_flow[
        (station_flow["date"] >= start_date)
        &
        (station_flow["date"] <= end_date)
        &
        (station_flow["line"].isin(
            selected_lines
        ))
        &
        (station_flow["cmrl_name"].isin(
            selected_stations
        ))
    ]

    st.divider()

    col1, col2, col3, col4 = st.columns(4)

    col1.metric(
        "Records",
        len(filtered)
    )

    col2.metric(
        "Boardings",
        f"{filtered['boardings'].sum():,}"
    )

    col3.metric(
        "Average",
        f"{filtered['boardings'].mean():,.0f}"
        if len(filtered) > 0
        else "0"
    )

    col4.metric(
        "Maximum",
        f"{filtered['boardings'].max():,}"
        if len(filtered) > 0
        else "0"
    )

    if len(filtered) == 0:

        st.warning(
            "No records match the selected filters."
        )

    else:

        st.divider()

        st.subheader(
            "📊 Daily Passenger Flow"
        )

        daily = (
            filtered
            .groupby("date")["boardings"]
            .sum()
        )

        st.line_chart(
            daily,
            use_container_width=True
        )

        st.divider()

        st.subheader(
            "🚉 Station Passenger Flow"
        )

        station_chart = (
            filtered
            .groupby("cmrl_name")["boardings"]
            .sum()
            .sort_values(
                ascending=False
            )
            .head(20)
        )

        st.bar_chart(
            station_chart,
            use_container_width=True
        )

        st.divider()

        st.subheader(
            "📋 Passenger Data"
        )

        display = filtered.copy()

        display["date"] = display[
            "date"
        ].dt.strftime("%Y-%m-%d")

        st.dataframe(
            display,
            use_container_width=True,
            hide_index=True
        )

        st.download_button(
            "⬇️ Download Filtered Data",
            display.to_csv(
                index=False
            ).encode("utf-8"),
            "cmrl_filtered_station_flow.csv",
            "text/csv"
        )


# =========================================================
# STATION ANALYSIS
# =========================================================

elif page == "Station Analysis":

    st.markdown(
        '<div class="dashboard-title">'
        '🚉 Station Analysis'
        '</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="dashboard-subtitle">'
        'Detailed passenger and built-environment '
        'analysis of Chennai Metro stations'
        '</div>',
        unsafe_allow_html=True
    )

    st.divider()

    station_names = sorted(
        stations["name"].dropna().unique()
    )

    selected_station = st.selectbox(
        "Select Station",
        station_names
    )

    station_info = stations[
        stations["name"] == selected_station
    ]

    station_flow_info = station_flow[
        station_flow["cmrl_name"] == selected_station
    ]

    if len(station_flow_info) == 0:

        # Try canonical CMRL name mapping
        matching = summary[
            summary["canonical_station_name"]
            == selected_station
        ]

        if len(matching) > 0:

            cmrl_name = matching.iloc[0][
                "cmrl_name"
            ]

            station_flow_info = station_flow[
                station_flow["cmrl_name"]
                == cmrl_name
            ]

    col1, col2, col3, col4 = st.columns(4)

    total = station_flow_info[
        "boardings"
    ].sum()

    average = station_flow_info[
        "boardings"
    ].mean()

    maximum = station_flow_info[
        "boardings"
    ].max()

    line = (
        station_info.iloc[0]["line"]
        if len(station_info) > 0
        else "N/A"
    )

    col1.metric(
        "Total Boardings",
        f"{total:,.0f}"
    )

    col2.metric(
        "Average Daily",
        f"{average:,.0f}"
    )

    col3.metric(
        "Maximum Daily",
        f"{maximum:,.0f}"
    )

    col4.metric(
        "Metro Line",
        line
    )

    st.divider()

    st.subheader(
        "📈 Station Ridership Over Time"
    )

    if len(station_flow_info) > 0:

        station_daily = (
            station_flow_info
            .groupby("date")["boardings"]
            .sum()
        )

        st.line_chart(
            station_daily,
            use_container_width=True
        )

    else:

        st.info(
            "No daily station-flow records are "
            "available for this station."
        )

    st.divider()

    st.subheader(
        "🌆 Station Information"
    )

    if len(station_info) > 0:

        info = station_info.iloc[0]

        c1, c2, c3, c4 = st.columns(4)

        c1.metric(
            "Phase",
            str(info["phase"])
        )

        c2.metric(
            "Layout",
            str(info["layout"])
        )

        c3.metric(
            "Latitude",
            f"{info['latitude']:.5f}"
        )

        c4.metric(
            "Longitude",
            f"{info['longitude']:.5f}"
        )

    st.divider()

    st.subheader(
        "🏙️ Catchment Features"
    )

    catch = catchment[
        catchment["name"] == selected_station
    ]

    if len(catch) > 0:

        row = catch.iloc[0]

        c1, c2, c3 = st.columns(3)

        c1.metric(
            "Population",
            f"{row['population']:,.0f}"
        )

        c2.metric(
            "Population Density",
            f"{row['population_density']:,.0f}"
        )

        c3.metric(
            "POIs",
            f"{row['poi_total']:,.0f}"
        )

        c1, c2, c3 = st.columns(3)

        c1.metric(
            "Bus Stops within 500m",
            f"{row['bus_stops_500m']:,.0f}"
        )

        c2.metric(
            "Metro Degree",
            f"{row['metro_degree']:.0f}"
        )

        c3.metric(
            "Interchange",
            "Yes"
            if row["is_interchange"]
            else "No"
        )


# =========================================================
# PEAK HOUR
# =========================================================

elif page == "Peak Hour":

    st.markdown(
        '<div class="dashboard-title">'
        '⏰ Peak-Hour Analysis'
        '</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="dashboard-subtitle">'
        'System-wide hourly passenger boarding patterns'
        '</div>',
        unsafe_allow_html=True
    )

    st.divider()

    hourly_clean = hourly[
        hourly["is_partial"] == False
    ].copy()

    hourly_totals = (
        hourly_clean
        .groupby("hour")["boardings"]
        .sum()
    )

    st.subheader(
        "📈 Hourly Passenger Flow"
    )

    st.line_chart(
        hourly_totals,
        use_container_width=True
    )

    st.divider()

    peak = hourly_totals.idxmax()

    peak_value = hourly_totals.max()

    col1, col2, col3 = st.columns(3)

    col1.metric(
        "Peak Hour",
        f"{int(peak):02d}:00"
    )

    col2.metric(
        "Peak Boardings",
        f"{int(peak_value):,}"
    )

    col3.metric(
        "Average Hourly Boardings",
        f"{int(hourly_totals.mean()):,}"
    )

    st.divider()

    st.subheader(
        "🏆 Top 10 Busiest Hours"
    )

    top_hours = (
        hourly_totals
        .sort_values(
            ascending=False
        )
        .head(10)
        .reset_index()
    )

    top_hours["hour"] = (
        top_hours["hour"]
        .astype(str)
        + ":00"
    )

    top_hours = top_hours.rename(
        columns={
            "hour": "Hour",
            "boardings": "Boardings"
        }
    )

    st.dataframe(
        top_hours,
        use_container_width=True,
        hide_index=True
    )

    st.divider()

    st.subheader(
        "📅 Daily Peak Hour"
    )

    daily_hour = (
        hourly_clean
        .groupby(
            ["date", "hour"]
        )["boardings"]
        .sum()
        .reset_index()
    )

    idx = daily_hour.groupby(
        "date"
    )["boardings"].idxmax()

    daily_peak = daily_hour.loc[
        idx
    ].sort_values(
        "date"
    )

    daily_peak["date"] = (
        daily_peak["date"]
        .dt.strftime("%Y-%m-%d")
    )

    st.dataframe(
        daily_peak,
        use_container_width=True,
        hide_index=True
    )


# =========================================================
# WEB ANALYTICS
# =========================================================

elif page == "Web Analytics":

    st.markdown(
        '<div class="dashboard-title">'
        '🌐 Web Analytics'
        '</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="dashboard-subtitle">'
        'Track dashboard usage and station-analysis searches'
        '</div>',
        unsafe_allow_html=True
    )

    total_visits = cursor.execute(
        "SELECT COUNT(*) FROM visits"
    ).fetchone()[0]

    page_visits = pd.read_sql_query(
        """
        SELECT page, COUNT(*) AS visits
        FROM visits
        GROUP BY page
        ORDER BY visits DESC
        """,
        conn
    )

    total_searches = cursor.execute(
        "SELECT COUNT(*) FROM route_searches"
    ).fetchone()[0]

    route_searches = pd.read_sql_query(
        """
        SELECT
            source,
            destination,
            COUNT(*) AS searches
        FROM route_searches
        GROUP BY source, destination
        ORDER BY searches DESC
        """,
        conn
    )

    col1, col2, col3 = st.columns(3)

    col1.metric(
        "👀 Page Visits",
        total_visits
    )

    col2.metric(
        "🧭 Network Searches",
        total_searches
    )

    col3.metric(
        "📄 Pages Used",
        len(page_visits)
    )

    st.divider()

    st.subheader(
        "📊 Page Usage"
    )

    if len(page_visits) > 0:

        st.bar_chart(
            page_visits.set_index(
                "page"
            ),
            use_container_width=True
        )

        st.dataframe(
            page_visits,
            use_container_width=True,
            hide_index=True
        )

    st.info(
        "Web analytics records usage of this Streamlit "
        "application. It is separate from the CMRL "
        "transport passenger dataset."
    )


# =========================================================
# PREDICTIONS
# =========================================================

elif page == "Predictions":

    st.markdown(
        '<div class="dashboard-title">'
        '🤖 Ridership Prediction'
        '</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="dashboard-subtitle">'
        'Station-level demand predictions from the CMRL dataset'
        '</div>',
        unsafe_allow_html=True
    )

    st.divider()

    st.subheader(
        "📊 Existing CMRL Prediction Results"
    )

    prediction_display = predictions[
        [
            "station_id",
            "name",
            "Line",
            "phase",
            "prediction",
            "lower",
            "upper"
        ]
    ].copy()

    prediction_display = prediction_display.rename(
        columns={
            "station_id": "Station ID",
            "name": "Station",
            "Line": "Line",
            "phase": "Phase",
            "prediction": "Prediction",
            "lower": "Lower Bound",
            "upper": "Upper Bound"
        }
    )

    st.dataframe(
        prediction_display,
        use_container_width=True,
        hide_index=True
    )

    st.divider()

    selected_station = st.selectbox(
        "Select Station",
        prediction_display["Station"].tolist()
    )

    selected_prediction = prediction_display[
        prediction_display["Station"]
        == selected_station
    ].iloc[0]

    col1, col2, col3 = st.columns(3)

    col1.metric(
        "Predicted Ridership",
        f"{selected_prediction['Prediction']:,.0f}"
    )

    col2.metric(
        "Lower Bound",
        f"{selected_prediction['Lower Bound']:,.0f}"
    )

    col3.metric(
        "Upper Bound",
        f"{selected_prediction['Upper Bound']:,.0f}"
    )

    st.divider()

    st.subheader(
        "📈 Top Predicted Station Demand"
    )

    top_predictions = (
        prediction_display
        .sort_values(
            "Prediction",
            ascending=False
        )
        .head(20)
        .set_index("Station")[
            "Prediction"
        ]
    )

    st.bar_chart(
        top_predictions,
        use_container_width=True
    )

    st.info(
        "The prediction file supplied with the CMRL dataset "
        "contains station-level model predictions and 90% "
        "confidence intervals. The application displays "
        "those supplied model results rather than claiming "
        "to reproduce the original training process."
    )


# =========================================================
# TICKET ANALYTICS
# =========================================================

elif page == "Ticket Analytics":

    st.markdown(
        '<div class="dashboard-title">'
        '💳 Ticket & Payment Analytics'
        '</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="dashboard-subtitle">'
        'Analysis of Chennai Metro ticketing and payment media'
        '</div>',
        unsafe_allow_html=True
    )

    st.divider()

    ticket = tickets.copy()

    ticket["date"] = pd.to_datetime(
        ticket["date"]
    )

    col1, col2 = st.columns(2)

    with col1:

        start = ticket["date"].min().date()
        end = ticket["date"].max().date()

        selected_dates = st.date_input(
            "Date Range",
            value=(start, end),
            min_value=start,
            max_value=end
        )

    filtered_ticket = ticket.copy()

    if isinstance(
        selected_dates,
        tuple
    ) and len(selected_dates) == 2:

        filtered_ticket = filtered_ticket[
            (
                filtered_ticket["date"]
                >= pd.Timestamp(
                    selected_dates[0]
                )
            )
            &
            (
                filtered_ticket["date"]
                <= pd.Timestamp(
                    selected_dates[1]
                )
            )
        ]

    total_tickets = filtered_ticket[
        "totalTickets"
    ].sum()

    total_ncmc = filtered_ticket[
        "noOfNCMCcard"
    ].sum()

    total_mobile = filtered_ticket[
        "noOfMobileQR"
    ].sum()

    total_paper = filtered_ticket[
        "noOfPaperQR"
    ].sum()

    col1, col2, col3, col4 = st.columns(4)

    col1.metric(
        "Total Tickets",
        f"{total_tickets:,}"
    )

    col2.metric(
        "NCMC",
        f"{total_ncmc:,}"
    )

    col3.metric(
        "Mobile QR",
        f"{total_mobile:,}"
    )

    col4.metric(
        "Paper QR",
        f"{total_paper:,}"
    )

    st.divider()

    ticket_columns = {
        "NCMC": "noOfNCMCcard",
        "Mobile QR": "noOfMobileQR",
        "Paper QR": "noOfPaperQR",
        "Paytm QR": "noOfPaytmQR",
        "WhatsApp QR": "noOfWhatsAppQR",
        "PhonePe QR": "noOfPhonePeQR",
        "ONDC": "noOfONDCQR",
        "Uber QR": "noOfUberQR",
        "Rapido QR": "noOfRapidoQR"
    }

    ticket_totals = {}

    for name, column in ticket_columns.items():

        if column in filtered_ticket.columns:

            ticket_totals[name] = (
                filtered_ticket[column].sum()
            )

    ticket_chart = pd.Series(
        ticket_totals
    ).sort_values(
        ascending=False
    )

    st.subheader(
        "💳 Payment Media Usage"
    )

    st.bar_chart(
        ticket_chart,
        use_container_width=True
    )

    st.divider()

    st.subheader(
        "📈 Daily Ticket Activity"
    )

    daily_ticket = (
        filtered_ticket
        .groupby("date")["totalTickets"]
        .sum()
    )

    st.line_chart(
        daily_ticket,
        use_container_width=True
    )

    st.divider()

    st.subheader(
        "📋 Ticket Dataset"
    )

    st.dataframe(
        filtered_ticket,
        use_container_width=True,
        hide_index=True
    )


# =========================================================
# REPORTS
# =========================================================

elif page == "Reports":

    st.markdown(
        '<div class="dashboard-title">'
        '📋 Chennai Metro Reports'
        '</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="dashboard-subtitle">'
        'Downloadable passenger, station, hourly and '
        'network reports'
        '</div>',
        unsafe_allow_html=True
    )

    st.divider()

    st.subheader(
        "📊 Dataset Summary"
    )

    col1, col2, col3, col4 = st.columns(4)

    col1.metric(
        "Station Records",
        f"{len(station_flow):,}"
    )

    col2.metric(
        "Stations",
        number_of_stations
    )

    col3.metric(
        "Metro Lines",
        number_of_lines
    )

    col4.metric(
        "Observed Days",
        number_of_days
    )

    st.divider()

    st.subheader(
        "🚉 Station Ridership Report"
    )

    station_report = (
        station_flow
        .groupby("cmrl_name")["boardings"]
        .agg(
            Total_Boardings="sum",
            Average_Boardings="mean",
            Maximum_Boardings="max",
            Minimum_Boardings="min"
        )
        .reset_index()
        .rename(
            columns={
                "cmrl_name": "Station"
            }
        )
    )

    station_report[
        "Average_Boardings"
    ] = station_report[
        "Average_Boardings"
    ].round(2)

    st.dataframe(
        station_report.sort_values(
            "Total_Boardings",
            ascending=False
        ),
        use_container_width=True,
        hide_index=True
    )

    st.divider()

    st.subheader(
        "🚇 Line Report"
    )

    line_report = (
        station_flow
        .groupby("line")["boardings"]
        .agg(
            Total_Boardings="sum",
            Average_Boardings="mean",
            Maximum_Boardings="max"
        )
        .reset_index()
    )

    st.dataframe(
        line_report,
        use_container_width=True,
        hide_index=True
    )

    st.divider()

    st.subheader(
        "⏰ Hourly Report"
    )

    hourly_report = (
        hourly
        .groupby("hour")["boardings"]
        .agg(
            Total_Boardings="sum",
            Average_Boardings="mean",
            Maximum_Boardings="max"
        )
        .reset_index()
    )

    st.dataframe(
        hourly_report,
        use_container_width=True,
        hide_index=True
    )

    st.divider()

    st.subheader(
        "🕸️ Network Report"
    )

    # Build the network report here as well.
    # network_table is created only inside the Network page,
    # so it cannot be reused directly from the Reports page.
    degree_report = nx.degree_centrality(G)
    betweenness_report = nx.betweenness_centrality(G)
    closeness_report = nx.closeness_centrality(G)

    report_network = pd.DataFrame({
        "Station": list(G.nodes()),
        "Degree Centrality": [
            round(degree_report[n], 4) for n in G.nodes()
        ],
        "Betweenness Centrality": [
            round(betweenness_report[n], 4) for n in G.nodes()
        ],
        "Closeness Centrality": [
            round(closeness_report[n], 4) for n in G.nodes()
        ]
    })

    report_network = report_network.merge(
        station_flow.groupby("cmrl_name")["boardings"]
        .sum()
        .reset_index()
        .rename(columns={
            "cmrl_name": "Station",
            "boardings": "Total Boardings"
        }),
        on="Station",
        how="left"
    )

    report_network["Total Boardings"] = (
        report_network["Total Boardings"]
        .fillna(0)
        .astype(int)
    )

    st.dataframe(
        report_network,
        use_container_width=True,
        hide_index=True
    )

    st.divider()

    st.subheader(
        "⬇️ Download Reports"
    )

    col1, col2 = st.columns(2)

    with col1:

        st.download_button(
            "🚉 Station Report",
            station_report.to_csv(
                index=False
            ).encode("utf-8"),
            "cmrl_station_report.csv",
            "text/csv",
            use_container_width=True
        )

    with col2:

        st.download_button(
            "🚇 Line Report",
            line_report.to_csv(
                index=False
            ).encode("utf-8"),
            "cmrl_line_report.csv",
            "text/csv",
            use_container_width=True
        )

    col1, col2 = st.columns(2)

    with col1:

        st.download_button(
            "⏰ Hourly Report",
            hourly_report.to_csv(
                index=False
            ).encode("utf-8"),
            "cmrl_hourly_report.csv",
            "text/csv",
            use_container_width=True
        )

    with col2:

        st.download_button(
            "🕸️ Network Report",
            report_network.to_csv(
                index=False
            ).encode("utf-8"),
            "cmrl_network_report.csv",
            "text/csv",
            use_container_width=True
        )


# =========================================================
# DATA MANAGEMENT
# =========================================================

elif page == "Data Management":

    st.markdown(
        '<div class="dashboard-title">'
        '⚙️ CMRL Data Management'
        '</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="dashboard-subtitle">'
        'View and download the imported CMRL datasets'
        '</div>',
        unsafe_allow_html=True
    )

    st.divider()

    st.info(
        "The CMRL source files are treated as source datasets. "
        "This page provides inspection and download tools "
        "rather than modifying the original CMRL records."
    )

    dataset_choice = st.selectbox(
        "Select Dataset",
        [
            "Station Daily Flow",
            "Hourly Ridership",
            "Station Directory",
            "Station Summary",
            "Ticket Mix",
            "Monthly Ridership",
            "Catchment Features",
            "Ridership Predictions"
        ]
    )

    dataset_map = {

        "Station Daily Flow":
            station_flow,

        "Hourly Ridership":
            hourly,

        "Station Directory":
            stations,

        "Station Summary":
            summary,

        "Ticket Mix":
            tickets,

        "Monthly Ridership":
            monthly,

        "Catchment Features":
            catchment,

        "Ridership Predictions":
            predictions
    }

    selected_data = dataset_map[
        dataset_choice
    ]

    st.subheader(
        f"📋 {dataset_choice}"
    )

    st.write(
        f"Rows: {len(selected_data):,}"
    )

    st.dataframe(
        selected_data,
        use_container_width=True,
        hide_index=True
    )

    st.download_button(
        "⬇️ Download Dataset",
        selected_data.to_csv(
            index=False
        ).encode("utf-8"),
        "cmrl_" + dataset_choice.lower()
        .replace(" ", "_")
        + ".csv",
        "text/csv",
        use_container_width=True
    )


# =========================================================
# ABOUT PROJECT
# =========================================================

elif page == "About Project":

    st.markdown(
        '<div class="dashboard-title">'
        '📘 About the Project'
        '</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="dashboard-subtitle">'
        'Web-Based Chennai Metro Passenger Flow '
        'and Mobility Network Analytics'
        '</div>',
        unsafe_allow_html=True
    )

    st.divider()

    st.subheader(
        "🎯 Project Overview"
    )

    st.write(
        "This project is a web-based analytics platform "
        "for examining Chennai Metro passenger flow, "
        "station characteristics and mobility-network "
        "structure."
    )

    st.write(
        "The system combines passenger-flow analysis, "
        "graph analytics, geographic station information, "
        "web analytics and machine-learning results in "
        "one interactive Streamlit application."
    )

    st.divider()

    st.subheader(
        "🎯 Project Objectives"
    )

    objectives = [
        "Analyze passenger boardings across Chennai Metro stations.",
        "Study passenger flow over time.",
        "Identify busy stations and peak hours.",
        "Represent metro stations and corridor connections as a graph.",
        "Calculate network centrality measures.",
        "Visualize station locations geographically.",
        "Analyze ticketing and payment-media usage.",
        "Display station-level ridership predictions.",
        "Track usage of the web application.",
        "Generate downloadable analytical reports."
    ]

    for item in objectives:

        st.write(
            f"• {item}"
        )

    st.divider()

    st.subheader(
        "🛠️ Technologies Used"
    )

    tech = pd.DataFrame({

        "Technology": [
            "Python",
            "Streamlit",
            "Pandas",
            "NetworkX",
            "Scikit-learn",
            "SQLite",
            "Matplotlib"
        ],

        "Purpose": [
            "Application programming and data analysis",
            "Interactive web dashboard",
            "Data processing",
            "Graph and network analysis",
            "Machine-learning analysis",
            "Web analytics storage",
            "Charts and network visualization"
        ]
    })

    st.dataframe(
        tech,
        use_container_width=True,
        hide_index=True
    )

    st.divider()

    st.subheader(
        "🕸️ Graph Analytics"
    )

    graph_methods = pd.DataFrame({

        "Method": [
            "Degree Centrality",
            "Betweenness Centrality",
            "Closeness Centrality",
            "Network Density",
            "Connected Components"
        ],

        "Purpose": [
            "Measures station connectivity.",
            "Measures how often a station lies between other stations.",
            "Measures distance-based accessibility in the network.",
            "Measures overall network connectivity.",
            "Examines groups of connected stations."
        ]
    })

    st.dataframe(
        graph_methods,
        use_container_width=True,
        hide_index=True
    )

    st.divider()

    st.subheader(
        "📊 Dataset"
    )

    col1, col2, col3, col4 = st.columns(4)

    col1.metric(
        "Stations",
        number_of_stations
    )

    col2.metric(
        "Station Flow Records",
        f"{len(station_flow):,}"
    )

    col3.metric(
        "Observed Days",
        number_of_days
    )

    col4.metric(
        "Metro Lines",
        number_of_lines
    )

    st.write(
        "The application uses the supplied CMRL dataset, "
        "including station-level daily boardings, "
        "system-wide hourly ridership, station metadata, "
        "ticketing information, monthly ridership and "
        "station catchment characteristics."
    )

    st.divider()

    st.subheader(
        "🔄 Project Workflow"
    )

    workflow = [
        "CMRL datasets",
        "Data processing with Pandas",
        "Passenger-flow analysis",
        "Metro network construction",
        "Graph analytics",
        "Geographic station analysis",
        "Web analytics with SQLite",
        "Machine-learning prediction results",
        "Interactive Streamlit dashboard",
        "Downloadable reports"
    ]

    for i, step in enumerate(
        workflow,
        start=1
    ):

        st.write(
            f"**{i}.** {step}"
        )

    st.divider()

    st.subheader(
        "🎓 Academic Project"
    )

    st.info(
        "Course: Graph and Web Analytics\n\n"
        "Project: Web-Based Chennai Metro Passenger "
        "Flow and Mobility Network Analytics"
    )

    st.warning(
        "Important: The station-flow data measures "
        "passenger boardings/entries at stations. It does "
        "not directly identify each passenger's origin and "
        "destination station."
    )