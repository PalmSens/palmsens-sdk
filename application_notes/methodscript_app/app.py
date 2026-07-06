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
from pypalmsens.data import CallbackData, Curve

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


session = st.session_state

if 'manager' not in session:
    session.manager = None

if 'is_measuring' not in session:
    session.is_measuring = False

if 'thread' not in session:
    session.thread = None

if 'start' not in session:
    session.start = False

if 'measurement' not in session:
    session.measurement = None

if 'curves' not in session:
    session.curves = {}
    session.e_curves_metadata = {}
    session.i_curves_metadata = {}
    session.i_curves_current = 0
    session.e_curves_current = 0


class MethodThread(Thread):
    def __init__(self, method, session):
        super().__init__()
        self.method = method
        self.session = session
        self.measurement = None
        self.message = None

    def run(self):
        session = self.session
        method = self.method

        session.curves.clear()
        session.i_curves_metadata.clear()
        session.e_curves_metadata.clear()

        def on_curve_begin(curve: Curve):
            if curve.title.startswith('CP: t vs E'):
                session.e_curves_metadata[curve.id] = curve.metadata()
                session.e_curves_current = curve.id
            elif curve.title.startswith('CP: t vs i'):
                session.i_curves_metadata[curve.id] = curve.metadata()
                session.i_curves_current = curve.id
            elif curve.title.startswith('Unknown'):
                pass

            session.curves[curve.id] = []

        def on_data(data: CallbackData):
            for row in zip(data.x_array[data.start :], data.y_array[data.start :]):
                session.curves[data.id].append(row)

        session.manager.events.on_curve_begin = on_curve_begin
        session.manager.events.on_curve_new_data = on_data
        session.manager.register_receive_message_callback(self.set_status_message)

        measurement = session.manager.measure(method)

        self.measurement = measurement

    def set_status_message(self, message: str):
        self.message = message


def make_chart(data, metadata) -> alt.Chart:
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

    c1, c2 = st.columns(2)

    with st.sidebar:
        potential_max = st.number_input(
            'Potential Max (mV)',
            value=4300,
            help='Maximum potential to charge to (units: mV).',
            disabled=session.thread is not None,
        )

        current_min = st.number_input(
            'Current Min (μA)',
            value=5,
            help='Minimum current to stop the CV charge step (units: μA).',
            disabled=session.thread is not None,
        )

        potential_min = st.number_input(
            'Potential Min (mV)',
            value=2500,
            help='Minimum potential to discharge to (units: mV).',
            disabled=session.thread is not None,
        )

        current_charge = st.number_input(
            'Current Charge (μA)',
            value=100,
            help='Constant current to charge with (units: μA).',
            disabled=session.thread is not None,
        )

        current_discharge = st.number_input(
            'Current Discharge (μA)',
            value=-100,
            help='Constant current to discharge with (units: μA).',
            disabled=session.thread is not None,
        )

        cycles = st.number_input(
            'Cycles',
            value=1,
            help='Number of charge and discharge cycles.',
            disabled=session.thread is not None,
        )

        interval = st.number_input(
            'Interval (s)',
            value=10,
            help='Interval time of each measurement point (units: s).',
            disabled=session.thread is not None,
        )

        max_time = st.number_input(
            'Max Time (s)',
            value=3,
            help='Maximum duration of each step (if the cut-off is not met) (units: s).',
            disabled=session.thread is not None,
        )

        delta_v = st.number_input(
            'Delta V (μV)',
            value=100,
            min_value=0,
            help='Minimum potential variation required for plotting data in CC steps (units: μV).',
            disabled=session.thread is not None,
        )

        delta_i = st.number_input(
            'Delta I (nA)',
            value=500,
            min_value=0,
            help='Minimum current variation reuqired for plotting data in the CV step (units: nA).',
            disabled=session.thread is not None,
        )

        delta_t = st.number_input(
            'Delta T (ms)',
            value=100,
            help='Maximum time without plotting data (units: ms).',
            disabled=session.thread is not None,
        )

    method = ps.energy.experimental_BatteryCycling(
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

    ms = method.to_methodscript()

    with st.expander('Click to show generated MethodSCRIPT'):
        c1, c2, _ = st.columns(3)

        _ = c1.download_button(
            'Save as script (.mscr)',
            data=ms.script,
            file_name='battery_cycler.mscr',
            mime='text/plain',
            icon=':material/download:',
            width='stretch',
            disabled=session.is_measuring,
        )
        _ = c2.download_button(
            'Save as method file (.psmethod)',
            data=ms._serialize(),
            file_name='battery_cycler.psmethod',
            mime='text/plain',
            icon=':material/download:',
            width='stretch',
            disabled=session.is_measuring,
        )

        st.code(ms.script, line_numbers=True, height=600)

    c1, c2, _ = st.columns(3)

    if not session.manager:
        if c1.button(
            'Connect',
            type='primary',
            icon=':material/add_link:',
            width='stretch',
        ):
            with c2.spinner('Connecting...'):
                try:
                    session.manager = ps.connect()
                except ConnectionError as e:
                    st.warning(str(e))
                    st.stop()

            st.rerun()

        st.stop()
    else:
        c2.write(f'Connected to {session.manager.instrument.name}')

        if c1.button(
            'Disconnect',
            width='stretch',
            icon=':material/link_off:',
        ):
            session.manager.disconnect()
            session.manager = None

            st.rerun()

    c1, c2, _ = st.columns(3)

    if not session.thread:
        if c1.button(
            'Start measurement',
            type='primary',
            icon=':material/play_circle:',
            width='stretch',
        ):
            with c2.spinner('Starting measurement...'):
                session.thread = MethodThread(method=method, session=session)
                add_script_run_ctx(session.thread, get_script_run_ctx())
                session.thread.start()
                session.is_measuring = True

            st.rerun()
    else:
        if c1.button(
            'Abort measurement',
            type='primary',
            icon=':material/cancel:',
            width='stretch',
        ):
            session.thread.join()
            session.manager.abort()
            session.thread = None
            st.rerun()

    st.space(size='small')

    e_col, i_col = st.columns(2)

    e_chart = e_col.empty()
    i_chart = i_col.empty()

    if session.thread:
        progress_bar = st.progress(0)

        update_every = 1

        while session.thread.is_alive():
            time.sleep(update_every)

            curve_no = len(session.e_curves_metadata)
            progress_bar.progress(
                curve_no / method.cycles,
                text=session.thread.message,
            )

            try:
                i_chart.altair_chart(
                    make_chart(
                        data=session.curves[session.i_curves_current],
                        metadata=session.i_curves_metadata[session.i_curves_current],
                    )
                )
            except KeyError:
                pass

            try:
                e_chart.altair_chart(
                    make_chart(
                        data=session.curves[session.e_curves_current],
                        metadata=session.e_curves_metadata[session.e_curves_current],
                    )
                )
            except KeyError:
                pass

        session.thread.join()
        session.measurement = session.thread.measurement
        session.thread = None
        session.is_measuring = False

        progress_bar.progress(1.0, text='Measurement finished!')

        st.rerun()
    else:
        try:
            i_chart.altair_chart(
                make_chart(
                    data=session.curves[session.i_curves_current],
                    metadata=session.i_curves_metadata[session.i_curves_current],
                )
            )
        except KeyError:
            pass

        try:
            e_chart.altair_chart(
                make_chart(
                    data=session.curves[session.e_curves_current],
                    metadata=session.e_curves_metadata[session.e_curves_current],
                )
            )
        except KeyError:
            pass

        c1, _, _ = st.columns(3)

        if session.measurement:
            _ = c1.download_button(
                'Save measurement data (.pssession) ',
                data=b'Not implemented yet =(',
                file_name='battery_cycler.pssession',
                mime='text/plain',
                icon=':material/download:',
                width='stretch',
            )


if __name__ == '__main__':
    main()
