import marimo

__generated_with = "0.9.14"
app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo
    import pandas as pd
    import numpy as np
    import geopandas as gpd
    import plotly.express as px
    import plotly.graph_objects as go
    return gpd, go, mo, np, pd, px


@app.cell
def _(mo):
    # Capped to the same 650px column as the slider and map below, so the
    # text doesn't run wider than the content under it — no more mismatch
    # where the page reads full-width up top but narrows partway down.
    mo.md(
        """
        # NYC Residential Composting: Interactive Capture Rate Map

        Drag the slider below to pick a month. The selected month is shown
        above the slider, and the map updates to show that month's
        residential composting **capture rate** by community district —
        organics collected as a share of compostable material estimated
        to have been generated (2023 NYC Waste Characterization Study;
        see Assumption A3 in [`nyc_composting_spatiotemporal.ipynb`](https://github.com/DynamicalSystemsGroup/civic-claim-provenance/blob/main/analysis/nyc_composting_spatiotemporal.ipynb)).
        Hover over a district on the map for its exact capture rate.

        Excludes yard waste (leaves, Christmas trees) per Assumption A2,
        and starts January 2021 per Assumption A1.
        """
    ).style(max_width="650px")
    return


@app.cell
def _(np, pd):
    # Same load + clean pipeline as Steps 1-4 of nyc_composting_spatiotemporal.ipynb
    DATASET_ID = "ebb7-mvp5"
    url = f"https://data.cityofnewyork.us/resource/{DATASET_ID}.csv?$limit=200000"
    df = pd.read_csv(url)

    TIME_COL = "month"
    BORO_COL = "borough"
    DIST_COL = "communitydistrict"
    REFUSE = "refusetonscollected"
    PAPER = "papertonscollected"
    MGP = "mgptonscollected"

    # INCLUDE_YARD_WASTE = False per Assumption A2
    ORG_COLS = ["resorganicstons", "otherorganicstons"]
    RECYCLING = [REFUSE, PAPER, MGP]
    ALL_STREAMS = RECYCLING + ORG_COLS
    COMPOSTABLE_FRACTION = 0.358  # 2023 NYC Waste Characterization Study (Assumption A3)

    import re

    for c in ALL_STREAMS:
        df[c] = pd.to_numeric(df[c], errors="coerce")

    def parse_month(s):
        m = re.search(r"(\d{4})\D+(\d{1,2})", str(s))
        return pd.Timestamp(int(m.group(1)), int(m.group(2)), 1) if m else pd.NaT

    df["date"] = df[TIME_COL].map(parse_month)
    df = df.dropna(subset=["date"])
    df = df[df["date"] >= "2021-01-01"].sort_values("date")  # Assumption A1

    df["organics"] = df[ORG_COLS].sum(axis=1)
    df["total"] = df[ALL_STREAMS].sum(axis=1)
    df["compost_rate"] = np.where(df["total"] > 0, df["organics"] / df["total"] * 100, np.nan)

    months = sorted(df["date"].unique())
    return BORO_COL, COMPOSTABLE_FRACTION, DIST_COL, df, months


@app.cell
def _(pd):
    POLICY_DATES = {
        "Mandatory (Oct 6 2024)": pd.Timestamp("2024-10-06"),
        "Enforcement (Apr 1 2025)": pd.Timestamp("2025-04-01"),
    }
    return (POLICY_DATES,)


@app.cell
def _(gpd):
    # NYC Community District boundaries (Assumption A5)
    GEO_DATASET_ID = "5crt-au7u"
    geo_url = f"https://data.cityofnewyork.us/resource/{GEO_DATASET_ID}.geojson?$limit=2000"
    cds = gpd.read_file(geo_url)
    GEO_JOIN_FIELD = "boro_cd"  # adjust if this doesn't match cds.columns.tolist()
    return GEO_JOIN_FIELD, cds


@app.cell
def _(GEO_JOIN_FIELD, cds):
    BORO_ID = {"Manhattan": 1, "Bronx": 2, "Brooklyn": 3, "Queens": 4, "Staten Island": 5}
    ID_TO_BORO = {v: k for k, v in BORO_ID.items()}
    cds["_boro_id"] = cds[GEO_JOIN_FIELD].astype(str).str[0].astype(int)
    boro_shapes = cds.dissolve(by="_boro_id")
    return BORO_ID, ID_TO_BORO, boro_shapes


@app.cell
def _(mo, months):
    # Compact slider, not the full page width: show_value=False hides the
    # raw index (nobody wants to read "53 of 67"); the live "Month Year"
    # label is drawn directly above it in the next cell instead, so the
    # meaning is always visible next to the control rather than buried in
    # a hover state that doesn't work well mid-drag or on touch devices.
    # full_width=False keeps its footprint close to the map's, not the
    # page's, so it doesn't sprawl past the choropleth below it.
    month_slider = mo.ui.slider(
        start=0,
        stop=len(months) - 1,
        value=len(months) - 1,  # defaults to the most recent month available
        step=1,
        show_value=False,
        full_width=False,
    )
    return (month_slider,)


@app.cell
def _(POLICY_DATES, mo, month_slider, months):
    selected_month = months[month_slider.value]

    mandate = POLICY_DATES["Mandatory (Oct 6 2024)"]
    enforcement = POLICY_DATES["Enforcement (Apr 1 2025)"]
    if selected_month < mandate:
        phase = "Pre-mandate"
    elif selected_month < enforcement:
        phase = "Post-mandate, pre-enforcement"
    else:
        phase = "Post-enforcement"

    mo.vstack(
        [
            mo.md(f"**{selected_month.strftime('%B %Y')}** · *{phase}*"),
            month_slider,
        ],
        align="start",
        gap=0.25,
    )
    return (selected_month,)


@app.cell
def _(
    BORO_COL,
    BORO_ID,
    COMPOSTABLE_FRACTION,
    DIST_COL,
    GEO_JOIN_FIELD,
    ID_TO_BORO,
    boro_shapes,
    cds,
    df,
    go,
    pd,
    px,
    selected_month,
):
    # Same composite-key fix as Steps 8-9: group by (borough, district)
    # together, since district numbers repeat across boroughs.
    sub = df[df["date"] == selected_month]
    latest = sub.groupby([BORO_COL, DIST_COL]).apply(
        lambda g: pd.Series({
            "diversion_%": g["organics"].sum() / g["total"].sum() * 100,
            "capture_%":   g["organics"].sum() / (COMPOSTABLE_FRACTION * g["total"].sum()) * 100,
        })
    ).reset_index()

    latest["boro_cd"] = (
        latest[BORO_COL].map(BORO_ID).astype(int) * 100 + latest[DIST_COL].astype(int)
    ).astype(str).str.zfill(3)

    merged = cds.merge(latest, left_on=GEO_JOIN_FIELD, right_on="boro_cd", how="left")
    merged["district_label"] = merged.apply(
        lambda r: f"{r[BORO_COL]} CD {int(r[DIST_COL])}"
        if pd.notna(r[DIST_COL])
        else "No data / excluded (e.g. JIA)",
        axis=1,
    )

    # Switched from a static matplotlib PNG to an interactive Plotly
    # choropleth so each district can carry its own hover tooltip (the
    # capture rate %) — a flat image has no way to do that per-shape.
    import json

    geojson = json.loads(merged.to_json())

    fig = px.choropleth(
        merged,
        geojson=geojson,
        locations=GEO_JOIN_FIELD,
        featureidkey=f"properties.{GEO_JOIN_FIELD}",
        color="capture_%",
        color_continuous_scale="Purples",
        hover_name="district_label",
        hover_data={"capture_%": ":.1f", GEO_JOIN_FIELD: False},
    )
    fig.update_traces(marker_line_width=0.5, marker_line_color="black")

    # Bold borough outlines, drawn as a second, fill-less choropleth layer.
    boro_flat = boro_shapes.reset_index()
    boro_geojson = json.loads(boro_flat.to_json())
    fig.add_trace(go.Choropleth(
        geojson=boro_geojson,
        locations=boro_flat["_boro_id"],
        featureidkey="properties._boro_id",
        z=[0] * len(boro_flat),
        colorscale=[[0, "rgba(0,0,0,0)"], [1, "rgba(0,0,0,0)"]],
        showscale=False,
        marker_line_width=3,
        marker_line_color="black",
        hoverinfo="skip",
    ))

    # Borough name labels at each borough's centroid.
    centroids = boro_shapes.geometry.centroid
    fig.add_trace(go.Scattergeo(
        lon=centroids.x,
        lat=centroids.y,
        text=[ID_TO_BORO.get(i, str(i)) for i in boro_shapes.index],
        mode="text",
        textfont=dict(size=14, color="black"),
        hoverinfo="skip",
        showlegend=False,
    ))

    fig.update_geos(fitbounds="locations", visible=False)
    fig.update_layout(
        title=f"Residential composting capture rate — {selected_month.strftime('%Y-%m')}",
        width=650,
        height=650,
        margin=dict(l=0, r=0, t=40, b=0),
        coloraxis_colorbar_title="Capture %",
    )
    fig
    return


if __name__ == "__main__":
    app.run()
