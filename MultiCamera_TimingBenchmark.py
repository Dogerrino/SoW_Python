# ===============================================================================
#   Multiple Cameras in an array, can be benchmarked for timing
# ===============================================================================
from pypylon import pylon
from pypylon import genicam

import sys
import time


# import only system from os
from os import system, name
 
# Clean the terminal output
def clear():

    # for windows
    if name == 'nt':
        _ = system('cls')
 
    # for mac and linux(here, os.name is 'posix')
    else:
        _ = system('clear')

#Get all cameras -> "devices"
def TryGetDevices():
    devices = tlFactory.EnumerateDevices()
    if len(devices) == 0:
        raise pylon.RuntimeException("No camera present.")
    return devices

#Setup Camera Array
def SetupCameras(devices):
    cameras = pylon.InstantCameraArray(min(len(devices), maxCamerasToUse))
    # Create and attach all Pylon Devices.
    for i, cam in enumerate(cameras):
        cam.Attach(tlFactory.CreateDevice(devices[i]))

        # Print the model name of the camera.
        print("Using device ", cam.GetDeviceInfo().GetModelName())
    return cameras

#Setup Cameras for triggering
def SetupTriggering(cameras, TriggerSettings):
    for cam in cameras:
        #Setup for Triggering
        cam.TriggerSelector.SetValue(TriggerSettings[0])
        cam.TriggerSource.SetValue(TriggerSettings[1])
        cam.TriggerMode.Value = TriggerSettings[2]

#Main Function // Timing the Trigger to Image Availability
def main():
    try:

        # Create an array of instant cameras for the found devices and avoid exceeding a maximum number of devices.
        devices = TryGetDevices()
        print(f"Length of deivces: {len(devices)}")
        cameras = SetupCameras(devices)
        cameras.Open()

        #Setup for Triggering
        SetupTriggering(cameras, TriggerSettings)

        # Start the grabbing 
        #Note that the Array uses only this method as of typing this
        cameras.StartGrabbing()

        # Camera.StopGrabbing() is called automatically by the RetrieveResult() method
        # when countOfImagesToGrab images have been retrieved.
        for i in range(countOfImagesToGrab):

            #Local Variable for referncing in this loop
            ThisCamera = i % maxCamerasToUse

            #Start Timing the camera, Single Image
            StartTime = time.time()

            cameras[ThisCamera].ExecuteSoftwareTrigger()

            # Wait for an image and then retrieve it. A timeout of 100 ms is used.
            grabResult = cameras[ThisCamera].RetrieveResult(100, pylon.TimeoutHandling_ThrowException)

            # Image grabbed successfully?
            if grabResult.GrabSucceeded():
                # This is where Image Processing would be placed;
                # Ergo - this is the end of the timing consideration.
                EndTime = time.time()
            else:
                print("Error: ", grabResult.ErrorCode, grabResult.ErrorDescription)
            grabResult.Release()
            # Calculate the time taken        
            TimeElapsed = EndTime - StartTime

            #Output Time & Which camera. Several possible references:
            #...for camera {cameras[ThisCamera].GetDeviceInfo().GetModelName()}")
            #...for camera {cameras[ThisCamera].DeviceUserID.GetValue()}")
            print(f"Time between software trigger and image retrieval: {(TimeElapsed*1000):.6f} ms for camera {cameras[ThisCamera].DeviceSerialNumber.GetValue()}")

        #End of Camera Things
        cameras.Close()
        return 0 #exitCode

    except genicam.GenericException as e:
        # Error handling.
        print("An exception occurred.")
        print(e)
        return 1 #exitCode

    #sys.exit(exitCode)

if(__name__):
    #Clean Slate
    clear()

    #Number of cameras to use
    # Limits the amount of cameras used for grabbing;
    # It is important to manage the available bandwidth when grabbing with multiple cameras;
    # This applies, for instance, if two GigE cameras are connected to the same network adapter via a switch;
    # To manage the bandwidth, the GevSCPD interpacket delay parameter and the GevSCFTD transmission delay
    # parameter can be set for each GigE camera device;
    maxCamerasToUse = 2

    # Number of images to be grabbed, per camera.
    countOfImagesToGrabperCamera = 5

    #Total Number of Images to get
    countOfImagesToGrab = countOfImagesToGrabperCamera * maxCamerasToUse

    #Trigger Settings for the Setup
    # Form of           <TriggerSelector>,  <TriggerSource>,    <TriggerMode>
    TriggerSettings = [ "FrameStart",       "Software",         "On"         ]

    #Camera Information
    info = pylon.DeviceInfo()
    #Callout by Interface approach:
    # BaslerUsb               for USB 
    # BaslerGigE              for GigE 
    # BaslerGTC/Basler/CXP    for CXP
    info.SetDeviceClass('BaslerUsb')

    # Get the transport layer factory.
    tlFactory = pylon.TlFactory.GetInstance()

    #Time Open to Close
    ProcessTimeStart = time.time()

    #Actual Main
    exitCode = main()

    ProcessTimeEnd = time.time()
    print(f"Time For Open to Close: {((ProcessTimeEnd-ProcessTimeStart)*1000):.6f} ms")

    #End things
    sys.exit(exitCode)