import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(
    page_title="Exoplanet Explorer",
    page_icon="🪐",
    layout="wide"
)

st.title("🪐 Exoplanet Explorer")
st.write(
    "Explore planets beyond our Solar System "
    "using NASA Exoplanet Archive data."
)

@st.cache_data
def load_data():
    url = (
        "https://exoplanetarchive.ipac.caltech.edu/"
        "TAP/sync?query=select+pl_name,hostname,"
        "discoverymethod,pl_rade,pl_orbper+from+pscomppars"
        "+where+pl_name+is+not+null&format=csv"
    )
    return pd.read_csv(url)

try:
    df = load_data()
except Exception as e:
    st.error("NASA data could not be loaded. Please try again.")
    st.stop()

st.sidebar.header("Search & Filters")

search = st.sidebar.text_input("Search planet name")

methods = sorted(
    df["discoverymethod"].dropna().unique().tolist()
)
selected_methods = st.sidebar.multiselect(
    "Discovery method",
    methods,
    default=methods
)

radius_range = st.sidebar.slider(
    "Planet radius (Earth radii)",
    min_value=0.0,
    max_value= float(
        min(100, max(1, df["pl_rade"].max()))
    ),
    value=(0.0, float(
        min(100, max(1, df["pl_rade"].max()))
    ))
)

filtered = df[
    df["discoverymethod"].isin(selected_methods)
].copy()

filtered = filtered[
    filtered["pl_rade"].between(
        radius_range[0], radius_range[1]
    )
]

if search:
    filtered = filtered[
        filtered["pl_name"].str.contains(
            search, case=False, na=False
        )
    ]

st.subheader("Explore Exoplanets")
st.metric("Matching planets", len(filtered))

st.dataframe(
    filtered[
        ["pl_name", "hostname", "discoverymethod",
         "pl_rade", "pl_orbper"]
    ].head(500),
    use_container_width=True
)

st.subheader("Planet Radius vs Orbital Period")

chart_data = filtered.dropna(
    subset=["pl_rade", "pl_orbper"]
)

chart_data = chart_data[
    (chart_data["pl_rade"] > 0) &
    (chart_data["pl_orbper"] > 0)
]

if not chart_data.empty:
    fig = px.scatter(
        chart_data,
        x="pl_orbper",
        y="pl_rade",
        hover_name="pl_name",
        color="discoverymethod",
        log_x=True,
        log_y=True,
        labels={
            "pl_orbper": "Orbital Period (days)",
            "pl_rade": "Planet Radius (Earth radii)",
            "discoverymethod": "Discovery Method"
        },
        title="Exoplanet Size and Orbital Period"
    )
    st.plotly_chart(fig, use_container_width=True)
else:
    st.info("No planets match the current filters.")

st.subheader("Planet Details")

if not filtered.empty:
    planet_name = st.selectbox(
        "Choose a planet",
        filtered["pl_name"].dropna().unique()
    )

    planet = filtered[
        filtered["pl_name"] == planet_name
    ].iloc[0]

    col1, col2, col3 = st.columns(3)

    col1.metric(
        "Host Star",
        str(planet["hostname"])
    )
    col2.metric(
        "Radius (Earth radii)",
        str(planet["pl_rade"])
    )
    col3.metric(
        "Orbital Period (days)",
        str(planet["pl_orbper"])
    )

    st.write(
        "**Discovery method:**",
        str(planet["discoverymethod"])
    )
