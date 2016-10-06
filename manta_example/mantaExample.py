import pymba
import numpy
import matplotlib.pyplot as plt

if __name__ == "__main__":
    vimba = pymba.Vimba()
    vimba.startup()
    system = vimba.getSystem()
    system.runFeatureCommand("GeVDiscoveryAllOnce")
    cameraIds = vimba.getCameraIds()
    camera0 = vimba.getCamera(cameraIds[0])
    camera0.openCamera()
    camera0.AcquisitionMode = "SingleFrame"
    frame0 = camera0.getFrame()
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
    plt.imshow(imgData)
    plt.show()

    camera0.endCapture()
    camera0.revokeAllFrames()
    vimba.shutdown()

