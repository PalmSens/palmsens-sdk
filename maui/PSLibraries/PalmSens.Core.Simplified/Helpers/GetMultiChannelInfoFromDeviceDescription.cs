using MathNet.Numerics.Distributions;
using PalmSens.Devices;
using System;

namespace PalmSens.Core.Simplified.Helpers
{
    public static class DeviceDescriptionHelper
    {
        public static (int Channel, string Serial) GetMultiChannelInfoFromDeviceDescription(string deviceDescription)
        {
            string serial = "";
            int channel = -1;

            int iCH = deviceDescription.IndexOf("ch", StringComparison.OrdinalIgnoreCase);
            if (iCH > 0)
            {
                serial = deviceDescription.Substring(0, iCH).ToLower();

                if (serial.Contains("mps4") || serial.Contains("mes4"))
                {
                    string channelString = deviceDescription.Split(new string[] { "CH" }, StringSplitOptions.None)[1];
                    if (channelString.Length > 0)
                    {
                        int.TryParse(channelString, out channel);
                    }
                }
                else
                {
                    string channelString = deviceDescription.Split(' ')[0];
                    if (channelString.Length > 3)
                    {
                        int.TryParse(channelString.Substring(channelString.Length - 3, 3), out channel);
                    }
                }
            }

            return (channel, serial);
        }
    }
}
