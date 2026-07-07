# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "pypalmsens>=1.9",
#     "streamlit>=1.55",
# ]
# ///

from __future__ import annotations

import time
from threading import Thread

import altair as alt
import pandas as pd
import streamlit as st
from streamlit.runtime.scriptrunner import add_script_run_ctx, get_script_run_ctx

import pypalmsens as ps
from pypalmsens.data import CallbackData, Curve, Measurement
from pypalmsens.energy import experimental_BatteryCycling

st.set_page_config(
    page_title='Battery Cycling',
    page_icon=':material/battery_android_frame_bolt:',
    menu_items={
        'Get Help': 'https://palmsens.com/contact',
        'Report a bug': 'https://github.com/palmsens/palmsens_sdk/issues',
    },
    layout='wide',
    initial_sidebar_state='expanded',
)


st.logo(
    'https://dev.palmsens.com/python/latest/_attachments/assets/banner.svg',
    link='https://dev.palmsens.com/python/latest',
    size='large',
)


SESSION = st.session_state

if 'manager' not in SESSION:
    SESSION.manager = None

if 'is_measuring' not in SESSION:
    SESSION.is_measuring = False

if 'thread' not in SESSION:
    SESSION.thread = None

if 'start' not in SESSION:
    SESSION.start = False

if 'measurement' not in SESSION:
    SESSION.measurement = None

if 'curves' not in SESSION:
    SESSION.curves = {}
    SESSION.curves_metadata = {}
    SESSION.i_curves = []
    SESSION.e_curves = []


class MethodThread(Thread):
    def __init__(self, method: experimental_BatteryCycling):
        super().__init__()
        self.method = method
        self.measurement: Measurement | None = None
        self.message: str | None = None

    def run(self):
        method = self.method

        SESSION.curves.clear()
        SESSION.curves_metadata.clear()
        SESSION.i_curves.clear()
        SESSION.e_curves.clear()

        def on_curve_begin(curve: Curve):
            if curve.title.startswith('CP: t vs E'):
                SESSION.e_curves.append(curve.id)
            elif curve.title.startswith('CP: t vs i'):
                SESSION.i_curves.append(curve.id)
            elif curve.title.startswith('Unknown'):
                pass

            SESSION.curves_metadata[curve.id] = curve.metadata()
            SESSION.curves[curve.id] = []

        def on_data(data: CallbackData):
            for row in zip(data.x_array[data.start :], data.y_array[data.start :]):
                SESSION.curves[data.id].append(row)

        SESSION.manager.events.on_curve_begin = on_curve_begin
        SESSION.manager.events.on_curve_new_data = on_data
        SESSION.manager.register_receive_message_callback(self.set_status_message)

        measurement = SESSION.manager.measure(method)

        self.measurement = measurement

    def set_status_message(self, message: str):
        self.message = message


def configure_method_widget() -> experimental_BatteryCycling:
    """Configure battery cycling method via widget."""
    potential_max = st.number_input(
        'Potential Max (mV)',
        value=4300,
        help='Maximum potential to charge to (units: mV).',
        disabled=SESSION.thread is not None,
    )

    current_min = st.number_input(
        'Current Min (μA)',
        value=5,
        help='Minimum current to stop the CV charge step (units: μA).',
        disabled=SESSION.thread is not None,
    )

    potential_min = st.number_input(
        'Potential Min (mV)',
        value=2500,
        help='Minimum potential to discharge to (units: mV).',
        disabled=SESSION.thread is not None,
    )

    current_charge = st.number_input(
        'Current Charge (μA)',
        value=100,
        help='Constant current to charge with (units: μA).',
        disabled=SESSION.thread is not None,
    )

    current_discharge = st.number_input(
        'Current Discharge (μA)',
        value=-100,
        help='Constant current to discharge with (units: μA).',
        disabled=SESSION.thread is not None,
    )

    cycles = st.number_input(
        'Cycles',
        value=1,
        help='Number of charge and discharge cycles.',
        disabled=SESSION.thread is not None,
    )

    interval = st.number_input(
        'Interval (s)',
        value=10,
        help='Interval time of each measurement point (units: s).',
        disabled=SESSION.thread is not None,
    )

    max_time = st.number_input(
        'Max Time (s)',
        value=3,
        help='Maximum duration of each step (if the cut-off is not met) (units: s).',
        disabled=SESSION.thread is not None,
    )

    delta_v = st.number_input(
        'Delta V (μV)',
        value=100,
        min_value=0,
        help='Minimum potential variation required for plotting data in CC steps (units: μV).',
        disabled=SESSION.thread is not None,
    )

    delta_i = st.number_input(
        'Delta I (nA)',
        value=500,
        min_value=0,
        help='Minimum current variation reuqired for plotting data in the CV step (units: nA).',
        disabled=SESSION.thread is not None,
    )

    delta_t = st.number_input(
        'Delta T (ms)',
        value=100,
        help='Maximum time without plotting data (units: ms).',
        disabled=SESSION.thread is not None,
    )

    return ps.energy.experimental_BatteryCycling(
        potential_max=potential_max,
        current_min=current_min,
        potential_min=potential_min,
        current_charge=current_charge,
        current_discharge=current_discharge,
        cycles=cycles,
        interval=interval,
        max_time=max_time,
        delta_v=delta_v,
        delta_i=delta_i,
        delta_t=delta_t,
    )


def show_methodscript_widget(methodscript: ps.MethodScript) -> None:
    """Show widget with generated methodscript."""
    c1, c2, _ = st.columns(3)

    _ = c1.download_button(
        'Save as script (.mscr)',
        data=methodscript.script,
        file_name='battery_cycler.mscr',
        mime='text/plain',
        icon=':material/download:',
        width='stretch',
        disabled=SESSION.is_measuring,
    )
    _ = c2.download_button(
        'Save as method file (.psmethod)',
        data=methodscript._serialize(),
        file_name='battery_cycler.psmethod',
        mime='text/plain',
        icon=':material/download:',
        width='stretch',
        disabled=SESSION.is_measuring,
    )

    st.code(methodscript.script, line_numbers=True, height=600)


def connect_to_device_widget():
    """Connect to device widget.

    Sets `session.manager`."""
    c1, c2, _ = st.columns(3)

    if not SESSION.manager:
        if c1.button(
            'Connect',
            type='primary',
            icon=':material/add_link:',
            width='stretch',
        ):
            with c2.spinner('Connecting...'):
                try:
                    SESSION.manager = ps.connect()
                except ConnectionError as e:
                    st.warning(str(e))
                    st.stop()

            st.rerun()

        st.stop()
    else:
        c2.write(f'Connected to {SESSION.manager.instrument.name}')

        if c1.button(
            'Disconnect',
            width='stretch',
            icon=':material/link_off:',
        ):
            SESSION.manager.disconnect()
            SESSION.manager = None

            st.rerun()


def start_measurement_widget(method: experimental_BatteryCycling):
    """This widget starts the measurement thread."""
    c1, c2, _ = st.columns(3)

    if not SESSION.thread:
        if c1.button(
            'Start measurement',
            type='primary',
            icon=':material/play_circle:',
            width='stretch',
        ):
            with c2.spinner('Starting measurement...'):
                SESSION.thread = MethodThread(method=method)
                add_script_run_ctx(SESSION.thread, get_script_run_ctx())
                SESSION.thread.start()
                SESSION.is_measuring = True

            st.rerun()
    else:
        if c1.button(
            'Abort measurement',
            type='primary',
            icon=':material/cancel:',
            width='stretch',
        ):
            SESSION.thread.join()
            SESSION.manager.abort()
            SESSION.thread = None
            st.rerun()


def live_measurement_widget(method: experimental_BatteryCycling):
    """Show live updates for measurement."""
    e_col, i_col = st.columns(2)

    e_chart = e_col.empty()
    i_chart = i_col.empty()

    if SESSION.thread:
        progress_bar = st.progress(0)

        update_every = 1

        while SESSION.thread.is_alive():
            time.sleep(update_every)

            curve_no = len(SESSION.i_curves)
            progress_bar.progress(
                curve_no / method.cycles,
                text=SESSION.thread.message,
            )

            if SESSION.i_curves:
                i_chart.altair_chart(make_chart(curve_id=SESSION.i_curves[-1]))

            if SESSION.e_curves:
                e_chart.altair_chart(make_chart(curve_id=SESSION.e_curves[-1]))

        SESSION.thread.join()
        SESSION.measurement = SESSION.thread.measurement
        SESSION.thread = None
        SESSION.is_measuring = False

        progress_bar.progress(1.0, text='Measurement finished!')

        st.rerun()


def show_measurement_widget():
    """Show measurement data."""
    c1, c2 = st.columns(2)

    if SESSION.i_curves:
        c1.altair_chart(make_chart(curve_id=SESSION.i_curves[-1]).interactive())

    if SESSION.e_curves:
        c2.altair_chart(make_chart(curve_id=SESSION.e_curves[-1]).interactive())

    if SESSION.measurement:
        c1, _, _ = st.columns(3)

        _ = c1.download_button(
            'Save measurement data (.pssession) ',
            data=b'Not implemented yet =(',
            file_name='battery_cycler.pssession',
            mime='text/plain',
            icon=':material/download:',
            width='stretch',
        )


def make_chart(curve_id: int) -> alt.Chart:
    """Make altair chart chart for curve id."""
    data = SESSION.curves[curve_id]
    metadata = SESSION.curves_metadata[curve_id]

    x_label, y_label = metadata.labels
    x_unit, y_unit = metadata.units

    source = pd.DataFrame(data, columns=metadata.columns)

    chart = (
        alt.Chart(source, title=metadata.title)
        .mark_line()
        .encode(
            alt.X('x').title(f'{x_label} / {x_unit}'),
            alt.Y('y').title(f'{y_label} / {y_unit}'),
        )
    )

    return chart


def main():

    st.title('Battery Cycling')

    with st.sidebar:
        method = configure_method_widget()

    methodscript = method.to_methodscript()

    with st.expander('Click to show generated MethodSCRIPT'):
        show_methodscript_widget(methodscript)

    connect_to_device_widget()

    start_measurement_widget(method)

    st.space(size='small')

    live_measurement_widget(method)

    if (not SESSION.is_measuring) and SESSION.measurement:
        show_measurement_widget()


if __name__ == '__main__':
    main()
