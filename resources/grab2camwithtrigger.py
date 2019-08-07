# Grab_MultipleCameras.cpp
# ============================================================================
# This sample illustrates how to grab and process images from multiple cameras
# using the CInstantCameraArray class. The CInstantCameraArray class represents
# an array of instant camera objects. It provides almost the same interface
# as the instant camera for grabbing.
# The main purpose of the CInstantCameraArray is to simplify waiting for images and
# camera events of multiple cameras in one thread. This is done by providing a single
# RetrieveResult method for all cameras in the array.
# Alternatively, the grabbing can be started using the internal grab loop threads
# of all cameras in the CInstantCameraArray. The grabbed images can then be processed by one or more
# image event handlers. Please note that this is not shown in this example.
# ============================================================================

import os

os.environ["PYLON_CAMEMU"] = "3"

from pypylon import genicam
from pypylon import pylon
import sys

# Number of images to be grabbed.
countOfImagesToGrab = 100

# Limits the amount of cameras used for grabbing.
# It is important to manage the available bandwidth when grabbing with multiple cameras.
# This applies, for instance, if two GigE cameras are connected to the same network adapter via a switch.
# To manage the bandwidth, the GevSCPD interpacket delay parameter and the GevSCFTD transmission delay
# parameter can be set for each GigE camera device.
# The "Controlling Packet Transmission Timing with the Interpacket and Frame Transmission Delays on Basler GigE Vision Cameras"
# Application Notes (AW000649xx000)
# provide more information about this topic.
# The bandwidth used by a FireWire camera device can be limited by adjusting the packet size.
maxCamerasToUse = 2

# The exit code of the sample application.
exitCode = 0

try:

    # Get the transport layer factory.
    tlFactory = pylon.TlFactory.GetInstance()

    # Get all attached devices and exit application if no device is found.
    devices = tlFactory.EnumerateDevices()
    if len(devices) == 0:
        raise pylon.RUNTIME_EXCEPTION("No camera present.")

    # Create an array of instant cameras for the found devices and avoid exceeding a maximum number of devices.
    cameras = pylon.InstantCameraArray(min(len(devices), maxCamerasToUse))

    l = cameras.GetSize()

    # Create and attach all Pylon Devices.
    for i, cam in enumerate(cameras):
        cam.Attach(tlFactory.CreateDevice(devices[i]))

        # Print the model name of the camera.
        print("Using device ", cam.GetDeviceInfo().GetModelName())
    
    #setting cameras trigger mode @gad
    cameras.Open()
    cameras[0].TriggerSource.SetValue("Line1") 
    cameras[0].TriggerMode.SetValue("On")
    cameras[1].TriggerSource.SetValue("Line1")
    cameras[1].TriggerMode.SetValue("On")


    # Starts grabbing for all cameras starting with index 0. The grabbing
    # is started for one camera after the other. That's why the images of all
    # cameras are not taken at the same time.
    # However, a hardware trigger setup can be used to cause all cameras to grab images synchronously.
    # According to their default configuration, the cameras are
    # set up for free-running continuous acquisition.
    cameras.StartGrabbing()
    #set flags to sync graping from both camers @gad
    flags = [False,False]
    # array to hold the imgs @gad
    imgs = [[],[]]

    # Grab c_countOfImagesToGrab from the cameras.
    for i in range(countOfImagesToGrab):
        if not cameras.IsGrabbing():
            break

        grabResult = cameras.RetrieveResult(5000, pylon.TimeoutHandling_ThrowException)

        # When the cameras in the array are created the camera context value
        # is set to the index of the camera in the array.
        # The camera context is a user settable value.
        # This value is attached to each grab result and can be used
        # to determine the camera that produced the grab result.
        cameraContextValue = grabResult.GetCameraContext()

	# check the flags and set the flag = 1 for corresponing captured frame @gad
        if (cameraContextValue == 0):
            print ('hi 0')
            flags[0] = True
            imgs[0] = grabResult.GetArray()
        elif (cameraContextValue == 1):
            print('hi 1')
            flags[1] = True
            imgs[1] = grabResult.GetArray()


	#this section enters if all cams captured the frame and all frames are ready for proccessing @gad
        if all(flags):
            print('I am here finally')
            #reset flags 
            flags = [0,0]
            #write your code here to proccess imgs
            print("first pixel cam0: ", imgs[0][0,0])
            print("first pixel cam1: ", imgs[1][0,0])

except genicam.GenericException as e:
    # Error handling
    print("An exception occurred.", e.GetDescription())
    exitCode = 1

# Comment the following two lines to disable waiting on exit.
sys.exit(exitCode)

