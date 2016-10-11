import pymba
import numpy
import matplotlib.pyplot as plt
import traceback
import sys
import time
import cv2

if __name__ == "__main__":
    vimba = pymba.Vimba()
    vimba.startup()
    system = vimba.getSystem()
    system.runFeatureCommand("GeVDiscoveryAllOnce")
    cameraIds = vimba.getCameraIds()
    camera0 = vimba.getCamera(cameraIds[0])
    camera0.openCamera()
    camera0.AcquisitionMode = "SingleFrame"
    tstart = time.time()
    nImg = 0
    while True:
        try:
            frame0 = camera0.getFrame()
            import pdb; pdb.set_trace()
            frame0.announceFrame()
            camera0.startCapture()
            frame0.queueFrameCapture()
            camera0.runFeatureCommand("AcquisitionStart")
            camera0.runFeatureCommand("AcquisitionStop")
            frame0.waitFrameCapture()
            imgData = numpy.ndarray(buffer = frame0.getBufferByteData(),
                                   dtype = numpy.uint8,
                                   shape = (frame0.height,
                                            frame0.width)
                                            )
            camera0.endCapture()
            camera0.revokeAllFrames()
            nImg += 1
            print ("fps: %.4f, nimg: %i"%(nImg/float(time.time()-tstart), nImg))
            #imgData = cv2.cvtColor(imgData, cv2.COLOR_BGR2GRAY)
            #cv2.imshow("frame", imgData)
            #cv2.waitKey(10)
        except Exception as e:
            print("oops")
            print str(e)
            traceback.print_exc(file=sys.stdout)
            #camera0.endCapture()
            cv2.destroyAllWindows()
            vimba.shutdown()
            break
            #import pdb; pdb.set_trace()

