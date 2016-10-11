import pymba
import numpy
import matplotlib.pyplot as plt
import traceback
import sys
import time
import cv2

tstart = None
nImg = 0

def frameCB(frame):
    print "frame cb"
    global tstart
    global nImg
    imgData = numpy.ndarray(buffer = frame.getBufferByteData(),
                           dtype = numpy.uint8,
                           shape = (frame.height,
                                    frame.width)
                            )
    nImg += 1
    print ("fps: %.4f, nimg: %i, medianVal: %.2f"%(nImg/float(time.time()-tstart), nImg, numpy.median(imgData)))
    cv2.imshow("frame", imgData)
    cv2.waitKey(1)
    frame.queueFrameCapture(frameCB)

if __name__ == "__main__":
    vimba = pymba.Vimba()
    vimba.startup()
    system = vimba.getSystem()
    system.runFeatureCommand("GeVDiscoveryAllOnce")
    cameraIds = vimba.getCameraIds()
    camera0 = vimba.getCamera(cameraIds[0])
    camera0.openCamera()
    camera0.AcquisitionMode = "Continuous"
    # use 3 frames
    frames = [
        camera0.getFrame(),
        camera0.getFrame(),
        camera0.getFrame(),
        ]
    # announce the frames
    for frame in frames:
        frame.announceFrame()

    print 1
    camera0.startCapture()
    print 2
    for frame in frames:
        frame.queueFrameCapture(frameCB)
    print 3
    camera0.runFeatureCommand("AcquisitionStart")
    print 4
    tstart = time.time()
    print 5
    while True:
        continue
   

