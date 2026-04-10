# Remote IoT Corrosion Monitoring Using Python

The code here accompanies the application note: [Remote IoT Corrosion Monitoring Using Python](https://www.palmsens.com/knowledgebase-article/remote-iot-corrosion-monitoring-using-python/).

The application note demonstrates how to set up a Raspberry Pi or equivalent low-power linux computer for remote corrosion measurements. The corrosion measurements are performed using the Linear Polarization Resistance (LPR) technique. The application note includes a example dashboard for viewing and analyzing results.

There are 2 scripts:
- [measure.py](./measure.py): This script runs a LPR measurement using [PyPalmSens](https://dev.palmsens.com/python/latest/_attachments/).
- [app.py](./app.py): An example [Streamlit](https://docs.streamlit.io) dashboard for monitoring remote data.

See the application note for instructions.

## Running the dashboard locally

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Licence

The code for this application note is licensed under the terms of the [MIT Licence](./LICENSE).
