<?xml version='1.0' encoding='UTF-8'?>
<Project Type="Project" LVVersion="25008000">
	<Item Name="My Computer" Type="My Computer">
		<Property Name="server.app.propertiesEnabled" Type="Bool">true</Property>
		<Property Name="server.control.propertiesEnabled" Type="Bool">true</Property>
		<Property Name="server.tcp.enabled" Type="Bool">false</Property>
		<Property Name="server.tcp.port" Type="Int">0</Property>
		<Property Name="server.tcp.serviceName" Type="Str">My Computer/VI Server</Property>
		<Property Name="server.tcp.serviceName.default" Type="Str">My Computer/VI Server</Property>
		<Property Name="server.vi.callsEnabled" Type="Bool">true</Property>
		<Property Name="server.vi.propertiesEnabled" Type="Bool">true</Property>
		<Property Name="specify.custom.address" Type="Bool">false</Property>
		<Item Name="PSLabView" Type="Folder">
			<Item Name="Libraries" Type="Folder">
				<Item Name="PalmSens.Core.Simplified.LabVIEW.dll" Type="Document" URL="../PalmSens/Libraries/PalmSens.Core.Simplified.LabVIEW.dll"/>
			</Item>
			<Item Name="ActiveCurve.ctl" Type="VI" URL="../PalmSens/ActiveCurve.ctl"/>
			<Item Name="ActiveMeasurementInfo.ctl" Type="VI" URL="../PalmSens/ActiveMeasurementInfo.ctl"/>
			<Item Name="CurveFinished Event Callback.vi" Type="VI" URL="../PalmSens/CurveFinished Event Callback.vi"/>
			<Item Name="CurveInfo.ctl" Type="VI" URL="../PalmSens/CurveInfo.ctl"/>
			<Item Name="CurvesByMeasurement.ctl" Type="VI" URL="../PalmSens/CurvesByMeasurement.ctl"/>
			<Item Name="InitCurveResults.vi" Type="VI" URL="../PalmSens/InitCurveResults.vi"/>
			<Item Name="LiveCurveResult.ctl" Type="VI" URL="../PalmSens/LiveCurveResult.ctl"/>
			<Item Name="MeasurementEnded Event Callback.vi" Type="VI" URL="../PalmSens/MeasurementEnded Event Callback.vi"/>
			<Item Name="MeasurementEventArgs.ctl" Type="VI" URL="../PalmSens/MeasurementEventArgs.ctl"/>
			<Item Name="MeasurementInfo.ctl" Type="VI" URL="../PalmSens/MeasurementInfo.ctl"/>
			<Item Name="MeasurementResults.ctl" Type="VI" URL="../PalmSens/MeasurementResults.ctl"/>
			<Item Name="MeasurementsResult.ctl" Type="VI" URL="../PalmSens/MeasurementsResult.ctl"/>
			<Item Name="NewCurveDataEventArgs.ctl" Type="VI" URL="../PalmSens/NewCurveDataEventArgs.ctl"/>
			<Item Name="NewDataAdded Event Callback.vi" Type="VI" URL="../PalmSens/NewDataAdded Event Callback.vi"/>
			<Item Name="PalmSens.lvclass" Type="LVClass" URL="../PalmSens/PalmSens.lvclass"/>
			<Item Name="ProcessActiveMeasurements.vi" Type="VI" URL="../PalmSens/ProcessActiveMeasurements.vi"/>
			<Item Name="ProcessCurveData.vi" Type="VI" URL="../PalmSens/ProcessCurveData.vi"/>
			<Item Name="SimpleCurveAdded Event Callback.vi" Type="VI" URL="../PalmSens/SimpleCurveAdded Event Callback.vi"/>
		</Item>
		<Item Name="BasicExample.vi" Type="VI" URL="../BasicExample.vi"/>
		<Item Name="BasicExampleExportCSV.vi" Type="VI" URL="../BasicExampleExportCSV.vi"/>
		<Item Name="BasicExampleMux.vi" Type="VI" URL="../BasicExampleMux.vi"/>
		<Item Name="BasicExampleOCP.vi" Type="VI" URL="../BasicExampleOCP.vi"/>
		<Item Name="BasicUIExample.vi" Type="VI" URL="../BasicUIExample.vi"/>
		<Item Name="EISExample.vi" Type="VI" URL="../EISExample.vi"/>
		<Item Name="MethodSCRIPTExample.vi" Type="VI" URL="../MethodSCRIPTExample.vi"/>
		<Item Name="MultiChannelExample.vi" Type="VI" URL="../MultiChannelExample.vi"/>
		<Item Name="MultiChannelMES4HWSyncExample.vi" Type="VI" URL="../MultiChannelMES4HWSyncExample.vi"/>
		<Item Name="Dependencies" Type="Dependencies"/>
		<Item Name="Build Specifications" Type="Build"/>
	</Item>
</Project>
