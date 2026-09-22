import marimo

__generated_with = "0.9.14"
app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo
    import pandas as pd
    import numpy as np
    import geopandas as gpd
    import matplotlib.pyplot as plt
    import matplotlib.patheffects as pe
    return gpd, mo, np, pd, pe, plt


@app.cell
def _(mo):
    mo.md(
        """
        # NYC Residential Composting — Interactive Capture Rate Map

        Drag the slider below to pick a month. The map updates to show that
        month's residential composting **capture rate** by community
        district — organics collected as a share of compostable material
        estimated to have been generated (2023 NYC Waste Characterization
        Study; see Assumption A3 in `nyc_composting_spatiotemporal.ipynb`).

        Excludes yard waste (leaves, Christmas trees) per Assumption A2,
        and starts January 2021 per Assumption A1.
        """
    )
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
    month_slider = mo.ui.slider(
        start=0,
        stop=len(months) - 1,
        value=len(months) - 1,  # defaults to the most recent month available
        step=1,
        label="Month",
        full_width=True,
    )
    month_slider
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

    mo.md(f"### {selected_month.strftime('%B %Y')}\n*{phase}*")
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
    pd,
    pe,
    plt,
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

    fig, ax = plt.subplots(figsize=(9, 9))
    merged.plot(
        column="capture_%", cmap="Purples", linewidth=0.5, edgecolor="black",
        legend=True, ax=ax, missing_kwds={"color": "lightgrey", "label": "No data / excluded (e.g. JIAs)"},
    )
    boro_shapes.boundary.plot(ax=ax, color="black", linewidth=2.2)

    for boro_id, geom in boro_shapes.geometry.items():
        centroid = geom.centroid
        ax.annotate(
            ID_TO_BORO.get(boro_id, str(boro_id)), xy=(centroid.x, centroid.y),
            ha="center", va="center", fontsize=11, fontweight="bold", color="black",
            path_effects=[pe.withStroke(linewidth=3, foreground="white")],
        )

    ax.set_title(f"Residential composting capture rate — {selected_month.strftime('%Y-%m')}")
    ax.set_axis_off()
    fig
    return


if __name__ == "__main__":
    app.run()
