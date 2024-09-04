import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np



train_path = "train.csv"
test_path = "test.csv"

train = pd.read_csv(
    train_path,
    index_col="ID_LAT_LON_YEAR_WEEK",
    engine="pyarrow",
).rename(columns=str.title)

test = pd.read_csv(
    test_path,
    index_col="ID_LAT_LON_YEAR_WEEK",
    engine="pyarrow",
).rename(columns=str.title)

def extract_date_from_year_and_week(year, week):
    return pd.to_datetime(year, format="%Y") + pd.to_timedelta(week.mul(7), unit="days")

train["Date"] = extract_date_from_year_and_week(train.Year, train.Week_No)
test["Date"] = extract_date_from_year_and_week(test.Year, test.Week_No)

train["Month_No"] = train.Date.dt.month
test["Month_No"] = test.Date.dt.month

def get_coordinates(lat, lon):
    return "(" + lat.astype(str) + ", " + lon.astype(str) + ")"

train["Coordinates"] = get_coordinates(train.Latitude, train.Longitude)
test["Coordinates"] = get_coordinates(test.Latitude, test.Longitude)
train_geo_pairs = train["Coordinates"].drop_duplicates().to_numpy()
test_geo_pairs = test["Coordinates"].drop_duplicates().to_numpy()

train_years = train.Year.unique()
test_years = test.Year.unique()

train_weeks = train.Week_No.unique()
test_weeks = test.Week_No.unique()

assert np.all(train_geo_pairs == test_geo_pairs)  # Are there the same locations?
assert len(train_geo_pairs) * len(train_years) * len(train_weeks) == len(train)
assert len(test_geo_pairs) * len(test_years) * len(test_weeks) == len(test)

missing_values = pd.DataFrame(index=test.columns)
missing_values["MissingTrain"] = train.isna().sum()
missing_values["MissingTrainRatio"] = missing_values.MissingTrain / len(train)
missing_values["MissingTest"] = test.isna().sum()
missing_values["MissingTestRatio"] = missing_values.MissingTest / len(test)

# We remove these features right away.
cols_to_reject = train.columns[train.columns.str.startswith("Uvaerosollayerheight")]

train = train.drop(cols_to_reject, axis=1)
test = test.drop(cols_to_reject, axis=1)
mean_emission_by_loc = train.groupby("Coordinates").Emission.mean()
zero_emission_loc = mean_emission_by_loc[mean_emission_by_loc == 0]
geo_mean_emission = train.groupby(["Latitude", "Longitude"]).Emission.mean().reset_index()
zero_emission = geo_mean_emission[geo_mean_emission.Emission == 0]

fig = px.scatter_mapbox(
    geo_mean_emission,
    lat="Latitude",
    lon="Longitude",
    color="Emission",
    size="Emission",
    color_continuous_scale=px.colors.sequential.Cividis,
    size_max=30,
    zoom=7,
    width=840,
    height=940,
    title="Distinct Locations of Data Collection in Rwanda<br>"
    "<span style='font-size: 75%; font-weight: bold;'>"
    "Each dot is associated with the mean CO\u2082 emission collected for this place</span>",
)
fig.add_scattermapbox(
    lat=zero_emission.Latitude,
    lon=zero_emission.Longitude,
    name="Zero-Emission",
    marker=dict(color="#E04C5F", size=15, symbol="circle", opacity=0.75),
)

# Update the layout to use a darker font color
fig.update_layout(
    mapbox_style="open-street-map",
    margin=dict(r=0, t=90, l=0, b=0),
    font=dict(
        color="#2C2C2C"  # Darker shade for all text elements
    ),
    title_font=dict(
        size=18,
        color="#2C2C2C",  # Title font color
    ),
    coloraxis_colorbar=dict(
        title=dict(
            text="Mean Emission",
            side="top",
            font=dict(
                color="#2C2C2C"  # Color of the colorbar title
            )
        ),
        orientation="h",
        yanchor="bottom",
        xanchor="center",
        y=-0.13,
        x=0.5,
    ),
    legend=dict(
        font=dict(
            color="#2C2C2C"  # Legend font color
        ),
        yanchor="bottom",
        xanchor="right",
        y=1,
        x=1,
        orientation="h"
    ),
    plot_bgcolor="white",  # Set the plot background color to white
    paper_bgcolor="white",  # Set the paper background color to white
)


st.plotly_chart(fig)
import base64

def get_base64_of_bin_file(bin_file):
    with open(bin_file, 'rb') as f:
        data = f.read()
    return base64.b64encode(data).decode()

def set_background(png_file):
    bin_str = get_base64_of_bin_file(png_file)
    page_bg_img = f'''
    <style>
    .stApp {{
        background-image: url("data:image/png;base64,{bin_str}");
        background-size: cover;
        background-position: center;
        background-repeat: no-repeat;
        background-attachment: fixed;
    }}
    </style>
    '''
    st.markdown(page_bg_img, unsafe_allow_html=True)

set_background('ivan-bandura-g_1_FXigeGc-unsplash.jpg')
