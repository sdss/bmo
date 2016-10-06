import pymba
import numpy
import matplotlib.pyplot as plt

if __name__ == "__main__":
    vimba = pymba.Vimba()
    vimba.startup()
    system = vimba.getSystem()
    system.runFeatureComand("GeVDiscoveryAllOnce")
    cameraIds = vimba.getCameraIds()
    camera0 = vimba.getCamera(cameraIds[0])
    camera0.openCamera()
    frame0 = camera0.getFrame()
    frame0.announceFrame()
    camera0.startCapture()
    frame0.queueFrameCapture()

    while True:
        try:
            camera0.runFeatureCommand("AcquisiontStart")
            camera0.runFeatureCommand("AcquisiontStop")
            frame0.waitFrameCapture()
            imgData = frame0.getBufferByteData()
            plt.imshow(imgData)
            plt.show()
        except:
            camera0.endCapture()
            camera0.revokeAllFrames()
            vimba.shutdown()
            break
