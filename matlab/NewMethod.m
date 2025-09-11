function [ method ] = NewMethod( technique )
%NewMethod instantiates a new method object of the specified technique
%
% Input
%
% technique: a number specifying the index of one of the following techniques
%
%     1.  Linear Sweep Voltammetry
%     2.  Cyclic Voltammetry
%     3.  AC Voltammetry
%     4.  Differential Pulse Voltammetry
%     5.  Square Wave Voltammetry
%     6.  Normal Pulse Voltammetry
%     7.  Chronoamperometry
%     8.  MultiStep Amperometry
%     9.  Fast Amperometry
%     10. Pulsed Amperometric Detection
%     11. Multiple Pulse Amperometry
%     12. Open Circuit Potentiometry
%     13. Chronopotentiometry
%     14. MultiStep Potentiometry
%     15. Chronopotentiometric Stripping
%     16. Impedance Spectroscopy (PS3, PS4, ESPico, Sensit and ES4 only)
%     17. Fast cyclic voltammetry
%     18. Galvanostatic Impedance Spectroscopy (PS4 and ES4 only)
%
% Output
%
% method: the respective tecnique's method object containing its parameters.
% (if an invalid method is specified this will return false)

method = false;

%Check whether a valid technique was specified.
if(technique < 1 || technique > 17)
    return;
end

if(technique == 1)
    method = PalmSens.Techniques.LinearSweep();
end
if(technique == 2)
    method = PalmSens.Techniques.CyclicVoltammetry();
end
if(technique == 3)
    method = PalmSens.Techniques.ACVoltammetry();
end
if(technique == 4)
    method = PalmSens.Techniques.DifferentialPulse();
end
if(technique == 5)
    method = PalmSens.Techniques.SquareWave();
end
if(technique == 6)
    method = PalmSens.Techniques.NormalPulse();
end
if(technique == 7)
    method = PalmSens.Techniques.AmperometricDetection();
end
if(technique == 8)
    method = PalmSens.Techniques.MultistepAmperometry();
end
if(technique == 9)
    method = PalmSens.Techniques.FastAmperometry();
end
if(technique == 10)
    method = PalmSens.Techniques.PulsedAmpDetection();
end
if(technique == 11)
    method = PalmSens.Techniques.MultiplePulseAmperometry();
end
if(technique == 12)
    method = PalmSens.Techniques.OpenCircuitPotentiometry();
end
if(technique == 13)
    method = PalmSens.Techniques.Potentiometry();
end
if(technique == 14)
    method = PalmSens.Techniques.MultistepPotentiometry();
end
if(technique == 15)
    method = PalmSens.Techniques.ChronoPotStripping();
end
if(technique == 16)
    method = PalmSens.Techniques.ImpedimetricMethod();
end
if(technique == 17)
    method = PalmSens.Techniques.FastCyclicVoltammetry();
end
if(technique == 18)
    method = PalmSens.Techinques.ImpedimetricGstatMethod();
end
