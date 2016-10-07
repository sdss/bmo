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
    global tstart
    global nImg
    imgData = numpy.ndarray(buffer = frame.getBufferByteData(),
                           dtype = numpy.uint8,
                           shape = (frame.height,
                                    frame.width)
                            )
    nImg += 1
    print ("fps: %.4f, nimg: %i, medianVal: %.2f"%(nImg/float(time.time()-tstart), nImg, numpy.median(imgData)))
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
        fame.announceFrame()

    camera0.startCapture()

    for frame in frames:
        frame.queueFrameCapture(frameCB)

    camera0.runFeatureCommand("AcquisitionStart")
    tstart = time.time()



            # camera0.runFeatureCommand("AcquisitionStop")
            # frame0.waitFrameCapture()

            # camera0.endCapture()
            # camera0.revokeAllFrames()
            # nImg += 1

            #imgData = cv2.cvtColor(imgData, cv2.COLOR_BGR2GRAY)
            # cv2.imshow("frame", imgData)
            # cv2.waitKey(10)

            # print str(e)
            # traceback.print_exc(file=sys.stdout)
            # #camera0.endCapture()
            # cv2.destroyAllWindows()
            # vimba.shutdown()
            #import pdb; pdb.set_trace()

