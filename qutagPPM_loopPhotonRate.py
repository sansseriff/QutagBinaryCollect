# Example for using the Coincidence Counters with python + quTAG
#
# Author: qutools GmbH
# Last edited: Oct 2019
#
# Tested with python 3.7.3 (32bit), numpy-1.13.3 and Windows 7 (64bit)
#
# This is demo code. Use at your own risk. No warranties.
#
# It may be used and modified with no restriction; raw copies as well as 
# modified versions may be distributed without limitation.

# for sleep
import time
import os
import numpy as np
import sys
import subprocess




# This code shows how to get timestamps from a quTAG connected via USB and write them into a text file.

# Import the python wrapper which wraps the DLL functions.
# The wrapper should be in the same directory like this code in the folder '..\QUTAG-V1.x.x\userlib\src'.
try:
        import QuTAG
except:
        print("Time Tagger wrapper QuTAG.py is not in the search path.")


# Initialize the quTAG device
qutag = QuTAG.QuTAG()

dirName = '/mnt/data/PPM_PDRDF/Testing7.30/PulseScan'
try:
    # Create target Directory
    os.mkdir(dirName)
    print("Directory " , dirName ,  " Created ") 
except FileExistsError:
    print("Directory " , dirName ,  " already exists")



path = "/mnt/data/PPM_PDRDF/2020.08.05/PhotonRateScan"
#path = "/home/elsa/Desktop"

qutag.enableChannels((1,2,3,4))

x = [int(100000*(1.51**i)) for i in range(21)]  #from 100000 photons per second to about 400 million in exponential steps
for pLevel in x:
        filename = 'TT_Terminal_80MHz_Bias_0.34V_trig_20mV_pRate_' + str(pLevel) + '.bin'
        full_name = os.path.join(path,filename)


        subprocess.call(['python','/home/elsa/src/snspd-measure/snspd_measure/photonRate.py', '-P', str(pLevel)])
        time.sleep(2)

        # The next function starts or stops writing the timestamp values to a file continuously.
        # The timestamps written are already corrected by the detector delays, see example 'qutag-GetHistogramLoop-channelDelay-example.py'.
        # Timestamps come in base units of 1 ps. The channel numbers start with 0 in binary formats, with 1 in ASCII.
        # A channel number of (100 + Marker Number) is associated with marker input events.
        # The 104 is a millisecond tick.
        # The following file formats are available:
        #    ASCII: FILEFORMAT_ASCII - Timestamp values (int base units) and channel numbers as decimal values in two comma separated columns. Channel numbers range from 1 to 8 in this format.
        #    binary: FILEFORMAT_BINARY - A binary header of 40 bytes, records of 10 bytes, 8 bytes for the timestamp, 2 for the channel number, stored in little endian (Intel) byte order.
        #    compressed: FILEFORMAT_COMPRESSED - A binary header of 40 bytes, records of 40 bits (5 bytes), 37 bits for the timestamp, 3 for the channel number, stored in little endian (Intel) byte order. No marker events and timer ticks are stored.
        #    raw: FILEFORMAT_RAW - Like binary, but without header. Provided for backward compatiblity.


        # Read back device parameters: coincidence window in bins (bin width is timebase) and exposuretime in ms
        #na, coincWin, expTime = qutag.getDeviceParams()
        #print("Coincidence window",coincWin, "bins, exposure time",expTime, "ms")


        #qutag.setChannelLink(False)
        

        qutag.setSignalConditioning(1,qutag.SCOND_MISC,True,0.001465)
        qutag.setSignalConditioning(2,qutag.SCOND_MISC,True,0.0)
        qutag.setSignalConditioning(3,qutag.SCOND_MISC,False,-0.02)
        qutag.setSignalConditioning(4,qutag.SCOND_MISC,False,-0.0205)

        delays = np.zeros(int(8), dtype=np.int32)
        delays[0] = 0 # Start
        delays[1] = 0 # Stop1
        delays[2] = 0 # Stop2
        delays[3] = 0  #Stop3
        delays[4] = 0  #Stop4
        rc = qutag.setChannelDelays(delays)

        #in ps
        qutag.setDeadTime(0,0) #Start
        qutag.setDeadTime(1,0)
        qutag.setDeadTime(2,0)
        qutag.setDeadTime(3,100*1000) 
        qutag.setDeadTime(4,0) 


        #rc = qutag.setChannelLink(True)
        #print("Set ChannelLink rc: ", rc)

        #qutag.setChannelLink(True) #turn on linked channel mode

        #qutag.enableMarkers((0,0)) doesn't work for some reason


        # start writing Timestamps from the quTAG
        qutag.writeTimestamps(full_name,qutag.FILEFORMAT_BINARY)
        print(qutag.getDataLost())
        print(qutag.getDataLost())
        # Give some time to accumulate data
        start = time.time()
        time.sleep(0.05) # 1 second sleep time
        end = time.time()

        print("elapsed: ", end - start)

        # stop writing Timestamps
        qutag.writeTimestamps('',qutag.FILEFORMAT_NONE)

        print(qutag.getDataLost())
        print(qutag.getDataLost())


        print("Done making  " + filename)


#qutag.setChannelLink(False)
# Disconnects a connected device and stops the internal event loop.
qutag.deInitialize()


