from streamlit_echarts5 import st_echarts
import streamlit as st
import pycountry

st.set_page_config(layout="wide")

st.sidebar.title("Controls")

display_mode = st.sidebar.radio(
    "Show data by:",
    ["Region", "Country", "Region + Country"]
)

# Chart type selector
chart_type = st.sidebar.radio(
    "Chart type:",
    ["Heatmap", "Pie Chart"]
)

st.sidebar.markdown("### GDP Statistics")

btn_total_gdp = st.sidebar.button(" Calculate Total GDP ")
btn_avg_gdp = st.sidebar.button(" Calculate Average GDP ")

all_regions = [
    "Asia", "Europe", "Africa",
    "South America", "North America", "Oceania"
]

selected_regions = st.sidebar.multiselect(
    "Select Regions",
    all_regions,
    default=all_regions
)

all_countries = sorted([country.name for country in pycountry.countries])

selected_countries = st.sidebar.multiselect(
    "Select Countries",
    all_countries,
    default=all_countries
)


start_year, end_year = st.sidebar.slider(
    "Select Year Range",
    min_value=1960,
    max_value=2024,
    value=(1960, 2024),
    step=1
)

years = list(range(start_year, end_year + 1))


if display_mode == "Region":
    x_labels = selected_regions
elif display_mode == "Country":
    x_labels = selected_countries
else:
    x_labels = (
        [f"Region: {r}" for r in selected_regions] +
        [f"Country: {c}" for c in selected_countries]
    )


heatmap_data = []
aggregated_gdp = {label: 0 for label in x_labels}

for y_idx, year in enumerate(years):
    for x_idx, label in enumerate(x_labels):
        gdp = (
            (year - 1960) * 10 +
            (x_idx + 1) * 180 +
            len(selected_countries) * 8
        )

        heatmap_data.append([x_idx, y_idx, gdp])
        aggregated_gdp[label] += gdp


if btn_total_gdp:
    st.subheader(" Total GDP ")
    st.metric("Total GDP", f"{12_500_000:,}")

if btn_avg_gdp:
    st.subheader(" Average GDP ")
    st.metric("Average GDP", f"{520_000:,}")

# Chart options
if chart_type == "Heatmap":
    options = {
        "title": {
            "text": f"GDP Heatmap ({display_mode} View)",
            "left": "center"
        },
        "tooltip": {"position": "top"},
        "grid": {"height": "75%", "top": "10%"},
        "xAxis": {
            "type": "category",
            "data": x_labels,
            "name": display_mode,
            "axisLabel": {"rotate": 45}
        },
        "yAxis": {
            "type": "category",
            "data": years,
            "name": "Year"
        },
        "visualMap": {
            "min": 0,
            "max": 4500,
            "calculable": True,
            "orient": "vertical",
            "right": "2%",
            "top": "center"
        },
        "series": [
            {
                "name": "GDP",
                "type": "heatmap",
                "data": heatmap_data,
                "label": {"show": False}
            }
        ]
    }

else:  
    pie_data = [
        {"name": label, "value": value}
        for label, value in aggregated_gdp.items()
    ]

    options = {
        "title": {
            "text": f"GDP Distribution ({display_mode})",
            "left": "center"
        },
        "tooltip": {
            "trigger": "item",
            "formatter": "{b}<br/>{c}"
        },
        "legend": {
            "orient": "horizontal",
            "bottom": "1%",
            "left": "center",
            "type": "scroll",
            "textStyle": {"fontSize": 11}
        },
        "series": [
            {
                "name": "GDP",
                "type": "pie",
                "radius": "60%",
                "center": ["50%", "45%"],
                "data": pie_data,

                "label": {"show": False},
                "labelLine": {"show": False},

                "emphasis": {
                    "itemStyle": {
                        "shadowBlur": 10,
                        "shadowOffsetX": 0,
                        "shadowColor": "rgba(0, 0, 0, 0.5)"
                    }
                }
            }
        ]
    }

st_echarts(options=options, height="700px")