# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "numpy>=2.4",
#     "pandas>=2.3",
#     "plotly>=6.6",
#     "streamlit>=1.55",
# ]
# ///

from __future__ import annotations

import datetime
from dataclasses import InitVar, dataclass
from textwrap import dedent
from typing import Any

import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st

st.set_page_config(
    page_title="LPR analysis",
    page_icon=":chart_with_upwards_trend:",
    menu_items={
        "Get Help": "https://palmsens.com/contact",
        "Report a bug": "https://github.com/palmsens/palmsens_sdk/issues",
    },
)


def generate_device(name: str, *, n_samples: int = 1000) -> Device:
    """Generate device including semi-random data."""
    lon = 5.149667 + np.random.normal(scale=0.01)
    lat = 52.020198 + np.random.normal(scale=0.01)
    device = Device(name=name, lon=lon, lat=lat, data=generate_data(n_samples))

    return device


def generate_data(n_samples: int = 1000):
    """Generate pseudo-random signal for demo / testing purposes."""
    normal = np.random.normal

    now = datetime.datetime(2026, 3, 23, 14, 50, 36)
    last_hour = now - datetime.timedelta(
        microseconds=now.microsecond, seconds=now.second, minutes=now.minute
    )

    rng = pd.date_range(end=last_hour, freq="h", periods=n_samples)

    noise = normal(loc=0, scale=0.01, size=n_samples)
    ocp = 1 + np.sin(np.linspace(0, abs(normal()), n_samples) + normal(scale=np.pi)) + noise
    rp = 1 + np.sin(np.linspace(0, abs(normal()), n_samples) + normal(scale=np.pi)) + noise

    return pd.DataFrame(
        {
            "timestamp": rng,
            "ocp": ocp,
            "rp": rp,
            "resid": np.zeros_like(ocp),
        }
    )


@dataclass
class Device:
    name: str
    """Identifier."""
    lon: float
    """device longitude."""
    lat: float
    """device latitude."""
    data: pd.DataFrame = None
    """Contains data."""
    path: InitVar[str | None] = None
    """Path or url for data."""

    def __post_init__(self, path):
        if path:
            self.data = self.load_data(path)
        assert self.data is not None

    @staticmethod
    @st.cache_data
    def load_data(path: str):
        """Read data from path."""
        df = pd.read_csv(path)
        df["timestamp"] = pd.to_datetime(df["timestamp"], format="ISO8601")
        df["rp"] = df["rp"]
        df["ocp"] = df["ocp"]
        return df

    def summary(self, last_n: int = 30) -> dict[str, Any]:
        """Generate summary for dataset."""
        assert self.data is not None

        last_row = self.data.iloc[-1]
        return {
            "name": self.name,
            "lat": self.lat,
            "lon": self.lon,
            "ocp": last_row["ocp"],
            "rp": last_row["rp"],
            "history": self.data["rp"].iloc[-last_n:].tolist(),
            "timestamp": last_row["timestamp"],
        }


@st.cache_data
def load_summary(devices: list[Device]) -> pd.DataFrame:
    """Load summary table from device listing."""
    return pd.DataFrame([device.summary() for device in devices])


@st.cache_data
def load_data(devices: list[Device]) -> pd.DataFrame:
    """Load long form data for device listing."""
    return pd.concat({loc.name: loc.data for loc in devices}, names=["name", None]).reset_index(
        "name"
    )


def make_chart(
    data: pd.DataFrame,
    *,
    selected: list[str] | None = None,
    y: str = "rp",
):
    """Make line chart for rp or ocp."""
    if selected:
        data = data[data["name"].isin(selected)]

    if y == "ocp":
        title = "Open Circuit Potential"
        ylabel = "Potential / V"
    else:
        assert y == "rp"
        ylabel = "Polarization resistance / Ω"
        title = "Linear Polarization Resistance"

    fig = px.line(
        data,
        x="timestamp",
        y=y,
        color="name",
        labels={
            "timestamp": "Time",
            y: ylabel,
        },
        title=title,
    )

    fig.update_layout(
        margin=dict(l=0, r=0, t=40, b=10),
    )

    return st.plotly_chart(fig)


def create_summary_table(data: pd.DataFrame):
    """Layout table with data summary."""
    return st.dataframe(
        data,
        column_config={
            "timestamp": st.column_config.DatetimeColumn(
                "Last update",
                help="Timestamp of the last data point.",
                format="D MMM YYYY, H:mm",
            ),
            "name": st.column_config.TextColumn(
                "Name",
                help="Name of the device or location.",
            ),
            "lat": None,
            "lon": None,
            "ocp": st.column_config.NumberColumn(
                "OCP (latest)",
                help="Open circuit potential (V)",
            ),
            "rp": st.column_config.NumberColumn(
                "Rp (latest)",
                help="Polarization resistance (Ω)",
            ),
            "history": st.column_config.AreaChartColumn(
                "Rp (trend)", help="Last 30 observations."
            ),
        },
        hide_index=True,
    )


def create_map(data: pd.DataFrame, *, devices: list[Device]):
    """List devices on map."""
    fig = px.scatter_map(
        data,
        lat="lat",
        lon="lon",
        color="rp",
        hover_name="name",
        color_continuous_scale=px.colors.sequential.Viridis_r,
        zoom=10,
        title="Device map",
    )

    fig.update_layout(
        margin=dict(l=0, r=0, t=40, b=10),
    )
    fig.update_traces(
        marker=dict(size=15),
    )

    event = st.plotly_chart(fig, on_select="rerun")

    rows = event["selection"]["point_indices"]
    selected = [devices[i].name for i in rows]

    return selected


def main():
    st.title("LPR analysis")

    st.write(
        dedent("""
        This is a simple dashboard to collect and analyze linear polarization resistance data from
        distributed devices collected using [PyPalmSens](https://dev.palmsens.com/python/latest/_attachments).
        """)
    )

    demo = st.checkbox(label="Demo mode", value=True, help="Generate semi-random noisy data.")

    if demo:
        col1, col2, col3 = st.columns(3)

        seed = col1.number_input("Random seed", value=1234)
        n_devices = col2.number_input("Number of devices", value=5, min_value=1)
        n_samples = col3.number_input("Number of samples", value=200, step=10, min_value=10)

        np.random.seed(seed)
        devices = [
            generate_device(f"Device #{i + 1}", n_samples=n_samples) for i in range(n_devices)
        ]
    else:
        template = pd.DataFrame(
            [
                {
                    "name": "PalmSens HQ",
                    "lon": 5.149667,
                    "lat": 52.020198,
                    "path": "https://raw.githubusercontent.com/PalmSens/PalmSens_SDK/refs/heads/main/application_notes/remote_corrosion/data.csv",
                },
            ],
        )

        st.write("Use the table below to add devices or other data sources.")

        devices_input = st.data_editor(template, num_rows="dynamic")
        devices = [Device(**row) for _, row in devices_input.iterrows()]

    data = load_data(devices)
    summary = load_summary(devices)

    tab1, tab2 = st.tabs(["Data", "Map"])

    with tab1:
        st.write("""Data summary table.""")
        create_summary_table(summary)

    with tab2:
        st.write("""Select devices on map to plot.""")
        selected = create_map(summary, devices=devices)

    tab1, tab2 = st.tabs(["Rₚ", "OCP"])

    with tab1:
        make_chart(data, selected=selected, y="rp")
    with tab2:
        make_chart(data, selected=selected, y="ocp")


if __name__ == "__main__":
    main()
